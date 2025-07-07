import random
from time import sleep

from fusionsearch import utils
from fusionsearch import log
from fusionsearch import utils as U
from fusionsearch import login as L
# from functools import wraps

from fusionsearch.utils import singleton


def search_for(wb, key, size=20):
    log.info(f'开始检索“{key}”，返回Size为{size}')
    headers = get_headers(wb)

    executeSearch = 'http://10.160.28.16/api/neusipo-app-search/fusionSearch/new/action/executeSearch'
    data = {"dbs": ["DB201"], "start": 0, "size": size, "searchType": "boolean", "viewMode": "1", "hitCounts": 0,
            "ssId": "",
            "showAbsFlag": "0", "showDescImageFlag": "0", "rdiDate": "", "complexChinese": False,
            "rootSearch": "GENERAL",
            "twSearch": "OFF", "crossSearch": "OFF", "searchModel": "TABLE_SEARCH",
            "semanticParam": {"top": "400", "boolterm": key, "rdiflag": False, "eid": ""}, "fromSource": "boolean"}
    r = utils.request(executeSearch, 'POST', data=data, headers=headers)
    log.info(r)
    t = r['t']

    forOverview = 'http://10.160.28.16/api/neusipo-app-search/fusionSearch/new/forOverview'
    data = {"dbs": ["DB201"], "start": 0, "size": size, "searchType": "boolean", "viewMode": "1", "hitCounts": 0,
            "ssId": t, "showAbsFlag": "0", "showDescImageFlag": "0", "rdiDate": "",
            "complexChinese": False, "rootSearch": "GENERAL", "twSearch": "OFF", "crossSearch": "OFF",
            "searchModel": "TABLE_SEARCH",
            "semanticParam": {"top": "400", "boolterm": key, "rdiflag": False, "eid": "", "stxt": ""}}
    r = utils.request(forOverview, 'POST', data=data, headers=headers)

    filter_keys = ['ssId', 'resultList']
    r_data = {k: v for k, v in r['t'].items() if k in filter_keys}
    log.debug(r_data)
    return r_data


def get_headers(wb):
    cookies = wb.get_cookies()
    cookie_str = ";".join([f'{x["name"]}:{x["value"]}' for x in cookies])
    authorization_token = 'Bearer ' + wb.get_cookie(name="neusipo_token")['value']

    headers = {
        'Host': '10.160.28.16',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'Authorization': authorization_token,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'http://10.160.28.16',
        'Referer': 'http://10.160.28.16/search',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': cookie_str
    }
    return headers


def result(wb, ssid, start=0, size=20):
    log.info(f'通过{ssid}获取检索结果')
    headers = get_headers(wb)
    url = 'http://10.160.28.16/api/neusipo-app-search/fusionResult/results'
    data = {"viewMode": "1", "start": start, "size": size, "lang": "1", "ssId": "9920b6bbec014243b710e183abe27059",
            "statDbs": [], "showAbsFlag": "0", "showDescImageFlag": "0", "statParams": [], "ifStat": 0,
            "sortField": ["", ""]}

    r = utils.request(url, 'POST', data=data, headers=headers)
    for rs in r['t']['resultList']:
        log.info(f'{rs["anId"]}-{rs["ti"]}-{rs["ipcMain"]}')

    filter_keys = ['ssId', 'resultList']
    r_data = {k: v for k, v in r['t'].items() if k in filter_keys}
    return r_data


def fusion_search(key, start=0, size=20, ssid=None):
    wb = utils.get_chrome()
    wb.implicitly_wait(30)

    r = []
    log.info(wb.title)
    if wb.title == '融合检索':
        if ssid is None:
            r = search_for(wb, key, size)
        else:
            r = result(wb, ssid, start, size)

    return r


def add_element(wb, sno, stxt):
    url = 'http://10.160.28.16/api/neusipo-app-search/element/addElement'
    headers = get_headers(wb)
    data = {"sno": sno, "stxt": stxt}
    r = utils.request(url, 'POST', data=data, headers=headers)

    if r['status'] != 200:
        log.error('添加语义基准出错')
        return None
    else:
        log.info(r['message'])
        return r['t']


def semantic_search(wb, t, start=0, size=20):
    url = 'http://10.160.28.16/api/neusipo-app-search/fusionSearch/new/forOverview'
    headers = get_headers(wb)
    data = {"dbs": ["DB201"], "start": start, "size": size, "searchType": "semantic", "viewMode": "1", "hitCounts": 0,
            "showAbsFlag": "0", "showDescImageFlag": "0", "rdiDate": "", "complexChinese": False,
            "rootSearch": "GENERAL", "twSearch": "OFF", "crossSearch": "OFF",
            "semanticParam": {"top": "400", "boolterm": "", "rdiflag": False, "eid": t, "stxt": ""}}
    log.debug(data)
    r = utils.request(url, 'POST', data=data, headers=headers)
    filter_keys = ['eId', 'resultList']
    r_data = None
    if r.get('t', None) is not None:
        r_data = {k: v for k, v in r['t'].items() if k in filter_keys}

    return r_data


def delete_search_statement_all(wb):
    r_num = random.randint(0, 100)
    if r_num <= 1:
        log.info('清空所有检索式')
        url = 'http://10.160.28.16/api/neusipo-app-search/retrievalApi/deleteSearchStatementAll'
        headers = get_headers(wb)
        data = {}
        utils.request(url, 'POST', data=data, headers=headers)


@singleton
class FusionSearcher():
    def __init__(self, url=None):
        if url is not None:
            self.url = url
        else:
            self.url = 'http://10.160.28.16/uniLogin'

        self.driver = U.get_chrome()
        self.driver.get(self.url)
        self.driver.implicitly_wait(30)
        sleep(3)

        if self.driver.title != '融合检索':
            L.login_by_n_time(3, url=self.url, driver=self.driver)
        else:
            log.info('融合检索系统已经打开')

    def search(self, key, search_type, size=20, start=0, ssid=None, eid=None):
        try:
            delete_search_statement_all(self.driver)
            if search_type.lower() == 'fusion':
                return fusion_search(key, start, size, ssid)
            elif search_type.lower() == 'semantic':
                if eid is not None:
                    t = eid
                else:
                    t = add_element(self.driver, key, '')

                return semantic_search(self.driver, t, start, size)
            else:
                log.error(f'search_type错误：{search_type}')
                return None
        except Exception as e:
            log.error(e)
            return None


if __name__ == '__main__':
    # wb = utils.get_chrome()
    # t = add_element(wb, 'CN111611866A', '')
    # if t is not None:
    #     r = semantic_search(wb, t)
    #     with open('out/r.json','w+', encoding='utf-8') as f:
    #         f.write(str(r))
    r = fusion_search('南通米兰特电气有限公司/pa and apd>20220415 and apd<20220425')
    # with open('out/pa.json', 'w+', encoding='utf-8') as f:
    #     f.write(str(r))
    log.info(r)
