import requests
import hmac
import hashlib
import base64
from urllib import parse
from tenacity import *


def __get_content_from_internet(url, method='GET', headers=None, params=None, data=None):
    req = requests.request(method=method, url=url, headers=headers, params=params, data=data)
    return req


def get_content_from_internet(url, method='GET', headers=None, params=None, data=None, retry_times=5,
                              sleep_seconds=5):
    params = {
        "url": url,
        "method": method,
        "headers": headers,
        "params": params,
        "data": data
    }
    _req = robust(__get_content_from_internet, params, retry_times=retry_times, sleep_seconds=sleep_seconds)
    return _req


def robust(func, params={}, func_name='', retry_times=5, sleep_seconds=5):
    retryer = Retrying(stop=stop_after_attempt(retry_times), wait=wait_fixed(sleep_seconds), reraise=True)
    return retryer(func, **params)


def cal_dingtalk_timestamp_sign(secret):
    timestamp = int(round(time.time() * 1000))
    secret_enc = bytes(secret.encode('utf-8'))
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = bytes(string_to_sign.encode('utf-8'))
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = parse.quote_plus(base64.b64encode(hmac_code))
    return str(timestamp), str(sign)
