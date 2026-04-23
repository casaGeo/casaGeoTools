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

from typing import Final

SERVER: Final = "https://cg-license.casageo.eu/"

ADDRESS_NAMES_MODES: Final = ["default", "matched", "normalized"]
POSTAL_CODE_MODES: Final = ["default", "cityLookup", "districtLookup"]
UNIT_SYSTEMS: Final = ["metric", "imperial"]

RANGE_TYPES: Final = ["time", "distance"]
RANGE_UNITS: Final = ["minutes", "meters"]
RANGE_TYPE_BY_UNIT: Final = {
    "minutes": "time",
    "meters": "distance",
}
RANGE_UNIT_BY_TYPE: Final = {
    "time": "minutes",
    "distance": "meters",
}

TRANSPORT_MODES: Final = ["car", "pedestrian", "bicycle"]
ROUTING_MODES: Final = ["fast", "short"]
DIRECTION_TYPES: Final = ["outgoing", "incoming"]

AVOIDABLE_FEATURES: Final = [
    "carShuttleTrain",
    "controlledAccessHighway",
    "dirtRoad",
    "ferry",
    "seasonalClosure",
    "tollRoad",
    "tunnel",
    "uTurns",  # Not supported for pedestrian, bicycle and scooter transport modes.
]
