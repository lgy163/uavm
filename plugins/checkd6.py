from plugins import verify_impl, plugin_return
import pandas as pd


@verify_impl
def after_verify(df, tags):
    result = df.groupby('联系人').filter(lambda x: x['申请人'].nunique() > 1)
    if len(result) > 0:
        ap_list = result['申请号'].values.tolist()
        for tag in tags:
            if tag[0] in ap_list:
                if not tag[1]:
                    tag[1] = 'D6'
                elif 'D6' in tag[1]:
                    pass
                else:
                    tag[1] += '|D6'
                tag[2] += '同一个联系人对应多个不同申请人，存在D6的风险；'
    result = df.groupby('联系电话').filter(lambda x: x['申请人'].nunique() > 1)
    if len(result) > 0:
        ap_list = result['申请号'].values.tolist()
        for tag in tags:
            if tag[0] in ap_list:
                if not tag[1]:
                    tag[1] = 'D6'
                elif 'D6' in tag[1]:
                    pass
                else:
                    tag[1] += '|D6'
                tag[2] += '同一个联系电话对应多个不同申请人，存在D6的风险；'
    result = df.groupby('缴费地址').filter(lambda x: x['申请人'].nunique() > 1)
    if len(result) > 0:
        ap_list = result['申请号'].values.tolist()
        for tag in tags:
            if tag[0] in ap_list:
                if not tag[1]:
                    tag[1] = 'D6'
                elif 'D6' in tag[1]:
                    pass
                else:
                    tag[1] += '|D6'
                tag[2] += '同一个缴费地址对应多个不同申请人，存在D6的风险；'


if __name__ == '__main__':
    df = pd.read_excel(r'../data/D6-0817.xlsx')
    after_verify(df, None)