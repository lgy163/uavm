import pandas as pd
import importlib
import pluggy
from plugins import VerifySpec, NAMESPACE, config
from fusionsearch import log

plugin_dir = "plugins"

pm = pluggy.PluginManager(NAMESPACE)
pm.add_hookspecs(VerifySpec)


def register_plugins(pm):
    for module_name in config.plugins:
        module = importlib.import_module(f"{plugin_dir}.{module_name}")
        log.info(f"加载插件{plugin_dir}.{module_name}")
        pm.register(module)


register_plugins(pm)


def df_to_be_checked(df, tags):
    aps = []
    with open(r'out/综合验证.txt', 'r') as f:
        for line in f:
            aps.append(line.split(' ')[0].replace('\n',''))
            tags.append([line.split(' ')[0].replace('\n',''),line.split(' ')[1].replace('\n',''),line.split(' ')[2].replace('\n','')])
    print(aps)
    filter_df = df[~df['申请号'].isin(aps)]
    print(filter_df)
    return filter_df


def verify(df, **kwargs):
    tags = []
    pb = kwargs.get('progress_bar', None)

    df = df_to_be_checked(df, tags)

    i = 0
    for index, row in df.iterrows():
        pm.hook.pre_verify(index=index, row=row)

        ret_list = pm.hook.run_verify(index=index, row=row)

        ap = row['申请号']
        tm_dict = {}
        for d in ret_list:
            if not list(d.values())[0]:
                continue
            for k, v in list(d.values())[0].items():
                tm_v = tm_dict.get(k, None)
                tm_dict[k] = tm_v + v if tm_v else v

        str_tags = ''
        str_desc = ''
        for k, v in tm_dict.items():
            str_tags = k if not str_tags else str_tags + '|' + k
            str_desc += v
        tags.append([ap, str_tags, str_desc])
        with open(r'out/综合验证.txt', 'a') as f:
            f.write(f'{ap} {str_tags} {str_desc}\n')
        if pb:
            pb.progress((i + 1) / len(df))
            i += 1
    # if pb:
    #     st.experimental_set_query_params(progress=1.0)
    #     st.success("恭喜你，所有的案件都已经检测完成！")
    pm.hook.after_verify(df=df, tags=tags)

    return tags


if __name__ == '__main__':
    df = pd.read_excel(r'data/综合验证.xlsx')

    r = verify(df, progress_bar=None)

    columns = ['申请号', '标签', '说明']
    df_out = pd.DataFrame(r, columns=columns)
    df_out.to_excel(r'out/综合验证结果.xlsx')
