from file_config import config

config=config()

from datetime import datetime

def TimeLimit():
    currentDateAndTime = datetime.now()
    float=currentDateAndTime.hour+currentDateAndTime.minute/60
    return (float>=config['time_in'] and float<=config['time_out'])


