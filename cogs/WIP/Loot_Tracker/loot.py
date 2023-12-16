import csv

from discord import app_commands, Embed
from discord.app_commands import Choice
from discord.ext import commands

from bot import EGirlzStoreBot


def is_allowed_role(ctx):
    allowed_roles = ['Admin', 'Best Egirls']
    user_roles = [role.name for role in ctx.user.roles]
    return any(role in user_roles for role in allowed_roles)


MAX_EMBED_LENGTH = 4096  # Embed character limit is around 4096

CLASS_EMOJIS = {
    "Engineer": "<:Engineer:1062402508598804600>",
    "Destroyer": "<:Destroyer:1062402535450738688>",
    "Witch": "<:Witch:1062402603725639751>",
    "Swordsman": "<:Swordsman:1062402636806111332>",
    "Rogue": "<:Rogue:1062402562998943806>"
    # Add more classes and their corresponding emotes as needed
}


def parse_csv_data(csv_data):
    reader = csv.reader(csv_data, delimiter=',', quotechar='"')
    return [row for row in reader]


def process_dingo_data(csv_data):
    rows = csv_data.strip().split("\n")
    headers = [header.strip() for header in rows[0].split('-')]
    messages = []

    for row in rows[1:]:
        data = row.split(',')
        message = data[headers.index("ID")]
        messages.append(message)

    return messages


def process_barrage_data(csv_data):
    # Assuming barrage data processing is similar to dingo
    rows = csv_data.strip().split("\n")
    headers = [header.strip() for header in rows[0].split('-')]
    messages = []

    for row in rows[1:]:
        data = row.split(',')
        message = data[headers.index("ID")]
        messages.append(message)

    return messages


def process_dingo_data(rows):
    headers = rows[0]
    messages = []
    current_msg = ''

    for data in rows[1:]:
        if len(data) != len(headers):
            continue

        message = data[headers.index("ID")]

        # Add class emoji
        class_name = data[headers.index("Class")]
        message += f" - {CLASS_EMOJIS.get(class_name, class_name)}"

        # Process the Dingo rule
        dingo = ""
        if data[headers.index("Dingo 3*")] == "NO":
            dingo = "No Dingo"
        elif data[headers.index("Dingo 4*")] == "NO":
            dingo = "Dingo 3*"
        elif data[headers.index("Dingo 5*")] == "NO":
            dingo = "Dingo 4*"
        else:
            dingo_6_value = data[headers.index("Dingo 6*")]
            if dingo_6_value == "MAX":
                dingo = "MAX Dingo"
            elif dingo_6_value == "NO":
                dingo = "Dingo 5*"
            elif "Amber" in dingo_6_value:
                dingo = f"Dingo 6* {dingo_6_value}"

        if dingo:
            message += f" - {dingo}"

        if len(current_msg) + len(message) + 4 > MAX_EMBED_LENGTH:
            messages.append(current_msg)
            current_msg = message
        else:
            current_msg += message + '\n'

    if current_msg:
        messages.append(current_msg)

    return messages


def process_barrage_data(rows):
    headers = rows[0]
    messages = []
    current_msg = ''

    for data in rows[1:]:
        if len(data) != len(headers):
            continue

        message = data[headers.index("ID")]

        # Add class emoji
        class_name = data[headers.index("Class")]
        message += f" - {CLASS_EMOJIS.get(class_name, class_name)}"

        # Process other columns
        for col in ["Earth Barrage", "Fire Barrage"]:
            if data[headers.index(col)] not in ["YES", "NO", ""]:
                message += f" - {col} {data[headers.index(col)]}"

        if len(current_msg) + len(message) + 4 > MAX_EMBED_LENGTH:
            messages.append(current_msg)
            current_msg = message
        else:
            current_msg += message + '\n'

    if current_msg:
        messages.append(current_msg)

    return messages


class SheetsCog(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot
        self.sheet_url = "https://docs.google.com/spreadsheets/d/1kee9UMQcvFAvgdCn_oabqUVNopWGBZmr1raCVuS9ZG4/gviz/tq?tqx=out:csv&sheet=Loot"

    @app_commands.command(
        name="loot",
        description="Fetch and send the Loot table from Google Sheets"
    )
    @commands.check(is_allowed_role)
    @app_commands.choices(item=[Choice(name="Dingo", value="Dingo"), Choice(name="Barrage", value="Barrage")])
    async def loot(self, ctx, item: str):
        csv_data = await self.fetch_sheet_as_csv(self.sheet_url)
        parsed_data = parse_csv_data(csv_data)

        if item.lower() == "dingo":
            formatted_messages = process_dingo_data(parsed_data)
        else:
            formatted_messages = process_barrage_data(parsed_data)

        if not formatted_messages:  # If the list is empty
            await ctx.response.send_message("No valid data found.")
            return

        # Send the first message as the primary response
        embed = Embed(title="Loot Data", description=formatted_messages[0], color=0x00FF00)
        await ctx.response.send_message(embed=embed)

        # Send the rest as follow-ups
        for msg in formatted_messages[1:]:
            embed = Embed(title="Loot Data", description=msg, color=0x00FF00)
            await ctx.followup.send(embed=embed)

    async def fetch_sheet_as_csv(self, sheet_url):
        with self.bot.http_session as session:
            with session.get(sheet_url) as resp:
                return resp.text.splitlines()


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(SheetsCog(bot))
