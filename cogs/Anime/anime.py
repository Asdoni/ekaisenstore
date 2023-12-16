import discord
import hmtai
from discord import app_commands
from discord.ext import commands

from bot import EGirlzStoreBot

class Anime(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    async def create_and_send_embed(self, ctx, user, action, image_type, emoji):
        username = ctx.user.display_name
        target_username = user.display_name
        image_url = hmtai.get("hmtai", image_type)

        embed = discord.Embed(
            title=f"{username} {action} {target_username} {emoji}",
            color=0x00ff00
        )
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Requested by {username}", icon_url=ctx.user.display_avatar.url)

        await ctx.response.send_message(embed=embed)

    # START SFW COMMANDS
    @app_commands.command(name="wave", description="Greeting! Wave gifs! (●'◡'●)")
    async def wave(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "waves at", "wave", "👋")

    @app_commands.command(name="tea", description="I want some tea! ☕")
    async def tea(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "gives", "tea", "☕")

    @app_commands.command(name="punch", description="ONE PUUUUUUUUUUUNCH")
    async def punch(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "punches", "punch", "👊")

    @app_commands.command(name="poke", description="Poke-poke :P")
    async def poke(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "pokes", "poke", ":P")

    @app_commands.command(name="pat", description="Let's pat some good guys (/ω＼)")
    async def pat(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "pats", "pat", "(/ω＼)")

    @app_commands.command(name="kiss", description="Kissu! :3")
    async def kiss(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "kisses", "kiss", ":3")

    @app_commands.command(name="feed", description="Who want eat? :P")
    async def feed(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "feeds", "feed", ":P")

    @app_commands.command(name="hug", description="I like hugs, do you?")
    async def hug(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "hugs", "hug", "❤️")

    @app_commands.command(name="cuddle", description="Cuddle cuddle cuddle xD")
    async def cuddle(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "cuddles with", "cuddle", "xD")

    @app_commands.command(name="cry", description="Bite bite biting 😢")
    async def cry(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "cries with", "cry", "😢")

    @app_commands.command(name="slap", description="BAKA!!")
    async def slap(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "slaps", "slap", "BAKA!!")

    @app_commands.command(name="lick", description="Mmm hum hum, so tasty💄")
    async def lick(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "licks", "lick", "💄")

    @app_commands.command(name="bite", description="Nyaaaaaa!!")
    async def bite(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "bites", "bite", "Nyaaaaaa!!")

    @app_commands.command(name="dance", description="Show off your dancing! 💃")
    async def dance(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "dances with", "dance", "💃")

    @app_commands.command(name="boop", description="Boopyy")
    async def boop(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "boops", "boop", "Boopyy")

    @app_commands.command(name="sleep", description="Zzz 💤")
    async def sleep(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "sleeps next to", "sleep", "💤")

    @app_commands.command(name="like", description="I like it, nice 👍")
    async def like(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "likes", "like", "👍")

    @app_commands.command(name="kill", description="Kill everyone, everybody!")
    async def kill(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "kills", "kill", "💀")

    @app_commands.command(name="nosebleed", description="That's...impressive")
    async def nosebleed(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "makes", "nosebleed", "👃💦")

    @app_commands.command(name="threaten", description="Rrrr")
    async def threaten(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "threatens", "threaten", "😡")

    @app_commands.command(name="tickle", description="Tiiickle tickle tickle :3")
    async def tickle(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "tickles", "tickle", ":3")

    @app_commands.command(name="depression", description="Depression Gifs :c")
    async def depression(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "sends", "depression", ":c")

    @app_commands.command(name="bonk", description="Bonk another user! 💥🔨")
    async def bonk(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "bonks", "bonk", "💥🔨")

    @app_commands.command(name="bully", description="User to bully")
    async def bully(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "bullies", "bully", "💢")

    @app_commands.command(name="hold", description="User to hold")
    async def hold(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "holds", "hold", "🤭")

    @app_commands.command(name="kick", description="Kick another user! 👢")
    async def kick(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "kicks", "kick", "👢")

    @app_commands.command(name="throw", description="Yeet another user! 🗑🤾‍♀️")
    async def throw(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "throws", "throw", "🗑🤾‍♀️")

    @app_commands.command(name="blush", description="Show your blush! 💗")
    async def blush(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "made", "blush", "blushes 💗")

    @app_commands.command(name="happy", description="Show off your happiness! 🥰")
    async def happy(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "make", "happy", "🥰")

    @app_commands.command(name="nom", description="Nom Nom! 🍔")
    async def nom(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "noms", "nom", "🍔")

    @app_commands.command(name="sad", description="Show your sadness! 😭")
    async def sad(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "is sad with", "sad", "😭")

    @app_commands.command(name="smile", description="Show your teeth! 😄")
    async def smile(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "smiles at", "smile", "😄")

    @app_commands.command(name="smug", description="You where right and they know it. 🤪")
    async def smug(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "is smug at", "smug", "🤪")

    @app_commands.command(name="wink", description="wink wink! 😉")
    async def wink(self, ctx, user: discord.Member):
        await self.create_and_send_embed(ctx, user, "winks at", "wink", "😉")

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(Anime(bot))
