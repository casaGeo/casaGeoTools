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
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from geopandas import GeoDataFrame
from pandas import DataFrame
from shapely import MultiLineString, MultiPolygon, Point

import casageo.spatial as cs
import casageo.tools as ct

API_KEY = "XXXXX-XXXXX-XXXXX-XXXXX"
FIXTURE_DIR = Path(__file__).parent / "fixtures"


@functools.cache
def load_fixture(name: str):
    with open(FIXTURE_DIR / f"{name}.json", mode="rb") as f:
        return json.load(f)


class TestIsolinesQuery(unittest.TestCase):
    def setUp(self):
        self.client = ct.CasaGeoClient(API_KEY)
        self.queries = DataFrame([
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

    @patch("casageo.tools._apiv2.isolines", autospec=True)
    def test_simple_query(self, mock):
        fixture = load_fixture("spatial_isolines_simple_query")
        mock.return_value = fixture["result"]
        results = cs.isolines(self.client, self.queries)

        mock.assert_called_once_with(
            self.client._httpxclient,
            [
                {
                    "arrival_time": None,
                    "avoid_features": (),
                    "departure_time": None,
                    "direction": "outgoing",
                    "exclude_countries": (),
                    "language": "en-US",
                    "position": (10.008223, 53.553089),
                    "ranges": [5, 15],
                    "ranges_unit": "minutes",
                    "routing_mode": "fast",
                    "traffic": False,
                    "transport_mode": "car",
                    "unit_system": "metric",
                },
                {
                    "arrival_time": None,
                    "avoid_features": (),
                    "departure_time": None,
                    "direction": "outgoing",
                    "exclude_countries": (),
                    "language": "en-US",
                    "position": (10.66865, 53.86621),
                    "ranges": [3000],
                    "ranges_unit": "meters",
                    "routing_mode": "fast",
                    "traffic": False,
                    "transport_mode": "pedestrian",
                    "unit_system": "metric",
                },
                {
                    "arrival_time": None,
                    "avoid_features": (),
                    "departure_time": None,
                    "direction": "outgoing",
                    "exclude_countries": (),
                    "language": "en-US",
                    "position": (10.13008, 54.31367),
                    "ranges": [10],
                    "ranges_unit": "minutes",
                    "routing_mode": "fast",
                    "traffic": False,
                    "transport_mode": "car",
                    "unit_system": "metric",
                },
            ],
            {
                "departure_info": False,
                "arrival_info": False,
            },
        )

        self.assertIsInstance(results, GeoDataFrame)
        self.assertEqual(results.crs, "EPSG:4326")
        self.assertEqual(len(results), 4)
        self.assertListEqual(results["id"].to_list(), [1, 1, 2, 3])
        self.assertListEqual(results["subid"].to_list(), [0, 1, 0, 0])
        for g in results["geometry"]:
            self.assertIsInstance(g, MultiPolygon)
            self.assertTrue(g.is_valid)
            self.assertFalse(g.is_empty)
        self.assertListEqual(
            results["rangetype"].to_list(), ["time", "time", "distance", "time"]
        )
        self.assertListEqual(
            results["rangeunit"].to_list(), ["minutes", "minutes", "meters", "minutes"]
        )
        self.assertListEqual(results["rangevalue"].to_list(), [5, 15, 3000, 10])
        for t in results["timestamp"]:
            self.assertIsInstance(t, datetime)


class TestRoutesQuery(unittest.TestCase):
    def setUp(self):
        self.client = ct.CasaGeoClient(API_KEY)
        self.queries = DataFrame([
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

    @patch("casageo.tools._apiv2.routes", autospec=True)
    def test_simple_query(self, mock):
        fixture = load_fixture("spatial_routes_simple_query")
        mock.return_value = fixture["result"]
        results = cs.routes(self.client, self.queries)

        mock.assert_called_once_with(
            self.client._httpxclient,
            [
                {
                    "alternatives": 0,
                    "arrival_time": None,
                    "avoid_features": (),
                    "departure_time": None,
                    "destination": (10.008223, 53.553089),
                    "exclude_countries": (),
                    "language": "en-US",
                    "origin": (9.4854461, 53.9580118),
                    "routing_mode": "fast",
                    "traffic": False,
                    "transport_mode": "car",
                    "unit_system": "metric",
                },
                {
                    "alternatives": 0,
                    "arrival_time": None,
                    "avoid_features": (),
                    "departure_time": None,
                    "destination": (10.13008, 54.31367),
                    "exclude_countries": (),
                    "language": "en-US",
                    "origin": (9.4854461, 53.9580118),
                    "routing_mode": "fast",
                    "traffic": False,
                    "transport_mode": "car",
                    "unit_system": "metric",
                },
                {
                    "alternatives": 0,
                    "arrival_time": None,
                    "avoid_features": (),
                    "departure_time": None,
                    "destination": (10.66865, 53.86621),
                    "exclude_countries": (),
                    "language": "en-US",
                    "origin": (9.4854461, 53.9580118),
                    "routing_mode": "fast",
                    "traffic": False,
                    "transport_mode": "car",
                    "unit_system": "metric",
                },
            ],
            {
                "arrival_info": False,
                "departure_info": False,
            },
        )

        self.assertIsInstance(results, GeoDataFrame)
        self.assertEqual(results.crs, "EPSG:4326")
        self.assertEqual(len(results), 3)
        self.assertListEqual(results["id"].to_list(), [1, 2, 3])
        self.assertListEqual(results["subid"].to_list(), [0, 0, 0])
        for g in results["geometry"]:
            self.assertIsInstance(g, MultiLineString)
            self.assertTrue(g.is_valid)
            self.assertFalse(g.is_empty)
        self.assertListEqual(results["length"].to_list(), [62603, 76977, 93361])
        self.assertListEqual(
            results["duration"].to_list(),
            [45.18333333333333, 54.983333333333334, 80.28333333333333],
        )
        for t in results["timestamp"]:
            self.assertIsInstance(t, datetime)


if __name__ == "__main__":
    unittest.main()
