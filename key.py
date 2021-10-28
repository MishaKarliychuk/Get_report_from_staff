from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton
# from config import admin
import random

# инлайнова кнопка
def join():
    key = InlineKeyboardMarkup()
    b1 = InlineKeyboardButton(text='Присоединится', callback_data=f'join')   # инлайнова кнопка
    key.row(b1)
    return key

def key_i_am_working():
    key = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton('Еще работаю')
    key.row(b1)
    return key

def key_when_remind():
    key = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton('через 20 мин')
    key.row(b1)
    b1 = KeyboardButton('через 30 мин')
    key.row(b1)
    b1 = KeyboardButton('через 1 час')
    key.row(b1)
    return key