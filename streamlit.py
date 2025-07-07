import streamlit as st
import pandas as pd

import time

from main import verify


def process_data(df, progress_bar):
    # 模拟数据处理，每处理一行数据休眠0.1秒
    tx = st.text('')
    for i in range(len(df)):
        time.sleep(0.1)
        progress_bar.progress((i + 1) / len(df))
        # text = f"正在处理第{i+1}行数据."
        # tx.text(text)
    st.experimental_set_query_params(progress=1.0)
    st.success("恭喜你，所有的案件都已经检测完成！")
    return df


# 读取Excel文件
uploaded_file = st.file_uploader("请选择包含待检测案件信息的Excel文件：", type=["xlsx", "xls"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # 显示原始数据框
    st.write("你导入的数据:")
    st.write(df)

    # 显示“开始检测”按钮
    if st.button("开始检测"):
        progress_bar = st.progress(0.0)
        # 处理数据框
        # processed_df = process_data(df, progress_bar)
        r = verify(df, progress_bar=progress_bar)

        columns = ['申请号', '标签', '说明']
        df_out = pd.DataFrame(r, columns=columns)
        # df_out.to_excel('out/test.xlsx', index=False)

        # df_out = pd.read_excel('结果样例.xlsx')
        # 显示处理后的数据框
        st.write("以下是检测结果:")
        st.write(df_out)
