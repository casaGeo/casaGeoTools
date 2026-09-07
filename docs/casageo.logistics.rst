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

   .. _logistics-matrix-queries:

   Matrix Queries
   ==============

   Calculate a matrix of distance and travel time between waypoints.

   .. _logistics-matrix-query-options:

   Matrix Query Options
   --------------------

   profile : str
      The parameter profile to use for route calculation, see
      :class:`RoutingProfile`.

   .. _logistics-matrix-input-columns:

   Matrix Input Columns
   --------------------

   The following columns will be read from the input dataframe:

   type : str
      Either ``"origin"`` or ``"destination"``, the default is ``"origin"``. If
      no destination waypoints are specified, routes are calculated between all
      origin waypoints.

   position : :class:`~shapely.Point`
      Navigation coordinates corresponding to the waypoint. Instead of a
      geometry object, you may also specify this as two separate fields
      ``position_latitude`` and ``position_longitude`` of type :class:`float`.
      **Required**.

   streetposition : :class:`~shapely.Point`
      Coordinates of the destination corresponding to the waypoint, if any. This
      is used to select the the correct side of the street where necessary.
      Instead of a geometry object, you may also specify this as two separate
      fields ``streetposition_latitude`` and ``streetposition_longitude`` of
      type :class:`float`.

   placename : str
      Name of the target destination to select between multiple destinations
      near the same location.

   course : int
      Optional.

   radius : int
      Optional.

   snap : bool
      Optional.

   .. _logistics-matrix-output-columns:

   Matrix Output Columns
   ---------------------

   id : Any
      Fixed identifier added to each result of a query.

   origin : int
      Index of the origin waypoint in the list of origins.

   destination : int
      Index of the destination waypoint in the list of destinations.

   distance : int
      Travel distance between origin and destination in meters.

   traveltime : float
      Travel time between origin and destination in minutes.

   statuscode : int
      Zero on success, nonzero if a route could not be calculated.

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

   position : :class:`~shapely.Point`
      Navigation coordinates corresponding to the waypoint. Instead of a
      geometry object, you may also specify this as two separate fields
      ``position_latitude`` and ``position_longitude`` of type :class:`float`.
      **Required**.

   streetposition : :class:`~shapely.Point`
      Coordinates of the destination corresponding to the waypoint, if any. This
      is used to select the the correct side of the street where necessary.
      Instead of a geometry object, you may also specify this as two separate
      fields ``streetposition_latitude`` and ``streetposition_longitude`` of
      type :class:`float`.

   course : int
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
