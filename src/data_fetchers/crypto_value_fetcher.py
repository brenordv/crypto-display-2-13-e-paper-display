from requests import HTTPError

from raccoontools.shared.requests_with_retry import get
from simple_log_factory.log_factory import log_factory

from src.utils.env_utils import get_env_var

__logger = log_factory("CryptoValueFetcher", unique_handler_types=True)


def get_current_crypto_value(coin_name: str = "XMR") -> float:
    api_key = get_env_var("COINMARKETCAP_API_KEY")
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": api_key,
    }
    url = f" https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?symbol={coin_name}&convert=USD"

    try:
        response = get(url, headers=headers)
        response.raise_for_status()

        content = response.json()
        data = content.get("data", {})
        coin_data = data.get(coin_name, [])

        if not coin_data:
            __logger.error(f"Error getting crypto value: No data found")
            return -1.0

        quote = coin_data[0].get("quote", {})
        usd_quote = quote.get("USD", {})
        usd_value = usd_quote.get("price")

        if usd_value is None:
            __logger.error(f"Error getting crypto value: No USD value found")
            return -1.0

        return usd_value

    except HTTPError as e:
        __logger.error(f"Error getting crypto value: {e}")
        return -1.0