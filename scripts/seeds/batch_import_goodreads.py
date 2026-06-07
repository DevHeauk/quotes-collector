"""
goodreads_popularity 테이블에서 미삽입 명언을 Claude API로 번역+태깅하여 quotes에 삽입.

사용법:
    python scripts/seeds/batch_import_goodreads.py --dry-run      # 확인만
    python scripts/seeds/batch_import_goodreads.py --batch 0      # 첫 50개
    python scripts/seeds/batch_import_goodreads.py --batch 1      # 다음 50개
    python scripts/seeds/batch_import_goodreads.py --all           # 전체
"""

import argparse
import json
import os
import uuid

import anthropic
import psycopg2
from dotenv import load_dotenv

load_dotenv()

BATCH_SIZE = 50
SIMILARITY_THRESHOLD = 0.4


DB_CONFIG = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": int(os.getenv("PG_PORT", "5432")),
    "user": os.getenv("PG_USER", "youheaukjun"),
    "password": os.getenv("PG_PASSWORD", ""),
    "dbname": os.getenv("PG_DATABASE", "quotes_db"),
}


def get_impact_score(likes):
    if likes > 100000:
        return 10
    elif likes > 50000:
        return 9
    elif likes > 30000:
        return 8
    elif likes > 20000:
        return 7
    elif likes > 10000:
        return 6
    elif likes > 5000:
        return 5
    elif likes > 1000:
        return 4
    else:
        return 3


def load_masters(cur):
    masters = {}
    for table in ("keywords", "situations", "professions", "fields"):
        if table == "fields":
            cur.execute(f"SELECT id, name FROM {table}")
            masters[table] = {r[1]: r[0] for r in cur.fetchall()}
        else:
            cur.execute(f"SELECT id, name FROM {table}")
            masters[table] = {r[1]: r[0] for r in cur.fetchall()}
    return masters


def get_or_create_master(cur, table, name):
    cur.execute(f"SELECT id FROM {table} WHERE name = %s", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    new_id = str(uuid.uuid4())
    cur.execute(f"INSERT INTO {table} (id, name) VALUES (%s, %s)", (new_id, name))
    print(f"  [NEW] {table}: {name}")
    return new_id


def get_or_create_author(cur, author_data, masters):
    cur.execute("SELECT id FROM authors WHERE name = %s", (author_data["name_ko"],))
    row = cur.fetchone()
    if row:
        return row[0]

    prof_id = masters["professions"].get(author_data.get("profession"))
    if not prof_id and author_data.get("profession"):
        prof_id = get_or_create_master(cur, "professions", author_data["profession"])

    field_id = masters["fields"].get(author_data.get("field"))
    if not field_id and author_data.get("field"):
        field_id = get_or_create_master(cur, "fields", author_data["field"])

    author_id = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO authors (id, name, nationality, birth_year, profession_id, field_id) VALUES (%s, %s, %s, %s, %s, %s)",
        (author_id, author_data["name_ko"], author_data.get("nationality", ""),
         author_data.get("birth_year", 0), prof_id, field_id),
    )
    print(f"  [NEW AUTHOR] {author_data['name_ko']}")
    return author_id


def is_duplicate(cur, text_original, text_ko):
    cur.execute("SELECT 1 FROM quotes WHERE text_original = %s", (text_original,))
    if cur.fetchone():
        return True
    cur.execute("SELECT 1 FROM quotes WHERE text = %s", (text_ko,))
    if cur.fetchone():
        return True
    cur.execute(
        "SELECT 1 FROM quotes WHERE similarity(text_original, %s) > %s LIMIT 1",
        (text_original, SIMILARITY_THRESHOLD),
    )
    if cur.fetchone():
        return True
    return False


