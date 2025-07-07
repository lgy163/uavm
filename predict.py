# !/usr/bin/python
# -*- coding: utf-8 -*-
import re
import sys
import os
import pandas as pd


from fusionsearch import singleton, log

path_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
path_sys = os.path.join(path_root, "pytorch_nlu", "pytorch_textclassification")
sys.path.append(path_sys)
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
from pytorch_nlu.pytorch_textclassification.tcPredict import TextClassificationPredict

# log = Logger(r'uavm-all.log', level='debug').logger


def read_claims():
    df = pd.read_excel(r'data/D3&D5数据集.xlsx')
    claims = []
    for i in range(df.shape[0]):
        # for i in range(10):
        item = df.iloc[i]
        claim = item['权利要求'].replace('\n', '').replace(' ', '')
        a = re.findall("^1\\.(.+)。3\\.", claim)
        if len(a) > 0:
            claim_one = a[0]
            claims.append('1.' + claim_one + '。')
    return claims


def max_key_value(predict_rs):
    max_key = max(predict_rs.items(), key=lambda x: x[1])[0]
    return max_key, predict_rs[max_key]


@singleton
class D4Checker():
    def __init__(self, path_config):
        # path_config = "output/text_classification/model_BERT/tc.config"
        self.tcp = TextClassificationPredict(path_config)

    def check(self, text, logits_type="softmax"):
        log.info(text)
        res = self.tcp.predict([{"text": text}], logits_type)
        max_key, max_value = max_key_value(res[0])
        # log.info(max_key, max_value)
        if max_key == 'PG' and max_value > 0.5:
            return 'D4', '疑似由人工智能专利生成模型PGM随机生成'
        elif max_key == 'NT' and max_value > 0.95:
            return 'D4', '疑似南通保护中心人工智能编写案件'
        else:
            return None, None


if __name__ == "__main__":
    path_config = "output/text_classification/model_BERT/tc.config"
    tcp = TextClassificationPredict(path_config)
    claims = read_claims()
    texts = [{"text": x} for x in claims]

    # res = tcp.predict(texts, logits_type="softmax")
    # for r in res:
    #     max_key_value(r)
    # print(res)
    while True:
        print("请输入:")
        question = input()
        res = tcp.predict([{"text": question}], logits_type="softmax")
        print(res)
