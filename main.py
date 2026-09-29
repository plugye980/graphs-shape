"""영화 데이터 그래프 도감 2 — 분포와 관계

디자인: '형태 없는 결'
- 바탕은 무채색, 색(하늘색·황동색)은 읽어야 할 한 점에만
- 테두리 없음. 구분이 필요한 곳은 한 단 올리거나(raise) 내려서(inset) 가른다
- 빛은 언제나 위에서 온다
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

TITLE = "영화 데이터 그래프 도감 2 - 분포와 관계"
DATA_URL = "https://raw.githubusercontent.com/happykth/data/main/kobis_movies.csv"

st.set_page_config(page_title=TITLE, layout="wide")


# ---------------------------------------------------------------- 색 토큰
TOKENS = {
    "dark": {
        "page-a": "#1b1d21", "page-b": "#212429", "page-c": "#262a30",
        "surface": "#25282d", "well": "#1c1f23", "well-2": "#202327",
        "text-a": "#eef0f3", "text-b": "#c5cad1",
        "body-a": "#b4bac2", "body-b": "#949aa3",
        "dim-a": "#7c828c", "dim-b": "#5b616a",
        "sky": "#7bb9de", "sky-b": "#5e93b9", "sky-soft": "rgba(123, 185, 222, 0.22)",
        "sky-text": "#8cc7e8", "sky-text-b": "#6ba8cc",
        "brass": "#d3a869", "brass-text": "#e0b878", "brass-text-b": "#bd9557",
        "brass-glow": "rgba(211, 168, 105, 0.5)",
        "hi": "rgba(255, 255, 255, 0.055)", "lo": "rgba(0, 0, 0, 0.55)",
        "lo-strong": "rgba(0, 0, 0, 0.7)",
        "inset-lo": "rgba(0, 0, 0, 0.34)", "edge-lo": "rgba(0, 0, 0, 0.45)",
        "wash-1": "rgba(120, 165, 205, 0.055)", "wash-2": "rgba(200, 165, 105, 0.03)",
        "tag": "rgba(255, 255, 255, 0.08)",
        "grid": "rgba(255, 255, 255, 0.06)",
        # 작은 장르(기타) — 무채색 단계
        "other-hi": "#7d8591", "other-lo": "#4a5059",
    },
    "light": {
        "page-a": "#f5fbff", "page-b": "#fbfeff", "page-c": "#eff7fe",
        "surface": "#fafeff", "well": "#ffffff", "well-2": "#f2f6fb",
        "text-a": "#2b3945", "text-b": "#42525f",
        "body-a": "#53616c", "body-b": "#6c7a86",
        "dim-a": "#8ea6b6", "dim-b": "#adc1d1",
        "sky": "#3fa3d6", "sky-b": "#2b86b8", "sky-soft": "rgba(63, 163, 214, 0.18)",
        "sky-text": "#217aa8", "sky-text-b": "#175d84",
        "brass": "#c08f39", "brass-text": "#8d6a22", "brass-text-b": "#6f521a",
        "brass-glow": "rgba(192, 143, 57, 0.46)",
        "hi": "rgba(255, 255, 255, 1)", "lo": "rgba(124, 164, 204, 0.24)",
        "lo-strong": "rgba(110, 152, 194, 0.34)",
        "inset-lo": "rgba(116, 152, 192, 0.32)", "edge-lo": "rgba(112, 150, 192, 0.42)",
        "wash-1": "rgba(115, 170, 210, 0.075)", "wash-2": "rgba(185, 150, 90, 0.035)",
        "tag": "rgba(66, 104, 140, 0.14)",
        "grid": "rgba(66, 104, 140, 0.10)",
        "other-hi": "#8a9aa6", "other-lo": "#c3ced7",
    },
}

# 장르 색 — 편수가 많은 순서로 고정된 자리에 앉는다(순위가 아니라 장르를 따른다).
# 색각 이상 시뮬레이션·명도 대역·대비를 검사기로 확인한 조합
SERIES = {
    "dark": ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9"],
    "light": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7"],
}


def pick_theme():
    if "theme" not in st.session_state:
        system = getattr(getattr(st.context, "theme", None), "type", None)
        st.session_state.theme = "LIGHT" if system == "light" else "DARK"
    return st.session_state.theme.lower()


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
[class*="st-key-well-"] .barlayer path,
[class*="st-key-well-"] .slice path.surface {{
  filter: drop-shadow(0 -1px 0 var(--hi)) drop-shadow(0 4px 6px var(--lo));
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
  padding: 1rem 1.2rem !important;
}}
[class*="st-key-note-"] textarea::placeholder {{ color: var(--dim-a); -webkit-text-fill-color: var(--dim-a); }}
[class*="st-key-note-"] [data-testid="stTextAreaRootElement"]:focus-within {{
  box-shadow: var(--inset-sm), 0 0 0 3px var(--sky-soft);
}}
[class*="st-key-note-"] [data-testid="InputInstructions"] {{ display: none; }}
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

/* 분할 선택(테마) — 바탕은 올라오고, 고른 칸만 내려간다 */
.st-key-theme {{ margin-left: auto; }}
.st-key-theme [role="radiogroup"] {{
  gap: 0;
  padding: 5px;
  border-radius: 999px;
  background: var(--surface);
  box-shadow: var(--raise);
  width: fit-content;
  margin-left: auto;
}}
.st-key-theme button {{
  border: 0 !important;
  border-radius: 999px !important;
  background: transparent !important;
  box-shadow: none !important;
  min-height: 0;
  padding: 0.45rem 1.1rem;
  transition: color 0.45s var(--ease), box-shadow 0.45s var(--ease);
}}
.st-key-theme button p {{
  font-family: var(--ui);
  font-size: 0.76rem;
  font-weight: 500;
  letter-spacing: 0.18em;
  color: var(--dim-a);
}}
.st-key-theme button:hover p {{ color: var(--body-a); }}
.st-key-theme button[aria-checked="true"] {{
  background: var(--well) !important;
  box-shadow: var(--inset-sm) !important;
}}
.st-key-theme button[aria-checked="true"] p {{ color: var(--text-a); }}

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
        height=140,
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


def genre_colors(df, theme, t):
    """편수 상위 장르는 고유 색, 나머지 작은 장르는 무채색 단계."""
    order = df["genre"].value_counts().index.tolist()
    hues = SERIES[theme]
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
        gridcolor=t["grid"], zeroline=False, showline=False,
        tickfont=dict(color=t["dim-a"], size=12), title_font=dict(color=t["body-b"], size=13),
        **kw,
    )


# ---------------------------------------------------------------- 01 장르 도넛
def tier_of(share):
    """면적(비율)이 클수록 한 단 더 올라온다 — 4단."""
    return 4 if share >= 0.20 else 3 if share >= 0.07 else 2 if share >= 0.03 else 1


def genre_donut(df, t, order, colors):
    counts = df["genre"].value_counts().reindex(order)
    total = counts.sum()
    hole, step = 1.0, 0.16  # 안쪽 반지름과 한 단의 높이

    fig = go.Figure()
    start = 0.0
    for g, c in counts.items():
        share = c / total
        span = share * 360
        tier = tier_of(share)
        fig.add_trace(
            go.Barpolar(
                name=g,
                r=[0.34 + step * tier],
                base=[hole],
                theta=[start + span / 2],
                width=[span],
                marker=dict(color=colors[g], line=dict(color=t["well"], width=2.5)),
                customdata=[[c, share, tier]],
                hovertemplate=f"<b>{g}</b><br>%{{customdata[0]}}편 · %{{customdata[1]:.1%}}<extra></extra>",
            )
        )
        start += span

    top = hole + 0.34 + step * 4
    fig.add_annotation(
        text=f"<span style='font-size:42px;color:{t['text-a']}'>{total}</span>"
        f"<span style='font-size:16px;color:{t['body-b']}'> 편</span>"
        f"<br><span style='font-size:12px;letter-spacing:3px;color:{t['dim-a']}'>{len(counts)}개 장르</span>",
        x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False,
    )
    fig.update_layout(
        **base_layout(t, 560),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            hole=0,
            radialaxis=dict(visible=False, range=[0, top]),
            angularaxis=dict(visible=False, rotation=90, direction="clockwise"),
        ),
        bargap=0,
    )
    return fig


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
            marker=dict(colors=fills, line=dict(color=t["well"], width=2), pad=dict(t=26, l=3, r=3, b=3)),
            customdata=hover,
            hovertemplate="%{customdata}<extra></extra>",
            texttemplate="%{label}",
            textfont=dict(family="Pretendard Variable, Pretendard, sans-serif", size=14, color="#ffffff"),
            pathbar=dict(visible=False),
            tiling=dict(packing="squarify", pad=2),
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


def audience_hist(df, t, theme):
    audi = df["total_audi"]
    width = nice_width(audi.max())
    edges = np.arange(0, audi.max() + width, width)
    counts, edges = np.histogram(audi, bins=edges)
    peak = int(counts.argmax())
    blue, orange = SERIES[theme][0], SERIES[theme][1]

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
        xaxis=axis(t, title="총 관객 (명)", tickvals=ticks, ticktext=[man(v) for v in ticks], showgrid=False),
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
                marker=dict(size=10, color=colors[g], opacity=0.9, line=dict(color=t["well"], width=1.5)),
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


# ---------------------------------------------------------------- 화면
theme = pick_theme()
tokens = TOKENS[theme]
inject_css(tokens)

top_l, top_r = st.columns([3, 2], vertical_alignment="center")
with top_l:
    html('<p class="fx mark">영화 데이터 그래프 도감<span class="mark-sub">KOBIS · BOX OFFICE TOP 10</span></p>')
with top_r:
    st.segmented_control(
        "테마", ["DARK", "LIGHT"], key="theme", label_visibility="collapsed",
        selection_mode="single",
    )
    if st.session_state.theme is None:  # 고른 칸을 다시 눌러 비워진 경우
        st.session_state.theme = theme.upper()
        st.rerun()

try:
    movies = load_data(DATA_URL)
except Exception as err:  # 네트워크 오류 등
    st.error(f"데이터를 불러오지 못했습니다: {err}")
    st.stop()

order, colors = genre_colors(movies, theme, tokens)
first, last = movies["openDt"].min(), movies["openDt"].max()
html(
    f"""
