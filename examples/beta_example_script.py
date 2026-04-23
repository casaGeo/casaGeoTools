"""
CasaGeoTools Beta Example Script
================================

👋 Welcome to the **casaGeoTools (Beta)** Python SDK!

This example demonstrates how to use casaGeoTools for:

  • Geocoding addresses
  • Computing routes between locations
  • Generating isolines (isochrones and isodistances)
  • Visualizing geospatial results on interactive maps

───────────────────────────────────────────────────────────────────────────────
🌐 Powered by HERE Platform
───────────────────────────────────────────────────────────────────────────────

casaGeoTools is a **Python connector for the HERE Location Platform**,
providing easy access to HERE’s powerful geospatial APIs — including
geocoding, routing, and isoline (isochrone / isodistance) services.

You can think of casaGeoTools as a simple and Pythonic interface to the
HERE ecosystem — ideal for data scientists, analysts, and developers who
want to work with location intelligence directly in Python.

───────────────────────────────────────────────────────────────────────────────
💰 Credit System (Beta Program)
───────────────────────────────────────────────────────────────────────────────

casaGeoTools uses a **credit-based API model**. Each API key is linked to
a credit balance that is valid for **1 year**. Unused credits expire after
12 months.

During the **public Beta phase**, all registered users receive **3,000 free credits**.

Each request to the underlying HERE APIs consumes credits:

  • Geocoding: 3 credits per request
  • Routing:   3 credits per request
  • Isolines:  20 credits per request

With 3,000 credits, you can approximately:

  • Geocode 1,000 addresses, or
  • Compute 1,000 routes, or
  • Generate 150 isolines

You can also combine different operations — for example,
→ 500 geocodes + 250 routes + 50 isolines.

───────────────────────────────────────────────────────────────────────────────
⚙️ Requirements
───────────────────────────────────────────────────────────────────────────────

Before running this example, install the following dependencies:

    pip install casaGeoTools geopandas shapely folium python-dotenv matplotlib pandas mapclassify

───────────────────────────────────────────────────────────────────────────────
🔑 Setup
───────────────────────────────────────────────────────────────────────────────

Create a `.env` file in your project directory and add your casaGeoTools API key:

    CASAGEOTOOLS_API_KEY=your_api_key_here

Then run this demo:

    python beta_example_script.py
"""

# --------------------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------------------

import os
import webbrowser

import geopandas as gpd
import pandas as pd
import shapely
from dotenv import load_dotenv

# casaGeoTools Beta modules
from casageo import coder as cc
from casageo import spatial as cs
from casageo import tools as ct

# --------------------------------------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------------------------------------

# Ensure dataframes are printed completely.
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 999)

# Load environment variables (API key)
load_dotenv()
API_KEY = os.getenv("CASAGEOTOOLS_API_KEY")

if not API_KEY:
    raise ValueError(
        "❌ No CASAGEOTOOLS_API_KEY found in .env file. Please set your casaGeoTools API key."
    )

# Initialize casaGeoTools client
cga = ct.CasaGeoClient(API_KEY)
cga.preferred_language = "de,en"


# --------------------------------------------------------------------------------------------------
# Create input data
# --------------------------------------------------------------------------------------------------

# ──────────────────────────────────────────────────────────────────────────────
# 🏠 Geocoding
# ──────────────────────────────────────────────────────────────────────────────
# Usage Notes:
# - Input format: "Street + House No., Postal Code + City, CountryCode"
# - Country codes (ISO3) examples:
#   Canada: CAN
#   France: FRA
#   Germany: DEU
#   United Kingdom: GBR
#   United States: USA
#   South Africa: ZAF
#   Ireland: IRL

address_list = pd.DataFrame([
    {"id": 1, "address": "Fraunhoferstr. 3, 25524 Itzehoe DEU"},
    {"id": 2, "address": "Hachmannplatz 16, 20099 Hamburg DEU"},
    {"id": 3, "address": "Sophienblatt 25, 24114 Kiel DEU"},
])

# ──────────────────────────────────────────────────────────────────────────────
# 🚗 Routing
# ──────────────────────────────────────────────────────────────────────────────
# Usage Notes:
# - routing_mode = 'fast'  (minimize time) or 'short' (minimize distance)
# - transport_mode = 'car', 'pedestrian', 'truck', or 'bicycle'

point_izet = shapely.Point(9.4854461, 53.9580118)
point_hh = shapely.Point(10.008223, 53.553089)
point_ki = shapely.Point(10.13008, 54.31367)
point_hl = shapely.Point(10.66865, 53.86621)

