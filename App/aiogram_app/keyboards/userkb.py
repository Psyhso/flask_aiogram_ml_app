from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

reg_log_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Регистрация')], [KeyboardButton(text='Вход в аккаунт')]],
                           resize_keyboard=True, one_time_keyboard=True,
                           input_field_placeholder='Если у вас нет аккаунта, вы можете его создать, иначе залогиньтесь')


log_in_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Профиль'), KeyboardButton(text='Предсказать сорт ириса')], [KeyboardButton(text='Выйти')]],
                           resize_keyboard=True, one_time_keyboard=True)