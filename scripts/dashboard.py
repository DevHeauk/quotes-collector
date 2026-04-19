"""
명언 데이터 현황 대시보드.

사용법:
    python scripts/dashboard.py
    # 브라우저에서 http://localhost:5050 접속
"""

import glob
import json
import os
import uuid
from functools import wraps

import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)


def get_db():
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


def query(sql):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


@app.route("/api/stats")
def stats():
    conn = get_db()
    cur = conn.cursor()
    counts = {}
    for table in ["quotes", "authors", "author_relations", "keywords", "situations", "fields"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cur.fetchone()[0]
    cur.close()
    conn.close()
    return jsonify(counts)


@app.route("/api/by-field")
def by_field():
    return jsonify(query("""
        SELECT f.name as field, COUNT(*) as count
        FROM quotes q
        JOIN authors a ON q.author_id = a.id
        JOIN fields f ON a.field_id = f.id
        GROUP BY f.name ORDER BY count DESC
    """))


@app.route("/api/by-nationality")
def by_nationality():
    return jsonify(query("""
        SELECT a.nationality, COUNT(*) as count
        FROM quotes q JOIN authors a ON q.author_id = a.id
        GROUP BY a.nationality ORDER BY count DESC
    """))


@app.route("/api/by-keyword")
def by_keyword():
    return jsonify(query("""
        SELECT k.name as keyword, k.group_name, COUNT(*) as count
        FROM quotes q, unnest(q.keyword_ids) AS kid
        JOIN keywords k ON k.id = kid
        GROUP BY k.name, k.group_name ORDER BY count DESC LIMIT 30
    """))


@app.route("/api/by-keyword-group")
def by_keyword_group():
    return jsonify(query("""
        SELECT COALESCE(k.group_name, '미분류') as group_name, COUNT(*) as count
        FROM quotes q, unnest(q.keyword_ids) AS kid
        JOIN keywords k ON k.id = kid
        GROUP BY k.group_name ORDER BY count DESC
    """))


@app.route("/api/by-situation")
def by_situation():
    return jsonify(query("""
        SELECT s.name as situation, s.group_name, COUNT(*) as count
        FROM quotes q, unnest(q.situation_ids) AS sid
        JOIN situations s ON s.id = sid
        GROUP BY s.name, s.group_name ORDER BY count DESC LIMIT 30
    """))


@app.route("/api/by-situation-group")
def by_situation_group():
    return jsonify(query("""
        SELECT COALESCE(s.group_name, '미분류') as group_name, COUNT(*) as count
        FROM quotes q, unnest(q.situation_ids) AS sid
        JOIN situations s ON s.id = sid
        GROUP BY s.group_name ORDER BY count DESC
    """))


@app.route("/api/by-profession")
def by_profession():
    return jsonify(query("""
        SELECT p.name as profession, p.group_name, COUNT(*) as count
        FROM quotes q
        JOIN authors a ON q.author_id = a.id
        JOIN professions p ON a.profession_id = p.id
        GROUP BY p.name, p.group_name ORDER BY count DESC
    """))


@app.route("/api/by-profession-group")
def by_profession_group():
    return jsonify(query("""
        SELECT COALESCE(p.group_name, '미분류') as group_name, COUNT(*) as count
        FROM quotes q
        JOIN authors a ON q.author_id = a.id
        JOIN professions p ON a.profession_id = p.id
        GROUP BY p.group_name ORDER BY count DESC
    """))


@app.route("/api/by-author")
def by_author():
    return jsonify(query("""
        SELECT a.name, f.name as field, p.name as profession, a.nationality, COUNT(*) as count
        FROM quotes q
        JOIN authors a ON q.author_id = a.id
        LEFT JOIN fields f ON a.field_id = f.id
        LEFT JOIN professions p ON a.profession_id = p.id
        GROUP BY a.id, a.name, f.name, p.name, a.nationality
        ORDER BY count DESC LIMIT 20
    """))


@app.route("/api/relations")
def relations():
    return jsonify(query("""
        SELECT
            a1.name as from_name, a2.name as to_name,
            ar.relation_type
        FROM author_relations ar
        JOIN authors a1 ON ar.from_author_id = a1.id
        JOIN authors a2 ON ar.to_author_id = a2.id
        ORDER BY ar.relation_type, a1.name
    """))


@app.route("/api/collection-history")
def collection_history():
    return jsonify(query("""
        SELECT category, requested_count, saved_count, duplicate_count, error_count,
               created_at::text
        FROM collection_logs
        ORDER BY created_at DESC LIMIT 30
    """))


@app.route("/api/verification-stats")
def verification_stats():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM quotes WHERE verified = TRUE")
    verified = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM quotes WHERE verified = FALSE")
    unverified = cur.fetchone()[0]
    cur.close()
    conn.close()
    return jsonify({"verified": verified, "unverified": unverified})


@app.route("/api/recent")
def recent():
    return jsonify(query("""
        SELECT q.text, a.name as author, q.keywords, q.created_at::text
        FROM quotes q JOIN authors a ON q.author_id = a.id
        ORDER BY q.created_at DESC LIMIT 10
    """))


@app.route("/api/trends")
def trends():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT fetched_at::text, timeframe, data FROM trends ORDER BY fetched_at DESC LIMIT 1")
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return jsonify({"error": "트렌드 데이터가 없습니다."}), 404
    result = row[2] if isinstance(row[2], dict) else json.loads(row[2])
    result["fetched_at"] = row[0]
    result["timeframe"] = row[1]
    return jsonify(result)


# ===========================================================================
# Admin API
# ===========================================================================

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not ADMIN_TOKEN:
            return jsonify({"error": "ADMIN_TOKEN not configured"}), 500
        auth = request.headers.get("Authorization", "")
        if auth != f"Bearer {ADMIN_TOKEN}":
            return jsonify({"error": "unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/admin/migrate", methods=["POST"])
def admin_migrate():
    """DB 마이그레이션 실행."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_interactions (
            id VARCHAR(36) PRIMARY KEY,
            device_id VARCHAR(64) NOT NULL,
            quote_id VARCHAR(36) NOT NULL REFERENCES quotes(id),
            interaction_type VARCHAR(20) NOT NULL,
            dwell_seconds FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_interactions_device ON user_interactions(device_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_interactions_created ON user_interactions(created_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_interactions_device_type ON user_interactions(device_id, interaction_type)")
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "migrated"})


@app.route("/admin/publish-all", methods=["POST"])
def admin_publish_all():
    """draft 상태 명언을 일괄 published로 변경."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE quotes SET status = 'published' WHERE status = 'draft'")
    count = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"updated": count})


# ---------------------------------------------------------------------------
# Admin Console API — 명언 CRUD
# ---------------------------------------------------------------------------

@app.route("/admin/api/quotes")
@require_admin
def admin_quotes_list():
    """명언 목록 (필터 + 페이지네이션)."""
    page = request.args.get("page", 1, type=int)
    limit = min(request.args.get("limit", 20, type=int), 100)
    offset = (page - 1) * limit

    where = []
    params = []

    status = request.args.get("status")
    if status:
        where.append("q.status = %s")
        params.append(status)

    keyword_group = request.args.get("keyword_group")
    if keyword_group:
        where.append("EXISTS (SELECT 1 FROM keywords k WHERE k.id = ANY(q.keyword_ids) AND k.group_name = %s)")
        params.append(keyword_group)

    reliability = request.args.get("reliability")
    if reliability:
        where.append("q.source_reliability = %s")
        params.append(reliability)

    search = request.args.get("search", "").strip()
    if search:
        where.append("(q.text ILIKE %s OR a.name ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])

    where_clause = " AND ".join(where) if where else "1=1"

    conn = get_db()
    cur = conn.cursor()

    # total count
    cur.execute(f"""
        SELECT COUNT(*) FROM quotes q
        JOIN authors a ON q.author_id = a.id
        WHERE {where_clause}
    """, params)
    total = cur.fetchone()[0]

    cur.execute(f"""
        SELECT q.id, q.text, q.text_original, q.original_language, q.source, q.year,
               q.status, q.source_reliability, q.created_at::text,
               q.keyword_ids, q.situation_ids,
               a.id as author_id, a.name as author_name,
               ARRAY(SELECT k.name FROM keywords k WHERE k.id = ANY(q.keyword_ids)) as keywords,
               ARRAY(SELECT s.name FROM situations s WHERE s.id = ANY(q.situation_ids)) as situations
        FROM quotes q
        JOIN authors a ON q.author_id = a.id
        WHERE {where_clause}
        ORDER BY q.created_at DESC
        LIMIT %s OFFSET %s
    """, params + [limit, offset])
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify({"quotes": rows, "total": total, "page": page, "limit": limit})


@app.route("/admin/api/quotes", methods=["POST"])
@require_admin
def admin_quotes_create():
    """명언 추가."""
    data = request.get_json()
    text = data.get("text", "").strip()
    author_id = data.get("author_id", "").strip()
    if not text or not author_id:
        return jsonify({"error": "text and author_id required"}), 400

    qid = str(uuid.uuid4())
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO quotes (id, text, text_original, original_language, author_id,
                            source, year, keywords, situation, keyword_ids, situation_ids,
                            status, source_reliability)
        VALUES (%s, %s, %s, %s, %s, %s, %s, '[]'::jsonb, '[]'::jsonb, %s, %s, %s, %s)
    """, (
        qid, text,
        data.get("text_original") or None,
        data.get("original_language") or None,
        author_id,
        data.get("source") or None,
        data.get("year") or None,
        data.get("keyword_ids") or [],
        data.get("situation_ids") or [],
        data.get("status", "draft"),
        data.get("source_reliability", "unknown"),
    ))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": qid}), 201


@app.route("/admin/api/quotes/<quote_id>", methods=["PATCH"])
@require_admin
def admin_quotes_update(quote_id):
    """명언 개별 수정 (변경 필드만)."""
    data = request.get_json()
    allowed = {"text", "text_original", "original_language", "author_id",
               "source", "year", "status", "source_reliability",
               "keyword_ids", "situation_ids"}
    sets = []
    params = []
    for key, val in data.items():
        if key in allowed:
            sets.append(f"{key} = %s")
            params.append(val)
    if not sets:
        return jsonify({"error": "no valid fields"}), 400

    params.append(quote_id)
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"UPDATE quotes SET {', '.join(sets)} WHERE id = %s", params)
    if cur.rowcount == 0:
        cur.close(); conn.close()
        return jsonify({"error": "not found"}), 404
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"updated": True})


@app.route("/admin/api/quotes/<quote_id>", methods=["DELETE"])
@require_admin
def admin_quotes_delete(quote_id):
    """명언 삭제 (interaction cascade)."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM user_interactions WHERE quote_id = %s", (quote_id,))
    cur.execute("DELETE FROM quotes WHERE id = %s", (quote_id,))
    if cur.rowcount == 0:
        cur.close(); conn.close()
        return jsonify({"error": "not found"}), 404
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"deleted": True})


