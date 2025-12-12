API Reference
=============

The project intentionally exposes most functionality via two modules. This
reference documents the public functions that other tooling can reuse.

fuel_route_recommender
----------------------

.. automodule:: fuel_route_recommender
   :members:
   :undoc-members:
   :show-inheritance:

fuel_route_recommender_with_map
-------------------------------

.. automodule:: fuel_route_recommender_with_map
   :members:
   :undoc-members:
   :show-inheritance:

Function quick reference (core pipeline)
----------------------------------------

- ``load_and_prepare``: 주유소 CSV들을 병합·필터링해 광진/송파 데이터프레임을 만든다.
- ``ensure_geocodes``: 주소 목록을 Kakao Local로 지오코딩해 lat/lon을 채우고 누락 행을 제거한다.
- ``preselect_candidates``: 출발–도착 직선 경로 ±1km 내 주유소 중 최저가 TOP N만 후보로 추린다.
- ``route_distance_time``: Kakao Directions로 A→B 기본 경로 거리/시간을 구한다.
- ``route_via_distance_time``: Kakao Directions로 A→주유소→B 우회 경로 거리/시간을 구한다.
- ``evaluate_total_cost``: 주유 단가 + 우회 연료비 + 우회 시간비를 합산해 총비용·유효단가를 계산한다.
