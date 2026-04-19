"""
태깅 검증 결과를 DB에 반영하는 스크립트.

번역-원문 불일치(translation_mismatch)는 태그만 수정하고 원문은 건드리지 않음.
원문 교정은 별도 작업으로 진행.

사용법:
    python scripts/apply_validation.py              # dry-run
    python scripts/apply_validation.py --apply      # 실제 반영
"""

import argparse
import json
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv(".env")


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


def run(apply=False):
    conn = get_db_connection()
    cur = conn.cursor()

    # 마스터 목록
    cur.execute("SELECT id, name FROM keywords")
    kw_name_to_id = {r[1]: r[0] for r in cur.fetchall()}

    cur.execute("SELECT id, name FROM situations")
    sit_name_to_id = {r[1]: r[0] for r in cur.fetchall()}

    # 검증 결과 로드
    with open("data/all_validation_issues.json", "r", encoding="utf-8") as f:
        issues = json.load(f)

    mode = "APPLY" if apply else "DRY-RUN"
    print(f"=== 태깅 검증 결과 반영 [{mode}] ===")
    print(f"총 {len(issues)}건 수정 대상\n")

    # 유형별 집계
    types = {}
    for issue in issues:
        t = issue.get("issue_type", "unknown")
        types[t] = types.get(t, 0) + 1
    for t, cnt in sorted(types.items(), key=lambda x: -x[1]):
        print(f"  {t}: {cnt}건")
    print()

    applied = 0
    skipped = 0
    errors = 0

    for issue in issues:
        qid = issue["id"]
        new_kws = issue.get("fixed_keywords", [])
        new_sits = issue.get("fixed_situations", [])

        # 마스터에 있는 것만 필터
        valid_kws = [k for k in new_kws if k in kw_name_to_id]
        valid_sits = [s for s in new_sits if s in sit_name_to_id]

        if not valid_kws or not valid_sits:
            skipped += 1
            continue

        new_kw_ids = [kw_name_to_id[k] for k in valid_kws]
        new_sit_ids = [sit_name_to_id[s] for s in valid_sits]

        if apply:
            try:
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
                        qid,
                    ),
                )
                applied += 1
            except Exception as e:
                print(f"  ERROR {qid[:8]}: {e}")
                errors += 1
        else:
            applied += 1

    print(f"수정 {'완료' if apply else '예정'}: {applied}건")
    print(f"스킵 (빈 태그): {skipped}건")
    if errors:
        print(f"오류: {errors}건")

    if apply:
        conn.commit()
        print("\n✅ DB 반영 완료")
    else:
        conn.rollback()
        print("\n📋 dry-run 완료. --apply 로 실제 반영하세요.")

    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    run(apply=args.apply)
