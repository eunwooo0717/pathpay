# PathPay
서울 광진구·송파구 구간을 주행할 때 **총비용(주유비 + 우회 연료비 + 시간가치)** 가 가장 낮은 주유소를 골라 주는 도구입니다. Kakao 지도 API를 이용해 출발지와 도착지 사이에서 경유 가능한 주유소를 평가하고, 우회를 통해 얻는 이득을 정량적으로 비교할 수 있습니다.

## 주요 기능
- 여러 개의 주유소 CSV를 통합해 광진구/송파구 주유소만 필터링
- Kakao Local API로 주소 지오코딩, Kakao Mobility Directions API로 경로/시간 계산
- 경로 중심선에서 일정 거리 이내의 주유소만 미리 선별해 효율적인 계산
- 우회 시 발생하는 연료비·시간비를 반영한 총비용 및 유효 단가 산출
- 최적 주유소 및 상위 3개 후보, 카카오맵 딥링크까지 콘솔에 출력

## 요구 사항
- Python 3.9 이상
- 라이브러리: `pandas`, `requests`
- Kakao Developers에서 발급한 REST API 키 (Local + Mobility 권한 필요)
- 광진구/송파구 주유소 정보가 담긴 CSV

```bash
pip install pandas requests
export KAKAO_REST_API_KEY="발급받은_키"
```

CSV에는 최소한 `지역`, `상호`, `주소`, 그리고 유가 칼럼(`휘발유`, `경유`, `고급휘발유` 등)이 포함되어야 합니다. 한국석유공사 오피넷(OPEN API)이나 자체 수집 데이터를 사용할 수 있으며, 여러 파일을 한 번에 입력할 수 있습니다.

## 사용법
`fuel_route_recommender.py` 스크립트를 실행해서 추천 결과를 확인합니다.

```bash
python fuel_route_recommender.py \
  --csv_dir price_csv \            # 또는 --csv file1.csv file2.csv ...
  --fuel 휘발유 \
  --liters 40 \
  --eff 12.5 \
  --alpha 600 \
  --origin "서울 광진구 ..." \
  --dest "서울 송파구 ..."
```

주요 옵션 설명:
- `--csv` / `--csv_dir`: 주유소 CSV 파일 목록 또는 디렉터리
- `--fuel`: 연료 종류 (`휘발유`, `경유`, `고급휘발유`)
- `--liters`: 주유 예정량(L)
- `--eff`: 차량 연비(km/L) **필수**
- `--alpha`: 1분당 시간 가치(원). 기본값 600원
- `--origin` / `--dest`: 출발지·도착지 주소 **필수**
- `--debug`: Kakao API 호출 경로 실패 시 경고 로그 출력

## 출력 예시
```
=== 추천 Top 3 (유효단가 기준) ===
[1] OO주유소 (OO)  서울시 ...
  주유단가: 1479 ₩/L | 유효단가: 1505 ₩/L
  우회: +0.80 km, +1.2 분  (연료비 200₩, 시간비 720₩)
  총비용: 60200 ₩

=== 의사결정 ===
→ 경유 추천: OO주유소 로 들르면 총비용 1800₩ 절감(근사).
경유 안내(첫 단계): https://map.kakao.com/link/to/...
```
`gain` 값이 음수면 우회하지 않는 것이 더 이득이라는 메시지를 출력합니다.

## 주의 사항
- Kakao Mobility Directions API는 무료 쿼터가 있으므로 레이트리밋에 주의하세요. 스크립트는 기본적으로 요청 사이에 지연을 둡니다.
- KakaoNavi를 실제로 연동하려면 출력된 딥링크 대신 KakaoNavi 스킴을 사용하는 것을 권장합니다.
- 광진구·송파구 외 지역 데이터는 필터링으로 제거됩니다. 다른 지역을 분석하고 싶다면 `load_and_prepare` 함수를 수정하세요.

## 라이선스
이 프로젝트는 [MIT License](LICENSE)를 따릅니다.
