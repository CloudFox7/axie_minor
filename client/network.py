from requests import get,post
from json import dumps
HOST = 'http://192.168.1.13:9999/'
def send_json(endpoint,data):
    post(HOST+endpoint,data=dumps(data))

def get_json(endpoint):
    return get(HOST+endpoint).json()
    