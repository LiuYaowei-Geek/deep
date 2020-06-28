# -*- coding: utf-8 -*-
# @Date    : 2017-10-14 15:35:17
# @Author  : test
import os
import logbook
from logbook.more import ColorizedStderrHandler
from functools import wraps
check_path='.'
LOG_DIR = os.path.join(check_path, 'log')
file_stream = False
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)#目录不存在自动创建
    file_stream = True
def get_logger(name='interface', file_log=file_stream, level=''):
    """ get logger Factory function """
    logbook.set_datetime_format('local')

    ColorizedStderrHandler(bubble=False, level=level).push_thread()
    logbook.TimedRotatingFileHandler(
            os.path.join(LOG_DIR, '%s.log' % name),
            date_format='%Y-%m-%d %H_%M_%S', bubble=True, encoding='utf-8').push_thread()
    return logbook.Logger(name)

LOG = get_logger(file_log=file_stream, level='INFO')
def logger(param):
    """ fcuntion from logger meta """
    def wrap(function):
        """ logger wrapper """
        @wraps(function)
        def _wrap(*args, **kwargs):
            """ wrap tool """
            LOG.info("运行位置 {}".format(param))
            # LOG.info("全部args参数参数信息 , {}".format(str(args)))
            # LOG.info("全部kwargs参数信息 , {}".format(str(kwargs)))
            return function(*args, **kwargs)
        return _wrap
    return wrap

