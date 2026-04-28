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

"""
Provides geocoding operations.
"""

import argparse
import os
import statistics
import sys
from collections.abc import Generator, Iterable, Mapping, Sequence
from typing import Any, cast

from geopandas import GeoDataFrame
from pandas import DataFrame

from casageo.tools import CasaGeoClient, CasaGeoError, _apiv2, _consts, _util
from casageo.tools._types import CasaGeoResult, MultiResult
from casageo.tools._util import (
    and_then,
    dict_to_point,
    getpoint,
    point_xy,
    split_if_str,
    to_records,
)

DEFAULT_LANGUAGE: str = "en-US"
"""The default language used in the results."""

DEFAULT_POLITICAL_VIEW: str | None = None
"""The default political view used in the results."""

DEFAULT_LIMIT: int = 20
"""The default limit on the number of computed results."""

DEFAULT_COUNTRIES: tuple[str, ...] | None = None
"""The default list of countries to restrict the search to."""

DEFAULT_ADDRESS_NAMES_MODE: str = "default"
"""The default address names mode."""

DEFAULT_POSTAL_CODE_MODE: str = "default"
"""The default postal code mode."""


def _average(nums):
    return statistics.mean(nums) if nums else None


def _coder_params(q: Mapping) -> dict:
    return {
        "language": q.get("language", DEFAULT_LANGUAGE),
        "political_view": q.get("political_view", DEFAULT_POLITICAL_VIEW),
        "limit": q.get("limit", DEFAULT_LIMIT),
        "countries": and_then(q.get("countries", DEFAULT_COUNTRIES), split_if_str(",")),
        "address_names_mode": q.get("address_names_mode", DEFAULT_ADDRESS_NAMES_MODE),
        "postal_code_mode": q.get("postal_code_mode", DEFAULT_POSTAL_CODE_MODE),
    }


def _split_navigation(items: Iterable[dict]) -> Generator[dict]:
    for item in items:
        if nav_positions := item.get("access", []):
            for nav_pos in nav_positions:
                yield item | {"access": nav_pos}
        else:
            single = item.copy()
            del single["access"]
            yield single


