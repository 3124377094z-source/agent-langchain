import logging
import os
# from datetime import datetime
from utils.path_tool import get_abspath
# 日志存放的根目录
LOG_ROOT = get_abspath('log')
# 确保日志的目录存在
os.makedirs(LOG_ROOT, exist_ok=True)
# 日志格式配置
Formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
def get_logger(logger_name:str = "agent", log_file = None) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    # 避免重复添加handler
    if logger.handlers:
        return logger
    # 控制台Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(Formatter)
    logger.addHandler(console_handler)
    # 文件Handler
    if not log_file:
        log_file = os.path.join(LOG_ROOT, logger_name + '.log')
    file_handler = logging.FileHandler(log_file,encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(Formatter)
    logger.addHandler(file_handler)

    return logger
logger = get_logger()
if __name__ == '__main__':
    logger.debug('debug')