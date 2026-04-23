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

import contextlib
from collections.abc import Sequence
from typing import Any

import httpx

from ._client import CasaGeoClient
from ._errors import (
    APIReturnTypeError,
    APIValueError,
    CasaGeoError,
    InsufficientCreditsError,
)
from ._util import and_then


def _as[T](tp: type[T], val: Any) -> T:
    if not isinstance(val, tp):
        raise APIReturnTypeError(f"Expected {tp!r}, got {type(val)!r}")
    return val


def _ensure_success(response: httpx.Response):
    if response.is_success:
        return

    if response.status_code == httpx.codes.BAD_REQUEST:
        raise APIValueError(response.text)

    if response.status_code == httpx.codes.PAYMENT_REQUIRED:
        with contextlib.suppress(TypeError, ValueError):
            json = _as(dict, response.json())
            raise InsufficientCreditsError(
                message=and_then(json.get("detail"), str),
                required=and_then(json.get("required"), int),
                available=and_then(json.get("available"), int),
            )
        raise InsufficientCreditsError(response.text)

    response.raise_for_status()

    raise CasaGeoError(f"Unexpected status code {response.status_code}")


def _decode_dict(response: httpx.Response) -> dict:
    _ensure_success(response)
    return _as(dict, response.json())


def address(
    client: httpx.Client,
    queries: list[dict],
    options: dict | None = None,
) -> dict:
    options = options if options is not None else {}
    response = client.post(
        "/api/v2/address",
        json={
            "options": options,
            "queries": queries,
        },
    )
    return _decode_dict(response)


def poi(
    client: httpx.Client,
    queries: list[dict],
    options: dict | None = None,
) -> dict:
    options = options if options is not None else {}
    response = client.post(
        "/api/v2/poi",
        json={
            "options": options,
            "queries": queries,
        },
    )
    return _decode_dict(response)


def isolines(
    client: httpx.Client,
    queries: list[dict],
    options: dict | None = None,
) -> dict:
    options = options if options is not None else {}
    response = client.post(
        "/api/v2/isolines",
        json={
            "options": options,
            "queries": queries,
        },
    )
    return _decode_dict(response)


def routes(
    client: httpx.Client,
    queries: list[dict],
    options: dict | None = None,
) -> dict:
    options = options if options is not None else {}
    response = client.post(
        "/api/v2/routes",
        json={
            "options": options,
            "queries": queries,
        },
    )
    return _decode_dict(response)


def _main(args: Sequence[str] | None = None) -> None:
    import argparse
    import json
    import os
    import sys

    parser = argparse.ArgumentParser(allow_abbrev=False)
    subparsers = parser.add_subparsers(required=True, metavar="COMMAND")

    address_parser = subparsers.add_parser("address")
    address_parser.set_defaults(command=address)
    address_parser.add_argument(
        "queries",
        nargs="?",
        default=sys.stdin,
        type=argparse.FileType("r"),
    )

    poi_parser = subparsers.add_parser("poi")
    poi_parser.set_defaults(command=poi)
    poi_parser.add_argument(
        "queries",
        nargs="?",
        default=sys.stdin,
        type=argparse.FileType("r"),
    )

    isolines_parser = subparsers.add_parser("isolines")
    isolines_parser.set_defaults(command=isolines)
    isolines_parser.add_argument(
        "queries",
        nargs="?",
        default=sys.stdin,
        type=argparse.FileType("r"),
    )

    routes_parser = subparsers.add_parser("routes")
    routes_parser.set_defaults(command=routes)
    routes_parser.add_argument(
        "queries",
        nargs="?",
        default=sys.stdin,
        type=argparse.FileType("r"),
    )

    options = parser.parse_args(args)
    queries = json.load(options.queries)
    api_key = os.getenv("CASAGEOTOOLS_API_KEY") or sys.exit(
        "Please specify an API key in the environment variable CASAGEOTOOLS_API_KEY"
    )

    client = CasaGeoClient(api_key)._httpxclient
    result = options.command(client, queries)

    json.dump(result, sys.stdout, ensure_ascii=False, indent=4, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    _main()
