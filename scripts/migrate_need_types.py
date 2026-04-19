"""
need_types 컬럼 추가 + 기존 태그 기반 자동 매핑.

사용법:
    python scripts/migrate_need_types.py              # dry-run
    python scripts/migrate_need_types.py --apply      # 실제 반영
"""

import argparse
import json
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv(".env")

NEED_MAPPING = {
    "motivation": {
        "keywords": [
            "끈기", "노력", "도전", "용기", "행동", "인내", "열정",
            "목표", "성공", "실패", "실천", "동기부여",
        ],
        "situations": [
            "게으를 때", "꾸준함이 필요할 때", "목표가 멀게 느껴질 때",
            "포기하고 싶을 때", "도전을 망설일 때",
        ],
    },
    "comfort": {
        "keywords": ["고통", "회복", "희망", "외로움", "두려움"],
        "situations": [
            "힘든 시기를 보낼 때", "절망적일 때", "좌절했을 때",
            "실패했을 때", "외로울 때", "희망이 필요할 때",
            "힘든 상황에서 거리를 두고 싶을 때", "불운할 때", "두려울 때",
        ],
    },
    "reflection": {
        "keywords": [
            "철학", "존재", "자아", "의미", "자기성찰",
            "인생", "시간", "죽음", "운명", "선택", "초월",
        ],
        "situations": [
            "자기 성찰", "삶의 의미를 찾을 때", "인생의 선택",
            "과거를 돌아볼 때", "죽음을 생각할 때", "현재를 살고 싶을 때",
            "변화를 마주할 때", "미래가 불안할 때",
        ],
    },
    "insight": {
        "keywords": ["학습", "지식", "지혜", "겸손", "교육", "창의성"],
        "situations": [
            "배움의 자세", "지식의 가치", "깊이 이해하고 싶을 때",
            "공부하기 싫을 때", "새로운 관점이 필요할 때",
            "과학적 사고", "창의적 사고",
        ],
    },
    "relationship": {
        "keywords": ["사랑", "관계", "우정", "가족", "헌신", "감사", "공동체"],
        "situations": [
            "관계의 소중함", "관계가 어려울 때",
            "사랑을 느낄 때", "사랑의 본질을 고민할 때", "감사할 때",
        ],
    },
    "humor": {
        "keywords": ["유머", "위트"],
        "situations": [
            "웃음이 필요할 때", "일상의 소소함", "기분 전환이 필요할 때",
        ],
    },
}


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


def compute_need_types(keywords, situations):
    """키워드/상황 리스트에서 need_types를 도출."""
    scores = {}
    kws = set(keywords) if isinstance(keywords, list) else set()
    sits = set(situations) if isinstance(situations, list) else set()

    for need, mapping in NEED_MAPPING.items():
        kw_match = len(kws & set(mapping["keywords"]))
        sit_match = len(sits & set(mapping["situations"]))
        score = kw_match * 1 + sit_match * 2  # 상황 매칭에 더 높은 가중치
        if score > 0:
            scores[need] = score

    if not scores:
        return ["reflection"]  # 폴백

    # 상위 3개까지만 (점수순)
    sorted_needs = sorted(scores.items(), key=lambda x: -x[1])
    return [n for n, _ in sorted_needs[:3]]


def run(apply=False):
    conn = get_db_connection()
    cur = conn.cursor()

    mode = "APPLY" if apply else "DRY-RUN"
    print(f"=== need_types 마이그레이션 [{mode}] ===\n")

    # 1. 컬럼 추가
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'quotes' AND column_name = 'need_types'
    """)
    has_column = cur.fetchone() is not None

    if not has_column:
        print("[DDL] need_types 컬럼 추가")
        if apply:
            cur.execute("ALTER TABLE quotes ADD COLUMN need_types VARCHAR(20)[]")
            conn.commit()
    else:
        print("[DDL] need_types 컬럼 이미 존재")

    # 2. 전체 명언의 need_types 계산 + 업데이트
    cur.execute("SELECT id, keywords, situation FROM quotes")
    quotes = cur.fetchall()

    dist = {}
    for qid, kws, sits in quotes:
        needs = compute_need_types(kws, sits)
        for n in needs:
            dist[n] = dist.get(n, 0) + 1

        if apply:
            cur.execute(
                "UPDATE quotes SET need_types = %s WHERE id = %s",
                (needs, qid),
            )

    print(f"\n[매핑] {len(quotes)}개 명언에 need_types 할당 {'완료' if apply else '예정'}")
    print("\nneed_type 분포:")
    for need, cnt in sorted(dist.items(), key=lambda x: -x[1]):
        print(f"  {need}: {cnt}건")

    # 3. need_types가 NULL인 것 확인
    if apply:
        conn.commit()
        cur.execute("SELECT count(*) FROM quotes WHERE need_types IS NULL")
        null_cnt = cur.fetchone()[0]
        print(f"\nneed_types NULL: {null_cnt}건")
    else:
        conn.rollback()

    print(f"\n{'✅ 마이그레이션 완료' if apply else '📋 dry-run 완료. --apply로 실행하세요.'}")
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    run(apply=args.apply)
