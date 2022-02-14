import os
from fight import Fight
import requests

def uploadFight(fight:Fight):
    '''
    sends a fight to the dofuseye backend.
    the backend stores the info and provides a presigned url to upload the screenshot.
    the backend also provides the fight ID.

    this function returns the fight ID on successful upload
    '''

    # TODO: figure out the base URL... env var or something
    BASE = 'http://127.0.0.1:5000'
    url = BASE + '/api/fights/post'
    response = requests.post(
        url=url,
        # TODO: need to handle tokens and logging in and expiration and all that...
        headers={'Authorization': "auth_token_goes_here"},
        json=fight.toDict()
    )
    if response.ok:
        print('response is OK!')
        resp_data = response.json()
        # print(resp_data)
        uploadScreenshot(resp_data['upload_url'], fight.filePath)
        return resp_data['fight_id']
    else:
        print('fight upload to backend failed!!!')
        return 0

def uploadScreenshot(presignedUrl, screenshotPath, deleteAfter=True):
    # upload file via presigned url
    with open(screenshotPath, 'rb') as f:
        files = {'file': (screenshotPath, f)}
        http_response = requests.post(presignedUrl['url'], data=presignedUrl['fields'], files=files)

    print(f"Screenshot upload HTTP status code: {http_response}")
    
    # now delete it
    if deleteAfter:
        if os.path.exists(screenshotPath):
            os.remove(screenshotPath)


# TODO: log in to backend with account
# TODO: store token
# TODO: when rejected due to expired token or not logged in, try to log in again (once or twice)