class AddressResult(CasaGeoResult):
    """
    Represents the result of a singular ``address()`` query.

    :meta private:
    """

    def dataframe(
        self,
        id_: Any | None = None,
        *,
        address_details: bool = False,
        coordinates: bool = False,
        match_quality: bool = False,
        error_info: bool = False,
    ) -> GeoDataFrame:
        """
        Return the result as a GeoDataFrame.

        The shape of the resulting dataframe matches the result of the
        ``address()`` function, except that error information is only
        included when ``error_info`` is set to ``True``.

        Args:
            id_: Fixed identifier to be added to each row. Defaults to 1.
            address_details: Include additional address details in the result.
            coordinates: Include numeric coordinate columns in the result.
            match_quality: Include match quality scores in the result.
            error_info: Include error information in the result.

        Returns:
            ~geopandas.GeoDataFrame: The list of determined locations as
            a GeoDataFrame.
        """

        if id_ is None:
            id_ = 1

        data: list[dict] = []
        for index, item in enumerate(_split_navigation(self._data.get("items", [{}]))):
            data.append(row := {})

            address = item.get("address", {})
            scoring = item.get("scoring", {})

            if True:
                # fmt: off
                row["id"]               = id_
                row["subid"]            = index
                row["address"]          = item.get("title")
                row["resulttype"]       = item.get("resultType")
                row["position"]         = and_then(item.get("position"), dict_to_point)
                row["navigation"]       = and_then(item.get("access"), dict_to_point)
                row["distance"]         = item.get("distance")
                row["relevance"]        = scoring.get("queryScore")
                row["timestamp"]        = self._timestamp
                # fmt: on

            if address_details:
                # fmt: off
                row["postaladdress"]    = address.get("label")
                row["country"]          = address.get("countryName")
                row["countrycode"]      = address.get("countryCode")
                row["state"]            = address.get("state")
                row["statecode"]        = address.get("stateCode")
                row["county"]           = address.get("county")
                row["countycode"]       = address.get("countyCode")
                row["city"]             = address.get("city")
                row["district"]         = address.get("district")
                row["subdistrict"]      = address.get("subdistrict")
                row["street"]           = address.get("street")
                # row["streets"]          = address.get("streets")
                row["block"]            = address.get("block")
                row["subblock"]         = address.get("subblock")
                row["postalcode"]       = address.get("postalCode")
                row["housenumber"]      = address.get("houseNumber")
                row["building"]         = address.get("building")
                row["unit"]             = address.get("unit")
                # fmt: on

            if coordinates:
                position = item.get("position", {})
                access = item.get("access", {})
                # fmt: off
                row["position_longitude"]       = position.get("lng")
                row["position_latitude"]        = position.get("lat")
                row["navigation_longitude"]     = access.get("lng")
                row["navigation_latitude"]      = access.get("lat")
                # fmt: on

            if match_quality:
                score = scoring.get("fieldScore", {})
                # fmt: off
                row["mq_country"]       = score.get("country")
                row["mq_countrycode"]   = score.get("countryCode")
                row["mq_state"]         = score.get("state")
                row["mq_statecode"]     = score.get("stateCode")
                row["mq_county"]        = score.get("county")
                row["mq_countycode"]    = score.get("countyCode")
                row["mq_city"]          = score.get("city")
                row["mq_district"]      = score.get("district")
                row["mq_subdistrict"]   = score.get("subdistrict")
                row["mq_street"]        = _average(score.get("streets"))
                # row["mq_streets"]       = score.get("streets")
                row["mq_block"]         = score.get("block")
                row["mq_subblock"]      = score.get("subblock")
                row["mq_postalcode"]    = score.get("postalCode")
                row["mq_housenumber"]   = score.get("houseNumber")
                row["mq_building"]      = score.get("building")
                row["mq_unit"]          = score.get("unit")
                row["mq_placename"]     = score.get("placeName")
                row["mq_ontologyname"]  = score.get("ontologyName")
                # fmt: on

        if not data:
            return GeoDataFrame()

        df = GeoDataFrame(data, geometry="position", crs="EPSG:4326")

        if error_info:
            err = self.error()
            # fmt: off
            df["error_code"]        = getattr(err, "code", "generic") if err else None
            df["error_message"]     = str(err) if err else None
            # fmt: on

        return df


