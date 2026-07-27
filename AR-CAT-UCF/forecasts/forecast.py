from logging.syslogger import log

class ForecastManager():
    def __init__(self):
        log.info("initializing the forecast manager")
        
    def run(self): # The forecast manager will manage the things in the forecast section.
        log.info(f"Running the forecast manager")