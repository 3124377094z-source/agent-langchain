import httpx
from langchain_core.runnables import RunnableConfig
from db.db_config import AsyncSessionLocal
from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
from datetime import datetime
from db import crud
rag = RagSummarizeService()
@tool(description="从产品知识库中检索与用户提问的相关信息并总结回答")
async def rag_summarize(query:str) -> str:
    return await rag.rag_summarize(query)

@tool(description="获取指定城市的天气，以消息字符串的形式返回")
async def get_weather(city: str) -> str:
    url = f"https://wttr.in/{city}"
    data = {"format": "j1", "lang": "zh"}
    try:
        async with httpx.AsyncClient() as client:
            response =  client.get(url, params=data, timeout=5)
            result = response.json()["current_condition"][0]["lang_zh"][0].get("value")
            time = datetime.now().strftime("%Y-%m-%d")
            return f"{time}，{city}的天气为{result}"
    except Exception:
        return f"获取{city}天气信息失败"
@tool(description="获取用户所在城市的名称，以纯字符串形式返回")
async def get_user_location() -> str:
    url = "http://ip-api.com/json/"
    data = {
        "lang": "zh-CN"
    }
    async with httpx.AsyncClient() as client:
        responses = await client.get(url,params=data,timeout=5)
        result = responses.json()
        region_name = result["regionName"]
        city = result["city"]
        return f"省份：{region_name},城市：{city}"

# @tool(description="获取用户的ID，以纯字符串形式返回")
# def get_user_id() -> str:
#     return random.choice(user_ids)

@tool(description="从数据库获取用户的ID，以纯字符串形式返回")
async def get_user_id(config:RunnableConfig) -> str:
    user_id = config.get("configurable", {}).get("user_id", "")
    return str(user_id)
@tool(description="获取当前月份，以纯字符串形式返回")
async def get_current_month() -> str:
    time = datetime.now().strftime("%Y-%m")
    return time

# def generate_external_data():
#     if not external_data:
#         external_data_path = get_abspath(agent_conf["external_data_path"])
#         if not os.path.exists(external_data_path):
#             raise FileNotFoundError(f"外部数据文件{external_data_path}不存在")
#         with open(external_data_path, "r", encoding="utf-8") as f:
#             for line in f.readlines()[1:]:
#                 arr: list[str] = line.strip().split(",")
#                 user_id: str = arr[0].replace('"', "")
#                 feature: str = arr[1].replace('"', "")
#                 efficiency: str = arr[2].replace('"', "")
#                 consumables: str = arr[3].replace('"', "")
#                 comparison: str = arr[4].replace('"', "")
#                 time: str = arr[5].replace('"', "")
#                 if user_id not in external_data:
#                     external_data[user_id] = {}
#                 external_data[user_id][time] = {
#                     "特征": feature,
#                     "效率": efficiency,
#                     "耗材": consumables,
#                     "对比": comparison,
#                 }
# @tool(description="从外部系统中获取指定用户在指定月份的使用记录，以纯字符串形式，如果未检索到返回空字符串")
# def fetch_external_data(query: str, month: str):
#     generate_external_data()
#     try:
#         return external_data[query][month]
#     except KeyError:
#         logger.warning(f"未检索到用户{query}在{month}时的使用记录")
#         return ""
# 从数据库获取用户的信息，使用记录
@tool(description="获取用户在数据库中的使用记录")
async def fetch_external_data(config: RunnableConfig) -> str:
    user_id = config.get("configurable", {}).get("user_id", "")
    if not user_id:
        return ""
    async with AsyncSessionLocal() as session:
        note = await crud.get_user_note(session, user_id)
        return note
@tool(description="无入参，无返回值，调用后触发中间件自动为报告生成的场景动态注入上下文信息，为后续提示词切换提供上下文信息")
async def fill_context_for_report():
    return "fill_context_for_report已调用"