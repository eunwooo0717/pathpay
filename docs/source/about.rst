About the Project
=================

PathPay is a decision-support CLI that evaluates whether detouring to a gas
station along a planned route is financially worthwhile. It ingests the latest
price CSVs for stations in Seoul’s Gwangjin and Songpa districts, geocodes each
station with Kakao Local, and queries Kakao Mobility Directions to estimate
detour distance and time. By comparing station fuel prices with the projected
detour cost (extra fuel + time value), PathPay surfaces the top fueling options
that minimize *total* trip cost rather than just price per liter.

Key objectives
--------------

* Present transparent calculations for detour distance, time, and effective
  per-liter cost.
* Integrate smoothly with Kakao REST APIs while respecting rate limits.
* Produce actionable console output (top 3 stations plus Kakao Map deeplink)
  and optional map visualizations.
* Keep the codebase intentionally small (single-file CLI plus map variant) so
  that new contributors can navigate it quickly.

Project scope
-------------

* **Region focus** – Current CSV filtering confines the dataset to Gwangjin and
  Songpa. More districts can be added by adjusting the filter in
  :func:`fuel_route_recommender.load_and_prepare`.
* **Data freshness** – CSVs can be downloaded from Opinet or other data
  sources; PathPay assumes each run points to the latest files.
* **API dependence** – Kakao REST API keys are required; users bring their own
  credentials and manage quota usage.
* **Output medium** – At present the CLI prints textual recommendations. The
  optional ``fuel_route_recommender_with_map.py`` script can save a Folium map
  for richer visualization.

