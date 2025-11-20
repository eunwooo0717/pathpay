#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
총비용(연료비 + 우회연료비 + 시간가치) 최소화 주유소 추천
- 지역: 광진구 + 송파구 (CSV 내부 필터)
- 입력 CSV: 번호, 지역, 상호, 주소, 기간, 상표, 셀프여부, 고급휘발유, 휘발유, 경유, 실내등유
- 차량 연비(--eff), 주유량(--liters), 시간가치(--alpha) 입력
- Kakao 지오코딩 + 길찾기 사용 (REST API 키 필요)
"""

import os
import math
import json
import time
import glob
import argparse
from typing import List, Dict, Tuple, Optional

import pandas as pd
import requests

# ============================
# 설정
# ============================

KAKAO_REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY", "")

# Kakao Local (지오코딩)
KAKAO_LOCAL_SEARCH_URL = "https://dapi.kakao.com/v2/local/search/address.json"

# Kakao Mobility Directions (문서에 따라 GET/POST 모두 지원 → 우선 GET, 실패 시 POST 폴백)
KAKAO_MOBILITY_ROUTE_URL = "https://apis-navi.kakaomobility.com/v1/directions"

# 후보/성능 파라미터
ROUTE_BUFFER_KM = 1.0     # 직선 경로 ±1km 근사
TOPK_BY_PRICE = 15        # 정밀 평가 후보 수
REQUEST_TIMEOUT = 10      # 초

# ============================
# 유틸
# ============================

def kakao_headers() -> Dict[str, str]:
    if not KAKAO_REST_API_KEY:
        raise RuntimeError("환경변수 KAKAO_REST_API_KEY가 설정되지 않았습니다.")
    return {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}

def haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = phi2 - phi1
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2*R*math.asin(math.sqrt(a))

def point_to_segment_distance_km(px, py, ax, ay, bx, by) -> float:
    """점 P와 선분 AB 거리(근거리 평면근사)."""
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
    """주소 → (lat, lon). 실패 시 None"""
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

# ---------- Directions: GET 우선, POST 폴백 ----------

def _kakao_route_request(params=None, json_body=None):
    headers = {**kakao_headers(), "Content-Type": "application/json"}

    # 1) GET 우선
    if params:
        r = requests.get(KAKAO_MOBILITY_ROUTE_URL, params=params,
                         headers=headers, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            return r.json()
        # 405/4xx면 POST 폴백 시도

    # 2) POST 폴백
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

def route_distance_time(A: Tuple[float, float], B: Tuple[float, float]) -> Tuple[float, float]:
    """A→B 거리(km)·시간(분). GET→POST 폴백."""
    get_params = {
        "origin": f"{A[1]},{A[0]}",         # x=lon, y=lat
        "destination": f"{B[1]},{B[0]}",
        # "priority": "TIME", "alternatives": "false", ... 필요 시 추가
    }
    post_body = {
        "origin": {"x": A[1], "y": A[0]},
        "destination": {"x": B[1], "y": B[0]},
    }
    data = _kakao_route_request(params=get_params, json_body=post_body)
    return _parse_route_summary(data)

def route_via_distance_time(A: Tuple[float, float], S: Tuple[float, float], B: Tuple[float, float]) -> Tuple[float, float]:
    """A→S→B 경유 거리(km)·시간(분). GET→POST 폴백."""
    get_params = {
        "origin": f"{A[1]},{A[0]}",
        "destination": f"{B[1]},{B[0]}",
        "waypoints": f"{S[1]},{S[0]}",      # 여러 개면 'x1,y1|x2,y2'
    }
    post_body = {
        "origin": {"x": A[1], "y": A[0]},
        "destination": {"x": B[1], "y": B[0]},
        "waypoints": [{"name": "FUEL", "x": S[1], "y": S[0]}],
    }
    data = _kakao_route_request(params=get_params, json_body=post_body)
    return _parse_route_summary(data)

def kakao_map_deeplink_route(Aname: str, A: Tuple[float,float], Bname: str, B: Tuple[float,float],
                             Sname: Optional[str]=None, S: Optional[Tuple[float,float]]=None) -> str:
    """간단 딥링크(지도 열기). 실제 네비는 KakaoNavi 스킴 권장."""
    base = "https://map.kakao.com/link/"
    if S and Sname:
        return f"{base}to/{Sname},{S[0]},{S[1]}"
    return f"{base}to/{Bname},{B[0]},{B[1]}"

# ============================
# 데이터 처리
# ============================

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
        raise RuntimeError(f"CSV 칼럼 부족. 최소 {required} 필요. 실제: {set(df.columns)}")

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
        time.sleep(0.2)  # Rate limit 보호
    return df.assign(lat=lats, lon=lons).dropna(subset=["lat","lon"])

def preselect_candidates(df: pd.DataFrame, A: Tuple[float,float], B: Tuple[float,float], fuel_col: str) -> pd.DataFrame:
    dists = [point_to_segment_distance_km(lat, lon, A[0], A[1], B[0], B[1])
             for lat, lon in zip(df["lat"], df["lon"])]
    df = df.assign(dist_to_line_km=dists)
    df = df[df["dist_to_line_km"] <= ROUTE_BUFFER_KM + 0.2]
    df = df.dropna(subset=[fuel_col])
    df = df.sort_values(by=[fuel_col, "dist_to_line_km"], ascending=[True, True]).head(TOPK_BY_PRICE)
    return df

def evaluate_total_cost(station_row: pd.Series,
                        A: Tuple[float,float], B: Tuple[float,float],
                        fuel_eff_km_per_L: float, liters: float, alpha_won_per_min: float,
                        fuel_col: str, avg_price_won_per_L: float) -> Dict:
    S = (station_row["lat"], station_row["lon"])
    via_dist_km, via_time_min = route_via_distance_time(A, S, B)
    base_dist_km, base_time_min = route_distance_time(A, B)
    d_detour = max(0.0, via_dist_km - base_dist_km)
    t_detour = max(0.0, via_time_min - base_time_min)

    detour_fuel_cost = (d_detour / fuel_eff_km_per_L) * avg_price_won_per_L
    detour_time_cost = t_detour * alpha_won_per_min
    station_price = float(station_row[fuel_col])

    total_cost = station_price * liters + detour_fuel_cost + detour_time_cost
    effective_unit = total_cost / liters

    return {
        "name": station_row["상호"],
        "brand": station_row.get("상표",""),
        "addr": station_row["주소"],
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

# ============================
# 메인
# ============================

def main():
    ap = argparse.ArgumentParser(description="광진/송파 주유소 총비용 최적 추천")
    ap.add_argument("--csv", nargs="*", help="주유소 CSV 경로(여러 개 가능)")
    ap.add_argument("--csv_dir", help="CSV 폴더 경로(*.csv 자동 수집)")
    ap.add_argument("--fuel", choices=["휘발유","경유","고급휘발유"], default="휘발유", help="연료")
    ap.add_argument("--liters", type=float, default=40.0, help="주유량(L)")
    ap.add_argument("--eff", type=float, required=True, help="차량 연비(km/L)")
    ap.add_argument("--alpha", type=float, default=600.0, help="시간가치(₩/분)")
    ap.add_argument("--origin", required=True, help="출발지 주소")
    ap.add_argument("--dest", required=True, help="도착지 주소")
    ap.add_argument("--debug", action="store_true", help="디버그 로그")
    args = ap.parse_args()

    # CSV 리스트
    csv_list: List[str] = []
    if args.csv:
        csv_list.extend(args.csv)
    if args.csv_dir:
        csv_list.extend(sorted(glob.glob(os.path.join(args.csv_dir, "*.csv"))))
    if not csv_list:
        raise RuntimeError("--csv 또는 --csv_dir 중 하나는 지정하세요.")

    # 데이터 로드 → 필터 → 가격 정리
    df = load_and_prepare(csv_list)
    if df.empty:
        print("광진구/송파구 데이터가 없습니다."); return

    # 좌표 확보
    df = ensure_geocodes(df)
    if df.empty:
        print("지오코딩 성공한 주유소가 없습니다."); return

    # 출발/도착 좌표
    A = geocode_address(args.origin)
    B = geocode_address(args.dest)
    if not A or not B:
        raise RuntimeError("출발지/도착지 지오코딩 실패")

    # 후보
    cand = preselect_candidates(df, A, B, args.fuel)
    if cand.empty:
        print("후보 주유소가 없습니다(버퍼 기준)."); return

    # 평균유가(우회연료비용 계산용) → 간단히 후보 평균으로 근사
    avg_price = float(cand[args.fuel].mean())

    # 정밀 평가
    results = []
    for _, row in cand.iterrows():
        try:
            info = evaluate_total_cost(
                row, A, B,
                fuel_eff_km_per_L=args.eff,
                liters=args.liters,
                alpha_won_per_min=args.alpha,
                fuel_col=args.fuel,
                avg_price_won_per_L=avg_price
            )
            results.append(info)
        except Exception as e:
            if args.debug:
                print(f"[WARN] {row.get('상호','?')} 경유 계산 실패: {e}")
            continue
        time.sleep(0.1)  # 레이트리밋 보호

    if not results:
        print("정밀 평가 결과가 없습니다."); return

    # 랭킹
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

    # 무경유 대비 간단 비교(평균가 근사)
    base_total = avg_price * args.liters
    gain = base_total - best["total_cost"]

    deeplink = kakao_map_deeplink_route(
        Aname="출발", A=A, Bname="도착", B=B,
        Sname=best["name"], S=(best["lat"], best["lon"])
    )

    print("=== 의사결정 ===")
    if gain > 0:
        print(f"→ 경유 추천: {best['name']} 로 들르면 총비용 {int(gain)}₩ 절감(근사).")
        print(f"경유 안내(첫 단계): {deeplink}")
        print("※ 실제 네비 시작은 KakaoNavi 스킴 사용 권장.")
    else:
        print("→ 지금은 경유하지 않는 것이 더 이득이거나 차이가 미미합니다.")

if __name__ == "__main__":
    main()
