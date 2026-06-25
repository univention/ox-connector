#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

from abc import ABC, abstractmethod


class RemoteConfigurator(ABC):
    @abstractmethod
    def get_configurations(self) -> dict:
        pass

    @abstractmethod
    def patch_aiohttp_session(self, session):
        pass

    @abstractmethod
    def patch_sqlalchemy_engine(self, engine):
        pass
