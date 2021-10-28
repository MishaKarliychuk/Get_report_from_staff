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
    get_answer_about_future_plans = State()
    get_answer_opinion_about_day = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Приветствую!')

    Base().insert_user(message.chat.id, message.from_user.first_name)




@dp.message_handler(state=Status.get_answer_about_future_plans)
async def get_answer_about_future_plans(message: types.Message, state: FSMContext):
    Base().update_future_plans_of_user(message.chat.id, message.text)
    await message.answer("Желаю продуктивного дня!")

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
        Base().update_opinion_about_day(message.chat.id, message.text)
        await message.answer("Спасибо, желаю приятного вечера!")
        await state.finish()

@dp.message_handler()
async def mmm(message: types.Message):
    if '/admin' == message.text and message.chat.id in ADMINS:
        await message.answer(f"Всего пользователей - {len(Base().select_all_users())}\nВсего отчетов - {len(Base().select_all_reports())}")
        users = Base().select_all_users()

        with open('reports.csv', 'w') as file:
            for user in users:
                his_reports = Base().select_all_reports_of_user(user[0])
                for report in his_reports:
                    file.write(f'{user[0]}; {user[1]}; {report[2]}; {report[3]}')

            # await message.reply_document(file)
        await bot.send_document(message.chat.id, open('reports.csv', 'r'))
            # await bot.send_document(message.chat.id, ('reports.csv', file))

    elif 'dkasdsadsads' == message.text:
        while True:
            now = datetime.datetime.now()

            future_plan = False
            opinion_about_day = False

            # тек < 8:00
            if now.hour <= HOUR_ASK_ABOUT_FUTURE_PLAN:
                print(f'Время меньше чем {HOUR_ASK_ABOUT_FUTURE_PLAN}   [HOUR_ASK_ABOUT_FUTURE_PLAN] 1')
                future_plan = True
                time_to_sleep = get_time_to_sleep(now.day, HOUR_ASK_ABOUT_FUTURE_PLAN, MINUTE_ASK_ABOUT_FUTURE_PLAN)

            # тек > 18:00
            elif now.hour > HOUR_ASK_OPINION_ABOUT_PLAN:
                print(f'Время больше чем {HOUR_ASK_OPINION_ABOUT_PLAN}   [HOUR_ASK_OPINION_ABOUT_PLAN] 2')
                future_plan = True
                time_to_sleep = get_time_to_sleep(now.day + 1, HOUR_ASK_ABOUT_FUTURE_PLAN, MINUTE_ASK_ABOUT_FUTURE_PLAN)

            # тек > 8:00
            elif now.hour >= HOUR_ASK_ABOUT_FUTURE_PLAN:
                print(f'Время больше чем {HOUR_ASK_ABOUT_FUTURE_PLAN}   [HOUR_ASK_ABOUT_FUTURE_PLAN] 3')
                opinion_about_day = True
                time_to_sleep = get_time_to_sleep(now.day, HOUR_ASK_OPINION_ABOUT_PLAN, MINUTE_ASK_OPINION_ABOUT_PLAN)

            print(f'Спим {time_to_sleep}')
            # time_to_sleep = 5
            await asyncio.sleep(time_to_sleep)
            all_users = Base().select_all_users()

            #"""# Если сообщение отправляется в 8 утра"""
            if future_plan:

                # Делаем рассылку, где спрашиваем о планах на день
                for user in all_users:
                    await bot.send_message(user[0], TEXT_ASK_ABOUT_FUTURE_PLAN)

                    Base().create_report_of_user(user[0])

                    state = dp.current_state(chat=user[0], user=user[0])
                    await state.set_state(Status.get_answer_about_future_plans)

                # Ждем пока пользователи ответят
                await asyncio.sleep(10) # WAITING_FOR_THE_USERS_RESPONSE

                # Проверяем написали ли пользователи отчет, если нет, то напоминаем им
                for user in all_users:
                    print(f"Проверяем пользователя {user[1]}")
                    report = Base().select_report_of_user(user[0])
                    if not report[2]:
                        print("Проверка не пройдена")
                        await bot.send_message(user[0], "Ты что сегодня не работаешь? Напиши планы на день")

                # Ждем пока пользователи ответят
                # await asyncio.sleep(10) # WAITING_FOR_THE_USERS_RESPONSE
                await asyncio.sleep(WAITING_FOR_THE_USERS_RESPONSE) # WAITING_FOR_THE_USERS_RESPONSE

                for user in all_users:
                    print("Делаем для пользователей (которые не ответили)")
                    report = Base().select_report_of_user(user[0])

                    state = dp.current_state(chat=user[0], user=user[0])
                    await state.set_state(Status.main)

                    if not report[2]:
                        Base().update_future_plans_of_user(user[0], "NONE")


                time_to_sleep = get_time_to_sleep(now.day, HOUR_ASK_OPINION_ABOUT_PLAN-1, MINUTE_ASK_OPINION_ABOUT_PLAN)
                # time_to_sleep = 5
                print(f"Процедура закончена, спим к второму вопросу {time_to_sleep}")
                await asyncio.sleep(time_to_sleep)

            #"""# Если сообщение отправляется в 18 вечера"""
            elif opinion_about_day:
                # Делаем рассылку, где спрашиваем как прошел день
                for user in all_users:
                    await bot.send_message(user[0], TEXT_ASK_OPINION_ABOUT_PLAN, reply_markup=key_i_am_working())

                    Base().create_report_of_user(user[0])

                    state = dp.current_state(chat=user[0], user=user[0])
                    await state.set_state(Status.get_answer_opinion_about_day)

                # Ждем пока пользователи ответят
                # await asyncio.sleep(10) # WAITING_FOR_THE_USERS_RESPONSE
                await asyncio.sleep(WAITING_FOR_THE_USERS_RESPONSE) # WAITING_FOR_THE_USERS_RESPONSE

                # Проверяем написали ли пользователи отчет, если нет, то напоминаем им
                for user in all_users:
                    report = Base().select_report_of_user(user[0])
                    if not report[1]:
                        await bot.send_message(user[0], "Как пришел день? Почему молчишь?", reply_markup=key_i_am_working())

                # Ждем пока пользователи ответят
                # await asyncio.sleep(10)
                await asyncio.sleep(WAITING_FOR_THE_USERS_RESPONSE) # WAITING_FOR_THE_USERS_RESPONSE

                for user in all_users:
                    report = Base().select_report_of_user(user[0])

                    state = dp.current_state(chat=user[0], user=user[0])
                    await state.set_state(Status.main)

                    if not report[1]:
                        await Base().update_opinion_about_day(user[0], "NONE")

@dp.callback_query_handler()
async def main(call: CallbackQuery):
    pass



if __name__ == '__main__':
    executor.start_polling(dp)