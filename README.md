# PathPay
PathPay recommends the gas station with the **lowest total cost (fuel price + detour fuel + time value)** when you drive between Seoul’s Gwangjin and Songpa districts. It relies on Kakao’s APIs to geocode addresses, evaluate detours, and quantify whether a stopover is worth it.

## Documentation
- Read the full guide on ReadTheDocs: https://pathpay.readthedocs.io/
- Build locally: `cd docs && pip install -r requirements.txt && make html`

## Website
- The GitHub Pages site lives in `website/`.
- Preview locally: `cd website && bundle install && bundle exec jekyll serve`
- When GitHub Pages is enabled it will publish to `https://eunwooo0717.github.io/pathpay`

## Features
- Merge multiple CSV files and keep only stations in Gwangjin/Songpa
- Geocode addresses through the Kakao Local API and fetch distance/time using Kakao Mobility Directions
- Preselect stations within a configurable buffer around the main route for faster evaluation
- Compute detour fuel, time cost, total cost, and effective price per liter
- Print the best station, the top 3 candidates, and a Kakao Map deeplink in the console

## Requirements
- Python 3.9+
- Libraries: `pandas`, `requests`
- Kakao REST API key (Local + Mobility permissions)
- CSV files containing at least `지역`, `상호`, `주소`, and price columns such as `휘발유`, `경유`, `고급휘발유`

```bash
pip install pandas requests
export KAKAO_REST_API_KEY="your_rest_api_key"
```

Data can come from Opinet or any custom source, and you can provide multiple files at once.

## Usage
Run `fuel_route_recommender.py` with CSV inputs plus driving parameters:

```bash
python fuel_route_recommender.py \
  --csv_dir price_csv \            # or --csv file1.csv file2.csv ...
  --fuel 휘발유 \
  --liters 40 \
  --eff 12.5 \
  --alpha 600 \
  --origin "서울 광진구 ..." \
  --dest "서울 송파구 ..."
```

### Important options
- `--csv` / `--csv_dir`: CSV files or a directory containing them
- `--fuel`: Fuel type (`휘발유`, `경유`, `고급휘발유`)
- `--liters`: Amount of fuel to purchase (L)
- `--eff`: Vehicle fuel economy (km/L) **required**
- `--alpha`: Time value in KRW per minute (default 600)
- `--origin`, `--dest`: Origin/destination addresses **required**
- `--debug`: Print warnings if Kakao API calls fail

## Sample output
```
=== Top 3 (by effective price) ===
[1] Station A (Brand)  Seoul ...
  Price: 1479 ₩/L | Effective: 1505 ₩/L
  Detour: +0.80 km, +1.2 min  (Fuel 200₩, Time 720₩)
  Total cost: 60,200 ₩

=== Decision ===
→ Recommended: stopping at Station A saves about 1,800₩.
Map shortcut: https://map.kakao.com/link/to/...
```
If the `gain` value is negative, the script tells you that skipping the detour is cheaper.

## Notes
- Kakao Mobility Directions has quota limits; the script throttles requests, but heavy use may still hit the rate limit.
- For real navigation, replace the printed URL with the KakaoNavi scheme.
- The dataset is currently filtered to Gwangjin/Songpa. Modify `load_and_prepare` if you need different regions.

## License
Distributed under the [Apache License 2.0](LICENSE).