@app.route("/admin/api/quotes/batch-status", methods=["POST"])
@require_admin
def admin_quotes_batch_status():
    """일괄 상태 변경."""
    data = request.get_json()
    ids = data.get("ids", [])[:200]
    status = data.get("status", "")
    if not ids or status not in ("draft", "reviewed", "published", "rejected"):
        return jsonify({"error": "ids and valid status required"}), 400

    conn = get_db()
    cur = conn.cursor()
    placeholders = ",".join(["%s"] * len(ids))
    cur.execute(f"UPDATE quotes SET status = %s WHERE id IN ({placeholders})", [status] + ids)
    count = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"updated": count})


@app.route("/admin/api/quotes/batch-delete", methods=["POST"])
@require_admin
def admin_quotes_batch_delete():
    """일괄 삭제."""
    data = request.get_json()
    ids = data.get("ids", [])[:200]
    if not ids:
        return jsonify({"error": "ids required"}), 400

    conn = get_db()
    cur = conn.cursor()
    placeholders = ",".join(["%s"] * len(ids))
    cur.execute(f"DELETE FROM user_interactions WHERE quote_id IN ({placeholders})", ids)
    cur.execute(f"DELETE FROM quotes WHERE id IN ({placeholders})", ids)
    count = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"deleted": count})


# ---------------------------------------------------------------------------
# Admin Console API — 저자 CRUD
# ---------------------------------------------------------------------------

@app.route("/admin/api/authors")
@require_admin
def admin_authors_list():
    """저자 목록 (검색 + 페이지네이션)."""
    page = request.args.get("page", 1, type=int)
    limit = min(request.args.get("limit", 20, type=int), 100)
    offset = (page - 1) * limit
    search = request.args.get("search", "").strip()

    where = []
    params = []
    if search:
        where.append("a.name ILIKE %s")
        params.append(f"%{search}%")
    where_clause = " AND ".join(where) if where else "1=1"

    conn = get_db()
    cur = conn.cursor()

    cur.execute(f"SELECT COUNT(*) FROM authors a WHERE {where_clause}", params)
    total = cur.fetchone()[0]

    cur.execute(f"""
        SELECT a.id, a.name, a.nationality, a.birth_year,
               p.id as profession_id, p.name as profession,
               f.id as field_id, f.name as field,
               COUNT(q.id) as quote_count
        FROM authors a
        LEFT JOIN professions p ON a.profession_id = p.id
        LEFT JOIN fields f ON a.field_id = f.id
        LEFT JOIN quotes q ON q.author_id = a.id
        WHERE {where_clause}
        GROUP BY a.id, a.name, a.nationality, a.birth_year, p.id, p.name, f.id, f.name
        ORDER BY quote_count DESC, a.name
        LIMIT %s OFFSET %s
    """, params + [limit, offset])
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify({"authors": rows, "total": total, "page": page, "limit": limit})


@app.route("/admin/api/authors", methods=["POST"])
@require_admin
def admin_authors_create():
    """저자 추가."""
    data = request.get_json()
    name = data.get("name", "").strip()
    nationality = data.get("nationality", "").strip()
    birth_year = data.get("birth_year")
    if not name or not nationality or birth_year is None:
        return jsonify({"error": "name, nationality, birth_year required"}), 400

    aid = str(uuid.uuid4())
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO authors (id, name, nationality, birth_year, profession_id, field_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (aid, name, nationality, birth_year,
          data.get("profession_id") or None,
          data.get("field_id") or None))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": aid}), 201


@app.route("/admin/api/authors/<author_id>", methods=["PATCH"])
@require_admin
def admin_authors_update(author_id):
    """저자 수정."""
    data = request.get_json()
    allowed = {"name", "nationality", "birth_year", "profession_id", "field_id"}
    sets = []
    params = []
    for key, val in data.items():
        if key in allowed:
            sets.append(f"{key} = %s")
            params.append(val)
    if not sets:
        return jsonify({"error": "no valid fields"}), 400

    params.append(author_id)
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"UPDATE authors SET {', '.join(sets)} WHERE id = %s", params)
    if cur.rowcount == 0:
        cur.close(); conn.close()
        return jsonify({"error": "not found"}), 404
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"updated": True})


