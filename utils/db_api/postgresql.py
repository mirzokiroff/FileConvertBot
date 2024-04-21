from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
            port=config.DB_PORT
        )

    async def execute(
            self,
            command,
            *args,
            fetch: bool = False,
            fetchval: bool = False,
            fetchrow: bool = False,
            execute: bool = False,
    ):
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

    async def add_channel(self, chat_id):
        sql = (
            "INSERT INTO chanel_channel (chat_id)"
            " VALUES($1) returning *"
        )
        return await self.execute(sql, chat_id, fetchrow=True)

    async def select_all_channel(self):
        sql = "SELECT * FROM chanel_channel"
        return await self.execute(sql, fetch=True)

    async def select_channel(self, **kwargs):
        sql = "SELECT * FROM chanel_channel WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def update_channel(self, chat_id):
        sql = "UPDATE chanel_channel SET chat_id=$1 WHERE id=$2"
        return await self.execute(sql, chat_id, execute=True)

    async def delete_channel(self, course_id):
        sql = "DELETE FROM chanel_channel WHERE id=$1"
        return await self.execute(sql, course_id, execute=True)
