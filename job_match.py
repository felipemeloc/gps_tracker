import os
from pickle import FALSE
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
    # coordinates = postcode.METHOD (df[['ReportID', 'LocksmithPostCode']])
    df = df.merge(coordinates, on='ReportID', how='inner')
    return df

def complete_jobs_data(df):
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
        
def get_split_time(df:pd.DataFrame):
    df.index.name = 'Route ID'
    df.reset_index(inplace=True)
    split = df.groupby(['Route ID', 'Time at location'], as_index=False).agg({'ReportID':'count'})
    split['split_time'] = split['Time at location'] / split['ReportID']
    return df.merge(split[['Route ID', 'split_time']], how='left', on='Route ID')

def save_match(df:pd.DataFrame, path:str)->None:
    delta_str = lambda x: f"{timedelta(seconds=x.total_seconds())}" if isinstance(x, pd.Timedelta) else np.NaN
    if not df.empty:
        for col in ['Duration', 'Time at location', 'split_time']:
            df[col] = df[col].apply(delta_str)
    df.to_csv(path, index=False)

if __name__ == '__main__':
    # NOW = pd.Timestamp.now().strftime('%Y-%m-%d)
    date_from = '2022-07-01' # YYYY-MM-DD
    date_to = '2022-07-01' # YYYY-MM-DD
    for date in get_dates(date_from, date_to):
        print(date)
        post_code_query = TS_completed_jobs_postcode.format(TARGET_DATE= date.strftime('%Y-%m-%d'))
        jobs_completed = db.sql_to_df(post_code_query)
        jobs_completed = complete_jobs_data(jobs_completed)
        travel_sheet_report = generate_reports(date, return_data=True)
        match_jobs = get_match_report(jobs_completed, travel_sheet_report)
        match_jobs = get_split_time(match_jobs)
        match_jobs['bca'] = check_for_BCA(jobs_completed, match_jobs)
        
        str_date = date.strftime('%Y-%m-%d')
        save_match(match_jobs, f'cache/job_match_{str_date}.csv')