import requests
import json
from Public.db_commit import db_commit
db_link=db_commit()
class delect_table_list(object):
    '''
    删除
    # '''
    # zhu逐仓
    # canshu1 = 315508
    # canshu2 = 315703
    #合仓
    # canshu1=315782
    # canshu2=316095
    #市价
    # canshu1 = '315908'
    # canshu2 = '315896'
    # #追加保证金
    # single = '315838'
    #一个用户全仓开多开空
    # 316220
    #减少保证金
    # single=316173
    #接口下单异常测试
    # single='315655'、
    #逐仓平仓开多开空
    # single=316040
    #逐仓成交一半数量
    # single = '316463'


    #合仓撤单、逐仓撤单
    # single=315900
    #全仓撤单/全仓部分撤单
    # single = 316183
    #逐仓增加调整杠杆
    # single = '316027'
    # 减少调整杠杆
    # single = '315736'
    # 逐仓增加调整杠杆
    # single = '316027'
    # # #调试
    # canshu1 = '315702'
    # canshu2 = '315703'

    # 全仓委托部分成交
    # # single =315766
    # canshu1 = '316032'
    # canshu2 = '315766'
    # single=315520
    # 全仓计算强平价
    # canshu1 = '316220'
    # canshu2 = '315944'
    single='315702'


    def test_delect(self):
        # de_pc_order="delete from pc_order where uid in ('%s','%s')" % (self.canshu1,self.canshu2)
        #
        # db_link.delete(de_pc_order)
        # de_pc_trade_order = "delete from pc_trade_order where uid in ('%s','%s')" % (self.canshu1,self.canshu2)
        # db_link.delete(de_pc_trade_order)
        # de_pc_order = "delete from pc_match where bid_uid in ('%s','%s')" % (self.canshu1,self.canshu2)
        # db_link.delete(de_pc_order)

        de_pc_order1 = "delete from pc_order where uid in ('%s')" % (self.single)
        db_link.delete(de_pc_order1)
        de_pc_trade_order1 = "delete from pc_trade_order where uid in ('%s')" % (self.single)
        db_link.delete(de_pc_trade_order1)
        de_pc_order1 = "delete from pc_match where bid_uid in ('%s')" % (self.single)
        db_link.delete(de_pc_order1)



sql=delect_table_list()
sql.test_delect()

