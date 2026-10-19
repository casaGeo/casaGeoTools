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
from pathlib import Path
from typing import cast
from unittest.mock import patch

from geopandas import GeoDataFrame
from pandas import DataFrame
from shapely import Point

import casageo.logistics as cl
import casageo.tools as ct

API_KEY = "XXXXX-XXXXX-XXXXX-XXXXX"
FIXTURE_DIR = Path(__file__).parent / "fixtures"


@functools.cache
def load_fixture(name: str):
    with open(FIXTURE_DIR / f"{name}.json", mode="rb") as f:
        return json.load(f)


class TestMatrixQuery(unittest.TestCase):
    symmetric_waypoints = DataFrame([
        {"position": Point(9.48545, 53.95801)},  # Itzehoe
        {"position": Point(10.008223, 53.553089)},  # Hamburg
        {"position": Point(10.13008, 54.31367)},  # Kiel
    ])

    asymmetric_waypoints = DataFrame([
        {"type": "origin", "position": Point(9.48545, 53.95801)},  # Itzehoe
        {"type": "origin", "position": Point(10.008223, 53.553089)},  # Hamburg
        {"type": "origin", "position": Point(10.13008, 54.31367)},  # Kiel
        {"type": "destination", "position": Point(9.48545, 53.95801)},  # Itzehoe
        {"type": "destination", "position": Point(10.008223, 53.553089)},  # Hamburg
        {"type": "destination", "position": Point(10.13008, 54.31367)},  # Kiel
    ])

    @staticmethod
    def generate_fixtures(client: ct.CasaGeoClient):
        yield (
            "logistics_matrix_symmetric",
            cl.matrix_result(client, TestMatrixQuery.symmetric_waypoints),
        )
        yield (
            "logistics_matrix_asymmetric",
            cl.matrix_result(client, TestMatrixQuery.asymmetric_waypoints),
        )

    def setUp(self):
        self.client = ct.CasaGeoClient(API_KEY)

    def tearDown(self):
        self.client.close()

    @patch("casageo.tools._client.CasaGeoClient.request", autospec=True)
    def test_matrix_symmetric(self, mock):
        fixture = load_fixture("logistics_matrix_symmetric")
        mock.return_value = fixture["result"]
        result = cl.matrix(self.client, waypoints=self.symmetric_waypoints)

        mock.assert_called_once_with(
            self.client,
            "POST",
            "/api/v2/matrix",
            json={
                "options": {"profile": cl.MatrixRoutingProfile.CAR_FAST},
                "waypoints": [
                    {"position": (9.48545, 53.95801)},
                    {"position": (10.008223, 53.553089)},
                    {"position": (10.13008, 54.31367)},
                ],
            },
        )

        self._check_result(result)

    @patch("casageo.tools._client.CasaGeoClient.request", autospec=True)
    def test_matrix_asymmetric(self, mock):
        fixture = load_fixture("logistics_matrix_asymmetric")
        mock.return_value = fixture["result"]
        result = cl.matrix(self.client, waypoints=self.asymmetric_waypoints)

        mock.assert_called_once_with(
            self.client,
            "POST",
            "/api/v2/matrix",
            json={
                "options": {"profile": cl.MatrixRoutingProfile.CAR_FAST},
                "waypoints": [
                    {"type": "origin", "position": (9.48545, 53.95801)},
                    {"type": "origin", "position": (10.008223, 53.553089)},
                    {"type": "origin", "position": (10.13008, 54.31367)},
                    {"type": "destination", "position": (9.48545, 53.95801)},
                    {"type": "destination", "position": (10.008223, 53.553089)},
                    {"type": "destination", "position": (10.13008, 54.31367)},
                ],
            },
        )

        self._check_result(result)

    def _check_result(self, result: DataFrame):
        self.assertIsInstance(result, DataFrame)
        self.assertEqual(len(result), 9)
        self.assertListEqual(result["id"].to_list(), [1] * 9)
        self.assertListEqual(result["origin"].to_list(), [0, 0, 0, 1, 1, 1, 2, 2, 2])
        self.assertListEqual(result["destination"].to_list(), [0, 1, 2] * 3)
        self.assertListEqual(result["statuscode"].to_list(), [0] * 9)
        self.assertTrue(result["distance"].notna().all())
        self.assertTrue(result["traveltime"].notna().all())

        for row in result.itertuples(index=False):
            with self.subTest(origin=row.origin, destination=row.destination):
                if row.origin == row.destination:
                    self.assertEqual(row.distance, 0)
                    self.assertEqual(row.traveltime, 0)
                else:
                    self.assertGreater(cast(float, row.distance), 0)
                    self.assertGreater(cast(float, row.traveltime), 0)


class TestTSPQuery(unittest.TestCase):
    waypoints = DataFrame([
        {
            "name": "Itzehoe",
            "navigation": Point(9.48545, 53.95801),
        },
        {
            "name": "Hamburg",
            "navigation": Point(10.008223, 53.553089),
        },
        {
            "name": "Kiel",
            "navigation": Point(10.13008, 54.31367),
        },
    ])

    @staticmethod
    def generate_fixtures(client: ct.CasaGeoClient):
        yield (
            "logistics_tsp_simple_query",
            cl.tsp_result(client, TestTSPQuery.waypoints),
        )

    def setUp(self):
        self.client = ct.CasaGeoClient(API_KEY)

    def tearDown(self):
        self.client.close()

    @patch("casageo.tools._client.CasaGeoClient.request", autospec=True)
    def test_tsp_simple(self, mock):
        fixture = load_fixture("logistics_tsp_simple_query")
        mock.return_value = fixture["result"]
        result = cl.tsp(self.client, self.waypoints)

        mock.assert_called_once_with(
            self.client,
            "POST",
            "/api/v2/tsp",
            json={
                "options": {
                    "origin": "Itzehoe",
                    "break_times": [],
                    "transport_mode": cl.TransportMode.CAR,
                    "routing_mode": cl.RoutingMode.FAST,
                    "optimize": cl.TspOptimizationTarget.TIME,
                    "traffic": False,
                    "avoid_features": [],
                    "exclude_countries": [],
                    "hazardous_cargo": [],
                },
                "waypoints": [
                    {"name": "Itzehoe", "position": (9.48545, 53.95801)},
                    {"name": "Hamburg", "position": (10.008223, 53.553089)},
                    {"name": "Kiel", "position": (10.13008, 54.31367)},
                ],
            },
        )

        self.assertIsInstance(result, GeoDataFrame)
        self.assertEqual(result.crs, "EPSG:4326")
        self.assertEqual(len(result), 3)
        self.assertListEqual(result["id"].to_list(), [1, 1, 1])
        self.assertListEqual(result["subid"].to_list(), [0, 1, 2])
        self.assertListEqual(result["name"].to_list(), ["Itzehoe", "Hamburg", "Kiel"])
        self.assertIsNotNone(result["position"].iloc[0])
        self.assertIsNotNone(result["travel_distance"].iloc[1])
        self.assertIsNotNone(result["travel_duration"].iloc[1])


if __name__ == "__main__":
    unittest.main()
