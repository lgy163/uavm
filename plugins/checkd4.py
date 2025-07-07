from plugins import verify_impl, plugin_return
import sys
import os
from fusionsearch import singleton, log

path_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
path_sys = os.path.join(path_root, "pytorch_nlu", "pytorch_textclassification")
sys.path.append(path_sys)
from pytorch_nlu.pytorch_textclassification.tcPredict import TextClassificationPredict


def max_key_value(predict_rs):
    max_key = max(predict_rs.items(), key=lambda x: x[1])[0]
    return max_key, predict_rs[max_key]


@singleton
class D4Checker():
    def __init__(self, path_config):
        self.tcp = TextClassificationPredict(path_config)

    def check(self, text, logits_type="softmax"):
        log.debug(text)
        res = self.tcp.predict([{"text": text}], logits_type)
        max_key, max_value = max_key_value(res[0])
        if max_key == 'PG' and max_value > 0.5:
            return 'D4', '疑似由人工智能专利生成模型PGM随机生成'
        elif max_key == 'NT' and max_value > 0.95:
            return 'D4', '疑似南通保护中心人工智能编写案件'
        else:
            return None, None


@verify_impl
@plugin_return
def run_verify(index, row):
    claim = row['权利要求'].replace('\n', '').replace(' ', '')
    # max_i = 512 if len(claim) > 512 else len(claim)
    # claim_one = claim[:max_i]
    claim_one = claim
    ret_dict = {}
    if claim_one:
        dc = D4Checker("output/text_classification/model_BERT/tc.config")
        tag, desc_str = dc.check(claim_one)
        if tag is not None:
            ret_dict['D4'] = desc_str + '，存在D4风险；'
    return ret_dict


if __name__ == '__main__':
    log.info('teeeeest444')
