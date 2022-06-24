import os
import requests
from dotenv import load_dotenv


load_dotenv()

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
AUTHENTICATION_URL = os.getenv('AUTHENTICATION_URL')

def authentication():
    credentials = {'email': EMAIL,
               'password': PASSWORD}

    api_response = requests.post(AUTHENTICATION_URL, json = credentials)
    status_code = api_response.status_code
    #print(f'AUTHENTICATION: STATUS CODE {status_code}')
    USER_API_HASH = None
    message = None
    if status_code == 200:
        USER_API_HASH = api_response.json()['user_api_hash']
    else:
        message = api_response.json()['message']
        print(f'\tERROR: {message}')
    return {'status_code': status_code,
            'USER_API_HASH': USER_API_HASH,
            'message': message,
            'process': 'AUTHENTICATION'}

if __name__ == '__main__':
    result = authentication()
    print(result)
