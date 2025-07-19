import re
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram import F
from aiogram.fsm.context import FSMContext # Новый импорт
from aiogram.fsm.state import State, StatesGroup # Новый импорт
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import check_password_hash

from database.orm_query import orm_add_user, orm_get_user
import keyboards.userkb as kb

register = Router()


@register.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}!", reply_markup=kb.reg_log_kb)


class Register(StatesGroup):
    first_name = State()
    last_name = State()
    user_name = State()
    email = State()
    password = State()


@register.message(F.text=='Регистрация')
async def start_registration(message: Message, state: FSMContext):
    await state.set_state(Register.first_name)
    await message.answer('Введите ваше имя')


@register.message(Register.first_name)
async def last_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(Register.last_name)
    await message.answer('Введите вашу фамилию')


@register.message(Register.last_name)
async def user_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(Register.user_name)
    await message.answer('Придумайте имя пользователя')


@register.message(Register.user_name)
async def email(message: Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await state.set_state(Register.email)
    await message.answer('Введите вашу почту')


@register.message(Register.email)
async def password(message: Message, state: FSMContext):
    email_regex = re.compile(r'^[a-zA-Z0-9_.+-]+@(?:mail\.ru|gmail\.com|bk\.ru|yandex\.ru)$')
    if not(email_regex.match(message.text)):
        await message.answer('Введена некорректная почта! Введите почту еще раз')
        return
    await state.update_data(email=message.text)
    await state.set_state(Register.password)
    await message.answer('Придумайте пароль')


@register.message(Register.password)
async def result(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(password=message.text)
    data = await state.get_data()
    await message.answer(f'Ваше имя: {data['first_name']}\nВаша фамилия: {data['last_name']}\nВаш никнейм: {data['user_name']}\nВаша почта: {data['email']}',
                         reply_markup=kb.reg_log_kb)
    
    await orm_add_user(session, data)

    await state.clear()


