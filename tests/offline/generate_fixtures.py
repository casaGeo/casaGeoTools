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


import json
from pathlib import Path

from pandas import DataFrame
from shapely import Point

import casageo.coder as cg
import casageo.logistics as cl
import casageo.spatial as cs
import casageo.tools as ct
from casageo.tools._types import CasaGeoResult, MultiResult

FIXTURE_DIR = Path(__file__).parent / "fixtures"
POINT_IZET = Point(9.4854461, 53.9580118)
POINT_HH = Point(10.008223, 53.553089)
POINT_KIEL = Point(10.13008, 54.31367)
POINT_LUEBECK = Point(10.66865, 53.86621)


def save_fixture[T: CasaGeoResult](result: MultiResult[T], name: str) -> None:
    # Do not replace a successful fixture with an API error response.
    for item in result:
        if (error := item.error()) is not None:
            raise error
    if not result:
        raise ValueError(f"No results returned for {name}")

    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    path = FIXTURE_DIR / f"{name}.json"
    contents = json.dumps({"result": result.json()}, ensure_ascii=False, indent=2)
    path.write_text(contents + "\n", encoding="utf-8")
    print(f"Saved fixture {name}")


def main() -> None:
    client = ct.CasaGeoClient()

    address_queries = DataFrame([
        {"id": 1, "address": "Fraunhoferstr. 3, 25524 Itzehoe DEU"},
        {"id": 2, "address": "Hachmannplatz 16, 20099 Hamburg DEU"},
        {"id": 3, "address": "Sophienblatt 25, 24114 Kiel DEU"},
    ])
    save_fixture(
        cg.address_result(client, address_queries), "coder_address_simple_query"
    )

    client.preferred_language = "de,en"
    poi_queries = DataFrame([
        {"id": 1, "position": Point(9.48545, 53.95801), "limit": 2},
    ])
    save_fixture(cg.poi_result(client, poi_queries), "coder_poi_simple_query")
    client.preferred_language = None

    isolines_queries = DataFrame([
        {
            "id": 1,
            "position": POINT_HH,
            "name": "Hamburg Central Station",
            "range_type": "time",
            "ranges": [5, 15],
            "transport_mode": "car",
        },
        {
            "id": 2,
            "position": POINT_LUEBECK,
            "name": "Lübeck Central Station",
            "range_type": "distance",
            "ranges": [3000],
            "transport_mode": "pedestrian",
        },
        {
            "id": 3,
            "position": POINT_KIEL,
            "name": "Kiel Central Station",
            "range_type": "time",
            "ranges": [10],
            "transport_mode": "car",
        },
    ])
    save_fixture(
        cs.isolines_result(client, isolines_queries), "spatial_isolines_simple_query"
    )

    routes_queries = DataFrame([
        {
            "id": index,
            "origin": POINT_IZET,
            "destination": position,
            "routing_mode": "fast",
            "transport_mode": "car",
            "destination_name": name,
        }
        for index, (position, name) in enumerate(
            [
                (POINT_HH, "Hamburg Central Station"),
                (POINT_KIEL, "Kiel Central Station"),
                (POINT_LUEBECK, "Lübeck Central Station"),
            ],
            start=1,
        )
    ])
    save_fixture(
        cs.routes_result(client, routes_queries), "spatial_routes_simple_query"
    )

    waypoints = DataFrame([
        {"name": "Itzehoe", "position": Point(9.48545, 53.95801)},
        {"name": "Hamburg", "position": POINT_HH},
        {"name": "Kiel", "position": POINT_KIEL},
    ])
    # Supply destinations explicitly: the server currently forwards an empty
    # destination list upstream instead of applying the all-origin fallback.
    matrix_waypoints = DataFrame([
        {"type": waypoint_type, "position": position}
        for waypoint_type in ("origin", "destination")
        for position in waypoints["position"]
    ])
    save_fixture(
        cl.matrix_result(client, matrix_waypoints), "logistics_matrix_simple_query"
    )
    save_fixture(cl.tsp_result(client, waypoints), "logistics_tsp_simple_query")


if __name__ == "__main__":
    main()
