"""영화 데이터 그래프 도감 2 — 분포와 관계

디자인: '형태 없는 결'
- 바탕은 무채색, 색(하늘색·황동색)은 읽어야 할 한 점에만
- 테두리 없음. 구분이 필요한 곳은 한 단 올리거나(raise) 내려서(inset) 가른다
- 빛은 언제나 위에서 온다
"""

import html as htmlib

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

TITLE = "영화 데이터 그래프 도감 2 - 분포와 관계"
DATA_URL = "https://raw.githubusercontent.com/happykth/data/main/kobis_movies.csv"

st.set_page_config(page_title=TITLE, layout="wide")


# ---------------------------------------------------------------- 색 토큰
TOKENS = {
        "page-a": "#1b1d21", "page-b": "#212429", "page-c": "#262a30",
        "surface": "#25282d", "well": "#1c1f23", "well-2": "#202327",
        "text-a": "#eef0f3", "text-b": "#c5cad1",
        "body-a": "#b4bac2", "body-b": "#949aa3",
        "dim-a": "#7c828c", "dim-b": "#5b616a",
        "sky": "#7bb9de", "sky-b": "#5e93b9", "sky-soft": "rgba(123, 185, 222, 0.22)",
        "sky-text": "#8cc7e8", "sky-text-b": "#6ba8cc",
        "brass": "#d3a869", "brass-text": "#e0b878", "brass-text-b": "#bd9557",
        "brass-glow": "rgba(211, 168, 105, 0.5)",
        "hi": "rgba(255, 255, 255, 0.055)", "hi-strong": "rgba(255, 255, 255, 0.10)", "lo": "rgba(0, 0, 0, 0.55)",
        "lo-strong": "rgba(0, 0, 0, 0.7)",
        "inset-lo": "rgba(0, 0, 0, 0.34)", "edge-lo": "rgba(0, 0, 0, 0.45)",
        "wash-1": "rgba(120, 165, 205, 0.055)", "wash-2": "rgba(200, 165, 105, 0.03)",
        "tag": "rgba(255, 255, 255, 0.08)",
        "grid": "rgba(255, 255, 255, 0.06)",
        # 작은 장르(기타) — 무채색 단계
        "other-hi": "#6d7784", "other-lo": "#474f59",
        # 누적 그래프의 면 — 디자인의 plateau(tier) 톤
        "tier-1": "#2f353c", "tier-edge": "#474f59",
}

# 장르 색 — 디자인 팔레트(하늘색·황동색 계열과 능선의 회청색) 안에서만 고른다.
# 하늘색과 황동색 계열을 번갈아 놓아 이웃한 장르가 섞이지 않게 하고,
# 편수가 많은 순서로 고정된 자리에 앉는다(순위가 아니라 장르를 따른다).
#          sky        brass      d1         d3         r2         sky-b      brass-b
SERIES = ["#7bb9de", "#d3a869", "#47738f", "#90703f", "#99a4b1", "#5e93b9", "#b08a4f"]


