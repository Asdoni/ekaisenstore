import logging
import os
import platform
import time
import traceback
import typing
from datetime import datetime, timedelta

from colorama import Fore
from discord import Message, app_commands, Interaction, LoginFailure, Intents, __version__, Activity, ActivityType, \
    Status, ClientUser
from discord.app_commands import AppCommandError, MissingPermissions
from discord.ext import commands
from discord.ext.commands import Context, errors
from discord.ext.commands._types import BotT
from dotenv import load_dotenv
from requests import Session

from customHttpAdapter import get_legacy_session
from database import Database
from formatter import format_timestamp, format_second
from oldCommandCustomErrors import NotAllowedGuild
from slashCommandCustomErrors import NSWFError, TranslationError

logger = logging.getLogger()


class EGirlzStoreBot(commands.Bot):
    http_session: Session
    _uptime: datetime = datetime.utcnow()

    def __init__(self, cogs_dir: str, enable_wip_commands=False, *args: typing.Any, **kwargs: typing.Any):
        load_dotenv()
        super().__init__(
            *args,
            **kwargs,
            command_prefix=os.environ.get('PREFIX'),
            intents=Intents.all(),
            tree_cls=CommandTree,
        )
        self.logger = logger
        self.db = Database(self.logger)
        self.cogs_dir = cogs_dir
        self.synced = False
        self.enable_wip_commands = enable_wip_commands

    async def _load_extensions(self) -> None:
        if not os.path.isdir(self.cogs_dir):
            self.logger.error(f"Cog directory {self.cogs_dir} does not exist.")
            return
        for (dirpath, dirnames, filenames) in os.walk(self.cogs_dir):
            if "not_working" in dirpath:
                continue  # don't load not working commands
            if "WIP" in dirpath and not self.enable_wip_commands:
                continue  # don't load wip commands
            for filename in filenames:
                if filename.endswith('.py') and not filename.startswith('_'):
                    try:
                        python_path = os.path.relpath(dirpath, os.path.dirname(__file__)).replace(os.sep, '.')
                        await self.load_extension(f"{python_path}.{filename[:-3]}")
                        self.logger.info(f"Loaded cog {filename[:-3]}")
                    except commands.ExtensionError:
                        self.logger.error(f"Failed to load cog {filename[:-3]}\n{traceback.format_exc()}")

    async def on_ready(self) -> None:
        self.logger.info(f'Logged in as {Fore.YELLOW}{self.user.name}{Fore.RESET}')
        self.logger.debug(f'Bot ID {Fore.YELLOW}{self.user.id}{Fore.RESET}')
        self.logger.debug(f'Discord Version {Fore.YELLOW}{__version__}{Fore.RESET}')
        self.logger.debug(f'Python Version {Fore.YELLOW}{platform.python_version()}{Fore.RESET}')
        custom_status = Activity(name="you...", type=ActivityType.watching)
        await self.change_presence(status=Status.online, activity=custom_status)

    async def setup_hook(self) -> None:
        self.http_session = get_legacy_session()
        await self.db.connect()
        await self._load_extensions()
        if not self.synced:
            self.logger.info("Start syncing command tree...")
            await self.tree.sync()
            self.synced = not self.synced
            self.logger.info("Synced command tree")

    async def close(self) -> None:
        await super().close()
        await self.db.close()
        self.http_session.close()

    def run(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        try:
            super().run(str(os.getenv("TOKEN")), *args, **kwargs)
        except (LoginFailure, KeyboardInterrupt):
            self.logger.info("Exiting...")
            exit()

    async def on_message(self, message: Message):
        # Check if the message author is a bot
        if message.author.bot:
            return  # Ignore messages from bots
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        author_display_name = message.author.display_name

        # Check if the message has attachments
        if message.attachments:
            attachment_info = "Attachment: " + ", ".join(attachment.filename for attachment in message.attachments)
            self.logger.debug(f"{timestamp} - {author_display_name}: - {attachment_info}")
        else:
            self.logger.debug(f"{timestamp} - {author_display_name}: - {message.content}")
        await self.process_commands(message)

    @property
    def user(self) -> ClientUser:
        assert super().user, "Bot is not ready yet"
        return typing.cast(ClientUser, super().user)

    @property
    def uptime(self) -> timedelta:
        return datetime.utcnow() - self._uptime

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context[BotT], error: errors.CommandError, /) -> None:
        if not isinstance(error, commands.CommandNotFound):
            # delete msg if a command error occurred
            await ctx.message.delete(delay=3)
        if isinstance(error, NotAllowedGuild):
            self.logger.error(f"{ctx.command} cannot be used in guild {ctx.guild.name}")
            await ctx.send(error.args[0], ephemeral=True, delete_after=20)
        elif isinstance(error, commands.CheckFailure):
            self.logger.error(f"{ctx.command} failed check {error}")
            await ctx.send(error.args[0], ephemeral=True, delete_after=20)
        else:
            return await super().on_command_error(ctx, error)


class CommandTree(app_commands.CommandTree):
    async def on_error(self, interaction: Interaction, error: AppCommandError) -> None:
        # FIXME handle issue when interaction had already a message sent
        if isinstance(error, app_commands.errors.CommandOnCooldown):
            logger.error(
                (
                    f"{interaction.user} failed to use command {interaction.command.name} because of cooldown"
                    f" ({format_second(round(error.retry_after))})"
                )
            )
            await interaction.response.send_message(
                f'This command is on cooldown, you can use it again'
                f' {format_timestamp(round(time.time() + error.retry_after))}',
                ephemeral=True,
            )
        elif isinstance(error, NSWFError):
            logger.error(
                (
                    f"{interaction.user} failed to use command {interaction.command.name} because "
                    f"{interaction.channel.name} is not nswf"
                )
            )
            await interaction.response.send_message(error, ephemeral=True)
        elif isinstance(error, commands.CheckFailure):
            logger.error(error)
            await interaction.response.send_message(error.args[0], ephemeral=True)
        elif isinstance(error, TranslationError):
            logger.error(f'{interaction.user} failed to use translation {traceback.format_exc()}')
            await interaction.response.send_message(error, ephemeral=True)
        elif isinstance(error, MissingPermissions):
            logger.error(f'{interaction.user} failed to use {interaction.command.name} because of missing permission')
            await interaction.response.send_message(error, ephemeral=True)
        # catch more errors if necessary
        else:
            logger.error(
                f'Ignoring exception in command {interaction.command}:\n'
                f'{traceback.format_exc()}'
            )
            await interaction.response.send_message(
                f'Ups! Something went wrong while processing the command',
                ephemeral=True,
            )
