#!/usr/bin/env python3
# Copyright 2026 casaGeo Data + Services GmbH <info@casageo.de>
# SPDX-License-Identifier: 0BSD

import os
import sys

import pandas as pd

import casageo.coder
import casageo.spatial
import casageo.tools

API_KEY = os.getenv("CASAGEOTOOLS_API_KEY")

if not API_KEY:
    sys.exit("CASAGEOTOOLS_API_KEY environment variable must be set")


# Ensure dataframes are printed completely.
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 999)


client = casageo.tools.CasaGeoClient(API_KEY)
client.preferred_language = "de-DE"


#############
# Geocoding #
#############


address_queries = pd.DataFrame([
    {
        "id": 1,
        "address": "Fraunhoferstr. 3, 25524 Itzehoe DEU",
    },
    {
        "id": 2,
        "street": "Hachmannplatz 16",
        "postalcode": "20099",
        "city": "Hamburg",
        "country": "DEU",
    },
    {
        "id": 3,
        "street": "Sophienblatt",
        "housenumber": "25",
        "postalcode": "24114",
        "city": "Kiel",
        "country": "DEU",
    },
])

address_results = casageo.coder.address(
    client,
    address_queries,
    address_details=True,
    coordinates=True,
    match_quality=True,
)

print()
print("Address Results:")
print(address_results)


##############
# POI Search #
##############


poi_queries = pd.DataFrame([
    {
        "id": 1,
        "position": (9.4854461, 53.9580118),  # IZET
    },
    {
        "id": 2,
        "position": (10.008223, 53.553089),  # Hamburg Central Station
    },
])

poi_results = casageo.coder.poi(
    client,
    poi_queries,
    {"limit": 3},
    address_details=True,
    coordinates=True,
)

print()
print("POI Results:")
print(poi_results)


############
# Isolines #
############


isolines_queries = pd.DataFrame([
    {
        "id": 1,
        "position": (10.008223, 53.553089),
        "name": "Hamburg Central Station",
        "ranges": [5, 15],
        "ranges_unit": "minutes",
        "transport_mode": "car",
    },
    {
        "id": 2,
        "position": (10.66865, 53.86621),
        "name": "Lübeck Central Station",
        "ranges": "3000",
        "ranges_unit": "meters",
        "transport_mode": "pedestrian",
    },
    {
        "id": 3,
        "position": (10.13008, 54.31367),
        "name": "Kiel Central Station",
        "ranges": "10,20",
        "range_type": "time",  # Same as "ranges_unit": "minutes"
        "transport_mode": "car",
    },
])

isolines_results = casageo.spatial.isolines(
    client,
    isolines_queries,
)

print()
print("Isolines Results:")
print(isolines_results)


###########
# Routing #
###########


routes_queries = pd.DataFrame([
    {
        "id": 1,
        "origin": (9.4854461, 53.9580118),  # IZET
        "destination": (10.008223, 53.553089),  # Hamburg Central Station
        "routing_mode": "fast",
        "transport_mode": "car",
    },
    {
        "id": 2,
        "origin": (9.4854461, 53.9580118),  # IZET
        "destination": (10.13008, 54.31367),  # Kiel Central Station
        "routing_mode": "fast",
        "transport_mode": "car",
    },
    {
        "id": 3,
        "origin": (9.4854461, 53.9580118),  # IZET
        "destination": (10.66865, 53.86621),  # Lübeck Central Station
        "routing_mode": "fast",
        "transport_mode": "car",
    },
])

routes_results = casageo.spatial.routes(
    client,
    routes_queries,
    {
        "transport_mode": "car",
        "routing_mode": "fast",
    },
    departure_info=True,
    arrival_info=True,
)

print()
print("Routes Results:")
print(routes_results)
