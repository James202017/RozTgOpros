
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter
import asyncio
import logging
from config import BOT_TOKEN, ADMIN_ID
from google_sheets import append_to_sheet
from datetime import datetime

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

class Survey(StatesGroup):
    housing = State()
    satisfied = State()
    property_type = State()
    city = State()
    budget = State()
    search_status = State()
    mortgage = State()
    purchase_time = State()
    name = State()
    phone = State()
    contact_method = State()
    preferred_time = State()
    sos = State()

user_data = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Добро пожаловать в конкурс!
Где вы сейчас живете?",
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Своя квартира")],
            [KeyboardButton(text="Съёмная квартира")],
            [KeyboardButton(text="С родителями")],
            [KeyboardButton(text="С парнем/девушкой")],
            [KeyboardButton(text="Общежитие")],
            [KeyboardButton(text="Другое")]
        ], resize_keyboard=True)
    )
    await state.set_state(Survey.housing)

@dp.message(StateFilter(Survey.housing))
async def step_housing(message: types.Message, state: FSMContext):
    await state.update_data(housing=message.text)
    await message.answer("Хотите ли вы улучшить жилищные условия?", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Да")], [KeyboardButton(text="Нет")]], resize_keyboard=True))
    await state.set_state(Survey.satisfied)

@dp.message(StateFilter(Survey.satisfied))
async def step_satisfied(message: types.Message, state: FSMContext):
    await state.update_data(satisfied=message.text)
    await message.answer("Какую недвижимость вы рассматриваете? (Дом, Квартира и т.д.)")
    await state.set_state(Survey.property_type)

@dp.message(StateFilter(Survey.property_type))
async def step_type(message: types.Message, state: FSMContext):
    await state.update_data(property_type=message.text)
    await message.answer("В каком городе или регионе хотите недвижимость?")
    await state.set_state(Survey.city)

@dp.message(StateFilter(Survey.city))
async def step_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Какой у вас бюджет?")
    await state.set_state(Survey.budget)

@dp.message(StateFilter(Survey.budget))
async def step_budget(message: types.Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await message.answer("Вы уже подбираете или только планируете?")
    await state.set_state(Survey.search_status)

@dp.message(StateFilter(Survey.search_status))
async def step_search_status(message: types.Message, state: FSMContext):
    await state.update_data(search_status=message.text)
    await message.answer("Рассматриваете ипотеку?")
    await state.set_state(Survey.mortgage)

@dp.message(StateFilter(Survey.mortgage))
async def step_mortgage(message: types.Message, state: FSMContext):
    await state.update_data(mortgage=message.text)
    await message.answer("Когда планируете покупку?")
    await state.set_state(Survey.purchase_time)

@dp.message(StateFilter(Survey.purchase_time))
async def step_purchase_time(message: types.Message, state: FSMContext):
    await state.update_data(purchase_time=message.text)
    await message.answer("Ваше ФИО:")
    await state.set_state(Survey.name)

@dp.message(StateFilter(Survey.name))
async def step_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Телефон для связи:")
    await state.set_state(Survey.phone)

@dp.message(StateFilter(Survey.phone))
async def step_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Как предпочитаете связаться? (Звонок, Telegram, WhatsApp и т.д.)")
    await state.set_state(Survey.contact_method)

@dp.message(StateFilter(Survey.contact_method))
async def step_contact_method(message: types.Message, state: FSMContext):
    await state.update_data(contact_method=message.text)
    await message.answer("Когда удобно связаться? (день и время)")
    await state.set_state(Survey.preferred_time)

@dp.message(StateFilter(Survey.preferred_time))
async def step_time(message: types.Message, state: FSMContext):
    await state.update_data(preferred_time=message.text)
    data = await state.get_data()
    append_to_sheet([
        data.get("name"), data.get("phone"), message.from_user.username,
        data.get("housing"), data.get("satisfied"), data.get("property_type"),
        data.get("city"), data.get("budget"), data.get("search_status"),
        data.get("mortgage"), data.get("purchase_time"), data.get("contact_method"),
        data.get("preferred_time"), "Нет", datetime.now().strftime("%Y-%m-%d %H:%M")
    ])
    await message.answer("Спасибо! Если хотите срочную помощь — нажмите /sos")

@dp.message(Command("sos"))
async def sos_command(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(sos="Да")
    await message.answer("С вами свяжется специалист как можно скорее.")
    await bot.send_message(ADMIN_ID, f"‼️ SOS от {message.from_user.full_name} (@{message.from_user.username})
Номер: {data.get('phone')}")
