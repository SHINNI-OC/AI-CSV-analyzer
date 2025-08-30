from http.client import responses

import streamlit as st
from utils import dataframe_agent
import pandas as pd

# 定义画图函数
def create_chart(input_data, chart_type):
    df_data = pd.DataFrame(
        input_data["data"],
        columns = input_data["columns"]
    )
    df_data.set_index(input_data["columns"][0], inplace=True)
    if chart_type == "bar":
        st.bar_chart(df_data)
    if chart_type == "line":
        st.line_chart(df_data)
    elif chart_type == "scatter":
        st.scatter_chart(df_data)

# 标题
st.title("CSV数据分析工具")

# 侧边栏
with st.sidebar:
    api_key = st.text_input("请输入你的OpenAI API Key：", type="password")
    api_base = st.text_input("请输入你的OpenAI API Base URL：", type="default")

data = st.file_uploader("上传CSV文件", type="csv")

# 交互区
if data:
    st.session_state["df"] = pd.read_csv(data)
    with st.expander("原始数据"):
        st.dataframe(st.session_state["df"])

query = st.text_area("请输入你关于以上表格的问题，或数据提取请求，或可视化要求(支持散点图、折线图、条形图")
button = st.button("生成回答")

if button and not (api_key or api_base):
    st.info("请输入密钥和api base url")

if button and "df" not in st.session_state:
    st.info("请先上传文件")

if button and "df" in st.session_state and api_base and api_key:
    with st.spinner("AI正在思考中，请稍后……"):
        response_dic = dataframe_agent(api_key, api_base, st.session_state["df"], query)
        if "answer" in response_dic:
            st.write(response_dic["answer"])
        if "table" in response_dic:
            st.table(pd.DataFrame(response_dic["table"]["data"],
                                  columns=response_dic["table"]["columns"]))
        if "bar" in response_dic:
            create_chart(response_dic["bar"],"bar")
        if "line" in response_dic:
            create_chart(response_dic["line"],"line")
        if "scatter" in response_dic:
            create_chart(response_dic["scatter"],"scatter")
