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
This module provides operations for logistical calculations.
"""

import logging
from collections.abc import Collection, Sequence
from datetime import datetime, timedelta
from typing import Any, Final, cast

from geopandas import GeoDataFrame
from pandas import DataFrame

from casageo.tools import CasaGeoClient, _apiv2
from casageo.tools._types import CasaGeoResult, MultiResult
from casageo.tools._util import (
    and_then,
    delna,
    dict_to_point,
    enlist_if_str,
    getpoint,
    iso_datetime,
    minutes_to_seconds,
    point_xy,
    to_records,
)

AVOIDABLE_FEATURES: Final[Sequence[str]] = [
    "tollroad",
    "motorway",
    "boatFerry",
    "railFerry",
    "tunnel",
    "dirtRoad",
    "park",
    "uTurns",
]

TRANSPORT_MODES: Final[Sequence[str]] = [
    "car",
    "pedestrian",
    "bicycle",
    "truck",
]

HAZARDOUS_CARGO_TYPES: Final[Sequence[str]] = [
    "explosive",
    "gas",
    "flammable",
    "combustible",
    "organic",
    "poison",
    "radioActive",
    "corrosive",
    "poisonousInhalation",
    "harmfulToWater",
    "other",
]


_logger = logging.getLogger(__name__)


def _fcs_errmsg(fcs: list[dict[str, Any]]) -> str:
    return ", ".join(f"FAILED {f.get('constraint')!r} ({f.get('reason')})" for f in fcs)


class TSPResult(CasaGeoResult):
    """
    Represents the result of a TSP (Traveling Salesman Problem) calculation.

    :meta private:
    """

    def dataframe(
        self,
        id_: Any | None = None,
        *,
        coordinates: bool = False,
        error_info: bool = False,
    ) -> GeoDataFrame:
        if id_ is None:
            id_ = 1

        if x := self._data.get("results"):
            result = x[0]
            waypoints = result.get("waypoints", [{}])
            interconnections = [{}, *result.get("interconnections", [])]
        elif x := self._data.get("warnings"):
            result = x[0]
            waypoints = result.get("outOfSequenceWaypoints", [{}])
            interconnections = []
        else:
            result = {}
            waypoints = [{}]
            interconnections = []

        data: list[dict[str, Any]] = []
        for index, item in enumerate(waypoints):
            data.append(row := {})

            try:
                conn = interconnections[index]
            except IndexError:
                conn = {}

            if True:
                # fmt: off
                row["id"]                   = id_
                row["subid"]                = index
                row["clusterid"]            = item.get("cluster")
                row["name"]                 = item.get("id")
                row["navigation"]           = dict_to_point(item)
                row["arrival_time"]         = item.get("estimatedArrival")
                row["departure_time"]       = item.get("estimatedDeparture")
                row["travel_distance"]      = conn.get("distance")
                row["travel_duration"]      = conn.get("time")
                row["travel_breaktime"]     = conn.get("break")
                row["travel_resttime"]      = conn.get("rest")
                row["travel_waittime"]      = conn.get("waiting")
                row["travel_warnings"]      = [w.get("message") for w in conn.get("warnings", [])]
                row["travel_warningcodes"]  = [w.get("code") for w in conn.get("warnings", [])]
                # fmt: on

            if coordinates:
                # fmt: off
                row["navigation_longitude"] = item.get("lng")
                row["navigation_latitude"]  = item.get("lat")
                # fmt: on

            if fcs := item.get("failedConstraints", []):
                # fmt: off
                row["error_code"]           = "failed_constraints"
                row["error_message"]        = _fcs_errmsg(fcs)
                # fmt: on
            elif err := self.error():
                # fmt: off
                row["error_code"]           = getattr(err, "code", "generic")
                row["error_message"]        = str(err)
                # fmt: on
            else:
                # fmt: off
                row["error_code"]           = None
                row["error_message"]        = None
                # fmt: on

        if not data:
            return GeoDataFrame()

        return GeoDataFrame(data, geometry="navigation", crs="EPSG:4326")


def tsp(
    client: CasaGeoClient,
    waypoints: DataFrame,
    *,
    origin: str | None = None,
    destination: str | None = None,
    clustering: str | None = None,
    break_times: Collection[tuple[datetime | str, timedelta | float | int]] = (),
    rest_schedule: str | None = None,
    transport_mode: str = TRANSPORT_MODES[0],
    routing_mode: str = ROUTING_MODES[0],
    optimize: str = OPTIMIZATION_TARGETS[0],
    departure_time: datetime | str | None = None,
    traffic: bool = False,
    avoid_features: Collection[str] = (),
    exclude_countries: Collection[str] = (),
    vehicle_length: int | None = None,  # cm
    vehicle_width: int | None = None,  # cm
    vehicle_height: int | None = None,  # cm
    vehicle_axle_weight: int | None = None,  # kg
    vehicle_total_weight: int | None = None,  # kg
    vehicle_trailers: int | None = None,
    hazardous_cargo: Collection[str] = (),
    walking_speed: int | None = None,  # m/s
    with_coordinates: bool = False,
) -> GeoDataFrame:
    df = tsp_result(
        client,
        waypoints,
        origin=origin,
        destination=destination,
        clustering=clustering,
        break_times=break_times,
        rest_schedule=rest_schedule,
        transport_mode=transport_mode,
        routing_mode=routing_mode,
        optimize=optimize,
        departure_time=departure_time,
        traffic=traffic,
        avoid_features=avoid_features,
        exclude_countries=exclude_countries,
        vehicle_length=vehicle_length,
        vehicle_width=vehicle_width,
        vehicle_height=vehicle_height,
        vehicle_axle_weight=vehicle_axle_weight,
        vehicle_total_weight=vehicle_total_weight,
        vehicle_trailers=vehicle_trailers,
        hazardous_cargo=hazardous_cargo,
        walking_speed=walking_speed,
        with_coordinates=with_coordinates,
    ).dataframe()
    return cast(GeoDataFrame, df)


def tsp_result(
    client: CasaGeoClient,
    waypoints: DataFrame,
    *,
    origin: str | None = None,
    destination: str | None = None,
    clustering: str | None = None,
    break_times: Collection[tuple[datetime | str, timedelta | float | int]] = (),
    rest_schedule: str | None = None,
    transport_mode: str = TRANSPORT_MODES[0],
    routing_mode: str = ROUTING_MODES[0],
    optimize: str = OPTIMIZATION_TARGETS[0],
    departure_time: datetime | str | None = None,
    traffic: bool = False,
    avoid_features: Collection[str] = (),
    exclude_countries: Collection[str] = (),
    vehicle_length: int | None = None,  # cm
    vehicle_width: int | None = None,  # cm
    vehicle_height: int | None = None,  # cm
    vehicle_axle_weight: int | None = None,  # kg
    vehicle_total_weight: int | None = None,  # kg
    vehicle_trailers: int | None = None,
    hazardous_cargo: Collection[str] = (),
    walking_speed: int | None = None,  # m/s
    with_coordinates: bool = False,
) -> MultiResult[TSPResult]:
    """:meta private:"""

    options = delna({
        "origin": origin if origin is not None else waypoints.iloc[0].at["name"],
        "destination": destination,
        "clustering": clustering,
        "break_times": [
            {"start": iso_datetime(start), "duration": minutes_to_seconds(duration)}
            for start, duration in break_times
        ],
        "rest_schedule": rest_schedule,
        "transport_mode": transport_mode,
        "routing_mode": routing_mode,
        "optimize": optimize,
        "departure_time": and_then(departure_time, iso_datetime),
        "traffic": traffic,
        "avoid_features": list(avoid_features),
        "exclude_countries": list(exclude_countries),
        "vehicle_length": vehicle_length,
        "vehicle_width": vehicle_width,
        "vehicle_height": vehicle_height,
        "vehicle_axle_weight": vehicle_axle_weight,
        "vehicle_total_weight": vehicle_total_weight,
        "vehicle_trailers": vehicle_trailers,
        "hazardous_cargo": list(hazardous_cargo),
        "walking_speed": walking_speed,
    })

    points = [
        delna({
            "name": and_then(wp.get("name"), str),
            "position": and_then(getpoint(wp, "position"), point_xy),
            "navigation": and_then(getpoint(wp, "navigation"), point_xy),
            "course": and_then(wp.get("course"), int),  # degrees (int)
            # Enlist instead of splitting because names might contain
            # commas. We can always change this later.
            "before": and_then(wp.get("before"), enlist_if_str),
            "at": and_then(wp.get("appointment_time"), iso_datetime),
            "st": and_then(wp.get("service_time"), minutes_to_seconds),
            "ir": and_then(wp.get("interruptible"), bool),
        })
        for wp in to_records(waypoints)
    ]

    response = client._httpxclient.post(
        "/api/v2/tsp", json={"options": options, "waypoints": points}
    )

    json = _apiv2._decode_dict(response)
    _logger.debug("TSP Response: %r", json)

    return MultiResult(
        json=json,
        ids=[1],
        options={"coordinates": with_coordinates},
        result_type=TSPResult,
    )
