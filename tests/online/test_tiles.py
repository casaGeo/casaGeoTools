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

import requests

import casageo.tools as ct


class TestTiles(unittest.TestCase):
    def setUp(self):
        key = os.getenv("CASAGEOTOOLS_API_KEY") or self.skipTest("No API key provided")
        self.client = ct.CasaGeoClient(key)

    def test_maptile(self):
        # XYZ tile containing Hamburg at zoom level 10.
        url = ct.get_maptile_url(self.client).format(z=10, x=540, y=330)

        response = requests.get(url, timeout=30)

        self.assertEqual(response.status_code, requests.codes.OK)
        self.assertTrue(response.headers.get("content-type", "").startswith("image/"))
        self.assertTrue(response.content)


if __name__ == "__main__":
    unittest.main()
