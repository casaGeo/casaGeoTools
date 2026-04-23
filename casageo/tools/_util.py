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

"""Contains internal utils for dealing with the client"""

import contextlib
import re
from collections import ChainMap
from collections.abc import Callable, Generator, Mapping, MutableMapping
from datetime import datetime
from typing import Any, cast

import flexpolyline.decoding
import numpy as np
import pandas as pd
import shapely
from shapely import Point

from . import _consts

ietf_bcp47_language_tag_pattern = re.compile(r"[A-Za-z0-9]+(-[A-Za-z0-9]+)*")
iso3166_alpha3_country_code_pattern = re.compile(r"[A-Z]{3}")
# https://www.here.com/docs/bundle/geocoding-and-search-api-developer-guide/page/topics-places/places-category-system-full.html
here_api_category_code_pattern = re.compile(r"!?\d{3}(-\d{4}){0,2}", re.ASCII)
# https://www.here.com/docs/bundle/geocoding-and-search-api-developer-guide/page/topics-places/places-chain-system-full.html
here_api_chain_code_pattern = re.compile(r"!?\d+", re.ASCII)
# https://www.here.com/docs/bundle/geocoding-and-search-api-developer-guide/page/topics-places/food-types-category-system-full.html
here_api_food_type_code_pattern = re.compile(r"!?\d{3}-\d{3}", re.ASCII)


def validate_ietf_bcp47_language_tag(string: str) -> None:
    if not ietf_bcp47_language_tag_pattern.fullmatch(string):
        raise ValueError(f"Invalid IETF BCP 47 language tag: {string!r}")


def validate_iso3166_alpha3_country_code(string: str) -> None:
    if not iso3166_alpha3_country_code_pattern.fullmatch(string):
        raise ValueError(f"Invalid ISO 3166-1 alpha-3 country code: {string!r}")


def validate_here_api_category_code(string: str) -> None:
    if not here_api_category_code_pattern.fullmatch(string):
        raise ValueError(f"Invalid HERE API category code: {string!r}")


def validate_here_api_chain_code(string: str) -> None:
    if not here_api_chain_code_pattern.fullmatch(string):
        raise ValueError(f"Invalid HERE API chain code: {string!r}")


def validate_here_api_food_type_code(string: str) -> None:
    if not here_api_food_type_code_pattern.fullmatch(string):
        raise ValueError(f"Invalid HERE API food type code: {string!r}")


def flexpolyline_points(encoded: str) -> np.ndarray:
    """
    Decode a flexpolyline into an array of points.

    While flexpolyline encodes points as lat-lng, this function returns an array
    of lng-lat points to match GeoPandas.

    If the input contains a third dimension, it will be reflected in the output.
    The type of the third dimension is ignored. The third dimension can be
    removed using ``shapely.force_2d()``.

    Args:
        encoded: The encoded flexpolyline.

    Returns:
        np.ndarray: An array of points with either (lng, lat) or (lng, lat, z)
        coordinates, depending on whether the input contained a third dimension.
    """
    return shapely.points([
        (lng, lat, *z) for lat, lng, *z in flexpolyline.decoding.iter_decode(encoded)
    ])


def dict_to_point(pos: dict) -> Point | None:
    with contextlib.suppress(KeyError):
        return Point(pos["lng"], pos["lat"], pos["elv"])
    with contextlib.suppress(KeyError):
        return Point(pos["lng"], pos["lat"])
    return None


def rename(newname: str):
    def decorator(func):
        func.__name__ = newname
        return func

    return decorator


def and_then(val, *funcs: Callable):
    for func in funcs:
        if val is None:
            break
        val = func(val)
    return val


def isscalarna(x: Any) -> bool:
    return pd.api.types.is_scalar(x) and cast(bool, pd.isna(x))


def delna(d: dict) -> dict:
    return {k: v for k, v in d.items() if not isscalarna(v)}


def replacena(d: dict) -> dict:
    return {k: (None if isscalarna(v) else v) for k, v in d.items()}


def getpoint(q: Mapping, key: str) -> Point | None:
    with contextlib.suppress(KeyError):
        return Point(q[key])
    with contextlib.suppress(KeyError):
        lng = q[f"{key}_longitude"]
        lat = q[f"{key}_latitude"]
        with contextlib.suppress(KeyError):
            return Point(lng, lat, q[f"{key}_elevation"])
        return Point(lng, lat)
    return None


def point_xy(p: Point) -> tuple[float, float]:
    return (p.x, p.y)


def split_if_str(sep: str | None = None, maxsplit: int = -1):
    def splitter[T](s: str | T) -> list[str] | T:
        return s.split(sep, maxsplit) if isinstance(s, str) else s

    return splitter


def to_records(
    df: pd.DataFrame, *fallbacks: MutableMapping
) -> Generator[MutableMapping]:
    records = df.to_dict(orient="records")
    return (ChainMap(replacena(r), *fallbacks) for r in records)


@rename("IETF BCP47 language tag")
def cli_ietf_bcp47_language_tag(value: str) -> str:
    validate_ietf_bcp47_language_tag(value)
    return value


@rename("ISO 3166-1 alpha-3 country code")
def cli_iso3166_alpha3_country_code(value: str) -> str:
    validate_iso3166_alpha3_country_code(value)
    return value


@rename("comma-separated ISO 3166-1 alpha-3 country code list")
def cli_iso3166_alpha3_country_code_list(value: str) -> list[str]:
    codes = value.split(",")
    for code in codes:
        validate_iso3166_alpha3_country_code(code)
    return codes


@rename("Latitude,Longitude point")
def cli_latlong_point(value: str) -> Point:
    lat, lng = value.split(",")
    return Point(float(lng), float(lat))


@rename("positive integer")
def cli_positive_int(value: str) -> int:
    if (x := int(value)) > 0:
        return x
    raise ValueError("number must be greater than zero")


@rename("non-negative integer")
def cli_non_negative_int(value: str) -> int:
    if (x := int(value)) >= 0:
        return x
    raise ValueError("number must be non-negative")


@rename("ISO 8601 datetime")
def cli_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


@rename("comma-separated feature list")
def cli_avoidable_feature_list(value: str) -> list[str]:
    features = value.split(",")
    for feature in features:
        if feature not in _consts.AVOIDABLE_FEATURES:
            raise ValueError(
                f"avoidable features may only contain {_consts.AVOIDABLE_FEATURES}, got {feature!r}"
            )
    return features


@rename("comma-separated HERE API category code list")
def cli_here_api_category_code_list(value: str) -> list[str]:
    codes = value.split(",")
    for code in codes:
        validate_here_api_category_code(code)
    return codes


@rename("comma-separated HERE API chain code list")
def cli_here_api_chain_code_list(value: str) -> list[str]:
    codes = value.split(",")
    for code in codes:
        validate_here_api_chain_code(code)
    return codes


@rename("comma-separated HERE API food type code list")
def cli_here_api_food_type_code_list(value: str) -> list[str]:
    codes = value.split(",")
    for code in codes:
        validate_here_api_food_type_code(code)
    return codes
