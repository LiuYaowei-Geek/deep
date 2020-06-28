import pandas
import os
s = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
class read_excel():
    def __init__(self,execl_name,sheetName):
        self.execl_name=execl_name
        self.sheetName=sheetName
    def exexl(self,lie):
        df=pandas.read_excel(self.execl_name,self.sheetName)
        test_data =[]
        for i in df.index.values:  # 获取行号的索引，并对其进行遍历：
            # 根据i来获取每一行指定的数据 并利用to_dict转成字典
            row_data= df.loc[i,[lie]].to_dict()

            test_data.append(row_data)
        return test_data
if __name__=='__main__':

    s=os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
    wenjian=s+'\\case\\jekn.xlsx'
    f=read_excel(wenjian,'Sheet2')
    s=f.exexl('url')
    print(type(s))
    g=s[0]['url']
    print(g)

