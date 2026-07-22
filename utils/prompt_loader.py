from utils.config_handler import prompts_conf
from utils.path_tool import get_abspath
from utils.logger_handler import logger


def load_system_prompts():
    """
    通过get_abspath组成系统提示词的绝对路径，文件路径不存在可以捕获错误，在用with open读出提示词文件内容，可捕获文件内容解析错误的错误
    :return: str
    """
    try:
        system_prompt_path = get_abspath(prompts_conf["main_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_system_prompts]在yaml配置项中没有main_prompt_path配置项")
        raise e
    try:
        return open(system_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_system_prompts]解析系统提示词出错，{str(e)}")
        raise e
def load_rag_prompts():
    try:
        rag_prompt_path = get_abspath(prompts_conf["rag_summarize_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_rag_prompts]在yaml配置项中没有rag_summarize_prompt_path配置项")
        raise e
    try:
        return open(rag_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_rag_prompts]解析RAG总结提示词出错，{str(e)}")
        raise e
def load_report_prompts():
    try:
        report_prompt_path = get_abspath(prompts_conf["report_prompt_path"])
    except KeyError as e:
        logger.error(f"[load_report_prompts]在yaml配置项中没有report_prompt_path配置项")
        raise e
    try:
        return open(report_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_report_prompts]解析报告生成提示词出错，{str(e)}")
        raise e
if __name__ == '__main__':
    print(load_report_prompts())

