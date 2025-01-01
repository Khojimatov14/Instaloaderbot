import os
import shutil
from aiogram import F
from data.config import ADMINS
from sqlite3 import IntegrityError
from aiogram.types import Message, FSInputFile
from aiogram.exceptions import TelegramBadRequest
from loader import dp, media_db, media_group_db, bot
from aiogram.utils.media_group import MediaGroupBuilder
from utils import get_video_resolution, InstagramDownloaderSingleton, send_media_group


@dp.message(F.text.startswith("https://www.instagram.com"))
async def send_media(message: Message):
    user_id = message.from_user.id
    shortcode = message.text.split("/")[-2]
    downloader = InstagramDownloaderSingleton.get_instance()

    media_file = media_db.select_media_by_url(media_url=shortcode)

    if media_file:
        if media_file[2] == "photo":
            await message.answer_photo(photo=media_file[1], caption="📥 @InstaLoaderUz_bot orqali yuklab olindi.")
        elif media_file[2] == "video":
            await message.answer_video(video=media_file[1], caption="📥 @InstaLoaderUz_bot orqali yuklab olindi.")
        elif media_file[2] == "big":
            await message.answer(text=f"Bu video hajmi juda katta!\nQuyidagi link orqali "
                                      f"browseringiz yordamida yuklab olishingiz mumkin!\n\n "
                                      f"<a href='{media_file[1]}'>🔗 Yuklab olish</a>")
        elif media_file[2] == "group":
            media_group = MediaGroupBuilder(caption="📥 @InstaLoaderUz_bot orqali yuklab olindi.")
            group = media_group_db.select_media_group(media_group_url=shortcode)
            for media in group:
                if media[2] == "photo":
                    media_group.add(type="photo", media=media[1])
                elif media[2] == "video":
                    media_group.add(type="video", media=media[1])
            await message.answer_media_group(media=media_group.build())
    else:
        folder_name = str(user_id)
        rem = await message.answer(text="⏳")
        post = await downloader.get_post_data(shortcode=shortcode)
        if not post:
            await message.reply(text="Afsuski ushbu media faylni yuklay olmadim.")
            await rem.delete()
            return

        if post.typename == "GraphVideo":
            try:
                msg_video = await message.answer_video(video=post.video_url, caption="📥 @InstaLoaderUz_bot orqali yuklab olindi.")
                try:
                    media_db.add_media(media_url=shortcode, media_id=msg_video.video.file_id, media_type="video")
                except IntegrityError:
                    pass
            except TelegramBadRequest:
                video_size = await downloader.get_video_size(video_url=post.video_url)
                if video_size <= 49:
                    result = await downloader.download_media(shortcode=shortcode, user_id=user_id)
                    if result and os.path.exists(folder_name):
                        for file_name in os.listdir(folder_name):
                            file_path = os.path.join(folder_name, file_name)
                            if file_name.endswith((".mp4", ".mov", ".avi")):
                                width, height = await get_video_resolution(file_path)
                                msg_video = await message.answer_video(video=FSInputFile(file_path),
                                                                       supports_streaming=True,
                                                                       width=width, height=height,
                                                                       caption="📥 @InstaLoaderUz_bot orqali yuklab olindi.")

                                media_db.add_media(media_url=shortcode, media_id=msg_video.video.file_id, media_type="video")
                                shutil.rmtree(folder_name)
                else:
                    await message.reply(text=f"Bu video hajmi juda katta!\nQuyidagi link orqali "
                                             f"browseringiz yordamida yuklab olishingiz mumkin!\n\n "
                                             f"<a href='{post.video_url}'>🔗 Yuklab olish</a>")
                    media_db.add_media(media_url=shortcode, media_id=post.video_url, media_type="big")
        elif post.typename == "GraphImage":
            msg_photo = await message.answer_photo(photo=post.url, caption="📥 @InstaLoaderUz_bot orqali yuklab olindi.")
            media_db.add_media(media_url=shortcode, media_id=msg_photo.photo[-1].file_id, media_type="photo")
        elif post.typename == "GraphSidecar":
            try:
                await send_media_group(post=post, downloader=downloader, message=message, shortcode=shortcode)
            except TelegramBadRequest as err:
                await message.reply(text="Afsuski ushbu media faylni yuklay olmadim.")
                await bot.send_message(chat_id=ADMINS[0],
                                       text=f"Media groupni yuborishda xatolik yuz berdi!\n\n{err}\n\n<code>{message.text}</code>")
        await rem.delete()


@dp.message()
async def get_insta_link(message: Message):
    await message.answer(text='Iltimos instagram post linkini yuboring...')