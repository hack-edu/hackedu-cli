import requests

HOST = 'http://localhost:5008'
#TODO: setup --env paramter to determine if we should use localhost or product HOST

class Api(object):
    def __init__(self, headers):
        self.headers = headers

    def get(self, path):
        url = '{}{}'.format(HOST, path)
        response = requests.get(url, headers=self.headers)
        return response

    def post(self, path, payload):
        url = '{}{}'.format(HOST, path)
        response = requests.post(url, data=payload, headers=self.headers)
        return response

    def put(self, path, payload):
        url = '{}{}'.format(HOST, path)
        response = requests.post(url, data=payload, headers=self.headers)
        return response