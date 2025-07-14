
import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
from google_sheets import append_row

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Состояния
class Form(StatesGroup):
    housing = State()
    improve = State()
    type = State()
    city = State()
    budget = State()
    search = State()
    mortgage = State()
    time = State()
    name = State()
    phone = State()
    contact = State()
    callback_time = State()
    sos = State()

# Кнопки
yes_no_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Да")], [KeyboardButton(text="Нет")]],
    resize_keyboard=True
)

contact_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Позвонить")],
        [KeyboardButton(text="Написать в мессенджер")],
        [KeyboardButton(text="Email")],
        [KeyboardButton(text="Подарок")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Привет! Давай подберём тебе идеальную недвижимость. Отвечай честно, и получишь подарок 🎁")
    await message.answer("1. Где ты живёшь сейчас? (своя, съёмная, с родителями, с девушкой/парнем и т.д.)")
    await state.set_state(Form.housing)

@dp.message(Form.housing)
async def step_housing(message: Message, state: FSMContext):
    await state.update_data(housing=message.text)
    await message.answer("2. Хотели бы улучшить условия?")
    await state.set_state(Form.improve)

@dp.message(Form.improve)
async def step_improve(message: Message, state: FSMContext):
    await state.update_data(improve=message.text)
    await message.answer("3. Какой тип недвижимости интересует? (Квартира, Дом, Участок...)")
    await state.set_state(Form.type)

@dp.message(Form.type)
async def step_type(message: Message, state: FSMContext):
    await state.update_data(type=message.text)
    await message.answer("4. В каком городе/регионе?")
    await state.set_state(Form.city)

@dp.message(Form.city)
async def step_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("5. Какой бюджет? (Есть немного денег, Материнский капитал за одного и больше двух, Есть деньги с продажи, Распиши более подробно для точного подбора специалистом)")
    await state.set_state(Form.budget)

@dp.message(Form.budget)
async def step_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await message.answer("6. Уже ищете жильё? (Да, Иногда, Пока думаю)")
    await state.set_state(Form.search)

@dp.message(Form.search)
async def step_search(message: Message, state: FSMContext):
    await state.update_data(search=message.text)
    await message.answer("7. Рассматриваете ипотеку?")
    await state.set_state(Form.mortgage)

@dp.message(Form.mortgage)
async def step_mortgage(message: Message, state: FSMContext):
    await state.update_data(mortgage=message.text)
    await message.answer("8. Когда планируете покупку?")
    await state.set_state(Form.time)

@dp.message(Form.time)
async def step_time(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await message.answer("9. Ваше ФИО:")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def step_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("10. Ваш телефон:")
    await state.set_state(Form.phone)

@dp.message(Form.phone)
async def step_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("11. Как с вами лучше связаться?", reply_markup=contact_kb)
    await state.set_state(Form.contact)

@dp.message(Form.contact)
async def step_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await message.answer("12. Когда с вами удобно связаться?")
    await state.set_state(Form.callback_time)

@dp.message(Form.callback_time)
async def step_callback_time(message: Message, state: FSMContext):
    await state.update_data(callback_time=message.text)
    await message.answer("Если вам нужно связаться СЕЙЧАС — напишите SOS, и мы свяжемся немедленно!", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="SOS")], [KeyboardButton(text="Нет, всё ок")]],
        resize_keyboard=True
    ))
    await state.set_state(Form.sos)

@dp.message(Form.sos)
async def step_sos(message: Message, state: FSMContext):
    data = await state.get_data()
    data["sos"] = message.text

    # Сохраняем в Google Sheets
    row = [
        message.date.isoformat(), data.get("name"), data.get("phone"),
        data.get("housing"), data.get("improve"), data.get("type"),
        data.get("city"), data.get("budget"), data.get("search"),
        data.get("mortgage"), data.get("time"), data.get("contact"),
        data.get("callback_time"), data.get("sos")
    ]
    append_row(row)

    await message.answer("Спасибо! Мы свяжемся с вами в указанное время.")
    if data["sos"].lower() == "sos":
        await message.answer("🔔 Специалист свяжется с вами в ближайшее время!")
        await bot.send_message(ADMIN_ID, f"🚨 SOS от {data.get('name')} {data.get('phone')}")

    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
