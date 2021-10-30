import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.callback_query import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.types import ReplyKeyboardRemove

import asyncio

from key import key_i_am_working, key_when_remind
from mysql_db import Base

import datetime
from pytz import timezone

from services import *
from config import *
from mysql_db import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token=api)
storage = MemoryStorage()
dp = Dispatcher(bot,storage=storage)

# base = Base()

class Status(StatesGroup):
    main = State()
    get_name = State()
    get_answer_about_future_plans = State()
    get_answer_opinion_about_day = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    await message.answer('Здраствуйте, как могу к вам обращаться?')

    await Status.get_name.set()





@dp.message_handler(state=Status.get_name)
async def get_answer_about_future_plans(message: types.Message, state: FSMContext):
        Base().insert_user(message.chat.id, message.text)
        await message.answer(f"Ок, буду к тебе обращаться {message.text}")
        await state.finish()


@dp.message_handler(state=Status.get_answer_about_future_plans)
async def get_answer_about_future_plans(message: types.Message, state: FSMContext):
    Base().create_report_of_user(message.chat.id, message.text)
    await message.answer("Желаю продуктивного дня!")
    await send_report_to_admin(bot, message)
    await state.finish()


@dp.message_handler(state=Status.get_answer_opinion_about_day)
async def get_answer_opinion_about_day(message: types.Message, state: FSMContext):

    if "Еще работаю" == message.text:
        await message.answer('Когда тебе напомнить?', reply_markup=key_when_remind())

    elif 'через 20 мин' == message.text or 'через 30 мин' == message.text or 'через 1 мин' == message.text:
        if 'через 20 мин' == message.text: time = 10*60
        elif 'через 30 мин' == message.text: time = 20*60
        else: time = 30*60
        await asyncio.sleep(time)
        await message.answer('Как прошел день?')

    else:
        Base().create_report_of_user(message.chat.id, message.text)
        await message.answer("Спасибо, желаю приятного вечера!")
        await state.finish()

        await send_report_to_admin(bot, message)

@dp.message_handler()
async def mmm(message: types.Message):
    if '/admin' == message.text and message.chat.id in ADMINS:
        await message.answer(f"Всего пользователей - {len(Base().select_all_users())}\nВсего отчетов - {len(Base().select_all_reports())}")
        create_excel_report()
        await bot.send_document(message.chat.id, open('reports.csv', 'r'))


    elif 'dkasdsadsads' == message.text:
        while True:
            now = datetime.datetime.now(timezone('Poland'))

            future_plan = False
            opinion_about_day = False

            # тек < 8:00
            if datetime.time(now.hour, now.minute) <= datetime.time(HOUR_ASK_ABOUT_FUTURE_PLAN, MINUTE_ASK_ABOUT_FUTURE_PLAN):
                print(f'Время меньше чем {HOUR_ASK_ABOUT_FUTURE_PLAN}   [HOUR_ASK_ABOUT_FUTURE_PLAN] 1')
                future_plan = True
                time_to_sleep = get_time_to_sleep(now.day, HOUR_ASK_ABOUT_FUTURE_PLAN, MINUTE_ASK_ABOUT_FUTURE_PLAN)

            # тек > 18:00
            elif datetime.time(now.hour, now.minute) >= datetime.time(HOUR_ASK_OPINION_ABOUT_PLAN, MINUTE_ASK_OPINION_ABOUT_PLAN):
                print(f'Время больше чем {HOUR_ASK_OPINION_ABOUT_PLAN}   [HOUR_ASK_OPINION_ABOUT_PLAN] 2')
                future_plan = True
                time_to_sleep = get_time_to_sleep(now.day + 1, HOUR_ASK_ABOUT_FUTURE_PLAN, MINUTE_ASK_ABOUT_FUTURE_PLAN)

            # тек > 8:00
            elif datetime.time(now.hour, now.minute) >= datetime.time(HOUR_ASK_ABOUT_FUTURE_PLAN, MINUTE_ASK_ABOUT_FUTURE_PLAN):
                print(f'Время больше чем {HOUR_ASK_ABOUT_FUTURE_PLAN}   [HOUR_ASK_ABOUT_FUTURE_PLAN] 3')
                opinion_about_day = True
                time_to_sleep = get_time_to_sleep(now.day, HOUR_ASK_OPINION_ABOUT_PLAN, MINUTE_ASK_OPINION_ABOUT_PLAN)
                print(now.day, HOUR_ASK_OPINION_ABOUT_PLAN, MINUTE_ASK_OPINION_ABOUT_PLAN)

            print(f'Спим {time_to_sleep}')
            await asyncio.sleep(time_to_sleep)

            # Если сегодня не выходной
            if datetime.datetime.today().weekday() not in [5,6]:
                all_users = Base().select_all_users()

                print("Напоминание пользователям")
                for user in all_users:
                    if user[0] in ADMINS:
                        continue

                    if opinion_about_day:
                        await bot.send_message(user[0], TEXT_ASK_OPINION_ABOUT_PLAN, reply_markup=key_i_am_working())
                        state = dp.current_state(chat=user[0], user=user[0])
                        await state.set_state(Status.get_answer_opinion_about_day)

                    elif future_plan:
                        await bot.send_message(user[0], TEXT_ASK_ABOUT_FUTURE_PLAN)
                        state = dp.current_state(chat=user[0], user=user[0])
                        await state.set_state(Status.get_answer_about_future_plans)

                # Ждем пока пользователи ответят
                await asyncio.sleep(WAITING_FOR_THE_USERS_RESPONSE) # WAITING_FOR_THE_USERS_RESPONSE

                # Проверяем написали ли пользователи отчет, если нет, то напоминаем им
                for user in all_users:
                    if user[0] in ADMINS:
                        continue

                    report = Base().select_report_of_user(user[0])
                    if not report:

                        if opinion_about_day:
                            await bot.send_message(user[0], "Как прошел день? Почему молчишь?", reply_markup=key_i_am_working())
                        elif future_plan:
                            await bot.send_message(user[0], "Ты что сегодня не работаешь? Напиши планы на день")

            else:
                print("Сегодня выходной, ждем будни дни [спим 2 час = 2*60*60]")
                await asyncio.sleep(2*60*60)

            await asyncio.sleep(WAITING_FOR_THE_USERS_RESPONSE)

    elif message.chat.id in ADMINS:
        await message.answer("Вы не можете писать отчет, вы админ /admin")

    else:
        Base().create_report_of_user(message.chat.id, message.text)
        await message.answer("Спасибо за отчет")

        await send_report_to_admin(bot, message)

@dp.callback_query_handler()
async def main(call: CallbackQuery):
    pass



if __name__ == '__main__':
    executor.start_polling(dp)