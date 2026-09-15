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

"""
This module provides spatial routing operations.
"""

import argparse
import logging
import math
import os
import sys
from collections.abc import Collection, Hashable, Mapping, Sequence
from datetime import datetime
from enum import StrEnum
from typing import Any, Final, cast

from geopandas import GeoDataFrame
from pandas import DataFrame
from shapely import (
    MultiLineString,
    MultiPolygon,
)

from casageo.tools import (
    CasaGeoClient,
    CasaGeoError,
    UnitSystem,
    _util,
)
from casageo.tools._types import CasaGeoResult, MultiResult
from casageo.tools._util import (
    and_then,
    delna,
    dict_to_point,
    duplicates,
    getpoint,
    iso_datetime,
    point_xy,
    split_if_str,
    to_records,
)

# Constants


class RangeType(StrEnum):
    TIME = "time"
    DISTANCE = "distance"


class RangeUnit(StrEnum):
    MINUTES = "minutes"
    METERS = "meters"


class TransportMode(StrEnum):
    CAR = "car"
    PEDESTRIAN = "pedestrian"
    BICYCLE = "bicycle"
    TRUCK = "truck"


class RoutingMode(StrEnum):
    FAST = "fast"
    SHORT = "short"


class DirectionType(StrEnum):
    OUTGOING = "outgoing"
    INCOMING = "incoming"


class AvoidableFeature(StrEnum):
    SEASONAL_CLOSURE = "seasonalClosure"
    TOLL_ROAD = "tollRoad"
    CONTROLLED_ACCESS_HIGHWAY = "controlledAccessHighway"
    FERRY = "ferry"
    CAR_SHUTTLE_TRAIN = "carShuttleTrain"
    TUNNEL = "tunnel"
    DIRT_ROAD = "dirtRoad"
    # U-Turns is not supported for pedestrian, bicycle and scooter transport modes.
    U_TURNS = "uTurns"


RANGE_TYPE_BY_UNIT: Final[Mapping[str, RangeType]] = {
    RangeUnit.MINUTES: RangeType.TIME,
    RangeUnit.METERS: RangeType.DISTANCE,
}

RANGE_COEFFICIENT_BY_UNIT: Final[Mapping[str, int]] = {
    RangeUnit.MINUTES: 60,
    RangeUnit.METERS: 1,
}


MIN_ALTERNATIVES: Final[int] = 0
MAX_ALTERNATIVES: Final[int] = 6

# Spatial

DEFAULT_REQUEST_ID: Final[int] = 1
"""The default ID value for single-shot requests."""

DEFAULT_LANGUAGE: Final[str] = "en-US"
"""The default language used in the results."""

DEFAULT_UNIT_SYSTEM: Final[UnitSystem] = UnitSystem.METRIC
"""The default unit system used in the results."""

DEFAULT_TRANSPORT_MODE: Final[TransportMode] = TransportMode.CAR
"""The default transport mode."""

DEFAULT_ROUTING_MODE: Final[RoutingMode] = RoutingMode.FAST
"""The default routing mode."""

DEFAULT_DIRECTION: Final[DirectionType] = DirectionType.OUTGOING
"""The default routing direction."""

# Isolines

DEFAULT_RANGE_UNIT: Final[RangeUnit] = RangeUnit.MINUTES
"""The default unit for range values."""

RESULT_RANGE_UNIT_BY_TYPE: Final[Mapping[str, RangeUnit]] = {
    RangeType.TIME: RangeUnit.MINUTES,
    RangeType.DISTANCE: RangeUnit.METERS,
}
"""The unit for returned range values by type."""

# Routes

DEFAULT_ALTERNATIVES: Final[int] = 0
"""The default number of alternative routes to compute."""


_logger = logging.getLogger(__name__)


def _isolines_ranges_unit(
    q: Mapping[Hashable, Any], default: str | None = None
) -> str | None:
    if (ru := and_then(q.get("ranges_unit"), str)) is not None:
        return ru

    if (rt := and_then(q.get("range_type"), str)) is not None:
        return RESULT_RANGE_UNIT_BY_TYPE.get(rt, rt)

    return default


