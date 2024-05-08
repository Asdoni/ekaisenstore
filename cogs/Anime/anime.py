import discord
import hmtai
from discord import app_commands
from discord.ext import commands

from bot import EGirlzStoreBot

class Anime(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    async def create_and_send_embed(self, interaction: discord.Interaction, user: discord.Member, action, image_type, emoji):
        await interaction.response.defer(ephemeral=False)

        username = interaction.user.display_name
        target_username = user.display_name
        image_url = hmtai.get("hmtai", image_type)

        embed = discord.Embed(
            title=f"{username} {action} {target_username} {emoji}",
            color=0x00ff00
        )
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Requested by {username}", icon_url=interaction.user.display_avatar.url)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="wave", description="Greeting! Wave gifs! (●'◡'●)")
    async def wave(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "waves at", "wave", "👋")

    @app_commands.command(name="tea", description="I want some tea! ☕")
    async def tea(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "gives", "tea", "☕")

    @app_commands.command(name="punch", description="ONE PUUUUUUUUUUUNCH")
    async def punch(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "punches", "punch", "👊")

    @app_commands.command(name="poke", description="Poke-poke :P")
    async def poke(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "pokes", "poke", ":P")

    @app_commands.command(name="pat", description="Let's pat some good guys (/ω＼)")
    async def pat(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "pats", "pat", "(/ω＼)")

    @app_commands.command(name="kiss", description="Kissu! :3")
    async def kiss(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "kisses", "kiss", ":3")

    @app_commands.command(name="feed", description="Who want eat? :P")
    async def feed(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "feeds", "feed", ":P")

    @app_commands.command(name="hug", description="I like hugs, do you?")
    async def hug(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "hugs", "hug", "❤️")

    @app_commands.command(name="cuddle", description="Cuddle cuddle cuddle xD")
    async def cuddle(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "cuddles with", "cuddle", "xD")

    @app_commands.command(name="cry", description="Cry 😭")
    async def cry(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "cries with", "cry", "😢")

    @app_commands.command(name="slap", description="BAKA!!")
    async def slap(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "slaps", "slap", "BAKA!!")

    @app_commands.command(name="lick", description="Mmm hum hum, so tasty💄")
    async def lick(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "licks", "lick", "💄")

    @app_commands.command(name="bite", description="Nyaaaaaa!!")
    async def bite(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "bites", "bite", "Nyaaaaaa!!")

    @app_commands.command(name="dance", description="Show off your dancing! 💃")
    async def dance(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "dances with", "dance", "💃")

    @app_commands.command(name="boop", description="Boopyy")
    async def boop(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "boops", "boop", "Boopyy")

    @app_commands.command(name="sleep", description="Zzz 💤")
    async def sleep(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "sleeps next to", "sleep", "💤")

    @app_commands.command(name="like", description="I like it, nice 👍")
    async def like(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "likes", "like", "👍")

    @app_commands.command(name="kill", description="Kill everyone, everybody!")
    async def kill(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "kills", "kill", "💀")

    @app_commands.command(name="nosebleed", description="That's...impressive")
    async def nosebleed(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "makes", "nosebleed", "👃💦")

    @app_commands.command(name="threaten", description="Rrrr")
    async def threaten(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "threatens", "threaten", "😡")

    @app_commands.command(name="tickle", description="Tiiickle tickle tickle :3")
    async def tickle(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "tickles", "tickle", ":3")

    @app_commands.command(name="depression", description="Depression Gifs :c")
    async def depression(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "sends", "depression", ":c")

    @app_commands.command(name="bonk", description="Bonk another user! 💥🔨")
    async def bonk(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "bonks", "bonk", "💥🔨")

    @app_commands.command(name="bully", description="User to bully")
    async def bully(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "bullies", "bully", "💢")

    @app_commands.command(name="hold", description="User to hold")
    async def hold(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "holds", "hold", "🤭")

    @app_commands.command(name="kick", description="Kick another user! 👢")
    async def kick(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "kicks", "kick", "👢")

    @app_commands.command(name="throw", description="Yeet another user! 🗑🤾‍♀️")
    async def throw(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "throws", "throw", "🗑🤾‍♀️")

    @app_commands.command(name="blush", description="Show your blush! 💗")
    async def blush(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "made", "blush", "blushes 💗")

    @app_commands.command(name="happy", description="Show off your happiness! 🥰")
    async def happy(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "make", "happy", "🥰")

    @app_commands.command(name="nom", description="Nom Nom! 🍔")
    async def nom(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "noms", "nom", "🍔")

    @app_commands.command(name="sad", description="Show your sadness! 😭")
    async def sad(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "is sad with", "sad", "😭")

    @app_commands.command(name="smile", description="Show your teeth! 😄")
    async def smile(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "smiles at", "smile", "😄")

    @app_commands.command(name="smug", description="You where right and they know it. 🤪")
    async def smug(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "is smug at", "smug", "🤪")

    @app_commands.command(name="wink", description="wink wink! 😉")
    async def wink(self, interaction: discord.Interaction, user: discord.Member):
        await self.create_and_send_embed(interaction, user, "winks at", "wink", "😉")

async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(Anime(bot))
