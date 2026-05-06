import logging
import os
from datetime import datetime
from globalVar import LOG_NAME

class Logger:
    def __init__(self):
        self.logger = logging.getLogger(LOG_NAME)
        self.logger.setLevel(logging.DEBUG)
        
        if not self.logger.handlers:
            log_dir = "log"
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.txt")
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def info(self, message):
        self.logger.info(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def debug(self, message):
        self.logger.debug(message)
