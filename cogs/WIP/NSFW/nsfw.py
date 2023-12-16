import discord
import hmtai
from discord import app_commands
from discord.ext import commands

from bot import EGirlzStoreBot
from customCommandErrors import UserMentionError


class Anime(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    async def is_nsfw_enabled(self, guild_id):
        res = await self.bot.db.fetchone(f"SELECT is_nsfw FROM nsfw_settings WHERE guild_id = {guild_id}")
        return res and bool(res[0])

    async def create_and_send_embed_sfw(self, ctx, user, action, image_type, emoji):
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

    async def create_and_send_embed_nsfw(self, ctx, image_type):
        username = ctx.user.display_name
        image_url = hmtai.get("hmtai", image_type)
        command_name = ctx.command.name
        command_description = ctx.command.description

        embed = discord.Embed(
            title=f"{command_name} - {command_description}",
            color=0x00ff00
        )

        embed.set_image(url=image_url)
        embed.set_footer(text=f"Requested by {username}", icon_url=ctx.user.display_avatar.url)

        await ctx.response.send_message(embed=embed)

    async def create_and_send_embed_sfw_no_user(self, ctx, image_type):
        username = ctx.user.display_name
        image_url = hmtai.get("hmtai", image_type)
        command_name = ctx.command.name
        command_description = ctx.command.description

        embed = discord.Embed(
            title=f"{command_name} - {command_description}",
            color=0x00ff00
        )

        embed.set_image(url=image_url)
        embed.set_footer(text=f"Requested by {username}", icon_url=ctx.user.display_avatar.url)

        await ctx.response.send_message(embed=embed)

    # START SFW COMMANDS

    @app_commands.command(name="wave", description="Greeting! Wave gifs! (●'◡'●)")
    @app_commands.check(UserMentionError)
    async def wave(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "waves at", "wave", "👋")

    @app_commands.command(name="tea", description="I want some tea! ☕")
    @app_commands.check(UserMentionError)
    async def tea(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "gives", "tea", "☕")

    @app_commands.command(name="punch", description="ONE PUUUUUUUUUUUNCH")
    @app_commands.check(UserMentionError)
    async def punch(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "punches", "punch", "👊")

    @app_commands.command(name="poke", description="Poke-poke :P")
    @app_commands.check(UserMentionError)
    async def poke(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "pokes", "poke", ":P")

    @app_commands.command(name="pat", description="Let's pat some good guys (/ω＼)")
    @app_commands.check(UserMentionError)
    async def pat(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "pats", "pat", "(/ω＼)")

    @app_commands.command(name="kiss", description="Kissu! :3")
    @app_commands.check(UserMentionError)
    async def kiss(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "kisses", "kiss", ":3")

    @app_commands.command(name="feed", description="Who want eat? :P")
    @app_commands.check(UserMentionError)
    async def feed(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "feeds", "feed", ":P")

    @app_commands.command(name="hug", description="I like hugs, do you?")
    @app_commands.check(UserMentionError)
    async def hug(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "hugs", "hug", "❤️")

    @app_commands.command(name="cuddle", description="Cuddle cuddle cuddle xD")
    @app_commands.check(UserMentionError)
    async def cuddle(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "cuddles with", "cuddle", "xD")

    @app_commands.command(name="cry", description="Bite bite biting 😢")
    @app_commands.check(UserMentionError)
    async def cry(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "cries with", "cry", "😢")

    @app_commands.command(name="slap", description="BAKA!!")
    @app_commands.check(UserMentionError)
    async def slap(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "slaps", "slap", "BAKA!!")

    @app_commands.command(name="lick", description="Mmm hum hum, so tasty💄")
    @app_commands.check(UserMentionError)
    async def lick(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "licks", "lick", "💄")

    @app_commands.command(name="bite", description="Nyaaaaaa!!")
    @app_commands.check(UserMentionError)
    async def bite(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "bites", "bite", "Nyaaaaaa!!")

    @app_commands.command(name="dance", description="Show off your dancing! 💃")
    @app_commands.check(UserMentionError)
    async def dance(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "dances with", "dance", "💃")

    @app_commands.command(name="boop", description="Boopyy")
    @app_commands.check(UserMentionError)
    async def boop(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "boops", "boop", "Boopyy")

    @app_commands.command(name="sleep", description="Zzz 💤")
    @app_commands.check(UserMentionError)
    async def sleep(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "sleeps next to", "sleep", "💤")

    @app_commands.command(name="like", description="I like it, nice 👍")
    @app_commands.check(UserMentionError)
    async def like(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "likes", "like", "👍")

    @app_commands.command(name="kill", description="Kill everyone, everybody!")
    @app_commands.check(UserMentionError)
    async def kill(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "kills", "kill", "💀")

    @app_commands.command(name="nosebleed", description="That's...impressive")
    @app_commands.check(UserMentionError)
    async def nosebleed(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "makes", "nosebleed", "👃💦")

    @app_commands.command(name="threaten", description="Rrrr")
    @app_commands.check(UserMentionError)
    async def threaten(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "threatens", "threaten", "😡")

    @app_commands.command(name="tickle", description="Tiiickle tickle tickle :3")
    @app_commands.check(UserMentionError)
    async def tickle(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "tickles", "tickle", ":3")

    @app_commands.command(name="depression", description="Depression Gifs :c")
    @app_commands.check(UserMentionError)
    async def depression(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "sends", "depression", ":c")

    @app_commands.command(name="bonk", description="Bonk another user! 💥🔨")
    @app_commands.check(UserMentionError)
    async def bonk(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "bonks", "bonk", "💥🔨")

    @app_commands.command(name="bully", description="User to bully")
    @app_commands.check(UserMentionError)
    async def bully(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "bullys", "bully", "💢")

    @app_commands.command(name="hold", description="User to hold")
    @app_commands.check(UserMentionError)
    async def hold(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "holds", "hold", "🤭")
        
    @app_commands.command(name="kick", description="Kick another user! 👢")
    @app_commands.check(UserMentionError)
    async def kick(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "kicks", "kick", "👢")

    @app_commands.command(name="throw", description="Yeet another user! 🗑🤾‍♀️")
    @app_commands.check(UserMentionError)
    async def throw(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "throws", "throw", "🗑🤾‍♀️")

    @app_commands.command(name="blush", description="Show your blush! 💗")
    @app_commands.check(UserMentionError)
    async def blush(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "made", "blush", "blushes 💗")
        
    @app_commands.command(name="happy", description="Show off your happiness! 🥰")
    @app_commands.check(UserMentionError)
    async def happy(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "make", "happy", "🥰")

    @app_commands.command(name="nom", description="Nom Nom! 🍔")
    @app_commands.check(UserMentionError)
    async def nom(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "noms", "nom", "🍔")
    
    @app_commands.command(name="sad", description="Show your sadness! 😭")
    @app_commands.check(UserMentionError)
    async def sad(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "is sad with", "sad", "😭")

    @app_commands.command(name="smile", description="Show your teeth! 😄")
    @app_commands.check(UserMentionError)
    async def smile(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "smiles at", "smile", "😄")

    @app_commands.command(name="smug", description="You where right and they know it. 🤪")
    @app_commands.check(UserMentionError)
    async def smug(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "is smug at", "smug", "🤪")

    @app_commands.command(name="wink", description="wink wink! 😉")
    @app_commands.check(UserMentionError)
    async def wink(self, ctx, user: discord.Member):
        await self.create_and_send_embed_sfw(ctx, user, "winks at", "wink", "😉")


'''''''''
# SFW NO USER - ARTS

    @app_commands.command(name="jahy_arts", description="So hot Jahy :3")
    @app_commands.check(UserMentionError)
    async def jahy_arts(self, ctx):
        await self.create_and_send_embed_sfw_no_user(ctx, "jahy_arts")

    @app_commands.command(name="neko_arts", description="SFW Neko Girls (Cat Girls)")
    @app_commands.check(UserMentionError)
    async def neko_arts(self, ctx):
        await self.create_and_send_embed_sfw_no_user(ctx, "neko_arts")

    @app_commands.command(name="coffee_arts", description="Do you want some coffee? And girls :3")
    @app_commands.check(UserMentionError)
    async def coffee_arts(self, ctx):
        await self.create_and_send_embed_sfw_no_user(ctx, "coffee_arts")

    @app_commands.command(name="wallpaper", description="SFW Wallpaper with Anime")
    @app_commands.check(UserMentionError)
    async def wallpaper(self, ctx):
        await self.create_and_send_embed_sfw_no_user(ctx, "wallpaper")

    @app_commands.command(name="mobilewallpaper", description="SFW Wallpaper with Anime on Mobile")
    @app_commands.check(UserMentionError)
    async def mobilewallpaper(self, ctx):
        await self.create_and_send_embed_sfw_no_user(ctx, "mobilewallpaper")


# ENABLE/DISABLE NSFW COMMANDS


    @app_commands.command(name="nsfw", description="Enable/Disable NSFW commands")
    @discord.app_commands.checks.has_permissions(administrator=True)
    @app_commands.check(UserMentionError)
    async def nsfw(self, ctx, setting: bool):
        await ctx.response.defer()
        guild_id = ctx.guild.id

        async with aiomysql.connect(
                host=os.environ.get('DB_HOST'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                db=os.environ.get('DB_NAME')) as conn:
            async with conn.cursor() as cur:
                await cur.execute("REPLACE INTO nsfw_settings (guild_id, is_nsfw) VALUES (%s, %s)", (guild_id, setting))
                await conn.commit()

        await ctx.followup.send(f"NSFW set to {setting}")

# START NSFW COMMANDS

    @app_commands.command(name="anal", description="Does somebody like being in all holes?~")
    @app_commands.check(UserMentionError)
    async def anal(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return
        
        await self.create_and_send_embed_nsfw(ctx, "anal")

    @app_commands.command(name="ass", description="I know you like anime ass~ uwu")
    @app_commands.check(UserMentionError)
    async def ass(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return
        
        await self.create_and_send_embed_nsfw(ctx, "ass")

    @app_commands.command(name="bdsm", description="If you don't know what it is, search it up")
    @app_commands.check(UserMentionError)
    async def bdsm(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return
        
        await self.create_and_send_embed_nsfw(ctx, "bdsm")

    @app_commands.command(name="cum", description="Basically sticky white stuff that is usually milked from sharpies.")
    @app_commands.check(UserMentionError)
    async def cum(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return
        
        await self.create_and_send_embed_nsfw(ctx, "cum")

    @app_commands.command(name="classic", description="Relaxing classic kekus uwu")
    @app_commands.check(UserMentionError)
    async def classic(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return
        
        await self.create_and_send_embed_nsfw(ctx, "classic")


    @app_commands.command(name="creampie", description="So hot, sticky, and inside uwu")
    @app_commands.check(UserMentionError)
    async def creampie(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return
        
        await self.create_and_send_embed_nsfw(ctx, "creampie")


    @app_commands.command(name="manga", description="Sends a random doujin page imageURL!")
    @app_commands.check(UserMentionError)
    async def manga(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return
        
        await self.create_and_send_embed_nsfw(ctx, "manga")


    @app_commands.command(name="femdom", description="Female Domination?")
    @app_commands.check(UserMentionError)
    async def femdom(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return
        
        await self.create_and_send_embed_nsfw(ctx, "femdom")


    @app_commands.command(name="hentai", description="Sends a random vanilla hentai imageURL~")
    @app_commands.check(UserMentionError)
    async def hentai(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return
        
        await self.create_and_send_embed_nsfw(ctx, "hentai")


    @app_commands.command(name="thighs", description="Oh, i so like it, it's best of the best, like a religion ❤️")
    @app_commands.check(UserMentionError)
    async def thighs(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "thighs")

    @app_commands.command(name="incest", description="I know, you like it. Brothet and sister <3 And..mo...omg")
    @app_commands.check(UserMentionError)
    async def incest(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "incest")

    @app_commands.command(name="masturbation", description="You like lewd solo?~")
    @app_commands.check(UserMentionError)
    async def masturbation(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "masturbation")

    @app_commands.command(name="public", description="Some people like do it on a public..uh~")
    @app_commands.check(UserMentionError)
    async def public(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "public")

    @app_commands.command(name="ero", description="eros, ero Uniforms, etc, you know what eros are :3")
    @app_commands.check(UserMentionError)
    async def ero(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "ero")

    @app_commands.command(name="orgy", description="Group Lewd Acts")
    @app_commands.check(UserMentionError)
    async def orgy(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "orgy")

    @app_commands.command(name="elves", description="So, it's not Elvis Presley, but i know, you like it :)")
    @app_commands.check(UserMentionError)
    async def elves(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "elves")

    @app_commands.command(name="yuri", description="What about cute Les?~")
    @app_commands.check(UserMentionError)
    async def yuri(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "yuri")

    @app_commands.command(name="pantsu", description="I mean... just why? You like underwear?")
    @app_commands.check(UserMentionError)
    async def pantsu(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "pantsu")

    @app_commands.command(name="glasses", description="Girls that wear glasses, uwu~")
    @app_commands.check(UserMentionError)
    async def glasses(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "glasses")

    @app_commands.command(name="boobjob", description="So soft, round ... gentle ... damn we love it")
    @app_commands.check(UserMentionError)
    async def boobjob(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "boobjob")


    @app_commands.command(name="cuckold", description="Wow, I won't even question your fetishes.")
    @app_commands.check(UserMentionError)
    async def cuckold(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "cuckold")


    @app_commands.command(name="blowjob", description="Basically an image of a girl sucking on a sharp blade!")
    @app_commands.check(UserMentionError)
    async def blowjob(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "blowjob")


    @app_commands.command(name="footjob", description="So you like smelly feet huh?")
    @app_commands.check(UserMentionError)
    async def footjob(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "footjob")


    @app_commands.command(name="handjob", description="So you like how's it feeling in hand, huh?")
    @app_commands.check(UserMentionError)
    async def handjob(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "handjob")


    @app_commands.command(name="boobs", description="A-am..that's normal size!")
    @app_commands.check(UserMentionError)
    async def boobs(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "boobs")
    
    
    @app_commands.command(name="gif", description="Basically an animated image, so yes :3")
    @app_commands.check(UserMentionError)
    async def gif(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "gif")


    @app_commands.command(name="tentacles", description="I'm sorry but, why do you like it? Uh..")
    @app_commands.check(UserMentionError)
    async def tentacles(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "tentacles")


    @app_commands.command(name="gangbang", description="5 on 1? Uh..")
    @app_commands.check(UserMentionError)
    async def gangbang(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "gangbang")


    @app_commands.command(name="ahegao", description="So happy woman faces :))")
    @app_commands.check(UserMentionError)
    async def ahegao(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "ahegao")


    @app_commands.command(name="uniform", description="School and many other Uniforms~")
    @app_commands.check(UserMentionError)
    async def uniform(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "uniform")


    @app_commands.command(name="pussy", description="The genitals of a female, or a cat, you give the meaning.")
    @app_commands.check(UserMentionError)
    async def pussy(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "pussy")


    @app_commands.command(name="nsfwneko", description="NSFW Neko Girls (Cat Girls)")
    @app_commands.check(UserMentionError)
    async def nsfwneko(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "nsfwneko")

    @app_commands.command(name="nsfwmobilewallpaper", description="NSFW Anime Mobile Wallpaper")
    @app_commands.check(UserMentionError)
    async def nsfwmobilewallpaper(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "nsfwmobilewallpaper")

    @app_commands.command(name="zettairyouiki", description="That one part of the flesh being squeeze in thigh-highs~<3")
    @app_commands.check(UserMentionError)
    async def zettairyouiki(self, ctx):
        if not ctx.channel.is_nsfw():
            await ctx.response.send_message("This command is only available in NSFW channels.")
            return

        if not await self.is_nsfw_enabled(ctx.guild.id):
            await ctx.response.send_message("NSFW commands are disabled in this server.")
            return

        await self.create_and_send_embed_nsfw(ctx, "zettairyouiki")

   
    @app_commands.command(name="sfw_commands", description="List all SFW commands")
    @app_commands.check(UserMentionError)
    async def sfw_commands(self, ctx):
        field_count = 0  # Counter for embed fields
        embed = discord.Embed(
            title="🌟 SFW Commands 🌟",
            description="Here are all the shiny commands available in the SFW section!",
            color=0x4CAF50  # Green color
        )
        
        
        commands_list = [
            (f"/wave", "Greeting! Wave gifs! (●'◡'●)"),
            (f"/tea", "I want some tea! ☕"),
            (f"/punch", "ONE PUUUUUUUUUUUNCH"),
            (f"/poke", "Poke-poke :P"),
            (f"/pat", "Let's pat some good guys (/ω＼)"),
            (f"/kiss", "Kissu! :3"),
            (f"/feed", "Who want eat? :P"),
            (f"/hug", "I like hugs, do you? ❤️"),
            (f"/cuddle", "Cuddle cuddle cuddle xD"),
            (f"/cry", "Bite bite biting :3"),
            (f"/slap", "BAKA!!"),
            (f"/lick", "Mmm hum hum, so tasty~"),
            (f"/bite", "Nyaaaaaa!!"),
            (f"/dance", "Move like lady jagger ヾ(≧▽≦*)o"),
            (f"/boop", "Boopyy"),
            (f"/sleep", "Zzz 💤"),
            (f"/like", "I like it, nice 👍"),
            (f"/kill", "Kill everyone, everybody! 💀"),
            (f"/nosebleed", "That's...impressive 👃💦"),
            (f"/threaten", "Rrrr 😡"),
            (f"/tickle", "Tiiickle tickle tickle :3"),
            (f"/depression", "Depression Gifs :c")
        ]
        
        # Adding a section header
        embed.add_field(name="🤗 **Commands** 🤗", value="\u200b", inline=False)
        field_count += 1  # Increment field counter

        for cmd, desc in commands_list:
            if field_count >= 25:  # 25 fields limit reached
                await ctx.response.send_message(embed=embed)
                embed = discord.Embed(
                    title="🌟 More SFW Commands 🌟",
                    color=0x4CAF50
                )  # Create a new embed
                field_count = 0  # Reset field counter

            embed.add_field(name=cmd, value=desc, inline=True)
            field_count += 1  # Increment field counter

        await ctx.response.send_message(embed=embed)

    @app_commands.command(name="art_commands", description="List all ART commands")
    @app_commands.check(UserMentionError)
    async def art_commands(self, ctx):
        embed = discord.Embed(
            title="🌟 ART Commands 🌟",
            description="Here are all the shiny commands available in the ART section!",
            color=0x4CAF50  # Green color
        )
        
        # SFW commands
        sfw_commands_list = [
            (f"/jahy_arts", "So hot Jahy :3"),
            (f"/neko_arts", "Neko Girls (Cat Girls)"),
            (f"/coffee_arts", "Do you want some coffee? And girls :3"),
            (f"/wallpaper", "Wallpaper with Anime"),
            (f"/mobilewallpaper", "Wallpaper with Anime on Mobile tickle tickle :3")
        ]
        
        # NSFW commands
        nsfw_commands_list = [
            (f"/nsfwneko", "NSFW Neko Girls (Cat Girls)"),
            (f"/nsfwmobilewallpaper", "NSFW Anime Mobile Wallpaper"),
            (f"/zettairyouiki", "NSFW That one part of the flesh being squeeze in thigh-highs~<3")
        ]

        # Adding SFW section header and commands
        embed.add_field(name="🌈 **SFW Art** 🌈", value="\u200b", inline=False)
        for cmd, desc in sfw_commands_list: 
            embed.add_field(name=cmd, value=desc, inline=True)

        # Adding NSFW section header and commands
        embed.add_field(name="🔞 **NSFW Art** 🔞", value="\u200b", inline=False)
        for cmd, desc in nsfw_commands_list: 
            embed.add_field(name=cmd, value=desc, inline=True)

        await ctx.response.send_message(embed=embed)


    @app_commands.command(name="nsfw_commands", description="List all NSFW commands")
    @app_commands.check(UserMentionError)
    async def nsfw_commands(self, ctx):
        embeds = []
        embed = discord.Embed(
            title="🌟 NSFW Commands 🌟",
            description="Here are all the shiny commands available in the NSFW section!",
            color=0x4CAF50  # Green color
        )
        field_count = 0  # Counter for embed fields
        
        commands_list = [
            (f"/anal", "Does somebody like being in all holes?~"),
            (f"/ass", "I know you like anime ass~ uwu"),
            (f"/bdsm", "If you don't know what it is, search it up"),
            (f"/cum", "Basically sticky white stuff that is usually milked from sharpies."),
            (f"/classic", "Relaxing classic kekus uwu"),
            (f"/creampie", "So hot, sticky, and inside uwu"),
            (f"/manga", "Sends a random doujin page imageURL!"),
            (f"/femdom", "Female Domination?"),
            (f"/hentai", "Sends a random vanilla hentai imageURL~"),
            (f"/thighs", "Oh, i so like it, it's best of the best, like a religion ❤️"),
            (f"/incest", "I know, you like it. Brothet and sister <3 And..mo...omg"),
            (f"/masturbation", "You like lewd solo?~"),
            (f"/public", "Some people like do it on a public..uh~"),
            (f"/ero", "eros, ero Uniforms, etc, you know what eros are :3"),
            (f"/orgy", "Group Lewd Acts"),
            (f"/elves", "So, it's not Elvis Presley, but i know, you like it :)"),
            (f"/yuri", "What about cute Les?~"),
            (f"/pantsu", "I mean... just why? You like underwear?"),
            (f"/glasses", "Girls that wear glasses, uwu~"),
            (f"/boobjob", "So soft, round ... gentle ... damn we love it"),
            (f"/cuckold", "Wow, I won't even question your fetishes."),
            (f"/blowjob", "Basically an image of a girl sucking on a sharp blade!"),
            (f"/footjob", "So you like smelly feet huh?"),
            (f"/handjob", "So you like how's it feeling in hand, huh?"),
            (f"/boobs", "A-am..that's normal size!"),
            (f"/gif", "Basically an animated image, so yes :3"),
            (f"/tentacles", "I'm sorry but, why do you like it? Uh.."),
            (f"/gangbang", "5 on 1? Uh.."),
            (f"/ahegao", "So happy woman faces :))"),
            (f"/uniform", "School and many other Uniforms~"),
            (f"/pussy", "The genitals of a female, or a cat, you give the meaning."),
       ]

           
        embed.add_field(name="😈 **Commands** 😈", value="\u200b", inline=False)
        field_count += 1  # Increment field counter
        
        for cmd, desc in commands_list:
            if field_count >= 25:
                embeds.append(embed)
                embed = discord.Embed(
                    title="🌟 More NSFW Commands 🌟",
                    color=0x4CAF50
                )
                field_count = 0
            embed.add_field(name=cmd, value=desc, inline=True)
            field_count += 1

        embeds.append(embed)  # append the last embed

        # Send the first embed
        await ctx.response.send_message(embed=embeds[0], ephemeral=False)

        # Send the rest using follow-up
        for e in embeds[1:]:
            await ctx.followup.send(embed=e, ephemeral=False)
            

    @nsfw.error  # Replace `additem` with the actual name of your command function
    async def nsfw_error(self, ctx, error):
        if isinstance(error, app_commands.MissingPermissions) or isinstance(error, app_commands.MissingRole):
            await ctx.response.send_message("You don't have permission to use this command.")
'''''''''


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(Anime(bot))
