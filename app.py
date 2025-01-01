import middlewares, filters, handlers
import asyncio
import logging
import sys
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from loader import dp, bot, media_db, media_group_db, users_db
from middlewares import ThrottlingMiddleware
from utils import send_zip_data


async def main():
    await on_startup_notify()
    await set_default_commands()
    dp.update.middleware.register(ThrottlingMiddleware())

    try:
        media_db.create_table_media()
    except Exception as err:
        print(err)
    try:
        media_group_db.create_table_media_group()
    except Exception as err:
        print(err)
    try:
        users_db.create_table_users()
    except Exception as err:
        print(err)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