def inject_css(t):
    variables = "\n".join(f"  --{k}: {v};" for k, v in t.items())
    st.markdown(
        f"""
<style>
@import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css");

:root {{
{variables}
  --ui: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont,
    "Apple SD Gothic Neo", "Noto Sans KR", "Segoe UI", system-ui, sans-serif;
  --ease: cubic-bezier(0.22, 0.68, 0.24, 1);
  --radius: 22px;
  --gap-2: 1.6rem;
  --gap-3: 4.5rem;
  --raise: 0 3px 7px var(--lo), 0 -1px 1px var(--hi);
  --inset: inset 0 3px 7px var(--inset-lo), inset 0 -2px 3px var(--hi),
    inset 0 17px 20px -15px var(--inset-lo);
  --inset-sm: inset 0 2px 5px var(--inset-lo), inset 0 -1px 2px var(--hi);
  --lit-text: drop-shadow(0 -1px 0 var(--hi)) drop-shadow(0 3px 6px var(--lo));
  --lit-text-sm: drop-shadow(0 -1px 0 var(--hi)) drop-shadow(0 2px 4px var(--lo));
  --edge: linear-gradient(90deg, transparent 0%, var(--edge-lo) 8%, var(--edge-lo) 92%, transparent 100%),
    linear-gradient(90deg, transparent 0%, var(--hi) 8%, var(--hi) 92%, transparent 100%);
}}

/* 바탕 — 무채색 위에 아주 옅은 물빛 */
html, body, .stApp, [data-testid="stAppViewContainer"] {{
  font-family: var(--ui);
  background-color: var(--page-b);
  color: var(--body-a);
}}
.stApp {{
  background-image:
    radial-gradient(110% 70% at 14% -8%, var(--wash-1) 0%, transparent 60%),
    radial-gradient(90% 60% at 88% 4%, var(--wash-2) 0%, transparent 62%),
    radial-gradient(150% 100% at 50% 120%, var(--page-c) 0%, transparent 64%),
    linear-gradient(170deg, var(--page-a) 0%, var(--page-b) 55%, var(--page-a) 100%);
  background-attachment: fixed;
}}
header[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stDecoration"], footer {{ display: none; }}
.block-container {{
  max-width: 1120px;
  padding: 2.4rem 1rem 4rem;
}}
*, *::before, *::after {{ outline: 0; }}
/* 한국어는 낱말 단위로 줄을 바꾼다 */
.stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp span, .stApp textarea, .stApp .stMarkdown {{
  word-break: keep-all !important;
  overflow-wrap: break-word !important;
  line-break: strict;
}}
::selection {{ background: var(--sky-soft); color: var(--text-a); }}

/* 글자 — 같은 색에서 농도만 내려가는 기울기 */
.fx {{
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  -webkit-text-fill-color: transparent;
  margin: 0;
}}

.mark {{
  font-size: 1rem;
  font-weight: 500;
  letter-spacing: 0.04em;
  line-height: 1.6;
  background-image: linear-gradient(100deg, var(--text-a), var(--text-b));
  filter: var(--lit-text-sm);
}}
.mark-sub {{
  display: block;
  font-size: 0.58rem;
  font-weight: 400;
  letter-spacing: 0.4em;
  line-height: 2.4;
  -webkit-text-fill-color: var(--dim-a);
  color: var(--dim-a);
}}

.eyebrow, .meta {{
  font-size: 0.76rem;
  font-weight: 500;
  letter-spacing: 0.34em;
  background-image: linear-gradient(90deg, var(--dim-a), var(--dim-b));
}}
.hero {{ padding: clamp(3.5rem, 12vh, 8rem) 0 clamp(4rem, 10vh, 7rem); }}
.display {{
  margin-top: var(--gap-2);
  font-size: clamp(2.2rem, 5.6vw, 4.4rem);
  font-weight: 300;
  line-height: 1.26;
  letter-spacing: 0.005em;
  background-image: linear-gradient(172deg, var(--text-a) 0%, var(--text-b) 70%, var(--body-b) 100%);
  filter: var(--lit-text);
}}
.display .line {{ display: block; }}
.display .line + .line {{ text-indent: 0.5em; }}
.lede {{
  margin-top: var(--gap-2);
  max-width: 32em;
  font-size: clamp(1rem, 1.4vw, 1.12rem);
  font-weight: 300;
  line-height: 1.95;
  background-image: linear-gradient(180deg, var(--body-a) 0%, var(--body-b) 100%);
}}
.hero .meta {{ margin-top: 3rem; }}
.meta b {{ font-weight: 500; -webkit-text-fill-color: var(--sky-text); color: var(--sky-text); }}

/* 절 머리 — 번호 칸 + 제목 */
.band-head {{
  display: grid;
  grid-template-columns: 6rem minmax(0, 1fr);
  column-gap: var(--gap-2);
  row-gap: 0.8rem;
  align-items: start;
}}
.band-head > *:not(.index) {{ grid-column: 2; }}
.index {{
  font-size: 0.76rem;
  font-weight: 500;
  letter-spacing: 0.3em;
  padding-top: 0.9rem;
  background-image: linear-gradient(180deg, var(--dim-a), var(--dim-b));
}}
.head {{
  font-size: clamp(1.8rem, 4.2vw, 3rem);
  font-weight: 400;
  line-height: 1.3;
  letter-spacing: 0.02em;
  background-image: linear-gradient(160deg, var(--text-a), var(--body-b));
  filter: var(--lit-text);
}}
.band-head .lede {{ margin-top: 0.4rem; }}

/* 계단 — 절과 절 사이, 실제로 한 단 올라오거나 내려간 판 */
.stair {{ position: relative; height: 26px; margin: 0 0 2.6rem; }}
.stair span {{
  position: absolute;
  height: 9px;
  border-radius: 5px;
  background: var(--surface);
  box-shadow: var(--raise);
}}
.stair span:nth-child(2) {{ background: var(--well-2); box-shadow: var(--inset-sm); }}
.stair span:nth-child(1) {{ left: 0; width: 30%; top: 0; }}
.stair span:nth-child(2) {{ left: 30%; width: 26%; top: 8px; }}
.stair span:nth-child(3) {{ left: 56%; width: 44%; top: 16px; }}
.stair.even span:nth-child(1) {{ left: 0; width: 33.33%; }}
.stair.even span:nth-child(2) {{ left: 33.33%; width: 33.33%; }}
.stair.even span:nth-child(3) {{ left: 66.66%; width: 33.34%; }}

/* 그래프 캡션 */
.cap {{
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--gap-2);
  flex-wrap: wrap;
  margin: var(--gap-3) 0 1.1rem;
}}
.c-title {{
  font-size: clamp(1.15rem, 2.1vw, 1.5rem);
  font-weight: 500;
  letter-spacing: 0.02em;
  background-image: linear-gradient(170deg, var(--text-b), var(--body-b));
}}
.c-note {{
  font-size: 0.76rem;
  letter-spacing: 0.16em;
  background-image: linear-gradient(180deg, var(--dim-a), var(--dim-b));
}}

/* 한 단 낮은 면 — 그래프가 놓이는 자리 */
[class*="st-key-well-"] {{
  background: var(--well);
  border-radius: var(--radius);
  box-shadow: var(--inset);
  padding: 1.4rem 1.2rem 1rem;
  overflow: hidden;
}}
[class*="st-key-well-"] [data-testid="stPlotlyChart"] {{ background: transparent; }}
/* 도넛 조각은 판 위로 떠 있다 — 윗면에 빛, 아래에 그늘 */
/* 데이터 면 — 선으로 가르지 않고, 윗면의 빛과 아래 그늘로 한 단 띄운다 */
.st-key-well-hist .barlayer .trace,
[class*="st-key-well-"] .treemaplayer path.surface,
[class*="st-key-well-"] .scatterlayer .trace {{
  filter: drop-shadow(0 -1px 0 var(--hi-strong)) drop-shadow(0 3px 4px var(--lo));
}}

.js-plotly-plot .hoverlayer .hovertext path {{
  filter: drop-shadow(0 6px 12px var(--lo));
}}

/* 이 그래프로 알 수 있는 것 — 상자 대신 위에 한 줄의 결 */
.insight {{
  margin-top: 2rem;
  padding-top: 1.6rem;
  background-image: var(--edge);
  background-size: 100% 1px, 100% 1px;
  background-position: 0 0, 0 1px;
  background-repeat: no-repeat;
}}
.insight-label {{
  font-size: 0.76rem;
  font-weight: 500;
  letter-spacing: 0.24em;
  background-image: linear-gradient(180deg, var(--dim-a), var(--dim-b));
}}
.insight-text {{
  margin-top: 0.8rem;
  font-size: clamp(1.05rem, 1.6vw, 1.2rem);
  font-weight: 400;
  line-height: 1.8;
  background-image: linear-gradient(150deg, var(--text-a), var(--text-b));
}}
/* 적는 자리 — 한 단 파인 면 */
[class*="st-key-note-"] [data-testid="stTextAreaRootElement"] {{
  border: 0 !important;
  background: var(--well-2) !important;
  border-radius: 14px;
  box-shadow: var(--inset-sm);
}}
[class*="st-key-note-"] [data-testid="stTextAreaRootElement"] *,
[class*="st-key-note-"] textarea {{ background: transparent !important; background-color: transparent !important; }}
[class*="st-key-note-"] textarea {{
  font-family: var(--ui) !important;
  font-size: clamp(1.02rem, 1.5vw, 1.15rem) !important;
  font-weight: 400;
  line-height: 1.8 !important;
  color: var(--text-b) !important;
  -webkit-text-fill-color: var(--text-b);
  caret-color: var(--sky);
  resize: none !important;
  field-sizing: content;
  height: auto !important;
  min-height: 4.2rem;
  padding: 1rem 1.2rem !important;
}}
[class*="st-key-note-"] textarea::placeholder {{ color: var(--dim-a); -webkit-text-fill-color: var(--dim-a); }}
[class*="st-key-note-"] [data-testid="stTextAreaRootElement"]:focus-within {{
  box-shadow: var(--inset-sm), 0 0 0 3px var(--sky-soft);
}}
[class*="st-key-note-"] [data-testid="InputInstructions"] {{ display: none; }}
[class*="st-key-note-"] [data-testid="stTextAreaRootElement"] {{ height: auto !important; }}
[class*="st-key-note-"] {{ margin-top: 0.9rem; }}

/* 그래프 아래 읽을거리 */
.readout {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
  gap: 1.2rem clamp(2rem, 5vw, 4rem);
  margin-top: 1.6rem;
}}
.readout > div {{
  padding-top: 1.2rem;
  background-image: var(--edge);
  background-size: 100% 1px, 100% 1px;
  background-position: 0 0, 0 1px;
  background-repeat: no-repeat;
}}
.readout .k {{
  font-size: 0.76rem;
  font-weight: 500;
  letter-spacing: 0.24em;
  background-image: linear-gradient(180deg, var(--dim-a), var(--dim-b));
}}
.readout .v {{
  margin-top: 0.5rem;
  font-size: clamp(1.02rem, 1.5vw, 1.15rem);
  line-height: 1.75;
  background-image: linear-gradient(150deg, var(--text-a), var(--text-b));
}}
.readout .v b {{ font-weight: 500; -webkit-text-fill-color: var(--sky-text); color: var(--sky-text); }}
.readout .v b.acc {{ -webkit-text-fill-color: var(--brass-text); color: var(--brass-text); }}

/* 스위치 */
[class*="st-key-log-"] label p {{ font-family: var(--ui); color: var(--body-a); font-size: 0.95rem; }}
[class*="st-key-log-"] label > div:first-child {{ box-shadow: var(--inset-sm); }}

[class*="st-key-band-"] {{ padding-bottom: clamp(5rem, 12vh, 8.5rem); }}

/* 푸터 */
.foot {{
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: var(--gap-2);
  flex-wrap: wrap;
  padding-top: 2.6rem;
}}
.foot-name {{
  font-weight: 500;
  letter-spacing: 0.03em;
  background-image: linear-gradient(110deg, var(--text-b), var(--dim-a));
}}

@media (max-width: 720px) {{
  .band-head {{ grid-template-columns: minmax(0, 1fr); }}
  .band-head > *:not(.index) {{ grid-column: 1; }}
  .index {{ padding-top: 0; }}
}}
</style>
""",
        unsafe_allow_html=True,
    )


