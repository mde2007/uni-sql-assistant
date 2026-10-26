import asyncpg
from app.config import DATABASE_URL

pool = None


async def init_pool():
    global pool
    pool = await asyncpg.create_pool(
        dsn=DATABASE_URL,
        min_size=2,
        max_size=10,
        command_timeout=10,
        server_settings={"statement_timeout": "5000"},  # 5 секунд на запрос
    )


async def close_pool():
    await pool.close()


async def fetch_all(sql):
    async with pool.acquire() as conn:
        async with conn.transaction(readonly=True):
            stmt = await conn.prepare(sql)
            columns = [attr.name for attr in stmt.get_attributes()]
            records = await stmt.fetch()
    rows = [list(record.values()) for record in records]
    return columns, rows