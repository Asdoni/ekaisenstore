from typing import Optional, Any

from discord.ext.commands import CheckFailure, NoPrivateMessage, check


class NotAllowedGuild(CheckFailure):
    def __init__(self, message: Optional[str] = None, *args: Any) -> None:
        super().__init__(message or "Command cannot be used on this Server", *args)


def is_allowed_guild(items: [str, int]):
    r"""A :func:`.check` that is added that checks if the command got invoked in
     **any** of the guilds specified. This means that if the guild is in
    one out of the guilds, then this check will return ``True``.

    The names or IDs passed in must be exact.

    This check raises one of two special exceptions, :exc:`.NotAllowedGuild` if the guild
    is not in the list, or :exc:`.NoPrivateMessage` if it is used in a private message.
    Both inherit from :exc:`.CheckFailure`.

    Parameters
    -----------
    items: List[:class:`str`, :class:`int`]
        An argument list of names or IDs to check that the guild is in.

    Example
    --------
        @bot.command()
        @is_allowed_guild('EGirlzstore', 674015699190022207)
        async def cool(ctx):
            await ctx.send('this is a cool server')
    """

    def predicate(ctx):
        if ctx.guild is None:
            raise NoPrivateMessage()
        if any(
                ctx.guild.id == item if isinstance(item, int)
                else ctx.guild.name == item for item in items
        ):
            return True
        raise NotAllowedGuild()

    return check(predicate)

# add more custom errors and checks if needed
