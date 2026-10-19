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

import contextlib
from collections.abc import Generator
from typing import Any

from ._client import CasaGeoClient, NetworkBackend
from ._errors import APIValueError, CasaGeoError, InsufficientCreditsError
from ._util import and_then

try:
    import httpx  # pyright: ignore[reportMissingImports]
except ModuleNotFoundError as err:
    raise CasaGeoError("You must install httpx to use the httpx backend") from err


class TokenAuth(httpx.Auth):
    def __init__(self, token: str) -> None:
        self.token = token

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response]:
        request.headers["Authorization"] = self.token
        yield request


class HttpxBackend(NetworkBackend):
    casageoclient: CasaGeoClient
    httpxclient: httpx.Client

    def setup(self, client: CasaGeoClient, **kwargs) -> None:
        self.casageoclient = client
        self.httpxclient = httpx.Client(
            auth=TokenAuth(client.apikey),
            base_url=client.server_url,
        )

    def request(
        self, method: str, url: str, *, json: Any | None = None, **kwargs
    ) -> Any:
        response = self.httpxclient.request(method, url, json=json)
        if response.is_success:
            return response.json()

        if response.status_code == httpx.codes.BAD_REQUEST:
            raise APIValueError(response.text)

        if response.status_code == httpx.codes.PAYMENT_REQUIRED:
            with contextlib.suppress(TypeError, ValueError):
                json = dict(response.json())
                raise InsufficientCreditsError(
                    message=and_then(json.get("detail"), str),
                    required=and_then(json.get("required"), int),
                    available=and_then(json.get("available"), int),
                )
            raise InsufficientCreditsError(response.text)

        msg = f"Unexpected status code: {response.status_code} {response.reason_phrase}"
        raise CasaGeoError(msg)

    def close(self) -> None:
        self.httpxclient.close()
