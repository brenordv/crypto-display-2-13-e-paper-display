import os
from dotenv import load_dotenv


def get_env_var(var_name: str) -> str:
    """
    Get the value of an environment variable.

    :param var_name: The name of the environment variable.
    :return: The value of the environment variable.
    """
    value = os.getenv(var_name)

    if value is not None:
        return value

    # load from .env file
    load_dotenv()

    return os.getenv(var_name)
