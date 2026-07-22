from langchain.agents import create_agent
from model.factory import chat_model
from agent.tools.agent_tools import (rag_summarize, get_weather, get_user_location, get_user_id,
                                     get_current_month, fetch_external_data, fill_context_for_report)
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch
from utils.prompt_loader import load_system_prompts
from db.db_model import User
class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model = chat_model,
            system_prompt= load_system_prompts(),
            tools=[rag_summarize, get_weather, get_user_location, get_user_id,get_current_month, fetch_external_data, fill_context_for_report],
            middleware=[monitor_tool, log_before_model, report_prompt_switch]
        )
        #实现agent的流式输出
    async def execute_stream(self, query: str, user:User):
        input_dic = {
            "messages": [
                {"role": "user", "content": query},
            ]
        }
        # 把用户信息放入 configurable，工具里可以读取
        config = {
            "configurable": {
                "user_id": user.user_id,
            }
        }
        # 第三个参数context就是上下文runtime中的信息，就是我们做提示词切换的标记
        async for chunk in self.agent.astream(input_dic, stream_mode="values", context={"report": False}, config=config):
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                yield latest_message.content.strip() + "\n"
agent_chat = ReactAgent()
if __name__ == '__main__':
   agent = ReactAgent()
   agent.execute_stream("扫地机器人")