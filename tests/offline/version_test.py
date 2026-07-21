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

import re
import runpy
import tomllib
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.parent
DOCUMENTATION_DIR = PROJECT_DIR / "docs"


def main() -> None:
    with open(PROJECT_DIR / "pyproject.toml", mode="rb") as f:
        pyproject = tomllib.load(f)

    project_version = pyproject["project"]["version"]
    assert isinstance(project_version, str)

    sphinx_conf = runpy.run_path(str(DOCUMENTATION_DIR / "conf.py"))

    if sphinx_version := sphinx_conf.get("version"):
        assert isinstance(sphinx_version, str)
        rx = r"(?:[0-9]+!)?" + re.escape(sphinx_version) + r"(?:[a-z._-].*)?"
        assert re.fullmatch(rx, project_version, re.ASCII | re.IGNORECASE)

    if sphinx_release := sphinx_conf.get("release"):
        assert isinstance(sphinx_release, str)
        assert sphinx_release == project_version


if __name__ == "__main__":
    main()
