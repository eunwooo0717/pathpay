Technical Overview
==================

PathPay intentionally keeps a compact architecture: one primary CLI file plus a
map-enabled variant. This section highlights the main components and data flow.

High-level architecture
-----------------------

1. **CSV ingestion** – ``load_and_prepare`` concatenates every file passed via
   ``--csv``/``--csv_dir`` and filters rows to Gwangjin/Songpa.
2. **Geocoding** – ``ensure_geocodes`` keeps existing ``lat``/``lon`` values
   and calls Kakao Local for the missing ones.
3. **Candidate preselection** – ``preselect_candidates`` keeps stations that lie
   within ~1 km of the straight-line path and sorts by price and proximity.
4. **Cost evaluation** – ``evaluate_total_cost`` compares the baseline route
   against the detour using Kakao Mobility Directions to compute distance/time
   deltas and monetary impact.
5. **Presentation** – Results are sorted by effective price and printed, and a
   Kakao Map deeplink is generated for the best choice. The map variant can also
   produce Folium HTML visualizations.

Key modules
-----------

``fuel_route_recommender.py``
   * Parses CLI arguments and orchestrates the run.
   * Loads and filters CSVs for Gwangjin/Songpa.
   * Geocodes stations if latitude/longitude is missing.
   * Calls Kakao Mobility for baseline and detour routes.
   * Calculates total cost, effective price, and prints the top 3 results.

``fuel_route_recommender_with_map.py``
   * Extends the base logic with ``--save_map`` to render Folium maps.
   * Adds markers for origin, destination, and top 3 stations and draws simple
     polylines (straight lines, not polyline traces from Directions).

Technologies
------------

* **Python Standard Library** – Argument parsing, math utilities, filesystem
  access, rate limiting via ``time.sleep``.
* **Pandas** – Concatenating and cleaning CSVs, numeric conversion, and sorting
  candidates.
* **Requests** – HTTP calls to Kakao Local and Mobility REST APIs.
* **Folium (optional)** – Static HTML map generation.

API integrations
----------------

* **Kakao Local Search** – ``/v2/local/search/address.json`` service used to
  convert textual addresses into WGS84 coordinates.
* **Kakao Mobility Directions** – ``/v1/directions`` endpoint used twice per
  station: once for the baseline route (origin → destination) and once for the
  detour (origin → station → destination).
* **Kakao Map Deeplink** – Simple ``https://map.kakao.com/link/to/...`` URLs so
  users can open the recommended stopover directly in the Kakao Map app.

Extensibility hooks
-------------------

* **Broader geography** – Modify ``load_and_prepare`` to adjust the ``지역``
  filter and optionally bring in additional CSV columns.
* **Alternative routing** – Swap out Kakao Mobility with another routing
  provider by implementing equivalents of ``route_distance_time`` and
  ``route_via_distance_time``.
* **Web UI** – Expose the same calculations via FastAPI or Django if you need a
  hosted experience. The CLI’s calculation routines are reusable from other
  entry points.
