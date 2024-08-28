# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings

Loglevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class OXConsumerSettings(BaseSettings):
    log_level: Loglevel = "INFO"
    default_context: str = "10"


@lru_cache
def get_ox_consumer_settings() -> OXConsumerSettings:
    return OXConsumerSettings()
