====================
casageo.coder module
====================

.. automodule:: casageo.coder
   :members:
   :undoc-members:
   :show-inheritance:

   .. _coder-address-queries:

   Address Queries
   ===============

   Geocode addresses.

   You can supply either a free-form address string or a combination of country,
   state, county, city, district, street, house number and postal code.
   Combining these two approaches is also supported.

   If the input data combines street and house number information into a
   single field, you can pass the resulting string to the ``street``
   field and leave the ``housenumber`` field unset.

   If you specify a ``position`` for the search, the search will favor places
   around that position and ``distance`` values will be computed for the
   results.

   The structured address fields are not hard filters, meaning it is possible to
   receive results from outside the specified country or city. In contrast, the
   ``countries`` list *is* a hard filter, limiting the search to only the
   specified countries.

   .. _coder-address-query-options:

   Address Query Options
   ---------------------

   address_details : bool
      Include additional address details in the result.

   coordinates : bool
      Include numeric coordinate columns in the result.

   match_quality : bool
      Include match quality scores in the result.

   .. _coder-address-input-columns:

   Address Input Columns
   ---------------------

   The following columns will be read from the input dataframe:

   id : Any
      Fixed identifier to be added to each result of this query.

   address : str
      A free-form address string.

   country : str
      The name of a country.

   state : str
      The name of a state or province.

   county : str
      The name of a county.

   city : str
      The name of a city.

   district : str
      The name of a city district.

   street : str
      The name of a street, optionally including a house number.

   housenumber : str
      The house number, including any extensions.

   postalcode : str
      The postal code.

   position : :class:`~shapely.Point`
      The geographical center of the search. Instead of a geometry object, you
      may also specify this as two separate fields ``position_latitude`` and
      ``position_longitude`` of type :class:`float`.

   language : str
      The preferred language for the response. This must be a valid `IETF
      BCP47`_ language tag, such as ``"en-US"``, or a comma-separated list of
      such tags in order of preference.

   political_view : str
      The political view of the query regarding disputed territories. This must
      be a valid `ISO 3166-1 alpha-3`_ country code.

   limit : int
      Limit on the number of results to return for each query. Must be between 1
      and 100. If unset, the default limit will be used.

   countries : str | list[str]
      If set, the search is limited to the specified countries. Must be a
      sequence of valid `ISO 3166-1 alpha-3`_ country codes. This parameter
      treats a comma-separated string as a list of strings.

   address_names_mode : str
      How to handle places with multiple names.

      -  ``"default"`` -- Prefer matched names for administrative places and
         normalized names for street names.
      -  ``"matched"`` -- Prefer names that match the input query.
      -  ``"normalized"`` -- Prefer the official names of places.

   postal_code_mode : str
      How to handle postal codes spanning multiple cities or districts.

      -  ``"default"`` -- Return only one result per postal code, leaving the
         city or district name blank if necessary.
      -  ``"cityLookup"`` -- When a postal code spans multiple cities, return
         all possible combinations of the postal code with the corresponding
         city names.
      -  ``"districtLookup"`` -- When a postal code spans multiple districts,
         return all possible combinations of the postal code with the
         corresponding city and district names.

   .. _coder-address-output-columns:

   Address Output Columns
   ----------------------

   The resulting dataframe contains the following columns:

   id : Any
      Fixed identifier added to each result of a query.

   subid : int
      Numeric index of the result starting from zero.

   address : str
      Localized display name of this result item.

   resulttype : str
      The type of the result item, one of ``"addressBlock"``,
      ``"administrativeArea"``, ``"houseNumber"``, ``"intersection"``,
      ``"locality"``, ``"place"``, ``"postalCodePoint"`` or ``"street"``.

   position : :class:`~shapely.Point`
      The coordinates of a pin on a map corresponding to the item.

   navigation : :class:`~shapely.Point`
      The coordinates of a navigation point corresponding to the item.

   distance : int
      The distance from the search position to the result item in meters.

   relevance : float
      The relevance of the result to the query as a number between zero and one.

   timestamp : datetime
      Timestamp of when this result was created.

   When ``address_details`` is ``True``, the dataframe also contains the
   following columns:

   postaladdress : str
      Full address of the item, formatted according to the regional postal
      rules. May not include all address components.

   country : str
      Name of the country.

   countrycode : str
      `ISO 3166-1 alpha-3`_ country code of the country.

   state : str
      Name of the state within the country.

   statecode : str
      Code or abbreviation of the state.

   county : str
      Name of the county or subdivision within the state.

   countycode : str
      Code or abbreviation of the county.

   city : str
      Name of the city.

   district : str
      Name of the district within the city.

   subdistrict : str
      Name of the subdistrict within the city.

   street : str
      Name of the street.

   streets : list[str]
      List of street names on an intersection.

   block : str
      Name of the city block.

   subblock : str
      Name of the subblock within the city block.

   postalcode : str
      Postal code associated with the item.

   housenumber : str
      House number, including associated qualifiers.

   building : str
      Name of the building.

   unit : str
      Information about the unit within the building.

   When ``coordinates`` is True, the dataframe also contains the following
   columns:

   position_longitude : float
      Longitude of the item’s position.

   position_latitude : float
      Latitude of the item’s position.

   navigation_longitude : float
      Longitude of the navigation point.

   navigation_latitude : float
      Latitude of the navigation point.

   When ``match_quality`` is ``True``, the dataframe also contains the columns
   below. Each of the values is a number between zero and one, indicating how
   well the output field matches the corresponding input field.

   mq_country : float
      Match quality of the ``country`` field.

   mq_countrycode : float
      Match quality of the ``countrycode`` field.

   mq_state : float
      Match quality of the ``state`` field.

   mq_statecode : float
      Match quality of the ``statecode`` field.

   mq_county : float
      Match quality of the ``county`` field.

   mq_countycode : float
      Match quality of the ``countycode`` field.

   mq_city : float
      Match quality of the ``city`` field.

   mq_district : float
      Match quality of the ``district`` field.

   mq_subdistrict : float
      Match quality of the ``subdistrict`` field.

   mq_street : float
      Average match quality of the ``streets`` field against each street name in
      the input query.

   mq_block : float
      Match quality of the ``block`` field.

   mq_subblock : float
      Match quality of the ``subblock`` field.

   mq_postalcode : float
      Match quality of the ``postalcode`` field.

   mq_housenumber : float
      Match quality of the ``housenumber`` field. If the requested house number
      could not be found, this indicates the numeric difference between the
      requested house number and the returned house number.

   mq_building : float
      Match quality of the ``building`` field.

   mq_unit : float
      Match quality of the ``unit`` field.

   mq_placename : float
      Match quality of the resulting place name against the input query.

   mq_ontologyname : float
      Match quality of the resulting ontology name against the input query.

   Finally, the dataframe always contains the following error information
   columns. These contain values only if the corresponding query could not be
   executed for some reason.

   error_code : str
      String indicating the type of error.

   error_message : str
      Human-readable error message.

   .. _coder-poi-queries:

   POI Queries
   ===========

   Search for points of interest (POI) around given positions.

   .. _coder-poi-query-options:

   POI Query Options
   -----------------

   address_details : bool
      Include additional address details in the result.

   coordinates : bool
      Include numeric coordinate columns in the result.

   category_codes : bool
      Include HERE category, chain and food type identifiers in the result.

   .. _coder-poi-input-columns:

   POI Input Columns
   -----------------

   The following columns will be read from the input dataframe:

   id : Any
      Fixed identifier to be added to each result of this query.

   position : :class:`~shapely.Point`
      The geographical center of the search. Instead of a geometry object, you
      may also specify this as two separate fields ``position_latitude`` and
      ``position_longitude`` of type :class:`float`.

   language : str
      The preferred language for the response. This must be a valid `IETF
      BCP47`_ language tag, such as ``"en-US"``, or a comma-separated list of
      such tags in order of preference.

   political_view : str
      The political view of the query regarding disputed territories. This must
      be a valid `ISO 3166-1 alpha-3`_ country code.

   limit : int
      Limit on the number of results to return for each query. Must be between 1
      and 100. If unset, the default limit will be used.

   countries : str | list[str]
      If set, the search is limited to the specified countries. Must be a
      sequence of valid `ISO 3166-1 alpha-3`_ country codes. This parameter
      treats a comma-separated string as a list of strings.

   address_names_mode : str
      How to handle places with multiple names.

      -  ``"default"`` -- Prefer matched names for administrative places and
         normalized names for street names.
      -  ``"matched"`` -- Prefer names that match the input query.
      -  ``"normalized"`` -- Prefer the official names of places.

   postal_code_mode : str
      How to handle postal codes spanning multiple cities or districts.

      -  ``"default"`` -- Return only one result per postal code, leaving the
         city or district name blank if necessary.
      -  ``"cityLookup"`` -- When a postal code spans multiple cities, return
         all possible combinations of the postal code with the corresponding
         city names.
      -  ``"districtLookup"`` -- When a postal code spans multiple districts,
         return all possible combinations of the postal code with the
         corresponding city and district names.

   .. _coder-poi-output-columns:

   POI Output Columns
   ------------------

   The resulting dataframe contains the following columns:

   id : Any
      Fixed identifier added to each result of a query.

   subid : int
      Numeric index of the result starting from zero.

   title : str
      Localized display name of this result item.

   resulttype : str
      The type of the result item.

   position : :class:`~shapely.Point`
      The coordinates of a pin on a map corresponding to the item.

   navigation : :class:`~shapely.Point`
      The coordinates of a navigation point corresponding to the item.

   distance : int
      The distance from the search position to the result item in meters.

   timestamp : datetime
      Timestamp of when this result was created.

   When ``address_details`` is ``True``, the dataframe also contains the
   following columns:

   postaladdress : str
      Full address of the item, formatted according to the regional postal
      rules. May not include all address components.

   country : str
      Name of the country.

   countrycode : str
      `ISO 3166-1 alpha-3`_ country code of the country.

   state : str
      Name of the state within the country.

   statecode : str
      Code or abbreviation of the state.

   county : str
      Name of the county or subdivision within the state.

   countycode : str
      Code or abbreviation of the county.

   city : str
      Name of the city.

   district : str
      Name of the district within the city.

   subdistrict : str
      Name of the subdistrict within the city.

   street : str
      Name of the street.

   streets : list[str]
      List of street names on an intersection.

   block : str
      Name of the city block.

   subblock : str
      Name of the subblock within the city block.

   postalcode : str
      Postal code associated with the item.

   housenumber : str
      House number, including associated qualifiers.

   building : str
      Name of the building.

   unit : str
      Information about the unit within the building.

   When ``coordinates`` is True, the dataframe also contains the following
   columns:

   position_longitude : float
      Longitude of the item’s position.

   position_latitude : float
      Latitude of the item’s position.

   navigation_longitude : float
      Longitude of the navigation point.

   navigation_latitude : float
      Latitude of the navigation point.

   When ``category_codes`` is ``True``, the dataframe also contains the
   following columns:

   here_categories : list[str]
      List of `HERE category identifiers`_ assigned to the item.

   here_chains : list[str]
      List of `HERE chain identifiers`_ assigned to the item.

   here_foodtypes : list[str]
      List of `HERE food type identifiers`_ assigned to the item.

   Finally, the dataframe always contains the following error information
   columns. These contain values only if the corresponding query could not be
   executed for some reason.

   error_code : str
      String indicating the type of error.

   error_message : str
      Human-readable error message.

   -----------------------------------------------------------------------------


.. _HERE category identifiers: https://docs.here.com/geocoding-and-search/docs/places-category-system-full
.. _HERE chain identifiers: https://docs.here.com/geocoding-and-search/docs/places-categories-and-cuisines
.. _HERE food type identifiers: https://docs.here.com/geocoding-and-search/docs/food-types-category-system-full
.. _IETF BCP47: https://en.wikipedia.org/wiki/IETF_language_tag
.. _ISO 3166-1 alpha-3: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3
