import os
import pandas as pd
import db
import utils
import geo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Define project main path
MAIN_FOLDER = os.getenv('MAIN_PATH')

query_path = os.path.join(MAIN_FOLDER, 'queries')

TS_cache_postcode = open(os.path.join(query_path,
                    'TS_cache_postcode.sql'), 'r').read()

def get_coordinates_from_db(df:pd.DataFrame)->pd.DataFrame:
    df['LocksmithPostCode'] = df['LocksmithPostCode'].apply(utils.fix_post_code_format)
    postcodes = ', '.join(df['LocksmithPostCode'].apply(lambda x: f"'{x}'").unique())
    cache_postcodes = db.sql_to_df(TS_cache_postcode.format(POSTCODE_LIST = postcodes), use_live=False)
    cache_postcodes['cache'] = True
    return df.merge(cache_postcodes, left_on='LocksmithPostCode', right_on='postcode', how='left').fillna(value=-1).drop(columns=['postcode'])

def get_new_coordinates(df:pd.DataFrame)->pd.DataFrame:
    df['coordinates'] = [
        geo.get_coordinates(post_code)
        if (postcode_lat == -1 and postcode_long == -1)
        else (postcode_lat, postcode_long)
        for post_code, postcode_lat, postcode_long
        in zip(
            df['LocksmithPostCode'],
            df['postcode_lat'],
            df['postcode_long'])
            ]
    df['postcode_lat'] = df['coordinates'].apply(lambda x: x[0]).astype(float)
    df['postcode_long'] = df['coordinates'].apply(lambda x: x[-1]).astype(float)
    df.drop(columns=['coordinates'], inplace=True)
    return df

def save_cache(df:pd.DataFrame):
    df = df[df['cache'] != True][['LocksmithPostCode', 'postcode_lat', 'postcode_long']].rename(columns={'LocksmithPostCode': 'postcode'})
    df.drop_duplicates(inplace=True)
    if not df.empty:
        db.df_to_sql(df,
                     table_name='postcode_coordinates',
                     table_schema= 'dbo',
                     use_live=False)

def postcode_process(df:pd.DataFrame):
    df = get_coordinates_from_db(df)
    df = get_new_coordinates(df)
    save_cache(df)
    return df[['ReportID', 'LocksmithPostCode', 'postcode_lat', 'postcode_long']].drop_duplicates().rename(columns={'LocksmithPostCode': 'postcode'})


if __name__== '__main__':
    df = pd.DataFrame({'ReportID': {0: 150099, 1: 154557, 2: 154291, 3: 154528, 4: 153911}, 'LocksmithPostCode': {0: 'PE11 4NW', 1: 'S6 1RZ', 2: 'S63 9DE', 3: 'DE11 0AN', 4: 'NG21 0AW'}})
    df = postcode_process(df)
    print(df)