def html(markup):
    st.markdown(markup, unsafe_allow_html=True)


def stair(even=False):
    html(f'<div class="stair{" even" if even else ""}" aria-hidden="true"><span></span><span></span><span></span></div>')


def band_head(no, title, lede, cap_title, cap_note):
    stair(even=int(no) % 2 == 0)
    html(
        f"""
<div class="band-head">
  <p class="fx index">{no}</p>
  <h2 class="fx head">{title}</h2>
  <p class="fx lede">{lede}</p>
</div>
<div class="cap">
  <span class="fx c-title">{cap_title}</span>
  <span class="fx c-note">{cap_note}</span>
</div>
"""
    )


def insight(key, suggestion):
    """이 그래프로 알 수 있는 것 — 데이터에서 뽑은 문장을 채워 두고, 직접 고쳐 쓸 수 있다."""
    html('<div class="insight"><p class="fx insight-label">이 그래프로 알 수 있는 것</p></div>')
    st.text_area(
        "이 그래프로 알 수 있는 것",
        value=suggestion,
        key=f"note-{key}",
        label_visibility="collapsed",
        placeholder="이곳에 한 문장을 적어 주세요.",
        height="content",
    )


def chart(fig, key):
    with st.container(key=f"well-{key}"):
        st.plotly_chart(fig, theme=None, width="stretch", config={"displayModeBar": False})


# ---------------------------------------------------------------- 데이터
@st.cache_data(show_spinner="데이터를 불러오는 중…")
def load_data(url):
    df = pd.read_csv(url, dtype={"movieCd": str, "openDt": str})
    # 세로막대(|)로 여러 장르가 적힌 영화는 첫 번째 장르만 쓴다
    df["genre"] = df["genre"].astype(str).str.split("|").str[0].str.strip()
    df["openDt"] = pd.to_datetime(df["openDt"], format="%Y%m%d", errors="coerce")
    return df


def blend(c1, c2, r):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * r):02x}" for x, y in zip(a, b))


