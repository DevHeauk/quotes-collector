"""저자별 명언 데이터 분류 시각화.

DB의 quotes/authors를 조회해 저자·국적·직업 기준 분포를
HTML 리포트(data/reports/authors.html)로 생성한다.

실행:
    python scripts/visualize_authors.py
    open data/reports/authors.html
"""
import json
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

REPORT_PATH = "data/reports/authors.html"


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


def collect():
    totals = query(
        "SELECT (SELECT count(*) FROM authors) AS authors, "
        "(SELECT count(*) FROM quotes) AS quotes"
    )[0]

    # 전체 저자 (명언 수 내림차순). 차트는 상위 30명만, 표는 전체 사용.
    all_authors = query(
        """
        SELECT a.id AS author_id, a.name, a.nationality, a.birth_year,
               COALESCE(p.name, '-') AS profession,
               COALESCE(f.name, '-') AS field,
               count(q.id) AS cnt
        FROM quotes q
        JOIN authors a ON q.author_id = a.id
        LEFT JOIN professions p ON a.profession_id = p.id
        LEFT JOIN fields f ON a.field_id = f.id
        GROUP BY a.id, a.name, a.nationality, a.birth_year, p.name, f.name
        ORDER BY cnt DESC, a.name
        """
    )
    top_authors = all_authors[:30]

    # 명언 상세 (저자별 카드 리스트용). 키워드/상황 ID를 이름으로 해석.
    quotes = query(
        """
        SELECT q.id, q.author_id, q.text, q.text_original, q.original_language,
               q.source, q.year, q.status, q.source_reliability, q.need_types,
               q.impact_score,
               q.created_at::date::text AS created_at,
               cl.category AS collection_category,
               (SELECT array_agg(k.name) FROM keywords k
                  WHERE k.id = ANY(q.keyword_ids)) AS keywords,
               (SELECT array_agg(s.name) FROM situations s
                  WHERE s.id = ANY(q.situation_ids)) AS situations,
               -- 외부 인기 지표 (참고 데이터): reddit/goodreads는 원문 매칭, naver는 quote_id
               (SELECT r.upvotes FROM reddit_popularity r
                  WHERE r.quote_text = q.text_original
                  ORDER BY r.upvotes DESC NULLS LAST LIMIT 1) AS reddit_upvotes,
               (SELECT r.subreddit FROM reddit_popularity r
                  WHERE r.quote_text = q.text_original
                  ORDER BY r.upvotes DESC NULLS LAST LIMIT 1) AS reddit_subreddit,
               (SELECT max(g.likes) FROM goodreads_popularity g
                  WHERE g.quote_text = q.text_original) AS goodreads_likes,
               (SELECT max(n.result_count) FROM naver_popularity n
                  WHERE n.quote_id = q.id) AS naver_results
        FROM quotes q
        LEFT JOIN collection_logs cl ON q.collection_log_id = cl.id
        ORDER BY q.created_at DESC
        """
    )

    # 저자당 명언 수 → 저자 수 (롱테일 분포)
    per_author = query(
        """
        SELECT cnt AS quotes_per_author, count(*) AS num_authors
        FROM (
            SELECT count(q.id) cnt
            FROM authors a JOIN quotes q ON q.author_id = a.id
            GROUP BY a.id
        ) s
        GROUP BY cnt ORDER BY cnt
        """
    )

    by_nationality = query(
        """
        SELECT a.nationality, count(q.id) cnt
        FROM quotes q JOIN authors a ON q.author_id = a.id
        GROUP BY a.nationality ORDER BY cnt DESC
        """
    )

    by_profession = query(
        """
        SELECT COALESCE(p.group_name, p.name, '미분류') AS grp, count(q.id) cnt
        FROM quotes q
        JOIN authors a ON q.author_id = a.id
        LEFT JOIN professions p ON a.profession_id = p.id
        GROUP BY grp ORDER BY cnt DESC
        """
    )

    # 태그관리(조회 전용): 키워드/상황 마스터 + 사용량(명언 수)
    keyword_usage = query(
        """
        SELECT k.name, COALESCE(k.group_name, '기타') AS grp,
               (SELECT count(*) FROM quotes q WHERE k.id = ANY(q.keyword_ids)) AS cnt
        FROM keywords k
        ORDER BY grp, cnt DESC, k.name
        """
    )
    situation_usage = query(
        """
        SELECT s.name, COALESCE(s.group_name, '기타') AS grp,
               (SELECT count(*) FROM quotes q WHERE s.id = ANY(q.situation_ids)) AS cnt
        FROM situations s
        ORDER BY grp, cnt DESC, s.name
        """
    )

    return {
        "totals": totals,
        "top_authors": top_authors,
        "all_authors": all_authors,
        "quotes": quotes,
        "per_author": per_author,
        "by_nationality": by_nationality,
        "by_profession": by_profession,
        "keyword_usage": keyword_usage,
        "situation_usage": situation_usage,
    }


HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>저자별 명언 분포</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  :root {{ --bg:#0f1115; --card:#1a1d24; --fg:#e6e8ec; --muted:#8a909c; --accent:#5b9dff; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg);
         font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif; padding:32px; }}
  h1 {{ font-size:22px; margin:0 0 4px; }}
  .sub {{ color:var(--muted); margin-bottom:24px; font-size:13px; }}
  .kpis {{ display:flex; gap:16px; margin-bottom:28px; flex-wrap:wrap; }}
  .kpi {{ background:var(--card); border-radius:12px; padding:16px 20px; min-width:140px; }}
  .kpi .v {{ font-size:28px; font-weight:700; }}
  .kpi .l {{ color:var(--muted); font-size:12px; margin-top:2px; }}
  .grid {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:20px; }}
  .card {{ background:var(--card); border-radius:12px; padding:20px; min-width:0; }}
  .card.full {{ grid-column:1 / -1; }}
  .card h2 {{ font-size:14px; margin:0 0 14px; color:var(--fg); font-weight:600; }}
  canvas {{ max-height:360px; max-width:100%; }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  th,td {{ text-align:left; padding:6px 8px; border-bottom:1px solid #262a33; }}
  th {{ color:var(--muted); font-weight:500; }}
  td.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  .filters {{ display:flex; gap:16px; margin-bottom:14px; flex-wrap:wrap; }}
  .filters label {{ font-size:12px; color:var(--muted); display:flex; align-items:center; gap:6px; }}
  .filters select {{ background:#0f1115; color:var(--fg); border:1px solid #2c313c;
                     border-radius:8px; padding:6px 10px; font-size:13px; }}
  .tokenbar {{ display:flex; align-items:center; gap:10px; margin-bottom:16px; flex-wrap:wrap; }}
  .tokenbar label {{ font-size:12px; color:var(--muted); display:flex; align-items:center; gap:8px; }}
  .tokenbar input {{ background:#0f1115; color:var(--fg); border:1px solid #2c313c;
                    border-radius:8px; padding:7px 11px; font-size:13px; min-width:240px;
                    font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }}
  .tokenbar input:focus {{ outline:none; border-color:var(--accent); }}
  #tokenSave {{ background:var(--card); color:var(--fg); border:1px solid #2c313c;
               border-radius:8px; padding:7px 14px; font-size:13px; cursor:pointer; }}
  #tokenSave:hover {{ border-color:var(--accent); }}
  #tokenStatus {{ font-size:12px; color:#5bffb0; }}
  tbody tr {{ cursor:pointer; }}
  tbody tr:hover td {{ background:#222633; }}
  /* 저자 상세 페이지 */
  .back {{ background:var(--card); color:var(--fg); border:1px solid #2c313c;
          border-radius:8px; padding:8px 14px; font-size:13px; cursor:pointer; margin-bottom:18px; }}
  .back:hover {{ border-color:var(--accent); }}
  #detailHead h1 {{ margin-bottom:6px; }}
  #detailHead .meta {{ color:var(--muted); font-size:13px; margin-bottom:24px; }}
  #detailHead .meta b {{ color:var(--fg); font-weight:600; }}
  .cards {{ display:flex; flex-direction:column; gap:16px; max-width:920px; }}
  .qcard {{ background:var(--card); border-radius:12px; padding:24px 26px; border:1px solid #232733;
           display:flex; flex-direction:row; gap:22px; align-items:stretch; }}
  .qmain {{ flex:1; min-width:0; display:flex; flex-direction:column; gap:14px; }}
  .qside {{ width:180px; flex-shrink:0; border-left:1px solid #2a2f3a; padding-left:18px;
           display:flex; flex-direction:column; gap:14px; }}
  .side-title {{ font-size:12px; color:var(--muted); font-weight:600; }}
  .mitem {{ display:flex; flex-direction:column; gap:2px; }}
  .mlabel {{ font-size:11px; color:#6b7280; }}
  .mval {{ font-size:18px; font-weight:700; color:#e6e8ec; font-variant-numeric:tabular-nums; }}
  .msub {{ font-size:11px; color:var(--muted); }}
  @media(max-width:680px){{ .qcard{{flex-direction:column;}}
    .qside{{width:auto;border-left:none;border-top:1px solid #2a2f3a;padding-left:0;
           padding-top:14px;flex-direction:row;gap:22px;}} }}
  .qhead {{ display:flex; justify-content:space-between; align-items:flex-start; gap:14px; flex-wrap:wrap; }}
  .qbadges {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; }}
  .qactions {{ display:flex; align-items:center; gap:8px; flex-shrink:0; }}
  .statusbtns {{ display:flex; gap:4px; }}
  .statusbtns button {{ background:#1f242e; color:#8a909c; border:1px solid #2c313c;
                       border-radius:6px; padding:4px 9px; font-size:12px; cursor:pointer; }}
  .statusbtns button:hover {{ border-color:var(--accent); color:var(--fg); }}
  .statusbtns button.active {{ background:#173a2a; color:#5bffb0; border-color:#2a5a44; }}
  .retrans {{ background:#2a2238; color:#c79dff; border:1px solid #3a3550;
             border-radius:6px; padding:4px 11px; font-size:12px; cursor:pointer; white-space:nowrap; }}
  .retrans:hover {{ border-color:#c79dff; }}
  .retrans:disabled {{ opacity:.6; cursor:default; }}
  .qdel, .del-author {{ background:#2a1a1d; color:#ff8a8a; border:1px solid #4a2a2e;
                       border-radius:6px; padding:4px 11px; font-size:12px; cursor:pointer; white-space:nowrap; }}
  .qdel:hover, .del-author:hover {{ border-color:#ff5b5b; color:#ffb0b0; }}
  .qcard .qtext {{ font-size:21px; line-height:1.6; }}
  .qcard .qorig {{ font-size:16px; color:var(--muted); font-style:italic; line-height:1.55; }}
  .qcard .tags {{ display:flex; flex-wrap:wrap; gap:8px; }}
  .tag {{ font-size:13px; padding:4px 11px; border-radius:999px; background:#222a3a; color:#9db8ff; }}
  .tag.sit {{ background:#2a2238; color:#c79dff; }}
  .tag.need {{ background:#223a2e; color:#7fe6b0; }}
  .qcard .qfoot {{ display:flex; flex-wrap:wrap; gap:8px 16px; font-size:13px;
                  color:var(--muted); border-top:1px solid #232733; padding-top:12px; }}
  .qcard .qfoot .k {{ color:#5b6470; }}
  .badge {{ font-size:12px; padding:3px 9px; border-radius:6px; font-weight:600; }}
  .badge.published {{ background:#173a2a; color:#5bffb0; }}
  .badge.draft {{ background:#3a3417; color:#ffe05b; }}
  .badge.reviewed {{ background:#17313a; color:#5bd6ff; }}
  .badge.rejected {{ background:#3a1717; color:#ff8a8a; }}
  .badge.verified {{ background:#173a2a; color:#5bffb0; }}
  .badge.attributed {{ background:#222a3a; color:#9db8ff; }}
  .badge.disputed {{ background:#3a2e17; color:#ffb05b; }}
  .badge.unknown {{ background:#2a2d34; color:#8a909c; }}
  .badge.score {{ background:#3a3417; color:#ffd95b; }}
  .impactsel {{ background:transparent; color:inherit; border:none; font-size:12px;
               font-weight:600; cursor:pointer; padding:0 1px; }}
  .impactsel:focus {{ outline:none; }}
  .impactsel option {{ background:#1a1d24; color:#e6e8ec; }}
  .topbar {{ display:flex; align-items:center; gap:20px; flex-wrap:wrap; margin-bottom:22px;
            padding-bottom:16px; border-bottom:1px solid #232733; }}
  .topbar h1 {{ margin:0; }}
  .topbar .tokenbar {{ margin:0; }}
  .tabs {{ display:flex; gap:6px; margin-left:auto; }}
  .tabbtn {{ background:transparent; color:var(--muted); border:1px solid transparent;
            border-radius:8px; padding:9px 18px; font-size:14px; cursor:pointer; }}
  .tabbtn:hover {{ color:var(--fg); }}
  .tabbtn.active {{ background:var(--card); color:var(--fg); border-color:#2c313c; }}
  .pane-title {{ font-size:18px; margin:0 0 18px; }}
  .pane-title .sub {{ display:inline; font-size:13px; }}
  .pager {{ display:flex; align-items:center; justify-content:center; gap:14px; margin-top:24px; }}
  .pager button {{ background:var(--card); color:var(--fg); border:1px solid #2c313c;
                  border-radius:8px; padding:8px 16px; font-size:13px; cursor:pointer; }}
  .pager button:disabled {{ opacity:.4; cursor:default; }}
  .pager .pinfo {{ font-size:13px; color:var(--muted); }}
  .taggroup {{ margin-bottom:22px; }}
  .taggroup h3 {{ font-size:14px; color:var(--accent); margin:0 0 10px; }}
  .tagchips {{ display:flex; flex-wrap:wrap; gap:8px; }}
  .tagchip {{ display:inline-flex; align-items:center; gap:7px; background:var(--card);
             border:1px solid #2c313c; border-radius:999px; padding:6px 12px; font-size:13px; }}
  .tagchip .c {{ background:#222a3a; color:#9db8ff; border-radius:999px; padding:1px 8px;
                font-size:11px; font-variant-numeric:tabular-nums; }}
  .tagchip.zero {{ opacity:.5; }}
  @media(max-width:820px){{ .grid{{grid-template-columns:minmax(0,1fr);}} .tabs{{margin-left:0;width:100%;}} }}

  /* ===== 모바일 / 폴더블(Galaxy Z Fold7) 최적화 ===== */
  /* Fold7 펼침(약 768~900px 정사각형 화면): 카드 폭 제한 해제 */
  @media(max-width:900px){{ .cards{{max-width:100%;}} }}

  /* 일반 모바일 + Fold7 커버(접힘) */
  @media(max-width:600px){{
    body {{ padding:16px 14px;
            padding-left:max(14px,env(safe-area-inset-left));
            padding-right:max(14px,env(safe-area-inset-right)); }}
    h1 {{ font-size:19px; }}
    .topbar {{ gap:12px; margin-bottom:16px; padding-bottom:14px; }}
    .topbar h1 {{ width:100%; }}
    .tokenbar {{ width:100%; gap:8px; }}
    .tokenbar label {{ flex:1; gap:6px; flex-wrap:wrap; }}
    .tokenbar input {{ min-width:0; flex:1 1 140px; min-height:42px; }}
    #tokenSave {{ min-height:42px; }}
    .tabs {{ width:100%; gap:4px; }}
    .tabbtn {{ flex:1; text-align:center; padding:11px 8px; font-size:13px; }}
    .kpis {{ gap:10px; margin-bottom:20px; }}
    .kpi {{ flex:1 1 calc(50% - 5px); min-width:0; padding:13px 14px; }}
    .kpi .v {{ font-size:23px; }}
    .grid {{ gap:14px; }}
    .card {{ padding:16px 14px; }}
    canvas {{ max-height:300px; }}
    /* 넓은 표는 카드 안에서 가로 스크롤 */
    .card table {{ display:block; overflow-x:auto; white-space:nowrap;
                   -webkit-overflow-scrolling:touch; }}
    .filters {{ gap:10px 14px; }}
    .filters label {{ flex:1 1 calc(50% - 7px); flex-wrap:wrap; }}
    .filters select, .filters input {{ flex:1 1 90px; min-width:0; min-height:40px; }}
    .pane-title {{ font-size:16px; }}
    /* 명언 카드 */
    .cards {{ gap:14px; }}
    .qcard {{ padding:18px 16px; gap:16px; }}
    .qcard .qtext {{ font-size:18px; line-height:1.55; }}
    .qcard .qorig {{ font-size:14px; }}
    .qhead {{ flex-direction:column; gap:10px; }}
    .qactions {{ width:100%; flex-wrap:wrap; }}
    .qcard .qfoot {{ gap:6px 12px; }}
    /* 터치 타깃 확대 */
    .statusbtns {{ flex-wrap:wrap; }}
    .statusbtns button, .retrans, .qdel, .del-author, .back {{
        padding:9px 13px; font-size:13px; min-height:40px; }}
    .pager button {{ padding:10px 16px; min-height:44px; }}
  }}

  /* Fold7 커버 등 초협소 화면 (≤404px) */
  @media(max-width:404px){{
    body {{ padding:12px 10px; }}
    h1 {{ font-size:18px; }}
    .qcard {{ padding:16px 13px; }}
    .qcard .qtext {{ font-size:17px; }}
    .tabbtn {{ padding:10px 4px; font-size:12px; }}
    .filters label {{ flex:1 1 100%; }}
    .qside {{ flex-direction:column; gap:12px; }}
  }}
</style>
</head>
<body>
<header class="topbar">
  <h1>명언 관리 콘솔</h1>
  <div class="tokenbar">
    <label>ADMIN_TOKEN
      <input id="tokenInput" type="text" autocomplete="off" autocapitalize="off"
             autocorrect="off" spellcheck="false" placeholder="토큰을 입력하세요">
    </label>
    <button id="tokenSave">저장</button>
    <span id="tokenStatus"></span>
  </div>
  <nav class="tabs">
    <button class="tabbtn active" data-tab="authors">저자관리</button>
    <button class="tabbtn" data-tab="quotes">명언관리</button>
    <button class="tabbtn" data-tab="tags">태그관리</button>
  </nav>
</header>

<section class="tabpane" data-tab="authors">
<div id="dashboard">
  <div class="sub">표에서 저자를 클릭하면 그 저자의 명언 카드가 열립니다</div>
  <div class="kpis">
    <div class="kpi"><div class="v">{n_quotes}</div><div class="l">전체 명언</div></div>
    <div class="kpi"><div class="v">{n_authors}</div><div class="l">전체 저자</div></div>
    <div class="kpi"><div class="v">{avg}</div><div class="l">저자당 평균 명언</div></div>
    <div class="kpi"><div class="v">{single}</div><div class="l">명언 1개 저자</div></div>
  </div>

  <div class="grid">
    <div class="card full"><h2>명언 많은 저자 Top 30</h2><canvas id="topAuthors"></canvas></div>
    <div class="card"><h2>저자당 명언 수 분포 (롱테일)</h2><canvas id="perAuthor"></canvas></div>
    <div class="card"><h2>직업군별 분포</h2><canvas id="byProf"></canvas></div>
    <div class="card full"><h2>국적별 분포</h2><canvas id="byNat"></canvas></div>
    <div class="card full">
      <h2>전체 저자 상세 (<span id="rowCount">{n_authors_rows}</span>명)</h2>
      <div class="filters">
        <label>국적 <select id="fNat"></select></label>
        <label>직업 <select id="fProf"></select></label>
        <label>정렬 <select id="fSort">
          <option value="cnt_desc">명언 수 ↓</option>
          <option value="cnt_asc">명언 수 ↑</option>
          <option value="name_asc">이름 ↑</option>
          <option value="name_desc">이름 ↓</option>
        </select></label>
      </div>
      <table>
        <thead><tr><th class="num">#</th><th>저자</th><th>국적</th><th>직업</th><th class="num">명언 수</th><th></th></tr></thead>
        <tbody id="authorBody"></tbody>
      </table>
    </div>
  </div>
</div>

<section id="detail" hidden>
  <button class="back" id="backBtn">← 저자 목록</button>
  <div id="detailHead"></div>
  <div class="filters">
    <label>정렬 <select id="cSort">
      <option value="score_desc">임팩트 ↓</option>
      <option value="score_asc">임팩트 ↑</option>
      <option value="date_desc">등록일 최신</option>
      <option value="date_asc">등록일 오래된</option>
    </select></label>
    <label>신뢰도 <select id="cRel"></select></label>
    <label>최소 임팩트 <select id="cMinScore"></select></label>
  </div>
  <div id="cardGrid" class="cards"></div>
</section>
</section>

<section class="tabpane" data-tab="quotes" hidden>
  <h2 class="pane-title">명언관리</h2>
  <div class="filters">
    <label>검색 <input id="qSearch" type="text" autocomplete="off" placeholder="명언·원문·저자"></label>
    <label>상태 <select id="qStatus">
      <option value="">전체</option><option>draft</option><option>reviewed</option>
      <option>published</option><option>rejected</option></select></label>
    <label>신뢰도 <select id="qRel">
      <option value="">전체</option><option>verified</option><option>attributed</option>
      <option>disputed</option><option>unknown</option></select></label>
    <label>최소 임팩트 <select id="qMinScore"></select></label>
    <label>정렬 <select id="qSort">
      <option value="impact_desc">임팩트 ↓</option>
      <option value="impact_asc">임팩트 ↑</option>
      <option value="date_desc">등록일 최신</option>
      <option value="date_asc">등록일 오래된</option>
    </select></label>
  </div>
  <div id="qlistInfo" class="sub"></div>
  <div id="qlist" class="cards"></div>
  <div id="qpager" class="pager"></div>
</section>

<section class="tabpane" data-tab="tags" hidden>
  <h2 class="pane-title">태그관리 <span class="sub">조회 전용 · 숫자는 사용 명언 수</span></h2>
  <div id="tagKeywords"></div>
  <div id="tagSituations"></div>
</section>

<script>
const DATA = {data_json};
const NAT_KO = {{
  AF:'아프가니스탄', AR:'아르헨티나', AT:'오스트리아', AU:'호주', BR:'브라질', CA:'캐나다',
  CH:'스위스', CL:'칠레', CN:'중국', CO:'콜롬비아', CZ:'체코', DE:'독일', DK:'덴마크',
  EG:'이집트', ES:'스페인', FR:'프랑스', GB:'영국', GR:'그리스', IE:'아일랜드', IL:'이스라엘',
  IN:'인도', IR:'이란', IT:'이탈리아', JM:'자메이카', JP:'일본', KR:'대한민국', LB:'레바논',
  MM:'미얀마', MX:'멕시코', NG:'나이지리아', NL:'네덜란드', NP:'네팔', NZ:'뉴질랜드', PL:'폴란드',
  PT:'포르투갈', RO:'루마니아', RS:'세르비아', RU:'러시아', SE:'스웨덴', SO:'소말리아',
  TR:'튀르키예', TT:'트리니다드토바고', UN:'미상', US:'미국', VN:'베트남', ZA:'남아프리카공화국',
}};
function natName(code) {{ return NAT_KO[code] || code || '미상'; }}
const C = ['#5b9dff','#7c5bff','#ff5b9d','#5bffb0','#ffb05b','#ff5b5b','#5bd6ff','#c0ff5b'];
const opts = (horiz)=>({{
  indexAxis: horiz ? 'y' : 'x',
  plugins:{{legend:{{display:false}}}},
  scales:{{x:{{ticks:{{color:'#8a909c'}},grid:{{color:'#262a33'}}}},
           y:{{ticks:{{color:'#8a909c'}},grid:{{color:'#262a33'}}}}}}
}});

new Chart(topAuthors,{{type:'bar',
  data:{{labels:DATA.top_authors.map(r=>r.name),
    datasets:[{{data:DATA.top_authors.map(r=>r.cnt),backgroundColor:'#5b9dff'}}]}},
  options:opts(true)}});

new Chart(perAuthor,{{type:'bar',
  data:{{labels:DATA.per_author.map(r=>r.quotes_per_author+'개'),
    datasets:[{{data:DATA.per_author.map(r=>r.num_authors),backgroundColor:'#7c5bff'}}]}},
  options:{{...opts(false),scales:{{...opts(false).scales,
    y:{{type:'logarithmic',ticks:{{color:'#8a909c'}},grid:{{color:'#262a33'}}}}}}}}}});

new Chart(byProf,{{type:'doughnut',
  data:{{labels:DATA.by_profession.map(r=>r.grp),
    datasets:[{{data:DATA.by_profession.map(r=>r.cnt),backgroundColor:C}}]}},
  options:{{plugins:{{legend:{{position:'right',labels:{{color:'#e6e8ec',font:{{size:11}}}}}}}}}}}});

new Chart(byNat,{{type:'bar',
  data:{{labels:DATA.by_nationality.map(r=>natName(r.nationality)),
    datasets:[{{data:DATA.by_nationality.map(r=>r.cnt),backgroundColor:'#5bffb0'}}]}},
  options:opts(false)}});

// --- 전체 저자 상세: 필터 + 정렬 ---
const fNat = document.getElementById('fNat');
const fProf = document.getElementById('fProf');
const fSort = document.getElementById('fSort');
const authorBody = document.getElementById('authorBody');
const rowCount = document.getElementById('rowCount');

function fillSelect(sel, values, labelFn) {{
  sel.innerHTML = '<option value="">전체</option>' +
    values.map(v => `<option value="${{v}}">${{labelFn ? labelFn(v) : v}}</option>`).join('');
}}
fillSelect(fNat, [...new Set(DATA.all_authors.map(r => r.nationality))].sort(), natName);
fillSelect(fProf, [...new Set(DATA.all_authors.map(r => r.profession))].sort());

function renderAuthors() {{
  const nat = fNat.value, prof = fProf.value, sort = fSort.value;
  let rows = DATA.all_authors.filter(r =>
    (!nat || r.nationality === nat) && (!prof || r.profession === prof));
  const cmp = {{
    cnt_desc: (a, b) => b.cnt - a.cnt || a.name.localeCompare(b.name),
    cnt_asc:  (a, b) => a.cnt - b.cnt || a.name.localeCompare(b.name),
    name_asc: (a, b) => a.name.localeCompare(b.name),
    name_desc:(a, b) => b.name.localeCompare(a.name),
  }}[sort];
  rows = [...rows].sort(cmp);
  rowCount.textContent = rows.length;
  authorBody.innerHTML = rows.map((r, i) =>
    `<tr data-aid="${{r.author_id}}"><td class="num">${{i + 1}}</td><td>${{esc(r.name)}}</td>`
    + `<td>${{esc(natName(r.nationality))}}</td><td>${{esc(r.profession)}}</td>`
    + `<td class="num">${{r.cnt}}</td>`
    + `<td><button class="del-author" title="저자 삭제">삭제</button></td></tr>`).join('');
}}
[fNat, fProf, fSort].forEach(el => el.addEventListener('change', renderAuthors));
renderAuthors();

// --- 저자 클릭 → 명언 카드 상세 페이지 ---
function esc(s) {{
  return String(s == null ? '' : s).replace(/[&<>"]/g,
    c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));
}}

const authorMap = {{}};
DATA.all_authors.forEach(a => {{ authorMap[a.author_id] = a; }});
const quotesByAuthor = {{}};
const quoteById = {{}};
DATA.quotes.forEach(q => {{ (quotesByAuthor[q.author_id] ||= []).push(q); quoteById[q.id] = q; }});

const dashboard = document.getElementById('dashboard');
const detail = document.getElementById('detail');
const detailHead = document.getElementById('detailHead');
const cardGrid = document.getElementById('cardGrid');

function tagList(arr, cls) {{
  return (arr || []).map(t => `<span class="tag ${{cls}}">${{esc(t)}}</span>`).join('');
}}

const STATUSES = ['draft', 'reviewed', 'published', 'rejected'];

function sideMeta(q) {{
  const items = [];
  if (q.reddit_upvotes != null)
    items.push(`<div class="mitem"><div class="mlabel">Reddit</div>`
      + `<div class="mval">▲ ${{q.reddit_upvotes.toLocaleString()}}</div>`
      + `${{q.reddit_subreddit ? `<div class="msub">r/${{esc(q.reddit_subreddit)}}</div>` : ''}}</div>`);
  if (q.goodreads_likes != null)
    items.push(`<div class="mitem"><div class="mlabel">Goodreads</div>`
      + `<div class="mval">♥ ${{q.goodreads_likes.toLocaleString()}}</div></div>`);
  if (q.naver_results != null)
    items.push(`<div class="mitem"><div class="mlabel">네이버 검색</div>`
      + `<div class="mval">${{q.naver_results.toLocaleString()}}</div></div>`);
  if (!items.length) return '';
  return `<div class="qside"><div class="side-title">참고 데이터</div>${{items.join('')}}</div>`;
}}

function quoteCard(q) {{
  const orig = q.text_original
    ? `<div class="qorig">“${{esc(q.text_original)}}” <span>(${{esc(q.original_language || '')}})</span></div>` : '';
  const foot = [
    `<span><span class="k">저자</span> ${{esc((authorMap[q.author_id] || {{}}).name || '?')}}</span>`,
    q.source ? `<span><span class="k">출처</span> ${{esc(q.source)}}</span>` : '',
    q.year ? `<span><span class="k">연도</span> ${{q.year}}</span>` : '',
    q.collection_category ? `<span><span class="k">수집</span> ${{esc(q.collection_category)}}</span>` : '',
    q.created_at ? `<span><span class="k">등록</span> ${{q.created_at}}</span>` : '',
    `<span><span class="k">ID</span> ${{esc(String(q.id).slice(0, 8))}}</span>`,
  ].filter(Boolean).join('');
  const statusBtns = STATUSES.map(s =>
    `<button data-s="${{s}}" class="${{q.status === s ? 'active' : ''}}">${{s}}</button>`).join('');
  // 원문이 있으면 재번역 가능 (방향 자동: ko→영어, 그 외→한국어)
  const canRetrans = q.text_original && q.original_language;
  const retransLabel = q.original_language === 'ko' ? '영어로 재번역' : '재번역';
  const impactOpts = (q.impact_score == null ? `<option value="" selected>-</option>` : '')
    + Array.from({{length: 10}}, (_, i) => i + 1)
        .map(n => `<option value="${{n}}" ${{q.impact_score === n ? 'selected' : ''}}>${{n}}</option>`).join('');
  const side = sideMeta(q);
  return `<div class="qcard" data-qid="${{esc(q.id)}}">
    <div class="qmain">
      <div class="qhead">
        <div class="qbadges">
          <span class="badge score">⚡ 임팩트 <select class="impactsel" title="임팩트 점수 변경">${{impactOpts}}</select>/10</span>
          <span class="badge js-status-badge ${{esc(q.status)}}">${{esc(q.status)}}</span>
          <span class="badge ${{esc(q.source_reliability)}}">${{esc(q.source_reliability)}}</span>
        </div>
        <div class="qactions">
          <div class="statusbtns">${{statusBtns}}</div>
          ${{canRetrans ? `<button class="retrans">${{retransLabel}}</button>` : ''}}
          <button class="qdel" title="명언 삭제">삭제</button>
        </div>
      </div>
      <div class="qtext">“${{esc(q.text)}}”</div>
      ${{orig}}
      <div class="tags">${{tagList(q.keywords, '')}}${{tagList(q.situations, 'sit')}}${{tagList(q.need_types, 'need')}}</div>
      <div class="qfoot">${{foot}}</div>
    </div>
    ${{side}}
  </div>`;
}}

const cSort = document.getElementById('cSort');
const cRel = document.getElementById('cRel');
const cMinScore = document.getElementById('cMinScore');
let currentAuthorQuotes = [];

function renderCards() {{
  const rel = cRel.value, minS = Number(cMinScore.value) || 0, sort = cSort.value;
  let qs = currentAuthorQuotes.filter(q =>
    (!rel || q.source_reliability === rel) && (q.impact_score || 0) >= minS);
  const cmp = {{
    score_desc: (a, b) => (b.impact_score || 0) - (a.impact_score || 0),
    score_asc:  (a, b) => (a.impact_score || 0) - (b.impact_score || 0),
    date_desc:  (a, b) => (b.created_at || '').localeCompare(a.created_at || ''),
    date_asc:   (a, b) => (a.created_at || '').localeCompare(b.created_at || ''),
  }}[sort];
  qs = qs.slice().sort(cmp);
  cardGrid.innerHTML = qs.length
    ? qs.map(quoteCard).join('')
    : '<div class="sub">조건에 맞는 명언이 없습니다.</div>';
}}
[cSort, cRel, cMinScore].forEach(el => el.addEventListener('change', renderCards));

function showAuthor(aid) {{
  const a = authorMap[aid];
  if (!a) return;
  currentAuthorQuotes = quotesByAuthor[aid] || [];
  detailHead.innerHTML = `<h1>${{esc(a.name)}}</h1>
    <div class="meta">
      <b>${{currentAuthorQuotes.length}}</b>개 명언 ·
      국적 <b>${{natName(a.nationality)}}</b> ·
      직업 <b>${{esc(a.profession)}}</b> ·
      분야 <b>${{esc(a.field)}}</b>
      ${{a.birth_year ? ` · 출생 <b>${{a.birth_year}}</b>` : ''}}
    </div>`;
  // 이 저자가 가진 신뢰도/점수 값으로 필터 옵션 구성
  const rels = [...new Set(currentAuthorQuotes.map(q => q.source_reliability))].filter(Boolean).sort();
  cRel.innerHTML = '<option value="">전체</option>'
    + rels.map(v => `<option value="${{v}}">${{v}}</option>`).join('');
  const scores = [...new Set(currentAuthorQuotes.map(q => q.impact_score).filter(s => s != null))].sort((x, y) => x - y);
  cMinScore.innerHTML = '<option value="0">전체</option>'
    + scores.map(v => `<option value="${{v}}">${{v}}+</option>`).join('');
  cSort.value = 'score_desc';
  renderCards();
  dashboard.hidden = true;
  detail.hidden = false;
  location.hash = 'author=' + encodeURIComponent(aid);
  window.scrollTo(0, 0);
}}

function showList() {{
  detail.hidden = true;
  dashboard.hidden = false;
  if (location.hash) history.replaceState(null, '', location.pathname);
}}

authorBody.addEventListener('click', e => {{
  const del = e.target.closest('.del-author');
  if (del) {{ deleteAuthor(del.closest('tr[data-aid]').dataset.aid); return; }}
  const tr = e.target.closest('tr[data-aid]');
  if (tr) showAuthor(tr.dataset.aid);
}});

async function deleteAuthor(aid) {{
  const t = adminToken();
  if (!t) return;
  const a = authorMap[aid];
  const name = a ? a.name : aid;
  if (!confirm(`저자 "${{name}}" 및 그 명언 ${{a ? a.cnt : '?'}}개·관계·로그를 모두 삭제합니다.\\n되돌릴 수 없습니다. 진행할까요?`)) return;
  try {{
    const res = await fetch(`/admin/api/authors/${{aid}}`, {{
      method: 'DELETE', headers: {{ 'Authorization': 'Bearer ' + t }},
    }});
    const data = await res.json().catch(() => ({{}}));
    if (res.status === 401) {{ alert('토큰 인증 실패. 토큰을 확인하세요.'); return; }}
    if (!res.ok) {{ alert('저자 삭제 실패: ' + (data.error || res.status)); return; }}
    DATA.all_authors = DATA.all_authors.filter(x => x.author_id !== aid);
    delete authorMap[aid];
    (quotesByAuthor[aid] || []).forEach(q => delete quoteById[q.id]);
    delete quotesByAuthor[aid];
    renderAuthors();
    alert(`삭제 완료 — 명언 ${{data.deleted_quotes || 0}}개 함께 삭제됨`);
  }} catch (e) {{ alert('네트워크 오류: ' + e.message); }}
}}
document.getElementById('backBtn').addEventListener('click', showList);

// --- 관리자 액션: 상태 변경 / 재번역 (동일 출처에서 서빙될 때만 동작) ---
const tokenInput = document.getElementById('tokenInput');
const tokenStatus = document.getElementById('tokenStatus');
tokenInput.value = localStorage.getItem('admin_token') || '';
document.getElementById('tokenSave').addEventListener('click', () => {{
  const v = tokenInput.value.trim();
  localStorage.setItem('admin_token', v);
  tokenStatus.textContent = v ? '✓ 저장됨' : '비어 있음';
  setTimeout(() => {{ tokenStatus.textContent = ''; }}, 2000);
}});

function adminToken() {{
  const t = tokenInput.value.trim();
  if (!t) {{
    alert('상단 ADMIN_TOKEN 입력란에 토큰을 먼저 입력하세요.');
    tokenInput.focus();
    return '';
  }}
  localStorage.setItem('admin_token', t);
  return t;
}}

function patchCardStatus(qid, status) {{
  const card = document.querySelector(`.qcard[data-qid="${{qid}}"]`);
  if (!card) return;
  const badge = card.querySelector('.js-status-badge');
  if (badge) {{ badge.textContent = status; badge.className = 'badge js-status-badge ' + status; }}
  card.querySelectorAll('.statusbtns button')
    .forEach(b => b.classList.toggle('active', b.dataset.s === status));
}}

async function setStatus(qid, status) {{
  const t = adminToken();
  if (!t) return;
  try {{
    const res = await fetch(`/admin/api/quotes/${{qid}}`, {{
      method: 'PATCH',
      headers: {{ 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + t }},
      body: JSON.stringify({{ status }}),
    }});
    if (res.status === 401) {{ localStorage.removeItem('admin_token'); alert('토큰 인증 실패. 다시 입력하세요.'); return; }}
    if (!res.ok) {{ alert('상태 변경 실패: ' + res.status); return; }}
    if (quoteById[qid]) quoteById[qid].status = status;
    patchCardStatus(qid, status);
  }} catch (e) {{ alert('네트워크 오류: ' + e.message + '\\n(대시보드에서 서빙된 페이지인지 확인하세요)'); }}
}}

async function retranslate(qid) {{
  const t = adminToken();
  if (!t) return;
  if (!confirm('원문을 LLM으로 재번역하고 상태를 draft로 초기화합니다. 진행할까요?')) return;
  const card = cardGrid.querySelector(`.qcard[data-qid="${{qid}}"]`);
  const btn = card && card.querySelector('.retrans');
  if (btn) {{ btn.disabled = true; btn.textContent = '번역 중…'; }}
  try {{
    const res = await fetch(`/admin/api/quotes/${{qid}}/retranslate`, {{
      method: 'POST', headers: {{ 'Authorization': 'Bearer ' + t }},
    }});
    const data = await res.json().catch(() => ({{}}));
    if (res.status === 401) {{ localStorage.removeItem('admin_token'); alert('토큰 인증 실패. 다시 입력하세요.'); return; }}
    if (!res.ok) {{ alert('재번역 실패: ' + (data.error || res.status)); return; }}
    if (quoteById[qid]) {{ quoteById[qid].text = data.text; quoteById[qid].status = data.status; }}
    const tEl = card && card.querySelector('.qtext');
    if (tEl) tEl.textContent = '“' + data.text + '”';
    patchCardStatus(qid, data.status);
  }} catch (e) {{ alert('네트워크 오류: ' + e.message); }}
  finally {{ if (btn) {{ btn.disabled = false; btn.textContent = '재번역'; }} }}
}}

async function setImpact(qid, val) {{
  if (val === '') return;
  const t = adminToken();
  if (!t) return;
  try {{
    const res = await fetch(`/admin/api/quotes/${{qid}}`, {{
      method: 'PATCH',
      headers: {{ 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + t }},
      body: JSON.stringify({{ impact_score: Number(val) }}),
    }});
    if (res.status === 401) {{ alert('토큰 인증 실패. 토큰을 확인하세요.'); return; }}
    if (!res.ok) {{ alert('임팩트 변경 실패: ' + res.status); return; }}
    if (quoteById[qid]) quoteById[qid].impact_score = Number(val);
  }} catch (e) {{ alert('네트워크 오류: ' + e.message); }}
}}

async function deleteQuote(qid) {{
  const t = adminToken();
  if (!t) return;
  if (!confirm('이 명언을 삭제합니다. 되돌릴 수 없습니다. 진행할까요?')) return;
  const aid = quoteById[qid] && quoteById[qid].author_id;
  try {{
    const res = await fetch(`/admin/api/quotes/${{qid}}`, {{
      method: 'DELETE', headers: {{ 'Authorization': 'Bearer ' + t }},
    }});
    if (res.status === 401) {{ alert('토큰 인증 실패. 토큰을 확인하세요.'); return; }}
    if (!res.ok) {{ alert('명언 삭제 실패: ' + res.status); return; }}
    delete quoteById[qid];
    if (aid && quotesByAuthor[aid]) quotesByAuthor[aid] = quotesByAuthor[aid].filter(x => x.id !== qid);
    currentAuthorQuotes = currentAuthorQuotes.filter(x => x.id !== qid);
    const card = document.querySelector(`.qcard[data-qid="${{qid}}"]`);
    if (card) card.remove();
  }} catch (e) {{ alert('네트워크 오류: ' + e.message); }}
}}

// 카드 액션은 어느 탭(저자 상세 / 명언관리)이든 동작하도록 document에 위임
document.addEventListener('click', e => {{
  const sb = e.target.closest('.statusbtns button');
  if (sb) {{ setStatus(sb.closest('.qcard').dataset.qid, sb.dataset.s); return; }}
  const rb = e.target.closest('.retrans');
  if (rb) {{ retranslate(rb.closest('.qcard').dataset.qid); return; }}
  const qd = e.target.closest('.qdel');
  if (qd) {{ deleteQuote(qd.closest('.qcard').dataset.qid); return; }}
}});

document.addEventListener('change', e => {{
  const sel = e.target.closest('.impactsel');
  if (sel) setImpact(sel.closest('.qcard').dataset.qid, sel.value);
}});

// ===== 탭 전환 =====
const tabBtns = document.querySelectorAll('.tabbtn');
const tabPanes = document.querySelectorAll('.tabpane');
let quotesInited = false, tagsRendered = false;
function showTab(name) {{
  tabPanes.forEach(p => p.hidden = p.dataset.tab !== name);
  tabBtns.forEach(b => b.classList.toggle('active', b.dataset.tab === name));
  if (name === 'quotes' && !quotesInited) {{ initQuoteList(); quotesInited = true; }}
  if (name === 'tags' && !tagsRendered) {{ renderTags(); tagsRendered = true; }}
}}
tabBtns.forEach(b => b.addEventListener('click', () => showTab(b.dataset.tab)));

// ===== 명언관리: 검색 + 필터 + 페이지네이션 =====
const qSearch = document.getElementById('qSearch');
const qStatus = document.getElementById('qStatus');
const qRel = document.getElementById('qRel');
const qMinScore = document.getElementById('qMinScore');
const qSort = document.getElementById('qSort');
const qlist = document.getElementById('qlist');
const qlistInfo = document.getElementById('qlistInfo');
const qpager = document.getElementById('qpager');
const Q_PAGE_SIZE = 20;
let qPage = 1;

function initQuoteList() {{
  qMinScore.innerHTML = '<option value="0">전체</option>'
    + Array.from({{length: 10}}, (_, i) => i + 1).map(n => `<option value="${{n}}">${{n}}+</option>`).join('');
  [qStatus, qRel, qMinScore, qSort].forEach(el =>
    el.addEventListener('change', () => {{ qPage = 1; renderQuoteList(); }}));
  qSearch.addEventListener('input', () => {{ qPage = 1; renderQuoteList(); }});
  renderQuoteList();
}}

function filteredQuotes() {{
  const kw = qSearch.value.trim().toLowerCase();
  const st = qStatus.value, rel = qRel.value, minS = Number(qMinScore.value) || 0;
  const rows = Object.values(quoteById).filter(q => {{
    if (st && q.status !== st) return false;
    if (rel && q.source_reliability !== rel) return false;
    if ((q.impact_score || 0) < minS) return false;
    if (kw) {{
      const name = (authorMap[q.author_id] || {{}}).name || '';
      const hay = (q.text + ' ' + (q.text_original || '') + ' ' + name).toLowerCase();
      if (!hay.includes(kw)) return false;
    }}
    return true;
  }});
  const cmp = {{
    impact_desc: (a, b) => (b.impact_score || 0) - (a.impact_score || 0),
    impact_asc:  (a, b) => (a.impact_score || 0) - (b.impact_score || 0),
    date_desc:   (a, b) => (b.created_at || '').localeCompare(a.created_at || ''),
    date_asc:    (a, b) => (a.created_at || '').localeCompare(b.created_at || ''),
  }}[qSort.value];
  return rows.sort(cmp);
}}

function renderQuoteList() {{
  const rows = filteredQuotes();
  const total = rows.length;
  const pages = Math.max(1, Math.ceil(total / Q_PAGE_SIZE));
  if (qPage > pages) qPage = pages;
  const start = (qPage - 1) * Q_PAGE_SIZE;
  const pageRows = rows.slice(start, start + Q_PAGE_SIZE);
  qlistInfo.textContent = `총 ${{total.toLocaleString()}}개 · ${{qPage}}/${{pages}} 페이지`;
  qlist.innerHTML = pageRows.length
    ? pageRows.map(quoteCard).join('')
    : '<div class="sub">조건에 맞는 명언이 없습니다.</div>';
  qpager.innerHTML = `<button id="qPrev" ${{qPage <= 1 ? 'disabled' : ''}}>← 이전</button>`
    + `<span class="pinfo">${{qPage}} / ${{pages}}</span>`
    + `<button id="qNext" ${{qPage >= pages ? 'disabled' : ''}}>다음 →</button>`;
  const prev = document.getElementById('qPrev'), next = document.getElementById('qNext');
  if (prev) prev.onclick = () => {{ if (qPage > 1) {{ qPage--; renderQuoteList(); window.scrollTo(0, 0); }} }};
  if (next) next.onclick = () => {{ if (qPage < pages) {{ qPage++; renderQuoteList(); window.scrollTo(0, 0); }} }};
}}

// ===== 태그관리 (조회 전용) =====
function tagSection(title, rows) {{
  const byGroup = {{}};
  rows.forEach(r => {{ (byGroup[r.grp] ||= []).push(r); }});
  const groups = Object.keys(byGroup).sort();
  let html = `<h3 style="font-size:15px;margin:8px 0 16px;">${{title}} `
    + `<span class="sub" style="display:inline">${{rows.length}}개</span></h3>`;
  html += groups.map(g => `<div class="taggroup"><h3>${{esc(g)}}</h3><div class="tagchips">`
    + byGroup[g].map(r => `<span class="tagchip ${{r.cnt == 0 ? 'zero' : ''}}">`
        + `${{esc(r.name)}}<span class="c">${{r.cnt}}</span></span>`).join('')
    + `</div></div>`).join('');
  return html;
}}
function renderTags() {{
  document.getElementById('tagKeywords').innerHTML = tagSection('키워드', DATA.keyword_usage);
  document.getElementById('tagSituations').innerHTML = tagSection('상황', DATA.situation_usage);
}}

window.addEventListener('hashchange', () => {{
  const m = location.hash.match(/author=([^&]+)/);
  if (m) showAuthor(decodeURIComponent(m[1])); else showList();
}});
// 새로고침 시 해시 복원
(() => {{
  const m = location.hash.match(/author=([^&]+)/);
  if (m) showAuthor(decodeURIComponent(m[1]));
}})();
</script>
</body>
</html>"""


def build_html():
    """현재 DB로 관리자 콘솔 HTML 문자열을 생성해 반환한다 (파일 미저장)."""
    data = collect()
    totals = data["totals"]
    n_quotes = totals["quotes"]
    n_authors = totals["authors"]
    single = next(
        (r["num_authors"] for r in data["per_author"] if r["quotes_per_author"] == 1),
        0,
    )
    return HTML.format(
        n_quotes=n_quotes,
        n_authors=n_authors,
        n_authors_rows=len(data["all_authors"]),
        avg=round(n_quotes / n_authors, 1) if n_authors else 0,
        single=single,
        data_json=json.dumps(data, ensure_ascii=False),
    )


def main():
    html = build_html()
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"리포트 생성 완료: {REPORT_PATH}")


if __name__ == "__main__":
    main()
