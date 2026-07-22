from agent.tools.agent_tools import fill_context_for_report
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
from utils.logger_handler import logger
from utils.prompt_loader import load_report_prompts, load_system_prompts
# 监控工具调用过程
@wrap_tool_call
async def monitor_tool(request,handler):
    logger.info(f"函数调用的工具：{request.tool_call['name']}以及传入工具的参数：{request.tool_call['args']}")
    try:
        result = await handler(request)
        logger.info(f"函数调用工具{request.tool_call['name']}成功")
        if request.tool_call['name'] == "fill_context_for_report":
            request.runtime.context["report"] = True
        return result
    except Exception as e:
        logger.error(f"函数调用工具{request.tool_call['name']}失败，错误信息：str{e}")
        raise e
@before_model
def log_before_model(
        state ,          # 整个Agent智能体中的状态记录
        runtime ,           # 记录了整个执行过程中的上下文信息
):         # 在模型执行前输出日志
    logger.info(f"[log_before_model]即将调用模型，带有{len(state['messages'])}条消息。")
    # logger.debug(f"[log_before_model]{type(state['messages'][-1]).__name__} | {state['messages'][-1].content.strip()}")
    return None
@dynamic_prompt   # 每一次在生成提示词之前，调用此函数
def report_prompt_switch(request):
    is_repoet = request.runtime.context.get("report", False)
    if is_repoet:
        return load_report_prompts()
    return load_system_prompts()