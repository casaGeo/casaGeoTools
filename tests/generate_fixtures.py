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

import functools
import json
import os
import sys
from contextlib import contextmanager

import httpx
from shapely import Point

import casageo.coder as cg
import casageo.spatial as cs
import casageo.tools as ct

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
POINT_IZET = Point(9.4854461, 53.9580118)
POINT_HH = Point(10.008223, 53.553089)
REDACTED_API_KEY = "XXXXX-XXXXX-XXXXX-XXXXX"


API_KEY = os.getenv("CASAGEOTOOLS_API_KEY") or sys.exit("Please specify an API key")
cga = ct.CasaGeoClient(API_KEY)
cga.preferred_language = "de,en"

cgs = cs.CasaGeoSpatial(cga)
cgc = cg.CasaGeoCoder(cga)


@contextmanager
def patch_request(fixture: dict):
    httpx_request = httpx.Client.request

    @functools.wraps(httpx_request)
    def request(self, method, url, **kwargs):
        kwargs["method"] = method
        kwargs["url"] = url
        response = httpx_request(self, **kwargs)
        fixture["request"] = kwargs
        fixture["response"] = {
            "status_code": response.status_code,
            "headers": dict(response.headers.items()),
            "json": response.json(),
        }
        return response

    try:
        httpx.Client.request = request  # type: ignore[method-assign]
        yield
    finally:
        httpx.Client.request = httpx_request  # type: ignore[method-assign]


def ensure(result):
    if not result:
        raise result.error()


def save_fixture(fixture: dict, name: str):
    with open(
        os.path.join(FIXTURE_DIR, f"{name}.json"),
        mode="w",
        encoding="utf-8",
        newline="\n",
    ) as f:
        json.dump(fixture, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Saved fixture {name}")


def account_info_1_fixture():
    fixture = {}
    with patch_request(fixture):
        ensure(cga.account_info())

    fixture["response"]["json"]["user"] = "testuser"
    fixture["response"]["json"]["credits"] = 43359
    fixture["response"]["json"]["note"] = "Professional"
    fixture["response"]["json"]["key"] = REDACTED_API_KEY

    save_fixture(fixture, "account_info_1")


def coder_address_1_fixture():
    fixture = {}
    with patch_request(fixture):
        ensure(cgc.address_single("Fraunhoferstr. 3, 25524 Itzehoe DEU"))

    save_fixture(fixture, "coder_address_1")


def spatial_isolines_1_fixture():
    fixture = {}
    with patch_request(fixture):
        ensure(cgs.isolines_single(POINT_HH, [3, 9, 15], range_type="time"))

    save_fixture(fixture, "spatial_isolines_1")


def spatial_routes_1_fixture():
    fixture = {}
    with patch_request(fixture):
        ensure(cgs.routes_single(POINT_IZET, POINT_HH))

    save_fixture(fixture, "spatial_routes_1")


def coder_poi_1_fixture():
    fixture = {}
    with patch_request(fixture):
        ensure(cgc.poi_single(POINT_IZET, categories=["100"]))

    save_fixture(fixture, "coder_poi_1")


def main():
    account_info_1_fixture()
    coder_address_1_fixture()
    spatial_isolines_1_fixture()
    spatial_routes_1_fixture()
    coder_poi_1_fixture()


if __name__ == "__main__":
    main()
