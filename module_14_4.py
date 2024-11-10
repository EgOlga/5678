from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from crud_functions import *

initiate_db()

api = "7565705801:AAFvLmFKnEMuH3Kkxc-bJ9VXiLZ_hiTsQ14"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


button_1 = KeyboardButton(text='Информация')
button_2 = KeyboardButton(text='Рассчитать')
button_3 = KeyboardButton(text='Купить')
kb = ReplyKeyboardMarkup(resize_keyboard=True).row(button_1, button_2, button_3)

in_button_1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
in_button_2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
ikb = InlineKeyboardMarkup(resize_keyboard=True).row(in_button_1, in_button_2)
product_1 = InlineKeyboardButton(text='Product 1', callback_data='product_buying')
product_2 = InlineKeyboardButton(text='Product 2', callback_data='product_buying')
product_3 = InlineKeyboardButton(text='Product 3', callback_data='product_buying')
product_4 = InlineKeyboardButton(text='Product 4', callback_data='product_buying')
ikb_product = InlineKeyboardMarkup(resize_keyboard = True).row(product_1, product_2, product_3, product_4)

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью.', reply_markup=kb)

@dp.message_handler(text='Информация')
async def info(message):
    await message.answer('Привет! Я бот, рассчитывающий норму ккал по упрощенной формуле Миффлина-Сан Жеора.')

@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=ikb)

@dp.message_handler(text='Купить')
async def get_buying_list(message):
    all_product = get_all_products()

    for product in all_product:
        product_id, title, description, price = product
        await message.answer(f'Название: {title} | Описание: {description} | Цена: {price}')
        with open (f'{product_id}.PNG', 'rb') as png:
            await message.answer_photo(png)
    await message.answer('Выберите продукт для покупки', reply_markup=ikb_product)

@dp.callback_query_handler(text='product_buying')
async def set_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5;'
                              '\nдля женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()

@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()
@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост (см):')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес (кг):')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    ccal_man = 10 * float(data['weight']) + 6.25 * float(data['growth']) - 5 * float(data['age']) + 5
    ccal_woman = 10 * float(data['weight']) + 6.25 * float(data['growth']) - 5 * float(data['age'])- 161

    await message.answer(f'Норма для мужчин: {ccal_man} ккал')
    await message.answer(f'Норма для женщин: {ccal_woman} ккал')
    await UserState.weight.set()
    await state.finish()

@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
