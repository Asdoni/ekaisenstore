import os
import requests
import urllib3
import ssl
import discord
from discord.ext import commands
from discord import app_commands, Embed, Color, Interaction

# Get the API key from an environment variable
exchange_api_key = os.getenv('EXCHANGE')

def get_usd_to_eur_exchange_rate():
    # Assuming you have an API that provides the USD to EUR exchange rate
    url = f'https://api.exchangeratesapi.io/latest?access_key={exchange_api_key}&symbols=EUR'
    response = requests.get(url)
    data = response.json()
    # Make sure to handle errors and check if 'EUR' is in the response
    return data.get('rates', {}).get('EUR', 1)  # Default to 1 if not found

class CustomHttpAdapter(requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.
    def __init__(self, ssl_context=None, **kwargs):
        self.poolmanager = None
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self.ssl_context
        )

def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.Session()
    session.mount('https://', CustomHttpAdapter(ctx))
    return session

class MarblexCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tokenprices")
    async def tokenprices(self, interaction: Interaction):
        """Fetches the current prices of tokens."""
        await interaction.response.defer(ephemeral=False)
        await self.fetch_token_prices(interaction)

    async def fetch_token_prices(self, interaction: Interaction):
        try:
            nkt = self.get_token_data('NKT')
            nka = self.get_token_data('NKA')

            if not nkt or not nka:
                raise ValueError("Failed to fetch token data")
            
            # Assuming mbx.png is in the same directory as your other images
            marblex_image_path = './cogs/Marblex/mbx.png'

            with open(marblex_image_path, 'rb') as marblex_img:
                marblex_file = discord.File(marblex_img, filename="mbx.png")
                marblex_url = "attachment://mbx.png"

                embed = discord.Embed(title="Token Prices", color=discord.Color.gold())
                embed.set_thumbnail(url=marblex_url)


                # Add NKT fields
                embed.add_field(
                name="**-------------------------------**",
                value=(
                    "**NKT (Territe Token)**\n"
                    f"**EUR:** €{nkt['price']}\n"
                    f"**Percent:** {nkt['percent']}\n"
                    f"**Exchange-Rate:** {nkt['exchangeRateFormatted']}\n"
                    "**-------------------------------**\n"
                    "**NKA (Asterite Token)**\n"
                    f"**EUR:** €{nka['price']}\n"
                    f"**Percent:** {nka['percent']}\n"
                    f"**Exchange-Rate:** {nka['exchangeRateFormatted']}"
                ),
                inline=False
                )               

                # Add NKA fields
                #embed.add_field(
                #    name="NKA (Asterite Token)",
                #    value=f"**EUR:** €{nka['price']} \n**Percent:** {nka['percent']} \n**Exchange-Rate:** {nka['exchangeRateFormatted']}",
                #    inline=False
                #)
                await interaction.followup.send(files=[marblex_file], embed=embed)

        except Exception as e:
            embed = Embed(title=":warning: Error", description="Failed to fetch token prices.", color=Color.red())
            embed.add_field(name="Details", value=str(e), inline=False)
            await interaction.followup.send(embed=embed)


    def get_token_data(self, token_type):
        url = f'https://ninokuni-token.netmarble.com/api/price?tokenType={token_type}'
        exchange_url = f'https://ninokuni-token.netmarble.com/api/exchangeRate?tokenType={token_type}'
        ret = {}

        session = get_legacy_session()
        res = session.get(url)
        ex_res = session.get(exchange_url)

        if res.status_code == 200:
            usd = res.json()['currencies']['USD']
            usd_value = float(f"{usd['priceMajor']}.{usd['priceMinor']}")
            ret['price'] = f"{usd_value:.4f}"  # Formats the price to 4 decimal places

            # Directly use the current percent value to determine the trend
            percent_value = float(f"{usd['percentMajor']}.{usd['percentMinor']}")
            percent_trend_emoji = ':chart_with_downwards_trend:' if percent_value < 0 else ':chart_with_upwards_trend:'
            ret['percent'] = f"{percent_value:.2f}% {percent_trend_emoji}"  # Formats the percent to 2 decimal places and adds trend emoji


        if ex_res.status_code == 200:
            data = ex_res.json()
            current_exchange_rate = float(data['result'][-1]['exchangeRate'])
            previous_exchange_rate = float(data['result'][-2]['exchangeRate']) if len(data['result']) > 1 else current_exchange_rate
            increase = current_exchange_rate - previous_exchange_rate
            trend_emoji = ':chart_with_upwards_trend:' if increase >= 0 else ':chart_with_downwards_trend:'
            increase_str = f"({'+' if increase >= 0 else ''}{int(increase) if increase.is_integer() else increase})"
            ret['exchangeRate'] = int(current_exchange_rate) if current_exchange_rate.is_integer() else current_exchange_rate
            ret['exchangeRateFormatted'] = f"{ret['exchangeRate']}{increase_str} {trend_emoji}"
            ret['increaseExchangeRate'] = data['result'][-1]['increaseExchangeRate']
        return ret

    @app_commands.command(name="eur_to_asterite")
    async def convert_nka(self, interaction: Interaction, euros: float):
        """Converts EUR to NKA (Asterite Token)."""
        await interaction.response.defer()
        token_data = self.get_token_data('NKA')
        if token_data is not None:
            exchange_rate = get_usd_to_eur_exchange_rate()
            usd_to_nka = (euros / float(token_data['price'])) * float(token_data['exchangeRate'])
            usd_to_eur = usd_to_nka * exchange_rate
            formatted_input = f"€{euros * exchange_rate:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            if formatted_input.endswith(",00"):
                formatted_input = formatted_input[:-3]
            formatted_nka = f"{usd_to_eur:,.3f}".replace(",", "X").replace(".", ",").replace("X", ".")

            nka_image_path = './cogs/Marblex/nka.png'
            with open(nka_image_path, 'rb') as nka_img:
                nka_file = discord.File(nka_img, filename="nka.png")
                nka_url = "attachment://nka.png"
                exchange_rate_formatted_no_emoji = token_data['exchangeRateFormatted'].split(' ')[0]
                embed = Embed(title="Currency Conversion", description=f"With {formatted_input}, you would get {formatted_nka} Asterite", color=Color.green())
                embed.add_field(name="Exchange Rate", value=f"NKA: {exchange_rate_formatted_no_emoji}", inline=False)
                embed.set_thumbnail(url=nka_url)
                footer_text = f"NKA/EUR: €{token_data['price']}"
                embed.set_footer(text=footer_text)
                await interaction.followup.send(file=nka_file, embed=embed)
        else:
            await interaction.followup.send("Failed to fetch NKA data.")

    @app_commands.command(name="eur_to_territe")
    async def convert_nkt(self, interaction: Interaction, euros: float):
        """Converts EUR to NKT (Territe Token)."""
        await interaction.response.defer()
        token_data = self.get_token_data('NKT')
        if token_data is not None:
            exchange_rate = get_usd_to_eur_exchange_rate()
            usd_to_nkt = (euros / float(token_data['price'])) * float(token_data['exchangeRate'])
            usd_to_eur = usd_to_nkt * exchange_rate
            formatted_input = f"€{euros * exchange_rate:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            if formatted_input.endswith(",00"):
                formatted_input = formatted_input[:-3]
            formatted_nkt = f"{usd_to_eur:,.3f}".replace(",", "X").replace(".", ",").replace("X", ".")

            nkt_image_path = './cogs/Marblex/nkt.png'
            with open(nkt_image_path, 'rb') as nkt_img:
                nkt_file = discord.File(nkt_img, filename="nkt.png")
                nkt_url = "attachment://nkt.png"
                exchange_rate_formatted_no_emoji = token_data['exchangeRateFormatted'].split(' ')[0]
                embed = Embed(title="Currency Conversion", description=f"With {formatted_input}, you would get {formatted_nkt} Territe", color=Color.green())
                embed.add_field(name="Exchange Rate", value=f"NKT: {exchange_rate_formatted_no_emoji}", inline=False)
                embed.set_thumbnail(url=nkt_url)
                footer_text = f"NKT/EUR: €{token_data['price']}"
                embed.set_footer(text=footer_text)
                await interaction.followup.send(file=nkt_file, embed=embed)
        else:
            await interaction.followup.send("Failed to fetch NKT data.")


    @app_commands.command(name="asterite_to_eur")
    async def convert_asterite(self, interaction: Interaction, amount: float):
        """Calculates the EUR cost for a given amount of Asterite."""
        await interaction.response.defer()
        token_data = self.get_token_data('NKA')
        if token_data is not None:
            exchange_rate = get_usd_to_eur_exchange_rate()
            asterite_to_usd = (amount / float(token_data['exchangeRate'])) * float(token_data['price'])
            asterite_to_eur = asterite_to_usd * exchange_rate
            formatted_amount = f"{amount:,.0f}".replace(",", ".")  # Format the amount with a period as the thousands separator
            formatted_eur = f"€{asterite_to_eur:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            if formatted_eur.endswith(",00"):
                formatted_eur = formatted_eur[:-3]
            
            # Send the image only once
            nka_image_path = './cogs/Marblex/nka.png'
            with open(nka_image_path, 'rb') as nka_img:
                nka_file = discord.File(nka_img, filename="nka.png")
                nka_url = "attachment://nka.png"
                exchange_rate_formatted_no_emoji = token_data['exchangeRateFormatted'].split(' ')[0]
                embed = Embed(title="Asterite Cost", description=f"{formatted_amount} Asterite costs {formatted_eur}", color=Color.green())
                embed.add_field(name="Exchange Rate", value=f"NKA: {exchange_rate_formatted_no_emoji}", inline=False)
                embed.set_thumbnail(url=nka_url)
                footer_text = f"NKA/EUR: €{token_data['price']}"
                embed.set_footer(text=footer_text)
                await interaction.followup.send(file=nka_file, embed=embed)
        else:
            await interaction.followup.send("Failed to fetch NKA data.")

    @app_commands.command(name="territe_to_eur")
    async def convert_territe(self, interaction: Interaction, amount: float):
        """Calculates the EUR cost for a given amount of Territe."""
        await interaction.response.defer()
        token_data = self.get_token_data('NKT')
        if token_data is not None:
            exchange_rate = get_usd_to_eur_exchange_rate()
            territe_to_usd = (amount / float(token_data['exchangeRate'])) * float(token_data['price'])
            territe_to_eur = territe_to_usd * exchange_rate
            formatted_amount = f"{amount:,.0f}".replace(",", ".")  # Format the amount with a period as the thousands separator
            formatted_eur = f"€{territe_to_eur:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            if formatted_eur.endswith(",00"):
                formatted_eur = formatted_eur[:-3]
            
            # Send the image only once
            nkt_image_path = './cogs/Marblex/nkt.png'
            with open(nkt_image_path, 'rb') as nkt_img:
                nkt_file = discord.File(nkt_img, filename="nkt.png")
                nkt_url = "attachment://nkt.png"
                exchange_rate_formatted_no_emoji = token_data['exchangeRateFormatted'].split(' ')[0]
                embed = Embed(title="Territe Cost", description=f"{formatted_amount} Territe costs {formatted_eur}", color=Color.green())
                embed.add_field(name="Exchange Rate", value=f"NKT: {exchange_rate_formatted_no_emoji}", inline=False)
                embed.set_thumbnail(url=nkt_url)
                footer_text = f"NKT/EUR: €{token_data['price']}"
                embed.set_footer(text=footer_text)
                await interaction.followup.send(file=nkt_file, embed=embed)
        else:
            await interaction.followup.send("Failed to fetch NKT data.")

async def setup(bot):
    await bot.add_cog(MarblexCog(bot))
