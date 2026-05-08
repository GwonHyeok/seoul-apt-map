# 호갱노노 OpenAPI + 서울 아파트 시각화

호갱노노(hogangnono.com) 비공식 OpenAPI 스펙(역공학)과 서울 아파트 지도.

## 라이브 데모
GitHub Pages 배포 후: `https://<github-username>.github.io/<repo-name>/`

## 폴더 구조

```
docs/                     # GitHub Pages 배포 대상
├── index.html            # Leaflet 지도 (정적)
├── data.json             # 서울 15억 이하 9,268개 (3.4MB)
└── README.md
crawl_seoul.py            # Playwright 크롤러 (재실행 가능)
openapi.yaml              # 호갱노노 비공식 OpenAPI 3.1 스펙 (419 path, 448 op)
```

## GitHub 배포 방법

```bash
# 1) git init + 첫 커밋
cd /Users/ghyeok/Developments/hogangnono/openapi-capture
git init
git add .gitignore docs/ openapi.yaml crawl_seoul.py README.md
git commit -m "init: 서울 아파트 지도 + 호갱노노 비공식 OpenAPI"

# 2) GitHub에 새 repo 만든 뒤
git remote add origin https://github.com/<username>/<repo>.git
git branch -M main
git push -u origin main

# 3) GitHub Pages 켜기
#    Settings → Pages → Source: "Deploy from a branch"
#    Branch: main, Folder: /docs → Save
#    → 1-2분 후 https://<username>.github.io/<repo>/ 접속 가능
```

또는 별도 브랜치 없이 main의 `/docs` 폴더가 자동으로 사이트가 됩니다.

## 데이터 갱신

```bash
pip install playwright
playwright install chromium
python3 crawl_seoul.py     # ~22분, seoul_apts.json 생성
# 그다음 docs/data.json으로 변환:
python3 -c "
import json
SIDO={'11680':'강남구','11740':'강동구','11305':'강북구','11500':'강서구','11620':'관악구','11215':'광진구','11530':'구로구','11545':'금천구','11350':'노원구','11320':'도봉구','11230':'동대문구','11590':'동작구','11440':'마포구','11410':'서대문구','11650':'서초구','11200':'성동구','11290':'성북구','11710':'송파구','11470':'양천구','11560':'영등포구','11170':'용산구','11380':'은평구','11110':'종로구','11140':'중구','11260':'중랑구'}
raw=json.load(open('seoul_apts.json'));out=[]
for v in raw.values():
    rc=v.get('region_code') or '';p=v.get('max_real_trade_price')
    if not rc.startswith('11') or not p or p>150000 or not v.get('lat'): continue
    out.append({'id':v['id'],'name':v.get('name'),'addr':(v.get('address') or '').replace('서울특별시 ',''),'sgg':SIDO.get(rc[:5]),'dong':v.get('dong'),'lat':round(v['lat'],6),'lng':round(v['lng'],6),'hh':v.get('total_household'),'pa':v.get('private_area'),'sa':v.get('public_area'),'maxP':v.get('max_real_trade_price'),'rentP':v.get('max_real_rent_price'),'offP':v.get('type_official_price'),'date':(v.get('date_max_real_trade') or '')[:10] or None,'fl':v.get('max_trade_floor'),'flMax':v.get('floor_max'),'tcR':v.get('trade_recent_count'),'tcA':v.get('trade_count'),'yr':v.get('diff_year_text'),'heat':v.get('heat_type'),'aisle':v.get('asile_type'),'park':v.get('parking_rate'),'co':v.get('company')})
open('docs/data.json','w').write(json.dumps(out,ensure_ascii=False,separators=(',',':')))
print(f'{len(out)} records')
"
git add docs/data.json && git commit -m "update: 데이터 갱신" && git push
```

## 면책
- 호갱노노 비공식 데이터로 학습/연구용입니다.
- 가격은 역대 실거래 최고가라 신뢰도가 일정하지 않습니다 ("최근 거래" 필터 사용 권장).
- 호갱노노 측 요청 시 즉시 비공개로 전환할 것.
