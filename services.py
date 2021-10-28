import datetime
from pytz import timezone
from config import ADMINS
import aiogram

def get_time_to_sleep(day, hour, minute):

    now_d = datetime.datetime.now(timezone('Poland'))
    future_date = datetime.datetime(now_d.year, now_d.month, day, hour, minute, tzinfo=timezone('Poland'))
    seconds = (future_date - now_d).total_seconds() - 2160
    return seconds

async def send_report_to_admin(bot, message_obj):
    for admin_id in ADMINS:
        try:
            await bot.send_message(admin_id, f"Отчет от пользователя <b>{message_obj.from_user.first_name}</b>\n\n{message_obj.text}", parse_mode='html')
        except aiogram.utils.exceptions.ChatNotFound:
            pass