def genre_colors(df, t):
    """편수 상위 장르는 고유 색, 나머지 작은 장르는 무채색 단계."""
    order = df["genre"].value_counts().index.tolist()
    hues = SERIES
    small = order[len(hues):]
    colors = {g: hues[i] for i, g in enumerate(order[: len(hues)])}
    for i, g in enumerate(small):
        colors[g] = blend(t["other-hi"], t["other-lo"], i / max(len(small) - 1, 1))
    return order, colors


def man(n):
    """사람 수를 '만 명' 단위로 짧게."""
    if n >= 10_000:
        v = n / 10_000
        return f"{v:,.0f}만" if v >= 10 or v == int(v) else f"{v:,.1f}만"
    return f"{n:,.0f}"


def josa(word, pair):
    """받침에 맞는 조사: josa('드라마', '이가') -> '가'."""
    ch = word.rstrip(")")[-1]
    code = ord(ch) - 0xAC00
    has_final = 0 <= code <= 11171 and code % 28 != 0
    return pair[0] if has_final else pair[1]


def base_layout(t, height):
    font = "Pretendard Variable, Pretendard, sans-serif"
    return dict(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=font, color=t["body-a"], size=13),
        hoverlabel=dict(
            bgcolor=t["surface"], bordercolor=t["surface"],
            font=dict(family=font, color=t["text-a"], size=14),
        ),
        legend=dict(
            orientation="h", x=0.5, xanchor="center", y=-0.02, yanchor="top",
            bgcolor="rgba(0,0,0,0)", font=dict(color=t["body-a"], size=13),
        ),
    )


def axis(t, **kw):
    return dict(
        showgrid=False, zeroline=False, showline=False,
        tickfont=dict(color=t["dim-a"], size=12), title_font=dict(color=t["body-b"], size=13),
        **kw,
    )


# ---------------------------------------------------------------- 01 장르 도넛
def genre_donut(df, t, order, colors):
    """편수가 가장 많은 장르가 가장 높은 단, 그다음 장르가 한 단 아래 — 순위마다 한 단씩 내려간다."""
    counts = df["genre"].value_counts().reindex(order)
    total, n = counts.sum(), len(counts)
    hole, top_h, low_h = 1.0, 0.95, 0.30  # 안쪽 반지름, 가장 높은 단과 가장 낮은 단의 두께
    step = (top_h - low_h) / max(n - 1, 1)

    slices, start = [], 0.0
    for rank, (g, c) in enumerate(counts.items()):
        span = c / total * 360
        slices.append((rank, g, c, start + span / 2, span))
        start += span

    fig = go.Figure()
    # 낮은 단부터 쌓아 올린다 — 높은 단이 나중에 그려져 이웃 위에 얹히고 그늘을 드리운다
    for rank, g, c, mid, span in reversed(slices):
        fig.add_trace(
            go.Barpolar(
                name=g,
                r=[top_h - step * rank],
                base=[hole],
                theta=[mid],
                width=[span],
                marker=dict(color=colors[g], line=dict(width=0)),
                customdata=[[c, c / total, rank + 1]],
                hovertemplate=f"<b>{g}</b><br>%{{customdata[0]}}편 · %{{customdata[1]:.1%}}<extra></extra>",
            )
        )

    fig.add_annotation(
        text=f"<span style='font-size:42px;color:{t['text-a']}'>{total}</span>"
        f"<span style='font-size:16px;color:{t['body-b']}'> 편</span>"
        f"<br><span style='font-size:12px;letter-spacing:3px;color:{t['dim-a']}'>{n}개 장르</span>",
        x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False,
    )
    fig.update_layout(
        **base_layout(t, 580),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            hole=0,
            radialaxis=dict(visible=False, range=[0, hole + top_h + 0.08]),
            angularaxis=dict(visible=False, rotation=90, direction="clockwise"),
        ),
        bargap=0,
    )
    fig.update_layout(legend=dict(traceorder="reversed"))
    return fig


def donut_depth_css(n):
    """조각마다 높이에 맞는 그늘 — 높은 단일수록 그늘이 길고 짙다.
    trace는 낮은 단부터 그려지므로 nth-child(1)이 가장 낮은 단이다."""
    rules = []
    for i in range(n):
        h = i / max(n - 1, 1)  # 0 가장 낮은 단 → 1 가장 높은 단
        y, blur, a = 1.5 + 9 * h, 2 + 10 * h, 0.35 + 0.4 * h
        rules.append(
            f".st-key-well-genre .barlayer .trace:nth-child({i + 1}) {{"
            f" filter: drop-shadow(0 -1px 0 rgba(255,255,255,{0.05 + 0.1 * h:.3f}))"
            f" drop-shadow(0 {y:.1f}px {blur:.1f}px rgba(0,0,0,{a:.2f})); }}"
        )
    return "<style>" + "\n".join(rules) + "</style>"


# ---------------------------------------------------------------- 02 트리맵
def genre_treemap(df, t, order, colors):
    ids, labels, parents, values, fills, hover = [], [], [], [], [], []
    by_genre = df.groupby("genre")["total_audi"].sum()
    for g in order:
        ids.append(f"g/{g}")
        labels.append(g)
        parents.append("")
        values.append(int(by_genre[g]))
        fills.append(colors[g])
        hover.append(f"<b>{g}</b><br>총 관객 {by_genre[g]:,.0f}명")
        for _, m in df[df["genre"] == g].iterrows():
            ids.append(f"m/{m['movieCd']}")
            labels.append(m["movieNm"])
            parents.append(f"g/{g}")
            values.append(int(m["total_audi"]))
            fills.append(colors[g])
            hover.append(f"<b>{m['movieNm']}</b><br>총 관객 {m['total_audi']:,.0f}명")

    fig = go.Figure(
        go.Treemap(
            ids=ids, labels=labels, parents=parents, values=values,
            branchvalues="total",
            marker=dict(colors=fills, line=dict(width=0), pad=dict(t=26, l=4, r=4, b=4)),
            customdata=hover,
            hovertemplate="%{customdata}<extra></extra>",
            texttemplate="%{label}",
            textfont=dict(family="Pretendard Variable, Pretendard, sans-serif", size=14),
            pathbar=dict(visible=False),
            tiling=dict(packing="squarify", pad=4),
            root=dict(color="rgba(0,0,0,0)"),
            sort=True,
        )
    )
    layout = base_layout(t, 620)
    layout["margin"] = dict(l=0, r=0, t=0, b=0)
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------- 03 히스토그램
def nice_width(max_value, max_bins=40):
    for w in (10_000, 20_000, 50_000, 100_000, 200_000, 250_000, 500_000, 1_000_000, 2_000_000, 5_000_000):
        if max_value / w <= max_bins:
            return w
    return 10_000_000


