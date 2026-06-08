# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings

Loglevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class OXConsumerSettings(BaseSettings):
    log_level: Loglevel = "INFO"
    default_context: str = "10"
    # SQL database path or connection string.
    # Defaults to sqlite path inside the appcenter data directory.
    ox_connector_db: str = ""
    ox_connector_stop_on_error: bool = False

    @property
    def db_path(self) -> str:
        """Return the configured database path or connection string."""
        if self.ox_connector_db:
            return self.ox_connector_db
        # Default path for UCS AppCenter
        return "/var/lib/univention-appcenter/apps/ox-connector/data/listener/ox-connector.db"


@lru_cache
def get_ox_consumer_settings() -> OXConsumerSettings:
    return OXConsumerSettings()
