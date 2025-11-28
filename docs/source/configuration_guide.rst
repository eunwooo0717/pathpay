Configuration Guide
===================

PathPay is configurable through CLI flags and environment variables. This guide
summarizes each option and suggested defaults.

Environment variables
---------------------

``KAKAO_REST_API_KEY``
   Required. Kakao REST API key with Local + Mobility scopes. Set it before
   running the CLI: ``export KAKAO_REST_API_KEY=...``.

``HTTP(S)_PROXY`` / ``NO_PROXY``
   Optional. Standard proxy variables honored by the ``requests`` library, if
   your network requires them.

CLI arguments
-------------

``--csv`` (repeatable)
   Explicit CSV files to load. Useful when you want to analyze a curated subset.

``--csv_dir``
   Directory that contains ``*.csv`` files. Combine with ``--csv`` if needed.

``--fuel`` (default: 휘발유)
   Fuel column to optimize. Valid values: ``휘발유``, ``경유``, ``고급휘발유``.

``--liters`` (default: 40)
   Planned fueling volume. Increasing this magnifies the effect of price
   differences and detour penalties.

``--eff`` (required)
   Vehicle efficiency in km/L. Used to convert detour kilometers into fuel cost.

``--alpha`` (default: 600)
   Monetary value of time per minute in KRW. For commercial fleets you can bump
   this higher to penalize time-consuming detours.

``--origin`` / ``--dest`` (required)
   Textual addresses that Kakao Local can resolve.

``--debug``
   Prints warnings when Kakao API calls fail or responses are missing data.

``--save_map`` (map script only)
   Output path for the Folium HTML map.

Tuning parameters in code
-------------------------

``ROUTE_BUFFER_KM``
   Candidate band around the straight-line path (defaults to 1 km). Increase if
   you want to inspect stations farther away from the route.

``TOPK_BY_PRICE``
   Number of cheapest stations (after preselection) to evaluate via Kakao
   Mobility. Balances accuracy vs. API usage.

``REQUEST_TIMEOUT``
   Timeout in seconds for HTTP calls. Raise this if you encounter slow network
   responses.

Customization tips
------------------

* **Different regions** – Modify the regular expression in
  ``load_and_prepare`` to include additional districts or provinces.
* **Alternate scoring** – Adjust the ``effective_unit`` calculation or add
  additional terms (e.g., tolls, waiting time) inside ``evaluate_total_cost``.
* **Output format** – Wrap the calculation functions inside a REST API, Slack
  bot, or GUI by importing them directly. The CLI entry point is small and easy
  to replace.