def translate_and_tag_batch(quotes_batch, masters):
    client = anthropic.Anthropic()

    kw_list = ", ".join(sorted(masters["keywords"].keys()))
    sit_list = ", ".join(sorted(masters["situations"].keys()))
    prof_list = ", ".join(sorted(masters["professions"].keys()))
    field_list = ", ".join(sorted(masters["fields"].keys()))

    quotes_text = "\n".join(
        f'{i+1}. "{q[0]}" — {q[1]} (likes: {q[2]})'
        for i, q in enumerate(quotes_batch)
    )

    system = f"""너는 명언 데이터 큐레이터야. 영어 명언을 한국어로 번역하고 메타데이터를 태깅해.

규칙:
- 자연스러운 한국어 번역. 직역보다 의역 선호.
- 저자 이름은 한국어 표기 (Oscar Wilde → 오스카 와일드).
- 소설/영화 대사도 포함. source에 작품명을 기재해.
- 키워드: [{kw_list}] 에서 2~5개 선택. 명언의 핵심 메시지 기준.
- 상황: [{sit_list}] 에서 1~3개 선택.
- need_types: motivation / comfort / reflection / insight / relationship / humor 중 1~2개.
- 직업: [{prof_list}] 에서 선택.
- 분야: [{field_list}] 에서 선택.
- nationality: ISO 3166-1 alpha-2 (US, GB, DE 등).
- birth_year: 정확한 출생연도. 모르면 0.

반드시 아래 JSON 형식으로만 응답해:
{{
  "quotes": [
    {{
      "index": 1,
      "text_ko": "한국어 번역",
      "source": "작품명 또는 null",
      "author": {{
        "name_ko": "한국어 저자명",
        "profession": "직업",
        "field": "분야",
        "nationality": "US",
        "birth_year": 1879
      }},
      "keywords": ["키워드1", "키워드2"],
      "situations": ["상황1"],
      "need_types": ["motivation"]
    }}
  ]
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        system=system,
        messages=[{"role": "user", "content": f"아래 명언들을 번역하고 태깅해줘:\n\n{quotes_text}"}],
    )

    text = message.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    return json.loads(text)["quotes"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--batch", type=int, default=None)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    masters = load_masters(cur)

    # 미삽입 명언 조회
    cur.execute("""
        SELECT gp.quote_text, gp.author_name, gp.likes
        FROM goodreads_popularity gp
        WHERE NOT EXISTS (
            SELECT 1 FROM quotes q WHERE q.text_original = gp.quote_text
        )
        ORDER BY gp.likes DESC
    """)
    all_quotes = cur.fetchall()
    print(f"미삽입 명언: {len(all_quotes)}개")

    if args.batch is not None:
        start = args.batch * BATCH_SIZE
        all_quotes = all_quotes[start:start + BATCH_SIZE]
        print(f"배치 {args.batch}: {start}~{start + len(all_quotes) - 1}")
    elif not args.all:
        all_quotes = all_quotes[:BATCH_SIZE]
        print(f"첫 {BATCH_SIZE}개만 처리 (--all로 전체)")

    if not all_quotes:
        print("처리할 명언이 없습니다.")
        return

    # Claude API로 번역+태깅 (BATCH_SIZE씩)
    saved = 0
    skipped_dup = 0

    for chunk_start in range(0, len(all_quotes), BATCH_SIZE):
        chunk = all_quotes[chunk_start:chunk_start + BATCH_SIZE]
        print(f"\n--- API 호출: {len(chunk)}개 번역+태깅 중... ---")

        try:
            tagged = translate_and_tag_batch(chunk, masters)
        except Exception as e:
            print(f"API 오류: {e}")
            continue

        for item in tagged:
            idx = item["index"] - 1
            if idx >= len(chunk):
                continue

            original_text, author_en, likes = chunk[idx]

            text_ko = item["text_ko"]
            source = item.get("source")

            if is_duplicate(cur, original_text, text_ko):
                skipped_dup += 1
                print(f"  [DUP] {original_text[:40]}...")
                continue

            if args.dry_run:
                print(f"  [DRY] {item['author']['name_ko']}: {text_ko[:50]}... (impact: {get_impact_score(likes)})")
                saved += 1
                continue

            # 저자 생성/매칭
            author_id = get_or_create_author(cur, item["author"], masters)

            # 키워드/상황 ID 변환
            kw_ids = [masters["keywords"][k] for k in item["keywords"] if k in masters["keywords"]]
            sit_ids = [masters["situations"][s] for s in item["situations"] if s in masters["situations"]]
            kw_json = json.dumps(item["keywords"], ensure_ascii=False)
            sit_json = json.dumps(item["situations"], ensure_ascii=False)
            need_types = item.get("need_types", [])

            quote_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO quotes
                (id, text, text_original, original_language, author_id, source,
                 keywords, situation, keyword_ids, situation_ids,
                 need_types, impact_score, status, source_reliability)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s, %s, %s, %s)
            """, (
                quote_id, text_ko, original_text, "en", author_id, source,
                kw_json, sit_json, kw_ids, sit_ids,
                need_types, get_impact_score(likes), "draft", "attributed",
            ))
            saved += 1
            print(f"  [OK] {item['author']['name_ko']}: {text_ko[:50]}...")

        if not args.dry_run:
            conn.commit()

    cur.close()
    conn.close()

    print(f"\n=== 완료 ===")
    print(f"삽입: {saved}개")
    print(f"중복 스킵: {skipped_dup}개")


if __name__ == "__main__":
    main()
