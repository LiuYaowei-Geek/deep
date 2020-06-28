import requests
import json
class requests_packge(object):
    '''
    适合execk多个参数循环的，配read_execl方法
    '''
    def __init__(self,url,requersts_type):
        self.url=url
        self.requersts_type=requersts_type
    def testapi(self):

        if self.requersts_type=="post" :
            response=requests.post(self.url)
        elif self.requersts_type=="get":
            response=requests.get(self.url)
        return response

    def getJson(self):
        json_data = self.testapi()
        return json.loads(json_data.text)
