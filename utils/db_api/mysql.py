# from typing import Union
# import aiomysql
# from aiomysql import Pool
#
# from data import config
#
#
# class Database:
#     def __init__(self):
#         self.pool: Union[Pool, None] = None
#
#     async def create(self):
#         try:
#             # MySQL ulanish poolini yaratish
#             self.pool = await aiomysql.create_pool(
#                 host=config.DB_HOST,
#                 port=config.DB_PORT,
#                 user=config.DB_USER,
#                 password=config.DB_PASS,
#                 db=config.DB_NAME,
#                 loop=None,  # Asinxron loopni avtomatik tarzda olish uchun
#             )
#             print("Database pool successfully created.")
#         except Exception as e:
#             print(f"Error creating database pool: {e}")
#
#     async def create_table_users(self):
#         sql = """
#         CREATE TABLE IF NOT EXISTS users_user (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             full_name VARCHAR(255),
#             username VARCHAR(255) UNIQUE,
#             phone_number VARCHAR(20),
#             telegram_id BIGINT,
#             password VARCHAR(255),
#             is_superuser BOOLEAN DEFAULT FALSE,
#             first_name VARCHAR(255),
#             last_name VARCHAR(255),
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
#         if self.pool is None:
#             raise Exception("Database pool is not created. Call create() method first.")
#
#         # Pool'dan ulanish olish va buyruqni bajarish
#         async with self.pool.acquire() as connection:
#             async with connection.cursor() as cursor:
#                 if fetch:
#                     await cursor.execute(command, *args)
#                     result = await cursor.fetchall()
#                 elif fetchval:
#                     await cursor.execute(command, *args)
#                     result = await cursor.fetchone()
#                 elif fetchrow:
#                     await cursor.execute(command, *args)
#                     result = await cursor.fetchone()
#                 elif execute:
#                     await cursor.execute(command, *args)
#                     result = None
#                 return result
#
#     @staticmethod
#     def format_args(sql, parameters: dict):
#         sql += " AND ".join(
#             [f"{item} = %s" for item in parameters.keys()]
#         )
#         return sql, tuple(parameters.values())
#
#     async def select_user_by_username(self, username):
#         sql = "SELECT * FROM users_user WHERE username = %s"
#         return await self.execute(sql, username, fetchrow=True)
#
#     async def add_user(self, full_name=None, username=None, phone_number=None, telegram_id=None,
#                        password=None, is_superuser=False, first_name=None, last_name=None,
#                        is_staff=False, is_active=True, is_premium=False, date_joined=None):
#         # Bazada bu usernameni tekshirish
#         user_exists = await self.select_user_by_username(username)
#         if user_exists:
#             # Bazada foydalanuvchi allaqachon mavjud
#             sql = """
#             UPDATE users_user SET full_name=%s, phone_number=%s, telegram_id=%s, password=%s,
#             is_superuser=%s, first_name=%s, last_name=%s, is_staff=%s, is_active=%s, is_premium=%s, date_joined=%s
#             WHERE username=%s
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
#             VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) returning *
#             """
#             result = await self.execute(sql, full_name, username, phone_number, telegram_id, password,
#                                         is_superuser, first_name, last_name, is_staff, is_active, is_premium,
#                                         date_joined, fetchrow=True)
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
#         sql += f" WHERE id=%s"
#         parameters += (user_id,)
#         return await self.execute(sql, *parameters, execute=True)
#
#     async def delete_user(self, user_id):
#         sql = "DELETE FROM users_user WHERE id=%s"
#         return await self.execute(sql, user_id, execute=True)
#
#     async def drop_users(self):
#         await self.execute("DROP TABLE users_user", execute=True)