class IsolinesResult(CasaGeoResult):
    """
    Represents the result of a singular ``isolines()`` query.

    :meta private:
    """

    @staticmethod
    def _geometry(isoline: dict[str, Any]) -> MultiPolygon | None:
        try:
            polygons = isoline["polygons"]
        except KeyError:
            return None

        return MultiPolygon([
            (
                _util.flexpolyline_points(outer),
                [
                    _util.flexpolyline_points(inner)
                    for inner in polygon.get("inner", ())
                ],
            )
            for polygon in polygons
            if (outer := polygon.get("outer")) is not None
        ])

    @staticmethod
    def _range_type(isoline: dict[str, Any]) -> str | None:
        try:
            return isoline["range"]["type"]
        except KeyError:
            return None

    @staticmethod
    def _range_unit(isoline: dict[str, Any]) -> str | None:
        try:
            return RESULT_RANGE_UNIT_BY_TYPE[isoline["range"]["type"]]
        except KeyError:
            return None

    @staticmethod
    def _range_value(isoline: dict[str, Any]) -> float | None:
        try:
            value = float(isoline["range"]["value"])
        except KeyError:
            return None

        # We interpret range_values as minutes, while HERE interprets them as seconds.
        if (unit := IsolinesResult._range_unit(isoline)) is not None:
            value /= RANGE_COEFFICIENT_BY_UNIT.get(unit, 1)

        return value

    def dataframe(
        self,
        id_: Any | None = None,
        *,
        departure_info: bool = False,
        arrival_info: bool = False,
        error_info: bool = False,
    ) -> GeoDataFrame:
        """
        Return the result as a GeoDataFrame.

        The shape of the resulting dataframe matches the result of the
        ``isolines()`` function, except that error information is only
        included when ``error_info`` is set to ``True``.

        Args:
            id_: Fixed identifier to be added to each row. Defaults to 1.
            departure_info: Include additional info about the departure
                time and location.
            arrival_info: Include additional info about the arrival
                time and location.
            error_info: Include error information in the result.

        Returns:
            ~geopandas.GeoDataFrame: The list of computed isolines as a
            GeoDataFrame.
        """

        if id_ is None:
            id_ = DEFAULT_REQUEST_ID

        data: list[dict[str, Any]] = []
        for index, isoline in enumerate(self._data.get("isolines", [{}])):
            data.append(row := {})

            if True:
                # fmt: off
                row["id"]               = id_
                row["subid"]            = index
                row["geometry"]         = self._geometry(isoline)
                row["rangetype"]        = self._range_type(isoline)
                row["rangeunit"]        = self._range_unit(isoline)
                row["rangevalue"]       = self._range_value(isoline)
                row["timestamp"]        = self._timestamp
                # fmt: on

        if not data:
            return GeoDataFrame()

        # TODO: When elevation is returned, the CRS should be different (EPSG:4979 ?).
        df = GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")

        if departure_info:
            departure = self.departure_info() or {}
            # fmt: off
            df["departure_time"]            = departure.get("time")
            df["departure_placename"]       = departure.get("placename")
            df["departure_position"]        = departure.get("position")
            df["departure_displayposition"] = departure.get("displayposition")
            df["departure_queryposition"]   = departure.get("queryposition")
            # fmt: on

        if arrival_info:
            arrival = self.arrival_info() or {}
            # fmt: off
            df["arrival_time"]              = arrival.get("time")
            df["arrival_placename"]         = arrival.get("placename")
            df["arrival_position"]          = arrival.get("position")
            df["arrival_displayposition"]   = arrival.get("displayposition")
            df["arrival_queryposition"]     = arrival.get("queryposition")
            # fmt: on

        if error_info:
            err = self.error()
            # fmt: off
            df["error_code"]        = getattr(err, "code", "generic") if err else None
            df["error_message"]     = str(err) if err else None
            # fmt: on

        return df

    def has_departure_info(self) -> bool:
        """Return ``True`` if the API response includes departure information."""
        return "departure" in self._data

    def departure_info(self) -> dict[str, Any] | None:
        """
        Return departure information, if available.

        Returns:
            dict | None: Departure information as a ``dict``, or
            ``None`` if no departure information is available.

        Output Columns:
            Departure information includes the following values, all of
            which can be ``None``:

            time : datetime
                Timestamp representing the expected departure time.
            placename : str
                Name of the departure location.
            position : :class:`~shapely.Point`
                Resolved position of the departure location used for
                route calculation.
            displayposition : :class:`~shapely.Point`
                Position of a map marker referring to the departure
                location.
            queryposition : :class:`~shapely.Point`
                The original departure position specified in the
                request.
        """
        try:
            departure = self._data["departure"]
            place = departure["place"]
        except KeyError:
            return None
        return {
            "time": and_then(departure.get("time"), datetime.fromisoformat),
            "placename": place.get("name"),
            "position": and_then(place.get("location"), dict_to_point),
            "displayposition": and_then(place.get("displayLocation"), dict_to_point),
            "queryposition": and_then(place.get("originalLocation"), dict_to_point),
        }

    def has_arrival_info(self) -> bool:
        """Return ``True`` if the API response includes arrival information."""
        return "arrival" in self._data

    def arrival_info(self) -> dict[str, Any] | None:
        """
        Return arrival information, if available.

        Returns:
            dict | None: Arrival information as a ``dict``, or ``None``
            if no arrival information is available.

        Output Columns:
            Arrival information includes the following values, all of
            which can be ``None``:

            time : datetime
                Timestamp representing the expected arrival time.
            placename : str
                Name of the arrival location.
            position : :class:`~shapely.Point`
                Resolved position of the arrival location used for route
                calculation.
            displayposition : :class:`~shapely.Point`
                Position of a map marker referring to the arrival
                location.
            queryposition : :class:`~shapely.Point`
                The original arrival position specified in the request.
        """
        try:
            arrival = self._data["arrival"]
            place = arrival["place"]
        except KeyError:
            return None
        return {
            "time": and_then(arrival.get("time"), datetime.fromisoformat),
            "placename": place.get("name"),
            "position": and_then(place.get("location"), dict_to_point),
            "displayposition": and_then(place.get("displayLocation"), dict_to_point),
            "queryposition": and_then(place.get("originalLocation"), dict_to_point),
        }