class PoiResult(CasaGeoResult):
    """
    Represents the result of a singular ``poi()`` query.

    :meta private:
    """

    def dataframe(
        self,
        id_: Any | None = None,
        *,
        address_details: bool = False,
        coordinates: bool = False,
        category_codes: bool = False,
        error_info: bool = False,
    ) -> GeoDataFrame:
        """
        Return the result as a GeoDataFrame.

        The shape of the resulting dataframe matches the result of the
        ``poi()`` function, except that error information is only
        included when ``error_info`` is set to ``True``.

        Args:
            id_: Fixed identifier to be added to each row. Defaults to 1.
            address_details: Include additional address details in the result.
            coordinates: Include numeric coordinate columns in the result.
            category_codes: Include category, chain and food type IDs in the result.
            error_info: Include error information in the result.

        Returns:
            ~geopandas.GeoDataFrame: The list of determined locations as
            a GeoDataFrame.
        """

        if id_ is None:
            id_ = 1

        data: list[dict] = []
        for index, item in enumerate(_split_navigation(self._data.get("items", [{}]))):
            data.append(row := {})

            address = item.get("address", {})

            if True:
                # fmt: off
                row["id"]               = id_
                row["subid"]            = index
                row["title"]            = item.get("title")
                row["resulttype"]       = item.get("resultType")
                row["position"]         = and_then(item.get("position"), dict_to_point)
                row["navigation"]       = and_then(item.get("access"), dict_to_point)
                row["distance"]         = item.get("distance")
                row["timestamp"]        = self._timestamp
                # fmt: on

            if address_details:
                # fmt: off
                row["postaladdress"]    = address.get("label")
                row["country"]          = address.get("countryName")
                row["countrycode"]      = address.get("countryCode")
                row["state"]            = address.get("state")
                row["statecode"]        = address.get("stateCode")
                row["county"]           = address.get("county")
                row["countycode"]       = address.get("countyCode")
                row["city"]             = address.get("city")
                row["district"]         = address.get("district")
                row["subdistrict"]      = address.get("subdistrict")
                row["street"]           = address.get("street")
                row["streets"]          = address.get("streets")
                row["block"]            = address.get("block")
                row["subblock"]         = address.get("subblock")
                row["postalcode"]       = address.get("postalCode")
                row["housenumber"]      = address.get("houseNumber")
                row["building"]         = address.get("building")
                row["unit"]             = address.get("unit")
                # fmt: on

            if coordinates:
                position = item.get("position", {})
                access = item.get("access", {})
                # fmt: off
                row["position_longitude"]       = position.get("lng")
                row["position_latitude"]        = position.get("lat")
                row["navigation_longitude"]     = access.get("lng")
                row["navigation_latitude"]      = access.get("lat")
                # fmt: on

            if category_codes:
                # fmt: off
                row["here_categories"]  = and_then(item.get("categories"), lambda cs: [c["id"] for c in cs])
                row["here_chains"]      = and_then(item.get("chains"),     lambda cs: [c["id"] for c in cs])
                row["here_foodtypes"]   = and_then(item.get("foodTypes"),  lambda cs: [c["id"] for c in cs])
                # fmt: on

        if not data:
            return GeoDataFrame()

        df = GeoDataFrame(data, geometry="position", crs="EPSG:4326")

        if error_info:
            err = self.error()
            # fmt: off
            df["error_code"]        = getattr(err, "code", "generic") if err else None
            df["error_message"]     = str(err) if err else None
            # fmt: on

        return df

    # https://www.here.com/docs/bundle/geocoding-and-search-api-developer-guide/page/topics-places/places-category-system-full.html
    def category_dataframe(self) -> DataFrame:
        """
        Returns a DataFrame containing category information about the search results.
        """
        data: list[dict] = []
        for index, item in enumerate(self._data.get("items", [])):
            for category in item.get("categories", []):
                data.append(row := {})
                # fmt: off
                row["subid"]                = index
                row["category_code"]        = category.get("id")
                row["category_name"]        = category.get("name")
                row["category_isprimary"]   = category.get("primary", False)
                # fmt: on

        return DataFrame(data)

    def contact_dataframe(self) -> DataFrame:
        """
        Returns a DataFrame containing contact information about the search results.
        """
        data: list[dict] = []
        for index, item in enumerate(self._data.get("items", [])):
            for contact_map in item.get("contacts", []):
                for contact_type, contact_info_list in contact_map.items():
                    for contact_info in contact_info_list:
                        data.append(row := {})
                        categories = contact_info.get("categories")
                        # fmt: off
                        row["subid"]                = index
                        row["contact_type"]         = contact_type
                        row["contact_label"]        = contact_info.get("label")
                        row["contact_value"]        = contact_info.get("value")
                        row["contact_categories"]   = [ct["id"] for ct in categories] if categories is not None else None  # type: ignore[assignment]
                        # fmt: on

        return DataFrame(data)

    # TODO: Opening hours information dataframe method.


def address(
    client: CasaGeoClient,
    queries: DataFrame,
    defaults: dict | None = None,
    *,
    address_details: bool = False,
    coordinates: bool = False,
    match_quality: bool = False,
) -> GeoDataFrame:
    """
    Geocode addresses.

    See :ref:`coder-address-queries` in the module documentation.

    Args:
        client (CasaGeoClient): The client object authorizing these queries.
        queries (~pandas.DataFrame): The dataframe of queries.
        defaults: An optional dict of default values for missing input columns.
        address_details: Include additional address details in the result.
        coordinates: Include numeric coordinate columns in the result.
        match_quality: Include match quality scores in the result.

    Returns:
        ~geopandas.GeoDataFrame: The list of results as an EPSG:4326
        GeoDataFrame. The shape is described under
        :ref:`coder-address-output-columns` in the module documentation.

        The geometry column of the dataframe is the ``position`` column.
        If you want to work with navigation points instead, change it to
        the ``navigation`` column instead.

    Raises:
        InsufficientCreditsError: If the account does not have enough credits.
        CasaGeoError: If the request could not be executed for another reason.
    """
    df = address_result(
        client,
        queries,
        defaults,
        address_details=address_details,
        coordinates=coordinates,
        match_quality=match_quality,
    ).dataframe()
    return cast(GeoDataFrame, df)