def audience_hist(df, t):
    audi = df["total_audi"]
    width = nice_width(audi.max())
    edges = np.arange(0, audi.max() + width, width)
    counts, edges = np.histogram(audi, bins=edges)
    peak = int(counts.argmax())
    blue, orange = t["sky"], t["brass"]

    fig = go.Figure(
        go.Bar(
            x=(edges[:-1] + edges[1:]) / 2,
            y=counts,
            width=width * 0.86,
            marker=dict(
                color=[orange if i == peak else blue for i in range(len(counts))],
                cornerradius=4,
            ),
            customdata=[
                [f"{man(a)} – {man(b)}명", c / len(audi)] for a, b, c in zip(edges[:-1], edges[1:], counts)
            ],
            hovertemplate="<b>%{customdata[0]}</b><br>%{y}편 · %{customdata[1]:.1%}<extra></extra>",
        )
    )
    tick = nice_width(audi.max(), 8)
    ticks = np.arange(0, edges[-1] + 1, tick)
    fig.update_layout(
        **base_layout(t, 420),
        showlegend=False,
        bargap=0,
        xaxis=axis(t, title="총 관객 (명)", tickvals=ticks, ticktext=[man(v) for v in ticks]),
        yaxis=axis(t, title="영화 편수"),
    )
    fig.update_layout(margin=dict(l=64, r=16, t=16, b=56))

    lo, hi = edges[peak], edges[peak + 1]
    top = df.loc[audi.idxmax()]
    return fig, dict(
        range=f"{man(lo)} – {man(hi)}명", n=int(counts[peak]), share=counts[peak] / len(audi),
        top_name=top["movieNm"], top_audi=int(top["total_audi"]),
    )


# ---------------------------------------------------------------- 04 산점도
def screen_scatter(df, t, order, colors, log):
    fig = go.Figure()
    for g in order:
        d = df[df["genre"] == g]
        fig.add_trace(
            go.Scatter(
                x=d["first_scrn"], y=d["total_audi"], mode="markers", name=g,
                marker=dict(size=10, color=colors[g], opacity=0.92, line=dict(width=0)),
                customdata=np.stack([d["movieNm"], d["genre"]], axis=-1),
                hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}"
                "<br>개봉일 스크린 %{x:,}개 · 총 관객 %{y:,}명<extra></extra>",
            )
        )
    kind = "log" if log else "linear"
    fig.update_layout(
        **base_layout(t, 560),
        xaxis=axis(t, title="개봉일 스크린 수 (개)", type=kind),
        yaxis=axis(t, title="총 관객 (명)", type=kind, tickformat="~s" if log else ",d"),
    )
    fig.update_layout(margin=dict(l=64, r=16, t=16, b=10), legend=dict(y=-0.16))
    return fig


# ---------------------------------------------------------------- 05 애니메이션 누적 관객
# 자료 페이지의 면적 그래프를 그대로 옮긴다 — 면(plateau) + 능선의 빛·그늘 + 세 단의 계단(step-face),
# 능선 색은 왼쪽 하늘색에서 오른쪽 황동색으로 옮겨 간다. Plotly로는 겹 구조를 못 그려 SVG로 직접 그린다.
ANIM_CSS = """
<style>
.area-well { background: var(--well); border-radius: var(--radius); box-shadow: var(--inset); overflow: hidden; }
.c-area { display: block; width: 100%; height: auto; overflow: hidden; }
.c-area .face { filter: url(#a-chroma); }
.c-area .ridge { fill: none; stroke-width: 2.4; stroke-linejoin: round; stroke-linecap: round; }
.c-area .ridge-lit { fill: none; stroke: rgba(255, 255, 255, 0.4); stroke-width: 1.8; stroke-linejoin: round; transform: translateY(-1.7px); }
.c-area .ridge-shade { fill: none; stroke: rgba(0, 0, 0, 0.75); stroke-width: 8; stroke-linejoin: round; transform: translate(2px, 6px); filter: blur(4.5px); }
.c-area .step-face { fill: #2a3037; }
.c-area .step-face.step-c { fill: #252a31; }
.c-area .step-lit { fill: none; stroke: rgba(255, 255, 255, 0.4); stroke-width: 1.1; opacity: 0.3; transform: translateY(-1.4px); }
.c-area .step-edge { fill: none; stroke: #474f59; stroke-width: 1.4; stroke-linejoin: round; }
.c-area .step-shade { fill: none; stroke: rgba(0, 0, 0, 0.75); stroke-width: 6; opacity: 0.5; transform: translate(1.5px, 4px); filter: blur(4px); }
.c-area .ridge-mark { fill: none; stroke-width: 2.6; stroke-linecap: round; }
.c-area text { font-family: var(--ui); }
.c-area .v-tag { font-size: 30px; font-weight: 300; letter-spacing: 0.14em; fill: rgba(255, 255, 255, 0.08); }
.c-area .v-axis { font-size: 13px; letter-spacing: 0.2em; fill: var(--dim-b); }
.c-area .v-peak { font-size: 19px; font-weight: 500; letter-spacing: 0.04em; fill: var(--brass-text); }
.c-area .v-jump { font-size: 14px; font-weight: 500; letter-spacing: 0.04em; fill: var(--brass-text); }
.c-area .dot { filter: drop-shadow(0 -1px 0 rgba(255,255,255,0.12)) drop-shadow(0 2px 3px rgba(0,0,0,0.6)); }
.c-area .dot-peak { fill: var(--brass); filter: drop-shadow(0 0 7px var(--brass-glow)); }
.c-area .hit { fill: transparent; cursor: pointer; }
.c-area .tip { opacity: 0; pointer-events: none; transition: opacity 0.2s var(--ease); }
.c-area .pt:hover .tip { opacity: 1; }
.c-area .pt:hover .dot { transform-box: fill-box; transform-origin: center; transform: scale(1.5); }
.c-area .tip rect { fill: var(--surface); filter: drop-shadow(0 -1px 0 rgba(255,255,255,0.06)) drop-shadow(0 8px 14px rgba(0,0,0,0.55)); }
.c-area .tip .t1 { font-size: 15px; font-weight: 500; fill: var(--text-a); }
.c-area .tip .t2 { font-size: 13px; fill: var(--body-a); }
.c-area .tip .t3 { font-size: 13px; fill: var(--sky-text); }
@media (max-width: 720px) {
  .c-area .v-axis { font-size: 24px; letter-spacing: 0.1em; }
  .c-area .v-peak { font-size: 30px; }
  .c-area .v-jump { font-size: 22px; }
}
</style>
"""


