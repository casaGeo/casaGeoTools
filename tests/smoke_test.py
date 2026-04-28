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
from collections.abc import Sequence
from pathlib import Path
from unittest.mock import patch

from pandas import DataFrame
from shapely import Point

import casageo.coder as cc
import casageo.spatial as cs  # type:ignore
import casageo.tools as ct

API_KEY = "XXXXX-XXXXX-XXXXX-XXXXX"
FIXTURE_DIR = Path(__file__).parent / "fixtures"


@functools.cache
def load_fixture(name: str):
    with open(FIXTURE_DIR / f"{name}.json", mode="rb") as f:
        return json.load(f)


def main(args: Sequence[str] | None = None) -> None:
    client = ct.CasaGeoClient("XXXXX-XXXXX-XXXXX-XXXXX")
    address_queries = DataFrame([
        {"id": 1, "address": "Fraunhoferstr. 3, 25524 Itzehoe DEU"},
        {"id": 2, "address": "Hachmannplatz 16, 20099 Hamburg DEU"},
        {"id": 3, "address": "Sophienblatt 25, 24114 Kiel DEU"},
    ])
    poi_queries = DataFrame([
        {
            "id": 1,
            "position": Point(9.48545, 53.95801),
            "limit": 2,
        },
    ])
    isolines_queries = DataFrame([
        {
            "id": 1,
            "position": Point(10.008223, 53.553089),
            "name": "Hamburg Central Station",
            "range_type": "time",
            "ranges": [5, 15],
            "transport_mode": "car",
        },
        {
            "id": 2,
            "position": Point(10.66865, 53.86621),
            "name": "Lübeck Central Station",
            "range_type": "distance",
            "ranges": [3000],
            "transport_mode": "pedestrian",
        },
        {
            "id": 3,
            "position": Point(10.13008, 54.31367),
            "name": "Kiel Central Station",
            "range_type": "time",
            "ranges": [10],
            "transport_mode": "car",
        },
    ])
    routes_queries = DataFrame([
        {
            "id": 1,
            "origin": Point(9.4854461, 53.9580118),
            "destination": Point(10.008223, 53.553089),
            "routing_mode": "fast",
            "transport_mode": "car",
            "destination_name": "Hamburg Central Station",
        },
        {
            "id": 2,
            "origin": Point(9.4854461, 53.9580118),
            "destination": Point(10.13008, 54.31367),
            "routing_mode": "fast",
            "transport_mode": "car",
            "destination_name": "Kiel Central Station",
        },
        {
            "id": 3,
            "origin": Point(9.4854461, 53.9580118),
            "destination": Point(10.66865, 53.86621),
            "routing_mode": "fast",
            "transport_mode": "car",
            "destination_name": "Lübeck Central Station",
        },
    ])

    with patch("casageo.tools._apiv2.address") as mock:
        fixture = load_fixture("coder_address_simple_query")
        mock.return_value = fixture["result"]
        cc.address(client, address_queries)
        assert mock.called

    with patch("casageo.tools._apiv2.poi") as mock:
        fixture = load_fixture("coder_poi_simple_query")
        mock.return_value = fixture["result"]
        cc.poi(client, poi_queries)
        assert mock.called

    with patch("casageo.tools._apiv2.isolines") as mock:
        fixture = load_fixture("spatial_isolines_simple_query")
        mock.return_value = fixture["result"]
        cs.isolines(client, isolines_queries)
        assert mock.called

    with patch("casageo.tools._apiv2.routes") as mock:
        fixture = load_fixture("spatial_routes_simple_query")
        mock.return_value = fixture["result"]
        cs.routes(client, routes_queries)
        assert mock.called


if __name__ == "__main__":
    main()
