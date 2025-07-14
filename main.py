from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.utils import executor
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from aiogram import F

import asyncio
import os

API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Анкета пользователей").sheet1

# States
class Survey(StatesGroup):
    location = State()
    satisfaction = State()
    property_type = State()
    region = State()
    budget = State()
    search_stage = State()
    mortgage = State()
    timing = State()
    name = State()
    phone = State()
    contact_method = State()
    contact_time = State()
    sos = State()

# Keyboard options
def make_keyboard(options):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for option in options:
        kb.add(KeyboardButton(option))
    return kb

@dp.message(F.text == '/start')
async def start(message: types.Message, state: FSMContext):
    await message.answer("Где вы сейчас живёте?", reply_markup=make_keyboard([
        "Своя квартира", "Снимаю квартиру", "С родителями", "С парнем/девушкой", "Общежитие", "Другое"]))
    await state.set_state(Survey.location)

@dp.message(Survey.location)
async def q1(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer("Вы довольны текущими условиями проживания?", reply_markup=make_keyboard([
        "Да, всё устраивает", "Нет, хочу улучшить", "Затрудняюсь ответить"]))
    await state.set_state(Survey.satisfaction)

@dp.message(Survey.satisfaction)
async def q2(message: types.Message, state: FSMContext):
    await state.update_data(satisfaction=message.text)
    await message.answer("Какой тип недвижимости вы хотели бы приобрести?", reply_markup=make_keyboard([
        "Квартира в новостройке", "Вторичка", "Дом", "Таунхаус", "Участок", "Пока не решил(а)"]))
    await state.set_state(Survey.property_type)

@dp.message(Survey.property_type)
async def q3(message: types.Message, state: FSMContext):
    await state.update_data(property_type=message.text)
    await message.answer("Где бы вы хотели приобрести недвижимость?", reply_markup=make_keyboard([
        "В текущем городе", "В другом городе", "За городом", "Пока не знаю"]))
    await state.set_state(Survey.region)

@dp.message(Survey.region)
async def q4(message: types.Message, state: FSMContext):
    await state.update_data(region=message.text)
    await message.answer("Какой у вас примерный бюджет?", reply_markup=make_keyboard([
        "До 2 млн ₽", "2–5 млн ₽", "5–10 млн ₽", "10+ млн ₽", "Затрудняюсь ответить"]))
    await state.set_state(Survey.budget)

@dp.message(Survey.budget)
async def q5(message: types.Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await message.answer("Вы уже подбирали варианты?", reply_markup=make_keyboard([
        "Да, активно ищу", "Смотрю, но пока без спешки", "Нет, только начал(а)", "Нет, но хочу узнать"]))
    await state.set_state(Survey.search_stage)

@dp.message(Survey.search_stage)
async def q6(message: types.Message, state: FSMContext):
    await state.update_data(search_stage=message.text)
    await message.answer("Рассматриваете ли вы ипотеку?", reply_markup=make_keyboard(["Да", "Нет", "Возможно"]))
    await state.set_state(Survey.mortgage)

@dp.message(Survey.mortgage)
async def q7(message: types.Message, state: FSMContext):
    await state.update_data(mortgage=message.text)
    await message.answer("Когда вы планируете покупку?", reply_markup=make_keyboard([
        "В ближайший месяц", "Через 3–6 месяцев", "В течение года", "Пока не знаю"]))
    await state.set_state(Survey.timing)

@dp.message(Survey.timing)
async def q8(message: types.Message, state: FSMContext):
    await state.update_data(timing=message.text)
    await message.answer("Ваше имя и фамилия:")
    await state.set_state(Survey.name)

@dp.message(Survey.name)
async def q9(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Ваш номер телефона:")
    await state.set_state(Survey.phone)

@dp.message(Survey.phone)
async def q10(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Как лучше с вами связаться?", reply_markup=make_keyboard([
        "Позвонить", "Написать в Telegram", "Написать в WhatsApp", "E-mail", "Другое"]))
    await state.set_state(Survey.contact_method)

@dp.message(Survey.contact_method)
async def q11(message: types.Message, state: FSMContext):
    await state.update_data(contact_method=message.text)
    await message.answer("Когда с вами удобно связаться? (день и время)")
    await state.set_state(Survey.contact_time)

@dp.message(Survey.contact_time)
async def finish(message: types.Message, state: FSMContext):
    await state.update_data(contact_time=message.text)
    data = await state.get_data()
    sheet.append_row([data.get(k, '') for k in [
        'name', 'phone', 'location', 'satisfaction', 'property_type', 'region', 'budget',
        'search_stage', 'mortgage', 'timing', 'contact_method', 'contact_time']])

    await message.answer("Спасибо! Если хотите, чтобы с вами связались СЕЙЧАС — нажмите /sos")
    await state.clear()

@dp.message(F.text == '/sos')
async def sos(message: types.Message):
    await message.answer("Наш специалист свяжется с вами в ближайшее время! Благодарим за участие!")
    # Здесь можно добавить уведомление админу

if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
