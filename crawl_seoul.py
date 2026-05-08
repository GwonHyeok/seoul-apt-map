#!/usr/bin/env python3
"""
호갱노노 서울 아파트 전수 크롤러 v2 — 최근 실거래 정보 포함

추가 필드:
- date_max_real_trade: 역대 최고가 거래일
- trade_count: 전체 거래 수
- trade_recent_count: 최근 거래 수
- max_real_trade_data: {"price":xxx, "floor":xx}
- popularity, trade_rate, deposit_rate, rent_rate
- start_month: 입주월 (정확한 날짜)
"""
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

OUT = Path(__file__).parent / "seoul_apts.json"

def make_tiles():
    tiles = []
    d_lng = 0.022
    d_lat = 0.013
    lng = 126.79
    while lng <= 127.18:
        lat = 37.45
        while lat <= 37.69:
            tiles.append({"lat": round(lat, 4), "lng": round(lng, 4)})
            lat += d_lat
        lng += d_lng
    return tiles

async def crawl():
    tiles = make_tiles()
    print(f"총 타일: {len(tiles)}", flush=True)

    apts = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        )
        page = await ctx.new_page()

        async def on_response(resp):
            url = resp.url
            if "/api/apt/bounding" not in url or resp.status != 200:
                return
            try:
                j = await resp.json()
                data = j.get("data") or []
                for it in data:
                    if it.get("poiType") == "apt" and it.get("id"):
                        area = it.get("area") or {}
                        bi = it.get("baseinfo") or {}
                        # 최고가 거래의 가격+층 파싱
                        mtd = area.get("max_real_trade_data") or ""
                        mt_floor = None
                        try:
                            if mtd:
                                d = json.loads(mtd)
                                mt_floor = d.get("floor")
                        except Exception:
                            pass
                        apts[it["id"]] = {
                            "id": it["id"],
                            "name": it.get("name"),
                            "address": it.get("address"),
                            "road_address": it.get("road_address"),
                            "lat": it.get("lat"),
                            "lng": it.get("lng"),
                            "dong": it.get("dong"),
                            "region_code": it.get("region_code"),
                            "total_household": it.get("total_household"),
                            "trade_count": it.get("trade_count"),
                            "trade_recent_count": it.get("trade_recent_count"),
                            "popularity": it.get("popularity"),
                            "trade_rate": it.get("trade_rate"),
                            "deposit_rate": it.get("deposit_rate"),
                            "rent_rate": it.get("rent_rate"),
                            # 가격 (만원)
                            "max_real_trade_price": area.get("max_real_trade_price"),
                            "second_max_real_trade_price": area.get("second_max_real_trade_price"),
                            "max_real_rent_price": area.get("max_real_rent_price"),
                            "real_trade_price": area.get("real_trade_price"),
                            "real_rent_price": area.get("real_rent_price"),
                            "type_real_trade_price": area.get("type_real_trade_price"),
                            "type_real_rent_price": area.get("type_real_rent_price"),
                            "type_official_price": area.get("type_official_price"),
                            "loanable_trade_price": area.get("loanable_trade_price"),
                            # 거래일
                            "date_max_real_trade": area.get("date_max_real_trade"),
                            "date_max_real_rent": area.get("date_max_real_rent"),
                            "date_official_price": area.get("date_official_price"),
                            # 최고가 층
                            "max_trade_floor": mt_floor,
                            # 면적
                            "private_area": area.get("private_area"),
                            "public_area": area.get("public_area"),
                            "area_total_household": area.get("total_household"),
                            # 단지 정보
                            "diff_year_text": it.get("diffYearText"),
                            "start_month": it.get("start_month"),
                            "approval_date": bi.get("approval_date") or bi.get("permission_date"),
                            "heat_type": bi.get("heat_type"),
                            "asile_type": bi.get("asile_type"),
                            "parking_rate": bi.get("parking_rate"),
                            "floor_max": bi.get("floor_max"),
                            "company": bi.get("company"),
                        }
            except Exception:
                pass

        page.on("response", lambda r: asyncio.create_task(on_response(r)))

        await page.goto("https://hogangnono.com/?nocache=1", wait_until="domcontentloaded")
        await page.wait_for_timeout(2500)

        for i, t in enumerate(tiles):
            try:
                await page.evaluate(
                    "(t) => { localStorage.setItem('MAP_CENTER', JSON.stringify({lat:t.lat, lng:t.lng})); localStorage.setItem('MAP_ZOOM', '16'); }",
                    t,
                )
                await page.reload(wait_until="domcontentloaded")
                await page.wait_for_timeout(2200)
            except Exception as e:
                print(f"  tile {i} err: {e}", flush=True)
                continue

            if (i + 1) % 5 == 0 or i == len(tiles) - 1:
                OUT.write_text(json.dumps(apts, ensure_ascii=False, indent=2))
                print(f"[{i+1}/{len(tiles)}] tile=({t['lat']},{t['lng']}) total_apts={len(apts)}", flush=True)

        await browser.close()

    OUT.write_text(json.dumps(apts, ensure_ascii=False, indent=2))
    print(f"\n총 수집: {len(apts)}개", flush=True)

if __name__ == "__main__":
    asyncio.run(crawl())
