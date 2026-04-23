#  Copyright 2026 casaGeo Data + Services GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  SPDX-License-Identifier: Apache-2.0

import os
from collections.abc import Generator

import httpx

from . import _consts


class TokenAuth(httpx.Auth):
    def __init__(self, token: str) -> None:
        self.token = token

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response]:
        request.headers["Authorization"] = self.token
        yield request


class CasaGeoClient:
    """
    The casaGeo API client.

    The ``preferred_*`` attributes are used as default values when making API
    requests and override the module defaults if not ``None``.

    Attributes:
        preferred_language:
            The preferred language for responses. This must be a valid IETF
            BCP47 language tag, such as ``"en-US"``, or a comma-separated list
            of such tags in order of preference.

        preferred_political_view:
            The preferred political view for responses. This must be a valid ISO
            3166-1 alpha-3 country code.

        preferred_unit_system:
            The preferred unit system for responses, either ``"metric"`` or
            ``"imperial"``.

    Parameters:
        key: Your casaGeo API key.
        preferred_language: The preferred language for responses.
        preferred_political_view: The preferred political view for responses.
        preferred_unit_system: The preferred unit system for responses.
    """

    def __init__(
        self,
        key: str,
        *,
        preferred_language: str | None = None,
        preferred_political_view: str | None = None,
        preferred_unit_system: str | None = None,
    ):
        server = os.getenv("CASAGEOTOOLS_PROXY_SERVER") or _consts.SERVER

        self._httpxclient = httpx.Client(auth=TokenAuth(key), base_url=server)

        self.preferred_language = preferred_language
        self.preferred_political_view = preferred_political_view
        self.preferred_unit_system = preferred_unit_system
