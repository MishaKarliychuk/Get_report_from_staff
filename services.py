import datetime
from pytz import timezone
from config import ADMINS
import aiogram

from mysql_db import *

def get_time_to_sleep(day, hour, minute):

    now_d = datetime.datetime.now(timezone('Poland'))
    future_date = datetime.datetime(now_d.year, now_d.month, day, hour, minute, tzinfo=timezone('Poland'))
    seconds = (future_date - now_d).total_seconds() - 2160
    return seconds

async def send_report_to_admin(bot, message_obj):
    for admin_id in ADMINS:
        user = Base().select_user(message_obj.chat.id)
        try:
            await bot.send_message(admin_id, f"Отчет от пользователя <b>{user[1]}</b>\n\n{message_obj.text}", parse_mode='html')
        except aiogram.utils.exceptions.ChatNotFound:
            pass

def create_excel_report():
    users = Base().select_all_users()
    with open('reports.csv', 'w') as file:
        file.write(u'Дата; ID в телеграм; Имя в телеграме; Отчет;\n')
        for user in users:
            his_reports = Base().select_all_reports_of_user(user[0])
            for report in his_reports:
                file.write(u'{date}; {user_id}; {user_name}; {report_text};\n'.format(date=report[2], user_id=user[0], user_name=user[1], report_text=report[3]))