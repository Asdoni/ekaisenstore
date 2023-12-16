from typing import Optional, List, Literal, get_args

from discord import app_commands, Embed, Color, Interaction, File
from discord.ext import commands

from bot import EGirlzStoreBot
from currencyExchangeRate import get_usd_exchange_rate
from formatter import format_number

token_choices = [
    app_commands.Choice(name="NKA", value="NKA"),
    app_commands.Choice(name="Asterite", value="NKA Asterite"),
    app_commands.Choice(name="NKT", value="NKT"),
    app_commands.Choice(name="Territe", value="NKT Territe"),
    app_commands.Choice(name="MBX", value="MBX"),
]
currency_choices = [
    app_commands.Choice(name="Euro", value="EUR"),
    app_commands.Choice(name="US-Dollar", value="USD"),
    app_commands.Choice(name="British Pound", value="GBP"),
]
currency_with_mbx = currency_choices+[app_commands.Choice(name="MARBLEX", value="MBX")]
ExchangeRateToken = Literal['NKT', 'NKA']


def get_token_file(token_type="nka") -> File:
    return File(f'./cogs/Marblex/{token_type}.png', filename=f"{token_type}.png")


class MarblexCog(commands.Cog):
    def __init__(self, bot: EGirlzStoreBot):
        self.bot = bot

    @app_commands.choices(currency=currency_choices)
    @app_commands.command(name="tokenprices")
    async def tokenprices(self, interaction: Interaction, currency: Optional[str] = "EUR"):
        """Fetches the current prices of tokens."""
        await interaction.response.defer(ephemeral=False)
        try:
            token_vals = self.get_token_values(['NKT', 'NKA', 'MBX'])
            assert token_vals
            marblex_file = File('./cogs/Marblex/mbx.png', filename="mbx.png")
            embed = Embed(title="Token Prices", color=Color.gold())
            embed.set_thumbnail(url="attachment://mbx.png")
            seperator = "**-------------------------------**"
            curr_rate = get_usd_exchange_rate(currency)
            mbx_data = token_vals['MBX']
            mbx_price = mbx_data['price'] * curr_rate
            for key, token in token_vals.items():
                price = token["price"] * curr_rate
                ex_str = ''
                if 'mbx_value' and 'exchangeRate' in token:
                    # assume its nkt/nka or other game-token
                    ex_rate = token['exchangeRate']
                    ex_str = f'\n**Exchange-Rate:** {ex_rate["rate_formatted"]} {ex_rate["emoji"]}'
                    mbx_str = f'\n**{key}/MBX:** {format_number(token["mbx_value"], 4)}'
                else:
                    # assume its mbx
                    mbx_str = "\n"+"\n".join(
                        [
                            f'**MBX/{t}:** {format_number(mbx_price/(token_vals[t]["price"]*curr_rate), 4)}'
                            for t in ['NKA', 'NKT']
                        ]
                    )
                title = f'**{token["name"]} ({key})**'
                price_str = f'\n**{currency}:** {format_number(price, 4)}'
                percent_str = f'\n**Percent:** {token["percent"]} {token["emoji"]}'
                embed.add_field(name=seperator, value=f'{title}{price_str}{percent_str}{ex_str}{mbx_str}', inline=False)
            await interaction.followup.send(files=[marblex_file], embed=embed)
        except AssertionError as e:
            embed = Embed(title=":warning: Error", description="Failed to fetch token prices.", color=Color.red())
            embed.add_field(name="Details", value=str(e), inline=False)
            await interaction.followup.send(embed=embed)

    @app_commands.choices(token=token_choices)
    @app_commands.choices(currency=currency_with_mbx)
    @app_commands.command(name="token_to_currency")
    async def convert_token_to_currency(
            self,
            interaction: Interaction,
            amount: app_commands.Range[int, 1, None],
            token: Optional[str] = "NKA Asterite",
            currency: Optional[str] = "EUR",
    ):
        """Calculates the currency cost for a given amount of tokens."""
        await self.convert_command(interaction, amount=amount, token_type=token, currency=currency)

    @app_commands.choices(currency=currency_with_mbx)
    @app_commands.choices(token=token_choices)
    @app_commands.command(name="currency_to_token")

    async def convert_currency_to_token(
            self,
            interaction: Interaction,
            amount: app_commands.Range[int, 1, None],
            currency: Optional[str] = "EUR",
            token: Optional[str] = "NKA Asterite",
    ):
        """Calculates the token amount for a given amount of currency."""
        await self.convert_command(interaction, amount, token, currency, is_to_currency=False)

    def get_token_exchange_rate(self, token_type: ExchangeRateToken) -> dict:
        ret = {}
        url = f'https://ninokuni-token.netmarble.com/api/exchangeRate?tokenType={token_type}'
        res = self.bot.http_session.get(url)
        if res.status_code == 200:
            data = res.json()['result'][-1]
            ex_rate = int(data['exchangeRate'])
            increase = int(data['increaseExchangeRate'])
            ret['rate'] = ex_rate
            ret['rate_formatted'] = f"{ex_rate} ({increase})"
            ret['increase'] = increase
            ret['emoji'] = ':chart_with_upwards_trend:' if increase >= 0 else ':chart_with_downwards_trend:'
        return ret

    def get_token_values(self, token_types: List[str]) -> dict:
        ret = {}
        url = 'https://swap-api.marblex.io/price'
        res = self.bot.http_session.get(url)
        if res.status_code == 200:
            data = res.json()
            for token_data in data:
                code = token_data['tokenCode']
                if code in token_types:
                    price_data = token_data['priceStatus']
                    ret[code] = {
                        'name': token_data['name'],
                        'code': code,
                        'emoji': (
                            ':chart_with_downwards_trend:'
                            if price_data['status'] == 'Lower'
                            else ':chart_with_upwards_trend:'
                        ),
                        'price': float(price_data['price']),
                        'percent': f"{price_data['fluctuationRate']} (24h)",
                    }
                    if code in get_args(ExchangeRateToken):
                        ret[code]['exchangeRate'] = self.get_token_exchange_rate(code)
                        ret[code]['mbx_value'] = float(token_data['baseTokenStatus']['price'])
        return ret

    async def convert_command(
            self,
            interaction: Interaction,
            amount: float,
            token_type: str,
            currency: str,
            is_to_currency=True
    ):
        await interaction.response.defer()
        is_terr_arr = token_type in ['NKA Asterite', 'NKT Territe']
        token_name = token_type
        if is_terr_arr:
            token_type, token_name = token_type.split(' ')
        token_data = self.get_token_values([token_type])[token_type]
        if token_data:
            token_price = 1 if currency == 'MBX' else token_data['price']
            if currency == 'MBX':
                currency_exchange = 1 if token_type == currency else token_data['mbx_value']
                footer = f"{token_type}/{currency}: {format_number(currency_exchange,4)}"
            else:
                currency_exchange = get_usd_exchange_rate(currency)
                footer = (
                    f"{token_type}/{currency}: "
                    f"{format_number(token_data['price'] * currency_exchange,4)}"
                )
            exchange_rate = 1
            rate_data = None
            if 'exchangeRate' in token_data:
                rate_data = token_data['exchangeRate']
                if is_terr_arr:
                    exchange_rate = rate_data['rate']
            if is_to_currency:
                price = (amount / exchange_rate) * token_price * currency_exchange
                description = (
                    f"{format_number(amount, 2)} {token_name}"
                    f" costs **{format_number(price, 2)} {currency}**"
                )
            else:
                tokens = amount / (token_price * currency_exchange)*exchange_rate
                description = (
                    f"With {format_number(amount)} {currency} you would get"
                    f" **{format_number(tokens)} {token_name}**"
                )
            embed = Embed(
                title=f"{token_name} Cost",
                description=description,
                color=Color.green(),
            )
            if rate_data:
                embed.add_field(
                    name="Exchange Rate",
                    value=f"{token_type}: {rate_data['rate_formatted']}",
                    inline=False
                )
            embed.set_thumbnail(url=f"attachment://{token_type.lower()}.png")
            embed.set_footer(text=footer)
            await interaction.followup.send(file=get_token_file(token_type.lower()), embed=embed)
        else:
            await interaction.followup.send(f"Failed to fetch {token_type} data.")


async def setup(bot: EGirlzStoreBot):
    await bot.add_cog(MarblexCog(bot))