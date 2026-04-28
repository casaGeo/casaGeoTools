# 🗺️ casaGeoTools

**A Python connector for the HERE Location Platform — designed for geocoding,
routing, and isoline analytics.**

---

## 🚀 Overview

**casaGeoTools** provides a simple and Pythonic way to access the power of the
**HERE Location Platform** directly from your Python environment. It allows
developers, analysts, and data scientists to integrate **location intelligence**
into their workflows with just a few lines of code.

With casaGeoTools, you can easily:

- 🏠 **Geocode** addresses into coordinates
- 🚗 **Compute routes** between locations
- 🕒 **Generate isolines** (isochrones or isodistances)
- 🌍 **Visualize results** interactively on a map

casaGeoTools wraps the HERE APIs with a clean, consistent interface optimized
for Python.

---

## 🌐 Powered by HERE Platform

casaGeoTools is built on top of the **HERE Platform** and provides a
ready-to-use Python connector to HERE’s core location services.

You don’t need to manage REST requests or API authentication manually —
casaGeoTools handles that for you while giving you a natural, Pandas- and
GeoPandas-friendly interface.

---

## 💰 Credit System (Beta Program)

casaGeoTools uses a **credit-based API model**.

Each API key includes a balance of credits that are **valid for 1 year**. Unused
credits **expire after 12 months**.

During the **public Beta phase**, every registered user receives **3,000 free
credits**.

### 🔢 Credit usage per API call

| Operation | Credits per request | Description                               |
|-----------|---------------------|-------------------------------------------|
| Geocoding | 3 credits           | Convert address → coordinates             |
| Routing   | 3 credits           | Compute route between two points          |
| Isolines  | 20 credits          | Generate isochrone or isodistance polygon |

### 💡 Example usage

With 3,000 credits you can approximately:

- Geocode **1,000 addresses**, or
- Compute **1,000 routes**, or
- Generate **150 isolines**

You can also combine requests freely:

> e.g., 500 geocodes + 250 routes + 50 isolines = 3,000 credits total

---

## ⚙️ Installation

Install the required packages using pip:

``` shell
pip install casaGeoTools
```

---

## casaGeoTools Beta Example Script

See the example script under `examples/beta_example_script.py` for a complete
example of how to use casaGeoTools.
