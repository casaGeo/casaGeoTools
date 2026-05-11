.. _spatial-module:

======================
casageo.spatial module
======================

.. automodule:: casageo.spatial
   :members:
   :undoc-members:
   :show-inheritance:

   .. _spatial-general-info:

   General Information
   ===================

   All routing is done independently of time and traffic data by default. To
   include traffic data in the calculations, set the ``traffic`` parameter to
   ``True`` and provide either a ``departure_time`` or an ``arrival_time``.

   .. _spatial-isoline-queries:

   Isolines Queries
   ================

   Calculate isolines around locations.

   .. _spatial-isoline-query-options:

   Isolines Query Options
   ----------------------

   departure_info : bool
      Include additional information about the departure time and location.

   arrival_info : bool
      Include additional information about the arrival time and location.

   .. _spatial-isoline-input-columns:

   Isolines Input Columns
   ----------------------

   The following columns will be read from the input dataframe:

   id : Any
      Fixed identifier to be added to each result of this query.

   position : :class:`~shapely.Point`
      The center point of the isolines. Instead of a geometry object, you may
      also specify this as two separate fields ``position_latitude`` and
      ``position_longitude`` of type :class:`float`.

   ranges : list[float]
      The distances or durations for which to calculate isolines.

   ranges_unit : str
      The unit for the range values, either ``"minutes"`` or ``"meters"``. If
      unset, falls back to reading the field ``range_type`` which can either be
      ``"time"`` (minutes) or ``"distance"`` (meters).

   language : str
      The preferred language for the response. This must be a valid `IETF
      BCP47`_ language tag, such as ``"en-US"``, or a comma-separated list of
      such tags in order of preference.

   unit_system : str
      The system of units to use for localized quantities, either ``"metric"``
      or ``"imperial"``.

   transport_mode : str
      The mode of transport to use for routing, e.g. ``"car"``.

   routing_mode : str
      Whether to prefer ``"fast"`` or ``"short"`` routes.

   direction : str
      The direction of travel relative to the center point, either
      ``"outgoing"`` or ``"incoming"``.

   departure_time : datetime
      The date and time of departure for time-dependent routing. This value is
      only used when ``direction`` is ``"outgoing"``.

   arrival_time : datetime
      The date and time of arrival for time-dependent routing. This value is
      only used when ``direction`` is ``"incoming"``.

   traffic : bool
      Whether to consider traffic data during routing.

      When using this feature, you should also specify either ``departure_time``
      or ``arrival_time``, depending on ``direction``, to get meaningful and
      reproducible results.

   avoid_features : str | list[str]
      If set, these route features are avoided during routing. This parameter
      treats a comma-separated string as a list of strings.

   exclude_countries : str | list[str]
      If set, these countries are excluded from routing. Must be a sequence of
      valid `ISO 3166-1 alpha-3`_ country codes. This parameter treats a
      comma-separated string as a list of strings.

   .. _spatial-isoline-output-columns:

   Isolines Output Columns
   -----------------------

   The resulting dataframe contains the following columns:

   id : Any
      Fixed identifier added to each result of a query.

   subid : int
      Numeric index of the result starting from zero.

   geometry : :class:`~shapely.MultiPolygon`
      A MultiPolygon representing the isoline’s geometry.

   rangetype : str
      String representing the type of the distance value.

   rangeunit : str
      String representing the unit of the range value.

   rangevalue : float
      The distance value represented by this range.

   timestamp : datetime
      Timestamp of when this result was created.

   When ``departure_info`` is ``True``, the dataframe also contains the columns
   below. If the direction of the query was not ``"outgoing"``, all these values
   will be null.

   departure_time : datetime
      Timestamp representing the expected departure time.

   departure_placename : str
      Name of the departure location.

   departure_position : :class:`~shapely.Point`
      Resolved position of the departure location used for route calculation.

   departure_displayposition : :class:`~shapely.Point`
      Position of a map marker referring to the departure location.

   departure_queryposition : :class:`~shapely.Point`
      The original position provided in the request.

   When ``arrival_info`` is ``True``, the dataframe also contains the columns
   below. If the direction of the query was not ``"incoming"``, all these values
   will be null.

   arrival_time : datetime
      Timestamp representing the expected arrival time.

   arrival_placename : str
      Name of the arrival location.

   arrival_position : :class:`~shapely.Point`
      Resolved position of the arrival location used for route calculation.

   arrival_displayposition : :class:`~shapely.Point`
      Position of a map marker referring to the arrival location.

   arrival_queryposition : :class:`~shapely.Point`
      The original position provided in the request.

   Finally, the dataframe always contains the following error information
   columns. These contain values only if the corresponding query could not be
   executed for some reason.

   error_code : str
      String indicating the type of error.

   error_message : str
      Human-readable error message.

   .. _spatial-routing-queries:

   Routing Queries
   ===============

   Calculate routes between two locations.

   .. _spatial-routing-query-options:

   Routing Query Options
   ---------------------

   departure_info : bool
      Include additional information about the departure time and location.

   arrival_info : bool
      Include additional information about the arrival time and location.

   .. _spatial-routing-input-columns:

   Routing Input Columns
   ---------------------

   The following columns will be read from the input dataframe:

   id : Any
      Fixed identifier to be added to each result of this query.

   origin : :class:`~shapely.Point`
      The starting point of the route. Instead of a geometry object, you may
      also specify this as two separate fields ``origin_latitude`` and
      ``origin_longitude`` of type :class:`float`.

   destination : :class:`~shapely.Point`
      The destination point of the route. Instead of a geometry object, you may
      also specify this as two separate fields ``destination_latitude`` and
      ``destination_longitude`` of type :class:`float`.

   alternatives : int
      The number of alternate routes to calculate.

   language : str
      The preferred language for the response. This must be a valid `IETF
      BCP47`_ language tag, such as ``"en-US"``, or a comma-separated list of
      such tags in order of preference.

   unit_system : str
      The system of units to use for localized quantities, either ``"metric"``
      or ``"imperial"``.

   transport_mode : str
      The mode of transport to use for routing, e.g. ``"car"``.

   routing_mode : str
      Whether to prefer ``"fast"`` or ``"short"`` routes.

   departure_time : datetime
      The date and time of departure for time-dependent routing.

   arrival_time : datetime
      The date and time of arrival for time-dependent routing.

   traffic : bool
      Whether to consider traffic data during routing.

      When using this feature, you should also specify either ``departure_time``
      or ``arrival_time``, depending on ``direction``, to get meaningful and
      reproducible results.

   avoid_features : str | list[str]
      If set, these route features are avoided during routing. This parameter
      treats a comma-separated string as a list of strings.

   exclude_countries : str | list[str]
      If set, these countries are excluded from routing. Must be a sequence of
      valid `ISO 3166-1 alpha-3`_ country codes. This parameter treats a
      comma-separated string as a list of strings.

   .. _spatial-routing-output-columns:

   Routing Output Columns
   ----------------------

   The resulting dataframe contains the following columns:

   id : Any
      Fixed identifier added to each result of a query.

   subid : int
      Numeric index of the result starting from zero.

   geometry : :class:`~shapely.MultiLineString`
      Geometry of the route by sections.

   length : float
      Total length of the route in meters.

   duration : float
      Total duration of the route in minutes.

   timestamp : datetime
      Timestamp of when this result was created.

   When ``departure_info`` is ``True``, the dataframe also contains the columns
   below. If the direction of the query was not ``"outgoing"``, all these values
   will be null.

   departure_time : datetime
      Timestamp representing the expected departure time.

   departure_placename : str
      Name of the departure location.

   departure_position : :class:`~shapely.Point`
      Resolved position of the departure location used for route calculation.

   departure_displayposition : :class:`~shapely.Point`
      Position of a map marker referring to the departure location.

   departure_queryposition : :class:`~shapely.Point`
      The original position provided in the request.

   When ``arrival_info`` is ``True``, the dataframe also contains the columns
   below. If the direction of the query was not ``"incoming"``, all these values
   will be null.

   arrival_time : datetime
      Timestamp representing the expected arrival time.

   arrival_placename : str
      Name of the arrival location.

   arrival_position : :class:`~shapely.Point`
      Resolved position of the arrival location used for route calculation.

   arrival_displayposition : :class:`~shapely.Point`
      Position of a map marker referring to the arrival location.

   arrival_queryposition : :class:`~shapely.Point`
      The original position provided in the request.

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