@app.route("/admin/api/authors/<author_id>/preview-delete")
@require_admin
def admin_authors_preview_delete(author_id):
    """저자 삭제 영향 미리보기."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM quotes WHERE author_id = %s", (author_id,))
    quote_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM author_relations WHERE from_author_id = %s OR to_author_id = %s",
                (author_id, author_id))
    relation_count = cur.fetchone()[0]
    cur.execute("""
        SELECT COUNT(*) FROM user_interactions
        WHERE quote_id IN (SELECT id FROM quotes WHERE author_id = %s)
    """, (author_id,))
    interaction_count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return jsonify({
        "quote_count": quote_count,
        "relation_count": relation_count,
        "interaction_count": interaction_count,
    })


@app.route("/admin/api/authors/<author_id>", methods=["DELETE"])
@require_admin
def admin_authors_delete(author_id):
    """저자 + 소속 명언 + 관계 + interaction 전부 삭제."""
    conn = get_db()
    cur = conn.cursor()
    # 1. interaction 삭제 (해당 저자 명언의)
    cur.execute("""
        DELETE FROM user_interactions
        WHERE quote_id IN (SELECT id FROM quotes WHERE author_id = %s)
    """, (author_id,))
    i_count = cur.rowcount
    # 2. 명언 삭제
    cur.execute("DELETE FROM quotes WHERE author_id = %s", (author_id,))
    q_count = cur.rowcount
    # 3. 관계 삭제
    cur.execute("DELETE FROM author_relations WHERE from_author_id = %s OR to_author_id = %s",
                (author_id, author_id))
    r_count = cur.rowcount
    # 4. 저자 삭제
    cur.execute("DELETE FROM authors WHERE id = %s", (author_id,))
    if cur.rowcount == 0:
        conn.rollback()
        cur.close(); conn.close()
        return jsonify({"error": "not found"}), 404
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({
        "deleted_quotes": q_count,
        "deleted_relations": r_count,
        "deleted_interactions": i_count,
    })


# ---------------------------------------------------------------------------
# Admin Console API — 마스터 데이터
# ---------------------------------------------------------------------------

@app.route("/admin/api/masters/keywords")
@require_admin
def admin_masters_keywords():
    return jsonify(query("SELECT id, name, group_name FROM keywords ORDER BY group_name, name"))


@app.route("/admin/api/masters/situations")
@require_admin
def admin_masters_situations():
    return jsonify(query("SELECT id, name, group_name FROM situations ORDER BY group_name, name"))


@app.route("/admin/api/masters/professions")
@require_admin
def admin_masters_professions():
    return jsonify(query("SELECT id, name, group_name FROM professions ORDER BY group_name, name"))


@app.route("/admin/api/masters/fields")
@require_admin
def admin_masters_fields():
    return jsonify(query("SELECT id, name FROM fields ORDER BY name"))


# ===========================================================================
# App API (모바일 앱 전용)
# ===========================================================================

def _quote_to_dict(row, cols):
    """쿼리 결과를 앱용 dict로 변환."""
    d = dict(zip(cols, row))
    for k in ("keywords", "situations"):
        if k in d and isinstance(d[k], str):
            d[k] = json.loads(d[k])
    return d


def _build_personalization(args):
    """개인화 파라미터에서 WHERE/ORDER BY 조건과 params를 빌드.

    needs 파라미터(신규): need_types 배열 매칭 보너스 (1차 시그널).
    situations/keywords(레거시): 기존 그룹 매칭 보너스 (2차 시그널).
    프로필 가중치(kw_weights, sit_weights): 행동 기반 보너스 (3차 시그널).
    profile_strength에 따라 온보딩/행동 비율을 혼합한다.
    """
    needs_raw = args.get("needs", "")
    sit_groups = args.get("situations", "")
    kw_groups = args.get("keywords", "")
    exclude_ids = args.get("exclude", "")
    needs_list = [n.strip() for n in needs_raw.split(",") if n.strip()]
    sit_list = [s.strip() for s in sit_groups.split(",") if s.strip()]
    kw_list = [k.strip() for k in kw_groups.split(",") if k.strip()]
    exclude_list = [e.strip() for e in exclude_ids.split(",") if e.strip()]

    # 프로필 가중치 파싱
    kw_weights = {}
    sit_weights = {}
    profile_strength = args.get("profile_strength", "")
    try:
        raw = args.get("kw_weights", "")
        if raw:
            kw_weights = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        pass
    try:
        raw = args.get("sit_weights", "")
        if raw:
            sit_weights = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        pass

    # 콜드 스타트 혼합 비율: 행동 비율 결정
    behavior_ratio = {"weak": 0.3, "moderate": 0.7, "strong": 1.0}.get(profile_strength, 0.0)
    onboarding_ratio = 1.0 - behavior_ratio

    params = []
    bonus_clauses = []
    where_clauses = []

    # 1차: need_types 매칭 보너스 (가장 강한 시그널)
    if needs_list and onboarding_ratio > 0:
        bonus_clauses.append(f"""
            CASE WHEN q.need_types && %s::varchar[]
            THEN {4 * onboarding_ratio:.2f} ELSE 0 END
        """)
        params.append(needs_list)

    # 2차: 레거시 온보딩 보너스 (하위 호환)
    if sit_list and onboarding_ratio > 0:
        bonus_clauses.append(f"""
            CASE WHEN EXISTS (
                SELECT 1 FROM situations s
                WHERE s.id = ANY(q.situation_ids) AND s.group_name = ANY(%s)
            ) THEN {3 * onboarding_ratio:.2f} ELSE 0 END
        """)
        params.append(sit_list)

    if kw_list and onboarding_ratio > 0:
        bonus_clauses.append(f"""
            CASE WHEN EXISTS (
                SELECT 1 FROM keywords k
                WHERE k.id = ANY(q.keyword_ids) AND k.group_name = ANY(%s)
            ) THEN {2 * onboarding_ratio:.2f} ELSE 0 END
        """)
        params.append(kw_list)

    # 3차: 행동 기반 동적 보너스 (프로필 가중치 × 5 × behavior_ratio)
    if kw_weights and behavior_ratio > 0:
        for group_name, weight in kw_weights.items():
            bonus_val = weight * 5 * behavior_ratio
            if bonus_val > 0.1:
                bonus_clauses.append(f"""
                    CASE WHEN EXISTS (
                        SELECT 1 FROM keywords k
                        WHERE k.id = ANY(q.keyword_ids) AND k.group_name = %s
                    ) THEN {bonus_val:.2f} ELSE 0 END
                """)
                params.append(group_name)

    if sit_weights and behavior_ratio > 0:
        for group_name, weight in sit_weights.items():
            bonus_val = weight * 5 * behavior_ratio
            if bonus_val > 0.1:
                bonus_clauses.append(f"""
                    CASE WHEN EXISTS (
                        SELECT 1 FROM situations s
                        WHERE s.id = ANY(q.situation_ids) AND s.group_name = %s
                    ) THEN {bonus_val:.2f} ELSE 0 END
                """)
                params.append(group_name)

    if exclude_list:
        where_clauses.append("q.id != ALL(%s)")
        params.append(exclude_list)

    bonus_sql = " + ".join(bonus_clauses) if bonus_clauses else "0"
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    return params, bonus_sql, where_sql


@app.route("/app/api/v1/interactions", methods=["POST"])
def app_interactions():
    """사용자 행동 로그 배치 업로드."""
    data = request.get_json()
    device_id = data.get("device_id", "")
    interactions = data.get("interactions", [])
    if not device_id or not interactions:
        return jsonify({"error": "device_id and interactions required"}), 400

    conn = get_db()
    cur = conn.cursor()
    saved = 0
    for item in interactions[:100]:  # 한 번에 최대 100개
        qid = item.get("quote_id", "")
        itype = item.get("type", "")
        if not qid or itype not in ("like", "unlike", "share", "view_detail", "dwell"):
            continue
        dwell_sec = None
        if itype == "dwell":
            dwell_sec = item.get("metadata", {}).get("dwell_seconds")
        ts = item.get("timestamp")
        try:
            cur.execute("""
                INSERT INTO user_interactions (id, device_id, quote_id, interaction_type, dwell_seconds, created_at)
                VALUES (%s, %s, %s, %s, %s, COALESCE(%s::timestamp, CURRENT_TIMESTAMP))
            """, (str(uuid.uuid4()), device_id, qid, itype, dwell_sec, ts))
            saved += 1
        except psycopg2.Error:
            conn.rollback()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"saved": saved})


@app.route("/app/api/v1/profile")
def app_profile():
    """사용자 행동 기반 선호 프로필 계산.

    확신 시그널(like, share)만 프로필에 직접 반영.
    참고 시그널(dwell, view_detail)은 같은 quote에 확신 시그널이 있을 때만 증폭.
    """
    device_id = request.args.get("device_id", "")
    if not device_id:
        return jsonify({"error": "device_id required"}), 400

    conn = get_db()
    cur = conn.cursor()

    # 1. 확신 시그널 조회 (like, unlike, share) + 시간 감쇠
    cur.execute("""
        SELECT quote_id, interaction_type,
               CASE
                   WHEN created_at > NOW() - INTERVAL '7 days' THEN 1.0
                   WHEN created_at > NOW() - INTERVAL '30 days' THEN 0.5
                   WHEN created_at > NOW() - INTERVAL '90 days' THEN 0.25
                   ELSE 0.1
               END as decay
        FROM user_interactions
        WHERE device_id = %s AND interaction_type IN ('like', 'unlike', 'share')
        ORDER BY created_at
    """, (device_id,))
    conviction_rows = cur.fetchall()

    if not conviction_rows:
        cur.close()
        conn.close()
        return jsonify({
            "keyword_weights": {},
            "situation_weights": {},
            "total_interactions": 0,
            "profile_strength": "weak",
        })

    # 확신 시그널이 있는 quote_id 집합
    conviction_quotes = set()
    # quote별 확신 점수 집계 (like=3, share=5, unlike=-3)
    quote_scores = {}
    score_map = {"like": 3.0, "share": 5.0, "unlike": -3.0}
    for qid, itype, decay in conviction_rows:
        conviction_quotes.add(qid)
        base = score_map.get(itype, 0)
        quote_scores[qid] = quote_scores.get(qid, 0) + base * decay

    # 2. 참고 시그널 조회 (확신 시그널이 있는 quote만)
    if conviction_quotes:
        placeholders = ",".join(["%s"] * len(conviction_quotes))
        cur.execute(f"""
            SELECT quote_id, interaction_type
            FROM user_interactions
            WHERE device_id = %s AND quote_id IN ({placeholders})
              AND interaction_type IN ('dwell', 'view_detail')
        """, [device_id] + list(conviction_quotes))
        ref_rows = cur.fetchall()

        # quote별 증폭 계수
        quote_boost = {}
        for qid, itype in ref_rows:
            if qid not in quote_boost:
                quote_boost[qid] = 1.0
            if itype == "dwell":
                quote_boost[qid] *= 1.5
            elif itype == "view_detail":
                quote_boost[qid] *= 1.3

        # 증폭 적용
        for qid, boost in quote_boost.items():
            if qid in quote_scores:
                quote_scores[qid] *= boost

    # 음수 점수인 quote 제거 (unlike으로 상쇄)
    quote_scores = {qid: s for qid, s in quote_scores.items() if s > 0}

    if not quote_scores:
        cur.close()
        conn.close()
        total = len(conviction_rows)
        return jsonify({
            "keyword_weights": {},
            "situation_weights": {},
            "total_interactions": total,
            "profile_strength": "weak" if total < 5 else "moderate",
        })

    # 3. quote별 keyword/situation 가져오기
    qids = list(quote_scores.keys())
    placeholders = ",".join(["%s"] * len(qids))
    cur.execute(f"""
        SELECT q.id,
               ARRAY(SELECT k.group_name FROM keywords k WHERE k.id = ANY(q.keyword_ids)) as kw_groups,
               ARRAY(SELECT s.group_name FROM situations s WHERE s.id = ANY(q.situation_ids)) as sit_groups
        FROM quotes q WHERE q.id IN ({placeholders})
    """, qids)

    kw_totals = {}
    sit_totals = {}
    for qid, kw_groups, sit_groups in cur.fetchall():
        score = quote_scores.get(qid, 0)
        if score <= 0:
            continue
        for g in (kw_groups or []):
            if g:
                kw_totals[g] = kw_totals.get(g, 0) + score
        for g in (sit_groups or []):
            if g:
                sit_totals[g] = sit_totals.get(g, 0) + score

    cur.close()
    conn.close()

    # 4. 정규화 (최대값 대비 0~1)
    def normalize(d):
        if not d:
            return {}
        mx = max(d.values())
        if mx <= 0:
            return {}
        return {k: round(v / mx, 3) for k, v in d.items()}

    kw_weights = normalize(kw_totals)
    sit_weights = normalize(sit_totals)

    total = len(conviction_rows)
    if total >= 20:
        strength = "strong"
    elif total >= 5:
        strength = "moderate"
    else:
        strength = "weak"

    return jsonify({
        "keyword_weights": kw_weights,
        "situation_weights": sit_weights,
        "total_interactions": total,
        "profile_strength": strength,
    })


@app.route("/app/api/v1/daily")
def app_daily():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT setseed(extract(doy from current_date)::float / 366.0)")

    params, bonus_sql, where_sql = _build_personalization(request.args)

    cur.execute(f"""
        SELECT q.id, q.text, q.text_original, q.original_language, q.source, q.year, q.impact_score,
               a.name as author_name, p.name as profession, f.name as field, a.nationality, a.birth_year,
               ARRAY(SELECT k.name FROM keywords k WHERE k.id = ANY(q.keyword_ids)) as keywords,
               ARRAY(SELECT s.name FROM situations s WHERE s.id = ANY(q.situation_ids)) as situations
        FROM quotes q
        JOIN authors a ON q.author_id = a.id
        LEFT JOIN professions p ON a.profession_id = p.id
        LEFT JOIN fields f ON a.field_id = f.id
        WHERE q.status = 'published' AND {where_sql}
        ORDER BY (COALESCE(q.impact_score, 3) + {bonus_sql}) * random()
        DESC LIMIT 1
    """, params)
    cols = [d[0] for d in cur.description]
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return jsonify({"error": "명언이 없습니다."}), 404
    d = dict(zip(cols, row))
    return jsonify({
        "id": d["id"], "text": d["text"], "text_original": d["text_original"],
        "original_language": d["original_language"], "source": d["source"],
        "year": d["year"], "impact_score": d["impact_score"],
        "keywords": d["keywords"] or [], "situations": d["situations"] or [],
        "author": {
            "name": d["author_name"], "profession": d["profession"],
            "field": d["field"], "nationality": d["nationality"], "birth_year": d["birth_year"],
        },
    })


@app.route("/app/api/v1/recommend")
def app_recommend():
    """개인화 추천 명언 N개 반환."""
    conn = get_db()
    cur = conn.cursor()

    limit = min(request.args.get("limit", 3, type=int), 20)
    params, bonus_sql, where_sql = _build_personalization(request.args)
    params.append(limit)

    cur.execute(f"""
        SELECT q.id, q.text, q.text_original, q.original_language, q.source, q.impact_score,
               q.need_types,
               a.name as author_name, p.name as profession, a.nationality,
               ARRAY(SELECT k.name FROM keywords k WHERE k.id = ANY(q.keyword_ids)) as keywords,
               ARRAY(SELECT s.name FROM situations s WHERE s.id = ANY(q.situation_ids)) as situations
        FROM quotes q
        JOIN authors a ON q.author_id = a.id
        LEFT JOIN professions p ON a.profession_id = p.id
        WHERE q.status = 'published' AND {where_sql}
        ORDER BY (COALESCE(q.impact_score, 3) + {bonus_sql}) * random()
        DESC LIMIT %s
    """, params)
    cols = [d[0] for d in cur.description]
    rows = []
    for r in cur.fetchall():
        d = dict(zip(cols, r))
        rows.append({
            "id": d["id"], "text": d["text"], "text_original": d["text_original"],
            "original_language": d["original_language"], "source": d["source"],
            "impact_score": d["impact_score"],
            "need_types": d["need_types"] or [],
            "keywords": d["keywords"] or [], "situations": d["situations"] or [],
            "author": {
                "name": d["author_name"], "profession": d["profession"],
                "nationality": d["nationality"],
            },
        })
    cur.close()
    conn.close()
    return jsonify(rows)


@app.route("/app/api/v1/categories")
def app_categories():
    return jsonify(query("""
        SELECT k.group_name, ARRAY_AGG(DISTINCT k.name) as keywords,
               COUNT(DISTINCT qk) as count
        FROM keywords k
        LEFT JOIN quotes q ON k.id = ANY(q.keyword_ids)
        LEFT JOIN unnest(q.keyword_ids) AS qk ON true
        GROUP BY k.group_name
        ORDER BY count DESC
    """))


@app.route("/app/api/v1/situations")
def app_situations():
    return jsonify(query("""
        SELECT s.group_name, ARRAY_AGG(DISTINCT s.name) as situations,
               COUNT(DISTINCT qs) as count
        FROM situations s
        LEFT JOIN quotes q ON s.id = ANY(q.situation_ids)
        LEFT JOIN unnest(q.situation_ids) AS qs ON true
        GROUP BY s.group_name
        ORDER BY count DESC
    """))


@app.route("/app/api/v1/authors")
def app_authors():
    page = request.args.get("page", 1, type=int)
    limit = min(request.args.get("limit", 20, type=int), 50)
    offset = (page - 1) * limit

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, a.name, p.name as profession, f.name as field,
               a.nationality, a.birth_year, COUNT(q.id) as quote_count
        FROM authors a
        LEFT JOIN professions p ON a.profession_id = p.id
        LEFT JOIN fields f ON a.field_id = f.id
        LEFT JOIN quotes q ON q.author_id = a.id
        GROUP BY a.id, a.name, p.name, f.name, a.nationality, a.birth_year
        HAVING COUNT(q.id) > 0
        ORDER BY quote_count DESC
        LIMIT %s OFFSET %s
    """, (limit, offset))
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(rows)


