from aiogram import types
from data.config import ADMINS
from aiogram.types import Message
from sqlite3 import IntegrityError
from loader import dp, users_db, bot
from aiogram.filters.command import CommandStart, Command


@dp.message(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(text=f"Assalomu alaykum men sizga instagramdan postlarni yuklab beraman!\n\nInstagram post linkini yuboring...")
    try:
        users_db.add_user(user_id=message.from_user.id,
                          user_name=message.from_user.username,
                          user_first_name=message.from_user.first_name,
                          user_last_name=message.from_user.last_name)
        await bot.send_message(chat_id=ADMINS[0], text="Botga yangi obunachi qo'shildi!")
    except IntegrityError:
        pass


@dp.message(Command("bot"))
async def bot_start(message: Message):
    await message.answer(text="Assalomu alaykum\n\nAgar sizga Telegram bot yaratish hizmati kerak bo'lsa menga yozing! "
                              "Yoki qo'ng'iroq qiling!\n\nTelegram: @khojimatov14\n+998 90-626-66-44")


