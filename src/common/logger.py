import logging
import sys

def setup_logger():
  logger = logging.getLogger("SCIChecker")
  logger.setLevel(logging.DEBUG)
  if logger.hasHandlers(): # para no duplicar mensajes
    logger.handlers.clear()
  
  consoleHandler = logging.StreamHandler(sys.stdout) # mensajes a consola
  consoleHandler.setLevel(logging.INFO) # muestra INFO, WARNING, ERROR, CRITICAL

  fileHandler = logging.FileHandler("sci_checker_run.log", mode='w', encoding='utf-8')
  fileHandler.setLevel(logging.DEBUG) # mensajes al archivo
    
  consoleFormat = logging.Formatter('%(levelname)s: %(message)s') # formato del texto en consola
  consoleHandler.setFormatter(consoleFormat)

  fileFormat = logging.Formatter('%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s')
  fileHandler.setFormatter(fileFormat)

  logger.addHandler(consoleHandler)
  logger.addHandler(fileHandler)
  return logger