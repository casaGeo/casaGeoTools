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
      The direction (degrees in clockwise direction, 0 is north) from which this
      waypoint should be approached or in which it should be left.

   radius : int
      Consider all places within this radius, in meters, as potential candidates
      for matching the waypoint. If ``snap`` is enabled, match the waypoint to
      the most significant road within this radius.

   snap : bool
      Controls the meaning of the ``radius`` parameter, the default is
      ``False``.

   .. _logistics-matrix-output-columns:

   Matrix Output Columns
   ---------------------

   The resulting dataframe contains the following columns:

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
      The direction (degrees in clockwise direction, 0 is north) from which this
      waypoint should be approached or in which it should be left.

   before : list[str]
      Names of other waypoints that must be sequenced after this waypoint.

   appointment_time : datetime | str
      Date and time of an appointment at this waypoint. If set, this waypoint
      must be reached before the start of the appointment and can only be left
      after the appointment has ended. You must set a ``service_time`` when
      using this feature.

   service_time : timedelta \| float \| int
      Duration of time spent at this waypoint. If an ``appointment_time`` is
      set, this specifies the duration of the appointment.

   interruptible : bool
      Whether the ``service_time`` at this waypoint can be interrupted by break
      times as specified in the ``break_times`` option. The default is ``True``.

   .. _logistics-tsp-output-columns:

   TSP Output Columns
   ------------------

   The resulting dataframe contains the following columns:

   id : Any
      Fixed identifier added to each result of a query.

   subid : int
      Numeric index of the waypoint in the result sequence starting from zero.

   clusterid : int | None
      If the waypoint is part of a cluster, this is the numeric index of the
      cluster starting from zero. If clustering is not enabled, or the waypoint
      is not part of a cluster, the value is ``None``.

   name : str
      Name of the waypoint.

   position : :class:`~shapely.Point`
      Position of the waypoint.

   arrival_time : datetime
      Estimated arrival time at the waypoint.

   departure_time : datetime
      Estimated departure time at the waypoint.

   travel_distance : float
      Distance from the previous waypoint to this waypoint in meters. This value
      is zero for the first waypoint in the sequence.

   travel_duration : float
      Travel time from the previous waypoint to this waypoint in minutes. This
      value is zero for the first waypoint in the sequence.

   travel_breaktime : float
      Total break time spent at this waypoint or traveling to this waypoint.

   travel_resttime : float
      Total rest time spent at this waypoint or traveling to this waypoint.

   travel_waittime : float
      Total waiting time at this waypoint.

   travel_warning_codes : list[str]
      Warning codes for traveling to this waypoint. Warnings may include
      violated routing constraints, physical restrictions or legal restrictions.
      Corresponding warning messages can be found in
      ``travel_warning_messages``.

   travel_warning_messages : list[str]
      Warning messages for traveling to this waypoint. Warnings may include
      violated routing constraints, physical restrictions or legal restrictions.
      Corresponding warning codes can be found in ``travel_warning_codes``.

   When ``coordinates`` is ``True``, the dataframe also contains the following
   columns:

   position_longitude : float
      Longitude of the waypoint’s position.

   position_latitude : float
      Latitude of the waypoint’s position.

   Finally, the dataframe always contains the following error information
   columns. These contain values only if the corresponding query could not be
   executed for some reason.

   error_code : str
      String indicating the type of error.

   error_message : str
      Human-readable error message.

   -----------------------------------------------------------------------------


.. _IETF BCP47: https://en.wikipedia.org/wiki/IETF_language_tag
.. _ISO 3166-1 alpha-3: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3
