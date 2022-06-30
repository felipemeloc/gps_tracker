import os
import re
import src.db as db
import pandas as pd
import numpy as np
import src.utils as utils
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from travel_sheet_report import generate_reports
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Define project main path
MAIN_FOLDER = os.getenv('MAIN_PATH')

TRAVEL_DATA = os.path.join(MAIN_FOLDER, 'csv/travel_sheet_report.csv')

################################## Cache Load #####################################

cache_path = os.path.join(MAIN_FOLDER, 'cache/coordinates.csv')

if os.path.exists(cache_path):
    cache = pd.read_csv(cache_path)
    cache['Coordinates'] = cache['Coordinates'].str.replace('"|\(|\)|\s','' , regex=True).str.split(',').apply(list)
    l_to_int = lambda coor: [float(num) for num in coor]
    cache['Coordinates'] = [l_to_int(coor) for coor in cache['Coordinates']]
    cache['Coordinates'] = cache['Coordinates'].apply(tuple)
else:
    cache = pd.DataFrame(columns= ['LocksmithPostCode', 'Coordinates'])
    

################################## Query Load #####################################

query_path = os.path.join(MAIN_FOLDER, 'queries')

TS_completed_jobs_postcode = open(os.path.join(query_path,
                    'TS_completed_jobs_postcode.sql'), 'r').read()


def fix_post_code_format(post_code:str)->str:
    post_code = re.sub(r'[^A-Z0-9]+', '', post_code.upper())
    return f'{post_code[:-3]} {post_code[-3:]}'

def get_coordinates(post_code:str)->tuple:
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(post_code)
    if location:
        return location.latitude, location.longitude
    else:
        return None
    
def get_distance(coor1:tuple, coor2:tuple)->float:
    distance = geodesic(coor1, coor2).miles
    return distance

def save_cache(df:pd.DataFrame):
    df[['LocksmithPostCode', 'Coordinates']].drop_duplicates('LocksmithPostCode').to_csv(cache_path, index=False)
    
def get_postcode_coor()->pd.DataFrame:
    completed_jobs = db.sql_to_df(TS_completed_jobs_postcode)
    completed_jobs['Locksmith'] = utils.clean_locksmith_name(completed_jobs['Locksmith'])
    completed_jobs['LocksmithPostCode'] = completed_jobs['LocksmithPostCode'].apply(fix_post_code_format)
    completed_jobs = completed_jobs.merge(cache, on='LocksmithPostCode', how='left').fillna(value=-1)
    completed_jobs['Coordinates'] = [get_coordinates(post_code) if coordinate == -1 else coordinate for post_code, coordinate in zip(completed_jobs['LocksmithPostCode'], completed_jobs['Coordinates'])]
    completed_jobs = completed_jobs[completed_jobs['Coordinates'].notnull()]
    save_cache(completed_jobs)
    return completed_jobs

def clean_position(coord:tuple)->tuple:
    return tuple([float(item) for item in coord.split(',')])
    
def get_travel_data(path:str)->pd.DataFrame:
    travel_data = pd.read_csv(path)
    for col in ['Position A', 'Position B']:
        travel_data[col] = travel_data[col].apply(clean_position)
    for col in ['Duration', 'Time at location']:
        travel_data[col] = pd.to_timedelta(travel_data[col])
    for col in ['Left', 'End', 'Departure time']:
        travel_data[col] = pd.to_datetime(travel_data[col])
    return travel_data

def get_match_report(completed_jobs:pd.DataFrame, travel_data:pd.DataFrame)->pd.DataFrame:
    match = []
    for _, row in completed_jobs.iterrows():
        locksmith = row['Locksmith']
        job_coordinates = row['Coordinates']
        ReportID = row['ReportID']
        tmp_df = travel_data[travel_data['Locksmith']==locksmith]
        tmp_df['distance'] = tmp_df['Position B'].apply(lambda x: get_distance(x, job_coordinates))
        tmp_df = tmp_df[(tmp_df['distance']<=0.5) & (tmp_df['distance'] == tmp_df['distance'].min())]
        if not tmp_df.empty:
            match.append({'ReportID': ReportID, 'index': tmp_df.index[0], 'Distance (Mi)': tmp_df.iloc[0]['distance']})
    match = pd.DataFrame(match).set_index('index')
    return travel_data.merge(match, how='left', left_index=True, right_index=True)

if __name__ == '__main__':
    generate_reports()
    travel_data = get_travel_data(TRAVEL_DATA)
    completed_jobs = get_postcode_coor()
    a = get_match_report(completed_jobs, travel_data)
    a.to_csv('csv/match.csv', index=False)