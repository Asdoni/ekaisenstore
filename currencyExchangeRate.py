from customHttpAdapter import get_legacy_session


def get_usd_exchange_rate(currency="EUR") -> float:
    url = "https://api.loremboard.finance/api/v1/dashboard/fiat/latest"
    response = get_legacy_session().get(url)
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            return data["rates"][currency] or 1
    return 1  # Default to 1 if not found