def address_result(
    client: CasaGeoClient,
    queries: DataFrame,
    defaults: dict | None = None,
    *,
    address_details: bool = False,
    coordinates: bool = False,
    match_quality: bool = False,
) -> MultiResult:
    """:meta private:"""

    fallbacks = [defaults] if defaults else []
    fallbacks.append(prefs := {})
    if (language := client.preferred_language) is not None:
        prefs["language"] = language
    if (political_view := client.preferred_political_view) is not None:
        prefs["political_view"] = political_view

    ids = queries.get("id", queries.index).to_list()
    options = {
        "address_details": address_details,
        "coordinates": coordinates,
        "match_quality": match_quality,
    }
    queryspecs = [
        {
            "address": q.get("address"),
            "country": q.get("country"),
            "state": q.get("state"),
            "county": q.get("county"),
            "city": q.get("city"),
            "district": q.get("district"),
            "street": q.get("street"),
            "housenumber": q.get("housenumber"),
            "postalcode": q.get("postalcode"),
            "position": and_then(getpoint(q, "position"), point_xy),
            **_coder_params(q),
        }
        for q in to_records(queries, *fallbacks)
    ]

    json = _apiv2.address(client._httpxclient, queryspecs, options)
    return MultiResult(json=json, ids=ids, options=options, result_type=AddressResult)


def poi(
    client: CasaGeoClient,
    queries: DataFrame,
    defaults: dict | None = None,
    *,
    address_details: bool = False,
    coordinates: bool = False,
    category_codes: bool = False,
) -> GeoDataFrame:
    """
    Search for points of interest (POI) around given positions.

    See :ref:`coder-poi-queries` in the module documentation.

    Args:
        client (CasaGeoClient): The client object authorizing these queries.
        queries (~pandas.DataFrame): The dataframe of queries.
        defaults: An optional dict of default values for missing input columns.
        address_details: Include additional address details in the result.
        coordinates: Include numeric coordinate columns in the result.
        category_codes: Include HERE category, chain and food type identifiers in the result.

    Returns:
        ~geopandas.GeoDataFrame: The list of results as an EPSG:4326
        GeoDataFrame. The shape is described under
        :ref:`coder-poi-output-columns` in the module documentation.

        The geometry column of the dataframe is the ``position`` column.
        If you want to work with navigation points instead, change it to
        the ``navigation`` column instead.

    Raises:
        InsufficientCreditsError: If the account does not have enough credits.
        CasaGeoError: If the request could not be executed for another reason.
    """
    df = poi_result(
        client,
        queries,
        defaults,
        address_details=address_details,
        coordinates=coordinates,
        category_codes=category_codes,
    ).dataframe()
    return cast(GeoDataFrame, df)


def poi_result(
    client: CasaGeoClient,
    queries: DataFrame,
    defaults: dict | None = None,
    *,
    address_details: bool = False,
    coordinates: bool = False,
    category_codes: bool = False,
) -> MultiResult:
    """:meta private:"""

    fallbacks = [defaults] if defaults else []
    fallbacks.append(prefs := {})
    if (language := client.preferred_language) is not None:
        prefs["language"] = language
    if (political_view := client.preferred_political_view) is not None:
        prefs["political_view"] = political_view

    ids = queries.get("id", queries.index).to_list()
    options = {
        "address_details": address_details,
        "coordinates": coordinates,
        "category_codes": category_codes,
    }
    queryspecs = [
        {
            "position": and_then(getpoint(q, "position"), point_xy),
            **_coder_params(q),
        }
        for q in to_records(queries, *fallbacks)
    ]

    json = _apiv2.poi(client._httpxclient, queryspecs, options)
    return MultiResult(json=json, ids=ids, options=options, result_type=PoiResult)


