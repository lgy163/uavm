from datetime import datetime, timedelta
# import datetime
from fusionsearch import FusionSearcher
from plugins import verify_impl, plugin_return
import pandas as pd
import difflib


def string_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


# def list_appendD1D2(ls, sn, ap, rz):
#     if len(ls):
#         for i in range(len(ls)):
#             if rz in ls[i]:
#                 # ls[i].append(ap)
#                 ls[i][0] = ls[i][0] + ',' + ap
#                 return sn
#         ls.append([])
#         sn = sn + 1
#         ls[sn].append(ap)
#         ls[sn].append(rz)
#     else:
#         ls.append([])
#         ls[0].append(ap)
#         ls[0].append(rz)
#     return sn




def search(row, **args):
    fs = FusionSearcher()
    ap = row['申请号']
    sr = fs.search(ap, 'semantic', size=10)
    if sr:
        return sr['resultList']
    else:
        return None

@verify_impl
@plugin_return
def run_verify(index, row):
    curr_search_result = search(row)

    ret_dict = {}
    d1_desc = ''
    d2_desc = ''

    if curr_search_result:
        for i in curr_search_result:
            if i['simVal'] == 100:  # 本申请
                sqd = datetime.strptime(i['apd'][:10], '%Y.%m.%d')
                ipc = i['ipcMain']
                ti = i['ti']
            if (i['simVal'] > 95) and (i['simVal'] < 100):  # simVal阈值
                # if i['pa'] == sqr:  # 申请人相同
                if abs((datetime.strptime(i['apd'], '%Y.%m.%d') - sqd).days) <= 180:  # 申请日区间阈值
                    if i['ipcMain'] == ipc:  # ipc分类号相同
                        if (string_similar(i['ti'], ti)) > 0.5:  # 发明名称相似
                            d1_desc += f'与{i["anId"]}内容相似、先后申请、ipc分类号相同、发明名称相似，存在D1风险；'
                        else:
                            d1_desc += f'与{i["anId"]}内容相似、先后申请、ipc分类号相同，存在D1风险；'
                    else:
                        if (string_similar(i['ti'], ti)) > 0.5:  # 发明名称相似
                            d1_desc += f'与{i["anId"]}内容相似、先后申请、发明名称相似，存在D1风险；'
                elif abs((datetime.strptime(i['apd'], '%Y.%m.%d') - sqd).days) > 180:
                    if (i['ipcMain'] == ipc) and ((string_similar(i['ti'], ti)) > 0.5):
                        d1_desc += f'与{i["anId"]}内容相似、ipc分类号相同、发明名称相似，存在D1风险；'
                if (abs((datetime.strptime(i['apd'], '%Y.%m.%d') - sqd).days) > 180) and (
                        i['ipcMain'] != ipc) and ((string_similar(i['ti'], ti)) <= 0.5):
                    d2_desc += f'与{i["anId"]}内容相似，但非先后申请、ipc分类号不同、发明名称不同，存在D2风险；'

    if len(d1_desc.strip()) > 0:
        ret_dict['D1'] = d1_desc

    if len(d2_desc.strip()) > 0:
        ret_dict['D5'] = d2_desc

    # return {__name__: ret_dict}
    return ret_dict

# @verify_impl
# def after_verify(self, index, row, **args):
#     print("处理识别结果")