def hex_mix(stops, r):
    """여러 색 사이를 r(0~1)로 옮겨 간다."""
    r = min(max(r, 0.0), 1.0) * (len(stops) - 1)
    i = min(int(r), len(stops) - 2)
    return blend(stops[i], stops[i + 1], r - i)


def animation_svg(df, t, genre="애니메이션"):
    d = df[df["genre"] == genre].sort_values(["openDt", "total_audi"]).reset_index(drop=True)
    d["cum"] = d["total_audi"].cumsum()
    jump = int(d["total_audi"].idxmax())

    W, H, left, right = 1000, 340, 24, 976
    y0, y1 = 292, 58  # 0명과 최댓값이 놓이는 높이
    start = d["openDt"].min() - pd.Timedelta(days=6)
    end = d["openDt"].max() + pd.Timedelta(days=6)
    span = (end - start).days
    X = lambda dt: left + (right - left) * (dt - start).days / span
    peak = d["cum"].iloc[-1]
    Y = lambda v: y0 - (y0 - y1) * v / peak

    # 능선 — 개봉일마다 그 영화의 관객만큼 한 단 올라가는 계단
    pts = [(-12.0, Y(0))]
    vertex = []
    for _, m in d.iterrows():
        x = X(m["openDt"])
        pts.append((x, pts[-1][1]))
        pts.append((x, Y(m["cum"])))
        vertex.append((x, Y(m["cum"])))
    pts.append((W + 12.0, pts[-1][1]))

    def off_b(x):  # 계단 사이 간격은 물결처럼 어긋난다
        return 20 + 7 * np.sin(x / 150 + 0.6)

    def off_c(x):
        return off_b(x) + 18 + 6 * np.sin(x / 110 + 1.9)

    def line(points):
        return "M " + " L ".join(f"{x:.1f} {min(y, H + 12):.1f}" for x, y in points)

    def closed(points):
        return line(points) + f" L {W + 12} {H + 12} L -12 {H + 12} Z"

    ridge = pts
    step_b = [(x, y + off_b(x)) for x, y in pts]
    step_c = [(x, y + off_c(x)) for x, y in pts]

    # 마디 — 가장 크게 오른 계단 한 칸을 같은 계열의 낮은 명도로 짚는다
    seg_len = [0.0] + [abs(x2 - x1) + abs(y2 - y1) for (x1, y1), (x2, y2) in zip(pts, pts[1:])]
    cum_len = np.cumsum(seg_len)
    total_len = cum_len[-1]
    j = 2 + 2 * jump  # 그 영화의 세로 한 칸이 끝나는 점
    mark_from, mark_to = cum_len[j - 2], cum_len[min(j + 1, len(cum_len) - 1)]

    ridge_d = line(ridge)
    parts = [
        f'<path class="face" fill="url(#a-plateau)" d="{closed(ridge)}" />',
        f'<path class="ridge-shade" d="{ridge_d}" />',
        f'<path class="ridge-lit" d="{ridge_d}" />',
    ]
    for cls, pts_ in (("step-b", step_b), ("step-c", step_c)):
        ld = line(pts_)
        parts += [
            f'<path class="step-face {cls}" d="{closed(pts_)}" />',
            f'<path class="step-shade" d="{ld}" />',
            f'<path class="step-edge" d="{ld}" />',
            f'<path class="step-lit" d="{ld}" />',
        ]
    parts += [
        f'<path class="ridge" stroke="url(#a-ridge)" d="{ridge_d}" />',
        f'<path class="ridge-mark" stroke="url(#a-deep)" pathLength="{total_len:.1f}" '
        f'stroke-dasharray="{mark_to - mark_from:.1f} 99999" stroke-dashoffset="{-mark_from:.1f}" d="{ridge_d}" />',
    ]

    # 눈금 — 두 달마다
    months = pd.date_range(start.normalize().replace(day=1), end, freq="MS")
    for i, mth in enumerate(months):
        if mth < start or i % 2:
            continue
        label = f"{mth:%Y.%m}" if (i == 0 or mth.month == 1) else f"{mth.month}월"
        parts.append(f'<text class="v-axis" x="{X(mth):.1f}" y="324" text-anchor="middle">{label}</text>')
    parts.append(f'<text class="v-tag" x="{right - 12}" y="324" text-anchor="end">ANIMATION</text>')
    parts.append(f'<text class="v-peak" x="{right - 6}" y="{Y(peak) - 16:.1f}" text-anchor="end">{man(peak)}명</text>')
    jx, jy = vertex[jump]
    top = d.loc[jump]
    parts.append(
        f'<text class="v-jump" x="{jx - 12:.1f}" y="{jy - 12:.1f}" text-anchor="end">'
        f'{htmlib.escape(top["movieNm"])} +{man(top["total_audi"])}명</text>'
    )

    # 점 — 위치에 따라 하늘색에서 황동색으로. 마우스를 올리면 영화명과 누적 관객
    stops = [t["sky"], "#99a4b1", t["brass"]]
    for i, ((x, y), (_, m)) in enumerate(zip(vertex, d.iterrows())):
        is_peak = i == jump
        dot = (
            f'<circle class="dot dot-peak" cx="{x:.1f}" cy="{y:.1f}" r="6.5" />'
            if is_peak
            else f'<circle class="dot" cx="{x:.1f}" cy="{y:.1f}" r="3.6" fill="{hex_mix(stops, (x - left) / (right - left))}" />'
        )
        name = htmlib.escape(m["movieNm"])
        lines = [
            (name, "t1"),
            (f'{m["openDt"]:%Y.%m.%d} 개봉 · 관객 {m["total_audi"]:,}명', "t2"),
            (f'누적 {m["cum"]:,}명', "t3"),
        ]
        tw = max(len(m["movieNm"]) * 15 + 32, 250)
        th = 86
        tx = min(max(x - tw / 2, 6), W - tw - 6)
        ty = y - th - 16 if y - th - 16 > 4 else y + 16
        tip = f'<g class="tip"><rect x="{tx:.1f}" y="{ty:.1f}" width="{tw}" height="{th}" rx="12" />' + "".join(
            f'<text class="{c}" x="{tx + 16:.1f}" y="{ty + 26 + k * 24:.1f}">{txt}</text>'
            for k, (txt, c) in enumerate(lines)
        ) + "</g>"
        parts.append(f'<g class="pt"><circle class="hit" cx="{x:.1f}" cy="{y:.1f}" r="13" />{dot}{tip}</g>')

    defs = f"""
<defs>
  <linearGradient id="a-plateau" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#2f353c" /><stop offset="62%" stop-color="#2f353c" /><stop offset="100%" stop-color="#1d2024" />
  </linearGradient>
  <linearGradient id="a-ridge" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#6f9dbb" /><stop offset="52%" stop-color="#99a4b1" /><stop offset="100%" stop-color="#c49c5f" />
  </linearGradient>
  <linearGradient id="a-deep" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#47738f" /><stop offset="52%" stop-color="#6d7784" /><stop offset="100%" stop-color="#90703f" />
  </linearGradient>
  <filter id="a-chroma" x="-8%" y="-30%" width="116%" height="160%" color-interpolation-filters="sRGB">
    <feOffset in="SourceGraphic" dx="-1.1" dy="-0.5" result="s1" />
    <feColorMatrix in="s1" type="matrix" result="c1" values="0 0 0 0 0.35  0 0 0 0 0.74  0 0 0 0 0.95  0 0 0 0.34 0" />
    <feOffset in="SourceGraphic" dx="1.1" dy="0.5" result="s2" />
    <feColorMatrix in="s2" type="matrix" result="c2" values="0 0 0 0 0.84  0 0 0 0 0.64  0 0 0 0 0.28  0 0 0 0.34 0" />
    <feMerge><feMergeNode in="c1" /><feMergeNode in="c2" /><feMergeNode in="SourceGraphic" /></feMerge>
  </filter>
</defs>"""
    svg = (
        f'<div class="area-well"><svg class="c-area" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="{genre} 누적 관객, {len(d)}편, 총 {man(peak)}명">{defs}{"".join(parts)}</svg></div>'
    )
    return svg, d, top


