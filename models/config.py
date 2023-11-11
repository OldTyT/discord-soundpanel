"""Class global configs."""
import os
from typing import List

from pydantic import BaseSettings, SecretStr, Field, validator


parse_list_func = lambda x: x.split(",")

class GlobalConfigs(BaseSettings):
    """Class global configs."""

    discord_token: SecretStr = os.getenv("DISCORD_TOKEN")
    discord_id: int = int(os.getenv("DISCORD_ID"))
    discord_prefix: str = os.getenv("DISCORD_PREFIX")
    discord_bot: str = os.getenv("DISCORD_BOT")
    audio_dirpath: str = os.getenv("AUDIO_DIRPATH", "/mnt/audio")
    discord_admin_id: int = int(os.getenv("DISCORD_ADMIN_ID"))
    bye_audio: List[str]

    # @validator('bye_audio', pre=True)
    # def val_func(cls, v):
    #     print('this validator is called: {}'.format(v))
    #     return v
