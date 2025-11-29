---
layout: page
title: ✨ Feature Showcase
permalink: /features
---

# What PathPay Delivers

## Recommendation Engine

- **CSV ingestion & cleaning** – Automatically merges multiple datasets and
  filters to Seoul’s Gwangjin/Songpa stations.
- **Kakao Local geocoding** – Resolves every station address into a precise
  latitude/longitude.
- **Smart candidate selection** – Keeps stations within ±1 km of the route to
  minimize unnecessary API calls.
- **Total cost calculator** – Adds detour fuel and time value to the raw station
  price to compute an “effective price per liter.”

## Driver Experience

- **Top 3 summary** – Console report highlights name, price, detour impact, and
  savings.
- **Kakao Map deeplink** – One-click link launches the recommended station in
  Kakao Map.
- **Folium visualization** – Optional HTML map plots origin, destination, and
  the leading stations.

## Operations

- **Configurable knobs** – Adjust detour buffer, number of candidates, and time
  value to match fleet policies.
- **Extensible APIs** – Core logic is packaged in modules that can be reused
  from web services, schedulers, or notebooks.
- **Documentation-first** – Full setup, architecture, and API docs live on
  [ReadTheDocs]({{ site.docs_url }}).
