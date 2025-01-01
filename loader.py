from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from data import config
from utils import DatabaseMedia, DatabaseMediaGroup, DatabaseUsers

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())
media_db = DatabaseMedia(path_to_db="data/allData.db")
media_group_db = DatabaseMediaGroup(path_to_db="data/allData.db")
users_db = DatabaseUsers(path_to_db="data/allData.db")