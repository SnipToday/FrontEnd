import base64
import hashlib
import json
import os
import time


def get_muut_sso(user):

    api_key = os.environ.get('MUUT_API_KEY')
    secret_key = os.environ.get('MUUT_SECRET_KEY')
    # create a JSON packet of our data attributes

    user_data = {"user": {}}
    if user.is_authenticated():
        user_data = {
            "user": {
                'id': user.id,
                'displayname': user.username,
                'email': user.email,
                'is_admin': user.is_staff
            }
        }

    data = json.dumps(user_data)
    # encode the data to base64
    msg = base64.b64encode(data.encode('utf-8')).decode()
    # generate a timestamp for signing the message
    timestamp = int(time.time())
    # generate signature
    sig = secret_key + " " + msg + " " + str(timestamp)
    sig = hashlib.sha1(sig.encode('utf-8')).hexdigest()

    return {'sig': sig, 'msg': msg, 't': timestamp, 'key': api_key}

