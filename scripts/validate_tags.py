"""
Claude API를 사용한 명언 태깅 의미 검증.

1,245개 명언을 배치(20개씩)로 나눠 Claude에게 태깅 적절성을 검증시킨다.
오분류로 판단된 건만 JSON으로 출력.

사용법:
    python scripts/validate_tags.py                    # 전체 검증
    python scripts/validate_tags.py --limit 100        # 100개만
    python scripts/validate_tags.py --apply            # 검증 결과 DB 반영
"""

import argparse
import json
import os
import sys
import time

import anthropic
import psycopg2
from dotenv import load_dotenv

load_dotenv(".env")

BATCH_SIZE = 20


def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=int(os.getenv("PG_PORT", "5432")),
        user=os.getenv("PG_USER", "youheaukjun"),
        password=os.getenv("PG_PASSWORD", ""),
        dbname=os.getenv("PG_DATABASE", "quotes_db"),
    )


def load_master_lists(cur):
    cur.execute("SELECT name, group_name FROM keywords ORDER BY group_name, name")
    keywords = [f"{r[0]} [{r[1]}]" for r in cur.fetchall()]

    cur.execute("SELECT name, group_name FROM situations ORDER BY group_name, name")
    situations = [f"{r[0]} [{r[1]}]" for r in cur.fetchall()]

    return keywords, situations


def build_validation_prompt(quotes_batch, keywords_list, situations_list):
    kw_str = ", ".join(keywords_list)
    sit_str = ", ".join(situations_list)

    quotes_str = ""
    for q in quotes_batch:
        quotes_str += f"""
---
ID: {q['id']}
저자: {q['author']}
명언: {q['text']}
현재 키워드: {json.dumps(q['keywords'], ensure_ascii=False)}
현재 상황: {json.dumps(q['situations'], ensure_ascii=False)}
"""

    return f"""당신은 명언 데이터 큐레이터입니다. 아래 명언들의 키워드/상황 태깅이 적절한지 검증하세요.

## 마스터 키워드 목록
{kw_str}

## 마스터 상황 목록
{sit_str}

## 분류 원칙
1. **명언의 핵심 메시지 기준** — 표면적 소재가 아닌 전달하려는 메시지로 분류
2. 키워드 3~5개, 상황 1~3개가 적정
3. 그룹 간 경계가 모호하면 더 구체적인 쪽으로
4. 고사성어는 원래 맥락 기준으로 분류
5. 마스터 목록에 있는 태그만 사용

## 검증 대상
{quotes_str}

## 출력 형식

오분류된 것만 JSON 배열로 출력하세요. 태깅이 적절한 명언은 출력하지 마세요.

```json
[
  {{
    "id": "명언 ID",
    "issue": "간단한 사유 (예: '고통은 이 명언의 메시지가 아님')",
    "fixed_keywords": ["수정된", "키워드", "목록"],
    "fixed_situations": ["수정된", "상황", "목록"]
  }}
]
```

태깅이 모두 적절하면 빈 배열 `[]`을 출력하세요.
반드시 JSON만 출��하세요. 설명은 불필요합니다."""


def validate_batch(client, quotes_batch, keywords_list, situations_list):
    prompt = build_validation_prompt(quotes_batch, keywords_list, situations_list)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()

    # JSON 블록 추출
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print(f"  ⚠️  JSON 파싱 실패: {text[:200]}", file=sys.stderr)
        return []


