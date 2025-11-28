Getting Started
===============

This guide walks through prerequisites, installation, and the minimal setup
needed to run PathPay locally.

Prerequisites
-------------

* **Python** – Version 3.9 or newer.
* **Pip packages** – ``pandas`` and ``requests`` for the CLI, plus ``folium``
  if you plan to generate HTML maps.
* **Kakao REST API key** – Enable both Local API (geocoding) and Mobility
  Directions API (routing) for the same key.
* **Gas price CSV files** – Any CSVs containing Gwangjin/Songpa stations with
  the columns ``지역``, ``상호``, ``주소``, and at least one price column such as
  ``휘발유`` or ``경유``.

Installation steps
------------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/eunwooo0717/pathpay.git
      cd pathpay

2. Install Python dependencies (feel free to use a virtual environment):

   .. code-block:: bash

      pip install pandas requests
      # optional for map output
      pip install folium

3. Export your Kakao key so the CLI can authenticate:

   .. code-block:: bash

      export KAKAO_REST_API_KEY="your_rest_api_key"

CSV preparation
---------------

* Gather the latest CSVs from Opinet or your preferred source.
* Place them in a directory such as ``price_csv/`` inside the repo (the folder
  is ignored by git so you can store proprietary data locally).
* Confirm that the encoding is one of UTF-8, UTF-8 with BOM, EUC-KR, or CP949.
  The loader tries each encoding automatically.

Verification
------------

After installation, run the CLI with ``--help`` to confirm dependencies are in
place:

.. code-block:: bash

   python fuel_route_recommender.py --help

You should see the argument list along with descriptions of each option. If
Python cannot find ``pandas`` or ``requests``, reinstall them in your active
environment.

