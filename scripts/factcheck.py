"""
명언 팩트체크 스크립트. Claude API로 명언의 실존 여부를 검증한다.

사용법:
    python scripts/factcheck.py             # 미검증 명언 전체
    python scripts/factcheck.py --limit 10  # 10개만
    python scripts/factcheck.py --all       # 검증 완료된 것도 재검증
"""

import argparse
import json
import os
from datetime import datetime

import anthropic
import psycopg2
from dotenv import load_dotenv

load_dotenv()

VERIFY_PROMPT = """너는 명언 팩트체커야. 아래 명언이 실제로 존재하는지 검증해줘.

검증 항목:
1. 이 명언이 실제로 존재하는가? (출처가 확인되는가?)
2. 저자가 맞는가?
3. 출처(책, 연설 등)가 맞는가?
4. 연도가 맞는가?

반드시 아래 JSON으로만 응답해:

{
  "verified": true 또는 false,
  "confidence": "high" 또는 "medium" 또는 "low",
  "issues": ["문제1", "문제2"],
  "corrections": {
    "author": "올바른 저자 (수정 필요 시)",
    "source": "올바른 출처 (수정 필요 시)",
    "year": 올바른 연도 (수정 필요 시)
  },
  "note": "검증 관련 메모"
}

규칙:
- verified=true: 실제로 존재하는 명언이 맞음
- verified=false: 출처를 확인할 수 없거나, 저자가 틀리거나, 지어낸 것으로 의심됨
- issues가 비어있으면 문제 없음
- corrections에는 수정이 필요한 필드만 포함"""


def get_db():
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=int(os.getenv("PG_PORT", "5432")),
        user=os.getenv("PG_USER", "youheaukjun"),
        password=os.getenv("PG_PASSWORD", ""),
        dbname=os.getenv("PG_DATABASE", "quotes_db"),
    )


def get_unverified_quotes(limit: int | None = None, include_verified: bool = False):
    conn = get_db()
    cur = conn.cursor()

    sql = """
        SELECT q.id, q.text, q.text_original, a.name as author, q.source, q.year
        FROM quotes q JOIN authors a ON q.author_id = a.id
    """
    if not include_verified:
        sql += " WHERE q.verified = FALSE"
    sql += " ORDER BY q.created_at"
    if limit:
        sql += f" LIMIT {limit}"

    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def verify_quote(quote: dict) -> dict:
    """Claude API로 명언을 검증한다."""
    client = anthropic.Anthropic()

    user_msg = f"""명언: "{quote['text']}"
원문: "{quote.get('text_original') or '없음'}"
저자: {quote['author']}
출처: {quote.get('source') or '불명'}
연도: {quote.get('year') or '불명'}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=VERIFY_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )

    text = message.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    return json.loads(text)


def save_verification(quote_id: str, result: dict):
    """검증 결과를 DB에 저장한다."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE quotes SET verified = %s, verified_at = %s WHERE id = %s",
        (result["verified"], datetime.now(), quote_id),
    )
    conn.commit()
    cur.close()
    conn.close()


def factcheck(limit: int | None = None, include_verified: bool = False):
    quotes = get_unverified_quotes(limit, include_verified)

    if not quotes:
        print("검증할 명언이 없습니다.")
        return

    print(f"{'='*60}")
    print(f"팩트체크: {len(quotes)}개 명언 검증")
    print(f"{'='*60}")

    stats = {"verified": 0, "suspicious": 0, "errors": 0}
    suspicious_list = []

    for i, q in enumerate(quotes, 1):
        print(f"\n[{i}/{len(quotes)}] \"{q['text'][:50]}...\" — {q['author']}")

        try:
            result = verify_quote(q)
            save_verification(q["id"], result)

            if result["verified"]:
                conf = result.get("confidence", "?")
                print(f"  ✓ 검증 완료 (신뢰도: {conf})")
                if result.get("issues"):
                    print(f"    참고: {', '.join(result['issues'])}")
                stats["verified"] += 1
            else:
                print(f"  ✗ 의심스러움")
                for issue in result.get("issues", []):
                    print(f"    - {issue}")
                if result.get("corrections"):
                    print(f"    수정 제안: {result['corrections']}")
                if result.get("note"):
                    print(f"    메모: {result['note']}")
                stats["suspicious"] += 1
                suspicious_list.append({
                    "text": q["text"][:60],
                    "author": q["author"],
                    "issues": result.get("issues", []),
                    "note": result.get("note", ""),
                })

        except Exception as e:
            print(f"  오류: {e}")
            stats["errors"] += 1

    # 요약
    print(f"\n{'='*60}")
    print(f"검증 완료!")
    print(f"  검증 통과: {stats['verified']}개")
    print(f"  의심스러움: {stats['suspicious']}개")
    print(f"  오류: {stats['errors']}개")

    if suspicious_list:
        print(f"\n--- 의심스러운 명언 목록 ---")
        for s in suspicious_list:
            print(f"  [{s['author']}] \"{s['text']}...\"")
            for issue in s["issues"]:
                print(f"    - {issue}")

    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="명언 팩트체크")
    parser.add_argument("--limit", type=int, help="검증할 최대 개수")
    parser.add_argument("--all", action="store_true", help="검증 완료된 것도 재검증")
    args = parser.parse_args()

    factcheck(limit=args.limit, include_verified=args.all)
