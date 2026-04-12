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

    # DB에 저장
    import uuid
    import psycopg2
    from psycopg2.extras import Json
    from dotenv import load_dotenv
    load_dotenv()

    data = {"global": global_all, "korea": kr_all}

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        conn = psycopg2.connect(database_url)
    else:
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST", "localhost"),
            port=int(os.getenv("PG_PORT", "5432")),
            user=os.getenv("PG_USER", "youheaukjun"),
            password=os.getenv("PG_PASSWORD", ""),
            dbname=os.getenv("PG_DATABASE", "quotes_db"),
        )
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO trends (id, fetched_at, timeframe, data) VALUES (%s, %s, %s, %s)",
        (str(uuid.uuid4()), datetime.now(), "today 12-m", Json(data)),
    )
    conn.commit()
    cur.close()
    conn.close()

    print(f"\n결과 DB 저장 완료")
    return data


if __name__ == "__main__":
    analyze()
