import logging
import sys

def setup_logging():
    """設定全域的 Log 環境"""
    
    # 獲取根 logger (root logger)
    # 不指定名稱的 getLogger() 會回傳 root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG) # 預設等級

    # 清除已經存在的 handlers，避免重複設定
    if logger.hasHandlers():
        logger.handlers.clear()

    # 建立一個輸出到檔案的 Handler
    file_handler = logging.FileHandler('app.log', mode='w', encoding='utf-8')
    file_handler.setLevel(logging.INFO) # 寫入檔案的最低等級

    # 建立一個輸出到主控台的 Handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG) # 主控台可以顯示更詳細的 DEBUG 訊息

    # 建立 Log 格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)-18s - %(levelname)-8s - %(message)s'
    )

    # 幫 handlers 設定格式
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # 將 handlers 加入到 logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)