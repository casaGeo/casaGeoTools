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

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any, Self, cast
from uuid import UUID, uuid4

import pandas as pd

from ._errors import APIReturnTypeError, SubqueryError


def _get_timestamp(
    d: dict[str, Any], /, default: datetime | None = None
) -> datetime | None:
    try:
        return datetime.fromisoformat(d["timestamp"])
    except (KeyError, TypeError, ValueError):
        return default


def _get_request_id(d: dict[str, Any], /, default: UUID | None = None) -> UUID | None:
    try:
        return UUID(d["request_id"])
    except (KeyError, TypeError, ValueError):
        return default


class CasaGeoResult:
    def __init__(
        self,
        *,
        _data: dict[str, Any],
        _error: Exception | None = None,
        _timestamp: datetime | None = None,
        _uuid: UUID | None = None,
    ) -> None:
        self._data = _data
        self._error = _error
        self._timestamp = _timestamp if _timestamp is not None else datetime.now()
        self._uuid = _uuid if _uuid is not None else uuid4()

    def __bool__(self) -> bool:
        return self._error is None

    def __repr__(self) -> str:
        classname = type(self).__qualname__
        return f"<{classname} {self._uuid} [{'OK' if self else repr(cast(Exception, self._error))}]>"

    @classmethod
    def from_json(
        cls,
        json: Any,
        *,
        index: int | None = None,
        timestamp: datetime | None = None,
        uuid: UUID | None = None,
    ) -> Self:
        if not isinstance(json, dict):
            msg = f"Invalid JSON response type: {json.__class__.__name__}"
            raise APIReturnTypeError(msg)

        value = json.get("value", {})
        if not isinstance(value, dict):
            msg = f"Invalid JSON response value type: {value.__class__.__name__}"
            raise APIReturnTypeError(msg)

        if isinstance(e := json.get("error"), dict):
            error = SubqueryError(
                e.get("message", repr(e)),
                code=e.get("code"),
                index=index,
                details=e.get("details"),
            )
        else:
            error = None

        return cls(
            _data=value,
            _error=error,
            _timestamp=_get_timestamp(json, timestamp),
            _uuid=_get_request_id(json, uuid),
        )

    def timestamp(self) -> datetime:
        """
        Return the timestamp of the API response.

        Returns:
            datetime: The timestamp of the API response.
        """
        return self._timestamp

    def uuid(self) -> UUID:
        """
        Return the UUID of this response object.

        Returns:
            uuid.UUID: The UUID of this response object.
        """
        return self._uuid

    def json(self) -> dict[str, Any]:
        """
        Return the raw API response as a dictionary.

        Returns:
            dict: The raw JSON API response.
        """
        return self._data

    def error(self) -> Exception | None:
        """
        Return the exception that occurred during the API request, if any.

        Returns:
            Exception | None: The exception that occurred, or None if no exception occurred.
        """
        return self._error

    def dataframe(self, id_: Any | None, *, error_info: bool) -> pd.DataFrame:
        raise NotImplementedError("dataframe() not implemented for CasaGeoResult")


class MultiResult[T: CasaGeoResult](Sequence[T]):
    def __init__(
        self,
        json: Any | None,
        *,
        ids: Sequence[Any],
        options: Mapping[str, Any],
        result_type: type[T] = CasaGeoResult,
    ):
        if json is None:
            json = {}

        if not isinstance(json, dict):
            msg = f"Invalid JSON response type: {type(json)}"
            raise APIReturnTypeError(msg)

        self._json = json
        self._timestamp = _get_timestamp(json) or datetime.now()
        self._uuid = _get_request_id(json) or uuid4()
        self._ids = list(ids)
        self._options = dict(options)
        self._results = [
            result_type.from_json(
                result,
                index=index,
                timestamp=self._timestamp,
                uuid=self._uuid,  # NOTE: Should this be the correlation ID?
            )
            for index, result in enumerate(self._json.get("results", []))
        ]

    def __getitem__(self, index):
        return self._results[index]

    def __iter__(self):
        return iter(self._results)

    def __len__(self) -> int:
        return len(self._results)

    def __repr__(self) -> str:
        classname = type(self).__qualname__
        results = [
            ((self._ids[index] if index < len(self._ids) else index), result)
            for index, result in enumerate(self._results)
        ]
        return f"<{classname} {self._uuid} {results!r}>"

    def _make_dataframe(self, index: int, result: CasaGeoResult):
        try:
            id_ = self._ids[index]
        except IndexError:
            id_ = index

        # noinspection PyArgumentList
        df = result.dataframe(id_=id_, error_info=True, **self._options)

        if (err := result.error()) and not df.empty:
            df["error_code"] = getattr(err, "code", "generic")
            df["error_message"] = str(err)
        # elif not df.empty:
        #     df["error_code"] = None
        #     df["error_message"] = None

        return df

    def timestamp(self) -> datetime:
        """
        Return the timestamp of the API response.

        Returns:
            datetime: The timestamp of the API response.
        """
        return self._timestamp

    def uuid(self) -> UUID:
        """
        Return the UUID of the API response.

        Returns:
            uuid.UUID: The UUID of the API response.
        """
        return self._uuid

    def json(self) -> dict[str, Any]:
        """
        Return the raw API response as a dictionary.

        Returns:
            dict: The raw JSON API response.
        """
        return self._json

    def dataframe(self) -> pd.DataFrame:
        return pd.concat(
            (self._make_dataframe(i, r) for i, r in enumerate(self._results)),
            ignore_index=True,
        )
