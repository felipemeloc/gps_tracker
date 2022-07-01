
import json
import requests
import pandas as pd
from api_authentication import authentication

json_path = 'jsons/devices.json'
csv_path = 'csv/devices.csv'

def get_devices():
    
    authentication_response = authentication()
    if authentication_response['status_code'] != 200:
        return authentication_response
        
    USER_API_HASH = authentication_response['USER_API_HASH']
    
    arguments = {'user_api_hash': USER_API_HASH,
                    'lang': 'en'}

    report_url = 'https://track.roedan.com/api/get_devices?'
    api_response = requests.get(report_url, json = arguments)
    status_code = api_response.status_code
    #print(f'GET DEVICES: STATUS CODE {status_code}')
    devices = None
    message = None 
    if status_code == 200:
        data = api_response.json()
        
        with open(json_path, 'w') as f:
            json.dump(data, f,  indent=4, sort_keys=True)
            
        devices = []
        for item in data:
            for group_item in item['items']:
                device = {'group_id': item['id'],
                          'group_name': item['title'],
                        'device_id': group_item['device_data']['id'],
                        'name': group_item['name']}
                devices.append(device)
        devices = pd.DataFrame(devices)
    else:
        message = api_response.json()['message']
        print(f'\tERROR: {message}')
        
    return {'status_code': status_code,
            'devices': devices,
            'message': message,
            'process': 'GET DEVICES'}

if __name__ == '__main__':
    results = get_devices()
    df = results['devices']
    devices = df[df['group_name']=='WGTK']
    devices.to_csv(csv_path, index=False)
    print(devices)