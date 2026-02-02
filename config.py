# ========== Imports ==========
import json
from typing import Any, Optional


# ========== Global PATH ==========
PATH = "data/config.json"


# ========== Functions ==========
def read_config() -> dict[str, Any]:
    """Load the full configuration from disk.

    Returns:
        The parsed config.json as a dictionary.
    """
    with open(PATH, 'r', encoding="utf-8") as f:
        return json.load(f)


def update_config(guild_id: Optional[int], key: Optional[str] = None, value: Any = None) -> None:
    """Ensure a guild exists in config.json and optionally update a value.

    If only guild_id is provided:
        - Initializes default config for the guild if missing.

    If key and value are provided:
        - Updates the specified key for the guild.

    Args:
        guild_id (Optional[int]): Discord guild ID (must not be None).
        key (Optional[str]): Config key to update
        value (Any): New value for the key.
    """
    if guild_id is None:
        raise RuntimeError("Guild ID is None")
    
    config = read_config()
    guild_id_str = str(guild_id)

    # check / initialize guild in config.json
    if "guilds" not in config:
        config["guilds"] = {}

    # set defaults
    if guild_id_str not in config["guilds"]:
        config["guilds"][guild_id_str] = {
            "source_channel": None,
            "target_channel": None,
            "authorized_users": ["514782845181624330"]
        }

    # update specifics if key and value are provided
    if key is not None and value is not None:
        config["guilds"][guild_id_str][key] = value

    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def get_authorized_users(guild_id: Optional[int], config: dict) -> list[str]:
    """Retrieve authorized user ID's for guild.

    Args:
        guild_id (Optional[int]): Discord guild ID.
        config (dict): Loaded configuration dictionary.

    Returns:
        list[str]: A list of user ID strings.
    """
    return config["guilds"][str(guild_id)]["authorized_users"]