@app.route("/app/api/v1/quotes")
def app_quotes():
    page = request.args.get("page", 1, type=int)
    limit = min(request.args.get("limit", 20, type=int), 50)
    offset = (page - 1) * limit

    conn = get_db()
    cur = conn.cursor()

    where = []
    params = []

    keyword_group = request.args.get("keyword_group")
    if keyword_group:
        where.append("EXISTS (SELECT 1 FROM keywords k WHERE k.id = ANY(q.keyword_ids) AND k.group_name = %s)")
        params.append(keyword_group)

    keyword = request.args.get("keyword")
    if keyword:
        where.append("EXISTS (SELECT 1 FROM keywords k WHERE k.id = ANY(q.keyword_ids) AND k.name = %s)")
        params.append(keyword)

    situation = request.args.get("situation")
    if situation:
        where.append("EXISTS (SELECT 1 FROM situations s WHERE s.id = ANY(q.situation_ids) AND s.name = %s)")
        params.append(situation)

    situation_group = request.args.get("situation_group")
    if situation_group:
        where.append("EXISTS (SELECT 1 FROM situations s WHERE s.id = ANY(q.situation_ids) AND s.group_name = %s)")
        params.append(situation_group)

    author_id = request.args.get("author_id")
    if author_id:
        where.append("q.author_id = %s")
        params.append(author_id)

    where_clause = " AND ".join(where) if where else "1=1"
    params.extend([limit, offset])

    cur.execute(f"""
        SELECT q.id, q.text, q.text_original, q.source, q.impact_score,
               a.name as author_name, a.nationality,
               ARRAY(SELECT k.name FROM keywords k WHERE k.id = ANY(q.keyword_ids)) as keywords
        FROM quotes q
        JOIN authors a ON q.author_id = a.id
        WHERE q.status = 'published' AND {where_clause}
        ORDER BY COALESCE(q.impact_score, 3) DESC
        LIMIT %s OFFSET %s
    """, params)

    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(rows)


@app.route("/app/api/v1/quotes/<quote_id>")
def app_quote_detail(quote_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT q.id, q.text, q.text_original, q.original_language, q.source, q.year, q.impact_score,
               a.id as author_id, a.name as author_name, p.name as profession,
               f.name as field, a.nationality, a.birth_year,
               ARRAY(SELECT k.name FROM keywords k WHERE k.id = ANY(q.keyword_ids)) as keywords,
               ARRAY(SELECT s.name FROM situations s WHERE s.id = ANY(q.situation_ids)) as situations
        FROM quotes q
        JOIN authors a ON q.author_id = a.id
        LEFT JOIN professions p ON a.profession_id = p.id
        LEFT JOIN fields f ON a.field_id = f.id
        WHERE q.id = %s
    """, (quote_id,))
    cols = [d[0] for d in cur.description]
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        return jsonify({"error": "명언을 찾을 수 없습니다."}), 404

    d = dict(zip(cols, row))

    # 같은 저자의 다른 명언 3개
    cur.execute("""
        SELECT q.id, q.text, q.impact_score
        FROM quotes q WHERE q.author_id = %s AND q.id != %s
        ORDER BY COALESCE(q.impact_score, 3) DESC LIMIT 3
    """, (d["author_id"], quote_id))
    related = [{"id": r[0], "text": r[1], "impact_score": r[2]} for r in cur.fetchall()]

    cur.close(); conn.close()
    return jsonify({
        "id": d["id"], "text": d["text"], "text_original": d["text_original"],
        "original_language": d["original_language"], "source": d["source"],
        "year": d["year"], "impact_score": d["impact_score"],
        "keywords": d["keywords"] or [], "situations": d["situations"] or [],
        "author": {
            "id": d["author_id"], "name": d["author_name"], "profession": d["profession"],
            "field": d["field"], "nationality": d["nationality"], "birth_year": d["birth_year"],
        },
        "related_quotes": related,
    })


@app.route("/app/api/v1/quotes/batch", methods=["POST"])
def app_quotes_batch():
    data = request.get_json()
    ids = data.get("ids", [])[:50]
    if not ids:
        return jsonify([])

    conn = get_db()
    cur = conn.cursor()
    placeholders = ",".join(["%s"] * len(ids))
    cur.execute(f"""
        SELECT q.id, q.text, q.text_original, q.source, q.impact_score,
               a.name as author_name, a.nationality,
               ARRAY(SELECT k.name FROM keywords k WHERE k.id = ANY(q.keyword_ids)) as keywords
        FROM quotes q
        JOIN authors a ON q.author_id = a.id
        WHERE q.status = 'published' AND q.id IN ({placeholders})
    """, ids)
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    cur.close(); conn.close()
    return jsonify(rows)


# ===========================================================================
# Admin Console HTML
# ===========================================================================

@app.route("/admin")
def admin_console():
    return """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>명언 관리자 콘솔</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}