def run(limit=None, apply=False):
    conn = get_db_connection()
    cur = conn.cursor()

    keywords_list, situations_list = load_master_lists(cur)

    cur.execute("""
        SELECT q.id, q.text, q.keywords, q.situation, a.name
        FROM quotes q
        JOIN authors a ON q.author_id = a.id
        ORDER BY q.created_at
    """)
    all_quotes = []
    for r in cur.fetchall():
        all_quotes.append({
            "id": r[0],
            "text": r[1],
            "keywords": r[2] if isinstance(r[2], list) else [],
            "situations": r[3] if isinstance(r[3], list) else [],
            "author": r[4],
        })

    if limit:
        all_quotes = all_quotes[:limit]

    print(f"검증 대상: {len(all_quotes)}개 명언")
    print(f"배치 크기: {BATCH_SIZE}개")
    print(f"예상 배치 수: {(len(all_quotes) + BATCH_SIZE - 1) // BATCH_SIZE}")
    print()

    client = anthropic.Anthropic()
    all_issues = []

    for i in range(0, len(all_quotes), BATCH_SIZE):
        batch = all_quotes[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(all_quotes) + BATCH_SIZE - 1) // BATCH_SIZE

        print(f"[{batch_num}/{total_batches}] 검증 중... ", end="", flush=True)

        try:
            issues = validate_batch(client, batch, keywords_list, situations_list)
            all_issues.extend(issues)
            print(f"오분류 {len(issues)}건")
        except Exception as e:
            print(f"오���: {e}")

        # Rate limiting
        if i + BATCH_SIZE < len(all_quotes):
            time.sleep(1)

    # 결과 출력
    print(f"\n{'=' * 60}")
    print(f"검증 완료: {len(all_quotes)}개 중 오분류 {len(all_issues)}건 ({len(all_issues)*100//len(all_quotes)}%)")
    print(f"{'=' * 60}\n")

    if all_issues:
        # 결과 저장
        result_path = "data/tag_validation_result.json"
        os.makedirs("data", exist_ok=True)
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(all_issues, f, ensure_ascii=False, indent=2)
        print(f"결과 저장: {result_path}")

        # 요약 출력
        print(f"\n## 오분류 목록")
        print(f"{'ID':>10} | {'명언 (앞 35자)':<37} | 사유")
        print("-" * 90)
        for issue in all_issues:
            qid = issue["id"][:8]
            # 해당 명언 찾기
            quote_text = ""
            for q in all_quotes:
                if q["id"] == issue["id"]:
                    quote_text = q["text"][:35]
                    break
            reason = issue.get("issue", "")[:40]
            print(f"{qid:>10} | {quote_text:<37} | {reason}")

        if apply:
            # DB 반영
            kw_name_to_id = {}
            cur.execute("SELECT id, name FROM keywords")
            for r in cur.fetchall():
                kw_name_to_id[r[1]] = r[0]

            sit_name_to_id = {}
            cur.execute("SELECT id, name FROM situations")
            for r in cur.fetchall():
                sit_name_to_id[r[1]] = r[0]

            fixed = 0
            for issue in all_issues:
                new_kws = issue.get("fixed_keywords", [])
                new_sits = issue.get("fixed_situations", [])

                # 마스터에 있는 것만 필터
                valid_kws = [k for k in new_kws if k in kw_name_to_id]
                valid_sits = [s for s in new_sits if s in sit_name_to_id]

                if not valid_kws and not valid_sits:
                    continue

                new_kw_ids = [kw_name_to_id[k] for k in valid_kws]
                new_sit_ids = [sit_name_to_id[s] for s in valid_sits]

                cur.execute(
                    """UPDATE quotes
                       SET keywords = %s::jsonb,
                           situation = %s::jsonb,
                           keyword_ids = %s,
                           situation_ids = %s
                       WHERE id = %s""",
                    (
                        json.dumps(valid_kws, ensure_ascii=False),
                        json.dumps(valid_sits, ensure_ascii=False),
                        new_kw_ids,
                        new_sit_ids,
                        issue["id"],
                    ),
                )
                fixed += 1

            conn.commit()
            print(f"\n✅ {fixed}건 DB 반영 완료")
        else:
            print(f"\n📋 DB 반영하려면 --apply 옵션을 추가하세요.")

    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="명언 태깅 의미 검증")
    parser.add_argument("--limit", type=int, help="검증할 명언 수 제한")
    parser.add_argument("--apply", action="store_true", help="검증 결과를 DB에 반영")
    args = parser.parse_args()
    run(limit=args.limit, apply=args.apply)
