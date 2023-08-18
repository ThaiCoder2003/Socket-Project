from file_config import config

config_info = config()

from datetime import datetime

def TimeLimit():
    currentDateAndTime = datetime.now()
    float=currentDateAndTime.hour+currentDateAndTime.minute/60
    return (float>=config_info['time_in'] and float<=config_info['time_out'])