def _main(args: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Provides geocoding operations.",
        allow_abbrev=False,
    )
    subparsers = parser.add_subparsers(
        title="subcommands",
        required=True,
        metavar="COMMAND",
    )

    # Subcommand Parent Parser

    parent_parser = argparse.ArgumentParser(add_help=False, conflict_handler="resolve")
    common_params = parent_parser.add_argument_group(title="common parameters")
    common_params.add_argument(
        "--language",
        type=_util.cli_ietf_bcp47_language_tag,
        help="the preferred language for the response",
    )
    common_params.add_argument(
        "--political-view",
        type=_util.cli_iso3166_alpha3_country_code,
        help="the political view of the query regarding disputed territories",
    )
    common_params.add_argument(
        "--limit",
        type=_util.cli_positive_int,
        help="limit on the number of search results (max 100)",
    )
    common_params.add_argument(
        "--countries",
        type=_util.cli_iso3166_alpha3_country_code_list,
        help="limits the search to the specified countries",
    )
    common_params.add_argument(
        "--address-names-mode",
        choices=_consts.ADDRESS_NAMES_MODES,
        help="the address names mode",
    )
    common_params.add_argument(
        "--postal-code-mode",
        choices=_consts.POSTAL_CODE_MODES,
        help="the postal code mode",
    )
    common_params.add_argument(
        "--with-id",
        help="sets the value of the 'id' column",
        metavar="ID",
        dest="id",
    )

    # Address Subcommand

    address_parser = subparsers.add_parser(
        "address",
        help="geocode an address",
        description="Geocode an address using a free-form string or structured fields.",
        parents=[parent_parser],
        allow_abbrev=False,
    )
    address_parser.set_defaults(command=address)

    address_params = address_parser.add_argument_group(title="address parameters")
    address_params.add_argument(
        "address",
        nargs="?",
        help="free-form address string",
    )
    address_params.add_argument("--country", help="the name of a country")
    address_params.add_argument("--state", help="the name of a state or province")
    address_params.add_argument("--county", help="the name of a county")
    address_params.add_argument("--city", help="the name of a city")
    address_params.add_argument("--district", help="the name of a district")
    address_params.add_argument("--street", help="the name of a street")
    address_params.add_argument("--housenumber", help="a house number")
    address_params.add_argument("--postalcode", help="a postal code")
    address_params.add_argument(
        "--position",
        type=_util.cli_latlong_point,
        help="the search center position",
    )

    address_dfparams = address_parser.add_argument_group(title="dataframe parameters")
    address_dfparams.add_argument(
        "--with-address-details",
        action="store_true",
        help="include detailed address components in the output",
    )
    address_dfparams.add_argument(
        "--with-coordinates",
        action="store_true",
        help="include latitude and longitude in the output",
    )
    address_dfparams.add_argument(
        "--with-match-quality",
        action="store_true",
        help="include match quality information in the output",
    )

    # POI Subcommand

    poi_parser = subparsers.add_parser(
        "poi",
        help="search for points of interest",
        description="Search for points of interest (POI) around a given position.",
        parents=[parent_parser],
        allow_abbrev=False,
    )
    poi_parser.set_defaults(command=poi)

    poi_params = poi_parser.add_argument_group(title="poi parameters")
    poi_params.add_argument(
        "position",
        type=_util.cli_latlong_point,
        help="the search center position",
    )

    poi_dfparams = poi_parser.add_argument_group(title="dataframe parameters")
    poi_dfparams.add_argument(
        "--with-address-details",
        action="store_true",
        help="include detailed address components in the output",
    )
    poi_dfparams.add_argument(
        "--with-coordinates",
        action="store_true",
        help="include latitude and longitude in the output",
    )
    poi_dfparams.add_argument(
        "--with-category-codes",
        action="store_true",
        help="include HERE category codes in the output",
    )

    # Main Function Body

    options = parser.parse_args(args)
    api_key = os.getenv("CASAGEOTOOLS_API_KEY") or sys.exit(
        "Please specify an API key in the environment variable CASAGEOTOOLS_API_KEY"
    )

    client = CasaGeoClient(api_key)
    queries = DataFrame([{k: v for k, v in vars(options).items() if v is not None}])
    kwargs = {
        k.removeprefix("with_"): v
        for k, v in vars(options).items()
        if k.startswith("with_")
    }
    results = options.command(client, queries, **kwargs)
    results.to_csv(sys.stdout, sep=";", index=False)


if __name__ == "__main__":
    try:
        _main()
    except CasaGeoError as e:
        sys.exit(f"{e.__class__.__name__}: {e}")
