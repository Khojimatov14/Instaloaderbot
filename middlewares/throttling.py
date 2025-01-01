# import time
# from aiogram import BaseMiddleware, types
# from aiogram.dispatcher.event.handler import HandlerObject
#
#
# class ThrottlingMiddleware(BaseMiddleware):
#     def __init__(self, default_rate: int = 0.5) -> None:
#         self.limiters = {}
#         self.default_rate = default_rate
#         self.count_throttled = 1
#         self.last_throttled = 0
#
#     async def __call__(self, handler, event: types.Update, data):
#         real_handler: HandlerObject = data["handler"]
#         skip_pass = True
#         if real_handler.flags.get("skip_pass") is not None:
#             skip_pass = real_handler.flags.get("skip_pass")
#         if skip_pass:
#             if int(time.time()) - self.last_throttled >= self.default_rate:
#                 self.last_throttled = int(time.time())
#                 self.default_rate = 0.5
#                 self.count_throttled = 0
#                 return await handler(event, data)
#             else:
#                 if self.count_throttled >= 2:
#                     self.default_rate = 3
#                 else:
#                     self.count_throttled += 1
#                     await event.message.reply("<b>So'rov ko'payib ketdi!</b>")
#
#             self.last_throttled = int(time.time())
#         else:
#             return await handler(event, data)


import time
from aiogram import BaseMiddleware, types
class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, default_rate: float = 0.5) -> None:
        self.default_rate = default_rate
        self.users_data = {}  # Har bir foydalanuvchi uchun throttling ma'lumotlari

    async def __call__(self, handler, event: types.Update, data: dict):
        # Foydalanuvchi identifikatorini olish
        user_id = None
        if hasattr(event, "message") and event.message:
            user_id = event.message.from_user.id
        elif hasattr(event, "callback_query") and event.callback_query:
            user_id = event.callback_query.from_user.id

        if user_id is None:
            # Agar foydalanuvchi ID aniqlanmasa, throttlingni o'tkazib yuborish
            return await handler(event, data)

        # Foydalanuvchi uchun throttling ma'lumotlarini olish yoki yaratish
        user_data = self.users_data.get(user_id, {"last_throttled": 0.0, "count_throttled": 0})
        current_time = time.time()

        # Foydalanuvchining throttling holatini tekshirish
        if current_time - user_data["last_throttled"] >= self.default_rate:
            user_data["last_throttled"] = current_time
            user_data["count_throttled"] = 0
            self.users_data[user_id] = user_data  # Ma'lumotlarni yangilash
            return await handler(event, data)
        else:
            if user_data["count_throttled"] >= 2:
                self.default_rate = 3.0
            else:
                user_data["count_throttled"] += 1
                self.users_data[user_id] = user_data  # Ma'lumotlarni yangilash
                if hasattr(event, "message") and event.message:
                    await event.message.reply("<b>So'rov ko'payib ketdi!</b>")

        user_data["last_throttled"] = current_time
        self.users_data[user_id] = user_data  # Ma'lumotlarni yangilash
