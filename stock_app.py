import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import json, os, warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="IronMin Research",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── 비밀번호 보호 ─────────────────────────────────
def _check_auth():
    _pw_correct = st.secrets.get("app", {}).get("password", "")
    if not _pw_correct:
        return  # 로컬 환경(secrets 없음)은 패스
    if st.session_state.get("_authenticated"):
        return
    st.markdown("""
<div style="max-width:360px;margin:120px auto 0;text-align:center">
  <div style="font-size:2.2em;margin-bottom:8px">⚡</div>
  <div style="font-size:1.1em;font-weight:800;letter-spacing:3px;margin-bottom:4px">IRONMIN</div>
  <div style="font-size:0.68em;opacity:0.4;letter-spacing:3px;margin-bottom:32px">STOCK RESEARCH</div>
</div>""", unsafe_allow_html=True)
    pw = st.text_input("비밀번호", type="password", placeholder="접속 비밀번호 입력")
    if pw:
        if pw == _pw_correct:
            st.session_state["_authenticated"] = True
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    st.stop()

_check_auth()

st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

/* ══ 전역 폰트 ══ */
html, body, [class*="css"], .stApp, div, span, p, label,
h1, h2, h3, h4, h5, h6, button, input, select, textarea,
[data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  letter-spacing: -0.2px;
}

/* ══ 전역 기본 폰트 크기 ══ */
html { font-size: 14px; }

/* ══ 레이아웃 ══ */
.main .block-container { padding: 1.6rem 1.1rem 4rem; max-width: 1400px; }
section[data-testid="stSidebar"] > div { padding-top: 0 !important; }

/* ══ 사이드바 메뉴 ══ */
div[role="radiogroup"] { gap: 1px !important; }
div[role="radiogroup"] label {
  background: transparent !important;
  border: none !important;
  font-size: 0.82em !important;
  font-weight: 500 !important;
  padding: 7px 12px !important;
  border-radius: 7px !important;
  transition: all 0.15s !important;
  width: 100% !important;
  margin-bottom: 1px !important;
  opacity: 0.5 !important;
}
div[role="radiogroup"] label:hover {
  background: rgba(59,130,246,0.08) !important;
  opacity: 0.85 !important;
}
div[role="radiogroup"] label[data-checked="true"],
div[role="radiogroup"] label[aria-checked="true"] {
  background: rgba(59,130,246,0.12) !important;
  opacity: 1 !important;
  font-weight: 700 !important;
  border-left: 3px solid #3b82f6 !important;
  padding-left: 9px !important;
}

/* ══ 제목 계층 ══ */
h1 { font-size: 1.3em !important; font-weight: 700 !important; letter-spacing: -0.5px !important; margin-bottom: 2px !important; }
h2 { font-size: 1.05em !important; font-weight: 600 !important; }
h3 { font-size: 0.9em  !important; font-weight: 600 !important; }
p  { font-size: 0.88em !important; line-height: 1.7 !important; }
.stCaption p { font-size: 0.74em !important; opacity: 0.42 !important; }
hr { opacity: 0.12 !important; margin: 12px 0 !important; }

/* ══ 메트릭 ══ */
[data-testid="stMetric"] {
  background: var(--secondary-background-color) !important;
  border: 1px solid rgba(128,128,128,0.15) !important;
  border-radius: 10px !important;
  padding: 12px 14px !important;
  transition: border-color 0.2s !important;
}
[data-testid="stMetric"]:hover { border-color: rgba(59,130,246,0.3) !important; }
[data-testid="stMetricLabel"] {
  font-size: 0.68em !important; font-weight: 600 !important;
  opacity: 0.45 !important; text-transform: uppercase !important; letter-spacing: 0.6px !important;
}
[data-testid="stMetricValue"] { font-size: 1.2em !important; font-weight: 700 !important; }