# ---------------------------------------------------------------- 화면
tokens = TOKENS
inject_css(tokens)

html('<p class="fx mark">영화 데이터 그래프 도감<span class="mark-sub">KOBIS · BOX OFFICE TOP 10</span></p>')

try:
    movies = load_data(DATA_URL)
except Exception as err:  # 네트워크 오류 등
    st.error(f"데이터를 불러오지 못했습니다: {err}")
    st.stop()

order, colors = genre_colors(movies, tokens)
first, last = movies["openDt"].min(), movies["openDt"].max()
html(
    f"""
<section class="hero">
  <p class="fx eyebrow">그래프 도감 &middot; 2</p>
  <h1 class="fx display"><span class="line">영화 데이터 그래프 도감 2</span><span class="line">- 분포와 관계</span></h1>
  <p class="fx lede">1년간 박스오피스 10위권에 든 영화 가운데 이 기간에 개봉한
  {len(movies)}편의 요약표입니다.</p>
  <p class="fx meta"><b>{len(movies)}</b>편 &middot; 개봉 {first:%Y.%m.%d} – {last:%Y.%m.%d}</p>
</section>
"""
)

# 01 — 장르별 영화 편수
counts = movies["genre"].value_counts()
with st.container(key="band-genre"):
    band_head(
        "01", "장르별 영화 편수",
        "여러 장르가 적힌 영화는 첫 번째 장르로 셉니다. 비율이 클수록 조각이 더 높이 올라와 있고, "
        "조각에 마우스를 올리면 편수와 비율이 보입니다.",
        "장르 분포", "도넛 · 편수 기준",
    )
    html(donut_depth_css(len(order)))
    chart(genre_donut(movies, tokens, order, colors), "genre")
    g1, g2 = counts.index[0], counts.index[1]
    insight(
        "genre",
        f"{g1}({counts.iloc[0]}편){josa(g1, '과와')} {g2}({counts.iloc[1]}편){josa(g2, '이가')} 전체 {counts.sum()}편 중 "
        f"{(counts.iloc[0] + counts.iloc[1]) / counts.sum():.0%}를 차지해, 두 장르가 박스오피스 10위권 영화의 절반을 넘습니다.",
    )

