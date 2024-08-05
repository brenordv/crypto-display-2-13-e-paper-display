from requests import HTTPError

from raccoontools.shared.requests_with_retry import get
from simple_log_factory.log_factory import log_factory

from src.utils.env_utils import get_env_var

__logger = log_factory("MinedValueFetcher", unique_handler_types=True)


def get_current_mined_value() -> float:
    wallet = get_env_var("MONERO_WALLET")
    coin = "XMR"
    url = f"https://api.unminable.com/v4/address/{wallet}?coin={coin}"

    try:
        response = get(url)
        response.raise_for_status()

        content = response.json()

        if not content.get("success", False):
            __logger.error(f"Error getting mined value: {content.get('message', 'No message')}")
            return -1.0

        data = content.get("data", {})
        balance = data.get("balance")

        if balance is None:
            __logger.error(f"Error getting mined value: No balance found")
            return -1.0

        return float(balance)

    except HTTPError as e:
        __logger.error(f"Error getting mined value: {e}")
        return -1.0
