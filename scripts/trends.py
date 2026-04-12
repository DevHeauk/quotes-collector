"""
Google Trends 기반 명언 카테고리 관심도 분석.

사용법:
    python scripts/trends.py
"""

import json
import os
from datetime import datetime

from pytrends.request import TrendReq


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "trends")


def fetch_trends(keywords: list[str], geo: str = "", timeframe: str = "today 12-m") -> dict[str, float]:
    """키워드 목록의 Google Trends 평균 관심도를 반환한다."""
    pytrends = TrendReq(hl="ko", tz=540)
    pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo)
    df = pytrends.interest_over_time()
    if df.empty:
        return {k: 0.0 for k in keywords}
    return df.drop(columns="isPartial", errors="ignore").mean().to_dict()


def analyze():
    """글로벌 + 한국 키워드를 분석하고 결과를 저장한다."""
    print("=== Google Trends 명언 카테고리 분석 ===\n")

    # 글로벌 영어 키워드
    global_1 = fetch_trends(
        ["motivational quotes", "love quotes", "life quotes", "inspirational quotes", "success quotes"]
    )
    global_2 = fetch_trends(
        ["funny quotes", "good morning quotes", "study quotes", "healing quotes", "self esteem quotes"]
    )
    global_all = {**global_1, **global_2}

    print("[글로벌]")
    for k, v in sorted(global_all.items(), key=lambda x: -x[1]):
        bar = "█" * int(v / 2)
        print(f"  {k:<25} {v:5.1f}  {bar}")

    # 한국 키워드
    kr_1 = fetch_trends(["명언", "힐링명언", "인생명언", "사랑명언", "성공명언"], geo="KR")
    kr_2 = fetch_trends(["자존감명언", "공부명언", "드라마명대사", "아침명언", "고사성어"], geo="KR")
    kr_all = {**kr_1, **kr_2}

    print("\n[한국]")
    for k, v in sorted(kr_all.items(), key=lambda x: -x[1]):
        bar = "█" * int(v / 2)
        print(f"  {k:<15} {v:5.1f}  {bar}")

    # 결과 저장
    result = {
        "fetched_at": datetime.now().isoformat(),
        "timeframe": "today 12-m",
        "global": global_all,
        "korea": kr_all,
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    filename = f"trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n결과 저장: {filepath}")
    return result


if __name__ == "__main__":
    analyze()