# 02 — 장르 안의 영화 (트리맵)
by_genre = movies.groupby("genre")["total_audi"].sum().sort_values(ascending=False)
top_movie = movies.loc[movies["total_audi"].idxmax()]
with st.container(key="band-tree"):
    band_head(
        "02", "장르 안의 영화",
        "큰 칸은 장르, 그 안의 작은 칸은 영화 한 편입니다. 칸의 크기는 총 관객 수이고, "
        "칸에 마우스를 올리면 영화명과 총 관객이 보입니다.",
        "관객으로 본 장르", "트리맵 · 총 관객 기준",
    )
    chart(genre_treemap(movies, tokens, order, colors), "tree")
    big = by_genre.index[0]
    lead = (
        f"{big}{josa(big, '은는')} 편수와 관객 수 모두 1위로, 전체 관객의 {by_genre.iloc[0] / by_genre.sum():.0%}를 차지하지만"
        if big == counts.index[0]
        else f"편수는 {counts.index[0]}{josa(counts.index[0], '이가')} 가장 많지만 관객 수로는 "
        f"{big}{josa(big, '이가')} {by_genre.iloc[0] / by_genre.sum():.0%}로 가장 크고"
    )
    insight(
        "tree",
        f"{lead}, 영화 한 편으로는 {top_movie['genre']} 장르의 '{top_movie['movieNm']}'가 가장 큰 칸입니다.",
    )

# 03 — 총 관객 히스토그램
fig_hist, h = audience_hist(movies, tokens)
with st.container(key="band-hist"):
    band_head(
        "03", "총 관객의 분포",
        "총 관객 수를 같은 너비의 구간으로 나누고, 구간마다 영화가 몇 편인지 세었습니다. "
        "영화가 가장 많이 몰린 구간만 다른 색입니다.",
        "총 관객 히스토그램", f"구간 너비 {man(nice_width(movies['total_audi'].max()))}명",
    )
    chart(fig_hist, "hist")
    html(
        f"""
<div class="readout">
  <div>
    <p class="fx k">영화가 몰린 구간</p>
    <p class="fx v">대부분의 영화는 <b class="acc">{h['range']}</b> 구간에 몰려 있습니다.
    {len(movies)}편 가운데 {h['n']}편({h['share']:.1%})입니다.</p>
  </div>
  <div>
    <p class="fx k">가장 관객이 많은 영화</p>
    <p class="fx v">가장 관객이 많은 영화는 <b>{h['top_name']}</b>{josa(h['top_name'], ['으로', '로'])},
    총 {h['top_audi']:,}명이 보았습니다.</p>
  </div>
</div>
"""
    )
    median = movies["total_audi"].median()
    insight(
        "hist",
        f"총 관객은 한쪽으로 크게 치우쳐 있어, 절반의 영화는 {man(median)}명을 넘지 못하지만 "
        f"'{h['top_name']}' 같은 몇 편이 수백만 명 이상을 모읍니다.",
    )

# 04 — 스크린 수와 총 관객 (산점도)
with st.container(key="band-scatter"):
    band_head(
        "04", "스크린 수와 총 관객",
        "점 하나가 영화 한 편입니다. 가로는 개봉일 스크린 수, 세로는 총 관객이며 점의 색은 장르입니다. "
        "점에 마우스를 올리면 영화명이 보이고, 범례를 누르면 장르를 켜고 끌 수 있습니다.",
        "스크린 수 × 총 관객", "산점도 · 장르별 색",
    )
    log = st.toggle("로그 눈금으로 보기", value=True, key="log-scatter")
    chart(screen_scatter(movies, tokens, order, colors, log), "scatter")
    def log_r(d):
        return np.corrcoef(np.log10(d["first_scrn"].clip(lower=1)), np.log10(d["total_audi"].clip(lower=1)))[0, 1]

    wide = movies[movies["first_scrn"] >= 100]
    insight(
        "scatter",
        f"전체로 보면 관계가 약하지만(로그 눈금 상관계수 {log_r(movies):.2f}), 개봉일 스크린이 100개 이상인 "
        f"{len(wide)}편만 보면 스크린이 많을수록 총 관객도 많은 뚜렷한 경향({log_r(wide):.2f})이 있고, "
        f"'{top_movie['movieNm']}'처럼 적은 스크린({top_movie['first_scrn']}개)으로 시작해 크게 흥행한 영화도 있습니다.",
    )

# 05 — 애니메이션 누적 관객
anim_svg, anim, anim_top = animation_svg(movies, tokens)
with st.container(key="band-anim"):
    band_head(
        "05", "애니메이션 누적 관객",
        "애니메이션 영화의 총 관객을 개봉일 순서대로 더해 갔습니다. 계단 한 칸이 영화 한 편이고, "
        "점에 마우스를 올리면 영화명과 그때까지의 누적 관객이 보입니다.",
        "누적 관객 증가", f"애니메이션 {len(anim)}편 · 개봉일 순",
    )
    html(ANIM_CSS)
    html(anim_svg)
    cum_total = int(anim["cum"].iloc[-1])
    insight(
        "anim",
        f"애니메이션 {len(anim)}편의 누적 관객은 {man(cum_total)}명이며, 그중 "
        f"'{anim_top['movieNm']}' 한 편({anim_top['openDt']:%Y.%m.%d} 개봉)이 "
        f"{anim_top['total_audi'] / cum_total:.0%}를 차지해 누적 곡선이 그 시점에 가장 크게 뛰어오릅니다.",
    )

stair(even=True)
html(
    """
<footer class="foot">
  <p class="fx foot-name">영화 데이터 그래프 도감 2 &middot; 분포와 관계</p>
  <p class="fx meta">자료 KOBIS 박스오피스</p>
</footer>
"""
)
