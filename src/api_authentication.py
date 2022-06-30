"""api_authentication.py

Contains the following function:
* authentication: Returns a dictionary with the message response from the authentication to the Rodean API. use:
    import api_authentication
    api_authentication.authentication()

"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
AUTHENTICATION_URL = os.getenv('AUTHENTICATION_URL')

def authentication()->dict:
    """Function for authentication inside the Rodean API. The function uses the credentias used for Rodean."

    Returns:
        dict: dictionary with the following structure:
        {
            status_code: server response (3 digit integer)
            USER_API_HASH: encrypted key for access the API endpoints
            message: in case of error, problem description
            process: name of the process carried out (for this case is AUTHENTICATION)
        }
    """
    credentials = {'email': EMAIL,
               'password': PASSWORD}

    api_response = requests.post(AUTHENTICATION_URL, json = credentials)
    status_code = api_response.status_code
    #print(f'AUTHENTICATION: STATUS CODE {status_code}')
    USER_API_HASH = None
    message = None
    # When the status code is 200, the connection was successfull
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
