"""
명언 데이터 품질 검증 스크립트.

사용법:
    python scripts/validate.py
"""

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_db():
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=int(os.getenv("PG_PORT", "5432")),
        user=os.getenv("PG_USER", "youheaukjun"),
        password=os.getenv("PG_PASSWORD", ""),
        dbname=os.getenv("PG_DATABASE", "quotes_db"),
    )


def validate():
    conn = get_db()
    cur = conn.cursor()
    issues = []

    print("=" * 60)
    print("명언 데이터 품질 검증 리포트")
    print("=" * 60)

    # 1. 기본 통계
    cur.execute("SELECT COUNT(*) FROM quotes")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM authors")
    total_authors = cur.fetchone()[0]
    print(f"\n총 명언: {total}개 | 총 저자: {total_authors}명\n")

    # 2. 필수 필드 누락
    print("--- 필수 필드 누락 ---")

    cur.execute("SELECT id, text FROM quotes WHERE text IS NULL OR text = ''")
    rows = cur.fetchall()
    if rows:
        issues.append(f"텍스트 없는 명언: {len(rows)}개")
        for r in rows:
            print(f"  [ERROR] quote {r[0]}: text 없음")

    cur.execute("SELECT id, text FROM quotes WHERE keyword_ids IS NULL OR array_length(keyword_ids, 1) IS NULL")
    rows = cur.fetchall()
    if rows:
        issues.append(f"키워드 없는 명언: {len(rows)}개")
        for r in rows:
            print(f"  [WARN] \"{r[1][:40]}...\": keyword_ids 없음")

    cur.execute("SELECT id, text FROM quotes WHERE situation_ids IS NULL OR array_length(situation_ids, 1) IS NULL")
    rows = cur.fetchall()
    if rows:
        issues.append(f"상황 없는 명언: {len(rows)}개")
        for r in rows:
            print(f"  [WARN] \"{r[1][:40]}...\": situation_ids 없음")

    if not issues:
        print("  모두 정상")

    # 3. 마스터 무결성 — keyword_ids
    print("\n--- 키워드 마스터 무결성 ---")
    cur.execute("""
        SELECT DISTINCT kid FROM quotes, unnest(keyword_ids) AS kid
        WHERE kid NOT IN (SELECT id FROM keywords)
    """)
    orphans = cur.fetchall()
    if orphans:
        issues.append(f"마스터에 없는 키워드 ID: {len(orphans)}개")
        for o in orphans:
            print(f"  [ERROR] 키워드 ID {o[0]}: 마스터에 없음")
    else:
        print("  모두 정상")

    # 4. 마스터 무결성 — situation_ids
    print("\n--- 상황 마스터 무결성 ---")
    cur.execute("""
        SELECT DISTINCT sid FROM quotes, unnest(situation_ids) AS sid
        WHERE sid NOT IN (SELECT id FROM situations)
    """)
    orphans = cur.fetchall()
    if orphans:
        issues.append(f"마스터에 없는 상황 ID: {len(orphans)}개")
        for o in orphans:
            print(f"  [ERROR] 상황 ID {o[0]}: 마스터에 없음")
    else:
        print("  모두 정상")

    # 5. 저자 FK 누락
    print("\n--- 저자 FK 누락 ---")
    cur.execute("SELECT id, name FROM authors WHERE profession_id IS NULL")
    rows = cur.fetchall()
    if rows:
        issues.append(f"직업 미지정 저자: {len(rows)}명")
        for r in rows:
            print(f"  [WARN] {r[1]}: profession_id NULL")

    cur.execute("SELECT id, name FROM authors WHERE field_id IS NULL")
    rows = cur.fetchall()
    if rows:
        issues.append(f"분야 미지정 저자: {len(rows)}명")
        for r in rows:
            print(f"  [WARN] {r[1]}: field_id NULL")

    if not any("저자" in i for i in issues[-2:] if issues):
        print("  모두 정상")

    # 6. 중복 의심 (유사도 > 0.4)
    print("\n--- 중복 의심 명언 ---")
    cur.execute("""
        SELECT q1.text, q2.text, similarity(q1.text, q2.text) AS sim
        FROM quotes q1, quotes q2
        WHERE q1.id < q2.id AND similarity(q1.text, q2.text) > 0.4
        ORDER BY sim DESC LIMIT 10
    """)
    dups = cur.fetchall()
    if dups:
        issues.append(f"중복 의심: {len(dups)}쌍")
        for d in dups:
            print(f"  [WARN] 유사도 {d[2]:.2f}")
            print(f"    A: \"{d[0][:50]}...\"")
            print(f"    B: \"{d[1][:50]}...\"")
    else:
        print("  중복 없음")

    # 7. 저자 정보 불일치 (같은 이름, 다른 birth_year)
    print("\n--- 저자 정보 불일치 ---")
    cur.execute("""
        SELECT name, array_agg(DISTINCT birth_year) AS years
        FROM authors
        GROUP BY name
        HAVING COUNT(DISTINCT birth_year) > 1
    """)
    conflicts = cur.fetchall()
    if conflicts:
        issues.append(f"저자 정보 불일치: {len(conflicts)}명")
        for c in conflicts:
            print(f"  [ERROR] {c[0]}: birth_year = {c[1]}")
    else:
        print("  불일치 없음")

    # 8. 미검증 명언
    print("\n--- 팩트체크 현황 ---")
    cur.execute("SELECT COUNT(*) FROM quotes WHERE verified = TRUE")
    verified = cur.fetchone()[0]
    unverified = total - verified
    print(f"  검증 완료: {verified}개 | 미검증: {unverified}개")
    if unverified > 0:
        issues.append(f"미검증 명언: {unverified}개")

    # 요약
    print(f"\n{'='*60}")
    if issues:
        print(f"발견된 이슈: {len(issues)}건")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("이슈 없음. 데이터 품질 양호.")
    print(f"{'='*60}")

    cur.close()
    conn.close()
    return len(issues)


if __name__ == "__main__":
    validate()
