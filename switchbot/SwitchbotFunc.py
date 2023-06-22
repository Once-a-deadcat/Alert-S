import requests
import json
from switchbot.SwitchbotAuth import make_sign, make_request_header # switchbot-auth.pyから関数をインポート
import os

base_url = 'https://api.switch-bot.com'

async def get_device_list(deviceListJson='deviceList.json'):
    # tokenとsecretを貼り付ける
    token = os.environ['API_KEY']
    secret = os.environ['CLIENT_SECRET']

    devices_url = base_url + "/v1.1/devices"

    headers = make_request_header(token, secret)

    try:
        # APIでデバイスの取得を試みる
        res = requests.get(devices_url, headers=headers)
        res.raise_for_status()

        print(res.text)
        deviceList = json.loads(res.text)
        return deviceList
    except requests.exceptions.RequestException as e:
        print('response error:',e)
        return None

if __name__ == "__main__":
    get_device_list()
    