# fmt: off
list_routing = pd.DataFrame([
    {"id": 1, "origin": point_izet, "destination": point_hh, "routing_mode": "fast", "transport_mode": "car", "destination_name": "Hamburg Central Station"},
    {"id": 2, "origin": point_izet, "destination": point_ki, "routing_mode": "fast", "transport_mode": "car", "destination_name": "Kiel Central Station"},
    {"id": 3, "origin": point_izet, "destination": point_hl, "routing_mode": "fast", "transport_mode": "car", "destination_name": "Lübeck Central Station"},
])
# fmt: on

# ──────────────────────────────────────────────────────────────────────────────
# 🌀 Isolines
# ──────────────────────────────────────────────────────────────────────────────
# Usage Notes:
# - range_type = 'time' (minutes) or 'distance' (meters)
# - transport_mode = 'car', 'truck', or 'pedestrian'

# fmt: off
list_isolines = pd.DataFrame([
    {"id": 1, "position": point_hh, "name": "Hamburg Central Station", "range_type": "time", "ranges": [5, 15], "transport_mode": "car"},
    {"id": 2, "position": point_hl, "name": "Lübeck Central Station", "range_type": "distance", "ranges": [3000], "transport_mode": "pedestrian"},
    {"id": 3, "position": point_ki, "name": "Kiel Central Station", "range_type": "time", "ranges": [10], "transport_mode": "car"},
])
# fmt: on


# --------------------------------------------------------------------------------------------------
# Batch queries – Geocoding
# --------------------------------------------------------------------------------------------------

print("\n🌍 --- Batch Geocoding ---")

try:
    geocoded_df = cc.address(
        cga,
        address_list,
        {"limit": 1},
        address_details=True,
        coordinates=True,
    )
    print(geocoded_df)
except Exception as e:
    geocoded_df = gpd.GeoDataFrame()
    print(f"⚠️ Error during batch geocoding: {e}")


# --------------------------------------------------------------------------------------------------
# Batch queries – POI
# --------------------------------------------------------------------------------------------------

print("\n📍 --- Batch POI ---")

if not geocoded_df.empty:
    try:
        poi_df = cc.poi(
            cga,
            geocoded_df,
            {"limit": 3},
            address_details=True,
            coordinates=True,
        )
        print(poi_df)
    except Exception as e:
        poi_df = gpd.GeoDataFrame()
        print(f"⚠️ Error during batch POI search: {e}")
else:
    poi_df = gpd.GeoDataFrame()
    print("⚠️ Skipping batch POI search because batch geocoding failed.")


# --------------------------------------------------------------------------------------------------
# Batch queries – Routing
# --------------------------------------------------------------------------------------------------

print("\n🗺️ --- Batch Routing ---")

try:
    routes_gdf = cs.routes(
        cga,
        list_routing,
        departure_info=True,
        arrival_info=True,
    ).join(list_routing.set_index("id"), on="id")
    print(routes_gdf)
except Exception as e:
    routes_gdf = gpd.GeoDataFrame()
    print(f"⚠️ Error during batch routing: {e}")


# --------------------------------------------------------------------------------------------------
# Batch queries – Isolines
# --------------------------------------------------------------------------------------------------

print("\n🌀 --- Batch Isolines ---")

try:
    isolines_gdf = cs.isolines(
        cga,
        list_isolines,
        departure_info=True,
    ).join(list_isolines.set_index("id"), on="id")
    print(isolines_gdf)
except Exception as e:
    isolines_gdf = gpd.GeoDataFrame()
    print(f"⚠️ Error during batch isoline generation: {e}")


# --------------------------------------------------------------------------------------------------
# Visualization
# --------------------------------------------------------------------------------------------------


def save_and_open_map(gdf, filename, color="blue", opacity=0.8):
    """Helper function to visualize and save GeoDataFrames as interactive HTML maps."""
    map_obj = gdf.explore(
        color=color,
        style_kwds={"weight": 4, "opacity": opacity},
        tiles="OpenStreetMap",
    )
    map_obj.save(filename)
    webbrowser.open(filename)


print("\n🖼️ --- Visualization ---")

if not routes_gdf.empty:  # Visualize routes
    save_and_open_map(routes_gdf, "routes_map.html", color="blue", opacity=0.8)

if not isolines_gdf.empty:  # Visualize isolines
    save_and_open_map(isolines_gdf, "isolines_map.html", color="blue", opacity=0.3)


# --------------------------------------------------------------------------------------------------
# Done
# --------------------------------------------------------------------------------------------------

print("\n✅ casaGeoTools Beta demo completed successfully.")
print("Thank you for testing casaGeoTools Beta — powered by HERE Platform.")
print("Your feedback helps shape the future of geospatial intelligence in Python!")
