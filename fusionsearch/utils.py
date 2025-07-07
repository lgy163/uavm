import subprocess
from functools import wraps

import urllib3
import os
import time
import json
import logging
from logging import handlers

from . import config
import datetime
from selenium import webdriver


def singleton(cls):
    instances = {}

    @wraps(cls)
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return getinstance


@singleton
class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }  # 日志级别关系映射

    def __init__(
            self,
            filename,
            level='info',
            when='D',
            backCount=30,
            fmt='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    ):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)  # 设置日志格式
        self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别
        sh = logging.StreamHandler()  # 往屏幕上输出
        sh.setFormatter(format_str)  # 设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(
            filename=filename,
            when=when,
            backupCount=backCount,
            encoding='utf-8')
        th.setFormatter(format_str)  # 设置文件里写入的格式
        self.logger.addHandler(sh)  # 把对象加到logger里
        self.logger.addHandler(th)


log = Logger(r'D:/log/all.log',
             level='debug').logger  # Logger(rf'{config.log_file_root}\uavm-all.log', level='debug').logger


def check_chrome():
    result = subprocess.run('tasklist', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if 'Chrome.exe' in result.stdout.decode('gbk'):
        log.info("Chrome Driver已经打开！")
        return True
    else:
        log.info("Chrome Driver没有打开！")
        return False


def get_chrome():
    if not check_chrome():
        log.info('重新打开chrome driver')
        options = webdriver.ChromeOptions()
        options.add_argument('--remote-debugging-port=%(port)s' %
                             config.chrome_debug_info)
        options.binary_location = config.chrome_binary_location
        wb = webdriver.Chrome(options=options)
        wb.maximize_window()
        return wb
    else:
        options = webdriver.ChromeOptions()
        options.add_argument('--remote-debugging-port=%(port)s' %
                             config.chrome_debug_info)
        options.add_experimental_option(
            "debuggerAddress", "%(host)s:%(port)s" % config.chrome_debug_info)
        options.binary_location = config.chrome_binary_location
        return webdriver.Chrome(options=options)


def download(url, download_path, method='GET', data=None, headers=None):
    log.info(f'用{method}进行文件下载，保存到<{download_path}>')
    http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=3.0, read=60 * 30))

    if method == 'GET':
        r = http.request('GET', url, headers=headers, preload_content=False)
    elif method == 'POST':
        body = json.dumps(data).encode('utf-8')
        r = http.request('POST', url, body=body,
                         headers=headers, preload_content=False)

    log.debug(f'http响应码:{r.status}')
    log.debug(f'http响应头:{r.headers}')
    with open(download_path, 'wb') as f:
        while True:
            d = r.read(4096)
            if not d:
                break
            f.write(d)

    r.release_conn()


def request(url, method='GET', data=None, headers=None):
    http = urllib3.PoolManager()
    # http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=3.0, read=60 * 30))
    if method == 'GET':
        r = http.request('GET', url, headers=headers)
    elif method == 'POST':
        body = json.dumps(data).encode('utf-8')
        r = http.request('POST', url, body=body, headers=headers)

    log.debug(f'http响应码:{r.status}')
    log.debug(f'http响应头:{r.headers}')
    data = r.data
    # log.debug(data)
    return json.loads(data)


def file_path_format(path, file_name):
    pass


def get_datetime():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')


def get_date():
    return datetime.datetime.now().strftime('%Y%m%d')


def get_yearmonth():
    return datetime.datetime.now().strftime('%Y%m')


def format_last_month_this_day(fmt):
    # 获取当前日期
    now_time = datetime.datetime.now()
    # 获取本月的第一天
    end_day_in_mouth = now_time.replace(day=1)
    # 获取上月的最后一天
    next_mouth = end_day_in_mouth - datetime.timedelta(days=1)
    # 返回上月的月份
    return next_mouth.strftime(fmt)


def format_today(fmt):
    return datetime.datetime.now().strftime(fmt)


def format_yesterday(fmt):
    return (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime(fmt)


def format_tomorrow(fmt):
    return (datetime.datetime.now() + datetime.timedelta(days=+1)).strftime(fmt)


def rename_by_datetime(f):
    log.info(f'文件<{f}>加时间戳重命名')
    if os.path.isfile(f):
        time_add = time.strftime(
            '%Y%m%d_%H%M%S', time.localtime(os.path.getmtime(f)))
        path, filename = os.path.split(f)
        filename, extname = os.path.splitext(filename)

        new_file_path = f'{path}\\{filename}_{time_add}{extname}'
        log.info(new_file_path)
        return os.rename(f, new_file_path)
    else:
        log.warning(f'{f}不是正确的文件路径')


if __name__ == '__main__':
    pass
