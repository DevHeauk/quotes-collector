#!/usr/bin/env python3
"""
한국 명언의 네이버 블로그 인기도 수집 스크립트
- DB에서 한국 저자(nationality='KR')의 명언을 조회
- 네이버 검색 결과에서 blog.naver.com 링크 수를 추출하여 인기도 추정
- 결과를 naver_popularity 테이블에 저장
"""

import psycopg2
import requests
import re
import time
import uuid
from datetime import datetime

# DB 연결
conn = psycopg2.connect(
    host="localhost",
    user="youheaukjun",
    database="quotes_db"
)
conn.autocommit = True
cur = conn.cursor()

# naver_popularity 테이블 생성 (이미 있으면 무시)
cur.execute("""
    CREATE TABLE IF NOT EXISTS naver_popularity (
        id VARCHAR(36) PRIMARY KEY,
        quote_id VARCHAR(36) REFERENCES quotes(id),
        search_query TEXT NOT NULL,
        result_count INT,
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

# 한국 저자의 명언 조회
cur.execute("""
    SELECT q.id, q.text, a.name FROM quotes q
    JOIN authors a ON q.author_id = a.id
    WHERE a.nationality = 'KR' AND q.impact_score >= 6
    ORDER BY q.impact_score DESC LIMIT 50
""")
quotes = cur.fetchall()
print(f"조회된 명언 수: {len(quotes)}")

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9',
}

def get_search_query(text):
    """명언 텍스트에서 검색용 핵심 구절 추출 (20~30자)"""
    # 쉼표나 마침표로 분리해서 첫 구절 사용
    parts = re.split(r'[,.。，]', text)
    first_part = parts[0].strip()
    if len(first_part) > 30:
        return first_part[:30]
    elif len(first_part) < 10 and len(parts) > 1:
        # 첫 부분이 너무 짧으면 두 번째까지 합침
        combined = first_part + ' ' + parts[1].strip()
        return combined[:30]
    return first_part

def fetch_naver_blog_count(query_text):
    """네이버 검색에서 blog.naver.com 링크 수를 세어 인기도 추정"""
    try:
        url = f'https://search.naver.com/search.naver?where=nexearch&query={requests.utils.quote(query_text)}'
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"  HTTP {r.status_code}")
            return None
        blog_urls = len(re.findall(r'blog\.naver\.com/[^"\'<>\s]+', r.text))
        return blog_urls
    except requests.exceptions.RequestException as e:
        print(f"  요청 오류: {e}")
        return None

# 처리 시작
success_count = 0
fail_count = 0
results = []
batch_size = 3

for i, (quote_id, text, author_name) in enumerate(quotes):
    search_query = get_search_query(text)
    print(f"[{i+1}/{len(quotes)}] {author_name}: {search_query[:25]}...")

    count = fetch_naver_blog_count(search_query)

    if count is None:
        # 재시도
        print("  재시도 중...")
        time.sleep(3)
        count = fetch_naver_blog_count(search_query)

    if count is not None:
        row_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO naver_popularity (id, quote_id, search_query, result_count, fetched_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (quote_id) DO UPDATE
            SET search_query = EXCLUDED.search_query,
                result_count = EXCLUDED.result_count,
                fetched_at = EXCLUDED.fetched_at
        """, (row_id, quote_id, search_query, count, datetime.now()))
        results.append((author_name, search_query[:30], count))
        success_count += 1
        print(f"  -> 블로그 링크 수: {count}")
    else:
        fail_count += 1
        print(f"  -> 실패")

    # Rate limit: 3개마다 1.5초 대기
    if (i + 1) % batch_size == 0:
        time.sleep(1.5)

# 결과 출력
print(f"\n{'='*60}")
print(f"총 조회: {success_count + fail_count}개, 성공: {success_count}개, 실패: {fail_count}개")

# TOP 10 출력
print(f"\n{'='*60}")
print("네이버 블로그 인기도 TOP 10")
print(f"{'='*60}")

cur.execute("""
    SELECT a.name, np.search_query, np.result_count
    FROM naver_popularity np
    JOIN quotes q ON np.quote_id = q.id
    JOIN authors a ON q.author_id = a.id
    ORDER BY np.result_count DESC
    LIMIT 10
""")
top10 = cur.fetchall()
for rank, (name, query, count) in enumerate(top10, 1):
    print(f"  {rank:2d}. [{count:4d}] {name} - {query[:35]}")

cur.close()
conn.close()
print("\n완료!")
