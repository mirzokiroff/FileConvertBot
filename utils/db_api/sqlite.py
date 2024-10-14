# from typing import Union
# import aiosqlite
#
# from data import config
#
#
# class Database:
#     def __init__(self):
#         self.db: Union[aiosqlite.Connection, None] = None
#
#     async def create(self):
#         try:
#             # SQLite uchun bog'lanishni yaratamiz
#             self.db = await aiosqlite.connect(config.DB_NAME)
#             print("Database successfully connected.")
#         except Exception as e:
#             print(f"Error connecting to database: {e}")
#
#     async def create_table_users(self):
#         sql = """
#         CREATE TABLE IF NOT EXISTS users_user (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             full_name TEXT,
#             username TEXT UNIQUE,
#             phone_number TEXT,
#             telegram_id INTEGER,
#             password TEXT,
#             is_superuser BOOLEAN DEFAULT FALSE,
#             first_name TEXT,
#             last_name TEXT,
#             is_staff BOOLEAN DEFAULT FALSE,
#             is_active BOOLEAN DEFAULT TRUE,
#             is_premium BOOLEAN DEFAULT FALSE,
#             date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         );
#         """
#         await self.execute(sql, execute=True)
#
#     async def execute(
#             self,
#             command,
#             *args,
#             fetch: bool = False,
#             fetchval: bool = False,
#             fetchrow: bool = False,
#             execute: bool = False,
#     ):
#         if self.db is None:
#             raise Exception("Database is not created. Call create() method first.")
#
#         # Albatta bog'lanishni ochamiz va tranzaksiya ichida ishlaymiz
#         async with self.db.execute(command, *args) as cursor:
#             if fetch:
#                 result = await cursor.fetchall()
#             elif fetchval:
#                 result = await cursor.fetchone()
#             elif fetchrow:
#                 result = await cursor.fetchone()
#             elif execute:
#                 result = cursor.lastrowid  # Agar insert yoki update qilish kerak bo'lsa
#             return result
#
#     @staticmethod
#     def format_args(sql, parameters: dict):
#         sql += " AND ".join(
#             [f"{item} = ?" for item in parameters.keys()]
#         )
#         return sql, tuple(parameters.values())
#
#     async def select_user_by_username(self, username):
#         sql = "SELECT * FROM users_user WHERE username = ?"
#         return await self.execute(sql, username, fetchrow=True)
#
#     async def add_user(self, full_name=None, username=None, phone_number=None, telegram_id=None,
#                        password=None, is_superuser=False, first_name=None, last_name=None,
#                        is_staff=False, is_active=True, is_premium=False, date_joined=None):
#         # Bazada bu usernameni tekshirish
#         user_exists = await self.select_user_by_username(username)
#         if user_exists:
#             # Bazada foydalanuvchi allaqachon mavjud
#             # Agar foydalanuvchi allaqachon mavjud bo'lsa, uni yangilash kerak
#             sql = """
#             UPDATE users_user SET full_name=?, phone_number=?, telegram_id=?, password=?,
#             is_superuser=?, first_name=?, last_name=?, is_staff=?, is_active=?, is_premium=?, date_joined=?
#             WHERE username=?
#             """
#             result = await self.execute(sql, full_name, phone_number, telegram_id, password,
#                                         is_superuser, first_name, last_name, is_staff, is_active, is_premium,
#                                         date_joined, username, execute=True)
#         else:
#             # Bazada foydalanuvchi mavjud emas
#             # Yangi foydalanuvchi qo'shish
#             sql = """
#             INSERT INTO users_user (full_name, username, phone_number, telegram_id, password, is_superuser,
#                                     first_name, last_name, is_staff, is_active, is_premium, date_joined)
#             VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#             """
#             result = await self.execute(sql, full_name, username, phone_number, telegram_id, password,
#                                         is_superuser, first_name, last_name, is_staff, is_active, is_premium,
#                                         date_joined, execute=True)
#         return result
#
#     async def select_all_users(self):
#         sql = "SELECT * FROM users_user"
#         return await self.execute(sql, fetch=True)
#
#     async def select_user(self, **kwargs):
#         sql = "SELECT * FROM users_user WHERE "
#         sql, parameters = self.format_args(sql, parameters=kwargs)
#         return await self.execute(sql, *parameters, fetchrow=True)
#
#     async def count_users(self):
#         sql = "SELECT COUNT(*) FROM users_user"
#         return await self.execute(sql, fetchval=True)
#
#     async def update_user(self, user_id, **kwargs):
#         sql = "UPDATE users_user SET "
#         sql, parameters = self.format_args(sql, parameters=kwargs)
#         sql += f" WHERE id=?"
#         parameters += (user_id,)
#         return await self.execute(sql, *parameters, execute=True)
#
#     async def delete_user(self, user_id):
#         sql = "DELETE FROM users_user WHERE id=?"
#         return await self.execute(sql, user_id, execute=True)
#
#     async def drop_users(self):
#         await self.execute("DROP TABLE IF EXISTS users_user", execute=True)
