import time
from datetime import datetime
import logging
import util.file_utl as file_utl
import atexit

class Logger(logging.Logger):
    _instance = None

    def __new__(cls, appName, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, appName):
        if self._initialized:
            return
        super().__init__(appName)
        self._initialized = True
        self.appName = appName

        # open file for logging with timestamp format: yy_MM_dd-HH_mm
        timestamp   = time.strftime("%y_%m_%d_%H_%M")
        log_dir     = file_utl.get_script_dir()
        log_dir     = log_dir +  '/logs/' + appName
        if not file_utl.file_exists(log_dir):
            file_utl.create_dir(log_dir)

        log_file_name = f"{log_dir}/{appName}_{timestamp}.log"
        self.logfile = open(log_file_name, "w")

        # create symbolic link to latest log file
        latest_log_symlink = f"{log_dir}/{appName}_latest.log"
        if file_utl.file_exists(latest_log_symlink):
            file_utl.remove_file(latest_log_symlink)
        file_utl.create_symbolic_link(log_file_name, latest_log_symlink)

        # log that logger is initialized with appName
        timestamp = self.get_timestamp()
        self.logfile.write(f"\t{timestamp}: Initializing logger for {appName}\n")
        self.logfile.flush()

        # Register the del function to be called on exit
        atexit.register(self.cleanup)


    def get_timestamp(self):
        now = datetime.now()
        return now.strftime("%H:%M:%S") + f".{now.microsecond // 1000:03d}"

    def log(self, message):
        # log with timestamp and message, timestamp format: HH_mm_ss_msms
        timestamp = self.get_timestamp()
        self.logfile.write(f"\t{timestamp}: {message}\n")
        self.logfile.flush()

    def loge(self, message):
        # log with timestamp and message, timestamp format: HHmmss
        timestamp = self.get_timestamp()
        self.logfile.write(f"E\t{timestamp}: {message}\n")
        self.logfile.flush()

    def cleanup(self):
        if hasattr(self, 'logfile'):
            # log that logger is closing
            timestamp = self.get_timestamp()
            self.logfile.write(f"\t{timestamp}: Closing logger\n")
            self.logfile.close()

# Initialize the logger instance
def initialize_logger(appName):
    return Logger(appName)

# Global logging functions
def log(message):
    logger = Logger._instance
    if logger:
        logger.log(message)
    else:
        raise RuntimeError("Logger not initialized")

def loge(message):
    logger = Logger._instance
    if logger:
        logger.loge(message)
    else:
        raise RuntimeError("Logger not initialized")
