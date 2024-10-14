from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        try:
            self.pool = await asyncpg.create_pool(
                user=config.DB_USER,
                password=config.DB_PASS,
                host=config.DB_HOST,
                database=config.DB_NAME,
                port=config.DB_PORT
            )
            print("Database pool successfully created.")
        except Exception as e:
            print(f"Error creating database pool: {e}")

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS users_user (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(255),
            username VARCHAR(255) UNIQUE,
            phone_number VARCHAR(20),
            telegram_id BIGINT,
            password VARCHAR(255),
            is_superuser BOOLEAN DEFAULT FALSE,
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            is_staff BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            is_premium BOOLEAN DEFAULT FALSE,
            date_joined TIMESTAMP DEFAULT NOW()
        );
        """
        await self.execute(sql, execute=True)

    async def execute(
            self,
            command,
            *args,
            fetch: bool = False,
            fetchval: bool = False,
            fetchrow: bool = False,
            execute: bool = False,
    ):
        if self.pool is None:
            raise Exception("Database pool is not created. Call create() method first.")

            # Acquire a connection and execute the SQL command
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join(
            [f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)]
        )
        return sql, tuple(parameters.values())

    async def select_user_by_username(self, username):
        sql = "SELECT * FROM users_user WHERE username = $1"
        return await self.execute(sql, username, fetchrow=True)

    async def add_user(self, full_name=None, username=None, phone_number=None, telegram_id=None,
                       password=None, is_superuser=False, first_name=None, last_name=None,
                       is_staff=False, is_active=True, is_premium=False, date_joined=None):
        # Bazada bu usernameni tekshirish
        user_exists = await self.select_user_by_username(username)
        if user_exists:
            # Bazada foydalanuvchi allaqachon mavjud
            # Agar foydalanuvchi allaqachon mavjud bo'lsa, uni yangilash kerak
            sql = """
            UPDATE users_user SET full_name=$1, phone_number=$2, telegram_id=$3, password=$4,
            is_superuser=$5, first_name=$6, last_name=$7, is_staff=$8, is_active=$9, is_premium=$10, date_joined=$11
            WHERE username=$12
            """
            result = await self.execute(sql, full_name, phone_number, telegram_id, password,
                                        is_superuser, first_name, last_name, is_staff, is_active, is_premium,
                                        date_joined, username, execute=True)
        else:
            # Bazada foydalanuvchi mavjud emas
            # Yangi foydalanuvchi qo'shish
            sql = """
            INSERT INTO users_user (full_name, username, phone_number, telegram_id, password, is_superuser, 
                                    first_name, last_name, is_staff, is_active, is_premium, date_joined)
            VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12) returning *
            """
            result = await self.execute(sql, full_name, username, phone_number, telegram_id, password,
                                        is_superuser, first_name, last_name, is_staff, is_active, is_premium,
                                        date_joined, fetchrow=True)
        return result

    async def select_all_users(self):
        sql = "SELECT * FROM users_user"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM users_user WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM users_user"
        return await self.execute(sql, fetchval=True)

    async def update_user(self, user_id, **kwargs):
        sql = "UPDATE users_user SET "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        sql += f" WHERE id=${len(parameters) + 1}"
        parameters += (user_id,)
        return await self.execute(sql, *parameters, execute=True)

    async def delete_user(self, user_id):
        sql = "DELETE FROM users_user WHERE id=$1"
        return await self.execute(sql, user_id, execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE users_user", execute=True)
