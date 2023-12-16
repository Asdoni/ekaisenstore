import os
from logging import Logger

import aiomysql


class Database:
    def __init__(self, logger: Logger):
        self.pool = None
        self.logger = logger

    async def connect(self):
        try:
            host = os.getenv('DB_HOST')
            port = int(os.environ.get('DB_PORT'))
            user = os.environ.get('DB_USER')
            self.logger.info(f"trying to connect to database on {host}:{port} with user: {user}")
            self.pool = await aiomysql.create_pool(
                host=host,
                user=user,
                port=port,
                password=os.environ.get('DB_PASSWORD'),
                db=os.environ.get('DB_NAME')
            )
            self.logger.info(f"Successfully connected to database '{os.environ.get('DB_NAME')}'")
        except Exception as e:
            self.logger.error(e.args[1])

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.logger.info("Closed database pool")

    async def get_cursor(self):
        if not self.pool:
            await self.connect()
        conn = await self.pool.acquire()
        return conn.cursor()

    async def release(self, con):
        await self.pool.release(con)

    async def commit(self, query=None, *args):
        async with await self.get_cursor() as cur:
            try:
                if query:
                    if args and isinstance(args[0], tuple):
                        await cur.execute(query, args[0])
                    else:
                        await cur.execute(query, args)
                await cur.connection.commit()
                self.logger.debug(f"[Database Commit]: '{query}'")
            except Exception as e:
                await cur.connection.rollback()
                raise e  # Re-raise the exception after rollback
            finally:
                await self.release(cur.connection)

    async def fetchone(self, query, *args):
        async with await self.get_cursor() as cur:
            try:
                if args and isinstance(args[0], tuple):
                    await cur.execute(query, args[0])
                else:
                    await cur.execute(query, args)
                self.logger.debug(f"[Database Fetchone]: '{query}'")
                return await cur.fetchone()
            except Exception as e:
                await cur.connection.rollback()
                raise e
            finally:
                await self.release(cur.connection)

    async def fetchall(self, query, *args):
        async with await self.get_cursor() as cur:
            try:
                if args and isinstance(args[0], tuple):
                    await cur.execute(query, args[0])
                else:
                    await cur.execute(query, args)
                self.logger.debug(f"[Database Fetchall]: '{query}'")
                return await cur.fetchall()
            except Exception as e:
                await cur.connection.rollback()
                raise e
            finally:
                await self.release(cur.connection)