<section class="hero">
  <p class="fx eyebrow">그래프 도감 &middot; 2</p>
  <h1 class="fx display"><span class="line">영화 데이터 그래프 도감 2</span><span class="line">- 분포와 관계</span></h1>
  <p class="fx lede">1년간 박스오피스 10위권에 든 영화 가운데 이 기간에 개봉한
  {len(movies)}편의 요약표입니다. 장르마다 같은 색을 끝까지 쓰므로, 한 그래프에서 본 색을 다음 그래프에서도 찾을 수 있습니다.</p>
  <p class="fx meta"><b>{len(movies)}</b>편 &middot; 개봉 {first:%Y.%m.%d} – {last:%Y.%m.%d}</p>
</section>
"""
)

# 01 — 장르별 영화 편수
counts = movies["genre"].value_counts()
with st.container(key="band-genre"):
    band_head(
        "01", "장르별 영화 편수",
        "여러 장르가 적힌 영화는 첫 번째 장르로 셉니다. 조각이 차지하는 면적이 클수록 한 단씩 더 "
        "높이 올라와 있고, 조각에 마우스를 올리면 편수와 비율이 보입니다.",
        "장르 분포", "도넛 · 편수 기준 · 4단",
    )
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
fig_hist, h = audience_hist(movies, tokens, theme)
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

stair(even=True)
html(
    """
<footer class="foot">
  <p class="fx foot-name">영화 데이터 그래프 도감 2 &middot; 분포와 관계</p>
  <p class="fx meta">자료 KOBIS 박스오피스 &middot; 무채색 바탕 &middot; 단차와 장르 색</p>
</footer>
"""
)