/* --- Layout --- */
.admin-header{background:#1e293b;padding:16px 24px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #334155}
.admin-header h1{font-size:20px;color:#f8fafc}
.admin-header .logout-btn{background:none;border:1px solid #64748b;color:#94a3b8;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:13px}
.admin-header .logout-btn:hover{border-color:#f87171;color:#f87171}
.admin-body{padding:24px;max-width:1400px;margin:0 auto}

/* --- Tabs --- */
.tabs{display:flex;gap:4px;margin-bottom:24px;border-bottom:2px solid #334155;padding-bottom:0}
.tab-btn{background:none;border:none;color:#94a3b8;padding:10px 20px;font-size:14px;cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all .2s}
.tab-btn:hover{color:#e2e8f0}
.tab-btn.active{color:#38bdf8;border-bottom-color:#38bdf8}
.tab-panel{display:none}
.tab-panel.active{display:block}

/* --- Auth --- */
.auth-container{display:flex;justify-content:center;align-items:center;height:100vh;background:#0f172a}
.auth-box{background:#1e293b;border-radius:12px;padding:40px;width:360px;text-align:center}
.auth-box h2{margin-bottom:24px;color:#f8fafc;font-size:20px}
.auth-box input{width:100%;padding:12px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#e2e8f0;font-size:14px;margin-bottom:16px}
.auth-box input:focus{outline:none;border-color:#38bdf8}
.auth-box button{width:100%;padding:12px;border-radius:8px;border:none;background:#38bdf8;color:#0f172a;font-weight:600;font-size:14px;cursor:pointer}
.auth-box button:hover{background:#7dd3fc}
.auth-error{color:#f87171;font-size:13px;margin-top:8px;display:none}

/* --- Buttons --- */
.btn{padding:6px 14px;border-radius:6px;border:none;font-size:13px;cursor:pointer;font-weight:500;transition:all .15s}
.btn:disabled{opacity:.4;cursor:not-allowed}
.btn-primary{background:#38bdf8;color:#0f172a}.btn-primary:hover:not(:disabled){background:#7dd3fc}
.btn-danger{background:#f87171;color:#0f172a}.btn-danger:hover:not(:disabled){background:#fca5a5}
.btn-success{background:#4ade80;color:#0f172a}.btn-success:hover:not(:disabled){background:#86efac}
.btn-warning{background:#fbbf24;color:#0f172a}.btn-warning:hover:not(:disabled){background:#fde68a}
.btn-ghost{background:none;border:1px solid #475569;color:#94a3b8}.btn-ghost:hover:not(:disabled){border-color:#94a3b8;color:#e2e8f0}
.btn-sm{padding:4px 10px;font-size:12px}

/* --- Filter bar --- */
.filter-bar{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap;align-items:center}
.filter-bar select,.filter-bar input{background:#0f172a;border:1px solid #334155;color:#e2e8f0;padding:8px 12px;border-radius:6px;font-size:13px}
.filter-bar select:focus,.filter-bar input:focus{outline:none;border-color:#38bdf8}

/* --- Batch bar --- */
.batch-bar{display:flex;gap:10px;margin-bottom:16px;align-items:center;padding:10px 16px;background:#1e293b;border-radius:8px}
.batch-bar .count{font-size:13px;color:#94a3b8;margin-right:8px}
.batch-bar select{background:#0f172a;border:1px solid #334155;color:#e2e8f0;padding:6px 10px;border-radius:6px;font-size:13px}

/* --- Table --- */
.data-table{width:100%;border-collapse:collapse;font-size:13px}
.data-table th{text-align:left;padding:10px 12px;color:#64748b;border-bottom:1px solid #334155;font-weight:500;white-space:nowrap}
.data-table td{padding:10px 12px;border-bottom:1px solid #1e293b;vertical-align:middle}
.data-table tr:hover{background:#1e293b}
.data-table input[type=checkbox]{accent-color:#38bdf8;width:16px;height:16px;cursor:pointer}
.text-truncate{max-width:300px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:inline-block;vertical-align:middle}

/* --- Badges --- */
.badge{display:inline-block;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;text-transform:uppercase}
.badge-draft{background:#334155;color:#94a3b8}
.badge-reviewed{background:#422006;color:#fbbf24}
.badge-published{background:#052e16;color:#4ade80}
.badge-rejected{background:#450a0a;color:#f87171}
.badge-tag{background:#334155;color:#94a3b8;border-radius:4px;padding:2px 6px;font-size:11px;margin:1px;font-weight:normal;text-transform:none}
.badge-reliability{font-size:11px;color:#64748b}

/* --- Status buttons --- */
.status-btns{display:flex;gap:3px}
.status-btns .btn{padding:3px 8px;font-size:11px}

/* --- Modal --- */
.modal-overlay{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.6);z-index:1000;justify-content:center;align-items:flex-start;padding-top:60px;overflow-y:auto}
.modal-overlay.active{display:flex}
.modal{background:#1e293b;border-radius:12px;width:680px;max-width:95vw;padding:24px;max-height:85vh;overflow-y:auto;margin-bottom:40px}
.modal h3{font-size:18px;color:#f8fafc;margin-bottom:20px}
.modal-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:20px;padding-top:16px;border-top:1px solid #334155}

/* --- Form --- */
.form-group{margin-bottom:16px}
.form-group label{display:block;font-size:13px;color:#94a3b8;margin-bottom:6px;font-weight:500}
.form-group input,.form-group select,.form-group textarea{width:100%;padding:10px 12px;border-radius:6px;border:1px solid #334155;background:#0f172a;color:#e2e8f0;font-size:14px;font-family:inherit}
.form-group input:focus,.form-group select:focus,.form-group textarea:focus{outline:none;border-color:#38bdf8}
.form-group textarea{min-height:80px;resize:vertical}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.checkbox-group{display:flex;flex-wrap:wrap;gap:6px;max-height:200px;overflow-y:auto;padding:8px;border:1px solid #334155;border-radius:6px;background:#0f172a}
.checkbox-group label{display:flex;align-items:center;gap:4px;font-size:12px;color:#94a3b8;cursor:pointer;padding:3px 6px;border-radius:4px}
.checkbox-group label:hover{background:#334155}
.checkbox-group-title{font-size:12px;font-weight:600;color:#64748b;margin-top:6px;margin-bottom:2px;width:100%;border-bottom:1px solid #334155;padding-bottom:3px}
.checkbox-group input[type=checkbox]{accent-color:#38bdf8}

/* --- Pagination --- */
.pagination{display:flex;justify-content:center;align-items:center;gap:12px;margin-top:20px;font-size:13px;color:#94a3b8}
.pagination .btn{min-width:80px}
.page-info{color:#64748b}

/* --- Author search dropdown --- */
.author-search-wrap{position:relative}
.author-dropdown{position:absolute;top:100%;left:0;right:0;background:#1e293b;border:1px solid #334155;border-radius:0 0 6px 6px;max-height:200px;overflow-y:auto;z-index:10;display:none}
.author-dropdown.open{display:block}
.author-dropdown-item{padding:8px 12px;font-size:13px;cursor:pointer;color:#e2e8f0}
.author-dropdown-item:hover{background:#334155}
.author-dropdown-item .sub{font-size:11px;color:#64748b}

/* --- Delete preview --- */
.delete-preview{background:#1c1917;border:1px solid #7f1d1d;border-radius:8px;padding:16px;margin:16px 0}
.delete-preview p{font-size:13px;margin-bottom:6px;color:#fca5a5}
.delete-preview .warn{font-size:14px;font-weight:600;color:#f87171;margin-bottom:12px}

/* --- Loading --- */
.loading{text-align:center;padding:40px;color:#64748b;font-size:14px}
.toast{position:fixed;bottom:24px;right:24px;background:#1e293b;border:1px solid #334155;border-radius:8px;padding:12px 20px;font-size:13px;z-index:2000;animation:slideUp .3s}
.toast-success{border-color:#4ade80;color:#4ade80}
.toast-error{border-color:#f87171;color:#f87171}
@keyframes slideUp{from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1}}
</style>
</head>
<body>

<!-- ========== AUTH SCREEN ========== -->
<div id="auth-screen" class="auth-container" style="display:none">
  <div class="auth-box">
    <h2>Admin Console</h2>
    <input type="password" id="token-input" placeholder="관리자 토큰 입력">
    <button onclick="doLogin()">로그인</button>
    <div id="auth-error" class="auth-error">인증에 실패했습니다.</div>
  </div>
</div>

<!-- ========== MAIN SCREEN ========== -->
<div id="main-screen" style="display:none">
  <div class="admin-header">
    <h1>명언 관리자 콘솔</h1>
    <button class="logout-btn" onclick="doLogout()">로그아웃</button>
  </div>
  <div class="admin-body">
    <div class="tabs">
      <button class="tab-btn active" data-tab="quotes">명언 관리</button>
      <button class="tab-btn" data-tab="authors">저자 관리</button>
    </div>

    <!-- ===================== QUOTES TAB ===================== -->
    <div id="tab-quotes" class="tab-panel active">
      <div class="filter-bar">
        <select id="f-status"><option value="">전체 상태</option><option value="draft">Draft</option><option value="reviewed">Reviewed</option><option value="published">Published</option><option value="rejected">Rejected</option></select>
        <select id="f-keyword-group"><option value="">전체 키워드 그룹</option></select>
        <select id="f-reliability"><option value="">전체 신뢰도</option><option value="verified">Verified</option><option value="attributed">Attributed</option><option value="disputed">Disputed</option><option value="unknown">Unknown</option></select>
        <input type="text" id="f-search" placeholder="텍스트/저자 검색..." style="flex:1;min-width:180px">
        <button class="btn btn-ghost" onclick="loadQuotes(1)">검색</button>
        <button class="btn btn-primary" onclick="openQuoteModal()">+ 명언 추가</button>
      </div>

      <!-- Batch bar -->
      <div id="batch-bar" class="batch-bar" style="display:none">
        <span class="count"><strong id="sel-count">0</strong>개 선택</span>
        <select id="batch-status-sel"><option value="">상태 변경...</option><option value="draft">Draft</option><option value="reviewed">Reviewed</option><option value="published">Published</option><option value="rejected">Rejected</option></select>
        <button class="btn btn-warning btn-sm" onclick="batchStatus()">적용</button>
        <button class="btn btn-danger btn-sm" onclick="batchDelete()">일괄 삭제</button>
      </div>

      <table class="data-table">
        <thead>
          <tr>
            <th><input type="checkbox" id="chk-all" onchange="toggleAll(this)"></th>
            <th>텍스트</th>
            <th>저자</th>
            <th>상태</th>
            <th>신뢰도</th>
            <th>키워드</th>
            <th>생성일</th>
            <th>액션</th>
          </tr>
        </thead>
        <tbody id="quotes-body"><tr><td colspan="8" class="loading">로딩 중...</td></tr></tbody>
      </table>
      <div class="pagination">
        <button class="btn btn-ghost btn-sm" id="q-prev" onclick="loadQuotes(qPage-1)">이전</button>
        <span id="q-page-info" class="page-info"></span>
        <button class="btn btn-ghost btn-sm" id="q-next" onclick="loadQuotes(qPage+1)">다음</button>
      </div>
    </div>

    <!-- ===================== AUTHORS TAB ===================== -->
    <div id="tab-authors" class="tab-panel">
      <div class="filter-bar">
        <input type="text" id="a-search" placeholder="저자 이름 검색..." style="flex:1;min-width:200px">
        <button class="btn btn-ghost" onclick="loadAuthors(1)">검색</button>
        <button class="btn btn-primary" onclick="openAuthorModal()">+ 저자 추가</button>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th>이름</th>
            <th>국적</th>
            <th>출생연도</th>
            <th>직업</th>
            <th>분야</th>
            <th>명언 수</th>
            <th>액션</th>
          </tr>
        </thead>
        <tbody id="authors-body"><tr><td colspan="7" class="loading">로딩 중...</td></tr></tbody>
      </table>
      <div class="pagination">
        <button class="btn btn-ghost btn-sm" id="a-prev" onclick="loadAuthors(aPage-1)">이전</button>
        <span id="a-page-info" class="page-info"></span>
        <button class="btn btn-ghost btn-sm" id="a-next" onclick="loadAuthors(aPage+1)">다음</button>
      </div>
    </div>
  </div>
</div>

<!-- ========== QUOTE MODAL ========== -->
<div id="quote-modal" class="modal-overlay">
  <div class="modal">
    <h3 id="qm-title">명언 추가</h3>
    <input type="hidden" id="qm-id">
    <div class="form-group"><label>텍스트 *</label><textarea id="qm-text" rows="3"></textarea></div>
    <div class="form-row">
      <div class="form-group"><label>원문</label><textarea id="qm-original" rows="2"></textarea></div>
      <div class="form-group"><label>원어</label>
        <select id="qm-lang"><option value="">-</option><option value="ko">한국어 (ko)</option><option value="en">영어 (en)</option><option value="zh">중국어 (zh)</option><option value="de">독일어 (de)</option><option value="fr">프랑스어 (fr)</option><option value="ja">일본어 (ja)</option><option value="la">라틴어 (la)</option><option value="el">그리스어 (el)</option><option value="ar">아랍어 (ar)</option><option value="sa">산스크리트어 (sa)</option></select>
      </div>
    </div>
    <div class="form-group"><label>저자 *</label>
      <div class="author-search-wrap">
        <input type="text" id="qm-author-search" placeholder="저자 이름으로 검색..." autocomplete="off">
        <input type="hidden" id="qm-author-id">
        <div id="qm-author-dropdown" class="author-dropdown"></div>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>출처</label><input type="text" id="qm-source"></div>
      <div class="form-group"><label>연도</label><input type="number" id="qm-year"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>상태</label>
        <select id="qm-status"><option value="draft">Draft</option><option value="reviewed">Reviewed</option><option value="published">Published</option><option value="rejected">Rejected</option></select>
      </div>
      <div class="form-group"><label>출처 신뢰도</label>
        <select id="qm-reliability"><option value="unknown">Unknown</option><option value="verified">Verified</option><option value="attributed">Attributed</option><option value="disputed">Disputed</option></select>
      </div>
    </div>
    <div class="form-group"><label>키워드</label><div id="qm-keywords" class="checkbox-group"></div></div>
    <div class="form-group"><label>상황</label><div id="qm-situations" class="checkbox-group"></div></div>
    <div class="modal-actions">
      <button class="btn btn-ghost" onclick="closeModal('quote-modal')">취소</button>
      <button class="btn btn-primary" id="qm-save" onclick="saveQuote()">저장</button>
    </div>
  </div>
</div>

<!-- ========== AUTHOR MODAL ========== -->
<div id="author-modal" class="modal-overlay">
  <div class="modal" style="width:480px">
    <h3 id="am-title">저자 추가</h3>
    <input type="hidden" id="am-id">
    <div class="form-group"><label>이름 *</label><input type="text" id="am-name"></div>
    <div class="form-row">
      <div class="form-group"><label>국적 (ISO 2자리) *</label><input type="text" id="am-nationality" maxlength="2" placeholder="KR, US, GB..."></div>
      <div class="form-group"><label>출생연도 *</label><input type="number" id="am-birth-year"></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label>직업</label><select id="am-profession"><option value="">-</option></select></div>
      <div class="form-group"><label>분야</label><select id="am-field"><option value="">-</option></select></div>
    </div>
    <div class="modal-actions">
      <button class="btn btn-ghost" onclick="closeModal('author-modal')">취소</button>
      <button class="btn btn-primary" id="am-save" onclick="saveAuthor()">저장</button>
    </div>
  </div>
</div>

<!-- ========== DELETE CONFIRM MODAL ========== -->
<div id="delete-modal" class="modal-overlay">
  <div class="modal" style="width:420px">
    <h3>삭제 확인</h3>
    <div id="del-content"></div>
    <div class="modal-actions">
      <button class="btn btn-ghost" onclick="closeModal('delete-modal')">취소</button>
      <button class="btn btn-danger" id="del-confirm">삭제</button>
    </div>
  </div>
</div>

<script>
// ===== Config =====
const TOKEN_KEY = 'admin_token';
let token = localStorage.getItem(TOKEN_KEY) || '';

// ===== State =====
let qPage = 1, qTotal = 0, qLimit = 20;
let aPage = 1, aTotal = 0, aLimit = 20;
let mastersLoaded = false;
let masterKeywords = [], masterSituations = [], masterProfessions = [], masterFields = [];
let authorCache = [];
let selectedIds = new Set();

// ===== Auth =====
function checkAuth() {
  if (!token) { showAuth(); return; }
  document.getElementById('auth-screen').style.display = 'none';
  document.getElementById('main-screen').style.display = 'block';
  init();
}
function showAuth() {
  document.getElementById('auth-screen').style.display = 'flex';
  document.getElementById('main-screen').style.display = 'none';
}
function doLogin() {
  const t = document.getElementById('token-input').value.trim();
  if (!t) return;
  token = t;
  localStorage.setItem(TOKEN_KEY, t);
  document.getElementById('auth-error').style.display = 'none';
  checkAuth();
}
function doLogout() {
  token = '';
  localStorage.removeItem(TOKEN_KEY);
  showAuth();
}

// ===== API Helper =====
async function api(path, opts = {}) {
  const res = await fetch(path, {
    ...opts,
    headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', ...(opts.headers || {}) },
    body: opts.body ? JSON.stringify(opts.body) : undefined
  });
  if (res.status === 401) { doLogout(); throw new Error('unauthorized'); }
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'API error');
  return data;
}

// ===== Toast =====
function toast(msg, type = 'success') {
  const el = document.createElement('div');
  el.className = 'toast toast-' + type;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

// ===== Init =====
async function init() {
  loadMasters();
  loadQuotes(1);
  // Enter key on search
  document.getElementById('f-search').addEventListener('keydown', e => { if (e.key === 'Enter') loadQuotes(1); });
  document.getElementById('a-search').addEventListener('keydown', e => { if (e.key === 'Enter') loadAuthors(1); });
}

// ===== Tabs =====
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
    if (btn.dataset.tab === 'authors' && aTotal === 0) loadAuthors(1);
  });
});

// ===== Masters =====
async function loadMasters() {
  if (mastersLoaded) return;
  try {
    const [kw, sit, prof, fld] = await Promise.all([
      api('/admin/api/masters/keywords'),
      api('/admin/api/masters/situations'),
      api('/admin/api/masters/professions'),
      api('/admin/api/masters/fields'),
    ]);
    masterKeywords = kw; masterSituations = sit; masterProfessions = prof; masterFields = fld;
    mastersLoaded = true;
    // Populate keyword group filter
    const groups = [...new Set(kw.map(k => k.group_name).filter(Boolean))].sort();
    const sel = document.getElementById('f-keyword-group');
    groups.forEach(g => { const o = document.createElement('option'); o.value = g; o.textContent = g; sel.appendChild(o); });
    // Populate profession/field selects
    populateSelect('am-profession', prof, 'name');
    populateSelect('am-field', fld, 'name');
  } catch (e) { console.error('Masters load failed', e); }
}
function populateSelect(id, items, labelKey) {
  const sel = document.getElementById(id);
  // keep first option
  items.forEach(item => { const o = document.createElement('option'); o.value = item.id; o.textContent = item.group_name ? item.name + ' (' + item.group_name + ')' : item.name; sel.appendChild(o); });
}

// ===== Quotes List =====
async function loadQuotes(page) {
  if (page < 1) return;
  qPage = page;
  selectedIds.clear();
  updateBatchBar();
  document.getElementById('chk-all').checked = false;
  const params = new URLSearchParams({ page, limit: qLimit });
  const status = document.getElementById('f-status').value;
  const kwGroup = document.getElementById('f-keyword-group').value;
  const rel = document.getElementById('f-reliability').value;
  const search = document.getElementById('f-search').value.trim();
  if (status) params.set('status', status);
  if (kwGroup) params.set('keyword_group', kwGroup);
  if (rel) params.set('reliability', rel);
  if (search) params.set('search', search);

  try {
    const data = await api('/admin/api/quotes?' + params);
    qTotal = data.total;
    renderQuotes(data.quotes);
    const totalPages = Math.ceil(qTotal / qLimit) || 1;
    document.getElementById('q-page-info').textContent = qPage + ' / ' + totalPages + ' (' + qTotal + '건)';
    document.getElementById('q-prev').disabled = qPage <= 1;
    document.getElementById('q-next').disabled = qPage >= totalPages;
  } catch (e) { console.error(e); }
}

function renderQuotes(quotes) {
  const tbody = document.getElementById('quotes-body');
  if (!quotes.length) { tbody.innerHTML = '<tr><td colspan="8" class="loading">데이터가 없습니다.</td></tr>'; return; }
  tbody.innerHTML = quotes.map(q => {
    const text = q.text.length > 50 ? q.text.slice(0, 50) + '...' : q.text;
    const kws = (q.keywords || []).slice(0, 4).map(k => '<span class="badge-tag">' + esc(k) + '</span>').join('');
    const extra = (q.keywords || []).length > 4 ? '<span class="badge-tag">+' + ((q.keywords.length) - 4) + '</span>' : '';
    const date = q.created_at ? q.created_at.slice(0, 10) : '';
    const statuses = ['draft','reviewed','published','rejected'];
    const statusBtns = statuses.map(s => {
      const cls = s === 'draft' ? 'btn-ghost' : s === 'reviewed' ? 'btn-warning' : s === 'published' ? 'btn-success' : 'btn-danger';
      const label = s.charAt(0).toUpperCase();
      return '<button class="btn btn-sm ' + cls + '" ' + (q.status === s ? 'disabled' : '') + ' onclick="quickStatus(\\'' + q.id + '\\',\\'' + s + '\\')" title="' + s + '">' + label + '</button>';
    }).join('');
    return '<tr>' +
      '<td><input type="checkbox" class="q-chk" value="' + q.id + '" onchange="onCheckChange()"></td>' +
      '<td><span class="text-truncate" title="' + esc(q.text) + '">' + esc(text) + '</span></td>' +
      '<td>' + esc(q.author_name || '') + '</td>' +
      '<td><span class="badge badge-' + q.status + '">' + q.status + '</span></td>' +
      '<td><span class="badge-reliability">' + (q.source_reliability || '-') + '</span></td>' +
      '<td>' + kws + extra + '</td>' +
      '<td style="white-space:nowrap;color:#64748b">' + date + '</td>' +
      '<td style="white-space:nowrap"><div class="status-btns">' + statusBtns + '</div><button class="btn btn-ghost btn-sm" style="margin-left:4px" onclick="editQuote(\\'' + q.id + '\\')" title="편집">&#9998;</button><button class="btn btn-danger btn-sm" style="margin-left:2px" onclick="deleteQuote(\\'' + q.id + '\\')" title="삭제">&#10005;</button></td>' +
      '</tr>';
  }).join('');
}
function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

// ===== Checkbox / Batch =====
function toggleAll(el) {
  document.querySelectorAll('.q-chk').forEach(c => { c.checked = el.checked; });
  onCheckChange();
}
function onCheckChange() {
  selectedIds.clear();
  document.querySelectorAll('.q-chk:checked').forEach(c => selectedIds.add(c.value));
  updateBatchBar();
}
function updateBatchBar() {
  const bar = document.getElementById('batch-bar');
  const n = selectedIds.size;
  bar.style.display = n > 0 ? 'flex' : 'none';
  document.getElementById('sel-count').textContent = n;
}
async function batchStatus() {
  const status = document.getElementById('batch-status-sel').value;
  if (!status) { toast('상태를 선택하세요', 'error'); return; }
  if (!confirm(selectedIds.size + '개 명언을 ' + status + '로 변경하시겠습니까?')) return;
  try {
    const data = await api('/admin/api/quotes/batch-status', { method: 'POST', body: { ids: [...selectedIds], status } });
    toast(data.updated + '개 변경 완료');
    loadQuotes(qPage);
  } catch (e) { toast(e.message, 'error'); }
}
async function batchDelete() {
  if (!confirm(selectedIds.size + '개 명언을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) return;
  try {
    const data = await api('/admin/api/quotes/batch-delete', { method: 'POST', body: { ids: [...selectedIds] } });
    toast(data.deleted + '개 삭제 완료');
    loadQuotes(qPage);
  } catch (e) { toast(e.message, 'error'); }
}

// ===== Quick Status =====
async function quickStatus(id, status) {
  try {
    await api('/admin/api/quotes/' + id, { method: 'PATCH', body: { status } });
    toast('상태 변경: ' + status);
    loadQuotes(qPage);
  } catch (e) { toast(e.message, 'error'); }
}

// ===== Quote Modal =====
let editingQuote = null;
function openQuoteModal(quote) {
  editingQuote = quote || null;
  document.getElementById('qm-title').textContent = quote ? '명언 편집' : '명언 추가';
  document.getElementById('qm-id').value = quote ? quote.id : '';
  document.getElementById('qm-text').value = quote ? quote.text : '';
  document.getElementById('qm-original').value = quote ? (quote.text_original || '') : '';
  document.getElementById('qm-lang').value = quote ? (quote.original_language || '') : '';
  document.getElementById('qm-author-search').value = quote ? (quote.author_name || '') : '';
  document.getElementById('qm-author-id').value = quote ? (quote.author_id || '') : '';
  document.getElementById('qm-source').value = quote ? (quote.source || '') : '';
  document.getElementById('qm-year').value = quote ? (quote.year || '') : '';
  document.getElementById('qm-status').value = quote ? quote.status : 'draft';
  document.getElementById('qm-reliability').value = quote ? (quote.source_reliability || 'unknown') : 'unknown';

  // Render keyword checkboxes grouped
  renderCheckboxGroup('qm-keywords', masterKeywords, quote ? (quote.keyword_ids || []) : []);
  renderCheckboxGroup('qm-situations', masterSituations, quote ? (quote.situation_ids || []) : []);

  document.getElementById('quote-modal').classList.add('active');
}
function renderCheckboxGroup(containerId, items, selectedIds) {
  const el = document.getElementById(containerId);
  const grouped = {};
  items.forEach(item => {
    const g = item.group_name || '미분류';
    if (!grouped[g]) grouped[g] = [];
    grouped[g].push(item);
  });
  let html = '';
  Object.keys(grouped).sort().forEach(g => {
    html += '<div class="checkbox-group-title">' + esc(g) + '</div>';
    grouped[g].forEach(item => {
      const checked = selectedIds.includes(item.id) ? 'checked' : '';
      html += '<label><input type="checkbox" value="' + item.id + '" ' + checked + '>' + esc(item.name) + '</label>';
    });
  });
  el.innerHTML = html;
}

// Author search dropdown
let authorSearchTimer;
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('qm-author-search');
  const dropdown = document.getElementById('qm-author-dropdown');
  if (!input) return;
  input.addEventListener('input', () => {
    clearTimeout(authorSearchTimer);
    authorSearchTimer = setTimeout(async () => {
      const q = input.value.trim();
      if (q.length < 1) { dropdown.classList.remove('open'); return; }
      try {
        const data = await api('/admin/api/authors?search=' + encodeURIComponent(q) + '&limit=10');
        authorCache = data.authors;
        if (!data.authors.length) { dropdown.classList.remove('open'); return; }
        dropdown.innerHTML = data.authors.map(a =>
          '<div class="author-dropdown-item" data-id="' + a.id + '" data-name="' + esc(a.name) + '">' +
          esc(a.name) + ' <span class="sub">' + (a.nationality || '') + (a.birth_year ? ' ' + a.birth_year : '') + '</span></div>'
        ).join('');
        dropdown.classList.add('open');
      } catch(e) {}
    }, 300);
  });
  dropdown.addEventListener('click', e => {
    const item = e.target.closest('.author-dropdown-item');
    if (!item) return;
    input.value = item.dataset.name;
    document.getElementById('qm-author-id').value = item.dataset.id;
    dropdown.classList.remove('open');
  });
  document.addEventListener('click', e => {
    if (!e.target.closest('.author-search-wrap')) dropdown.classList.remove('open');
  });
});

async function saveQuote() {
  const text = document.getElementById('qm-text').value.trim();
  const authorId = document.getElementById('qm-author-id').value;
  if (!text) { toast('텍스트를 입력하세요', 'error'); return; }
  if (!authorId) { toast('저자를 선택하세요', 'error'); return; }

  const kwIds = [...document.querySelectorAll('#qm-keywords input:checked')].map(c => parseInt(c.value));
  const sitIds = [...document.querySelectorAll('#qm-situations input:checked')].map(c => parseInt(c.value));

  const body = {
    text,
    text_original: document.getElementById('qm-original').value.trim() || null,
    original_language: document.getElementById('qm-lang').value || null,
    author_id: authorId,
    source: document.getElementById('qm-source').value.trim() || null,
    year: document.getElementById('qm-year').value ? parseInt(document.getElementById('qm-year').value) : null,
    status: document.getElementById('qm-status').value,
    source_reliability: document.getElementById('qm-reliability').value,
    keyword_ids: kwIds,
    situation_ids: sitIds,
  };

  const id = document.getElementById('qm-id').value;
  try {
    if (id) {
      await api('/admin/api/quotes/' + id, { method: 'PATCH', body });
      toast('명언 수정 완료');
    } else {
      await api('/admin/api/quotes', { method: 'POST', body });
      toast('명언 추가 완료');
    }
    closeModal('quote-modal');
    loadQuotes(qPage);
  } catch (e) { toast(e.message, 'error'); }
}

async function editQuote(id) {
  try {
    // Fetch fresh data by loading current page data
    const params = new URLSearchParams({ page: 1, limit: 1, search: id });
    // We need full data; let's just find in current data or refetch
    const data = await api('/admin/api/quotes?page=1&limit=100&search=');
    const q = data.quotes.find(q => q.id === id);
    if (q) { openQuoteModal(q); return; }
    // Fallback: search by full list on current page
    toast('명언을 찾을 수 없습니다', 'error');
  } catch(e) {
    // Simpler approach: reconstruct from table
    toast('편집 데이터를 불러올 수 없습니다', 'error');
  }
}

function deleteQuote(id) {
  document.getElementById('del-content').innerHTML = '<p>이 명언을 삭제하시겠습니까?</p><p style="color:#64748b;font-size:12px">관련 사용자 인터랙션도 함께 삭제됩니다.</p>';
  document.getElementById('del-confirm').onclick = async () => {
    try {
      await api('/admin/api/quotes/' + id, { method: 'DELETE' });
      toast('명언 삭제 완료');
      closeModal('delete-modal');
      loadQuotes(qPage);
    } catch (e) { toast(e.message, 'error'); }
  };
  document.getElementById('delete-modal').classList.add('active');
}

// ===== Authors List =====
async function loadAuthors(page) {
  if (page < 1) return;
  aPage = page;
  const search = document.getElementById('a-search').value.trim();
  const params = new URLSearchParams({ page, limit: aLimit });
  if (search) params.set('search', search);
  try {
    const data = await api('/admin/api/authors?' + params);
    aTotal = data.total;
    renderAuthors(data.authors);
    const totalPages = Math.ceil(aTotal / aLimit) || 1;
    document.getElementById('a-page-info').textContent = aPage + ' / ' + totalPages + ' (' + aTotal + '건)';
    document.getElementById('a-prev').disabled = aPage <= 1;
    document.getElementById('a-next').disabled = aPage >= totalPages;
  } catch(e) { console.error(e); }
}

function renderAuthors(authors) {
  const tbody = document.getElementById('authors-body');
  if (!authors.length) { tbody.innerHTML = '<tr><td colspan="7" class="loading">데이터가 없습니다.</td></tr>'; return; }
  tbody.innerHTML = authors.map(a =>
    '<tr>' +
    '<td>' + esc(a.name) + '</td>' +
    '<td>' + esc(a.nationality || '-') + '</td>' +
    '<td>' + (a.birth_year || '-') + '</td>' +
    '<td>' + esc(a.profession || '-') + '</td>' +
    '<td>' + esc(a.field || '-') + '</td>' +
    '<td>' + (a.quote_count || 0) + '</td>' +
    '<td style="white-space:nowrap">' +
      '<button class="btn btn-ghost btn-sm" onclick="editAuthor(\\'' + a.id + '\\')" title="편집">&#9998;</button>' +
      '<button class="btn btn-danger btn-sm" style="margin-left:4px" onclick="deleteAuthor(\\'' + a.id + '\\',\\'' + esc(a.name).replace(/'/g,"\\\\'") + '\\')" title="삭제">&#10005;</button>' +
    '</td></tr>'
  ).join('');
}

// ===== Author Modal =====
function openAuthorModal(author) {
  document.getElementById('am-title').textContent = author ? '저자 편집' : '저자 추가';
  document.getElementById('am-id').value = author ? author.id : '';
  document.getElementById('am-name').value = author ? author.name : '';
  document.getElementById('am-nationality').value = author ? (author.nationality || '') : '';
  document.getElementById('am-birth-year').value = author ? (author.birth_year || '') : '';
  document.getElementById('am-profession').value = author ? (author.profession_id || '') : '';
  document.getElementById('am-field').value = author ? (author.field_id || '') : '';
  document.getElementById('author-modal').classList.add('active');
}

async function editAuthor(id) {
  try {
    const data = await api('/admin/api/authors?limit=100');
    const a = data.authors.find(a => a.id === id);
    if (a) { openAuthorModal(a); return; }
    toast('저자를 찾을 수 없습니다', 'error');
  } catch(e) { toast('편집 데이터를 불러올 수 없습니다', 'error'); }
}

async function saveAuthor() {
  const name = document.getElementById('am-name').value.trim();
  const nationality = document.getElementById('am-nationality').value.trim().toUpperCase();
  const birthYear = document.getElementById('am-birth-year').value;
  if (!name || !nationality || !birthYear) { toast('이름, 국적, 출생연도는 필수입니다', 'error'); return; }
  if (nationality.length !== 2) { toast('국적은 ISO 2자리 코드여야 합니다 (예: KR, US)', 'error'); return; }

  const body = {
    name,
    nationality,
    birth_year: parseInt(birthYear),
    profession_id: document.getElementById('am-profession').value ? parseInt(document.getElementById('am-profession').value) : null,
    field_id: document.getElementById('am-field').value ? parseInt(document.getElementById('am-field').value) : null,
  };

  const id = document.getElementById('am-id').value;
  try {
    if (id) {
      await api('/admin/api/authors/' + id, { method: 'PATCH', body });
      toast('저자 수정 완료');
    } else {
      await api('/admin/api/authors', { method: 'POST', body });
      toast('저자 추가 완료');
    }
    closeModal('author-modal');
    loadAuthors(aPage);
  } catch (e) { toast(e.message, 'error'); }
}

async function deleteAuthor(id, name) {
  try {
    const preview = await api('/admin/api/authors/' + id + '/preview-delete');
    document.getElementById('del-content').innerHTML =
      '<div class="delete-preview">' +
      '<div class="warn">"' + esc(name) + '" 저자를 삭제합니다</div>' +
      '<p>연결된 명언: <strong>' + preview.quote_count + '</strong>개</p>' +
      '<p>저자 관계: <strong>' + preview.relation_count + '</strong>개</p>' +
      '<p>사용자 인터랙션: <strong>' + preview.interaction_count + '</strong>개</p>' +
      '</div>' +
      '<p style="font-size:13px;color:#f87171;margin-top:8px">위 데이터가 모두 함께 삭제됩니다. 되돌릴 수 없습니다.</p>';
  } catch(e) {
    document.getElementById('del-content').innerHTML = '<p>"' + esc(name) + '" 저자를 삭제하시겠습니까?</p>';
  }
  document.getElementById('del-confirm').onclick = async () => {
    try {
      const data = await api('/admin/api/authors/' + id, { method: 'DELETE' });
      toast('저자 삭제 완료 (명언 ' + data.deleted_quotes + '개 함께 삭제)');
      closeModal('delete-modal');
      loadAuthors(aPage);
    } catch (e) { toast(e.message, 'error'); }
  };
  document.getElementById('delete-modal').classList.add('active');
}

// ===== Modal Helpers =====
function closeModal(id) { document.getElementById(id).classList.remove('active'); }
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', e => { if (e.target === overlay) closeModal(overlay.id); });
});

// ===== Boot =====
checkAuth();
</script>
</body>
</html>"""


# ===========================================================================
# Dashboard HTML
# ===========================================================================

@app.route("/")
def index():
    return """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>명언 수집기 대시보드</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;padding:24px}
h1{font-size:24px;margin-bottom:24px;color:#f8fafc}
h2{font-size:16px;margin-bottom:12px;color:#94a3b8;font-weight:500}
.stats{display:flex;gap:16px;margin-bottom:24px;flex-wrap:wrap}
.stat-card{background:#1e293b;border-radius:12px;padding:20px;flex:1;min-width:120px}
.stat-card .number{font-size:36px;font-weight:700;color:#38bdf8}
.stat-card .label{font-size:14px;color:#94a3b8;margin-top:4px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px}
.card{background:#1e293b;border-radius:12px;padding:20px;max-height:500px;overflow-y:auto}
.bar{display:flex;align-items:center;margin-bottom:6px;font-size:13px}
.bar-label{width:120px;text-align:right;margin-right:10px;color:#94a3b8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex-shrink:0}
.bar-fill{height:20px;border-radius:4px;transition:width 0.5s;min-width:2px}
.bar-count{margin-left:8px;color:#64748b;font-size:12px;white-space:nowrap}
.recent{margin-top:8px}
.recent-item{padding:12px 0;border-bottom:1px solid #334155}
.recent-item:last-child{border-bottom:none}
.recent-text{font-size:14px;line-height:1.5}
.recent-author{font-size:12px;color:#64748b;margin-top:4px}
.tag{display:inline-block;background:#334155;border-radius:4px;padding:2px 6px;font-size:11px;margin:2px;color:#94a3b8}
.gap-section{margin-top:8px}
.gap-item{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #334155;font-size:13px}
.gap-item .area{color:#94a3b8}
.gap-item .status{font-weight:600}
.status-low{color:#f87171}
.status-mid{color:#fbbf24}
.status-ok{color:#4ade80}
.section-title{font-size:18px;margin:32px 0 16px;color:#f8fafc;border-bottom:1px solid #334155;padding-bottom:8px}
</style>
</head>
<body>
<h1>명언 수집기 대시보드</h1>

<div class="stats">
  <div class="stat-card"><div class="number" id="s-quotes">-</div><div class="label">총 명언</div></div>
  <div class="stat-card"><div class="number" id="s-authors">-</div><div class="label">총 저자</div></div>
  <div class="stat-card"><div class="number" id="s-relations">-</div><div class="label">저자 관계</div></div>
  <div class="stat-card"><div class="number" id="s-keywords">-</div><div class="label">키워드</div></div>
  <div class="stat-card"><div class="number" id="s-situations">-</div><div class="label">상황</div></div>
  <div class="stat-card"><div class="number" id="s-fields">-</div><div class="label">분야</div></div>
  <div class="stat-card"><div class="number" id="s-verified">-</div><div class="label">검증 완료</div></div>
</div>

<div class="grid">
  <div class="card"><h2>분야별 분포</h2><div id="by-field"></div></div>
  <div class="card"><h2>국가별 분포</h2><div id="by-nationality"></div></div>
  <div class="card"><h2>직업 그룹별</h2><div id="by-profession-group"></div></div>
  <div class="card"><h2>직업별 (개별)</h2><div id="by-profession"></div></div>
</div>

<div class="section-title">수집 갭 분석</div>
<div class="grid">
  <div class="card" style="grid-column:span 2"><div id="gap-analysis" class="gap-section"></div></div>
</div>

<div class="section-title">키워드</div>
<div class="grid">
  <div class="card"><h2>키워드 그룹별</h2><div id="by-keyword-group"></div></div>
  <div class="card"><h2>키워드 TOP 20 (개별)</h2><div id="by-keyword"></div></div>
</div>

<div class="section-title">상황</div>
<div class="grid">
  <div class="card"><h2>상황 그룹별</h2><div id="by-situation-group"></div></div>
  <div class="card"><h2>상황 TOP 15 (개별)</h2><div id="by-situation"></div></div>
</div>

<div class="section-title">트렌드 분석</div>
<div id="trends-time" style="font-size:12px;color:#64748b;margin-bottom:12px"></div>
<div class="grid">
  <div class="card"><h2>글로벌 트렌드</h2><div id="trends-global"></div></div>
  <div class="card"><h2>한국 트렌드</h2><div id="trends-korea"></div></div>
</div>

<div class="section-title">수집 이력</div>
<div class="grid">
  <div class="card" style="grid-column:span 2"><div id="collection-history"></div></div>
</div>

<div class="section-title">최근 수집</div>
<div class="grid">
  <div class="card" style="grid-column:span 2"><div id="recent" class="recent"></div></div>
</div>

<script>
const C={field:'#38bdf8',nat:'#818cf8',kw:'#a78bfa',kwg:'#f472b6',sit:'#fb923c',sitg:'#4ade80'};
const TARGET={
  field:{'철학':30,'문학':25,'과학':20,'정치':15,'역사':15,'예술':15,'종교':10,'경영':10,'스포츠':10,'심리학':10,'기술':10,'문화':10},
  nationality:{'KR':20,'US':20,'GB':15,'CN':15,'DE':10,'FR':10,'GR':10,'JP':10,'IN':10,'IT':10}
};

async function load(){
  const[stats,vstats,field,nat,prof,profg,kw,kwg,sit,sitg,history,recent]=await Promise.all([
    fetch('/api/stats').then(r=>r.json()),
    fetch('/api/verification-stats').then(r=>r.json()),
    fetch('/api/by-field').then(r=>r.json()),
    fetch('/api/by-nationality').then(r=>r.json()),
    fetch('/api/by-profession').then(r=>r.json()),
    fetch('/api/by-profession-group').then(r=>r.json()),
    fetch('/api/by-keyword').then(r=>r.json()),
    fetch('/api/by-keyword-group').then(r=>r.json()),
    fetch('/api/by-situation').then(r=>r.json()),
    fetch('/api/by-situation-group').then(r=>r.json()),
    fetch('/api/collection-history').then(r=>r.json()),
    fetch('/api/recent').then(r=>r.json()),
  ]);
  document.getElementById('s-quotes').textContent=stats.quotes;
  document.getElementById('s-authors').textContent=stats.authors;
  document.getElementById('s-relations').textContent=stats.author_relations;
  document.getElementById('s-keywords').textContent=stats.keywords;
  document.getElementById('s-situations').textContent=stats.situations;
  document.getElementById('s-fields').textContent=stats.fields;
  document.getElementById('s-verified').textContent=vstats.verified+'/'+stats.quotes;

  bars('by-field',field,'field',C.field);
  bars('by-nationality',nat,'nationality',C.nat);
  bars('by-profession',prof,'profession','#2dd4bf');
  bars('by-profession-group',profg,'group_name','#e879f9');
  bars('by-keyword',kw.slice(0,20),'keyword',C.kw);
  bars('by-keyword-group',kwg,'group_name',C.kwg);
  bars('by-situation',sit.slice(0,15),'situation',C.sit);
  bars('by-situation-group',sitg,'group_name',C.sitg);
  renderRecent(recent);
  renderGap(field,nat);
  renderHistory(history);
}

function bars(id,data,key,color){
  const el=document.getElementById(id);
  const max=data.length?Math.max(...data.map(d=>d.count)):1;
  el.innerHTML=data.map(d=>{
    const name=d[key]||'미분류';
    const pct=(d.count/max*100);
    const grp=d.group_name&&key!=='group_name'?' <span style="color:#475569;font-size:11px">('+d.group_name+')</span>':'';
    return '<div class="bar"><span class="bar-label" title="'+name+'">'+name+'</span><div class="bar-fill" style="width:'+pct+'%;background:'+color+'"></div><span class="bar-count">'+d.count+grp+'</span></div>';
  }).join('');
}

function renderRecent(data){
  document.getElementById('recent').innerHTML=data.map(d=>{
    const kws=(typeof d.keywords==='string'?JSON.parse(d.keywords):d.keywords)||[];
    return '<div class="recent-item"><div class="recent-text">\u201c'+d.text+'\u201d</div><div class="recent-author">\u2014 '+d.author+'</div><div>'+kws.map(k=>'<span class="tag">'+k+'</span>').join('')+'</div></div>';
  }).join('');
}

function renderGap(fieldData,natData){
  const el=document.getElementById('gap-analysis');
  let html='<div style="font-size:13px;color:#64748b;margin-bottom:12px">목표 대비 부족한 영역 (빨간색 우선 수집)</div>';
  const fMap={};fieldData.forEach(d=>fMap[d.field]=d.count);
  const nMap={};natData.forEach(d=>nMap[d.nationality]=d.count);
  const gaps=[];
  for(const[f,t]of Object.entries(TARGET.field)){const c=fMap[f]||0;gaps.push({area:f+' (분야)',current:c,target:t,pct:Math.round(c/t*100)})}
  for(const[n,t]of Object.entries(TARGET.nationality)){const c=nMap[n]||0;gaps.push({area:n+' (국가)',current:c,target:t,pct:Math.round(c/t*100)})}
  gaps.sort((a,b)=>a.pct-b.pct);
  html+=gaps.map(g=>{
    const cls=g.pct<30?'status-low':g.pct<70?'status-mid':'status-ok';
    return '<div class="gap-item"><span class="area">'+g.area+'</span><span class="status '+cls+'">'+g.current+'/'+g.target+' ('+g.pct+'%)</span></div>';
  }).join('');
  el.innerHTML=html;
}

async function loadTrends(){
  try{
    const res=await fetch('/api/trends');
    if(!res.ok){document.getElementById('trends-global').innerHTML='<span style="color:#64748b">데이터 없음</span>';document.getElementById('trends-korea').innerHTML='<span style="color:#64748b">데이터 없음</span>';return}
    const data=await res.json();
    if(data.fetched_at){document.getElementById('trends-time').textContent='마지막 조회: '+data.fetched_at}
    renderTrendBars('trends-global',data.global||{},'#38bdf8');
    renderTrendBars('trends-korea',data.korea||{},'#f472b6');
  }catch(e){console.error('트렌드 로드 실패',e)}
}

function renderTrendBars(id,obj,color){
  const el=document.getElementById(id);
  const entries=Object.entries(obj).sort((a,b)=>b[1]-a[1]);
  if(!entries.length){el.innerHTML='<span style="color:#64748b">데이터 없음</span>';return}
  const max=Math.max(...entries.map(e=>e[1]),1);
  el.innerHTML=entries.map(([k,v])=>{
    const pct=(v/max*100);
    return '<div class="bar"><span class="bar-label" title="'+k+'">'+k+'</span><div class="bar-fill" style="width:'+pct+'%;background:'+color+'"></div><span class="bar-count">'+v+'</span></div>';
  }).join('');
}

function renderHistory(data){
  const el=document.getElementById('collection-history');
  if(!data.length){el.innerHTML='<span style="color:#64748b">수집 이력이 없습니다.</span>';return}
  let html='<table style="width:100%;font-size:13px;border-collapse:collapse"><tr style="color:#64748b;border-bottom:1px solid #334155"><th style="text-align:left;padding:8px">일시</th><th>카테고리</th><th>요청</th><th>저장</th><th>중복</th><th>오류</th></tr>';
  html+=data.map(d=>'<tr style="border-bottom:1px solid #1e293b"><td style="padding:6px;color:#94a3b8">'+d.created_at.slice(0,16)+'</td><td style="text-align:center">'+d.category+'</td><td style="text-align:center">'+d.requested_count+'</td><td style="text-align:center;color:#4ade80">'+d.saved_count+'</td><td style="text-align:center;color:#fbbf24">'+d.duplicate_count+'</td><td style="text-align:center;color:#f87171">'+d.error_count+'</td></tr>').join('');
  html+='</table>';
  el.innerHTML=html;
}

load();
loadTrends();
</script>
</body>
</html>"""


if __name__ == "__main__":
    print("대시보드: http://localhost:5050")
    app.run(port=5050, debug=True)
