from aiogram import F
from aiogram.enums import ContentType
from data.config import ADMINS
from aiogram.types import Message
from loader import dp, media_db, bot
from aiogram.exceptions import TelegramBadRequest
from utils import InstagramDownloaderSingleton, send_media_group, send_video, send_media_on_db


@dp.message(F.text.startswith(("https://www.instagram.com", "https://instagram.com")))
async def send_media(message: Message):
    shortcode = message.text.split("/")[-2]
    downloader = InstagramDownloaderSingleton.get_instance()

    media_file = media_db.select_media_by_url(media_url=shortcode)

    if media_file:
        await send_media_on_db(media_file=media_file, message=message, shortcode=shortcode)
    else:
        rem = await message.answer(text="⏳")
        post = await downloader.get_post_data(shortcode=shortcode)
        if not post:
            await message.reply(text="Afsuski ushbu media faylni yuklay olmadim.\n\nUshbu post yopiq akkauntga tegishli bo'lishi mumkin!")
            await rem.delete()
            return

        if post.typename == "GraphVideo":
            await send_video(post=post, downloader=downloader, message=message, shortcode=shortcode)

        elif post.typename == "GraphImage":
            msg_photo = await message.answer_photo(photo=post.url, caption="📥 @InstaLoaderUz_bot orqali yuklab olindi.")
            media_db.add_media(media_url=shortcode, media_id=msg_photo.photo[-1].file_id, media_type="photo")
        elif post.typename == "GraphSidecar":
            try:
                await send_media_group(post=post, downloader=downloader, message=message, shortcode=shortcode)
            except TelegramBadRequest as err:
                await message.reply(text="Afsuski ushbu media faylni yuklay olmadim.\n\nBirozdan so'ng qayta urinib ko'ring foydalanuvchilar juda ko'p!")
                await bot.send_message(chat_id=ADMINS[0],
                                       text=f"Media groupni yuborishda xatolik yuz berdi!\n\n{err}\n\n<code>{message.text}</code>")
        await rem.delete()


@dp.message()
async def get_insta_link(message: Message):
    if message.content_type != ContentType.SUCCESSFUL_PAYMENT:
        await message.answer(text='Iltimos instagram post linkini yuboring...')
    else:
        await message.delete()