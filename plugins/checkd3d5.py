from datetime import datetime, timedelta
# import datetime
from fusionsearch import FusionSearcher
from plugins import verify_impl, plugin_return
import pandas as pd
import re


def checkAge(curr_row):
    age = str(curr_row['发明人年龄'])
    if pd.isna(float(age)):
        return False
    for curr_age in (age.split('，')):
        if int(float(curr_age)) < 18:
            return True

    return False


def checkInvestment(curr_row):
    inves = str(curr_row['实缴资本'])
    for curr_inves in (inves.split('，')):
        if not pd.isna(float(curr_inves)) and float(curr_inves) < 200:
            return True
    return False


def checkEmployee(curr_row):
    emp = str(curr_row['申请人参保人数'])
    for curr_emp in (emp.split('，')):
        if not pd.isna(float(curr_emp)) and float(curr_emp) < 20:
            return True
    return False


def checkApplicant(curr_row):
    applicants = curr_row['申请人']
    univst = 0
    univst_211985 = 0
    individual = 0
    enterprise = 0
    keywords_univst = ['大学', '学院', '研究所', '实验室']
    keywords_985211 = ['清华大学', '北京大学', '中国人民大学', '北京理工大学', '北京航空航天大学',
                       '中央民族大学', '北京师范大学', '中国农业大学']
    keywords_entprs = ['公司', '会社']
    for curr_applicant in (applicants.split('，')):
        if any(kword_1 in curr_applicant for kword_1 in keywords_univst):
            univst += 1
            if any(kword_2 in curr_applicant for kword_2 in keywords_985211):
                univst_211985 += 1

        elif (any(kword_3 in curr_applicant for kword_3 in keywords_entprs)
              or len(curr_applicant) > 4):
            enterprise += 1
        else:
            individual += 1
    return [univst, univst_211985, individual, enterprise]


def checkClaim(curr_row):
    claim_1 = curr_row['权利要求']
    claim_1 = re.sub('\s|\n|\t', '', claim_1)
    pattern = r'\d+\..*?。'
    match = re.findall(pattern, claim_1)
    if len(match) > 0:
        claim_1 = match[0]
        if pd.isna(claim_1):
            return False
        curr_applicant = checkApplicant(curr_row)
        if len(claim_1.encode('utf-8')) / 3 > 1000*0.95 and curr_applicant[1] == 0:
            return True
        else:
            return False


def checkIPC(resultList, curr_applcnt):
    if resultList == []:
        return False
    ipc_set = set()
    for i in range(len(resultList)):
        curr_ipc = resultList[i].get('ipcMain', None)
        if curr_ipc == None:
            continue
        else:
            if len(curr_ipc)>0:
                ipc_set.add(curr_ipc[0])
        if len(ipc_set) > 1 and curr_applcnt[2] != 0:
            return True
    return False


def date_scope(apd):
    # 将日期格式的字符串转换为datetime对象
    the_date = datetime.strptime(str(apd), '%Y%m%d')
    # 计算5天后的日期
    date_after_5_days = the_date + timedelta(days=5)
    # 计算5天前的日期
    date_before_5_days = the_date - timedelta(days=5)
    return date_before_5_days.strftime('%Y%m%d'), date_after_5_days.strftime('%Y%m%d')


def search(row, **args):
    fs = FusionSearcher()
    apd = row['申请日']
    pa = row['申请人']
    pa = pa.replace('(','"("').replace(')','")"')
    start_date, end_date = date_scope(apd)
    sr = fs.search(f'{pa}/pa and apd>{start_date} and apd<{end_date}', 'fusion', size=100)
    if sr:
        return sr['resultList']
    else:
        return None


@verify_impl
@plugin_return
def run_verify(index, row):
    curr_search_result = search(row)

    ret_dict = {}
    d3_desc = ''
    d5_desc = ''
    if checkAge(row):
        d3_desc += "申请人年龄小于18周岁，存在D3风险;"

    if checkInvestment(row):
        d3_desc += "实缴资本小于200万，存在D3风险;"

    if checkEmployee(row):
        d3_desc += "参保人数20人以下，存在D3风险;"

    if checkClaim(row):
        d5_desc += "权利要求字数过千且非211/985申请，存在D5风险;"

    applcnt = checkApplicant(row)
    if curr_search_result:
        if checkIPC(curr_search_result, applcnt):
            d3_desc += "申请人疑似同日申请多个不同领域的专利;"

    if len(d3_desc.strip()) > 0:
        ret_dict['D3'] = d3_desc

    if len(d5_desc.strip()) > 0:
        ret_dict['D5'] = d5_desc

    return ret_dict

# @verify_impl
# def after_verify(self, row, **args):
#     print("处理识别结果")
