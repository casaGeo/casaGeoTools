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

import datetime
import uuid
from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd

from ._errors import SubqueryError


class CasaGeoResult:
    def __init__(self, *, _data: dict, _error: Exception | None = None) -> None:
        self._timestamp = datetime.datetime.now()
        self._uuid = uuid.uuid4()
        self._data = _data
        self._error = _error

    def __bool__(self) -> bool:
        return self._error is None

    def __repr__(self) -> str:
        classname = type(self).__qualname__
        return f"<{classname} {self._uuid} [{'OK' if self else repr(self._error)}]>"

    def timestamp(self) -> datetime.datetime:
        """
        Return the timestamp of the API response.

        Returns:
            datetime: The timestamp of the API response.
        """
        return self._timestamp

    def uuid(self) -> uuid.UUID:
        """
        Return the UUID of this response object.

        Returns:
            uuid.UUID: The UUID of this response object.
        """
        return self._uuid

    def json(self) -> dict:
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

    def dataframe(self, id_: Any | None) -> pd.DataFrame:
        raise NotImplementedError("dataframe() not implemented for CasaGeoResult")


class MultiResult(Sequence):
    ResultType = CasaGeoResult

    def __init__(
        self,
        json: dict,
        *,
        ids: Sequence[Any],
        options: Mapping[str, Any],
        result_type: type[CasaGeoResult] | None = None,
    ):
        assert isinstance(json, dict)
        assert isinstance(json["results"], list)

        self._json = json
        self._uuid = (
            uuid.UUID(rqid) if (rqid := json.get("request_id")) else uuid.uuid4()
        )
        self._timestamp = (
            datetime.datetime.fromisoformat(rqts)
            if (rqts := json.get("timestamp"))
            else datetime.datetime.now()
        )

        if result_type is not None:
            self.ResultType = result_type

        self._ids = list(ids)
        self._options = dict(options)
        self._results = [
            self._make_result(i, r) for i, r in enumerate(self._json["results"])
        ]

        assert len(self._ids) == len(self._results)

    def __getitem__(self, index):
        return self._results[index]

    def __iter__(self):
        return iter(self._results)

    def __len__(self) -> int:
        return len(self._results)

    def __repr__(self) -> str:
        classname = type(self).__qualname__
        results = list(zip(self._ids, self._results, strict=True))
        return f"<{classname} {self._uuid} {results!r}>"

    def _make_result(self, index: int, data: Any):
        assert isinstance(data, dict)
        result = self.ResultType(
            _data=data.get("value", {}),
            _error=SubqueryError(
                e.get("message", repr(e)),
                code=e.get("code"),
                index=index,
                details=e.get("details"),
            )
            if (e := data.get("error"))
            else None,
        )
        result._timestamp = self._timestamp
        result._uuid = self._uuid  # NOTE: Should this be the correlation ID?
        return result

    def _make_dataframe(self, index: int, result: CasaGeoResult):
        # noinspection PyArgumentList
        df = result.dataframe(id_=self._ids[index], **self._options)
        if (err := result.error()) and not df.empty:
            df["error_code"] = getattr(err, "code", "generic")
            df["error_message"] = str(err)
        elif not df.empty:
            df["error_code"] = None
            df["error_message"] = None
        return df

    def timestamp(self) -> datetime.datetime:
        """
        Return the timestamp of the API response.

        Returns:
            datetime: The timestamp of the API response.
        """
        return self._timestamp

    def uuid(self) -> uuid.UUID:
        """
        Return the UUID of the API response.

        Returns:
            uuid.UUID: The UUID of the API response.
        """
        return self._uuid

    def json(self) -> dict:
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
