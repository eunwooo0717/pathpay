How to Use PathPay
==================

This section demonstrates typical CLI workflows and expected outputs.

Basic invocation
----------------

.. code-block:: bash

   python fuel_route_recommender.py \
     --csv_dir price_csv \
     --fuel 휘발유 \
     --liters 40 \
     --eff 12.5 \
     --alpha 600 \
     --origin "서울특별시 광진구 세종대길 1" \
     --dest "서울특별시 송파구 올림픽로 300"

Explanation of core parameters:

* ``--csv_dir`` – Directory containing station CSVs (alternatively pass one or
  more ``--csv`` paths).
* ``--fuel`` – Fuel type column to optimize (휘발유, 경유, 고급휘발유).
* ``--liters`` – Planned fueling amount so total cost can be computed.
* ``--eff`` – Vehicle efficiency in km/L (required).
* ``--alpha`` – Value of time in KRW per minute (defaults to 600).
* ``--origin`` / ``--dest`` – Text addresses that Kakao Local can geocode.

Sample output
-------------

.. code-block:: text

   === 추천 Top 3 (유효단가 기준) ===
   [1] OO주유소 (SK)  서울시 송파구 ...
     주유단가: 1479 ₩/L | 유효단가: 1505 ₩/L
     우회: +0.80 km, +1.2 분  (연료비 200₩, 시간비 720₩)
     총비용: 60200 ₩

   === 의사결정 ===
   → 경유 추천: OO주유소 로 들르면 총비용 1800₩ 절감(근사).
   경유 안내(첫 단계): https://map.kakao.com/link/to/...

Interpretation tips
-------------------

* **유효단가 (effective price)** – The per-liter cost after factoring in detour
  time and fuel penalties. This is the primary ranking metric.
* **우회 metrics** – Positive values indicate additional distance/time compared
  to driving directly from origin to destination. Large detours can negate
  cheap fuel prices.
* **Gain estimate** – ``gain = avg_price * liters - best.total_cost``. If the
  number is negative, skip the detour.

Optional map export
-------------------

Use the companion script to render Folium HTML maps:

.. code-block:: bash

   python fuel_route_recommender_with_map.py \
     --csv_dir price_csv \
     --eff 12.5 --liters 40 --fuel 휘발유 \
     --origin "..." --dest "..." \
     --save_map recommend_map.html

Open the generated HTML file in a browser to visualize start/end points and the
top 3 stations along the route.

