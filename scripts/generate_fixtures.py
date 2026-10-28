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
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from shapely import Point

import casageo.tools as ct
from casageo.tools._types import MultiResult

PROJECT_DIR = Path(__file__).parent.parent
TESTS_DIR = PROJECT_DIR / "tests"
FIXTURE_DIR = TESTS_DIR / "fixtures"
POINT_IZET = Point(9.4854461, 53.9580118)
POINT_HH = Point(10.008223, 53.553089)
POINT_KIEL = Point(10.13008, 54.31367)
POINT_LUEBECK = Point(10.66865, 53.86621)


def save_fixture(result: MultiResult[Any], name: str) -> None:
    # Do not replace a successful fixture with an API error response.
    for item in result:
        if (error := item.error()) is not None:
            raise error
    if not result:
        raise ValueError(f"No results returned for {name}")

    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)

    with open(
        FIXTURE_DIR / f"{name}.json",
        mode="w",
        encoding="utf-8",
        newline="\n",
    ) as fp:
        json.dump({"result": result.json()}, fp, ensure_ascii=False, indent=2)
        fp.write("\n")

    print(f"Saved fixture {name}")


def main(argv: Sequence[str] | None = None) -> None:
    import sys

    import dotenv

    sys.path.insert(0, str(PROJECT_DIR.absolute()))

    from tests.test_coder import TestGeocodeQuery, TestPOIQuery
    from tests.test_logistics import TestMatrixQuery, TestTSPQuery
    from tests.test_spatial import TestIsolineQuery, TestRoutesQuery

    if argv is None:
        argv = sys.argv

    dotenv.load_dotenv()

    client = ct.CasaGeoClient()

    selected = set(argv[1:])

    for testcase in (
        TestGeocodeQuery,
        TestPOIQuery,
        TestIsolineQuery,
        TestRoutesQuery,
        TestMatrixQuery,
        TestTSPQuery,
    ):
        for name, result in testcase.generate_fixtures(client):
            if selected and name not in selected:
                continue
            save_fixture(result, name)


if __name__ == "__main__":
    main()