class RoutesResult(CasaGeoResult):
    """
    Represents the result of a singular ``routes()`` query.

    :meta private:
    """

    @staticmethod
    def _geometry(route: dict[str, Any]) -> MultiLineString | None:
        try:
            return MultiLineString([
                _util.flexpolyline_points(section["polyline"])
                for section in route["sections"]
            ])
        except KeyError:
            return None

    @staticmethod
    def _length(route: dict[str, Any]) -> float:
        return sum(
            section.get("summary", {}).get("length", math.nan)
            for section in route.get("sections", [])
        )

    @staticmethod
    def _duration(route: dict[str, Any]) -> float:
        duration_seconds = sum(
            section.get("summary", {}).get("duration", math.nan)
            for section in route.get("sections", [])
        )
        return duration_seconds / 60.0

    def dataframe(
        self,
        id_: Any | None = None,
        *,
        departure_info: bool = False,
        arrival_info: bool = False,
        error_info: bool = False,
    ) -> GeoDataFrame:
        """
        Return the result as a GeoDataFrame.

        The shape of the resulting dataframe matches the result of the
        ``routes()`` function, except that error information is only
        included when ``error_info`` is set to ``True``.

        Args:
            id_: Fixed identifier to be added to each row. Defaults to 1.
            departure_info: Include additional info about the departure
                time and location of each route.
            arrival_info: Include additional info about the arrival
                time and location of each route.
            error_info: Include error information in the result.

        Returns:
            ~geopandas.GeoDataFrame: The list of computed routes as a
            GeoDataFrame.
        """

        if id_ is None:
            id_ = DEFAULT_REQUEST_ID

        data: list[dict[str, Any]] = []
        for index, route in enumerate(self._data.get("routes", [{}])):
            data.append(row := {})

            if True:
                # fmt: off
                row["id"]                           = id_
                row["subid"]                        = index
                row["geometry"]                     = self._geometry(route)
                row["length"]                       = self._length(route)
                row["duration"]                     = self._duration(route)
                row["timestamp"]                    = self._timestamp
                # fmt: on

            if departure_info:
                departure = self.departure_info(index) or {}
                # fmt: off
                row["departure_time"]               = departure.get("time")
                row["departure_placename"]          = departure.get("placename")
                row["departure_position"]           = departure.get("position")
                row["departure_displayposition"]    = departure.get("displayposition")
                row["departure_queryposition"]      = departure.get("queryposition")
                # fmt: on

            if arrival_info:
                arrival = self.arrival_info(index) or {}
                # fmt: off
                row["arrival_time"]                 = arrival.get("time")
                row["arrival_placename"]            = arrival.get("placename")
                row["arrival_position"]             = arrival.get("position")
                row["arrival_displayposition"]      = arrival.get("displayposition")
                row["arrival_queryposition"]        = arrival.get("queryposition")
                # fmt: on

        if not data:
            return GeoDataFrame()

        # TODO: When elevation is returned, the CRS should be different (EPSG:4979 ?).
        df = GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")

        if error_info:
            err = self.error()
            # fmt: off
            df["error_code"]        = getattr(err, "code", "generic") if err else None
            df["error_message"]     = str(err) if err else None
            # fmt: on

        return df

    def departure_info(self, route: int, section: int = 0) -> dict[str, Any] | None:
        """
        Returns departure information for a specific route or section.

        Args:
            route: Index of the route in the result list.
            section: Index of the section within the route, defaults to
                the first section.

        Returns:
            dict | None: Departure information as a ``dict``, or
            ``None`` if no such information exists for the specified
            route and section.

        Output Columns:
            Departure information includes the following values, all of
            which can be ``None``:

            time : datetime
                Timestamp representing the expected departure time.
            placename : str
                Name of the departure location.
            position : :class:`~shapely.Point`
                Resolved position of the departure location used for
                route calculation.
            displayposition : :class:`~shapely.Point`
                Position of a map marker referring to the departure
                location.
            queryposition : :class:`~shapely.Point`
                The original departure position specified in the
                request.
        """
        try:
            departure = self._data["routes"][route]["sections"][section]["departure"]
            place = departure["place"]
        except (KeyError, IndexError):
            return None
        return {
            "time": and_then(departure.get("time"), datetime.fromisoformat),
            "placename": place.get("name"),
            "position": and_then(place.get("location"), dict_to_point),
            "displayposition": and_then(place.get("displayLocation"), dict_to_point),
            "queryposition": and_then(place.get("originalLocation"), dict_to_point),
        }

    def arrival_info(self, route: int, section: int = -1) -> dict[str, Any] | None:
        """
        Returns arrival information for a specific route or section.

        Args:
            route: Index of the route in the result list.
            section: Index of the section within the route, defaults to
                the last section.

        Returns:
            dict | None: Arrival information as a ``dict``, or ``None``
            if no such information exists for the specified route and
            section.

        Output Columns:
            Arrival information includes the following values, all of
            which can be ``None``:

            time : datetime
                Timestamp representing the expected arrival time.
            placename : str
                Name of the arrival location.
            position : :class:`~shapely.Point`
                Resolved position of the arrival location used for route
                calculation.
            displayposition : :class:`~shapely.Point`
                Position of a map marker referring to the arrival
                location.
            queryposition : :class:`~shapely.Point`
                The original arrival position specified in the request.
        """
        try:
            arrival = self._data["routes"][route]["sections"][section]["arrival"]
            place = arrival["place"]
        except (KeyError, IndexError):
            return None
        return {
            "time": and_then(arrival.get("time"), datetime.fromisoformat),
            "placename": place.get("name"),
            "position": and_then(place.get("location"), dict_to_point),
            "displayposition": and_then(place.get("displayLocation"), dict_to_point),
            "queryposition": and_then(place.get("originalLocation"), dict_to_point),
        }


