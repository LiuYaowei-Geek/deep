import pymysql
class db_commit(object):
    '''
        1、添删改需要commit
        2、查询无需commit
        3、连接地址写死在代码里面，因为只有一个数据库，无需做成参数
    '''
    #连接数据库
    def connect(self):
        self.conn = pymysql.connect(host='103.14.33.145',port=3366,user='root',database = None,password='123456',db='bbj_db',charset='utf8',cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.conn.cursor()
    '''关闭链接'''
    def close(self):
        self.cursor.close()
        self.conn.close()
    '''取第一条数据'''
    def get_one(self, sql, params=()):
        result = None
        try:
            #创建链接
            self.connect()
            #执行sql
            self.cursor.execute(sql, params)
            #取反回值得第一条数据
            result = self.cursor.fetchone()
            #关闭查询
            self.close()
        except Exception as e:
            print(e)
        #返回结果
        return result

    '''取所有sql里面的值'''
    def get_all(self, sql, params=()):
        #声明数组
        list_data =[]
        try:
            # 创建链接
            self.connect()
            # 执行sql
            self.cursor.execute(sql, params)
            # 取反回值的所有值
            list_data=dict()
            list_data=self.cursor.fetchall()
            self.close()
        except Exception as e:
            print(e)
        #返回
        return list_data
    '''
     执行增删改
              :param sql: sql语句
              :param params: sql语句对象的参数列表，默认值为None
              :return: 受影响的行数
    '''
    def __edit(self, sql, params):
        count = 0
        try:
            #连接
            self.connect()
            #执行传sql,params添加的参数列表
            count = self.cursor.execute(sql, params)
            #提交
            self.conn.commit()
            self.close()
        except Exception as e:
            print(e)
        return count

    #添加
    def insert(self, sql, params=()):
        return self.__edit(sql, params)
    #修改
    def update(self, sql, params=()):
        return self.__edit(sql, params)
    #删除
    def delete(self, sql, params=()):
        return self.__edit(sql, params)

if __name__ == '__main__':
    s=db_commit()
    s.connect()
    print(s)