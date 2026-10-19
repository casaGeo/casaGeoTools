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

import string
import unittest
from urllib.parse import quote_plus

import casageo.tools as ct

API_KEY = "XXXXX-XXXXX-XXXXX-XXXXX"
SERVER_URL = "https://api.example.com"


class TestMaptiles(unittest.TestCase):
    def setUp(self):
        self.client = ct.CasaGeoClient(API_KEY, server_url=SERVER_URL)
        self.expected_base = (
            SERVER_URL + "/api/maps/v1/tiles/{z}/{x}/{y}?apikey=" + quote_plus(API_KEY)
        )
        self.raw_value = string.printable
        self.escaped_value = quote_plus(self.raw_value)

    def tearDown(self):
        self.client.close()

    def test_maptiles_empty(self):
        self.assertEqual(ct.get_maptile_url(self.client), self.expected_base)

    def test_maptiles_layer(self):
        url = ct.get_maptile_url(self.client, layer=self.raw_value)
        self.assertEqual(url, self.expected_base + "&layer=" + self.escaped_value)

    def test_maptiles_proj(self):
        url = ct.get_maptile_url(self.client, proj=self.raw_value)
        self.assertEqual(url, self.expected_base + "&proj=" + self.escaped_value)

    def test_maptiles_style(self):
        url = ct.get_maptile_url(self.client, style=self.raw_value)
        self.assertEqual(url, self.expected_base + "&style=" + self.escaped_value)

    def test_maptiles_language(self):
        url = ct.get_maptile_url(self.client, language=self.raw_value)
        self.assertEqual(url, self.expected_base + "&lang=" + self.escaped_value)

    def test_maptiles_second_language(self):
        url = ct.get_maptile_url(self.client, second_language=self.raw_value)
        self.assertEqual(url, self.expected_base + "&lang2=" + self.escaped_value)

    def test_maptiles_political_view(self):
        url = ct.get_maptile_url(self.client, political_view=self.raw_value)
        self.assertEqual(url, self.expected_base + "&pview=" + self.escaped_value)

    def test_maptiles_ppi(self):
        url = ct.get_maptile_url(self.client, ppi=self.raw_value)
        self.assertEqual(url, self.expected_base + "&ppi=" + self.escaped_value)


if __name__ == "__main__":
    unittest.main()