def isolines(
    client: CasaGeoClient,
    queries: DataFrame,
    defaults: Mapping[str, Any] | None = None,
    *,
    departure_info: bool = False,
    arrival_info: bool = False,
) -> GeoDataFrame:
    """
    Calculate isolines around locations.

    See :ref:`spatial-isoline-queries` in the module documentation.

    Args:
        client (CasaGeoClient): The client object authorizing these queries.
        queries (~pandas.DataFrame): The dataframe of queries.
        defaults: An optional mapping of default values for missing input columns.
        departure_info: Include additional information about the departure time and location.
        arrival_info: Include additional information about the arrival time and location.

    Returns:
        ~geopandas.GeoDataFrame: The list of results as an EPSG:4326
        GeoDataFrame. The shape is described under
        :ref:`spatial-isoline-output-columns` in the module
        documentation.

        The geometry column of the dataframe is the ``geometry`` column.

    Raises:
        InsufficientCreditsError: If the account does not have enough credits.
        CasaGeoError: If the request could not be executed for another reason.
    """
    df = isolines_result(
        client,
        queries,
        defaults,
        departure_info=departure_info,
        arrival_info=arrival_info,
    ).dataframe()
    return cast(GeoDataFrame, df)


def isolines_result(
    client: CasaGeoClient,
    queries: DataFrame,
    defaults: Mapping[str, Any] | None = None,
    *,
    departure_info: bool = False,
    arrival_info: bool = False,
) -> MultiResult[IsolinesResult]:
    """:meta private:"""

    fallbacks = [defaults] if defaults else []

    ids = queries.get("id", queries.index).to_list()
    if any(dups := duplicates(ids)):
        raise ValueError(f"Duplicate ID values: {dups}")

    options = {
        "departure_info": departure_info,
        "arrival_info": arrival_info,
    }

    json = client.request(
        "POST",
        "/api/v2/isolines",
        json={
            "options": options,
            "queries": [
                delna({
                    "position": and_then(getpoint(q, "position"), point_xy),
                    "ranges": and_then(q.get("ranges"), split_if_str(",")),
                    "ranges_unit": _isolines_ranges_unit(q, DEFAULT_RANGE_UNIT),
                    "direction": q.get("direction", DEFAULT_DIRECTION),
                    "language": q.get("language", client.preferred_language),
                    "unit_system": q.get("unit_system", client.preferred_unit_system),
                    "transport_mode": q.get("transport_mode", DEFAULT_TRANSPORT_MODE),
                    "routing_mode": q.get("routing_mode", DEFAULT_ROUTING_MODE),
                    "departure_time": q.get("departure_time"),
                    "arrival_time": q.get("arrival_time"),
                    "traffic": q.get("traffic"),
                    "avoid_features": and_then(
                        q.get("avoid_features"), split_if_str(",")
                    ),
                    "exclude_countries": and_then(
                        q.get("exclude_countries"), split_if_str(",")
                    ),
                })
                for q in to_records(queries, *fallbacks)
            ],
        },
    )

    _logger.debug("Isolines Response: %r", json)

    return MultiResult(json=json, ids=ids, options=options, result_type=IsolinesResult)


