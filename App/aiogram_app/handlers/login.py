
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram import F
from aiogram.fsm.context import FSMContext # Новый импорт
from aiogram.fsm.state import State, StatesGroup # Новый импорт
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import check_password_hash

from joblib import load
from sklearn.linear_model import LogisticRegressionCV , LogisticRegression

from database.orm_query import orm_add_iris, orm_get_user, orm_get_irises, orm_get_iris
import keyboards.userkb as kb
import keyboards.inline as kbi

login = Router()


class Login(StatesGroup):
    user_name = State()
    password = State()
    authorized = State()
    predictioniris = State()
    real_iris = State()

    real_ir = None

@login.message(F.text=='Вход в аккаунт')
async def start_login(message: Message, state: FSMContext):
    await state.set_state(Login.user_name)
    await message.answer('Введите ваш никнейм')


@login.message(Login.user_name)
async def password_login(message: Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await state.set_state(Login.password)
    await message.answer('Введите ваш пароль')


@login.message(Login.password)
async def result_login(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(password=message.text)  
    data = await state.get_data()
    user = await orm_get_user(session, data['user_name'])
    if user:
        if check_password_hash(user.password, data['password']):
            await state.set_state(Login.authorized)
            await message.answer(f'Добро пожаловать: {user.first_name} {user.last_name}', reply_markup=kb.log_in_kb)
        else:
            await message.answer(f'Неверный пароль! Попробуйте снова.')
            return
    else:    
        await message.answer(f'Такого пользователя не существует!', reply_markup=kb.reg_log_kb)
        await state.clear()
        return
    

@login.message(Login.authorized, F.text=='Предсказать сорт ириса')
async def prediction_iris(message: Message, state: FSMContext):
    await state.set_state(Login.predictioniris)
    await message.answer('<i>Введите данные об ирисе</i> (в одну строку через пробел, дробные числа через точку):\n<b>1</b>. Длина чашелистика\n<b>2</b>. Ширина чашелистика\n<b>3</b>. Длина лепестка\n<b>4</b>. Ширина лепестка')


@login.message(Login.predictioniris, F.text)
async def prediction(message: Message, state: FSMContext, session: AsyncSession):
    try:
        data_iris = list(map(float, message.text.split(' ')))
        if len(data_iris) != 4:
            await message.answer('<b>Должно быть 4-ре характеристики ириса!</b> Попробуйте снова.')
            return
    except ValueError:
        await message.answer('<b>Дробные числа пишутся через точку (5.5 2.3 4.1 2.3)!</b> Попробуйте снова.')
        return

    model = load('iris_model.joblib')
    scaler = load('scaler.joblib')
    X = scaler.transform([[data_iris[0], data_iris[1], data_iris[2], data_iris[3]]])
    prediction_iris_model = model.predict(X)

    data_iris.append(prediction_iris_model[0])
    await state.update_data(predictioniris=data_iris)
    user_data = await state.get_data()
    await orm_add_iris(session, user_data)
    await state.set_state(Login.authorized)

    await message.answer_photo(FSInputFile(f'aiogram_app/images/{prediction_iris_model[0]}.jpg'),caption=f'Ваш ирис: <b>{prediction_iris_model[0]}</b>', reply_markup=kb.log_in_kb)


@login.message(Login.authorized, F.text=='Профиль')
async def profil(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer("<b>Вот все ваши ирисы:</b>")
    user_data = await state.get_data()
    irises = await orm_get_irises(session, user_data['user_name'])
    for iris in irises:
        if iris.real:
            if iris.real == iris.prediction:
                await message.answer(f'id: {iris.id}\nДлина чашелистика: {iris.sepal_length}\nШирина чашелистика: {iris.sepal_width}\
                                \nДлина лепестка: {iris.petal_length}\nШирина лепестка: {iris.petal_width}\nПредсказанный сорт: {iris.prediction}\n<b>Предсказание верно</b> ✔️')
            else:
                await message.answer(f'id: {iris.id}\nДлина чашелистика: {iris.sepal_length}\nШирина чашелистика: {iris.sepal_width}\
                                \nДлина лепестка: {iris.petal_length}\nШирина лепестка: {iris.petal_width}\nПредсказанный сорт: {iris.prediction}\n<b>Предсказание неверно</b> ❌')
        else:
            await message.answer(f'id: {iris.id}\nДлина чашелистика: {iris.sepal_length}\nШирина чашелистика: {iris.sepal_width}\
                             \nДлина лепестка: {iris.petal_length}\nШирина лепестка: {iris.petal_width}\nПредсказанный сорт: {iris.prediction}',
                             reply_markup=kbi.get_callback_btns(btns={
                                 'Предсказание верно': f'true_{iris.id}',
                                 'Предсказание неверно': f'false_{iris.id}',
                             }))
    
    await state.set_state(Login.authorized)
    await message.answer(f'Вы вышли из профиля', reply_markup=kb.log_in_kb)

    
@login.message(Login.authorized, F.text=='Выйти')
async def logout(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer("Вы успешно вышли из своего профиля!", reply_markup=kb.reg_log_kb)
    await state.clear()


@login.callback_query(F.data.startswith('true_'))
async def true_pred(callback: types.CallbackQuery, session: AsyncSession):
    data = callback.data.split('_')
    iris_id = data[1]
    iris = await orm_get_iris(session, iris_id)
    iris.real = iris.prediction
    await session.commit()

    await callback.answer()


@login.callback_query(F.data.startswith('false_'))
async def true_pred(callback: types.CallbackQuery, state: FSMContext,session: AsyncSession):
    data = callback.data.split('_')
    iris_id = data[1]
    iris = await orm_get_iris(session, iris_id)
    await state.update_data(real_ir=iris_id)
    await callback.answer()
    await callback.message.answer('Введите название правильного сорта')
    await state.set_state(Login.real_iris)


@login.message(Login.real_iris, F.text)
async def true_iris_db(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    iris_id = data['real_ir']
    iris = await orm_get_iris(session, iris_id)
    iris.real = message.text
    await session.commit()
    await message.answer('Данные успешно обработаны!', reply_markup=kb.log_in_kb)
    await state.set_state(Login.authorized)
    