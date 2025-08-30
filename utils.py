from langchain.chains.flare.prompts import PROMPT_TEMPLATE
from langchain_experimental.llms.anthropic_functions import prompt
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import json
# import os
# import pandas as pd


def dataframe_agent(api_key, api_base, df, query):

    model = ChatOpenAI(
        model="gpt-3.5-turbo",
        openai_api_key=api_key,
        openai_api_base=api_base,
        temperature=0
    )

    agent = create_pandas_dataframe_agent(
        llm=model,
        df=df,
        agent_executor_kwargs={"handle_parsing_errors": True},  # 修正拼写错误：handel -> handle
        verbose=True
    )

    PROMPT_TEMPLATE = """
    你是一位数据分析专家，你会被给予一个DataFrame和一些问题，请根据DataFrame和问题使用中文进行回答。
    1. 对于文字回答的问题，回答格式如下：
    {"answer": "<你的答案写在这里>"}
    例如：
    {"answer": "订单量最高的产品ID是'MNWC3-067'"}

    2. 如果用户需要一个表格，回答格式如下：
    {"table": 
    {"columns":["column1", "column2",...] ,
     "data":[["value1", "value2", ...], ["value1", "value2", ...],...]}
     }
     3. 如果用户的请求适合返回条形图，按照这样的格式回答：
     "bar": {"columns": ["A", "B", "C", ...], "data": [34, 21, 91, ...] }}

     4. 如果用户的请求适合返回折线图，按照这样的格式回答：
     {"line": {"columns": ["A", "B", "C", ...], "data": [34, 21, 91, ...]}}

     5. 如果用户的请求适合返回散点图，按照这样的格式回答：
     {"scatter": {"columns": ["A", "B", "C", ...], "data": [34, 21, 91, ...]}}

     注意：我们只支持三种类型的图表："bar", "line" 和 "scatter"。

     请将所有输出作为JSON字符串返回。请注意要将"columns"列表和数据列表中的所有字符串都用双引号包围。

     例如：{"columns": ["Products", "Orders"], "data": [["32085Lip", 245], ["76439Eye", 178]]}

     你要处理的用户请求如下： 
     """
    prompt = PROMPT_TEMPLATE + query
    response = agent.invoke({"input": prompt})

    # 添加错误处理，防止JSON解析失败
    try:
        response_dict = json.loads(response["output"])
    except json.JSONDecodeError:
        # 如果返回的不是标准JSON，直接返回原始响应
        response_dict = {"answer": response["output"]}

    return response_dict


# # 修复文件路径转义问题
# df = pd.read_csv(r"D:\desktop\large_model_application_development\CSV-analyzer\personal_data.csv")
#
# # 检查API密钥是否存在
# api_key = os.environ.get("OPENAI_API_KEY")
# if not api_key:
#     print("错误: 请设置 OPENAI_API_KEY 环境变量")
# else:
#     result = dataframe_agent(api_key, df, "数据里出现最多的职业是什么？")
#     print(result)