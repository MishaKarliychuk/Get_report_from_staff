import datetime

def get_time_to_sleep(day, hour, minute):

    now_d = datetime.datetime.now()
    future_date = datetime.datetime(now_d.year, now_d.month, day, hour, minute)
    seconds = (future_date - now_d).total_seconds()

    return seconds

get_time_to_sleep(26, 18, 22)