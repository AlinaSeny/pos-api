import asyncpg

async def get_db_connection():
    return await asyncpg.connect(
        user="postgres",
        password="admin",
        database="pos_db",
        host="localhost"
    )