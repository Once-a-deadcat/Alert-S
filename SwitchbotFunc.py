import requests
import json
from SwitchbotAuth import make_sign, make_request_header # switchbot-auth.pyから関数をインポート
import os

base_url = 'https://api.switch-bot.com'

def get_device_list(deviceListJson='deviceList.json'):
    # tokenとsecretを貼り付ける
    token = os.environ['API_KEY']
    secret = os.environ['CLIENT_SECRET']
    # token = "ca6ac1771f2e39829355fef5d76b2ea335aadbfba5e90e3a251e2718b29c18ddb2f5c04c77e11f386e325e3d5f6cf4c9"
    # secret = "f779a0b782cc0c518fd53ea88e6245d2"

    devices_url = base_url + "/v1.1/devices"

    headers = make_request_header(token, secret)

    try:
        # APIでデバイスの取得を試みる
        res = requests.get(devices_url, headers=headers)
        res.raise_for_status()

        print(res.text)
        deviceList = json.loads(res.text)
        # 取得データをjsonファイルに書き込み
        with open(deviceListJson, mode='wt', encoding='utf-8') as f:
            json.dump(deviceList, f, ensure_ascii=False, indent=2)

    except requests.exceptions.RequestException as e:
        print('response error:',e)

if __name__ == "__main__":
    get_device_list()
    