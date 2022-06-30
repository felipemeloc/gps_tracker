import os
import pandas as pd
import requests
from datetime import timedelta
from src.get_devices import get_devices
from src.api_authentication import authentication
from  src.read_api_report_response import get_full_response_table
from dotenv import load_dotenv
import logging


load_dotenv()

MAIN_FOLDER = os.getenv('MAIN_PATH')

USER_API_HASH = authentication()['USER_API_HASH']

# LOG File save
log_file = os.path.join(MAIN_FOLDER, 'logs/travel_report.log')
logger = logging.getLogger(__name__)
handler = logging.FileHandler(log_file)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

################################## Basic paths #####################################

csv_path = os.path.join(MAIN_FOLDER, 'csv')

def get_devices_ids():
    response = get_devices()
    status_code= response['status_code']
    if  status_code== 200:
        df = response['devices']
        df = df[df['group_name']== 'WGTK']
        return list(df['device_id'].astype(str).unique())
    else:
        message = response['message']
        process = response['process']
        raise Exception(f'{process}: STATUS CODE {status_code}, {message}')
    
def get_travel_sheet_report(date_from, date_to):
    arguments= {'user_api_hash': USER_API_HASH,
                    'lang': 'en',
                    'format': 'html',  # "html", "xls", "pdf", "pdf_land"
                    'type': 39, # Travel sheet custom
                    'date_from': date_from,
                    'date_to': date_to,
                    'devices':  get_devices_ids(),
                    'stops': 3*60 # 3 minutes * 60 seconds // number of seconds
                    }
    TRAVEL_SHEET_REPORT_URL =  os.getenv('TRAVEL_SHEET_REPORT_URL')
    api_response = requests.post(TRAVEL_SHEET_REPORT_URL, json = arguments)
    status_code = api_response.status_code
    message = None
    report_url = None
    logger.info(f'GENERATE TRAVEL REPORT: STATUS CODE {status_code}')
    if status_code == 200:
        report_url = api_response.json()['url']
        
    else:
        message = api_response.json()['message']
        logger.error(f'\tERROR: {message}')
        
    return {'status_code': status_code,
            'url':  report_url,
            'message': message,
            'process': 'GENERATE TRAVEL REPORT'}

def generate_reports(date:pd.Timestamp=None, return_data=False):
    if not date:
        date = pd.Timestamp.now()
    date_from= date.strftime('%Y-%m-%d') + ' 00:00:00'
    date_to= (date + pd.Timedelta(1, unit='d')).strftime('%Y-%m-%d') + ' 00:00:00'
    report_response = get_travel_sheet_report(date_from, date_to)
    url = report_response['url']
    df = get_full_response_table(url)
    df.to_csv(os.path.join(csv_path, 'travel_sheet_report.csv'), index=False)

    average_stat = df.groupby('Locksmith', as_index=False).agg(
        {'Duration': 'sum',
        'Time at location': 'sum',
        'Route length (Mi)': 'sum'}
        ).rename(
            columns={'Duration': 'Driving time',
            'Time at location': 'Stop time',
            'Route length (Mi)': 'Miles covered'}
        ).sort_values('Miles covered', ascending=False)

    delta_str = lambda x: f"{timedelta(seconds=x.total_seconds())}"
    for col in ['Driving time', 'Stop time']:
        average_stat[col] = average_stat[col].apply(delta_str)
    
    average_stat.to_csv(os.path.join(csv_path, 'average_stat.csv'), index=False)
    if return_data:
        return df
    
if __name__ == '__main__':
    logger.info('Process started')
    try:
        generate_reports()
        logger.info('Process Successful')
    except Exception as e:
        logger.exception(e)
        