/* ══ 버튼 ══ */
.stButton > button {
  background: rgba(59,130,246,0.08) !important;
  color: #3b82f6 !important;
  border: 1px solid rgba(59,130,246,0.3) !important;
  border-radius: 7px !important;
  font-weight: 600 !important;
  font-size: 0.78em !important;
  padding: 6px 14px !important;
  transition: all 0.15s !important;
}
.stButton > button:hover { background: rgba(59,130,246,0.16) !important; border-color: rgba(59,130,246,0.55) !important; }
.stButton > button[kind="primary"] { background: #2563eb !important; color: #fff !important; border-color: #2563eb !important; }
.stButton > button[kind="primary"]:hover { background: #3b82f6 !important; }

/* ══ 입력 ══ */
.stTextInput input, .stTextArea textarea, .stNumberInput input {
  background: var(--secondary-background-color) !important;
  border: 1px solid rgba(128,128,128,0.2) !important;
  border-radius: 8px !important;
  font-size: 0.88em !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: #3b82f6 !important;
  box-shadow: 0 0 0 2px rgba(59,130,246,0.12) !important;
}
/* 라벨 겹침 방지 — 레이블을 input 위에 고정 */
.stTextInput > label, .stTextInput > div > label,
.stNumberInput > label, .stSelectbox > label,
.stDateInput > label {
  position: static !important;
  transform: none !important;
  font-size: 0.78em !important;
  opacity: 0.7 !important;
  margin-bottom: 3px !important;
  display: block !important;
}
.stTextInput > div { margin-top: 0 !important; }
.stSelectbox > div > div {
  background: var(--secondary-background-color) !important;
  border: 1px solid rgba(128,128,128,0.2) !important;
  border-radius: 8px !important;
}

/* ══ 기타 Streamlit ══ */
.stDataFrame { border-radius: 10px !important; overflow: hidden !important; }
.stProgress > div > div { background: #3b82f6 !important; }
.stInfo, .stSuccess, .stWarning, .stError { border-radius: 8px !important; font-size: 0.87em !important; }
.streamlit-expanderHeader {
  background: var(--secondary-background-color) !important;
  border-radius: 8px !important;
  border: 1px solid rgba(128,128,128,0.12) !important;
  font-size: 0.87em !important;
}

/* ══ 인덱스 카드 ══ */
.idx-card {
  background: var(--secondary-background-color);
  border: 1px solid rgba(128,128,128,0.13);
  border-radius: 10px;
  padding: 12px 14px;
  text-align: center;
  transition: border-color 0.2s, transform 0.15s;
}
.idx-card:hover { border-color: rgba(59,130,246,0.3); transform: translateY(-1px); }

/* ══ 종목 카드 ══ */
.card {
  background: var(--secondary-background-color);
  border: 1px solid rgba(128,128,128,0.13);
  border-radius: 14px;
  padding: 22px 24px;
  margin-bottom: 14px;
  transition: border-color 0.2s;
}
.card:hover { border-color: rgba(59,130,246,0.25); }

/* ══ 테마 카드 ══ */
.theme-card {
  background: var(--secondary-background-color);
  border: 1px solid rgba(128,128,128,0.1);
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 10px;
  transition: border-color 0.2s;
}
.theme-card:hover { border-color: rgba(59,130,246,0.22); }

/* ══ 브리핑 박스 ══ */
.briefing-box {
  background: var(--secondary-background-color);
  border: 1px solid rgba(128,128,128,0.1);
  border-left: 3px solid #3b82f6;
  border-radius: 0 12px 12px 0;
  padding: 16px 20px;
  font-size: 0.88em;
  line-height: 1.85;
  opacity: 0.9;
  margin-bottom: 10px;
}

/* ══ 섹션 헤더 ══ */
.sec-hdr { display:flex; align-items:center; gap:8px; margin:22px 0 10px; }
.sec-hdr-line { flex:1; height:1px; background:rgba(128,128,128,0.12); }
.sec-hdr-text {
  font-size: 0.64em; font-weight: 700;
  opacity: 0.35; letter-spacing: 2px;
  text-transform: uppercase; white-space: nowrap;
}

/* ══ F&G 게이지 ══ */
.fng-bar-wrap {
  width:100%; height:4px;
  background:rgba(128,128,128,0.15);
  border-radius:4px; margin:8px 0 4px; overflow:hidden;
}
.fng-bar { height:100%; border-radius:4px; }

/* ══ 배지 ══ */
.badge {
  display:inline-block; border-radius:5px;
  padding:2px 8px; font-size:0.68em;
  font-weight:600; letter-spacing:0.2px;
}
.b-blue   { background:rgba(59,130,246,0.15);  color:#93c5fd; border:1px solid rgba(59,130,246,0.3); }
.b-green  { background:rgba(34,197,94,0.15);   color:#86efac; border:1px solid rgba(34,197,94,0.3); }
.b-red    { background:rgba(239,68,68,0.15);   color:#fca5a5; border:1px solid rgba(239,68,68,0.3); }
.b-amber  { background:rgba(245,158,11,0.15);  color:#fcd34d; border:1px solid rgba(245,158,11,0.3); }
.b-purple { background:rgba(139,92,246,0.15);  color:#d8b4fe; border:1px solid rgba(139,92,246,0.3); }

/* ══ 태그 ══ */
.tag {
  display:inline-block; border-radius:4px;
  padding:2px 7px; font-size:0.68em;
  font-weight:500; margin:2px;
}
.t-green  { background:rgba(34,197,94,0.13);   color:#86efac; }
.t-red    { background:rgba(239,68,68,0.13);   color:#fca5a5; }
.t-amber  { background:rgba(245,158,11,0.13);  color:#fcd34d; }
.t-blue   { background:rgba(59,130,246,0.13);  color:#93c5fd; }
.t-purple { background:rgba(139,92,246,0.13);  color:#d8b4fe; }

/* ══ 신호 ══ */
.sig-buy  { color:#4ade80; font-weight:800; font-size:1.25em; }
.sig-sell { color:#f87171; font-weight:800; font-size:1.25em; }
.sig-hold { color:#fbbf24; font-weight:800; font-size:1.25em; }

/* ══ 별점 ══ */
.star-on  { color:#f59e0b; }
.star-off { opacity:0.12; }

/* ══ 사이드바 로고 ══ */
.sidebar-logo {
  padding:26px 16px 18px; text-align:center;
  border-bottom:1px solid rgba(128,128,128,0.1);
  margin-bottom:10px;
}

/* ══ 구분 점선 ══ */
.dot-divider {
  border:none; border-top:1px dashed rgba(128,128,128,0.12);
  margin:18px 0;
}

/* ══ 모바일 반응형 ══ */
@media (max-width: 768px) {
  /* 패딩 축소 */
  .main .block-container { padding: 0.8rem 0.7rem 3rem !important; max-width: 100% !important; }

  /* st.columns() 가로 스크롤 (시장심리·FRED 등 복잡한 카드) */
  [data-testid="stHorizontalBlock"] {
    overflow-x: auto !important;
    flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch;
    padding-bottom: 6px;
  }
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    min-width: 180px !important;
    flex: 0 0 auto !important;
  }

  /* 메트릭 카드 조정 */
  [data-testid="stMetricValue"] { font-size: 1em !important; }
  [data-testid="stMetricLabel"] { font-size: 0.6em !important; }
  [data-testid="stMetric"] { padding: 9px 11px !important; }

  /* 제목/텍스트 */
  h1 { font-size: 1.1em !important; }
  h2 { font-size: 0.95em !important; }
  p  { font-size: 0.84em !important; }

  /* 카드 패딩 */
  .card { padding: 14px 15px !important; }
  .theme-card { padding: 13px 14px !important; }
  .idx-card { padding: 9px 10px !important; }

  /* 차트 스크롤 허용 */
  [data-testid="stPlotlyChart"] { overflow-x: auto !important; }
}
</style>
""", unsafe_allow_html=True)

# ── 상수 ──────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
STOCKS_FILE = os.path.join(BASE_DIR, "discovered_stocks.json")
TRENDS_FILE = os.path.join(BASE_DIR, "market_trends.json")

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

# ── 종목명 매핑 ──────────────────────────────────
# 형식: "TICKER": ("한국명", "영어명")  |  한국주식: ("한국명", None)
STOCK_NAMES = {
    # ── 한국 주식 ──
    "000660.KS": ("SK하이닉스", None),
    "005930.KS": ("삼성전자", None),
    "012450.KS": ("한화에어로스페이스", None),
    "079550.KS": ("LIG넥스원", None),
    "064350.KS": ("현대로템", None),
    "047810.KS": ("한국항공우주", None),
    "000270.KS": ("기아", None),
    "005380.KS": ("현대차", None),
    "035420.KS": ("NAVER", None),
    "035720.KS": ("카카오", None),
    "068270.KS": ("셀트리온", None),
    "207940.KS": ("삼성바이오로직스", None),
    "003550.KS": ("LG", None),
    "051910.KS": ("LG화학", None),
    "006400.KS": ("삼성SDI", None),
    "373220.KS": ("LG에너지솔루션", None),
    # ── 미국 주식 ──
    "NVDA": ("엔비디아", "NVIDIA"),
    "AMD": ("AMD", "Advanced Micro Devices"),
    "AVGO": ("브로드컴", "Broadcom"),
    "TSM": ("TSMC", "Taiwan Semiconductor"),
    "MU": ("마이크론", "Micron Technology"),
    "SNDK": ("샌디스크", "SanDisk"),
    "STX": ("씨게이트", "Seagate"),
    "MRVL": ("마벨", "Marvell Technology"),
    "ARM": ("ARM홀딩스", "ARM Holdings"),
    "INTC": ("인텔", "Intel"),
    "AAPL": ("애플", "Apple"),
    "MSFT": ("마이크로소프트", "Microsoft"),
    "GOOGL": ("알파벳", "Alphabet"),
    "AMZN": ("아마존", "Amazon"),
    "META": ("메타", "Meta Platforms"),
    "TSLA": ("테슬라", "Tesla"),
    "POET": ("POET테크", "POET Technologies"),
    "AAOI": ("AAOI", "Applied Optoelectronics"),
    "COHR": ("코히런트", "Coherent"),
    "LITE": ("루멘텀", "Lumentum"),
    "IIVI": ("II-VI", "II-VI Incorporated"),
    "VST": ("비스트라", "Vistra Energy"),
    "CEG": ("콘스텔레이션", "Constellation Energy"),
    "PWR": ("퀀타서비스", "Quanta Services"),
    "NVT": ("엔버트", "nVent Electric"),
    "PRIM": ("프리머리스", "Primoris Services"),
    "OKLO": ("오클로", "Oklo"),
    "NNE": ("나노뉴클리어", "Nano Nuclear Energy"),
    "BWXT": ("BWX테크", "BWX Technologies"),
    "CCJ": ("캠에코", "Cameco"),
    "LTBR": ("라이트브리지", "Lightbridge"),
    "ARBE": ("아르베로보틱스", "Arbe Robotics"),
    "MBOT": ("마이크로봇", "Microbot Medical"),
    "BFLY": ("버터플라이", "Butterfly Network"),
    "FIG": ("피규레이트", "Figurate"),
    "ISRG": ("인튜이티브서지컬", "Intuitive Surgical"),
    "RXRX": ("리커전파마", "Recursion Pharmaceuticals"),
    "ABSI": ("앱사이", "Absci"),
    "SDAI": ("SDAI", "SDAI"),
    "SANA": ("사나바이오", "Sana Biotechnology"),
    "EXAI": ("엑사이바이오", "Exai Bio"),
    "SPY": ("S&P500 ETF", "SPDR S&P 500 ETF"),
    "QQQ": ("나스닥100 ETF", "Invesco QQQ"),
    # ── 반도체 ──
    "QCOM": ("퀄컴", "Qualcomm"),
    "ASML": ("ASML", "ASML Holding"),
    "AMAT": ("어플라이드머티리얼즈", "Applied Materials"),
    "LRCX": ("램리서치", "Lam Research"),
    "KLAC": ("KLA", "KLA Corporation"),
    "TER":  ("테라다인", "Teradyne"),
    "ONTO": ("온토이노베이션", "Onto Innovation"),
    # ── 클라우드 ──
    "SNOW": ("스노우플레이크", "Snowflake"),
    "NET":  ("클라우드플레어", "Cloudflare"),
    "DDOG": ("데이터독", "Datadog"),
    "MDB":  ("몽고DB", "MongoDB"),
    "CFLT": ("컨플루언트", "Confluent"),
    "GTLB": ("깃랩", "GitLab"),
    # ── AI 소프트웨어 ──
    "ORCL": ("오라클", "Oracle"),
    "CRM":  ("세일즈포스", "Salesforce"),
    "PLTR": ("팔란티어", "Palantir"),
    "AI":   ("씨쓰리에이아이", "C3.ai"),
    "PATH": ("유아이패스", "UiPath"),
    # ── AI 광통신 ──
    "GLW":  ("코닝", "Corning"),
    "CIEN": ("시에나", "Ciena"),
    "GFS":  ("글로벌파운드리스", "GlobalFoundries"),
    # ── 전력 인프라 ──
    "NEE":  ("넥스트에라에너지", "NextEra Energy"),
    # ── 휴머노이드 로봇 ──
    "ABB":  ("ABB", "ABB Ltd"),
    "ROK":  ("로크웰오토메이션", "Rockwell Automation"),
    "HON":  ("허니웰", "Honeywell"),
    # ── 방산 ──
    "RTX":  ("RTX", "RTX Corporation"),
    "LMT":  ("록히드마틴", "Lockheed Martin"),
    "NOC":  ("노스롭그루먼", "Northrop Grumman"),
    "BA":   ("보잉", "Boeing"),
    "GD":   ("제너럴다이나믹스", "General Dynamics"),
    # ── 바이오 ──
    "LLY":  ("일라이릴리", "Eli Lilly"),
    "ABBV": ("애브비", "AbbVie"),
    "TEVA": ("테바파마슈티컬", "Teva Pharmaceutical"),
    # ── 양자컴퓨팅 ──
    "IBM":  ("IBM", "IBM"),
    "IONQ": ("아이온큐", "IonQ"),
    "RGTI": ("리게티컴퓨팅", "Rigetti Computing"),
    "QUBT": ("퀀텀컴퓨팅", "Quantum Computing Inc"),
    "QMCO": ("퀀텀코퍼레이션", "Quantum Corporation"),
    "ARQQ": ("아르킷퀀텀", "Arqit Quantum"),
    "SMR":  ("뉴스케일파워", "NuScale Power"),
    # ── 데이터센터 ──
    "EQIX": ("에퀴닉스", "Equinix"),
    "AMT":  ("아메리칸타워", "American Tower"),
    "DLR":  ("디지털리얼티", "Digital Realty"),
    "VRT":  ("버티브", "Vertiv"),
    "DELL": ("델테크놀로지스", "Dell Technologies"),
    "SMCI": ("슈퍼마이크로", "Super Micro Computer"),
    "HPE":  ("HP엔터프라이즈", "HP Enterprise"),
    "NTAP": ("넷앱", "NetApp"),
    # ── 2차전지 ──
    "ALB":  ("알베마를", "Albemarle"),
    "MP":   ("MP머티리얼즈", "MP Materials"),
    # ── 추가 한국 주식 ──
    "039440.KS": ("오이솔루션", None),
    "094280.KQ": ("옵티시스", None),
    "015760.KS": ("한국전력", None),
    "010120.KS": ("LS ELECTRIC", None),
    "034020.KS": ("두산에너빌리티", None),
    "052690.KS": ("한전기술", None),
    "454910.KS": ("두산로보틱스", None),
    "277810.KQ": ("레인보우로보틱스", None),
    "108490.KQ": ("로보티즈", None),
    "207940.KS": ("삼성바이오로직스", None),
    "068270.KS": ("셀트리온", None),
    "009540.KS": ("HD현대중공업", None),
    "010140.KS": ("삼성중공업", None),
    "042660.KS": ("한화오션", None),
    "010620.KS": ("현대미포조선", None),
    "096770.KS": ("SK이노베이션", None),
    "247540.KS": ("에코프로비엠", None),
    "003670.KS": ("포스코퓨처엠", None),
    "042700.KS": ("한미반도체", None),
    "039030.KS": ("이오테크닉스", None),
}

# 이름 → 티커 역방향 매핑 (소문자 키)
_NAME_TO_TK: dict[str, str] = {}
for _tk, (_kn, _en) in STOCK_NAMES.items():
    _NAME_TO_TK[_kn.lower()] = _tk
    if _en:
        _NAME_TO_TK[_en.lower()] = _tk

def resolve_ticker(inp: str) -> tuple[str, str | None]:
    """
    사용자 입력 → (정규 티커, 힌트 메시지)
    지원 형식: 티커(AAPL), 숫자 6자리(005930), 한국명(삼성전자), 영어명(Apple)
    """
    s = inp.strip()
    if not s:
        return s, None
    # 6자리 숫자 → KOSPI
    if s.isdigit() and len(s) == 6:
        return s + ".KS", None
    # 정확히 일치하는 이름
    lo = s.lower()
    if lo in _NAME_TO_TK:
        tk = _NAME_TO_TK[lo]
        return tk, f"'{s}' → {tk}"
    # 부분 일치 (가나다 순 첫 번째)
    matches = [(name, tk) for name, tk in _NAME_TO_TK.items() if lo in name]
    if matches:
        _, tk = sorted(matches)[0]
        nm = stock_display_name(tk, short=True)
        return tk, f"'{s}' → {nm} ({tk})"
    # 그대로 티커로 처리
    return s.upper(), None

def stock_display_name(ticker: str, short: bool = False) -> str:
    """티커 → 표시명 변환.
    short=True : 한국명만 반환 (공간 부족 시)
    short=False: 한국명 (영어명) 형태, 한국주식은 한국명만
    """
    info = STOCK_NAMES.get(ticker.upper())
    if info is None:
        # 매핑 없음 → 티커 그대로
        return ticker
    kor_name, eng_name = info
    if eng_name is None:
        # 한국 주식
        return kor_name
    if short:
        return kor_name
    return f"{kor_name} ({eng_name})"

def stock_link_url(ticker: str) -> str:
    """종목 URL: 한국주식 → 네이버 금융, 미국주식 → Yahoo Finance"""
    tk = ticker.upper()
    if ".KS" in tk or ".KQ" in tk:
        code = tk.replace(".KS","").replace(".KQ","")
        return f"https://finance.naver.com/item/main.naver?code={code}"
    return f"https://finance.yahoo.com/quote/{tk}"

def stock_linked_name(ticker: str, short: bool = False, style: str = "") -> str:
    """클릭 가능한 종목명 HTML — 네이버금융(KR) / Yahoo Finance(US) 링크"""
    url  = stock_link_url(ticker)
    name = stock_display_name(ticker, short=short)
    base = "color:inherit;text-decoration:none;border-bottom:1px dotted rgba(128,128,128,0.25);cursor:pointer"
    return f'<a href="{url}" target="_blank" rel="noopener" style="{base};{style}">{name}</a>'

def stock_label(ticker: str) -> str:
    """카드/표 헤더용: 이름 + 티커 배지"""
    is_kr = ".KS" in ticker or ".KQ" in ticker
    name = stock_display_name(ticker)
    if is_kr:
        return name
    return name  # ticker는 별도 표시

# ── 데이터 함수 ───────────────────────────────────
@st.cache_data(ttl=300)
def get_info(tk):
    try: return yf.Ticker(tk).info
    except: return {}

@st.cache_data(ttl=300)
def get_hist(tk, period="1y"):
    try:
        df = yf.download(tk, period=period, progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=180)
def get_index_data(tickers):
    out = {}
    for tk in tickers:
        try:
            h = yf.Ticker(tk).history(period="5d")
            if len(h) >= 2:
                c, p = h["Close"].iloc[-1], h["Close"].iloc[-2]
                out[tk] = {"price": c, "chg": (c-p)/p*100}
        except: pass
    return out

@st.cache_data(ttl=180)
def get_etf_chg(tickers):
    out = {}
    for tk in tickers:
        try:
            h = yf.Ticker(tk).history(period="5d")
            if len(h) >= 2:
                c, p = h["Close"].iloc[-1], h["Close"].iloc[-2]
                out[tk] = (c-p)/p*100
        except: out[tk] = None
    return out

@st.cache_data(ttl=3600*4)
def get_yearly_returns(tickers: tuple) -> dict:
    """섹터 전체 티커 1년 수익률 배치 조회"""
    result = {}
    try:
        tks = list(tickers)
        raw = yf.download(tks, period="1y", auto_adjust=True, progress=False)
        closes = raw["Close"] if "Close" in raw.columns else raw
        if isinstance(closes, pd.Series):
            closes = closes.to_frame(tks[0])
        for tk in tks:
            if tk in closes.columns:
                col = closes[tk].dropna()
                if len(col) >= 2:
                    result[tk] = (col.iloc[-1] / col.iloc[0] - 1) * 100
    except:
        pass
    return result

@st.cache_data(ttl=3600*24)
def get_fundamental_data(ticker: str) -> dict:
    """종목 핵심 재무 지표 조회 (24시간 캐시)"""
    try:
        info = yf.Ticker(ticker).info
        return {
            "name":           info.get("shortName", ticker),
            "grossMargin":    info.get("grossMargins"),
            "revenueGrowth":  info.get("revenueGrowth"),
            "operatingMargin":info.get("operatingMargins"),
            "marketCap":      info.get("marketCap"),
            "sector":         info.get("sector", ""),
        }
    except:
        return {}

def score_ai_moat(d: dict) -> int:
    """재무 지표 기반 AI 해자 점수 (0~8)"""
    score = 0
    gm = d.get("grossMargin")
    rg = d.get("revenueGrowth")
    om = d.get("operatingMargin")
    if gm is not None:
        if gm >= 0.65:  score += 3
        elif gm >= 0.50: score += 2
        elif gm >= 0.35: score += 1
    if rg is not None:
        if rg >= 0.30:  score += 3
        elif rg >= 0.20: score += 2
        elif rg >= 0.10: score += 1
    if om is not None:
        if om >= 0.20:  score += 2
        elif om >= 0.10: score += 1
    return score

@st.cache_data(ttl=3600*24)
def get_turnaround_data(ticker: str) -> dict:
    """흑자전환 예상 기업 분석 — 분기 추세 + 포워드 추정치 포함 (24시간 캐시)"""
    try:
        tk_obj = yf.Ticker(ticker)
        info   = tk_obj.info
        qf     = tk_obj.quarterly_financials  # 행=항목, 열=분기

        trailing_eps = info.get("trailingEps")
        forward_eps  = info.get("forwardEps")
        # 포워드 EPS가 양수이고 트레일링이 음수 → 흑자전환 임박
        eps_turning = (forward_eps is not None and forward_eps > 0
                       and trailing_eps is not None and trailing_eps < 0)
        # 포워드 EPS 개선율 (둘 다 존재할 때)
        eps_improvement = None
        if forward_eps is not None and trailing_eps is not None and trailing_eps != 0:
            eps_improvement = (forward_eps - trailing_eps) / abs(trailing_eps)

        result = {
            "name":            info.get("shortName", ticker),
            "grossMargin":     info.get("grossMargins"),
            "revenueGrowth":   info.get("revenueGrowth"),
            "operatingMargin": info.get("operatingMargins"),
            "marketCap":       info.get("marketCap"),
            "totalCash":       info.get("totalCash"),
            "totalDebt":       info.get("totalDebt"),
            "trailingEps":     trailing_eps,
            "forwardEps":      forward_eps,
            "eps_turning":     eps_turning,       # 트레일링↓ → 포워드↑
            "eps_improvement": eps_improvement,   # 개선율
            "op_trend":        None,              # 분기 영업이익 추세 (0~3)
            "op_quarters":     [],                # 최근 4분기 영업이익
        }

        if qf is not None and not qf.empty:
            op_row = None
            for label in ["Operating Income", "Operating Income Or Loss", "EBIT"]:
                if label in qf.index:
                    op_row = qf.loc[label]
                    break
            if op_row is not None:
                op_vals = op_row.dropna().tolist()[:4]
                result["op_quarters"] = op_vals
                if len(op_vals) >= 3:
                    improving = sum(1 for i in range(len(op_vals)-1) if op_vals[i] > op_vals[i+1])
                    result["op_trend"] = improving  # 3 = 매 분기 개선

        return result
    except:
        return {}

def score_turnaround(d: dict) -> int:
    """흑자전환 예상 점수 (0~10) — 분기 추세 + 포워드 EPS 전환 신호 반영"""
    score = 0
    gm   = d.get("grossMargin")
    rg   = d.get("revenueGrowth")
    om   = d.get("operatingMargin")
    tr   = d.get("op_trend")
    cash = d.get("totalCash") or 0
    debt = d.get("totalDebt") or 0
    eps_turning    = d.get("eps_turning", False)
    eps_imp        = d.get("eps_improvement")

    # ① 단위경제성 — 매출총이익률
    if gm is not None:
        if gm >= 0.60: score += 3
        elif gm >= 0.40: score += 2
        elif gm >= 0.25: score += 1

    # ② 매출 성장 속도 (고정비 레버리지)
    if rg is not None:
        if rg >= 0.40: score += 2
        elif rg >= 0.25: score += 1

    # ③ 분기별 영업이익 개선 추세
    if tr is not None:
        if tr >= 3: score += 2
        elif tr >= 2: score += 1

    # ④ 포워드 EPS 전환 신호 (핵심 — 애널리스트 컨센서스)
    if eps_turning:
        score += 2   # 트레일링 적자 → 포워드 흑자 예상
    elif eps_imp is not None and eps_imp > 0.50:
        score += 1   # EPS 50%+ 개선 예상

    # ⑤ 현재 적자 폭이 작을수록 가산 (손익분기 근접)
    if om is not None:
        if -0.05 < om < 0:   score += 1   # 5% 미만 적자 — 매우 임박
        elif -0.15 < om < 0: score += 0   # 중간

    # ⑥ 현금 여력
    if cash > debt * 1.5: score += 1

    return min(score, 10)

@st.cache_data(ttl=3600*4)
def get_rsi_data(tickers: tuple) -> dict:
    """섹터 전체 티커 RSI(14) 배치 계산"""
    result = {}
    try:
        tks = list(tickers)
        raw = yf.download(tks, period="3mo", auto_adjust=True, progress=False)
        closes = raw["Close"] if "Close" in raw.columns else raw
        if isinstance(closes, pd.Series):
            closes = closes.to_frame(tks[0])
        for tk in tks:
            if tk in closes.columns:
                col = closes[tk].dropna()
                if len(col) >= 15:
                    delta    = col.diff()
                    gain     = delta.clip(lower=0).rolling(14).mean()
                    loss     = (-delta.clip(upper=0)).rolling(14).mean()
                    avg_g    = gain.iloc[-1]
                    avg_l    = loss.iloc[-1]
                    if avg_l == 0:
                        result[tk] = 100.0
                    else:
                        result[tk] = 100 - (100 / (1 + avg_g / avg_l))
    except:
        pass
    return result

def rsi_signal(rsi):
    """RSI 값을 신호등 이모지로 변환"""
    if rsi is None: return "⚪"
    if rsi < 40:    return "🟢"
    if rsi > 65:    return "🔴"
    return "🟡"

def get_price(tk):
    try: return yf.Ticker(tk).fast_info.last_price
    except: return None

def _secret(section, key, default=""):
    try: return st.secrets[section][key]
    except: return default

@st.cache_data(ttl=3600)
def get_fred(series_id, limit=14):
    """FRED 시계열 데이터 (최신순 정렬, 결측값 제거)"""
    api_key = _secret("fred", "api_key")
    if not api_key or "여기에" in api_key:
        return None
    try:
        import urllib.request as _ur2, json as _json2
        url = (f"https://api.stlouisfed.org/fred/series/observations"
               f"?series_id={series_id}&api_key={api_key}"
               f"&limit={limit}&sort_order=desc&file_type=json")
        with _ur2.urlopen(url, timeout=6) as r:
            obs = _json2.loads(r.read())["observations"]
        return [o for o in obs if o["value"] != "."]
    except: return None

def fred_latest(series_id, limit=2):
    """(최신값, 전기대비변화, 날짜) 반환"""
    data = get_fred(series_id, limit)
    if not data: return None, None, None
    v0 = float(data[0]["value"])
    v1 = float(data[1]["value"]) if len(data) > 1 else None
    return v0, (v0 - v1) if v1 is not None else None, data[0]["date"]

def fred_cpi_yoy():
    """CPI 전년비 YoY% 계산"""
    data = get_fred("CPIAUCSL", 14)
    if not data or len(data) < 13: return None, None, None
    latest   = float(data[0]["value"])
    year_ago = float(data[12]["value"])
    yoy = (latest / year_ago - 1) * 100
    chg = None
    if len(data) >= 14:
        prev_yoy = (float(data[1]["value"]) / float(data[13]["value"]) - 1) * 100
        chg = yoy - prev_yoy
    return yoy, chg, data[0]["date"]

@st.cache_data(ttl=1800)
def get_dart_list(days=14, page_count=15):
    """DART 최근 주요 공시 목록"""
    api_key = _secret("dart", "api_key")
    if not api_key or "여기에" in api_key:
        return []
    try:
        import urllib.request as _ur3, json as _json3
        from datetime import timedelta
        end   = datetime.today()
        start = end - timedelta(days=days)
        url = (f"https://opendart.fss.or.kr/api/list.json"
               f"?crtfc_key={api_key}"
               f"&bgn_de={start.strftime('%Y%m%d')}"
               f"&end_de={end.strftime('%Y%m%d')}"
               f"&pblntf_ty=B&page_count={page_count}")  # B=주요사항보고
        with _ur3.urlopen(url, timeout=6) as r:
            data = _json3.loads(r.read())
        if data.get("status") != "000": return []
        return data.get("list", [])
    except: return []

@st.cache_data(ttl=3600*24)
def get_dart_corp_code(stock_code: str) -> str:
    """DART corp_code 조회 (stock_code: '005930' 형식)"""
    api_key = _secret("dart", "api_key")
    if not api_key or "여기에" in api_key:
        return ""
    try:
        import urllib.request as _ur4
        url = (f"https://opendart.fss.or.kr/api/company.json"
               f"?crtfc_key={api_key}&stock_code={stock_code}")
        with _ur4.urlopen(url, timeout=8) as r:
            data = json.loads(r.read())
        if data.get("status") == "000":
            return data.get("corp_code", "")
    except:
        pass
    return ""

@st.cache_data(ttl=3600*24)
def get_dart_kr_financials(corp_code: str, bsns_year: int = 0) -> dict:
    """DART 연간 재무제표 — 매출·영업이익·순이익·자본·부채 (연결우선, 개별 fallback)"""
    if not corp_code:
        return {}
    api_key = _secret("dart", "api_key")
    if not api_key or "여기에" in api_key:
        return {}
    if bsns_year == 0:
        bsns_year = datetime.today().year - 1

    import urllib.request as _ur5

    def _fetch(fs_div):
        url = (f"https://opendart.fss.or.kr/api/fnlttSinglAcnt.json"
               f"?crtfc_key={api_key}&corp_code={corp_code}"
               f"&bsns_year={bsns_year}&reprt_code=11011&fs_div={fs_div}")
        try:
            with _ur5.urlopen(url, timeout=10) as r:
                return json.loads(r.read())
        except:
            return {}

    def _extract_amount(items, keywords):
        for it in items:
            nm = it.get("account_nm", "")
            for kw in keywords:
                if nm == kw or (kw in nm and nm.replace(kw, "").strip() in ("", "(연결)", "(별도)")):
                    try:
                        raw = it.get("thstrm_amount", "").replace(",", "").replace(" ", "")
                        if raw and raw not in ("-", ""):
                            return int(raw)
                    except:
                        pass
        return None

    def _extract_prev(items, keywords):
        for it in items:
            nm = it.get("account_nm", "")
            for kw in keywords:
                if nm == kw or (kw in nm and nm.replace(kw, "").strip() in ("", "(연결)", "(별도)")):
                    try:
                        raw = it.get("frmtrm_amount", "").replace(",", "").replace(" ", "")
                        if raw and raw not in ("-", ""):
                            return int(raw)
                    except:
                        pass
        return None

    for fs_div in ("CFS", "OFS"):
        data = _fetch(fs_div)
        if data.get("status") == "000" and data.get("list"):
            items = data["list"]
            rev      = _extract_amount(items, ["매출액", "수익(매출액)"])
            op_inc   = _extract_amount(items, ["영업이익", "영업이익(손실)"])
            net_inc  = _extract_amount(items, ["당기순이익", "당기순이익(손실)"])
            equity   = _extract_amount(items, ["자본총계"])
            debt_tot = _extract_amount(items, ["부채총계"])
            prev_rev = _extract_prev(items, ["매출액", "수익(매출액)"])

            result = {
                "매출액":     rev,
                "영업이익":   op_inc,
                "당기순이익": net_inc,
                "자본총계":   equity,
                "부채총계":   debt_tot,
                "bsns_year":  bsns_year,
                "fs_div":     fs_div,
            }
            # 파생 비율
            if rev and rev != 0:
                result["opm"] = op_inc / rev if op_inc is not None else None
                result["npm"] = net_inc / rev if net_inc is not None else None
                if prev_rev and prev_rev != 0:
                    result["rev_g"] = (rev - prev_rev) / abs(prev_rev)
            if equity and equity != 0:
                result["roe"] = net_inc / equity if net_inc is not None else None
                result["dte"] = (debt_tot / equity * 100) if debt_tot is not None else None
            return result
    return {}

@st.cache_data(ttl=3600*3)
def get_news_kr(ticker: str, max_items: int = 5) -> list:
    """종목 최신 뉴스 한글 번역 (deep-translator 사용, fallback: 영문 원본)"""
    try:
        news = yf.Ticker(ticker).news
        if not news:
            return []
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source="auto", target="ko")
        except Exception:
            translator = None

        results = []
        for item in news[:max_items]:
            content = item.get("content") or {}
            title   = content.get("title") or item.get("title", "")
            link    = content.get("canonicalUrl", {}).get("url", "") or \
                      item.get("link", "") or item.get("url", "")
            pub_ts  = item.get("providerPublishTime") or \
                      (content.get("pubDate", "") or "")[:10]
            if not title:
                continue
            if translator:
                try:
                    title_kr = translator.translate(title)
                except Exception:
                    title_kr = title
            else:
                title_kr = title
            results.append({"title": title_kr, "title_en": title, "link": link, "date": pub_ts})
        return results
    except Exception:
        return []

@st.cache_data(ttl=1800)
def get_surge_news(ticker: str) -> str:
    """거래량 급등 종목 최신 뉴스 헤드라인 1건 반환"""
    try:
        items = yf.Ticker(ticker).news
        if not items:
            return ""
        first = items[0]
        # yfinance 버전에 따라 구조가 다름
        title = (first.get("content", {}) or {}).get("title") or first.get("title", "")
        return title[:60] if title else ""
    except:
        return ""

@st.cache_data(ttl=600)
def get_volume_surge(tickers, lookback=21):
    """거래량 급등 종목 스크리닝: (ticker, name, 현재가, 오늘거래량, 20일평균, 배율, 등락률) 반환"""
    results = []
    for tk in tickers:
        try:
            df = yf.download(tk, period="3mo", progress=False, auto_adjust=True)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if df.empty or len(df) < lookback + 1:
                continue
            vol_today = df["Volume"].iloc[-1]
            vol_avg   = df["Volume"].iloc[-(lookback+1):-1].mean()
            if vol_avg < 1000 or vol_today == 0:
                continue
            ratio = vol_today / vol_avg
            cl = df["Close"].iloc[-1]
            pr = df["Close"].iloc[-2]
            chg = (cl - pr) / pr * 100 if pr else 0
            nm = stock_display_name(tk) if tk in STOCK_NAMES else tk
            if nm == tk:
                try:
                    nm = yf.Ticker(tk).info.get("shortName") or tk
                except:
                    pass
            results.append({
                "ticker": tk, "name": nm,
                "price": float(cl), "chg": float(chg),
                "vol_today": int(vol_today), "vol_avg": int(vol_avg),
                "ratio": float(ratio)
            })
        except:
            continue
    return sorted(results, key=lambda x: x["ratio"], reverse=True)

def calc_rsi(s, n=14):
    d = s.diff()
    g = d.clip(lower=0).ewm(com=n-1, min_periods=n).mean()
    l = (-d.clip(upper=0)).ewm(com=n-1, min_periods=n).mean()
    return 100 - 100/(1+g/l)

def calc_macd(s):
    m = s.ewm(span=12).mean() - s.ewm(span=26).mean()
    sig = m.ewm(span=9).mean()
    return m, sig, m-sig

def fmt(v, sfx=""):
    if v is None or (isinstance(v, float) and np.isnan(v)): return "N/A"
    if abs(v)>=1e12: return f"{v/1e12:.2f}조{sfx}"
    if abs(v)>=1e8:  return f"{v/1e8:.2f}억{sfx}"
    return f"{v:,.0f}{sfx}"

def load_stocks():
    if os.path.exists(STOCKS_FILE):
        with open(STOCKS_FILE, encoding="utf-8") as f: return json.load(f)
    return []

def save_stocks(stocks):
    with open(STOCKS_FILE, "w", encoding="utf-8") as f:
        json.dump(stocks, f, ensure_ascii=False, indent=2)

def load_trends():
    if os.path.exists(TRENDS_FILE):
        with open(TRENDS_FILE, encoding="utf-8") as f: return json.load(f)
    return {}

def stars_html(n, mx=5):
    return (f'<span class="star-on">{"★"*max(0,min(n,mx))}</span>'
            f'<span class="star-off">{"★"*(mx-max(0,min(n,mx)))}</span>')

def badge(status):
    m = {"관찰 중":"b-blue","매수 고려":"b-green","주의":"b-red"}
    return f'<span class="badge {m.get(status,"b-blue")}">{status}</span>'

def chg_badge(v):
    if v is None: return '<span style="opacity:0.3">—</span>'
    c = "#22c55e" if v>=0 else "#ef4444"
    a = "▲" if v>=0 else "▼"
    return f'<span style="color:{c};font-weight:600">{a} {abs(v):.2f}%</span>'

def theme_badge(s):
    if any(k in s for k in ["상승","강세","모멘텀"]): cls = "b-green"
    elif any(k in s for k in ["하락","약세","주의"]): cls = "b-red"
    else: cls = "b-amber"
    return f'<span class="badge {cls}">{s}</span>'

def sec_hdr(icon, title):
    return f"""
<div class="sec-hdr">
  <span style="font-size:1em">{icon}</span>
  <span class="sec-hdr-text">{title}</span>
  <div class="sec-hdr-line"></div>
</div>"""

def mk_card(icon, label, val_str, chg=None, sub=None, url=None):
    if url:
        _ls = "color:inherit;text-decoration:none;border-bottom:1px dotted rgba(128,128,128,0.22);cursor:pointer"
        label_html = f'<a href="{url}" target="_blank" rel="noopener" style="{_ls}">{label}</a>'
    else:
        label_html = label
    if chg is not None:
        c = "#ef4444" if chg>=0 else "#3b82f6"
        a = "▲" if chg>=0 else "▼"
        chg_html = f'<div style="font-size:0.75em;color:{c};font-weight:600;margin-top:1px">{a} {abs(chg):.2f}%</div>'
    else:
        chg_html = ""
    sub_html = f'<div style="font-size:0.62em;opacity:0.38;margin-top:1px">{sub}</div>' if sub else ""
    return f"""
<div class="idx-card">
  <div style="font-size:0.62em;opacity:0.42;margin-bottom:2px;font-weight:600;letter-spacing:0.3px">{icon} {label_html}</div>
  <div style="font-size:1.0em;font-weight:700;letter-spacing:-0.3px">{val_str}</div>
  {chg_html}{sub_html}
</div>"""

# ── 사이드바 ──────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div class="sidebar-logo">
  <div style="font-size:1.8em;margin-bottom:6px;filter:drop-shadow(0 0 8px rgba(59,130,246,0.3))">⚡</div>
  <div style="font-size:1.05em;font-weight:800;letter-spacing:3px">IRONMIN</div>
  <div style="font-size:0.6em;color:#3b82f6;letter-spacing:3.5px;margin-top:4px;font-weight:600">STOCK RESEARCH</div>
</div>
""", unsafe_allow_html=True)

    menu = st.radio("", ["📰  시장 동향", "⚡  발굴 종목", "🔍  종목 분석", "💼  포트폴리오", "📊  매매 신호"])

    st.markdown("<hr class='dot-divider'>", unsafe_allow_html=True)

    stocks  = load_stocks()
    trends  = load_trends()
    w = sum(1 for s in stocks if s.get("current_status")=="관찰 중")
    b = sum(1 for s in stocks if s.get("current_status")=="매수 고려")
    c = sum(1 for s in stocks if s.get("current_status")=="주의")
    upd = trends.get("last_updated","—")

    st.markdown(f"""
<div style="padding:4px 10px;font-size:0.8em;line-height:2.3;opacity:0.7;">
  <div style="color:#3b82f6;font-weight:700;font-size:0.82em;margin-bottom:6px;letter-spacing:1.5px">WATCHLIST</div>
  <div style="display:flex;justify-content:space-between"><span>관찰 중</span><b style="color:#60a5fa">{w}</b></div>
  <div style="display:flex;justify-content:space-between"><span>매수 고려</span><b style="color:#22c55e">{b}</b></div>
  <div style="display:flex;justify-content:space-between"><span>주의</span><b style="color:#ef4444">{c}</b></div>
  <div style="margin-top:12px;opacity:0.35;font-size:0.8em;border-top:1px solid rgba(128,128,128,0.12);padding-top:10px">업데이트 {upd}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<hr class='dot-divider'>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.7em;opacity:0.28;padding:0 10px;line-height:1.7;">본 앱은 참고용 정보만 제공합니다.<br>투자 결정은 본인 판단으로 진행하세요.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# 📰 시장 동향
# ══════════════════════════════════════════════════
if "시장 동향" in menu:
    import urllib.request as _ur, json as _json
    trends = load_trends()
    upd    = trends.get("last_updated","—")

    st.markdown(f"""
<div style="margin-bottom:20px">
  <h1 style="margin-bottom:4px">시장 동향</h1>
  <div style="font-size:0.75em;opacity:0.42;letter-spacing:0.3px">매일 오전 8시 자동 업데이트 &nbsp;·&nbsp; 최근 업데이트 {upd}</div>
</div>""", unsafe_allow_html=True)

    # ── 주요 지수 ──
    st.markdown(sec_hdr("🌐", "주요 지수"), unsafe_allow_html=True)
    IDX   = {"S&P 500":"^GSPC","NASDAQ":"^IXIC","Dow Jones":"^DJI","필라델피아반도체":"^SOX","러셀 2000":"^RUT","KOSPI":"^KS11","KOSDAQ":"^KQ11"}
    FLAGS = {"S&P 500":"🇺🇸","NASDAQ":"🇺🇸","Dow Jones":"🇺🇸","필라델피아반도체":"🇺🇸","러셀 2000":"🇺🇸","KOSPI":"🇰🇷","KOSDAQ":"🇰🇷"}
    IDX2  = {"니케이 225":"^N225","상해종합":"000001.SS","항셍":"^HSI","대만가권":"^TWII","인도 SENSEX":"^BSESN","유로스톡스50":"^STOXX50E","브라질 IBOV":"^BVSP","아르헨티나 MER":"^MERV"}
    FLAGS2= {"니케이 225":"🇯🇵","상해종합":"🇨🇳","항셍":"🇭🇰","대만가권":"🇹🇼","인도 SENSEX":"🇮🇳","유로스톡스50":"🇪🇺","브라질 IBOV":"🇧🇷","아르헨티나 MER":"🇦🇷"}
    _all_idx = list(IDX.values()) + list(IDX2.values())
    _GRID = "display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:6px;margin-bottom:8px"
    with st.spinner(""):
        idx = get_index_data(_all_idx)

    # 미국·한국 주요 지수
    _cards_html = ""
    for label, tk in IDX.items():
        d   = idx.get(tk)
        url = f"https://finance.yahoo.com/quote/{tk.replace('^','%5E')}"
        _cards_html += mk_card(FLAGS[label], label, f"{d['price']:,.2f}" if d else "—", d["chg"] if d else None, url=url)
    st.markdown(f'<div style="{_GRID}">{_cards_html}</div>', unsafe_allow_html=True)

    # 국가 지수
    _cards_html = ""
    for label, tk in IDX2.items():
        d   = idx.get(tk)
        url = f"https://finance.yahoo.com/quote/{tk.replace('^','%5E')}"
        _cards_html += mk_card(FLAGS2[label], label, f"{d['price']:,.2f}" if d else "—", d["chg"] if d else None, url=url)
    st.markdown(f'<div style="{_GRID}">{_cards_html}</div>', unsafe_allow_html=True)

    # ── 환율 · 원자재 · 암호화폐 ──
    st.markdown(sec_hdr("💱", "환율 · 원자재 · 암호화폐"), unsafe_allow_html=True)
    COMM      = {"USD/KRW":"KRW=X","WTI 원유":"CL=F","브렌트유":"BZ=F","금($/oz)":"GC=F","은":"SI=F","구리":"HG=F","천연가스":"NG=F","비트코인":"BTC-USD"}
    COMM_DEC  = {"USD/KRW":0,"WTI 원유":2,"브렌트유":2,"금($/oz)":0,"은":2,"구리":3,"천연가스":3,"비트코인":0}
    COMM_ICON = {"USD/KRW":"💱","WTI 원유":"🛢","브렌트유":"🛢","금($/oz)":"🥇","은":"🪙","구리":"🔶","천연가스":"🔥","비트코인":"₿"}
    COMM_PFX  = {"USD/KRW":"","WTI 원유":"$","브렌트유":"$","금($/oz)":"$","은":"$","구리":"$","천연가스":"$","비트코인":"$"}
    with st.spinner(""):
        comm_data = get_index_data(list(COMM.values()))
    _cards_html = ""
    for label, tk in COMM.items():
        d   = comm_data.get(tk)
        url = f"https://finance.yahoo.com/quote/{tk.replace('^','%5E')}"
        if d:
            p_fmt = f"{COMM_PFX[label]}{d['price']:,.{COMM_DEC[label]}f}"
            _cards_html += mk_card(COMM_ICON[label], label, p_fmt, d["chg"], url=url)
        else:
            _cards_html += mk_card(COMM_ICON[label], label, "—", url=url)
    st.markdown(f'<div style="{_GRID}">{_cards_html}</div>', unsafe_allow_html=True)

    # ── 시장 심리 ──
    st.markdown(sec_hdr("🧠", "시장 심리"), unsafe_allow_html=True)

    @st.cache_data(ttl=1800)
    def get_cnn_fng():
        """VIX(60%) + SPY 모멘텀(30%) + Put/Call(10%) 합성 공탐지수"""
        try:
            # 1) VIX — 낮을수록 탐욕 (VIX 10→100점, VIX 40→0점)
            vix_hist = yf.download("^VIX", period="5d", progress=False, auto_adjust=True)["Close"].squeeze().dropna()
            vix_now  = float(vix_hist.iloc[-1])
            vix_prev = float(vix_hist.iloc[-2]) if len(vix_hist) >= 2 else vix_now
            def _vix_score(v): return max(0, min(100, (40 - v) / 30 * 100))
            vs_now  = _vix_score(vix_now)
            vs_prev = _vix_score(vix_prev)

            # 2) SPY vs 125일 이동평균 — 위면 탐욕(65), 아래면 공포(35)
            spy_hist = yf.download("SPY", period="7mo", progress=False, auto_adjust=True)["Close"].squeeze().dropna()
            ma125    = float(spy_hist.rolling(125).mean().iloc[-1])
            mom_score = 65 if float(spy_hist.iloc[-1]) > ma125 else 35

            # 3) Put/Call 비율 — 낮을수록 탐욕 (0.5→80점, 1.2→20점)
            try:
                pc_df = yf.download("^PCALL", period="5d", progress=False, auto_adjust=True)["Close"].squeeze().dropna()
                pc    = float(pc_df.iloc[-1]) if not pc_df.empty else 0.8
            except:
                pc = 0.8
            pc_score = max(0, min(100, (1.2 - pc) / 0.7 * 60 + 20))

            score      = round(vs_now  * 0.6 + mom_score * 0.3 + pc_score * 0.1)
            prev_score = round(vs_prev * 0.6 + mom_score * 0.3 + pc_score * 0.1)

            if   score >= 75: label = "극탐욕"
            elif score >= 55: label = "탐욕"
            elif score >= 45: label = "중립"
            elif score >= 25: label = "공포"
            else:             label = "극공포"

            return score, score - prev_score, label
        except:
            return None, None, None

    @st.cache_data(ttl=1800)
    def get_btc_fng():
        try:
            with _ur.urlopen("https://api.alternative.me/fng/?limit=2", timeout=4) as r:
                data = _json.loads(r.read())["data"]
                cur  = int(data[0]["value"])
                prev = int(data[1]["value"])
                lbl  = data[0]["value_classification"]
                lbl_map = {"Extreme Fear":"극공포","Fear":"공포","Neutral":"중립",
                           "Greed":"탐욕","Extreme Greed":"극탐욕"}
                return cur, cur-prev, lbl_map.get(lbl, lbl)
        except: return None, None, None

    @st.cache_data(ttl=1800)
    def get_put_call():
        try:
            spy   = yf.Ticker("SPY")
            exp   = spy.options[0]
            chain = spy.option_chain(exp)
            pv    = chain.puts["volume"].fillna(0).sum()
            cv    = chain.calls["volume"].fillna(0).sum()
            if cv == 0: return None, None
            return round(pv / cv, 2), exp
        except: return None, None

    @st.cache_data(ttl=3600*6)
    def get_aaii_sentiment():
        """AAII 투자자 심리 설문 — 주간 발표 (강세%·약세%·스프레드)"""
        try:
            import csv, io
            req = _ur.Request(
                "https://www.aaii.com/sentimentsurvey/sent_results.csv",
                headers={"User-Agent":"Mozilla/5.0"}
            )
            with _ur.urlopen(req, timeout=7) as r:
                text = r.read().decode("utf-8", errors="ignore")
            rows = list(csv.DictReader(io.StringIO(text)))
            # 유효한 마지막 행 (Bullish 값 있는 것)
            rows = [row for row in rows if row.get("Bullish","").strip()]
            if not rows:
                return None, None, None, None
            last = rows[-1]
            def _p(s):
                s = s.strip().replace("%","")
                v = float(s)
                return v * 100 if v <= 1.0 else v   # 소수형(0.34) → %로 변환
            bull = _p(last["Bullish"])
            bear = _p(last["Bearish"])
            spread = bull - bear
            date = last.get("Date","").strip()
            return bull, bear, spread, date
        except:
            return None, None, None, None

    def fng_gauge_card(icon, title, val, chg, label):
        """공탐지수 카드 — 게이지 바 포함"""
        if val is None:
            return mk_card(icon, title, "—")
        if val >= 75:   fc = "#34d399"; fl = "극탐욕"
        elif val >= 55: fc = "#86efac"; fl = "탐욕"
        elif val >= 45: fc = "#fbbf24"; fl = "중립"
        elif val >= 25: fc = "#fb923c"; fl = "공포"
        else:           fc = "#f87171"; fl = "극공포"
        lbl = label or fl
        chg_sign = f"{chg:+d}pt" if chg is not None else "—"
        pct = max(0, min(val, 100))
        return f"""
<div class="idx-card" style="text-align:left;padding:16px 18px">
  <div style="font-size:0.65em;opacity:0.45;font-weight:600;letter-spacing:0.3px;margin-bottom:8px">{icon} {title}</div>
  <div style="display:flex;align-items:baseline;gap:8px">
    <span style="font-size:1.55em;font-weight:800;color:{fc};letter-spacing:-1px">{val}</span>
    <span style="font-size:0.72em;color:{fc};font-weight:700">{lbl}</span>
  </div>
  <div class="fng-bar-wrap">
    <div class="fng-bar" style="width:{pct}%;background:linear-gradient(90deg,#ef4444,{fc})"></div>
  </div>
  <div style="font-size:0.62em;opacity:0.38;margin-top:2px">전일比 {chg_sign} &nbsp;·&nbsp; 25↓ 공포 / 75↑ 탐욕</div>
</div>"""

    cnn_val, cnn_chg, cnn_lbl = get_cnn_fng()
    btc_val, btc_chg, btc_lbl = get_btc_fng()
    pc_ratio, pc_exp           = get_put_call()
    aaii_bull, aaii_bear, aaii_spread, aaii_date = get_aaii_sentiment()
    with st.spinner(""):
        vix_data    = get_index_data(["^VIX"])
        skew_dxy    = get_index_data(["^SKEW", "DX-Y.NYB"])

    si1, si2, si3, si4 = st.columns(4)

    with si1:
        st.markdown(fng_gauge_card("😨", "공탐지수 (VIX기반)", cnn_val, cnn_chg, cnn_lbl), unsafe_allow_html=True)
    with si2:
        vd = vix_data.get("^VIX")
        if vd:
            vc = "#f87171" if vd["price"]>25 else "#fbbf24" if vd["price"]>18 else "#34d399"
            vl = "고변동성" if vd["price"]>25 else "경계" if vd["price"]>18 else "안정"
            vix_pct = min(vd['price'] / 50 * 100, 100)
            st.markdown(f"""
<div class="idx-card" style="text-align:left;padding:16px 18px">
  <div style="font-size:0.65em;opacity:0.45;font-weight:600;letter-spacing:0.3px;margin-bottom:8px">📉 VIX 변동성지수</div>
  <div style="display:flex;align-items:baseline;gap:8px">
    <span style="font-size:1.55em;font-weight:800;color:{vc};letter-spacing:-1px">{vd['price']:.2f}</span>
    <span style="font-size:0.72em;color:{vc};font-weight:700">{vl}</span>
  </div>
  <div class="fng-bar-wrap">
    <div class="fng-bar" style="width:{vix_pct:.1f}%;background:linear-gradient(90deg,#22c55e,{vc})"></div>
  </div>
  <div style="font-size:0.62em;opacity:0.38;margin-top:2px">전일比 {vd['chg']:+.2f}% &nbsp;·&nbsp; 18↑ 경계 / 25↑ 위험</div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown(mk_card("📉","VIX","—"), unsafe_allow_html=True)
    with si3:
        if pc_ratio is not None:
            if pc_ratio >= 1.2:   pc,pl = "#f87171","강한 공포"
            elif pc_ratio >= 0.9: pc,pl = "#fb923c","공포"
            elif pc_ratio >= 0.7: pc,pl = "#fbbf24","중립"
            elif pc_ratio >= 0.5: pc,pl = "#86efac","낙관"
            else:                 pc,pl = "#34d399","과열"
            pc_pct = min(pc_ratio / 2.0 * 100, 100)
            st.markdown(f"""
<div class="idx-card" style="text-align:left;padding:16px 18px">
  <div style="font-size:0.65em;opacity:0.45;font-weight:600;letter-spacing:0.3px;margin-bottom:8px">📊 풋/콜 비율 (SPY)</div>
  <div style="display:flex;align-items:baseline;gap:8px">
    <span style="font-size:1.55em;font-weight:800;color:{pc};letter-spacing:-1px">{pc_ratio:.2f}</span>
    <span style="font-size:0.72em;color:{pc};font-weight:700">{pl}</span>
  </div>
  <div class="fng-bar-wrap">
    <div class="fng-bar" style="width:{pc_pct:.1f}%;background:linear-gradient(90deg,#22c55e,{pc})"></div>
  </div>
  <div style="font-size:0.62em;opacity:0.38;margin-top:2px">만기 {pc_exp} &nbsp;·&nbsp; 0.7↓ 낙관 / 1.0↑ 공포</div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown(mk_card("📊","풋/콜 비율","—"), unsafe_allow_html=True)
    with si4:
        st.markdown(fng_gauge_card("₿", "공탐지수 (BTC)", btc_val, btc_chg, btc_lbl), unsafe_allow_html=True)

    # ── 시장 심리 2행: SKEW · DXY · AAII ──
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    si5, si6, si7 = st.columns(3)

    with si5:
        sd = skew_dxy.get("^SKEW")
        if sd:
            sv = sd["price"]
            sc = "#f87171" if sv >= 140 else "#fbbf24" if sv >= 120 else "#34d399"
            sl = "꼬리리스크 경보" if sv >= 140 else "경계" if sv >= 120 else "안정"
            skew_pct = min(max((sv - 100) / 60 * 100, 0), 100)
            st.markdown(f"""
<div class="idx-card" style="text-align:left;padding:16px 18px">
  <div style="font-size:0.65em;opacity:0.45;font-weight:600;letter-spacing:0.3px;margin-bottom:8px">📐 CBOE SKEW 지수</div>
  <div style="display:flex;align-items:baseline;gap:8px">
    <span style="font-size:1.55em;font-weight:800;color:{sc};letter-spacing:-1px">{sv:.1f}</span>
    <span style="font-size:0.72em;color:{sc};font-weight:700">{sl}</span>
  </div>
  <div class="fng-bar-wrap">
    <div class="fng-bar" style="width:{skew_pct:.1f}%;background:linear-gradient(90deg,#22c55e,{sc})"></div>
  </div>
  <div style="font-size:0.62em;opacity:0.38;margin-top:2px">전일比 {sd['chg']:+.2f}% &nbsp;·&nbsp; 120+ 경계 / 140+ 위험</div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown(mk_card("📐","SKEW","—"), unsafe_allow_html=True)

    with si6:
        dd = skew_dxy.get("DX-Y.NYB")
        if dd:
            dv = dd["price"]
            dc = "#ef4444" if dd["chg"] >= 0 else "#3b82f6"
            da = "▲" if dd["chg"] >= 0 else "▼"
            dl = "달러 강세 (리스크오프 압력)" if dd["chg"] >= 0 else "달러 약세 (리스크온 우호)"
            dxy_pct = min(max((dv - 90) / 30 * 100, 0), 100)   # 90~120 범위 정규화
            st.markdown(f"""
<div class="idx-card" style="text-align:left;padding:16px 18px">
  <div style="font-size:0.65em;opacity:0.45;font-weight:600;letter-spacing:0.3px;margin-bottom:8px">💵 달러 인덱스 (DXY)</div>
  <div style="display:flex;align-items:baseline;gap:8px">
    <span style="font-size:1.55em;font-weight:800;color:{dc};letter-spacing:-1px">{dv:.2f}</span>
    <span style="font-size:0.72em;color:{dc};font-weight:700">{da} {abs(dd['chg']):.2f}%</span>
  </div>
  <div class="fng-bar-wrap">
    <div class="fng-bar" style="width:{dxy_pct:.1f}%;background:linear-gradient(90deg,#3b82f6,{dc})"></div>
  </div>
  <div style="font-size:0.62em;opacity:0.38;margin-top:2px">{dl}</div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown(mk_card("💵","DXY","—"), unsafe_allow_html=True)

    with si7:
        if aaii_bull is not None:
            ac = "#34d399" if aaii_spread >= 10 else "#fbbf24" if aaii_spread >= -10 else "#f87171"
            al = "강세 우세" if aaii_spread >= 10 else "팽팽" if aaii_spread >= -10 else "약세 우세"
            a_pct = min(max((aaii_spread + 50) / 100 * 100, 0), 100)
            st.markdown(f"""
<div class="idx-card" style="text-align:left;padding:16px 18px">
  <div style="font-size:0.65em;opacity:0.45;font-weight:600;letter-spacing:0.3px;margin-bottom:8px">📋 AAII 투자자 심리 (주간)</div>
  <div style="display:flex;align-items:baseline;gap:8px">
    <span style="font-size:1.55em;font-weight:800;color:{ac};letter-spacing:-1px">{aaii_spread:+.0f}pt</span>
    <span style="font-size:0.72em;color:{ac};font-weight:700">{al}</span>
  </div>
  <div class="fng-bar-wrap">
    <div class="fng-bar" style="width:{a_pct:.1f}%;background:linear-gradient(90deg,#f87171,{ac})"></div>
  </div>
  <div style="font-size:0.62em;opacity:0.38;margin-top:2px">강세 {aaii_bull:.0f}% · 약세 {aaii_bear:.0f}% &nbsp;({aaii_date})</div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown(mk_card("📋","AAII 심리","—"), unsafe_allow_html=True)

    # ── 거시 경제지표 (FRED) ──
    st.markdown(sec_hdr("🏛️", "거시 경제지표"), unsafe_allow_html=True)

    fred_key_ok = _secret("fred","api_key") and "여기에" not in _secret("fred","api_key","여기에")
    if not fred_key_ok:
        st.markdown("""
<div style="padding:14px 18px;background:var(--secondary-background-color);
            border:1px dashed rgba(128,128,128,0.2);border-radius:10px;
            font-size:0.84em;opacity:0.7;line-height:1.9">
  🔑 <b>FRED API 키 미설정</b><br>
  <a href="https://fred.stlouisfed.org/docs/api/api_key.html" target="_blank"
     style="color:#3b82f6">fred.stlouisfed.org</a> 에서 무료 발급 후
  <code style="color:#3b82f6;background:rgba(59,130,246,0.08);padding:1px 6px;border-radius:4px">.streamlit/secrets.toml</code>
  의 <code style="color:#3b82f6;background:rgba(59,130,246,0.08);padding:1px 6px;border-radius:4px">[fred] api_key</code> 에 입력하세요.
</div>""", unsafe_allow_html=True)
    else:
        def fred_card(icon, label, val, unit, chg, date, color_fn=None):
            if val is None:
                return mk_card(icon, label, "—")
            fc = color_fn(val) if color_fn else "#60a5fa"
            chg_html = ""
            if chg is not None:
                ca = "▲" if chg >= 0 else "▼"
                cc = "#ef4444" if chg >= 0 else "#22c55e"  # 금리·CPI는 오르면 나쁨
                chg_html = f'<div style="font-size:0.72em;color:{cc};font-weight:600;margin-top:3px">{ca} {abs(chg):.2f}{unit}</div>'
            m = date[2:7] if date else ""  # "YYYY-MM-DD" → "YY-MM"
            return f"""
<div class="idx-card" style="text-align:left;padding:16px 18px">
  <div style="font-size:0.63em;opacity:0.45;font-weight:600;letter-spacing:0.3px;margin-bottom:7px">{icon} {label}</div>
  <div style="display:flex;align-items:baseline;gap:6px">
    <span style="font-size:1.45em;font-weight:800;color:{fc};letter-spacing:-1px">{val:.2f}</span>
    <span style="font-size:0.72em;color:{fc};font-weight:600">{unit}</span>
  </div>
  {chg_html}
  <div style="font-size:0.6em;opacity:0.3;margin-top:4px">{m}</div>
</div>"""

        # 데이터 호출
        ff_v,  ff_c,  ff_d  = fred_latest("FEDFUNDS")
        g10_v, g10_c, g10_d = fred_latest("DGS10")
        g2_v,  g2_c,  g2_d  = fred_latest("DGS2")
        cpi_v, cpi_c, cpi_d = fred_cpi_yoy()
        un_v,  un_c,  un_d  = fred_latest("UNRATE")

        spread_v = (g10_v - g2_v) if (g10_v and g2_v) else None
        spread_c = None
        if spread_v is not None and g10_c is not None and g2_c is not None:
            spread_c = g10_c - g2_c

        fc1, fc2, fc3, fc4, fc5, fc6 = st.columns(6)
        with fc1:
            st.markdown(fred_card("🏦","기준금리", ff_v,"%", ff_c, ff_d,
                lambda v: "#f87171" if v>5 else "#fbbf24" if v>3 else "#34d399"), unsafe_allow_html=True)
        with fc2:
            st.markdown(fred_card("📈","10년물 국채", g10_v,"%", g10_c, g10_d,
                lambda v: "#60a5fa"), unsafe_allow_html=True)
        with fc3:
            st.markdown(fred_card("📉","2년물 국채", g2_v,"%", g2_c, g2_d,
                lambda v: "#60a5fa"), unsafe_allow_html=True)
        with fc4:
            def spread_color(v):
                return "#34d399" if v > 0.5 else "#fbbf24" if v > 0 else "#f87171"
            st.markdown(fred_card("↕️","장단기 스프레드", spread_v,"%p", spread_c, g10_d,
                spread_color), unsafe_allow_html=True)
        with fc5:
            st.markdown(fred_card("🔥","CPI(YoY)", cpi_v,"%", cpi_c, cpi_d,
                lambda v: "#f87171" if v>4 else "#fbbf24" if v>2.5 else "#34d399"), unsafe_allow_html=True)
        with fc6:
            st.markdown(fred_card("👷","실업률", un_v,"%", un_c, un_d,
                lambda v: "#34d399" if v<4 else "#fbbf24" if v<5 else "#f87171"), unsafe_allow_html=True)

    # ── 관심 섹터 (대표 종목 바스켓) ──
    st.markdown(sec_hdr("📊", "관심 섹터"), unsafe_allow_html=True)

    SECTOR_BASKETS = [
        {"icon":"🔲","name":"반도체",
         "tickers":["NVDA","TSM","AVGO","AMD","ARM","QCOM","MU","INTC","005930.KS","000660.KS"]},
        {"icon":"🤖","name":"AI\n소프트웨어",
         "tickers":["MSFT","GOOGL","META","AMZN","ORCL","CRM","PLTR","AI","PATH"]},
        {"icon":"☁️","name":"클라우드",
         "tickers":["AMZN","MSFT","GOOGL","SNOW","NET","DDOG","MDB","CFLT","GTLB"]},
        {"icon":"💡","name":"AI 광통신",
         "tickers":["COHR","LITE","MRVL","GLW","CIEN","GFS","AAOI","POET"]},
        {"icon":"⚡","name":"전력\n인프라",
         "tickers":["NEE","CEG","VST","PWR","NVT","PRIM","015760.KS","010120.KS"]},
        {"icon":"⚛️","name":"원자력",
         "tickers":["CEG","BWXT","CCJ","OKLO","NNE","SMR","LTBR","034020.KS","052690.KS"]},
        {"icon":"🦾","name":"휴머노이드\n로봇",
         "tickers":["TSLA","NVDA","ABB","ROK","HON","005380.KS","454910.KS","277810.KQ","108490.KQ"]},
        {"icon":"🛡️","name":"방산",
         "tickers":["RTX","LMT","NOC","BA","GD","012450.KS","079550.KS","064350.KS","047810.KS"]},
        {"icon":"🧬","name":"바이오",
         "tickers":["LLY","ABBV","TEVA","RXRX","ABSI","SDAI","SANA","EXAI","207940.KS","068270.KS"]},
        {"icon":"🔮","name":"양자\n컴퓨팅",
         "tickers":["IBM","IONQ","RGTI","QUBT","QMCO","ARQQ"]},
        {"icon":"🖥️","name":"데이터\n센터",
         "tickers":["EQIX","AMT","DLR","VRT","DELL","SMCI","HPE","NTAP"]},
        {"icon":"🔬","name":"반도체\n장비",
         "tickers":["ASML","AMAT","LRCX","KLAC","TER","ONTO","042700.KS","039030.KS"]},
        {"icon":"🚢","name":"조선",
         "tickers":["009540.KS","010140.KS","042660.KS","010620.KS"]},
        {"icon":"🔋","name":"2차전지",
         "tickers":["373220.KS","006400.KS","096770.KS","247540.KS","003670.KS","ALB","MP"]},
    ]

    # 전체 티커 한 번에 로딩
    BIGTECH_TKS = ["AAPL","MSFT","GOOGL","AMZN","META","NVDA","TSLA","AVGO","TSM"]
    _all_sector_tks = tuple({tk for cat in SECTOR_BASKETS for tk in cat["tickers"]} | set(BIGTECH_TKS))
    with st.spinner(""):
        _sector_data = get_index_data(list(_all_sector_tks))
        _yearly_data = get_yearly_returns(_all_sector_tks)
        _rsi_data    = get_rsi_data(_all_sector_tks)

    # ── 빅테크 체온계 ──
    st.markdown(sec_hdr("🌡️", "빅테크 체온계"), unsafe_allow_html=True)
    bt_cols = st.columns(len(BIGTECH_TKS))
    for _col, _tk in zip(bt_cols, BIGTECH_TKS):
        _d    = _sector_data.get(_tk)
        _nm   = stock_display_name(_tk, short=True) if _tk in STOCK_NAMES else _tk
        _url  = stock_link_url(_tk)
        with _col:
            if _d:
                _c = "#ef4444" if _d["chg"] >= 0 else "#3b82f6"
                _a = "▲" if _d["chg"] >= 0 else "▼"
                st.markdown(f"""
<div class="idx-card" style="padding:8px 5px;text-align:center">
  <div style="font-size:0.6em;opacity:0.45;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
    <a href="{_url}" target="_blank" style="color:inherit;text-decoration:none">{_nm}</a>
  </div>
  <div style="font-size:0.82em;font-weight:700;letter-spacing:-0.3px;margin-bottom:1px">${_d['price']:,.2f}</div>
  <div style="font-size:0.8em;font-weight:800;color:{_c}">{_a}{abs(_d['chg']):.2f}%</div>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="idx-card" style="padding:8px 5px;text-align:center"><div style="font-size:0.6em;opacity:0.4">{_nm}</div><div style="font-size:0.9em;opacity:0.25">—</div></div>', unsafe_allow_html=True)

    # ── 관심 섹터 ──
    st.markdown(sec_hdr("📊", "관심 섹터"), unsafe_allow_html=True)

    def render_sector_card(cat):
        rows_data = []
        for tk in cat["tickers"]:
            d = _sector_data.get(tk)
            if d is None:
                continue
            rows_data.append((tk, d["chg"]))

        if not rows_data:
            return

        rows_data.sort(key=lambda x: x[1], reverse=True)
        avg   = sum(c for _, c in rows_data) / len(rows_data)
        avg_c = "#ef4444" if avg >= 0 else "#3b82f6"

        rows_html = ""
        for tk, chg in rows_data:
            is_kr = ".KS" in tk or ".KQ" in tk
            flag  = "🇰🇷" if is_kr else "🇺🇸"
            nm    = stock_display_name(tk, short=True) if tk in STOCK_NAMES else tk
            url   = stock_link_url(tk)
            dc    = "#ef4444" if chg >= 0 else "#3b82f6"
            yr    = _yearly_data.get(tk)
            yr_html = f'<span style="color:{"#ef4444" if yr >= 0 else "#3b82f6"}">{yr:+.0f}%</span>' if yr is not None else '<span style="opacity:0.25">—</span>'
            price = _sector_data.get(tk, {}).get("price")
            if price is not None:
                if is_kr:
                    p_html = f'<span style="opacity:0.7">{price:,.0f}</span>'
                else:
                    p_html = f'<span style="opacity:0.7">${price:,.2f}</span>'
            else:
                p_html = '<span style="opacity:0.25">—</span>'
            sig = rsi_signal(_rsi_data.get(tk))
            rows_html += f"""
<div style="display:flex;align-items:center;padding:2px 5px;border-radius:3px">
  <div style="flex:1;font-size:0.75em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0">
    <span style="font-size:0.78em">{sig}</span>
    <a href="{url}" target="_blank" style="color:inherit;text-decoration:none;margin-left:2px">{nm}</a>
  </div>
  <div style="font-size:0.7em;min-width:52px;text-align:right;opacity:0.7">{p_html}</div>
  <div style="font-size:0.75em;font-weight:700;color:{dc};min-width:46px;text-align:right">{chg:+.2f}%</div>
  <div style="font-size:0.7em;min-width:40px;text-align:right;opacity:0.65">{yr_html}</div>
</div>"""

        sector_name = cat['name'].replace('\n', ' ')
        st.markdown(f"""
<div style="background:var(--secondary-background-color);border:1px solid rgba(128,128,128,0.13);
            border-radius:10px;padding:9px 8px 5px;margin-bottom:6px">
  <div style="display:flex;justify-content:space-between;align-items:center;padding:0 5px;margin-bottom:4px">
    <div style="font-size:0.78em;font-weight:700">{cat['icon']} {sector_name}</div>
    <div style="font-size:0.72em;font-weight:700;color:{avg_c}">avg {avg:+.2f}%</div>
  </div>
  <div style="display:flex;font-size:0.58em;opacity:0.3;font-weight:600;letter-spacing:0.4px;
              padding:0 5px 3px;border-bottom:1px solid rgba(128,128,128,0.08);margin-bottom:1px">
    <div style="flex:1">RSI · 종목</div>
    <div style="min-width:52px;text-align:right">현재가</div>
    <div style="min-width:46px;text-align:right">당일</div>
    <div style="min-width:40px;text-align:right">1년</div>
  </div>
  {rows_html}
</div>""", unsafe_allow_html=True)

    # 3열 배치
    for i in range(0, len(SECTOR_BASKETS), 3):
        c1, c2, c3 = st.columns(3)
        with c1:
            render_sector_card(SECTOR_BASKETS[i])
        with c2:
            if i + 1 < len(SECTOR_BASKETS):
                render_sector_card(SECTOR_BASKETS[i + 1])
        with c3:
            if i + 2 < len(SECTOR_BASKETS):
                render_sector_card(SECTOR_BASKETS[i + 2])

    st.markdown("<hr class='dot-divider'>", unsafe_allow_html=True)

    # ── 국내 주요 공시 (DART) ──
    st.markdown(sec_hdr("📋", "국내 주요 공시"), unsafe_allow_html=True)

    dart_key_ok = _secret("dart","api_key") and "여기에" not in _secret("dart","api_key","여기에")
    if not dart_key_ok:
        st.markdown("""
<div style="padding:14px 18px;background:var(--secondary-background-color);
            border:1px dashed rgba(128,128,128,0.2);border-radius:10px;
            font-size:0.84em;opacity:0.7;line-height:1.9">
  🔑 <b>DART API 키 미설정</b><br>
  <a href="https://opendart.fss.or.kr" target="_blank"
     style="color:#3b82f6">opendart.fss.or.kr</a> 에서 무료 발급 후
  <code style="color:#3b82f6;background:rgba(59,130,246,0.08);padding:1px 6px;border-radius:4px">.streamlit/secrets.toml</code>
  의 <code style="color:#3b82f6;background:rgba(59,130,246,0.08);padding:1px 6px;border-radius:4px">[dart] api_key</code> 에 입력하세요.
</div>""", unsafe_allow_html=True)
    else:
        with st.spinner(""):
            dart_items = get_dart_list(days=14, page_count=20)
        if not dart_items:
            st.caption("최근 공시가 없거나 데이터를 불러올 수 없습니다.")
        else:
            # 공시 유형별 배지색
            TYPE_COLOR = {
                "유상증자":"b-amber", "무상증자":"b-green", "전환사채":"b-purple",
                "합병":"b-red", "분할":"b-amber", "자기주식":"b-blue",
                "최대주주변경":"b-red", "불성실공시":"b-red",
            }
            def dart_badge(title):
                for kw, cls in TYPE_COLOR.items():
                    if kw in title:
                        return f'<span class="badge {cls}" style="font-size:0.66em">{kw}</span>'
                return ""

            for item in dart_items[:15]:
                corp  = item.get("corp_name", "")
                title = item.get("report_nm", "")
                date  = item.get("rcept_dt", "")[:8]  # YYYYMMDD
                rcept = item.get("rcept_no", "")
                link  = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept}"
                date_fmt = f"{date[:4]}.{date[4:6]}.{date[6:]}" if len(date)==8 else date
                bdg = dart_badge(title)
                st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:9px 16px;margin-bottom:3px;
            background:var(--secondary-background-color);
            border:1px solid rgba(128,128,128,0.1);border-radius:8px;
            transition:border-color 0.15s">
  <div style="display:flex;align-items:center;gap:10px;min-width:0">
    <span style="font-size:0.82em;font-weight:700;color:#60a5fa;min-width:80px;
                 white-space:nowrap">{corp}</span>
    <a href="{link}" target="_blank"
       style="font-size:0.8em;opacity:0.65;text-decoration:none;
              white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
              max-width:400px">{title}</a>
    {bdg}
  </div>
  <span style="font-size:0.68em;opacity:0.3;flex-shrink:0;margin-left:10px">{date_fmt}</span>
</div>""", unsafe_allow_html=True)

    st.markdown("<hr class='dot-divider'>", unsafe_allow_html=True)

    # ── Claude 브리핑 ──
    st.markdown(sec_hdr("🤖", "Claude 시장 브리핑"), unsafe_allow_html=True)
    bf  = trends.get("claude_briefing", {})
    us  = bf.get("us_market",  "업데이트 대기 중입니다.")
    kr  = bf.get("kr_market",  "업데이트 대기 중입니다.")
    out = bf.get("outlook",    "업데이트 대기 중입니다.")

    bc1, bc2 = st.columns(2)
    with bc1:
        st.markdown(f"""
<div class="briefing-box">
  <div style="font-size:0.65em;color:#2563eb;font-weight:700;letter-spacing:1.5px;margin-bottom:10px">🇺🇸 미국 시장</div>
  {us}
</div>""", unsafe_allow_html=True)
    with bc2:
        st.markdown(f"""
<div class="briefing-box">
  <div style="font-size:0.65em;color:#2563eb;font-weight:700;letter-spacing:1.5px;margin-bottom:10px">🇰🇷 한국 시장</div>
  {kr}
</div>""", unsafe_allow_html=True)

    st.markdown(f"""
<div class="briefing-box" style="border-left-color:#f59e0b">
  <div style="font-size:0.65em;color:#f59e0b;font-weight:700;letter-spacing:1.5px;margin-bottom:10px">🎯 IronMin 포인트</div>
  {out}
</div>""", unsafe_allow_html=True)

    st.markdown("<hr class='dot-divider'>", unsafe_allow_html=True)

    # ── 거래량 급등 모니터링 ──
    st.markdown(sec_hdr("🔥", "IronMin 관심 종목 — 거래량 급등"), unsafe_allow_html=True)

    _all_themes = trends.get("ironmin_themes", [])
    _theme_tickers = []
    for _t in _all_themes:
        _theme_tickers.extend(_t.get("tickers", []))
    _disc_tickers = [s.get("ticker") for s in load_stocks() if s.get("ticker")]
    _monitor_tickers = list(dict.fromkeys(_theme_tickers + _disc_tickers))  # 중복 제거

    with st.spinner("거래량 데이터 계산 중..."):
        _surge = get_volume_surge(_monitor_tickers, lookback=20)

    if not _surge:
        st.caption("거래량 데이터를 불러올 수 없습니다.")
    else:
        # 2배 이상 급등만 필터, 최대 10개
        _surge_filtered = [r for r in _surge if r["ratio"] >= 1.5][:10]
        if not _surge_filtered:
            st.caption("현재 거래량 급등 종목이 없습니다. (기준: 20일 평균 대비 1.5배 이상)")
        else:
            # 헤더 행
            hdr_cols = st.columns([3, 2, 2, 3, 2, 6])
            _hdr_labels = ["종목명 / 티커", "현재가", "등락률", "거래량 배율", "오늘 거래량", "급등 사유 (최신 뉴스)"]
            for _hc, _hl in zip(hdr_cols, _hdr_labels):
                _hc.markdown(f'<div style="font-size:0.65em;opacity:0.38;font-weight:700;letter-spacing:1px;padding-bottom:4px;border-bottom:1px solid rgba(128,128,128,0.12)">{_hl}</div>', unsafe_allow_html=True)

            def _fmt_vol(v):
                if v >= 1e8:   return f"{v/1e8:.1f}억"
                if v >= 1e6:   return f"{v/1e6:.1f}M"
                if v >= 1000:  return f"{v/1000:.0f}K"
                return str(v)

            for _r in _surge_filtered:
                _tk   = _r["ticker"]
                _nm   = _r["name"]
                _px   = _r["price"]
                _chg  = _r["chg"]
                _rat  = _r["ratio"]
                _vtd  = _r["vol_today"]
                _vav  = _r["vol_avg"]
                _cc   = "#ef4444" if _chg >= 0 else "#3b82f6"
                _ca   = "▲" if _chg >= 0 else "▼"
                _rc   = "#f87171" if _rat >= 3 else "#fb923c" if _rat >= 2 else "#fcd34d"
                _bar_w = min(_rat / 5 * 100, 100)
                _pfx = "$" if not (".KS" in _tk or ".KQ" in _tk) else "₩"
                _pfmt = f"{_pfx}{_px:,.2f}" if _px >= 1 else f"{_pfx}{_px:.4f}"
                _news = get_surge_news(_tk)

                r_cols = st.columns([3, 2, 2, 3, 2, 6])
                with r_cols[0]:
                    _lnk = stock_link_url(_tk)
                    st.markdown(f'<div style="padding:7px 0"><div style="font-size:0.85em;font-weight:700"><a href="{_lnk}" target="_blank" rel="noopener" style="color:inherit;text-decoration:none;border-bottom:1px dotted rgba(128,128,128,0.25)">{_nm[:20]}</a></div><div style="font-size:0.7em;opacity:0.4;letter-spacing:0.4px;margin-top:1px">{_tk}</div></div>', unsafe_allow_html=True)
                with r_cols[1]:
                    st.markdown(f'<div style="font-size:0.83em;font-weight:600;padding:7px 0">{_pfmt}</div>', unsafe_allow_html=True)
                with r_cols[2]:
                    st.markdown(f'<div style="font-size:0.83em;font-weight:600;color:{_cc};padding:7px 0">{_ca} {abs(_chg):.2f}%</div>', unsafe_allow_html=True)
                with r_cols[3]:
                    st.markdown(f"""
<div style="padding:7px 0">
  <div style="display:flex;align-items:center;gap:8px">
    <span style="font-size:0.88em;font-weight:700;color:{_rc}">{_rat:.1f}x</span>
    <div style="flex:1;height:4px;background:rgba(128,128,128,0.12);border-radius:3px;overflow:hidden">
      <div style="height:100%;width:{_bar_w:.0f}%;background:{_rc};border-radius:3px;opacity:0.75"></div>
    </div>
  </div>
  <div style="font-size:0.62em;opacity:0.35;margin-top:2px">평균 {_fmt_vol(_vav)}</div>
</div>""", unsafe_allow_html=True)
                with r_cols[4]:
                    st.markdown(f'<div style="font-size:0.8em;opacity:0.65;padding:7px 0">{_fmt_vol(_vtd)}</div>', unsafe_allow_html=True)
                with r_cols[5]:
                    _news_html = f'<span style="opacity:0.7">{_news}</span>' if _news else '<span style="opacity:0.22">—</span>'
                    st.markdown(f'<div style="font-size:0.76em;padding:7px 0;line-height:1.4">{_news_html}</div>', unsafe_allow_html=True)

    st.markdown("<hr class='dot-divider'>", unsafe_allow_html=True)

    # ── 테마 동향 ──
    st.markdown(sec_hdr("🔭", "IronMin 관심 테마"), unsafe_allow_html=True)
    themes = trends.get("ironmin_themes", [])
    if not themes:
        st.info("내일 오전 8시 스크리닝 후 업데이트됩니다.")
    else:
        tc1, tc2 = st.columns(2)
        for i, t in enumerate(themes):
            col = tc1 if i%2==0 else tc2
            with col:
                name    = t.get("theme","")
                icon    = t.get("icon","🔭")
                status  = t.get("status","—")
                summary = t.get("summary","")
                events  = t.get("key_events",[])
                tickers = t.get("tickers",[])
                tk_html = "".join(
                    f'<a href="{stock_link_url(x)}" target="_blank" rel="noopener" style="text-decoration:none"><span class="tag t-blue" title="{x}">{stock_display_name(x, short=True) if x in STOCK_NAMES else x}</span></a>'
                    for x in tickers
                )
                ev_html = "".join(f'<span class="tag t-purple">· {e}</span>' for e in events)
                st.markdown(f"""
<div class="theme-card">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap">
    <div style="font-weight:700;font-size:0.93em">{icon} {name}</div>
    {theme_badge(status)}
  </div>
  <div style="margin-top:8px">{tk_html}</div>
  <div style="margin-top:10px;opacity:0.62;font-size:0.84em;line-height:1.8">{summary}</div>
  {"<div style='margin-top:10px;padding-top:8px;border-top:1px solid rgba(128,128,128,0.1)'>" + ev_html + "</div>" if events else ""}
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# ⚡ 발굴 종목
# ══════════════════════════════════════════════════
elif "발굴 종목" in menu:
    st.markdown("""
<div style="margin-bottom:20px">
  <h1 style="margin-bottom:4px">발굴 종목</h1>
  <div style="font-size:0.75em;opacity:0.42">IronMin 기준(저평가 · 성장성 · 기술 해자)으로 스크리닝한 관심 종목</div>
</div>""", unsafe_allow_html=True)

    # 공통 유니버스
    _SCR_UNIVERSE = list({
        tk for cat in [
            {"tickers":["NVDA","TSM","AVGO","AMD","ARM","QCOM","MU","INTC"]},
            {"tickers":["MSFT","GOOGL","META","AMZN","ORCL","CRM","PLTR","AI","PATH"]},
            {"tickers":["AMZN","MSFT","GOOGL","SNOW","NET","DDOG","MDB","CFLT","GTLB"]},
            {"tickers":["COHR","LITE","MRVL","GLW","CIEN","GFS","AAOI","POET"]},
            {"tickers":["NEE","CEG","VST","PWR","NVT","PRIM"]},
            {"tickers":["CEG","BWXT","CCJ","OKLO","NNE","SMR","LTBR"]},
            {"tickers":["TSLA","NVDA","ABB","ROK","HON"]},
            {"tickers":["RTX","LMT","NOC","BA","GD"]},
            {"tickers":["LLY","ABBV","TEVA","RXRX","ABSI"]},
            {"tickers":["IBM","IONQ","RGTI","QUBT","QMCO","ARQQ"]},
            {"tickers":["EQIX","AMT","DLR","VRT","DELL","SMCI","HPE","NTAP"]},
            {"tickers":["ASML","AMAT","LRCX","KLAC","TER","ONTO"]},
            {"tickers":["ALB","MP"]},
        ]
        for tk in cat["tickers"]
        if ".KS" not in tk and ".KQ" not in tk
    })

    # ── 원클릭 스크리닝 ──
    _disc_existing = {s.get("ticker") for s in load_stocks()}
    _today_str = datetime.today().strftime("%Y-%m-%d")

    _run_col, _info_col = st.columns([2, 3])
    with _run_col:
        _run_all = st.button("🔍 오늘 스크리닝 실행", type="primary", use_container_width=True, key="btn_run_all")
    with _info_col:
        _last_run = st.session_state.get("scr_last_run")
        if _last_run:
            _n_moat = len(st.session_state.get("scr_moat_results", []))
            _n_tr   = len(st.session_state.get("scr_tr_results", []))
            st.markdown(f'<div style="font-size:0.78em;opacity:0.5;padding-top:10px">마지막 실행: {_last_run} &nbsp;·&nbsp; AI해자 {_n_moat}개 · 흑자전환 {_n_tr}개 발견</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:0.78em;opacity:0.4;padding-top:10px">버튼을 눌러 오늘 유망 종목을 스크리닝합니다 (약 1~2분 소요)</div>', unsafe_allow_html=True)

    if _run_all:
        # AI 해자 스크리닝
        _moat_results = []
        _prog = st.progress(0, text="[1/2] AI 해자 스크리닝 중...")
        for _i, _tk in enumerate(_SCR_UNIVERSE):
            _prog.progress((_i+1)/len(_SCR_UNIVERSE)/2, text=f"[1/2] AI 해자 분석 중: {_tk}")
            _fd = get_fundamental_data(_tk)
            if not _fd: continue
            _gm = _fd.get("grossMargin"); _rg = _fd.get("revenueGrowth"); _om = _fd.get("operatingMargin")
            if _gm is None or _rg is None: continue
            if _gm*100 < 40 or _rg*100 < 10: continue
            if (_om or 0) < 0: continue
            _sc = score_ai_moat(_fd)
            if _sc < 4: continue
            _moat_results.append({
                "ticker":_tk, "name":_fd.get("name",_tk), "type":"AI해자",
                "grossMargin":_gm, "revenueGrowth":_rg, "operatingMargin":_om,
                "score":_sc, "marketCap":_fd.get("marketCap"),
            })
        # 흑자전환 예상 스크리닝
        _tr_results = []
        for _i, _tk in enumerate(_SCR_UNIVERSE):
            _prog.progress(0.5 + (_i+1)/len(_SCR_UNIVERSE)/2, text=f"[2/2] 흑자전환 분석 중: {_tk}")
            _td = get_turnaround_data(_tk)
            if not _td: continue
            _gm = _td.get("grossMargin"); _rg = _td.get("revenueGrowth"); _om = _td.get("operatingMargin")
            if _gm is None or _rg is None: continue
            if _gm*100 < 35 or _rg*100 < 15: continue
            # 핵심 필터: 현재 적자이거나 5% 미만 흑자 (아직 본격 수익화 전)
            if (_om or 0) >= 0.05: continue
            # 최소한 분기 개선 추세 또는 포워드 EPS 전환 신호 중 하나는 있어야 함
            _eps_turn = _td.get("eps_turning", False)
            _op_tr    = _td.get("op_trend") or 0
            if not _eps_turn and _op_tr < 1: continue
            _sc = score_turnaround(_td)
            if _sc < 4: continue
            _tr_results.append({
                "ticker":_tk, "name":_td.get("name",_tk), "type":"흑자전환",
                "grossMargin":_gm, "revenueGrowth":_rg, "operatingMargin":_om,
                "op_trend":_op_tr, "eps_turning":_eps_turn,
                "forwardEps":_td.get("forwardEps"), "trailingEps":_td.get("trailingEps"),
                "score":_sc, "marketCap":_td.get("marketCap"),
            })
        _prog.empty()
        _moat_results.sort(key=lambda x: x["score"], reverse=True)
        _tr_results.sort(key=lambda x: x["score"], reverse=True)
        st.session_state["scr_moat_results"] = _moat_results
        st.session_state["scr_tr_results"]   = _tr_results
        st.session_state["scr_last_run"]      = _today_str
        st.rerun()

    # 결과 표시 (session_state 유지)
    _moat_res = st.session_state.get("scr_moat_results", [])
    _tr_res   = st.session_state.get("scr_tr_results", [])

    if _moat_res or _tr_res:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        def _render_scr_table(rows, score_max, label_color):
            """스크리닝 결과 테이블 + 관심목록 추가 버튼"""
            _disc_now = {s.get("ticker") for s in load_stocks()}
            _hcols = st.columns([2,3,2,2,2,1,2])
            for _hc, _hl in zip(_hcols, ["종목","이름","총이익률","매출성장","영업이익률","점수","추가"]):
                _hc.markdown(f'<div style="font-size:0.63em;opacity:0.35;font-weight:700;letter-spacing:1px;padding-bottom:4px;border-bottom:1px solid rgba(128,128,128,0.1)">{_hl}</div>', unsafe_allow_html=True)
            for _r in rows:
                _tk2 = _r["ticker"]
                _already = _tk2 in _disc_now
                _rc = st.columns([2,3,2,2,2,1,2])
                _lnk = stock_link_url(_tk2)
                _mc  = f'${_r["marketCap"]/1e9:.0f}B' if _r.get("marketCap") else "—"
                _om_v = f'{_r["operatingMargin"]*100:.1f}%' if _r.get("operatingMargin") is not None else "—"
                _rg_c = "#ef4444" if _r["revenueGrowth"]>=0.30 else "#fbbf24" if _r["revenueGrowth"]>=0.15 else "inherit"
                _stars = "★" * min(_r["score"], score_max)
                with _rc[0]: st.markdown(f'<div style="padding:5px 0;font-size:0.82em;font-weight:700"><a href="{_lnk}" target="_blank" style="color:inherit;text-decoration:none">{_tk2}</a> <span style="opacity:0.28;font-size:0.72em">{_mc}</span></div>', unsafe_allow_html=True)
                with _rc[1]: st.markdown(f'<div style="padding:5px 0;font-size:0.78em;opacity:0.65">{_r["name"][:20]}</div>', unsafe_allow_html=True)
                with _rc[2]: st.markdown(f'<div style="padding:5px 0;font-size:0.82em;font-weight:600;color:#34d399">{_r["grossMargin"]*100:.1f}%</div>', unsafe_allow_html=True)
                with _rc[3]: st.markdown(f'<div style="padding:5px 0;font-size:0.82em;font-weight:600;color:{_rg_c}">{_r["revenueGrowth"]*100:+.1f}%</div>', unsafe_allow_html=True)
                with _rc[4]: st.markdown(f'<div style="padding:5px 0;font-size:0.82em;font-weight:600;color:{label_color}">{_om_v}</div>', unsafe_allow_html=True)
                with _rc[5]: st.markdown(f'<div style="padding:5px 0;font-size:0.75em;color:#fbbf24">{_stars}</div>', unsafe_allow_html=True)
                with _rc[6]:
                    if _already:
                        st.markdown('<div style="padding:5px 0;font-size:0.72em;opacity:0.35">✓ 목록에 있음</div>', unsafe_allow_html=True)
                    else:
                        if st.button("＋ 추가", key=f"add_{_tk2}_{_r['type']}"):
                            _info2 = get_info(_tk2)
                            _nm2   = _info2.get("shortName") or _tk2 if _info2 else _tk2
                            _new_s = {
                                "ticker": _tk2, "name": _nm2,
                                "market": "US",
                                "sector": "🤖 AI_반도체" if _r["type"]=="AI해자" else "🌐 기술_전반",
                                "added_date": _today_str,
                                "current_status": "관찰 중",
                                "discovery_reason": f"IronMin 스크리너 [{_r['type']}] — 매출총이익률 {_r['grossMargin']*100:.1f}%, 매출성장 {_r['revenueGrowth']*100:+.1f}%",
                                "catalysts": [f"매출성장 {_r['revenueGrowth']*100:.0f}%", "AI·기술 테마"],
                                "risks": ["밸류에이션 점검 필요"],
                                "buy_triggers": ["기술적 돌파", "52주 신고가"],
                                "target_price": None, "stop_loss": None,
                                "ironmin_score": min(_r["score"], 5),
                                "notes": f"스크리닝 자동 발굴 ({_today_str}). 추가 분석 후 상태 업데이트 권장.",
                            }
                            _all = load_stocks()
                            _all.append(_new_s)
                            save_stocks(_all)
                            st.success(f"{_tk2} 관심목록에 추가!")
                            st.rerun()

        if _moat_res:
            st.markdown(f'<div style="font-size:0.8em;font-weight:700;margin:10px 0 6px">🏰 AI 해자 — {len(_moat_res)}개</div>', unsafe_allow_html=True)
            _render_scr_table(_moat_res, 8, "#34d399")

        if _tr_res:
            st.markdown(f'<div style="font-size:0.8em;font-weight:700;margin:16px 0 6px">🚀 흑자전환 예상 — {len(_tr_res)}개</div>', unsafe_allow_html=True)
            # 흑자전환용 확장 테이블 (포워드 EPS 전환 신호 포함)
            _disc_now2 = {s.get("ticker") for s in load_stocks()}
            _htr = st.columns([2,3,2,2,2,2,1,2])
            for _hc, _hl in zip(_htr, ["종목","이름","총이익률","매출성장","분기추세","EPS전환","점수","추가"]):
                _hc.markdown(f'<div style="font-size:0.63em;opacity:0.35;font-weight:700;letter-spacing:1px;padding-bottom:4px;border-bottom:1px solid rgba(128,128,128,0.1)">{_hl}</div>', unsafe_allow_html=True)
            for _r in _tr_res:
                _tk2     = _r["ticker"]
                _already = _tk2 in _disc_now2
                _rc      = st.columns([2,3,2,2,2,2,1,2])
                _lnk     = stock_link_url(_tk2)
                _mc      = f'${_r["marketCap"]/1e9:.0f}B' if _r.get("marketCap") else "—"
                _rg_c    = "#ef4444" if _r["revenueGrowth"]>=0.30 else "#fbbf24" if _r["revenueGrowth"]>=0.15 else "inherit"
                _tr_icon = "📈📈📈" if _r["op_trend"]>=3 else "📈📈" if _r["op_trend"]>=2 else "📈" if _r["op_trend"]==1 else "—"
                _feps    = _r.get("forwardEps"); _teps = _r.get("trailingEps")
                _eps_str = f'<span style="color:#4ade80;font-weight:700">⚡ 전환</span>' if _r.get("eps_turning") else (f'<span style="opacity:0.5;font-size:0.85em">{_feps:+.2f}</span>' if _feps else "—")
                _stars   = "★" * min(_r["score"], 10)
                with _rc[0]: st.markdown(f'<div style="padding:5px 0;font-size:0.82em;font-weight:700"><a href="{_lnk}" target="_blank" style="color:inherit;text-decoration:none">{_tk2}</a> <span style="opacity:0.28;font-size:0.72em">{_mc}</span></div>', unsafe_allow_html=True)
                with _rc[1]: st.markdown(f'<div style="padding:5px 0;font-size:0.78em;opacity:0.65">{_r["name"][:20]}</div>', unsafe_allow_html=True)
                with _rc[2]: st.markdown(f'<div style="padding:5px 0;font-size:0.82em;font-weight:600;color:#34d399">{_r["grossMargin"]*100:.1f}%</div>', unsafe_allow_html=True)
                with _rc[3]: st.markdown(f'<div style="padding:5px 0;font-size:0.82em;font-weight:600;color:{_rg_c}">{_r["revenueGrowth"]*100:+.1f}%</div>', unsafe_allow_html=True)
                with _rc[4]: st.markdown(f'<div style="padding:5px 0;font-size:0.85em">{_tr_icon}</div>', unsafe_allow_html=True)
                with _rc[5]: st.markdown(f'<div style="padding:5px 0;font-size:0.82em">{_eps_str}</div>', unsafe_allow_html=True)
                with _rc[6]: st.markdown(f'<div style="padding:5px 0;font-size:0.75em;color:#fbbf24">{_stars}</div>', unsafe_allow_html=True)
                with _rc[7]:
                    if _already:
                        st.markdown('<div style="padding:5px 0;font-size:0.72em;opacity:0.35">✓ 목록에 있음</div>', unsafe_allow_html=True)
                    else:
                        if st.button("＋ 추가", key=f"add_{_tk2}_tr2"):
                            _info2  = get_info(_tk2)
                            _nm2    = (_info2.get("shortName") or _tk2) if _info2 else _tk2
                            _reason = f"흑자전환 예상 — 매출총이익률 {_r['grossMargin']*100:.1f}%, 매출성장 {_r['revenueGrowth']*100:+.1f}%"
                            if _r.get("eps_turning"): _reason += f", 포워드EPS 흑자전환 예상(+{_feps:.2f})"
                            _all = load_stocks()
                            _all.append({
                                "ticker":_tk2, "name":_nm2, "market":"US",
                                "sector":"🌐 기술_전반",
                                "added_date":_today_str, "current_status":"관찰 중",
                                "discovery_reason":_reason,
                                "catalysts":["흑자전환 임박","매출 고성장","분기 적자 축소"],
                                "risks":["흑자전환 지연 리스크","희석 우려"],
                                "buy_triggers":["첫 흑자 분기 발표","어닝서프라이즈"],
                                "target_price":None,"stop_loss":None,
                                "ironmin_score":min(_r["score"]//2, 5),
                                "notes":f"흑자전환 예상 스크리너 자동 발굴 ({_today_str}).",
                            })
                            save_stocks(_all)
                            st.success(f"{_tk2} 관심목록에 추가!")
                            st.rerun()

    elif not st.session_state.get("scr_last_run"):
        st.markdown('<div style="font-size:0.82em;opacity:0.4;margin:20px 0;text-align:center">스크리닝 결과가 여기에 표시됩니다</div>', unsafe_allow_html=True)

    st.markdown("<hr class='dot-divider'>", unsafe_allow_html=True)

    stocks = load_stocks()
    if not stocks:
        st.info("아직 발굴된 종목이 없습니다.")
    else:
        f1, f2, _ = st.columns([1,1,2])
        with f1: sf = st.selectbox("상태", ["전체","관찰 중","매수 고려","주의"])
        with f2: mf = st.selectbox("시장", ["전체","US","KR"])

        filtered = [s for s in stocks
                    if (sf=="전체" or s.get("current_status")==sf)
                    and (mf=="전체" or s.get("market")==mf)]

        st.markdown(f'<div style="color:#2d4a72;font-size:0.77em;margin-bottom:16px">{len(filtered)}개 종목</div>', unsafe_allow_html=True)

        for s in filtered:
            tk     = s.get("ticker","")
            name   = s.get("name", tk)
            market = s.get("market","US")
            sector = s.get("sector","")
            added  = s.get("added_date","")
            status = s.get("current_status","관찰 중")
            reason = s.get("discovery_reason","")
            cats   = s.get("catalysts",[])
            risks  = s.get("risks",[])
            trigs  = s.get("buy_triggers",[])
            target = s.get("target_price")
            stop   = s.get("stop_loss")
            score  = s.get("ironmin_score", 3)
            notes  = s.get("notes","")

            price   = get_price(tk)
            flag    = "🇺🇸" if market=="US" else "🇰🇷"
            pfx     = "$" if market=="US" else "₩"
            p_str   = f"{pfx}{price:,.2f}" if price else "—"
            tgt_str = f"{pfx}{target:,.2f}" if target else "—"
            stp_str = f"{pfx}{stop:,.2f}"   if stop   else "—"

            cats_h  = "".join(f'<span class="tag t-green">✦ {c}</span>' for c in cats)
            risks_h = "".join(f'<span class="tag t-red">⚠ {r}</span>'  for r in risks)
            trigs_h = "".join(f'<span class="tag t-amber">▶ {t}</span>'for t in trigs)

            st.markdown(f"""
<div class="card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px">
    <div>
      <span style="font-size:1.2em;font-weight:800;letter-spacing:-0.3px">{flag} {stock_linked_name(tk) if tk in STOCK_NAMES else f'<a href="{stock_link_url(tk)}" target="_blank" rel="noopener" style="color:inherit;text-decoration:none;border-bottom:1px dotted rgba(128,128,128,0.25)">{name}</a>'}</span>
      <span style="opacity:0.35;margin-left:8px;font-size:0.72em;letter-spacing:0.3px">{tk}</span>
      &nbsp;{badge(status)}
    </div>
    <div style="text-align:right">
      <div style="font-size:1.5em;font-weight:800;letter-spacing:-0.5px">{p_str}</div>
      <div style="font-size:0.68em;opacity:0.38;margin-top:3px">목표 {tgt_str} &nbsp;·&nbsp; 손절 {stp_str}</div>
    </div>
  </div>
  <div style="margin-top:6px;font-size:0.7em;opacity:0.38;letter-spacing:0.2px">
    {sector} &nbsp;·&nbsp; 발굴 {added} &nbsp;·&nbsp; {stars_html(score)}
  </div>
  <div style="margin-top:12px;opacity:0.68;font-size:0.85em;line-height:1.8">{reason}</div>
  <hr class="dot-divider">
  <div style="display:flex;gap:32px;flex-wrap:wrap">
    <div style="flex:1;min-width:280px">
      <div style="margin-bottom:6px"><span style="font-size:0.62em;font-weight:700;opacity:0.38;letter-spacing:1.5px;text-transform:uppercase">카탈리스트</span></div>
      <div>{cats_h}</div>
    </div>
    <div style="flex:1;min-width:280px">
      <div style="margin-bottom:6px"><span style="font-size:0.62em;font-weight:700;opacity:0.38;letter-spacing:1.5px;text-transform:uppercase">리스크</span></div>
      <div>{risks_h}</div>
    </div>
    <div style="flex:1;min-width:280px">
      <div style="margin-bottom:6px"><span style="font-size:0.62em;font-weight:700;opacity:0.38;letter-spacing:1.5px;text-transform:uppercase">매수 트리거</span></div>
      <div>{trigs_h}</div>
    </div>
  </div>
  <div style="margin-top:14px;padding:12px 15px;background:rgba(59,130,246,0.05);border-left:2px solid #3b82f6;border-radius:0 8px 8px 0;font-size:0.83em;opacity:0.75;line-height:1.8">
    {notes}
  </div>
</div>""", unsafe_allow_html=True)

            with st.spinner(""):
                _news_list = get_news_kr(tk)
            if _news_list:
                _news_items = ""
                for _n in _news_list:
                    _nl  = _n.get("link","")
                    _nd  = str(_n.get("date",""))[:10]
                    _nt  = _n.get("title","")
                    _anchor = f'<a href="{_nl}" target="_blank" rel="noopener" style="color:inherit;text-decoration:none;border-bottom:1px dotted rgba(128,128,128,0.25)">{_nt}</a>' if _nl else _nt
                    _news_items += f"""
<div style="display:flex;gap:10px;align-items:flex-start;padding:5px 0;border-bottom:1px solid rgba(128,128,128,0.07)">
  <div style="font-size:0.65em;opacity:0.3;white-space:nowrap;padding-top:2px;min-width:60px">{_nd}</div>
  <div style="font-size:0.8em;line-height:1.5;flex:1">{_anchor}</div>
</div>"""
                st.markdown(f"""
<div style="background:var(--secondary-background-color);border:1px solid rgba(128,128,128,0.13);
            border-radius:10px;padding:10px 14px;margin-bottom:4px">
  <div style="font-size:0.6em;font-weight:700;opacity:0.35;letter-spacing:1.5px;margin-bottom:6px">📰 최신 뉴스</div>
  {_news_items}
</div>""", unsafe_allow_html=True)

            with st.spinner(""):
                df_h = get_hist(tk, "1y")
            if not df_h.empty:
                cl_h = df_h["Close"].squeeze()
                ret  = (cl_h.iloc[-1] - cl_h.iloc[0]) / cl_h.iloc[0] * 100
                ret_c = "#ef4444" if ret >= 0 else "#3b82f6"
                ret_a = "▲" if ret >= 0 else "▼"
                ma20 = cl_h.rolling(20).mean()
                ma60 = cl_h.rolling(60).mean()
                fig_s = go.Figure()
                fig_s.add_trace(go.Scatter(x=df_h.index, y=cl_h, mode="lines", name="주가",
                    line=dict(color="#3b82f6", width=2), fill="tozeroy", fillcolor="rgba(59,130,246,0.05)"))
                fig_s.add_trace(go.Scatter(x=df_h.index, y=ma20, mode="lines", name="MA20",
                    line=dict(color="#f59e0b", width=1.2, dash="dot")))
                fig_s.add_trace(go.Scatter(x=df_h.index, y=ma60, mode="lines", name="MA60",
                    line=dict(color="#8b5cf6", width=1.2, dash="dot")))
                if target:
                    fig_s.add_hline(y=target, line_dash="dash", line_color="#4ade80", line_width=1.3,
                        annotation_text=f"목표 {tgt_str}", annotation_font_size=10,
                        annotation_font_color="#4ade80", annotation_position="right")
                if stop:
                    fig_s.add_hline(y=stop, line_dash="dash", line_color="#f87171", line_width=1.3,
                        annotation_text=f"손절 {stp_str}", annotation_font_size=10,
                        annotation_font_color="#f87171", annotation_position="right")
                fig_s.update_layout(height=260, margin=dict(t=36, b=8, l=4, r=80),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(128,128,128,0.03)",
                    legend=dict(orientation="h", x=1, xanchor="right", y=1.12,
                                font=dict(size=10, family="Pretendard"), bgcolor="rgba(0,0,0,0)"),
                    font=dict(family="Pretendard", color="rgba(128,128,128,0.5)"),
                    xaxis=dict(showgrid=False, color="rgba(128,128,128,0.3)", tickfont=dict(size=9)),
                    yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.07)",
                               color="rgba(128,128,128,0.4)", tickfont=dict(size=9)),
                    title=dict(text=f"1년 주가 흐름 &nbsp; <span style='color:{ret_c};font-size:0.9em'>{ret_a} {abs(ret):.1f}%</span>",
                               font=dict(size=11, family="Pretendard"), x=0, xanchor="left"))
                st.plotly_chart(fig_s, use_container_width=True, config={"displayModeBar": False})

            STATUS_OPTS = ["관찰 중", "매수 고려", "주의"]
            cur_idx = STATUS_OPTS.index(status) if status in STATUS_OPTS else 0
            sc1, sc2, sc3 = st.columns([2, 1, 3])
            with sc1:
                new_status = st.selectbox("상태 변경", STATUS_OPTS, index=cur_idx,
                    key=f"status_{tk}", label_visibility="collapsed")
            with sc2:
                if st.button("저장", key=f"save_{tk}", type="primary"):
                    all_stocks = load_stocks()
                    for item in all_stocks:
                        if item.get("ticker") == tk:
                            item["current_status"] = new_status
                            break
                    save_stocks(all_stocks)
                    st.success(f"{tk} → {new_status} 변경 완료")
                    st.rerun()

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# 🔍 종목 심층 분석
# ══════════════════════════════════════════════════
elif "분석" in menu:
    st.markdown("""
<div style="margin-bottom:20px">
  <h1 style="margin-bottom:4px">종목 심층 분석</h1>
  <div style="font-size:0.75em;opacity:0.42">재무지표 · IronMin 스코어 · 기술적 분석 통합</div>
</div>""", unsafe_allow_html=True)

    s1, s2, s3 = st.columns([3, 1, 1])
    with s1:
        stk = st.text_input("종목 검색", placeholder="삼성전자 · POET · NVDA · 005930")
    with s2:
        pm2 = {"3개월":"3mo", "6개월":"6mo", "1년":"1y", "2년":"2y"}
        pl2 = st.selectbox("차트 기간", list(pm2.keys()), index=2)
    with s3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        run2 = st.button("분석 실행", type="primary")

    if run2 and stk.strip():
        tk, _hint2 = resolve_ticker(stk.strip())
        if _hint2:
            st.caption(f"🔍 {_hint2}")
        with st.spinner(""):
            df   = get_hist(tk, pm2[pl2])
            info = get_info(tk)

        if not info or df.empty:
            st.error("데이터를 불러올 수 없습니다. 티커를 확인해주세요.")
        else:
            nm       = stock_display_name(tk) if tk in STOCK_NAMES else (info.get("shortName") or info.get("longName") or tk)
            sector   = info.get("sector", "—")
            industry = info.get("industry", "—")
            biz      = info.get("longBusinessSummary", "")
            is_kr_a  = ".KS" in tk or ".KQ" in tk
            flag     = "🇰🇷" if is_kr_a else "🇺🇸"
            pfx      = "₩" if is_kr_a else "$"
            px_dec   = 0 if is_kr_a else 2

            cl    = df["Close"].squeeze()
            lx    = cl.iloc[-1]
            prev  = info.get("previousClose") or (cl.iloc[-2] if len(cl) >= 2 else lx)
            chg   = (lx - prev) / prev * 100 if prev else 0
            hi52  = info.get("fiftyTwoWeekHigh")
            lo52  = info.get("fiftyTwoWeekLow")
            cap   = info.get("marketCap")
            beta  = info.get("beta")

            per   = info.get("trailingPE")
            fper  = info.get("forwardPE")
            pbr   = info.get("priceToBook")
            roe   = info.get("returnOnEquity")
            rev_g = info.get("revenueGrowth")
            eps_g = info.get("earningsGrowth")
            opm   = info.get("operatingMargins")
            dte   = info.get("debtToEquity")
            peg   = info.get("pegRatio")
            eps   = info.get("trailingEps")

            _dart_fin = {}
            if is_kr_a:
                _stock_code = tk.replace(".KS", "").replace(".KQ", "")
                _dart_key_ok = _secret("dart", "api_key") and "여기에" not in _secret("dart", "api_key", "여기에")
                if _dart_key_ok:
                    with st.spinner("🇰🇷 DART 재무데이터 조회 중..."):
                        _corp_code = get_dart_corp_code(_stock_code)
                        if _corp_code:
                            _dart_fin = get_dart_kr_financials(_corp_code)
                    if _dart_fin:
                        if _dart_fin.get("opm")   is not None: opm   = _dart_fin["opm"]
                        if _dart_fin.get("roe")   is not None: roe   = _dart_fin["roe"]
                        if _dart_fin.get("dte")   is not None: dte   = _dart_fin["dte"] / 100
                        if _dart_fin.get("rev_g") is not None: rev_g = _dart_fin["rev_g"]
                        _net  = _dart_fin.get("당기순이익")
                        _eq   = _dart_fin.get("자본총계")
                        _cap  = info.get("marketCap")
                        if _cap and _net and _net > 0 and not per:
                            per = _cap / _net
                        if _cap and _eq and _eq > 0 and not pbr:
                            pbr = _cap / _eq
                else:
                    st.info("🔑 DART API 키를 설정하면 국내주식 재무데이터를 볼 수 있습니다.", icon=None)

            df["MA20"]  = cl.rolling(20).mean()
            df["MA60"]  = cl.rolling(60).mean()
            df["MA120"] = cl.rolling(120).mean()
            df["RSI"]   = calc_rsi(cl)
            df["MACD"], df["SIG"], df["HIST"] = calc_macd(cl)
            m20  = df["MA20"].iloc[-1]
            m60  = df["MA60"].iloc[-1]
            rsi  = df["RSI"].iloc[-1]
            mv   = df["MACD"].iloc[-1]
            ms   = df["SIG"].iloc[-1]

            sc = 0; rsn = []
            if rev_g is not None:
                if rev_g > 0.30:   sc += 2; rsn.append(f"✅ 매출성장 {rev_g*100:.0f}% — 고성장")
                elif rev_g > 0.10: sc += 1; rsn.append(f"✅ 매출성장 {rev_g*100:.0f}%")
                elif rev_g < 0:    sc -= 1; rsn.append(f"❌ 매출 역성장 {rev_g*100:.0f}%")
                else:                        rsn.append(f"➖ 매출성장 {rev_g*100:.0f}%")
            if eps_g and eps_g > 0.20: sc += 1; rsn.append(f"✅ EPS성장 {eps_g*100:.0f}%")
            if per:
                if per < 20:   sc += 2; rsn.append(f"✅ PER {per:.1f} — 저평가")
                elif per < 40: sc += 1; rsn.append(f"➖ PER {per:.1f} — 적정")
                elif per > 80: sc -= 1; rsn.append(f"❌ PER {per:.1f} — 고평가")
                else:                    rsn.append(f"➖ PER {per:.1f}")
            if pbr and pbr < 3: sc += 1; rsn.append(f"✅ PBR {pbr:.2f} — 매력적")
            if roe is not None:
                if roe > 0.15:   sc += 1; rsn.append(f"✅ ROE {roe*100:.1f}%")
                elif roe < 0:    sc -= 1; rsn.append(f"❌ ROE 음수 ({roe*100:.1f}%)")
            if dte is not None:
                if dte < 100:    sc += 1; rsn.append(f"✅ 부채비율 {dte:.0f}% — 안정")
                elif dte > 200:  sc -= 1; rsn.append(f"❌ 부채비율 {dte:.0f}% — 과다")
            if not pd.isna(m60):
                if lx > m60:  sc += 1; rsn.append("✅ 주가 > MA60 (중기 상승)")
                else:         sc -= 1; rsn.append("❌ 주가 < MA60 (중기 하락)")
            if not pd.isna(rsi):
                if 30 <= rsi <= 60: sc += 1; rsn.append(f"✅ RSI {rsi:.0f} — 적정 구간")
                elif rsi > 70:      sc -= 1; rsn.append(f"❌ RSI {rsi:.0f} — 과매수")
                elif rsi < 30:      sc += 1; rsn.append(f"✅ RSI {rsi:.0f} — 과매도(역발상)")

            sc = max(0, min(10, sc))
            stars = round(sc / 2)
            star_html = "".join(['<span class="star-on">★</span>' if i < stars else '<span class="star-off">★</span>' for i in range(5)])

            if sc >= 7:   grade, gcls, gbadge = "강력 관심", "b-green", "t-green"
            elif sc >= 4: grade, gcls, gbadge = "관심 보유", "b-amber", "t-amber"
            else:         grade, gcls, gbadge = "신중 검토", "b-red",   "t-red"

            chg_c = "#ef4444" if chg >= 0 else "#3b82f6"
            chg_a = "▲" if chg >= 0 else "▼"
            price_fmt = f"{pfx}{lx:,.{px_dec}f}" if lx >= 1 else f"{pfx}{lx:.4f}"
            hi_fmt = f"{pfx}{hi52:,.{px_dec}f}" if hi52 else "—"
            lo_fmt = f"{pfx}{lo52:,.{px_dec}f}" if lo52 else "—"
            pos_pct = ""
            if hi52 and lo52 and hi52 > lo52:
                pos_pct = f"{(lx - lo52) / (hi52 - lo52) * 100:.0f}"

            st.markdown(f"""
<div class="card">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;flex-wrap:wrap">
    <div>
      <div style="font-size:1.35em;font-weight:800;letter-spacing:-0.5px">{flag} <a href="{stock_link_url(tk)}" target="_blank" rel="noopener" style="color:inherit;text-decoration:none;border-bottom:1px dotted rgba(128,128,128,0.25)">{nm}</a></div>
      <div style="opacity:0.42;font-size:0.75em;margin-top:3px;letter-spacing:0.3px">{tk}</div>
      <div style="opacity:0.38;font-size:0.72em;margin-top:2px">{sector} &nbsp;·&nbsp; {industry}</div>
      <div style="margin-top:10px">{star_html} &nbsp;<span class="badge {gcls}">{grade}</span> &nbsp;<span style="opacity:0.4;font-size:0.78em">IronMin 스코어 {sc}/10</span></div>
    </div>
    <div style="text-align:right">
      <div style="font-size:2em;font-weight:800;letter-spacing:-1.5px">{price_fmt}</div>
      <div style="color:{chg_c};font-weight:600;font-size:0.9em;margin-top:2px">{chg_a} {abs(chg):.2f}%</div>
      <div style="opacity:0.38;font-size:0.72em;margin-top:6px">시가총액 {fmt(cap)}</div>
    </div>
  </div>
  <div style="margin-top:16px">
    <div style="display:flex;justify-content:space-between;font-size:0.72em;opacity:0.45;margin-bottom:4px">
      <span>52주 저 {lo_fmt}</span>
      <span>현재 위치 {pos_pct}%</span>
      <span>52주 고 {hi_fmt}</span>
    </div>
    <div style="height:5px;background:rgba(128,128,128,0.12);border-radius:4px;overflow:hidden">
      <div style="height:100%;width:{pos_pct or 50}%;background:linear-gradient(90deg,#3b82f6,#8b5cf6);border-radius:4px"></div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

            st.markdown(sec_hdr("📊", "재무 지표"), unsafe_allow_html=True)

            if is_kr_a and _dart_fin:
                def _fmt_krw(v):
                    if v is None: return "N/A"
                    abs_v = abs(v)
                    if abs_v >= 1e12: return f"{'−' if v<0 else ''}₩{abs_v/1e12:.1f}조"
                    if abs_v >= 1e8:  return f"{'−' if v<0 else ''}₩{abs_v/1e8:.0f}억"
                    return f"{'−' if v<0 else ''}₩{abs_v/1e6:.0f}백만"
                _yr_lbl = f"{_dart_fin.get('bsns_year','?')}년 ({_dart_fin.get('fs_div','?')})"
                dart_cards = [
                    ("매출액",     _fmt_krw(_dart_fin.get("매출액"))),
                    ("영업이익",   _fmt_krw(_dart_fin.get("영업이익"))),
                    ("당기순이익", _fmt_krw(_dart_fin.get("당기순이익"))),
                    ("자본총계",   _fmt_krw(_dart_fin.get("자본총계"))),
                ]
                _dart_grid = "".join(f'<div class="idx-card" style="margin-bottom:8px"><div style="font-size:0.60em;opacity:0.40;font-weight:600;margin-bottom:4px">{l}</div><div style="font-size:0.95em;font-weight:700">{v}</div></div>' for l, v in dart_cards)
                st.markdown(f'<div style="font-size:0.7em;opacity:0.5;margin-bottom:6px">📋 DART 재무제표 — {_yr_lbl}</div><div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:10px">{_dart_grid}</div>', unsafe_allow_html=True)

            fi = [
                ("PER (Trailing)", f"{per:.1f}"      if per  else "N/A"),
                ("PER (Forward)",  f"{fper:.1f}"     if fper else "N/A"),
                ("PBR",            f"{pbr:.2f}"      if pbr  else "N/A"),
                ("ROE",            f"{roe*100:.1f}%" if roe  else "N/A"),
                ("매출성장 YoY",   f"{rev_g*100:.1f}%" if rev_g is not None else "N/A"),
                ("EPS성장 YoY",    f"{eps_g*100:.1f}%" if eps_g is not None else "N/A"),
                ("영업이익률",     f"{opm*100:.1f}%" if opm  else "N/A"),
                ("부채비율",       f"{dte*100:.0f}%" if (dte and is_kr_a) else (f"{dte:.0f}%" if dte else "N/A")),
            ]
            cols_fi = st.columns(4)
            for i, (lbl, val) in enumerate(fi):
                with cols_fi[i % 4]:
                    st.markdown(f'<div class="idx-card" style="margin-bottom:10px"><div style="font-size:0.63em;opacity:0.42;font-weight:600;margin-bottom:5px">{lbl}</div><div style="font-size:1.15em;font-weight:700">{val}</div></div>', unsafe_allow_html=True)

            st.markdown(sec_hdr("🎯", "IronMin 스코어 근거"), unsafe_allow_html=True)
            rc1, rc2 = st.columns(2)
            for i, r in enumerate(rsn):
                with rc1 if i % 2 == 0 else rc2:
                    st.markdown(f'<div style="font-size:0.84em;padding:5px 0;border-bottom:1px solid rgba(128,128,128,0.08)">{r}</div>', unsafe_allow_html=True)

            st.markdown(sec_hdr("📈", "기술적 분석"), unsafe_allow_html=True)
            fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                                row_heights=[0.50, 0.20, 0.17, 0.13], vertical_spacing=0.025,
                                subplot_titles=["주가 & 이동평균", "RSI", "MACD", "거래량"])
            fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"],
                low=df["Low"], close=df["Close"], name="OHLC",
                increasing_line_color="#ef4444", decreasing_line_color="#3b82f6"), row=1, col=1)
            for mc, col in {"MA20": "#f59e0b", "MA60": "#3b82f6", "MA120": "#8b5cf6"}.items():
                if mc in df.columns and not df[mc].isna().all():
                    fig.add_trace(go.Scatter(x=df.index, y=df[mc], name=mc,
                                             line=dict(color=col, width=1.4)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
                                     line=dict(color="#f97316", width=1.4)), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", opacity=0.4, row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="#3b82f6", opacity=0.4, row=2, col=1)
            hc = ["#ef4444" if v >= 0 else "#3b82f6" for v in df["HIST"].fillna(0)]
            fig.add_trace(go.Bar(x=df.index, y=df["HIST"], name="Hist", marker_color=hc, opacity=0.7), row=3, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD", line=dict(color="#3b82f6", width=1.2)), row=3, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df["SIG"],  name="Signal", line=dict(color="#f97316", width=1.2, dash="dot")), row=3, col=1)
            if "Volume" in df.columns:
                vol_s = df["Volume"].squeeze()
                vol_ma20 = vol_s.rolling(20).mean()
                vol_colors = ["#ef4444" if df["Close"].iloc[i] >= df["Open"].iloc[i]
                              else "#3b82f6" for i in range(len(df))]
                fig.add_trace(go.Bar(x=df.index, y=vol_s, name="거래량",
                    marker_color=vol_colors, opacity=0.55), row=4, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=vol_ma20, name="거래량 MA20",
                    line=dict(color="#f59e0b", width=1.2, dash="dot")), row=4, col=1)
            fig.update_layout(height=760, xaxis_rangeslider_visible=False,
                legend=dict(orientation="h", y=1.02, x=1, xanchor="right",
                            font=dict(family="Pretendard", size=11)),
                margin=dict(t=28, b=8),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(128,128,128,0.04)",
                font=dict(family="Pretendard", color="rgba(128,128,128,0.6)"))
            fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.08)", color="rgba(128,128,128,0.45)")
            fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.08)", color="rgba(128,128,128,0.45)")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            if biz:
                st.markdown(sec_hdr("🏢", "기업 소개"), unsafe_allow_html=True)
                st.markdown(f'<div class="briefing-box">{biz[:600]}{"..." if len(biz)>600 else ""}</div>',
                            unsafe_allow_html=True)

    elif run2:
        st.warning("티커를 입력해주세요.")


# ══════════════════════════════════════════════════
# 💼 포트폴리오
# ══════════════════════════════════════════════════
elif "포트폴리오" in menu:
    st.markdown("""
<div style="margin-bottom:20px">
  <h1 style="margin-bottom:4px">포트폴리오</h1>
  <div style="font-size:0.75em;color:#2d4a72">섹터별 그룹핑 · 수익률 추적</div>
</div>""", unsafe_allow_html=True)

    SECTORS = [
        "🤖 AI_반도체", "⚡ AI_전력인프라", "💡 AI_광통신", "🏭 AI_데이터센터", "🦾 AI_로봇",
        "⚛️ 원자력", "☀️ 태양광·클린에너지", "🔋 2차전지",
        "🛡️ 방산", "🚀 우주·항공",
        "🧬 바이오·제약", "🌐 기술_전반",
        "🛒 소비재_성장", "🧴 필수소비재·방어",
        "🏠 리츠·인프라", "💰 원자재·귀금속", "🏦 금융", "🗂️ 기타",
    ]
    SECTOR_PAL = {
        "🤖 AI_반도체":"#3b82f6","⚡ AI_전력인프라":"#f59e0b","💡 AI_광통신":"#a78bfa",
        "🏭 AI_데이터센터":"#06b6d4","🦾 AI_로봇":"#10b981","⚛️ 원자력":"#f97316",
        "☀️ 태양광·클린에너지":"#fcd34d","🔋 2차전지":"#34d399","🛡️ 방산":"#e2645a",
        "🚀 우주·항공":"#c084fc","🧬 바이오·제약":"#f472b6","🌐 기술_전반":"#60a5fa",
        "🛒 소비재_성장":"#fb923c","🧴 필수소비재·방어":"#86efac","🏠 리츠·인프라":"#67e8f9",
        "💰 원자재·귀금속":"#fbbf24","🏦 금융":"#94a3b8","🗂️ 기타":"#475569",
    }

    with st.expander("＋ 종목 추가", expanded=not st.session_state.portfolio):
        a1, a2, a3 = st.columns(3)
        with a1: atk  = st.text_input("티커", placeholder="AAPL · 005930.KS")
        with a2: asec = st.selectbox("섹터", SECTORS)
        with a3: aqty = st.number_input("수량", min_value=1, value=1)
        b1, b2, b3 = st.columns(3)
        with b1: apx  = st.number_input("매수가 ($·₩)", min_value=0.01, value=100.0, step=0.01)
        with b2: adt  = st.date_input("매수일", value=datetime.today())
        with b3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("추가", type="primary"):
                if atk.strip():
                    info = get_info(atk.strip().upper())
                    _atk_up = atk.strip().upper()
                    _mapped_name = stock_display_name(_atk_up) if _atk_up in STOCK_NAMES else (info.get("shortName") or _atk_up)
                    st.session_state.portfolio.append({
                        "ticker": _atk_up, "name": _mapped_name, "sector": asec,
                        "qty": aqty, "buy_price": apx, "buy_date": str(adt)
                    })
                    st.success(f"{atk.upper()} ({asec}) 추가됨")
                    st.rerun()

    if not st.session_state.portfolio:
        st.info("보유 종목을 추가해주세요.")
    else:
        enriched = []
        ti = tv = 0.0
        for i, it in enumerate(st.session_state.portfolio):
            cur  = get_price(it["ticker"])
            inv  = it["qty"] * it["buy_price"]
            val  = it["qty"] * cur if cur else inv
            pnl  = val - inv
            pp   = pnl / inv * 100 if inv else 0
            ti  += inv; tv += val
            enriched.append({
                "_i": i, "sector": it.get("sector", "🗂️ 기타"),
                "ticker": it["ticker"], "name": it["name"],
                "qty": it["qty"], "buy_px": it["buy_price"],
                "cur_px": cur, "inv": inv, "val": val,
                "pnl": pnl, "pp": pp, "buy_date": it["buy_date"],
            })
        tp  = tv - ti
        tpp = tp / ti * 100 if ti else 0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("총 투자금", f"{ti:,.0f}")
        m2.metric("총 평가금", f"{tv:,.0f}")
        m3.metric("총 수익금", f"{tp:+,.0f}")
        m4.metric("총 수익률", f"{tpp:+.2f}%")

        st.markdown("<hr class='dot-divider'>", unsafe_allow_html=True)

        from collections import defaultdict
        by_sector = defaultdict(list)
        for row in enriched:
            by_sector[row["sector"]].append(row)
        ordered_sectors = [s for s in SECTORS if s in by_sector]

        for sec in ordered_sectors:
            rows   = by_sector[sec]
            s_inv  = sum(r["inv"] for r in rows)
            s_val  = sum(r["val"] for r in rows)
            s_pnl  = s_val - s_inv
            s_pp   = s_pnl / s_inv * 100 if s_inv else 0
            s_wt   = s_val / tv * 100 if tv else 0
            color  = SECTOR_PAL.get(sec, "#475569")
            pnl_c  = "#ef4444" if s_pnl >= 0 else "#3b82f6"
            pnl_a  = "▲" if s_pnl >= 0 else "▼"

            st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:10px 16px;margin-bottom:6px;
            background:linear-gradient(90deg,{color}18,transparent);
            border-left:3px solid {color};border-radius:0 8px 8px 0">
  <div style="display:flex;align-items:center;gap:10px">
    <span style="font-size:0.9em;font-weight:700">{sec}</span>
    <span style="font-size:0.68em;opacity:0.5;background:rgba(128,128,128,0.1);padding:2px 8px;border-radius:10px">{len(rows)}종목 · 비중 {s_wt:.1f}%</span>
  </div>
  <div style="text-align:right">
    <span style="font-size:0.82em;font-weight:700;color:{pnl_c}">{pnl_a} {abs(s_pp):.2f}%</span>
    <span style="font-size:0.72em;opacity:0.45;margin-left:8px">{s_pnl:+,.0f}</span>
  </div>
</div>""", unsafe_allow_html=True)

            for r in rows:
                _r_kr  = ".KS" in r["ticker"] or ".KQ" in r["ticker"]
                _r_pfx = "₩" if _r_kr else "$"
                _r_dec = 0 if _r_kr else 2
                cur_str = f"{_r_pfx}{r['cur_px']:,.{_r_dec}f}" if r["cur_px"] else "—"
                buy_str = f"{_r_pfx}{r['buy_px']:,.{_r_dec}f}"
                pnl_str = f"{_r_pfx}{r['pnl']:+,.{_r_dec}f}"
                pc = "#ef4444" if r["pp"] >= 0 else "#3b82f6"
                pa = "▲" if r["pp"] >= 0 else "▼"
                inv_w = r["val"] / tv * 100 if tv else 0
                st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:8px 16px 8px 24px;margin-bottom:3px;
            background:var(--secondary-background-color);
            border:1px solid rgba(128,128,128,0.1);border-radius:8px">
  <div>
    <div style="font-size:0.85em;font-weight:700"><a href="{stock_link_url(r['ticker'])}" target="_blank" rel="noopener" style="color:inherit;text-decoration:none;border-bottom:1px dotted rgba(128,128,128,0.25)">{stock_display_name(r['ticker']) if r['ticker'] in STOCK_NAMES else r['name']}</a></div>
    <div style="font-size:0.68em;opacity:0.38;margin-top:1px">{r['ticker']} · {r['qty']}주 · 매수 {buy_str}</div>
  </div>
  <div style="display:flex;align-items:center;gap:20px;text-align:right">
    <span style="font-size:0.82em;opacity:0.65">{cur_str}</span>
    <span style="font-size:0.82em;font-weight:700;color:{pc}">{pa} {abs(r['pp']):.2f}%</span>
    <span style="font-size:0.78em;opacity:0.45">{pnl_str}</span>
    <span style="font-size:0.68em;opacity:0.3">{inv_w:.1f}%</span>
  </div>
</div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        st.markdown("<hr class='dot-divider'>", unsafe_allow_html=True)
        all_tks = [r["ticker"] for r in enriched]
        dc1, dc2 = st.columns([3, 1])
        with dc1: dtk = st.selectbox("종목 삭제", all_tks)
        with dc2:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("삭제"):
                for idx, p in enumerate(st.session_state.portfolio):
                    if p["ticker"] == dtk:
                        st.session_state.portfolio.pop(idx)
                        break
                st.rerun()

        if len(enriched) >= 1:
            st.markdown("<hr class='dot-divider'>", unsafe_allow_html=True)
            ch1, ch2 = st.columns(2)
            with ch1:
                st.markdown(sec_hdr("🥧", "섹터 비중"), unsafe_allow_html=True)
                sec_vals = [(s, sum(r["val"] for r in by_sector[s])) for s in ordered_sectors]
                s_lbls   = [s for s, _ in sec_vals]
                s_vs     = [v for _, v in sec_vals]
                s_colors = [SECTOR_PAL.get(s, "#475569") for s in s_lbls]
                fig = go.Figure(go.Pie(labels=s_lbls, values=s_vs, hole=0.58,
                    textinfo="label+percent",
                    marker=dict(colors=s_colors, line=dict(color="#060a12", width=2)),
                    textfont=dict(family="Pretendard", size=11)))
                fig.update_layout(height=320, margin=dict(t=8, b=8, l=8, r=8),
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#7c9ab8", family="Pretendard"), showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            with ch2:
                st.markdown(sec_hdr("📈", "섹터별 수익률"), unsafe_allow_html=True)
                sec_pps = []
                for s in ordered_sectors:
                    rows_s = by_sector[s]
                    si = sum(r["inv"] for r in rows_s)
                    sv = sum(r["val"] for r in rows_s)
                    sec_pps.append((s, (sv - si) / si * 100 if si else 0))
                sec_pps_sorted = sorted(sec_pps, key=lambda x: x[1], reverse=True)
                bar_lbls   = [x[0] for x in sec_pps_sorted]
                bar_vals   = [x[1] for x in sec_pps_sorted]
                bar_colors = [SECTOR_PAL.get(l, "#475569") if v >= 0 else "#ef4444"
                              for l, v in sec_pps_sorted]
                fig2 = go.Figure(go.Bar(x=bar_vals, y=bar_lbls, orientation="h",
                    marker_color=bar_colors, opacity=0.85,
                    text=[f"{v:+.2f}%" for v in bar_vals], textposition="outside",
                    textfont=dict(color="rgba(128,128,128,0.7)", size=10, family="Pretendard")))
                fig2.update_layout(height=320, margin=dict(t=8, b=8, l=8, r=60),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(128,128,128,0.04)",
                    font=dict(color="#4d7ab5", family="Pretendard"),
                    xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.08)",
                               color="#2d4a72", ticksuffix="%", zeroline=True),
                    yaxis=dict(showgrid=False, color="#7c9ab8", tickfont=dict(size=10)))
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════════
# 📊 매매 신호
# ══════════════════════════════════════════════════
elif "매매 신호" in menu:
    st.markdown("""
<div style="margin-bottom:20px">
  <h1 style="margin-bottom:4px">매매 신호 분석</h1>
  <div style="font-size:0.75em;color:#2d4a72">이동평균 · RSI · MACD + 재무 지표 복합 분석</div>
</div>""", unsafe_allow_html=True)

    s1,s2,s3=st.columns([2,1,1])
    with s1: stk=st.text_input("종목 검색",placeholder="삼성전자 · SK하이닉스 · NVDA · 005930")
    with s2:
        pm={"3개월":"3mo","6개월":"6mo","1년":"1y","2년":"2y"}
        pl=st.selectbox("기간",list(pm.keys()),index=2)
    with s3:
        st.markdown("<div style='height:28px'></div>",unsafe_allow_html=True)
        run=st.button("분석 실행",type="primary")

    if run and stk.strip():
        tk, _hint = resolve_ticker(stk.strip())
        if _hint:
            st.caption(f"🔍 {_hint}")
        is_kr = ".KS" in tk or ".KQ" in tk
        pfx_s = "₩" if is_kr else "$"
        with st.spinner(""):
            df=get_hist(tk,pm[pl]); info=get_info(tk)
        if df.empty:
            st.error("데이터를 불러올 수 없습니다.")
        else:
            cl=df["Close"].squeeze()
            df["MA20"]=cl.rolling(20).mean()
            df["MA60"]=cl.rolling(60).mean()
            df["MA120"]=cl.rolling(120).mean()
            df["RSI"]=calc_rsi(cl)
            df["MACD"],df["SIG"],df["HIST"]=calc_macd(cl)

            lx=cl.iloc[-1]; m20=df["MA20"].iloc[-1]; m60=df["MA60"].iloc[-1]
            rsi=df["RSI"].iloc[-1]; mv=df["MACD"].iloc[-1]; ms=df["SIG"].iloc[-1]
            per=info.get("trailingPE"); pbr=info.get("priceToBook"); roe=info.get("returnOnEquity")

            sc=0; rsn=[]
            if lx>m20:  sc+=1; rsn.append("✅ 주가 > MA20")
            else:       sc-=1; rsn.append("❌ 주가 < MA20")
            if lx>m60:  sc+=1; rsn.append("✅ 주가 > MA60")
            else:       sc-=1; rsn.append("❌ 주가 < MA60")
            if m20>m60: sc+=1; rsn.append("✅ 골든크로스")
            else:       sc-=1; rsn.append("❌ 데드크로스")
            if rsi<30:  sc+=2; rsn.append(f"✅ RSI {rsi:.1f} — 과매도")
            elif rsi>70:sc-=2; rsn.append(f"❌ RSI {rsi:.1f} — 과매수")
            else:               rsn.append(f"➖ RSI {rsi:.1f} — 중립")
            if mv>ms:   sc+=1; rsn.append("✅ MACD 상승 모멘텀")
            else:       sc-=1; rsn.append("❌ MACD 하락 모멘텀")
            if per:
                if per<20: sc+=1; rsn.append(f"✅ PER {per:.1f} — 저평가")
                elif per>40:sc-=1; rsn.append(f"❌ PER {per:.1f} — 고평가")
            if roe:
                if roe>0.15: sc+=1; rsn.append(f"✅ ROE {roe*100:.1f}%")
                elif roe<0.05:sc-=1; rsn.append(f"❌ ROE {roe*100:.1f}%")

            if sc>=3:   slbl,scls="매수 (BUY)","sig-buy"
            elif sc<=-3:slbl,scls="매도 (SELL)","sig-sell"
            else:       slbl,scls="관망 (HOLD)","sig-hold"

            nm = stock_display_name(tk) if tk in STOCK_NAMES else (info.get("shortName") or tk)
            flag_s = "🇰🇷" if is_kr else "🇺🇸"
            px_fmt = f"{pfx_s}{lx:,.0f}" if is_kr else f"{pfx_s}{lx:,.2f}"
            tk_badge = f'<span style="opacity:0.38;font-weight:400;font-size:0.72em;letter-spacing:0.5px">{tk}</span>'
            st.markdown(f'<div style="font-size:1.05em;font-weight:700;margin-bottom:4px">{flag_s} {nm}</div><div style="margin-bottom:10px">{tk_badge}</div>', unsafe_allow_html=True)
            t1,t2,t3,t4,t5=st.columns(5)
            t1.metric("현재가", px_fmt)
            t2.metric("RSI",   f"{rsi:.1f}")
            t3.metric("PER",   f"{per:.1f}" if per else "N/A")
            t4.metric("PBR",   f"{pbr:.2f}" if pbr else "N/A")
            t5.metric("ROE",   f"{roe*100:.1f}%" if roe else "N/A")

            st.markdown(f"""
<div style="margin:18px 0 10px;padding:16px 20px;background:var(--secondary-background-color);border:1px solid rgba(128,128,128,0.15);border-radius:12px;display:flex;align-items:center;gap:16px">
  <span class="{scls}">{slbl}</span>
  <span style="opacity:0.45;font-size:0.8em">종합 점수 <b>{sc:+d}</b> / ±8</span>
</div>""", unsafe_allow_html=True)

            with st.expander("신호 근거", expanded=True):
                for r in rsn:
                    st.markdown(f'<div style="font-size:0.86em;padding:4px 0;border-bottom:1px solid rgba(128,128,128,0.08)">{r}</div>', unsafe_allow_html=True)

            st.markdown("<hr class='dot-divider'>", unsafe_allow_html=True)
            fig=make_subplots(rows=3,cols=1,shared_xaxes=True,
                              row_heights=[0.55,0.25,0.2],vertical_spacing=0.03,
                              subplot_titles=["주가 & 이동평균","RSI","MACD"])
            fig.add_trace(go.Candlestick(x=df.index,open=df["Open"],high=df["High"],
                low=df["Low"],close=df["Close"],name="OHLC",
                increasing_line_color="#ef4444",decreasing_line_color="#3b82f6"),row=1,col=1)
            for mc,col in {"MA20":"#f59e0b","MA60":"#3b82f6","MA120":"#8b5cf6"}.items():
                if mc in df.columns and not df[mc].isna().all():
                    fig.add_trace(go.Scatter(x=df.index,y=df[mc],name=mc,
                                             line=dict(color=col,width=1.4)),row=1,col=1)
            fig.add_trace(go.Scatter(x=df.index,y=df["RSI"],name="RSI",
                                     line=dict(color="#f97316",width=1.4)),row=2,col=1)
            fig.add_hline(y=70,line_dash="dash",line_color="#ef4444",opacity=0.4,row=2,col=1)
            fig.add_hline(y=30,line_dash="dash",line_color="#3b82f6",opacity=0.4,row=2,col=1)
            hc=["#ef4444" if v>=0 else "#3b82f6" for v in df["HIST"].fillna(0)]
            fig.add_trace(go.Bar(x=df.index,y=df["HIST"],name="Hist",marker_color=hc,opacity=0.7),row=3,col=1)
            fig.add_trace(go.Scatter(x=df.index,y=df["MACD"],name="MACD",line=dict(color="#3b82f6",width=1.2)),row=3,col=1)
            fig.add_trace(go.Scatter(x=df.index,y=df["SIG"],name="Signal",line=dict(color="#f97316",width=1.2,dash="dot")),row=3,col=1)
            fig.update_layout(height=680,xaxis_rangeslider_visible=False,
                legend=dict(orientation="h",y=1.02,x=1,xanchor="right",
                            font=dict(family="Pretendard",size=11)),
                margin=dict(t=28,b=8),
                paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(128,128,128,0.04)",
                font=dict(color="rgba(128,128,128,0.6)",family="Pretendard"))
            fig.update_xaxes(showgrid=True,gridcolor="rgba(128,128,128,0.08)",color="rgba(128,128,128,0.45)")
            fig.update_yaxes(showgrid=True,gridcolor="rgba(128,128,128,0.08)",color="rgba(128,128,128,0.45)")
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    elif run:
        st.warning("티커를 입력해주세요.")
