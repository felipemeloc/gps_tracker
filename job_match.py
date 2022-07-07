import os
import src.db as db
import pandas as pd
import numpy as np
import src.utils as utils
import src.postcode_match as postcode
import src.geo as geo
from datetime import timedelta
from travel_sheet_report import generate_reports
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Define project main path
MAIN_FOLDER = os.getenv('MAIN_PATH')


query_path = os.path.join(MAIN_FOLDER, 'queries')

TS_completed_jobs_postcode = open(os.path.join(query_path,
                    'tmp_completed_jobs_postcode.sql'), 'r').read()

def get_dates(date_from:str, date_to:str)->pd.Timestamp:
    date = pd.Timestamp(date_from)
    date_to = pd.Timestamp(date_to)
    if date <= date_to:
        while date <= date_to:
            yield date
            date = date + pd.Timedelta(1, unit='d')
    else:
        raise Exception(f'date_from should be minor or equal to date_to, instead:\ndate_from:{date_from}, date_to:{date_to}')

def get_postcode_coordinates(df:pd.DataFrame)->pd.DataFrame:
    coordinates = postcode.postcode_process(df[['ReportID', 'LocksmithPostCode']])
    df = df.merge(coordinates, on='ReportID', how='inner')
    return df

def complete_jobs_data(df:pd.DataFrame)->pd.DataFrame:
    df['Locksmith'] = utils.clean_locksmith_name(df['Locksmith'])
    df = get_postcode_coordinates(df)
    df['Coordinates'] = df[['postcode_lat', 'postcode_long']].apply(tuple, axis=1)
    return df[['ReportID', 'Locksmith', 'postcode', 'Coordinates']]

def check_for_BCA(jobs_completed:pd.DataFrame, match:pd.DataFrame)->list:
    bca_locksmith = list(jobs_completed[jobs_completed['postcode']=='BS11 0YW']['Locksmith'].unique())
    coordinates = match[['Position B_lat', 'Position B_long']].apply(tuple, axis=1).values
    return [geo.into_bca(coordinate) if locksmith in bca_locksmith else False for locksmith, coordinate in zip(match['Locksmith'], coordinates) ]
    
    
def get_match_report(completed_jobs:pd.DataFrame, travel_data:pd.DataFrame)->pd.DataFrame:
    match = []
    for _, row in completed_jobs.iterrows():
        locksmith = row['Locksmith']
        job_coordinates = row['Coordinates']
        tmp_df = travel_data[travel_data['Locksmith']==locksmith]
        tmp_df['Position B'] = tmp_df[['Position B_lat', 'Position B_long']].apply(tuple, axis=1)
        tmp_df['distance'] = tmp_df['Position B'].apply(lambda x: geo.get_distance(x, job_coordinates))
        tmp_df = tmp_df[(tmp_df['distance']<=0.5) & (tmp_df['distance'] == tmp_df['distance'].min())]
        if not tmp_df.empty:
            match.append({'index': tmp_df.index[0],
                          'ReportID': row['ReportID'],
                          'Distance (Mi)': tmp_df.iloc[0]['distance']
                        })
    if match:
        match = pd.DataFrame(match).set_index('index')
        return travel_data.merge(match, how='left', left_index=True, right_index=True)
    else:
        return pd.DataFrame(
            columns=[*list(travel_data.columns), 'ReportID', 'Distance (Mi)']
            )
        
def get_split_time(df:pd.DataFrame)->pd.DataFrame:
    df.index.name = 'Route ID'
    df.reset_index(inplace=True)
    split = df.groupby(['Route ID', 'Time at location'], as_index=False).agg({'ReportID':'count'})
    split['split_time'] = split['Time at location'] / split['ReportID']
    return df.merge(split[['Route ID', 'split_time']], how='left', on='Route ID')

def change_for_sql_format(df:pd.DataFrame)->pd.DataFrame:
    delta_str = lambda x: f"{timedelta(seconds=x.total_seconds())}" if isinstance(x, pd.Timedelta) else np.NaN
    if not df.empty:
        for col in ['Duration', 'Time at location', 'split_time']:
            df[col] = df[col].apply(delta_str)
            
    df['Route ID'] = [
        f'{locksmith}_{time}'
        for locksmith, time
        in zip(
            df['Locksmith'].str.lower().str.replace('\s', '', regex=True),
            df['Left'].dt.strftime('%Y%m%d%H%M%S')
            )
    ]
    df.columns = [col.replace(' ', '_') for col in df.columns]
    df.drop_duplicates(inplace=True)
    return df

def get_match_jobs(date_from:str=None, date_to:str=None, save_db:bool=True, csv_folder_path:str='cache/'):
    NOW = pd.Timestamp.now().strftime('%Y-%m-%d')
    if not date_to:
        date_to = NOW
    if not date_from:
        date_from = NOW
    for date in get_dates(date_from, date_to):
        print(date)
        post_code_query = TS_completed_jobs_postcode.format(TARGET_DATE= date.strftime('%Y-%m-%d'))
        jobs_completed = db.sql_to_df(post_code_query)
        jobs_completed = complete_jobs_data(jobs_completed)
        travel_sheet_report = generate_reports(date, return_data=True)
        match_jobs = get_match_report(jobs_completed, travel_sheet_report)
        match_jobs = get_split_time(match_jobs)
        match_jobs['bca'] = check_for_BCA(jobs_completed, match_jobs)
        match_jobs = change_for_sql_format(match_jobs)
        
        if save_db:
            db.df_to_sql(match_jobs,
                        table_name='gps_roedan_locksmith',
                        table_schema='dbo')
        else:
            date_str = date.strftime('%Y-%m-%d')
            match_jobs.to_csv(os.path.join(csv_folder_path, f'job_match_{date_str}.csv'), index=False)
            

if __name__ == '__main__':
    # NOW = pd.Timestamp.now().strftime('%Y-%m-%d)
    date_from = '2022-07-06' # YYYY-MM-DD
    date_to = '2022-07-07' # YYYY-MM-DD
    get_match_jobs(date_from, date_to, save_db=True)