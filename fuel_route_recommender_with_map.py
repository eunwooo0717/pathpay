
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
총비용(연료비 + 우회연료비 + 시간가치) 최소화 주유소 추천 + 지도 시각화.

기능:

* 기존 CLI 기능 그대로 + ``--save_map <파일경로.html>`` 옵션 제공.
* Folium(Leaflet)로 출발지/도착지/Top3 마커와 직선 경로(A→B, A→S→B)를 표시
  한다. (주의: 실제 도로 폴리라인이 아닌 단순 지오메트리 직선입니다. Directions
  폴리라인을 쓰려면 Kakao API 응답을 파싱해 확장하세요.)
"""

import os, math, json, time, glob, argparse
from typing import List, Dict, Tuple, Optional
import pandas as pd
import requests

# 지도
try:
    import folium
except ImportError:
    folium = None

KAKAO_REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY", "")
KAKAO_LOCAL_SEARCH_URL = "https://dapi.kakao.com/v2/local/search/address.json"
KAKAO_MOBILITY_ROUTE_URL = "https://apis-navi.kakaomobility.com/v1/directions"

ROUTE_BUFFER_KM = 1.0
TOPK_BY_PRICE = 15
REQUEST_TIMEOUT = 10

def kakao_headers() -> Dict[str, str]:
    if not KAKAO_REST_API_KEY:
        raise RuntimeError("환경변수 KAKAO_REST_API_KEY가 설정되지 않았습니다.")
    return {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}

def point_to_segment_distance_km(px, py, ax, ay, bx, by) -> float:
    def to_xy(lat, lon):
        x = lon * 111.320 * math.cos(math.radians(lat))
        y = lat * 110.574
        return x, y
    px_, py_ = to_xy(px, py)
    ax_, ay_ = to_xy(ax, ay)
    bx_, by_ = to_xy(bx, by)
    abx, aby = bx_ - ax_, by_ - ay_
    apx, apy = px_ - ax_, py_ - ay_
    ab2 = abx*abx + aby*aby
    t = 0.0 if ab2 == 0 else max(0.0, min(1.0, (apx*abx + apy*aby)/ab2))
    cx, cy = ax_ + t*abx, ay_ + t*aby
    dx, dy = px_ - cx, py_ - cy
    return math.sqrt(dx*dx + dy*dy)

def geocode_address(addr: str) -> Optional[Tuple[float, float]]:
    params = {"query": addr}
    try:
        r = requests.get(KAKAO_LOCAL_SEARCH_URL, params=params,
                         headers=kakao_headers(), timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        docs = r.json().get("documents", [])
        if not docs:
            return None
        y = float(docs[0]["y"])  # lat
        x = float(docs[0]["x"])  # lon
        return (y, x)
    except Exception:
        return None

def _kakao_route_request(params=None, json_body=None):
    headers = {**kakao_headers(), "Content-Type": "application/json"}
    if params:
        r = requests.get(KAKAO_MOBILITY_ROUTE_URL, params=params,
                         headers=headers, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            return r.json()
    if json_body:
        r = requests.post(KAKAO_MOBILITY_ROUTE_URL, json=json_body,
                          headers=headers, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()
    raise RuntimeError("Directions 요청에 params/json_body가 없습니다.")

def _parse_route_summary(data):
    routes = data.get("routes", [])
    if not routes:
        raise RuntimeError(f"Directions 응답에 routes 없음: {data}")
    summary = routes[0].get("summary", {})
    dist_km = summary.get("distance", 0) / 1000.0
    time_min = summary.get("duration", 0) / 60.0
    return dist_km, time_min

def route_distance_time(A, B):
    get_params = {
        "origin": f"{A[1]},{A[0]}",
        "destination": f"{B[1]},{B[0]}",
    }
    post_body = {
        "origin": {"x": A[1], "y": A[0]},
        "destination": {"x": B[1], "y": B[0]},
    }
    data = _kakao_route_request(params=get_params, json_body=post_body)
    return _parse_route_summary(data)

def route_via_distance_time(A, S, B):
    get_params = {
        "origin": f"{A[1]},{A[0]}",
        "destination": f"{B[1]},{B[0]}",
        "waypoints": f"{S[1]},{S[0]}",
    }
    post_body = {
        "origin": {"x": A[1], "y": A[0]},
        "destination": {"x": B[1], "y": B[0]},
        "waypoints": [{"name": "FUEL", "x": S[1], "y": S[0]}],
    }
    data = _kakao_route_request(params=get_params, json_body=post_body)
    return _parse_route_summary(data)

def kakao_map_deeplink_route(Aname, A, Bname, B, Sname=None, S=None) -> str:
    base = "https://map.kakao.com/link/"
    if S and Sname:
        return f"{base}to/{Sname},{S[0]},{S[1]}"
    return f"{base}to/{Bname},{B[0]},{B[1]}"

def load_and_prepare(csv_paths: List[str]) -> pd.DataFrame:
    frames = []
    for p in csv_paths:
        ok = False
        for enc in ("utf-8-sig", "cp949", "euc-kr", "utf-8"):
            try:
                frames.append(pd.read_csv(p, encoding=enc))
                ok = True
                break
            except Exception:
                continue
        if not ok:
            raise RuntimeError(f"CSV 읽기 실패: {p}")
    df = pd.concat(frames, ignore_index=True)
    required = {"지역", "상호", "주소"}
    if not required.issubset(df.columns):
        raise RuntimeError(f"CSV 칼럼 부족. 최소 {required} 필요.")
    df = df.dropna(subset=["주소","지역","상호"])
    df = df[df["지역"].astype(str).str.contains("광진구|송파구", na=False)]
    for col in ["휘발유","경유","고급휘발유","실내등유"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def ensure_geocodes(df: pd.DataFrame) -> pd.DataFrame:
    if "lat" in df.columns and "lon" in df.columns and df["lat"].notna().any():
        return df.dropna(subset=["lat","lon"])
    lats, lons = [], []
    for addr in df["주소"].tolist():
        loc = geocode_address(addr)
        if loc is None:
            lats.append(float("nan")); lons.append(float("nan"))
        else:
            lats.append(loc[0]); lons.append(loc[1])
        time.sleep(0.2)
    return df.assign(lat=lats, lon=lons).dropna(subset=["lat","lon"])

def preselect_candidates(df: pd.DataFrame, A, B, fuel_col: str) -> pd.DataFrame:
    dists = [point_to_segment_distance_km(lat, lon, A[0], A[1], B[0], B[1])
             for lat, lon in zip(df["lat"], df["lon"])]
    df = df.assign(dist_to_line_km=dists)
    df = df[df["dist_to_line_km"] <= ROUTE_BUFFER_KM + 0.2]
    df = df.dropna(subset=[fuel_col])
    df = df.sort_values(by=[fuel_col, "dist_to_line_km"], ascending=[True, True]).head(TOPK_BY_PRICE)
    return df

def evaluate_total_cost(row, A, B, eff, liters, alpha, fuel_col, avg_price):
    S = (row["lat"], row["lon"])
    via_dist_km, via_time_min = route_via_distance_time(A, S, B)
    base_dist_km, base_time_min = route_distance_time(A, B)
    d_detour = max(0.0, via_dist_km - base_dist_km)
    t_detour = max(0.0, via_time_min - base_time_min)
    detour_fuel_cost = (d_detour / eff) * avg_price
    detour_time_cost = t_detour * alpha
    station_price = float(row[fuel_col])
    total_cost = station_price * liters + detour_fuel_cost + detour_time_cost
    effective_unit = total_cost / liters
    return {
        "name": row["상호"],
        "brand": row.get("상표",""),
        "addr": row["주소"],
        "lat": S[0], "lon": S[1],
        "station_price": station_price,
        "via_dist_km": via_dist_km, "via_time_min": via_time_min,
        "base_dist_km": base_dist_km, "base_time_min": base_time_min,
        "detour_km": d_detour, "detour_min": t_detour,
        "detour_fuel_cost": detour_fuel_cost,
        "detour_time_cost": detour_time_cost,
        "total_cost": total_cost,
        "effective_unit": effective_unit,
    }

def make_map_html(path, A, B, top3):
    if folium is None:
        raise RuntimeError("folium이 설치되어 있지 않습니다. `pip install folium` 후 --save_map 사용 가능.")
    center_lat = (A[0] + B[0]) / 2
    center_lon = (A[1] + B[1]) / 2
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    folium.Marker(A, tooltip="출발지", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(B, tooltip="도착지", icon=folium.Icon(color="red")).add_to(m)
    colors = ["blue", "cadetblue", "lightblue"]
    for i, r in enumerate(top3):
        popup = folium.Popup(f"""
        <b>#{i+1} {r['name']}</b><br/>
        단가: {int(r['station_price'])} ₩/L<br/>
        유효단가: {int(r['effective_unit'])} ₩/L<br/>
        우회: +{r['detour_km']:.2f} km, +{r['detour_min']:.1f} 분<br/>
        총비용: {int(r['total_cost'])} ₩
        """, max_width=300)
        folium.Marker(
            [r["lat"], r["lon"]],
            tooltip=f"#{i+1} {r['name']}",
            popup=popup,
            icon=folium.Icon(color=colors[i if i < len(colors) else -1])
        ).add_to(m)
    folium.PolyLine([A, B], tooltip="Baseline A→B", weight=4).add_to(m)
    best = top3[0]
    S = (best["lat"], best["lon"])
    folium.PolyLine([A, S, B], tooltip="Recommended A→S→B (straight)", weight=4).add_to(m)
    m.save(path)
    return path

def main():
    ap = argparse.ArgumentParser(description="광진/송파 주유소 총비용 최적 추천 + 지도 시각화")
    ap.add_argument("--csv", nargs="*", help="주유소 CSV 경로(여러 개 가능)")
    ap.add_argument("--csv_dir", help="CSV 폴더 경로(*.csv 자동 수집)")
    ap.add_argument("--fuel", choices=["휘발유","경유","고급휘발유"], default="휘발유")
    ap.add_argument("--liters", type=float, default=40.0)
    ap.add_argument("--eff", type=float, required=True)
    ap.add_argument("--alpha", type=float, default=600.0)
    ap.add_argument("--origin", required=True)
    ap.add_argument("--dest", required=True)
    ap.add_argument("--save_map", help="지도를 저장할 HTML 경로 (예: /path/map.html)")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    csv_list: List[str] = []
    if args.csv:
        csv_list.extend(args.csv)
    if args.csv_dir:
        csv_list.extend(sorted(glob.glob(os.path.join(args.csv_dir, "*.csv"))))
    if not csv_list:
        raise RuntimeError("--csv 또는 --csv_dir 중 하나는 지정하세요.")

    df = load_and_prepare(csv_list)
    if df.empty:
        print("광진구/송파구 데이터가 없습니다."); return
    df = ensure_geocodes(df)
    if df.empty:
        print("지오코딩 성공한 주유소가 없습니다."); return
    A = geocode_address(args.origin)
    B = geocode_address(args.dest)
    if not A or not B:
        raise RuntimeError("출발지/도착지 지오코딩 실패")
    cand = preselect_candidates(df, A, B, args.fuel)
    if cand.empty:
        print("후보 주유소가 없습니다(버퍼 기준)."); return
    avg_price = float(cand[args.fuel].mean())

    results = []
    for _, row in cand.iterrows():
        try:
            info = evaluate_total_cost(
                row, A, B, eff=args.eff, liters=args.liters, alpha=args.alpha,
                fuel_col=args.fuel, avg_price=avg_price
            )
            results.append(info)
        except Exception as e:
            if args.debug:
                print(f"[WARN] {row.get('상호','?')} 경유 계산 실패: {e}")
            continue
        time.sleep(0.1)

    if not results:
        print("정밀 평가 결과가 없습니다."); return

    results.sort(key=lambda x: x["effective_unit"])
    best = results[0]

    print("\n=== 추천 Top 3 (유효단가 기준) ===")
    for i, r in enumerate(results[:3], 1):
        print(f"[{i}] {r['name']} ({r['brand']})  {r['addr']}")
        print(f"  주유단가: {int(r['station_price'])} ₩/L | 유효단가: {int(r['effective_unit'])} ₩/L")
        print(f"  우회: +{r['detour_km']:.2f} km, +{r['detour_min']:.1f} 분  "
              f"(연료비 {int(r['detour_fuel_cost'])}₩, 시간비 {int(r['detour_time_cost'])}₩)")
        print(f"  총비용: {int(r['total_cost'])} ₩")
        print()

    base_total = avg_price * args.liters
    gain = base_total - best["total_cost"]
    deep = kakao_map_deeplink_route("출발", A, "도착", B, best["name"], (best["lat"], best["lon"]))
    print("=== 의사결정 ===")
    if gain > 0:
        print(f"→ 경유 추천: {best['name']} 로 들르면 총비용 {int(gain)}₩ 절감(근사).")
        print(f"경유 안내(첫 단계): {deep}")
    else:
        print("→ 지금은 경유하지 않는 것이 더 이득이거나 차이가 미미합니다.")

    if args.save_map:
        if folium is None:
            print("folium 미설치로 지도 저장을 건너뜁니다. `pip install folium` 후 --save_map 사용 가능.")
        else:
            out = make_map_html(args.save_map, A, B, results[:3])
            print(f"[OK] 지도 저장: {out}")

if __name__ == "__main__":
    main()