def routes(
    client: CasaGeoClient,
    queries: DataFrame,
    defaults: Mapping[str, Any] | None = None,
    *,
    departure_info: bool = False,
    arrival_info: bool = False,
) -> GeoDataFrame:
    """
    Calculate routes between two locations.

    See :ref:`spatial-routing-queries` in the module documentation.

    Args:
        client (CasaGeoClient): The client object authorizing these queries.
        queries (~pandas.DataFrame): The dataframe of queries.
        defaults: An optional mapping of default values for missing input columns.
        departure_info: Include additional information about the departure time and location.
        arrival_info: Include additional information about the arrival time and location.

    Returns:
        ~geopandas.GeoDataFrame: The list of results as an EPSG:4326
        GeoDataFrame. The shape is described under
        :ref:`spatial-routing-output-columns` in the module
        documentation.

        The geometry column of the dataframe is the ``geometry`` column.

    Raises:
        InsufficientCreditsError: If the account does not have enough credits.
        CasaGeoError: If the request could not be executed for another reason.
    """
    df = routes_result(
        client,
        queries,
        defaults,
        departure_info=departure_info,
        arrival_info=arrival_info,
    ).dataframe()
    return cast(GeoDataFrame, df)


def routes_result(
    client: CasaGeoClient,
    queries: DataFrame,
    defaults: Mapping[str, Any] | None = None,
    *,
    departure_info: bool = False,
    arrival_info: bool = False,
) -> MultiResult[RoutesResult]:
    """:meta private:"""

    fallbacks = [defaults] if defaults else []

    ids = queries.get("id", queries.index).to_list()
    if any(dups := duplicates(ids)):
        raise ValueError(f"Duplicate ID values: {dups}")

    options = {
        "departure_info": departure_info,
        "arrival_info": arrival_info,
    }

    json = client.request(
        "POST",
        "/api/v2/routes",
        json={
            "options": options,
            "queries": [
                delna({
                    "origin": and_then(getpoint(q, "origin"), point_xy),
                    "destination": and_then(getpoint(q, "destination"), point_xy),
                    "alternatives": q.get("alternatives", DEFAULT_ALTERNATIVES),
                    "language": q.get("language", client.preferred_language),
                    "unit_system": q.get("unit_system", client.preferred_unit_system),
                    "transport_mode": q.get("transport_mode", DEFAULT_TRANSPORT_MODE),
                    "routing_mode": q.get("routing_mode", DEFAULT_ROUTING_MODE),
                    "departure_time": q.get("departure_time"),
                    "arrival_time": q.get("arrival_time"),
                    "traffic": q.get("traffic"),
                    "avoid_features": and_then(
                        q.get("avoid_features"), split_if_str(",")
                    ),
                    "exclude_countries": and_then(
                        q.get("exclude_countries"), split_if_str(",")
                    ),
                })
                for q in to_records(queries, *fallbacks)
            ],
        },
    )

    _logger.debug("Routing Response: %r", json)

    return MultiResult(json=json, ids=ids, options=options, result_type=RoutesResult)


