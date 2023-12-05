import os
import time
import hashlib
import hmac
import base64
import requests
import json
import os

base_url = "https://api.switch-bot.com"
device_id = os.environ["LED_DEVICE_ID"]


def make_sign(token: str, secret: str):
    nonce = ""
    t = int(round(time.time() * 1000))
    string_to_sign = bytes(f"{token}{t}{nonce}", "utf-8")
    secret = bytes(secret, "utf-8")
    sign = base64.b64encode(
        hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest()
    )
    return sign, str(t), nonce


def make_request_header(token: str, secret: str) -> dict:
    sign, t, nonce = make_sign(token, secret)
    headers = {
        "Authorization": token,
        "sign": sign.decode(),
        "t": str(t),
        "nonce": nonce,
    }
    return headers


async def get_device_list():
    # tokenとsecretを貼り付ける
    token = os.environ["API_KEY"]
    secret = os.environ["CLIENT_SECRET"]

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
        print("response error:", e)
        return None


async def set_light_color(color: str):
    token = os.environ["API_KEY"]
    secret = os.environ["CLIENT_SECRET"]

    device_url = base_url + f"/v1.1/devices/{device_id}/commands"
    headers = make_request_header(token, secret)

    if color.lower() == "red":
        color_hex = "180:20:20"  # Hex color code for red
    elif color.lower() == "yellow":
        color_hex = "200:200:0"  # Hex color code for yellow
    elif color.lower() == "blue":
        color_hex = "127:255:212"  # Hex color code for blue
    elif color.lower() == "none":
        command1 = {
            "command": "turnOff",
            "parameter": "default",
            "commandType": "command",
        }
        try:
            res = requests.post(device_url, headers=headers, json=command1)
            res.raise_for_status()
            print(res.text)
            return
        except requests.exceptions.RequestException as e:
            print(f"Error sending command: {e}")
            return
    else:
        raise ValueError(f"Unsupported color: {color}")

    # ライトをオンにする
    command1 = {"command": "turnOn", "parameter": "default", "commandType": "command"}
    try:
        res = requests.post(device_url, headers=headers, json=command1)
        res.raise_for_status()
        print(res.text)
    except requests.exceptions.RequestException as e:
        print(f"Error sending command: {e}")

    # ライトの明るさを50%にする
    command2 = {"command": "setBrightness", "parameter": 3, "commandType": "command"}
    try:
        res = requests.post(device_url, headers=headers, json=command2)
        res.raise_for_status()
        print(res.text)
    except requests.exceptions.RequestException as e:
        print(f"Error sending command: {e}")

    # ライトの色を変える
    command3 = {"command": "setColor", "parameter": color_hex, "commandType": "command"}
    try:
        res = requests.post(device_url, headers=headers, json=command3)
        res.raise_for_status()
        print(res.text)
    except requests.exceptions.RequestException as e:
        print(f"Error sending command: {e}")

    return True


if __name__ == "__main__":
    get_device_list()
