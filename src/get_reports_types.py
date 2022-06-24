
import json
import requests
from api_authentication import authentication

json_path = 'jsons/reports_types.json'

def get_report_types():

    USER_API_HASH = authentication()['USER_API_HASH']

    arguments = {'user_api_hash': USER_API_HASH,
                    'lang': 'en'}
    report_url = 'https://track.roedan.com/api/get_reports_types?'
    api_response = requests.get(report_url, json = arguments)
    status_code = api_response.status_code
    print(f'GET REPORT TYPES: STATUS CODE {status_code}')
    if status_code == 200:
        data = api_response.json()
        path = json_path
        with open(json_path, 'w') as f:
            json.dump(data, f,  indent=4, sort_keys=True)
    else:
        data = None
        path = None
        error = api_response.json()['message']
        print(f'\tERROR: {error}')
        
    return {'status_code': status_code, 'data':data, 'json_path': path}

if __name__ == '__main__':
    report_types = get_report_types()
    data = report_types['data']
    list_reports = sorted(data['items'], key =lambda x: x['type'])
    for item in list_reports:
        report_name = str(item['name']).strip()
        print(f"{item['type']:>2}, {report_name:<45}, {item['fields']}")