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
from shapely import Point

import casageo.coder as cc
import casageo.tools as ct

API_KEY = "XXXXX-XXXXX-XXXXX-XXXXX"
FIXTURE_DIR = Path(__file__).parent / "fixtures"


@functools.cache
def load_fixture(name: str):
    with open(FIXTURE_DIR / f"{name}.json", mode="rb") as f:
        return json.load(f)


class TestAddressQuery(unittest.TestCase):
    def setUp(self):
        self.client = ct.CasaGeoClient(API_KEY)
        self.address_queries = DataFrame([
            {"id": 1, "address": "Fraunhoferstr. 3, 25524 Itzehoe DEU"},
            {"id": 2, "address": "Hachmannplatz 16, 20099 Hamburg DEU"},
            {"id": 3, "address": "Sophienblatt 25, 24114 Kiel DEU"},
        ])

    @patch("casageo.tools._apiv2.address", autospec=True)
    def test_simple_query(self, mock):
        fixture = load_fixture("coder_address_simple_query")
        mock.return_value = fixture["result"]
        results = cc.address(self.client, self.address_queries)
        mock.assert_called_once_with(
            self.client._httpxclient,
            [
                {
                    "address": "Fraunhoferstr. 3, 25524 Itzehoe DEU",
                    "country": None,
                    "state": None,
                    "county": None,
                    "city": None,
                    "district": None,
                    "street": None,
                    "housenumber": None,
                    "postalcode": None,
                    "position": None,
                    "language": "en-US",
                    "political_view": None,
                    "limit": 20,
                    "countries": None,
                    "address_names_mode": "default",
                    "postal_code_mode": "default",
                },
                {
                    "address": "Hachmannplatz 16, 20099 Hamburg DEU",
                    "country": None,
                    "state": None,
                    "county": None,
                    "city": None,
                    "district": None,
                    "street": None,
                    "housenumber": None,
                    "postalcode": None,
                    "position": None,
                    "language": "en-US",
                    "political_view": None,
                    "limit": 20,
                    "countries": None,
                    "address_names_mode": "default",
                    "postal_code_mode": "default",
                },
                {
                    "address": "Sophienblatt 25, 24114 Kiel DEU",
                    "country": None,
                    "state": None,
                    "county": None,
                    "city": None,
                    "district": None,
                    "street": None,
                    "housenumber": None,
                    "postalcode": None,
                    "position": None,
                    "language": "en-US",
                    "political_view": None,
                    "limit": 20,
                    "countries": None,
                    "address_names_mode": "default",
                    "postal_code_mode": "default",
                },
            ],
            {
                "address_details": False,
                "coordinates": False,
                "match_quality": False,
            },
        )

        self.assertIsInstance(results, GeoDataFrame)
        self.assertEqual(results.crs, "EPSG:4326")
        self.assertEqual(len(results), 3)
        self.assertListEqual(results["id"].to_list(), [1, 2, 3])
        self.assertListEqual(results["subid"].to_list(), [0, 0, 0])
        self.assertListEqual(
            results["address"].to_list(),
            [
                "Fraunhoferstraße 3, 25524 Itzehoe, Germany",
                "Hachmannplatz 16, 20099 Hamburg, Germany",
                "Sophienblatt 25, 24114 Kiel, Germany",
            ],
        )
        self.assertListEqual(results["resulttype"].to_list(), ["houseNumber"] * 3)
        self.assertListEqual(
            results["position"].to_list(),
            [
                Point(9.48572, 53.95815),
                Point(10.007, 53.55281),
                Point(10.13147, 54.31544),
            ],
        )
        self.assertListEqual(
            results["navigation"].to_list(),
            [
                Point(9.48615, 53.95801),
                Point(10.00805, 53.55291),
                Point(10.13124, 54.31543),
            ],
        )
        self.assertListEqual(results["distance"].to_list(), [None] * 3)
        self.assertListEqual(results["relevance"].to_list(), [1.0] * 3)
        for t in results["timestamp"]:
            self.assertIsInstance(t, datetime)


class TestPOIQuery(unittest.TestCase):
    def setUp(self):
        self.client = ct.CasaGeoClient(API_KEY)
        self.client.preferred_language = "de,en"
        self.poi_queries = DataFrame([
            {
                "id": 1,
                "position": Point(9.48545, 53.95801),
                "limit": 2,
            },
        ])

    @patch("casageo.tools._apiv2.poi", autospec=True)
    def test_simple_query(self, mock):
        fixture = load_fixture("coder_poi_simple_query")
        mock.return_value = fixture["result"]
        results = cc.poi(self.client, self.poi_queries)
        mock.assert_called_once_with(
            self.client._httpxclient,
            [
                {
                    "position": (9.48545, 53.95801),
                    "language": "de,en",
                    "political_view": None,
                    "limit": 2,
                    "countries": None,
                    "address_names_mode": "default",
                    "postal_code_mode": "default",
                }
            ],
            {
                "address_details": False,
                "coordinates": False,
                "category_codes": False,
            },
        )

        self.assertIsInstance(results, GeoDataFrame)
        self.assertEqual(results.crs, "EPSG:4326")
        self.assertEqual(len(results), 2)
        self.assertListEqual(results["id"].to_list(), [1, 1])
        self.assertListEqual(results["subid"].to_list(), [0, 1])
        self.assertListEqual(
            results["title"].to_list(),
            ["Plietsch und Lecker", "Kalle Bäcker"],
        )
        self.assertListEqual(results["resulttype"].to_list(), ["place"] * 2)
        self.assertListEqual(
            results["position"].to_list(),
            [
                Point(9.49558, 53.95869),
                Point(9.49377, 53.95202),
            ],
        )
        self.assertListEqual(
            results["navigation"].to_list(),
            [
                Point(9.49557, 53.9588),
                Point(9.49378, 53.95192),
            ],
        )
        self.assertListEqual(results["distance"].to_list(), [667, 860])
        for t in results["timestamp"]:
            self.assertIsInstance(t, datetime)


if __name__ == "__main__":
    unittest.main()
