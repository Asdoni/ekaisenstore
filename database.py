import asyncio
import os
from logging import Logger
import asyncpg

class Database:
    def __init__(self, logger: Logger):
        self.pool = None
        #self.logger = logger
        
    async def connect(self):
        try:
            #self.logger.info("Trying to connect to the database...")
            # Include SSL mode in the connection parameters
            self.pool = await asyncpg.create_pool(
                dsn=os.getenv('DATABASE_URL'), 
                ssl='require'
                )

            #self.logger.info("Successfully connected to the database with SSL.")
        except Exception as e:
            #self.logger.error(f"Failed to connect to the database: {e}")
            raise

    async def close(self):
        if self.pool:
            await self.pool.close()
            #self.logger.info("Closed database pool")

    async def execute(self, query, *args):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    await connection.execute(query, *args)
                    #self.logger.debug(f"[Database Execute]: '{query}'")
                    return True, None  # Indicate success, and no error message
                except asyncpg.UniqueViolationError as e:
                    #self.logger.error(f"Unique constraint failed to execute query: {e}")
                    return False, "This PID is already registered in this guild."  # Indicate failure and provide an error message
                except Exception as e:
                    #self.logger.error(f"Failed to execute query: {e}")
                    return False, f"An error occurred: {e}"  # Indicate failure and provide a generic error message

    async def fetchone(self, query, *args):
        async with self.pool.acquire() as connection:
            try:
                result = await connection.fetchrow(query, *args)
                #self.logger.debug(f"[Database Fetchone]: '{query}'")
                return result
            except Exception as e:
                #self.logger.error(f"Failed to fetch data: {e}")
                raise

    async def fetchall(self, query, *args):
        async with self.pool.acquire() as connection:
            try:
                result = await connection.fetch(query, *args)
                #self.logger.debug(f"[Database Fetchall]: '{query}'")
                return result
            except Exception as e:
                #self.logger.error(f"Failed to fetch data: {e}")
                raise
