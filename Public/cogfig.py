import os
#取当前文件上一级的路径
#os.path.split截取
#[0]确定层级，根据下标确认
#os.path.abspath(__file__))获取当前位置绝对路径
BASE_PATH=os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
#os.path.join拼接目录，case是目录，BASE_PATH是当前路径的上一级目录
EXECL_PATH=os.path.join(BASE_PATH,'case')