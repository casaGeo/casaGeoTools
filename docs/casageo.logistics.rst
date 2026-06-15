.. Copyright 2026 casaGeo Data + Services GmbH <info@casageo.de>
   SPDX-License-Identifier: CC-BY-SA-4.0

.. _logistics-module:

========================
casageo.logistics module
========================

.. automodule:: casageo.logistics
   :members:
   :undoc-members:
   :show-inheritance:

   .. _logistics-general-info:

   General Information
   ===================

   The functions in this module are single-shot calculations, not batch
   calculations like in :ref:`coder-module` and :ref:`spatial-module`.

   .. _logistics-tsp-queries:

   TSP Queries
   ===========

   Calculate the shortest path among a set of waypoints.

   .. _logistics-tsp-query-options:

   TSP Query Options
   -----------------

   TBD

   .. _logistics-tsp-input-columns:

   TSP Input Columns
   -----------------

   The following columns will be read from the input dataframe:

   name : str
      Unique string identifier for the waypoint. **Required**.

   navigation : :class:`~shapely.Point`
      Navigation coordinates corresponding to the waypoint. Instead of a
      geometry object, you may also specify this as two separate fields
      ``navigation_latitude`` and ``navigation_longitude`` of type
      :class:`float`. **Required**.

   course : int
      Optional.

   position : :class:`~shapely.Point`
      Optional.

   before : list[str]
      Optional.

   appointment_time : datetime | str
      Optional.

   service_time : timedelta \| float \| int
      Optional.

   interruptible : bool
      Optional.

   .. _logistics-tsp-output-columns:

   TSP Output Columns
   ------------------

   TBD

   -----------------------------------------------------------------------------


.. _IETF BCP47: https://en.wikipedia.org/wiki/IETF_language_tag
.. _ISO 3166-1 alpha-3: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3
