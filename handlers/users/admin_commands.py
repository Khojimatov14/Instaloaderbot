import asyncio
from loader import dp
from aiogram import F
from data.config import ADMINS
from utils import send_zip_data
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command


@dp.message(Command("startdb"), F.from_user.id.in_(ADMINS))
async def bot_start(message: Message, state: FSMContext):
    data = await state.get_data()

    if data.get("auto_db") is None:
        await state.update_data(auto_db=True)
        await message.answer(text="Malumotlar bazasini avtomatik yuborish boshlandi!")
        while True:
            await send_zip_data()
            await asyncio.sleep(43200)
    else:
        await message.answer(text="Malumotlar bazasini avtomatik yuborish avval boshlangan!")


@dp.message(Command("senddb"), F.from_user.id.in_(ADMINS))
async def bot_start(message: Message):
    await message.answer(text="Malumotlar bazasi yuborildi")
    await send_zip_data()