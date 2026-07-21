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
import unittest

import casageo.logistics as cl
import casageo.tools as ct


class TestLogistics(unittest.TestCase):
    def setUp(self):
        key = os.getenv("CASAGEOTOOLS_API_KEY") or self.skipTest("No API key provided")
        self.client = ct.CasaGeoClient(key)

    def test_tsp(self):
        from geopandas import GeoDataFrame
        from pandas import DataFrame
        from shapely import Point

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

        result = cl.tsp(self.client, waypoints=waypoints)

        self.assertIsInstance(result, GeoDataFrame)
        self.assertEqual(result.crs, "EPSG:4326")
        self.assertEqual(len(result), 3)
        self.assertListEqual(result["id"].to_list(), [1, 1, 1])
        self.assertListEqual(result["subid"].to_list(), [0, 1, 2])
        self.assertListEqual(result["name"].to_list(), ["Itzehoe", "Hamburg", "Kiel"])
        self.assertIsNotNone(result["navigation"].iloc[0])
        self.assertIsNotNone(result["travel_distance"].iloc[1])
        self.assertIsNotNone(result["travel_duration"].iloc[1])
