#!/usr/bin/env python3
"""
Reddit r/quotes에서 인기 명언을 수집하여 PostgreSQL에 저장하는 스크립트.
Reddit 공개 JSON API 사용 (인증 불필요).
"""

import json
import re
import subprocess
import time
import uuid
from typing import Dict, List, Optional, Tuple
import psycopg2

URLS = [
    "https://www.reddit.com/r/quotes/top/.json?t=all&limit=100",
    "https://www.reddit.com/r/quotes/top/.json?t=year&limit=100",
    "https://www.reddit.com/r/quotes/top/.json?t=month&limit=100",
]

HEADERS = {"User-Agent": "QuoteCollector/1.0 (Python)"}

DB_CONFIG = {
    "host": "localhost",
    "user": "youheaukjun",
    "dbname": "quotes_db",
}

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS reddit_popularity (
    id VARCHAR(36) PRIMARY KEY,
    quote_text TEXT NOT NULL,
    author_name VARCHAR(255),
    upvotes INT NOT NULL,
    reddit_id VARCHAR(20),
    subreddit VARCHAR(50) DEFAULT 'quotes',
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def fetch_reddit_json(url: str) -> List[Dict]:
    """Reddit JSON API에서 게시물 목록을 가져온다 (curl 사용)."""
    result = subprocess.run(
        ["curl", "-s", "-H",
         "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
         url],
        capture_output=True, text=True, timeout=30
    )
    data = json.loads(result.stdout)
    posts = []
    for child in data.get("data", {}).get("children", []):
        d = child.get("data", {})
        posts.append({
            "reddit_id": d.get("id", ""),
            "title": d.get("title", ""),
            "ups": d.get("ups", 0),
        })
    return posts


def parse_quote_and_author(title: str) -> Tuple[str, Optional[str]]:
    """
    title에서 명언 텍스트와 저자를 분리한다.
    일반적인 형식:
      "quote text" — Author
      "quote text" - Author
      "quote text" ~ Author
      quote text — Author
    """
    # 따옴표 정규화
    title = title.replace("\u201c", '"').replace("\u201d", '"')
    title = title.replace("\u2018", "'").replace("\u2019", "'")
    title = title.replace("\u2015", "—")  # horizontal bar -> em dash

    # 저자 분리 패턴: — , - , ~ 로 구분
    # 뒤에서부터 매칭 (마지막 구분자 기준)
    patterns = [
        r'^(.+?)\s*[—–]\s*([A-Z].+)$',       # em/en dash
        r'^(.+?)\s+[-]\s+([A-Z].+)$',          # hyphen with spaces
        r'^(.+?)\s*[~]\s*([A-Z].+)$',          # tilde
        r'^"(.+?)"\s*[-—–~]\s*(.+)$',          # quoted with any separator
        r'^["\'](.+?)["\']\s*[-—–~]\s*(.+)$',  # various quotes
    ]

    for pattern in patterns:
        m = re.match(pattern, title, re.DOTALL)
        if m:
            quote = m.group(1).strip().strip('"\'')
            author = m.group(2).strip().strip('"\'')
            if len(quote) > 5 and len(author) < 200:
                return quote, author

    # 저자를 파싱하지 못한 경우, 전체를 quote로
    clean = title.strip().strip('"\'')
    return clean, None


def main():
    # 1. Reddit에서 데이터 수집
    all_posts = {}
    for url in URLS:
        label = "all" if "t=all" in url else ("year" if "t=year" in url else "month")
        print(f"[*] Fetching top/{label} ...")
        try:
            posts = fetch_reddit_json(url)
            print(f"    -> {len(posts)}개 게시물 수신")
            for p in posts:
                rid = p["reddit_id"]
                # 중복 reddit_id는 upvote가 더 높은 것만 유지
                if rid not in all_posts or p["ups"] > all_posts[rid]["ups"]:
                    all_posts[rid] = p
        except Exception as e:
            print(f"    -> 오류: {e}")
        time.sleep(1)  # rate limit 방지

    print(f"\n[*] 총 {len(all_posts)}개 고유 게시물 수집됨")

    # 2. 파싱
    parsed = []
    for p in all_posts.values():
        quote_text, author_name = parse_quote_and_author(p["title"])
        if len(quote_text) < 5:
            continue
        parsed.append({
            "id": str(uuid.uuid4()),
            "quote_text": quote_text,
            "author_name": author_name,
            "upvotes": p["ups"],
            "reddit_id": p["reddit_id"],
        })

    print(f"[*] {len(parsed)}개 명언 파싱 완료")

    # 3. DB 저장
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()

    # 테이블 생성
    cur.execute(CREATE_TABLE_SQL)
    print("[*] 테이블 reddit_popularity 준비 완료")

    # 중복 체크 후 삽입
    inserted = 0
    skipped = 0
    for item in parsed:
        cur.execute(
            "SELECT 1 FROM reddit_popularity WHERE quote_text = %s",
            (item["quote_text"],)
        )
        if cur.fetchone():
            skipped += 1
            continue

        cur.execute(
            """INSERT INTO reddit_popularity (id, quote_text, author_name, upvotes, reddit_id, subreddit)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (item["id"], item["quote_text"], item["author_name"],
             item["upvotes"], item["reddit_id"], "quotes")
        )
        inserted += 1

    cur.close()
    conn.close()

    # 4. 결과 보고
    upvotes_list = [item["upvotes"] for item in parsed]
    min_up = min(upvotes_list) if upvotes_list else 0
    max_up = max(upvotes_list) if upvotes_list else 0

    print(f"\n{'='*50}")
    print(f"[결과]")
    print(f"  파싱된 명언: {len(parsed)}개")
    print(f"  새로 저장:   {inserted}개")
    print(f"  중복 스킵:   {skipped}개")
    print(f"  Upvote 범위: {min_up} ~ {max_up}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
