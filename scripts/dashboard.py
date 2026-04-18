"""
명언 데이터 현황 대시보드.

사용법:
    python scripts/dashboard.py
    # 브라우저에서 http://localhost:5050 접속
"""

import glob
import json
import os

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
    """개인화 파라미터에서 WHERE/ORDER BY 조건과 params를 빌드."""
    sit_groups = args.get("situations", "")
    kw_groups = args.get("keywords", "")
    exclude_ids = args.get("exclude", "")
    sit_list = [s.strip() for s in sit_groups.split(",") if s.strip()]
    kw_list = [k.strip() for k in kw_groups.split(",") if k.strip()]
    exclude_list = [e.strip() for e in exclude_ids.split(",") if e.strip()]

    params = []
    bonus_clauses = []
    where_clauses = []

    if sit_list:
        bonus_clauses.append("""
            CASE WHEN EXISTS (
                SELECT 1 FROM situations s
                WHERE s.id = ANY(q.situation_ids) AND s.group_name = ANY(%s)
            ) THEN 3 ELSE 0 END
        """)
        params.append(sit_list)

    if kw_list:
        bonus_clauses.append("""
            CASE WHEN EXISTS (
                SELECT 1 FROM keywords k
                WHERE k.id = ANY(q.keyword_ids) AND k.group_name = ANY(%s)
            ) THEN 2 ELSE 0 END
        """)
        params.append(kw_list)

    if exclude_list:
        where_clauses.append("q.id != ALL(%s)")
        params.append(exclude_list)

    bonus_sql = " + ".join(bonus_clauses) if bonus_clauses else "0"
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    return params, bonus_sql, where_sql


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
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
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
