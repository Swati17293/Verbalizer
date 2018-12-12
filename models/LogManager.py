import logging
from logging.handlers import RotatingFileHandler

class LogManager(object):
    logger = None
    
    @staticmethod
    def init():
        logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            filename="logs.txt", 
                            filemode='w', 
                            datefmt='%d/%m/%Y %I:%M:%S %p',
                            level=logging.INFO)
        LogManager.logger = logging.getLogger(__name__)

    @staticmethod
    def LogInfo(info):
        LogManager.logger.info(info)
    
    @staticmethod
    def LogWarning(warning):
        LogManager.logger.warning(warning)
    
    @staticmethod
    def LogError(error):
        LogManager.logger.error(error)
    
