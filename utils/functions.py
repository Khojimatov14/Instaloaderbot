import os
import asyncio
import requests
import pyminizip
from data.config import ADMINS
from moviepy import VideoFileClip
from sqlite3 import IntegrityError
from aiogram.types import FSInputFile
from instaloader import Instaloader, Post
from aiogram.utils.media_group import MediaGroupBuilder




class InstagramDownloader:
    PROXIES = [
        "85.214.195.118:80",
        "13.36.104.85:80",
        "54.224.215.61:8888",
        "8.221.139.222:9098",
        "47.91.120.190:3128",
        "38.9.141.250:10609",
        "203.144.144.146:8080",
        "18.185.169.150:3128",
        "103.194.175.138:8080",
        "45.201.216.126:8080",
        "27.79.234.2:16000",
        "44.219.175.186:80"
    ]

    def __init__(self, switch_after=5):
        self.proxy_list = self.PROXIES
        self.proxy_index = 0
        self.requests_counter = 0
        self.switch_after = switch_after
        self.loader = Instaloader(
            save_metadata=False,
            request_timeout=20,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"
        )

    async def switch_proxy(self):
        if not self.proxy_list:
            raise ValueError("Proksi ro'yxati bo'sh! PROXIES to'g'ri o'rnatilganligini tekshiring.")

        self.proxy_index = (self.proxy_index + 1) % len(self.proxy_list)
        current_proxy = self.proxy_list[self.proxy_index]

        self.loader.context.http_proxies = {
            'http': f"http://{current_proxy}",
            'https': f"http://{current_proxy}"
        }

    async def get_post_data(self, shortcode):
        from loader import bot
        if self.requests_counter >= self.switch_after:
            await self.switch_proxy()
            self.requests_counter = 0

        try:
            self.requests_counter += 1
            post = Post.from_shortcode(self.loader.context, shortcode)
            return post
        except Exception as e:
            await bot.send_message(chat_id=ADMINS[0], text=f"Xatolik yuz berdi: {e}")
            return None

    async def download_media(self, shortcode, user_id):
        from loader import bot
        if self.requests_counter >= self.switch_after:
            await self.switch_proxy()
            self.requests_counter = 0

        try:
            self.requests_counter += 1
            post = Post.from_shortcode(self.loader.context, shortcode)
            self.loader.download_post(post, target=f"{user_id}")
            await asyncio.sleep(2)
            return True
        except Exception as e:
            await bot.send_message(chat_id=ADMINS[0], text=f"Media yuklanayotganda xatolik yuz berdi: {e}")
            return False

    async def get_video_size(self, video_url: str):
        from loader import bot
        if self.requests_counter >= self.switch_after:
            await self.switch_proxy()
            self.requests_counter = 0

        try:
            self.requests_counter += 1
            response = requests.head(video_url)
            total_size = int(response.headers.get('Content-Length', 0))
            file_size_in_mb = total_size / (1024 * 1024)
            return file_size_in_mb
        except Exception as e:
            await bot.send_message(chat_id=ADMINS[0], text=f"Videoning hajmini olishda xatolik: {e}")
            return 0


class InstagramDownloaderSingleton:
    _instance = None  # Bitta obyektni saqlash uchun o'zgaruvchi

    @classmethod
    def get_instance(cls):
        if cls._instance is None:  # Agar obyekt hali yaratilmagan bo'lsa
            cls._instance = InstagramDownloader(switch_after=2)
        return cls._instance  # Mavjud obyektni qaytaradi



async def get_video_resolution(file_path):
    clip = VideoFileClip(file_path)
    width, height = clip.size
    clip.close()
    return width, height


async def send_zip_data():
    while True:
        from loader import bot
        input_file = "data/allData.db"
        output_file = "instaloader_data_base.zip"
        password = "14081997"
        compression_level = 5
        pyminizip.compress(input_file, None, output_file, password, compression_level)

        await asyncio.sleep(3)
        await bot.send_document(chat_id="@akjjkjkskjddhdhksajdhaksjdhaksdj", document=FSInputFile(output_file))
        try:
            os.remove(path=output_file)
        except FileNotFoundError:
            await bot.send_message(chat_id=ADMINS[0],text="Faylni o'chirishda hatolik yuz berdi!")
        await asyncio.sleep(43200)


async def send_media_group(post, downloader, message, shortcode,):
    from loader import media_db, media_group_db, bot
    media_group = MediaGroupBuilder(caption="📥 @InstaLoaderUz_bot orqali yuklab olindi.")
    for node in post.get_sidecar_nodes():
        if node.is_video:
            video_size = await downloader.get_video_size(video_url=node.video_url)
            if video_size <= 49 and video_size != 0:
                media_group.add(type="video", media=node.video_url)
        else:
            media_group.add(type="photo", media=node.display_url)

    msg_group = await message.answer_media_group(media=media_group.build())
    try:
        media_db.add_media(media_url=shortcode, media_id="none", media_type="group")
        for msg in msg_group:
            if msg.photo:
                media_group_db.add_media_group(media_group_url=shortcode, media_id=msg.photo[-1].file_id,
                                               media_type="photo")
            elif msg.video:
                media_group_db.add_media_group(media_group_url=shortcode, media_id=msg.video.file_id,
                                               media_type="video")
    except IntegrityError as err:
        await bot.send_message(chat_id=ADMINS[0], text=f"Media groupni saqlashda xatolik yuz berdi!\n\n{err}\n\n<code>{message.text}</code>")
    # except TelegramBadRequest as err:
    #     await message.reply(text="Afsuski ushbu media faylni yuklay olmadim.")
    #     await bot.send_message(chat_id=ADMINS[0],
    #                            text=f"Media groupni yuborishda xatolik yuz berdi!\n\n{err}\n\n<code>{message.text}</code>")