def routesvia(
    client: CasaGeoClient,
    waypoints: DataFrame,
    *,
    alternatives: int = DEFAULT_ALTERNATIVES,
    transport_mode: str = DEFAULT_TRANSPORT_MODE,
    routing_mode: str = DEFAULT_ROUTING_MODE,
    departure_time: datetime | str | None = None,
    arrival_time: datetime | str | None = None,
    avoid_features: Collection[str] = (),
    exclude_countries: Collection[str] = (),
    with_departure_info: bool = False,
    with_arrival_info: bool = False,
    with_id: Any = DEFAULT_REQUEST_ID,
) -> GeoDataFrame:
    df = routesvia_result(
        client,
        waypoints,
        alternatives=alternatives,
        transport_mode=transport_mode,
        routing_mode=routing_mode,
        departure_time=departure_time,
        arrival_time=arrival_time,
        avoid_features=avoid_features,
        exclude_countries=exclude_countries,
        with_departure_info=with_departure_info,
        with_arrival_info=with_arrival_info,
        with_id=with_id,
    ).dataframe()
    return cast(GeoDataFrame, df)


def routesvia_result(
    client: CasaGeoClient,
    waypoints: DataFrame,
    *,
    alternatives: int = DEFAULT_ALTERNATIVES,
    transport_mode: str = DEFAULT_TRANSPORT_MODE,
    routing_mode: str = DEFAULT_ROUTING_MODE,
    departure_time: datetime | str | None = None,
    arrival_time: datetime | str | None = None,
    avoid_features: Collection[str] = (),
    exclude_countries: Collection[str] = (),
    with_departure_info: bool = False,
    with_arrival_info: bool = False,
    with_id: Any = DEFAULT_REQUEST_ID,
) -> MultiResult[RoutesResult]:
    """:meta private:"""

    options = delna({
        "alternatives": alternatives,
        "transport_mode": transport_mode,
        "routing_mode": routing_mode,
        "departure_time": and_then(departure_time, iso_datetime),
        "arrival_time": and_then(arrival_time, iso_datetime),
        "avoid_features": list(avoid_features),
        "exclude_countries": list(exclude_countries),
    })

    points = [
        delna({
            "position": and_then(getpoint(wp, "position"), point_xy),
            # Generation of result IDs is still unsolved...
            # "isorigin": and_then(wp.get("isorigin"), bool),
            "displayposition": and_then(getpoint(wp, "displayposition"), point_xy),
            "streetposition": and_then(getpoint(wp, "streetposition"), point_xy),
            "placename": and_then(wp.get("placename"), str),
            "course": and_then(wp.get("course"), int),
            "radius": and_then(wp.get("radius"), int),
            "snap": and_then(wp.get("snap"), bool),
        })
        for wp in to_records(waypoints)
    ]

    json = client.request(
        "POST",
        "/api/v2/routesvia",
        json={
            "options": options,
            "waypoints": points,
        },
    )

    _logger.debug("RoutesVia Response: %r", json)

    return MultiResult(
        json=json,
        ids=[with_id],
        options={
            "departure_info": with_departure_info,
            "arrival_info": with_arrival_info,
        },
        result_type=RoutesResult,
    )


