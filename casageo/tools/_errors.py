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


class CasaGeoError(Exception):
    # TODO: Exception hierarchy wrapping low-level and API errors.
    pass


class APIValueError(CasaGeoError, ValueError):
    pass


class APIReturnTypeError(CasaGeoError, TypeError):
    pass


class InsufficientCreditsError(CasaGeoError):
    def __init__(
        self,
        message: str | None = None,
        *,
        required: int | None = None,
        available: int | None = None,
    ):
        if message is None:
            message = "Insufficient credits"

        message += " ({:,} required, {:,} available)".format(
            required if required is not None else "unknown number",
            available if available is not None else "unknown number",
        )

        super().__init__(message)
        self.required = required
        self.available = available


class SubqueryError(CasaGeoError):
    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        index: int | None = None,
        details: str | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.index = index
        self.details = details
        if self.code is not None:
            self.add_note(f"code {self.code!r}")
        if self.index is not None:
            self.add_note(f"at index [{self.index!r}]")
        if self.details is not None:
            self.add_note(self.details)
