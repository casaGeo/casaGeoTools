import datetime
import os
import unittest

import pandas as pd

import casageo.tools as ct
from casageo.coder import geocode


class TestBadKeys(unittest.TestCase):
    def setUp(self):
        self.queries = pd.DataFrame({"address": ["Hamburg, Germany"]})

    def test_empty_key(self):
        key = os.getenv("CASAGEOTOOLS_EMPTY_API_KEY") or self.skipTest(
            "No empty API key provided"
        )
        with ct.CasaGeoClient(key) as client:
            if ct.account_info(client)["credits"] != 0:
                self.skipTest("Empty API key has credits")

            with self.assertRaises(ct.InsufficientCreditsError):
                geocode(client, self.queries)

    def test_expired_key(self):
        key = os.getenv("CASAGEOTOOLS_EXPIRED_API_KEY") or self.skipTest(
            "No expired API key provided"
        )
        with ct.CasaGeoClient(key) as client:
            expires = datetime.datetime.fromisoformat(
                ct.account_info(client)["expires"]
            )
            if expires >= datetime.datetime.now(expires.tzinfo):
                self.skipTest("Expired API key is still valid")

            with self.assertRaisesRegex(
                ct.CasaGeoError, r"^Unexpected status code: (401|403)\b"
            ):
                geocode(client, self.queries)


if __name__ == "__main__":
    unittest.main()
