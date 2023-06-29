import os
import time
import hashlib
import hmac
import base64


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