def _main(args: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Provides spatial calculations such as routing and isolines.",
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
        "--unit-system",
        default=DEFAULT_UNIT_SYSTEM,
        choices=list(UnitSystem),
        help="the system of units to use for localized quantities",
    )
    common_params.add_argument(
        "--transport-mode",
        default=DEFAULT_TRANSPORT_MODE,
        choices=list(TransportMode),
        help="the mode of transport used for routing",
    )
    common_params.add_argument(
        "--routing-mode",
        default=DEFAULT_ROUTING_MODE,
        choices=list(RoutingMode),
        help="whether to prefer 'fast' or 'short' routes",
    )
    common_params.add_argument(
        "--departure-time",
        type=_util.cli_datetime,
        help="the date and time of departure for time-dependent routing",
    )
    common_params.add_argument(
        "--arrival-time",
        type=_util.cli_datetime,
        help="the date and time of arrival for time-dependent routing",
    )
    common_params.add_argument(
        "--traffic",
        action="store_true",
        help="consider traffic data during routing",
    )
    common_params.add_argument(
        "--avoid-features",
        type=_util.cli_avoidable_feature_list,
        help="route features to avoid during routing",
    )
    common_params.add_argument(
        "--exclude-countries",
        type=_util.cli_iso3166_alpha3_country_code_list,
        help="countries to exclude from routing",
    )
    common_params.add_argument(
        "--with-id",
        help="sets the value of the 'id' column",
        metavar="ID",
        dest="id",
    )

    # Isolines Subcommand

    isolines_parser = subparsers.add_parser(
        "isolines",
        help="calculate isolines for a given location and time/distance",
        description="Calculate isolines around a location.",
        parents=[parent_parser],
        allow_abbrev=False,
    )
    isolines_parser.set_defaults(command=isolines)

    isolines_params = isolines_parser.add_argument_group(title="isolines parameters")
    isolines_params.add_argument(
        "position",
        type=_util.cli_latlong_point,
        help="the location for which to calculate isolines",
    )
    isolines_params.add_argument(
        "ranges",
        nargs="+",
        type=float,
        help="the ranges for which to calculate isolines",
    )
    isolines_params.add_argument(
        "--unit",
        default=DEFAULT_RANGE_UNIT,
        choices=list(RangeUnit),
        help="the unit of the range values",
        dest="ranges_unit",
    )
    isolines_params.add_argument(
        "--direction",
        default=DEFAULT_DIRECTION,
        choices=list(DirectionType),
        help="the direction of travel relative to the center point",
    )

    isolines_dfparams = isolines_parser.add_argument_group(title="dataframe parameters")
    isolines_dfparams.add_argument(
        "--with-departure-info",
        action="store_true",
        help="include departure information in the results",
    )
    isolines_dfparams.add_argument(
        "--with-arrival-info",
        action="store_true",
        help="include arrival information in the results",
    )

    # Routes Subcommand

    routes_parser = subparsers.add_parser(
        "routes",
        help="calculate routes between two locations",
        description="Calculate routes between an origin and a destination.",
        parents=[parent_parser],
        allow_abbrev=False,
    )
    routes_parser.set_defaults(command=routes)

    routes_params = routes_parser.add_argument_group(title="routes parameters")
    routes_params.add_argument(
        "origin",
        type=_util.cli_latlong_point,
        help="the starting point for the route",
    )
    routes_params.add_argument(
        "destination",
        type=_util.cli_latlong_point,
        help="the destination point for the route",
    )
    routes_params.add_argument(
        "--alternatives",
        default=DEFAULT_ALTERNATIVES,
        type=_util.cli_non_negative_int,
        help="number of alternate routes to calculate",
    )

    routes_dfparams = routes_parser.add_argument_group(title="dataframe parameters")
    routes_dfparams.add_argument(
        "--with-departure-info",
        action="store_true",
        help="include departure information in the results",
    )
    routes_dfparams.add_argument(
        "--with-arrival-info",
        action="store_true",
        help="include arrival information in the results",
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
