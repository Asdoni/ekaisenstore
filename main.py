import logging

from bot import EGirlzStoreBot

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(levelname)s: %(message)s")
    bot = EGirlzStoreBot(cogs_dir="cogs", enable_wip_commands=False, case_insensitive=True)
    bot.run()
