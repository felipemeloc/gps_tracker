import os
import src.db as db
import pandas as pd
import numpy as np
import src.utils as utils
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Define project main path
MAIN_FOLDER = os.getenv('MAIN_PATH')

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

TS_completed_jobs = open(os.path.join(query_path,
                    'TS_completed_jobs.sql'), 'r').read()


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
    
def save_cache(df:pd.DataFrame):
    df[['LocksmithPostCode', 'Coordinates']].drop_duplicates('LocksmithPostCode').to_csv(cache_path, index=False)

completed_jobs = db.sql_to_df(TS_completed_jobs)
completed_jobs['Locksmith'] = utils.clean_locksmith_name(completed_jobs['Locksmith'])
completed_jobs['LocksmithPostCode'] = completed_jobs['LocksmithPostCode'].apply(fix_post_code_format)
completed_jobs = completed_jobs.merge(cache, on='LocksmithPostCode', how='left').fillna(value=-1)
completed_jobs['Coordinates'] = [get_coordinates(post_code) if coordinate == -1 else coordinate for post_code, coordinate in zip(completed_jobs['LocksmithPostCode'], completed_jobs['Coordinates'])]
save_cache(completed_jobs)
print(completed_jobs)




