from __future__ import annotations
import os
from dotenv import load_dotenv
from fight import Fight
import requests

# TODO: is storing this token as a global variable a good way to do this? is there a better practice here?
authToken = ''
# TODO: figure out the base URL... env var or something
load_dotenv()
BACKEND_URL = os.environ['BACKEND_URL']
BACKEND_USER = os.environ['BACKEND_USER']
BACKEND_PASS = os.environ['BACKEND_PASS']
NO_BACKEND_MODE = os.environ['NO_BACKEND_MODE']

def uploadFight(fight:Fight, upload:bool=True, attemptLogin=True):
    '''
    sends a fight to the dofuseye backend.
    the backend stores the info and provides a presigned url to upload the screenshot.
    the backend also provides the fight ID.

    this function returns the fight ID on successful upload
    '''
    if NO_BACKEND_MODE == "TRUE":
        print('fight not uploaded - NO_BACKEND_MODE enabled.')
        return 1

    try:
        response = requests.post(
            url=BACKEND_URL + '/api/fights/post',
            headers={'Authorization': authToken},
            json=fight.toDict()
        )
        if response.ok:
            resp_data = response.json()
            fightID = resp_data['fight_id']
            print(f'fight {fightID} successfully sent to API.')
            if upload:
                uploadScreenshot(resp_data['upload_url'], fight.filePath)
            else:
                print('fight screenshot was not uploaded (as requested)')
            return fightID
        elif response.status_code == 401:
            # eror 401 - unauthorised -> need to log in again, then retry upload (once)
            print('fight not uploaded, need to log in')
            if attemptLogin:
                login()
                return uploadFight(fight, upload, attemptLogin=False)
        elif response.status_code == 403:
            print(f'fight failed to upload to backend. status code: {response.status_code} ({response.reason})')
            print('logged in, but these credentials do not have authorization to upload fight!')
            return 0
        else:
            print(f'fight failed to upload to backend. status code: {response.status_code} ({response.reason})')
            return 0
    except Exception as e:
        print('some exception occured while attempting to post to backend server:')
        print(e)
        return 0

def uploadScreenshot(presignedUrl, screenshotPath, deleteAfter=True):
    if NO_BACKEND_MODE == "TRUE":
        print('screenshot not uploaded - NO_BACKEND_MODE enabled.')
        return 1
    # upload file via presigned url
    print(f'Uploading fight screenshot to aws: {screenshotPath}')
    with open(screenshotPath, 'rb') as f:
        files = {'file': (screenshotPath, f)}
        http_response = requests.post(presignedUrl['url'], data=presignedUrl['fields'], files=files)

    # TODO: check if the status code is a fail, add error handling
    print(f"Screenshot upload HTTP status code: {http_response}")
    
    # now delete it
    if deleteAfter:
        print(f"Deleting local image file: {screenshotPath}")
        if os.path.exists(screenshotPath):
            os.remove(screenshotPath)

def login():
    '''login to the backend and store auth token recieved'''
    if NO_BACKEND_MODE == "TRUE":
        print('no login attempted - NO_BACKEND_MODE enabled.')
        return 1
    print('attempting to log in to backend...')
    response = requests.post(
        url=BACKEND_URL + '/auth/login',
        json={
            "username": BACKEND_USER,
            "password": BACKEND_PASS
        }
    )

    if response.ok:
        print(f"successfully logged in!")
        resp_data = response.json()
        global authToken 
        authToken = resp_data['auth_token']
    else:
        # TODO: handle come failure modes. like wrong username/pass (what others?)
        print(f"failed to log in! status code: {response.status_code} ({response.reason})")
    return

def pingBackend():
    '''checks backend server status, returns response time (ms) if response OK, else -1'''
    if NO_BACKEND_MODE == "TRUE":
        print('no backend ping attempted - NO_BACKEND_MODE enabled.')
        return -1
    response = requests.get(url=BACKEND_URL + "/api")
    if response.ok:
        return response.elapsed.microseconds
    else:
        return -1