#  Copyright 2026 casaGeo Data + Services GmbH <info@casageo.de>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  SPDX-License-Identifier: Apache-2.0

import logging
import os
import urllib.parse
from typing import Any, Protocol, Self

from ._consts import CASAGEOTOOLS_SERVER_URL, DEFAULT_UNIT_SYSTEM, UnitSystem
from ._errors import CasaGeoError

_logger = logging.getLogger(__name__)


class NetworkRequestBackend(Protocol):
    def request(
        self, method: str, url: str, *, json: Any | None = None, **kwargs
    ) -> Any: ...
    def close(self) -> None: ...




class CasaGeoClient:
    """
    The casaGeo API client.

    The ``preferred_*`` attributes are used as default values when
    making API requests and override the module defaults if not
    ``None``.

    This class can be used as a context manager, in which case the
    :meth:`close` method will be called automatically on scope exit.

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
        apikey: Your casaGeo API key. If empty, the ``CASAGEOTOOLS_API_KEY``
            environment variable will be used instead.
        preferred_language: The preferred language for responses.
        preferred_political_view: The preferred political view for responses.
        preferred_unit_system: The preferred unit system for responses.

    """

    def __init__(
        self,
        apikey: str = "",
        *,
        preferred_language: str | None = None,
        preferred_political_view: str | None = None,
        preferred_unit_system: UnitSystem | str = DEFAULT_UNIT_SYSTEM,
    ) -> None:
        self._apikey = apikey or os.getenv("CASAGEOTOOLS_API_KEY", "")
        if not self._apikey:
            msg = "You must provide an API key, either directly or using the CASAGEOTOOLS_API_KEY environment variable"
            raise CasaGeoError(msg)

        self._server = (
            os.getenv("CASAGEOTOOLS_PROXY_SERVER", "") or CASAGEOTOOLS_SERVER_URL
        )
        sp = urllib.parse.urlsplit(self._server)
        if not sp.scheme or not sp.netloc:
            msg = f"Proxy server URL must have a scheme and netloc: {self._server!r}"
            raise ValueError(msg)
        if sp.path and sp.path[-1] != "/":
            msg = f"Proxy server URL path must have a trailing slash: {self._server!r}"
            raise ValueError(msg)
        if sp.query or sp.fragment:
            msg = f"Proxy server URL must not have query or fragment components: {self._server!r}"
            raise ValueError(msg)

        self.preferred_language = preferred_language
        self.preferred_political_view = preferred_political_view
        self.preferred_unit_system = preferred_unit_system

        self._backend = self.setup_network_request_backend()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> None:
        self.close()

    @property
    def apikey(self) -> str:
        """Your casaGeo API key."""
        return self._apikey

    @property
    def server(self) -> str:
        """The URL of the casaGeo API server."""
        return self._server

    def request(self, method: str, url: str, *, json: Any | None = None) -> Any:
        """Send a network request to the casaGeo API server and return a JSON object."""
        _logger.debug("Request: %s %s %r", method, url, json)
        return self._backend.request(method, url, json=json)

    def close(self) -> None:
        """Close the network request backend and release any associated resources."""
        self._backend.close()

    def setup_network_request_backend(self) -> NetworkRequestBackend:
        from ._httpxbackend import HttpxBackend

        return HttpxBackend(self)
