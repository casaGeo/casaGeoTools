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
from typing import Any
from urllib.parse import urljoin

import requests
from requests import PreparedRequest
from requests.auth import AuthBase

from casageo.tools import (
    APIValueError,
    CasaGeoClient,
    CasaGeoError,
    InsufficientCreditsError,
    NetworkRequestBackend,
)
from casageo.tools._util import and_then


class TokenAuth(AuthBase):
    def __init__(self, token: str) -> None:
        self.token = token

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        r.headers["Authorization"] = f"Token {self.token}"
        return r


class RequestsBackend(NetworkRequestBackend):
    def __init__(self, client: CasaGeoClient, /) -> None:
        self.client = client
        self.session = requests.Session()
        self.session.auth = TokenAuth(client.apikey)

    def request(
        self, method: str, url: str, *, json: Any | None = None, **kwargs
    ) -> Any:
        url = urljoin(self.client.server_url, url)
        response = self.session.request(method, url, json=json)
        if 200 <= response.status_code <= 299:
            return response.json()

        if response.status_code == requests.codes.BAD_REQUEST:
            raise APIValueError(response.text)

        if response.status_code == requests.codes.PAYMENT_REQUIRED:
            with contextlib.suppress(TypeError, ValueError):
                json = dict(response.json())
                raise InsufficientCreditsError(
                    message=and_then(json.get("detail"), str),
                    required=and_then(json.get("required"), int),
                    available=and_then(json.get("available"), int),
                )
            raise InsufficientCreditsError(response.text)

        msg = f"Unexpected status code: {response.status_code} {response.reason}"
        raise CasaGeoError(msg)

    def close(self) -> None:
        self.session.close()
