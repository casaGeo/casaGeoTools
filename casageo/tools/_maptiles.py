#  Copyright 2026 casaGeo Data + Services GmbH <info@casageo.de>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  SPDX-License-Identifier: Apache-2.0

from urllib.parse import urlencode, urljoin

from casageo.tools import CasaGeoClient


def get_maptile_url(
    client: CasaGeoClient,
    *,
    layer: str = "",
    proj: str = "",
    style: str = "",
    language: str = "",
    second_language: str = "",
    political_view: str = "",
    ppi: int | str = "",
) -> str:
    """
    Build a query URL template for the casaGeo XYZ map tiles API.

    Args:
        client: The casaGeo client instance used to retrieve the server URL and API key.
        layer: Map layer, only ``"base"`` is supported for now.
        proj: Map projection, only ``"mercator"`` is supported for now.
        style: Style of the map, one of ``"standard"``, ``"light"`` or ``"satellite"``.
        language: Language to use for map labels (BCP 47 language tag).
        second_language: Second language to use for bilingual map labels (BCP 47 language tag).
        political_view: Which political view to use (ISO 3166 ALPHA-2 or ALPHA-3 code).
        ppi: Map tile resolution in pixels per inch, either 100, 200 or 400.

    Returns:
        str: The constructed URL template with ``{x}``, ``{y}`` and ``{z}`` placeholders.
    """

    query = {"apikey": client.apikey}

    if layer:
        query["layer"] = layer
    if proj:
        query["proj"] = proj
    if style:
        query["style"] = style
    if language:
        query["lang"] = language
    if second_language:
        query["lang2"] = second_language
    if political_view:
        query["pview"] = political_view
    if ppi != "":
        query["ppi"] = str(ppi)

    return urljoin(client.server, "api/maps/v1/tiles/{z}/{x}/{y}?" + urlencode(query))
