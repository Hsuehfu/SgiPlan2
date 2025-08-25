import logging
import sys
from logging import handlers

def setup_logging():
    """設定全域的 Log 環境"""
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    # 使用 RotatingFileHandler，設定檔案大小上限為 1MB，保留 5 個備份
    file_handler = handlers.RotatingFileHandler(
        'app.log', 
        maxBytes=1024*1024, 
        backupCount=5, 
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)-18s - %(levelname)-8s - %(message)s'
    )

    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)