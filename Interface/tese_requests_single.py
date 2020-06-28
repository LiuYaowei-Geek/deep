import requests
import json
class requests_single(object):
    '''
    适合单个方法只需要取一个值，配get_execl方法
    '''
    def __init__(self,url,requersts_type,paramt,headers):
        self.url=url
        self.requersts_type=requersts_type
        self.paramt=paramt
        self.headers=headers
    def testapi(self):
        headers_1= {"Content-Type": "application/json", }
        head={"Content-Type": "application/x-www-form-urlencoded","token": self.headers}
        if self.requersts_type=="post" :
            response=requests.post(self.url,data=self.paramt,headers=head)
        elif self.requersts_type=="get":
            response=requests.get(self.url,headers=head)
        return response

    def getJson(self):
        json_data = self.testapi()
        print(json.loads(json_data.text))
        return json.loads(json_data.text)


