# -*- coding: utf-8 -*-
"""STOCK RADAR — ETF RADAR의 국내 개별주식 파일럿 전환본"""
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests, xml.etree.ElementTree as ET, re, html, json, os
from datetime import datetime

st.set_page_config(page_title="STOCK RADAR", page_icon="📈", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
:root{--bg:#07111f;--panel:#0d1928;--text:#edf3fa;--muted:#bdc9d8;--border:#30465e}
.stApp{background:#07111f;color:#edf3fa}
/* 모바일에서 Streamlit 상단 툴바와 제목이 겹치지 않도록 여백 확보 */
.block-container{padding-top:2.4rem!important;padding-bottom:2.2rem!important;max-width:820px}
[data-testid="stHeader"]{background:rgba(7,17,31,.96)}
[data-testid="stMarkdownContainer"] p{line-height:1.55}
[data-testid="stCaptionContainer"]{color:#bdc9d8!important;font-size:.94rem!important;line-height:1.55}
[data-testid="stMetric"]{background:#122137;padding:13px;border-radius:12px;border:1px solid #30465e}
[data-testid="stMetricLabel"]{color:#d2dce8!important;font-size:.95rem!important}
[data-testid="stMetricValue"]{color:#fff!important;font-size:1.35rem!important}
div[data-testid="stExpander"]{border:1px solid #30465e;border-radius:12px;background:#0b1726}
div[data-testid="stExpander"] summary{padding:.65rem .35rem;font-size:1rem;line-height:1.45;color:#edf3fa}
.stock-card{border:2px solid #4b8cff;border-radius:16px;padding:18px;margin:12px 0 16px;background:linear-gradient(145deg,rgba(59,130,246,.16),rgba(15,23,42,.28));overflow-wrap:anywhere}
.stock-muted{color:#bdc9d8;font-size:.94rem;line-height:1.55}.stock-title{font-size:1.7rem;font-weight:850;line-height:1.25;margin:.3rem 0 .45rem;color:#fff}
/* 버튼 대비와 터치 영역 통일 */
.stButton>button{min-height:3.1rem;border-radius:11px;border:1px solid #4778b5;background:#14263b;color:#f4f8ff;font-weight:750;font-size:1rem;white-space:normal}
.stButton>button:hover{border-color:#78aaff;background:#1b3552;color:#fff}
.stButton>button:focus{outline:2px solid #78aaff;outline-offset:2px}
[data-testid="stRadio"] label{font-size:1rem;color:#e5edf7}
hr{border-color:#30465e}
@media (max-width:600px){
 .block-container{padding-left:1rem!important;padding-right:1rem!important;padding-top:2.8rem!important}
 .stock-card{padding:15px;border-radius:14px}
 .stock-title{font-size:1.55rem}
 .stock-muted{font-size:.92rem}
 [data-testid="stMetric"]{padding:10px 8px}
 [data-testid="stMetricValue"]{font-size:1.15rem!important}
 div[data-testid="stExpander"] summary{font-size:1rem;padding:.75rem .25rem}
 .stButton>button{min-height:3.2rem;font-size:1rem}
}
</style>""", unsafe_allow_html=True)

THEME_RULES = {
 "AI·반도체": ["삼성전자","SK하이닉스","한미반도체","이오테크닉스","주성엔지니어링","리노공업","HPSP","원익IPS","테크윙","DB하이텍","하나마이크론","ISC","동진쎄미켐","솔브레인","피에스케이"],
 "방산·우주": ["한화에어로스페이스","현대로템","LIG넥스원","한국항공우주","한화시스템","풍산","쎄트렉아이","인텔리안테크"],
 "전력·전력기기": ["HD현대일렉트릭","효성중공업","LS ELECTRIC","LS","산일전기","제룡전기","일진전기","가온전선","대한전선"],
 "조선": ["HD한국조선해양","HD현대중공업","삼성중공업","한화오션","HJ중공업","현대미포조선"],
 "바이오·헬스케어": ["삼성바이오로직스","셀트리온","유한양행","리가켐바이오","알테오젠","에이비엘바이오","한미약품","SK바이오팜","HLB","휴젤","클래시스"],
 "2차전지": ["LG에너지솔루션","삼성SDI","포스코퓨처엠","에코프로비엠","에코프로","엘앤에프","SK이노베이션","엔켐","코스모신소재","나노신소재"],
 "자동차·로봇": ["현대차","기아","현대모비스","HL만도","두산로보틱스","레인보우로보틱스","로보티즈","에스피지","삼성전기"],
 "AI·소프트웨어": ["NAVER","카카오","더존비즈온","안랩","한글과컴퓨터","이스트소프트","엠로","솔트룩스","폴라리스오피스"],
 "화장품·K뷰티": ["아모레퍼시픽","LG생활건강","한국콜마","코스맥스","실리콘투","브이티","에이피알","클리오"],
 "엔터·콘텐츠": ["하이브","에스엠","JYP Ent.","와이지엔터테인먼트","CJ ENM","스튜디오드래곤"],
 "금융·증권": ["KB금융","신한지주","하나금융지주","우리금융지주","메리츠금융지주","삼성증권","키움증권"],
 "산업재·기타": []
}
US_LEADERS = {
 "AI·반도체": ["NVDA","AVGO","AMD","MU","AMAT"],
 "방산·우주": ["RTX","LMT","NOC","PLTR"],
 "전력·전력기기": ["GEV","ETN","VRT","PWR"],
 "조선": ["CAT","GE"],
 "바이오·헬스케어": ["LLY","REGN","ISRG","VRTX"],
 "2차전지": ["TSLA","ALB","FSLR"],
 "자동차·로봇": ["TSLA","ROK","TER"],
 "AI·소프트웨어": ["MSFT","ORCL","CRM","PANW","CRWD","NOW"],
 "화장품·K뷰티": ["EL","ULTA"],
 "엔터·콘텐츠": ["NFLX","DIS","SPOT"],
 "금융·증권": ["JPM","GS","MS"]
}

# 네이버 금융 접근이 차단되거나 응답 형식이 바뀌어도 앱이 빈 화면으로 끝나지 않도록
# 1) 네이버 API 2) 네이버 시가총액 HTML 3) 테마별 국내 대표 종목 목록 순으로 대체합니다.
FALLBACK_STOCKS = {
    "005930":"삼성전자", "000660":"SK하이닉스", "042700":"한미반도체", "039030":"이오테크닉스",
    "036930":"주성엔지니어링", "058470":"리노공업", "403870":"HPSP", "240810":"원익IPS",
    "089030":"테크윙", "000990":"DB하이텍",
    "012450":"한화에어로스페이스", "064350":"현대로템", "079550":"LIG넥스원", "047810":"한국항공우주",
    "272210":"한화시스템", "267260":"HD현대일렉트릭", "298040":"효성중공업",
    "010120":"LS ELECTRIC", "010060":"OCI홀딩스", "062040":"산일전기", "033100":"제룡전기",
    "267250":"HD현대", "009540":"HD한국조선해양", "329180":"HD현대중공업",
    "010140":"삼성중공업", "042660":"한화오션", "207940":"삼성바이오로직스", "068270":"셀트리온",
    "000100":"유한양행", "141080":"리가켐바이오", "196170":"알테오젠", "298380":"에이비엘바이오",
    "068760":"셀트리온제약", "326030":"SK바이오팜", "028300":"HLB", "145020":"휴젤",
    "373220":"LG에너지솔루션", "006400":"삼성SDI", "003670":"포스코퓨처엠", "247540":"에코프로비엠",
    "086520":"에코프로", "066970":"엘앤에프", "096770":"SK이노베이션", "348370":"엔켐",
    "005380":"현대차", "000270":"기아", "012330":"현대모비스", "454910":"두산로보틱스",
    "277810":"레인보우로보틱스", "035420":"NAVER", "035720":"카카오",
    "053800":"안랩", "012510":"더존비즈온", "051900":"LG생활건강", "090430":"아모레퍼시픽",
    "161890":"한국콜마", "192820":"코스맥스", "257720":"실리콘투",
    "352820":"하이브", "041510":"에스엠", "035900":"JYP Ent.", "122870":"와이지엔터테인먼트",
    "105560":"KB금융", "055550":"신한지주", "086790":"하나금융지주", "316140":"우리금융지주",
    "138040":"메리츠금융지주"
}
# 잘못된/비숫자 키를 안전하게 제거해 대체 목록을 정리합니다.
FALLBACK_STOCKS = {str(k): v for k, v in FALLBACK_STOCKS.items() if str(k).isdigit() and len(str(k)) == 6 and v}

def _clean_stock_name(name):
    name = re.sub(r"\s+", " ", str(name or "")).strip()
    if not name or any(x in name.upper() for x in ("ETF", "ETN", "SPAC", "스팩", "리츠")):
        return ""
    if name.endswith(("우", "우B", "우C")):
        return ""
    return name

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_stock_master(limit=180):
    """코스피·코스닥 종목 목록을 여러 경로로 수집하고 실패 시 대표 종목 목록으로 대체합니다."""
    out = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
        "Referer": "https://finance.naver.com/sise/sise_market_sum.naver",
    }
    # 1) 네이버 금융 JSON API
    for market in ("KOSPI", "KOSDAQ"):
        for page in range(1, 5):
            try:
                url = f"https://finance.naver.com/api/sise/marketSum.nhn?market={market}&fieldIds=&industryCodes=&page={page}"
                r = requests.get(url, headers=headers, timeout=8)
                r.raise_for_status()
                payload = r.json()
                rows = payload.get("result", {}).get("list", []) if isinstance(payload, dict) else []
                for row in rows:
                    code = str(row.get("itemCode", "")).zfill(6)
                    name = _clean_stock_name(row.get("itemName", ""))
                    if code.isdigit() and len(code) == 6 and name:
                        out[code] = name
                if not rows:
                    break
            except Exception:
                break
        if len(out) >= min(limit, 50):
            break

    # 2) API 응답이 비었거나 불완전하면 시가총액 HTML 표에서 종목코드를 추출
    if len(out) < min(limit, 30):
        for sosok in (0, 1):  # 0=코스피, 1=코스닥
            for page in range(1, 5):
                try:
                    url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok={sosok}&page={page}"
                    r = requests.get(url, headers=headers, timeout=8)
                    r.raise_for_status()
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(r.text, "html.parser")
                    found = 0
                    for a in soup.select('a[href*="/item/main.naver?code="]'):
                        m = re.search(r"code=(\d{6})", a.get("href", ""))
                        name = _clean_stock_name(a.get_text(" ", strip=True))
                        if m and name:
                            out[m.group(1)] = name
                            found += 1
                    if found == 0:
                        break
                except Exception:
                    break

    # 3) 네트워크/사이트 차단 시에도 파일럿이 동작하도록 테마별 대표주로 대체
    if len(out) < 15:
        out.update(FALLBACK_STOCKS)
    # 시가총액 순 API/HTML 결과를 먼저 유지하고, 부족분만 대체 목록으로 보충
    return dict(list(out.items())[:max(15, int(limit))])

@st.cache_data(ttl=900, show_spinner=False)
def fetch_history(code, period="3y"):
    code=str(code).zfill(6)
    for suffix in (".KS",".KQ"):
        try:
            df=yf.download(code+suffix,period=period,interval="1d",auto_adjust=True,progress=False,threads=False,timeout=10)
            if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
            if not df.empty and "Close" in df: return df.dropna(subset=["Close"]).sort_index()
        except Exception: pass
    try:
        url=f"https://fchart.stock.naver.com/sise.nhn?symbol={code}&timeframe=day&count=800&requestType=0"
        r=requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=10); root=ET.fromstring(r.text); rows=[]
        for node in root.findall(".//item"):
            p=node.attrib.get("data","").split("|")
            if len(p)>=6: rows.append(p[:6])
        if rows:
            d=pd.DataFrame(rows,columns=["Date","Open","High","Low","Close","Volume"]); d["Date"]=pd.to_datetime(d.Date,errors="coerce")
            for c in ["Open","High","Low","Close","Volume"]: d[c]=pd.to_numeric(d[c],errors="coerce")
            return d.dropna(subset=["Date","Close"]).set_index("Date").sort_index()
    except Exception: pass
    return pd.DataFrame()

@st.cache_data(ttl=900, show_spinner=False)
def us_theme_scores():
    result={}
    all_tickers=sorted(set(t for group in US_LEADERS.values() for t in group))
    for ticker in all_tickers:
        try:
            d=yf.download(ticker,period="6mo",interval="1d",auto_adjust=True,progress=False,threads=False,timeout=8)
            if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
            c=pd.to_numeric(d.get("Close",pd.Series(dtype=float)),errors="coerce").dropna()
            if len(c)<65: continue
            r20=(c.iloc[-1]/c.iloc[-21]-1)*100; r60=(c.iloc[-1]/c.iloc[-61]-1)*100
            score=float(np.clip(50+1.3*r20+0.45*r60,0,100))
            result[ticker]=score
        except Exception: continue
    theme={}
    for t, tickers in US_LEADERS.items():
        vals=[result[x] for x in tickers if x in result]
        if vals: theme[t]=float(np.mean(vals))
    return theme, result

def classify_theme(name):
    for theme, names in THEME_RULES.items():
        if any(n.lower() in name.lower() for n in names): return theme
    return "산업·기타"

def calc_stock_score(code,name,us_scores,benchmark):
    d=fetch_history(code)
    if d.empty or len(d)<65: return None
    close=pd.to_numeric(d.Close,errors="coerce").dropna()
    if len(close)<65 or close.iloc[-1]<=0: return None
    ret20=(close.iloc[-1]/close.iloc[-21]-1)*100; ret60=(close.iloc[-1]/close.iloc[-61]-1)*100
    ma20=close.rolling(20).mean().iloc[-1]; ma60=close.rolling(60).mean().iloc[-1]
    theme=classify_theme(name); us=us_scores.get(theme,np.nan)
    b20=b60=0.0
    if not benchmark.empty and len(benchmark)>=61:
        bc=pd.to_numeric(benchmark.Close,errors="coerce").dropna()
        if len(bc)>=61:
            b20=(bc.iloc[-1]/bc.iloc[-21]-1)*100; b60=(bc.iloc[-1]/bc.iloc[-61]-1)*100
    rs20=ret20-b20; rs60=ret60-b60
    trend=50 + (15 if close.iloc[-1]>ma20 else -8) + (12 if ma20>ma60 else -5)
    momentum=np.clip(50+1.2*ret20+0.35*ret60,0,100)
    relative=np.clip(50+1.4*rs20+0.5*rs60,0,100)
    us_component=us if np.isfinite(us) else 50
    target=float(np.clip(.38*momentum+.25*relative+.22*trend+.15*us_component,0,100))
    risk=0
    if close.iloc[-1]<ma20: risk+=8
    if ret20>25: risk+=10
    entry=float(np.clip(target-risk,0,100))
    if entry>=75 and close.iloc[-1]>ma20 and rs20>0: action="관심 매수 후보"
    elif entry>=62: action="관심 유지·눌림 대기"
    else: action="관망·추세 확인"
    return {"code":code,"name":name,"theme":theme,"price":float(close.iloc[-1]),"ret20":float(ret20),"ret60":float(ret60),"rs20":float(rs20),"rs60":float(rs60),"ma20":float(ma20),"ma60":float(ma60),"us":float(us) if np.isfinite(us) else np.nan,"target":target,"entry":entry,"risk":risk,"action":action}

# header
st.markdown('<div style="font-size:1.85rem;font-weight:900;line-height:1.25;margin:.25rem 0 .55rem;color:#ffffff">📈 STOCK RADAR</div><div class="stock-muted">미국장 선행신호 → 국내 개별주식 후보 → 진입 판단</div>',unsafe_allow_html=True)
st.caption("1차 파일럿 · 국내 코스피·코스닥 개별주식 · 데이터 기반 후보 선별")
page=st.radio("메뉴",["🏆 종목 추천","📊 내 종목"],horizontal=True,label_visibility="collapsed")

WATCHLIST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stock_radar_watchlist.json")
def load_watchlist():
    try:
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            data=json.load(f)
        return list(dict.fromkeys(str(x).zfill(6) for x in data if str(x).isdigit() and len(str(x))<=6))
    except Exception:
        return []
def save_watchlist():
    try:
        with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.watchlist, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
if "watchlist" not in st.session_state: st.session_state.watchlist=load_watchlist()
if "held_stocks" not in st.session_state: st.session_state.held_stocks={}
if page=="🏆 종목 추천":
    st.subheader("오늘의 개별주식 후보")
    st.caption("시가총액 상위 종목부터 평가합니다. 가격 이력이 부족한 종목은 제외하고, 적격 후보를 최대 15개까지 표시합니다.")
    if st.button("🔄 데이터 새로고침",use_container_width=True):
        fetch_stock_master.clear(); fetch_history.clear(); us_theme_scores.clear(); st.rerun()
    with st.spinner("국내 종목·미국장 신호·가격 추세를 평가하는 중입니다…"):
        master=fetch_stock_master(260); us_scores, us_ticker_scores=us_theme_scores()
        bench=fetch_history("069500")
        results=[]
        # 시장 규모 상위 후보를 순차 평가해 호출량을 억제합니다.
        for i,(code,name) in enumerate(master.items()):
            if i>=200: break
            try:
                item=calc_stock_score(code,name,us_scores,bench)
                if item: results.append(item)
            except Exception: continue
        results.sort(key=lambda x:(x["target"],x["entry"]),reverse=True)
        # 같은 테마 쏠림을 줄이되 후보가 모자라면 같은 테마를 허용
        shortlist=[]; counts={}
        for x in results:
            if counts.get(x["theme"],0)>=2: continue
            shortlist.append(x); counts[x["theme"]]=counts.get(x["theme"],0)+1
            if len(shortlist)>=15: break
        if len(shortlist)<15:
            used={x["code"] for x in shortlist}
            for x in results:
                if x["code"] not in used:
                    shortlist.append(x)
                    if len(shortlist)>=15: break
    if not shortlist:
        st.error("추천 후보를 가져오지 못했습니다. 네이버 금융 또는 Yahoo Finance 데이터 연결을 확인해 주세요.")
    else:
        first=shortlist[0]
        st.markdown(f'''<div class="stock-card"><div class="stock-muted">⭐ 통합 종목 후보 · 1순위</div><div class="stock-title">{html.escape(first['name'])}</div><div class="stock-muted">{first['code']} · {first['theme']} · {first['price']:,.0f}원</div><hr><div style="display:flex;gap:12px;flex-wrap:wrap"><div style="flex:1;min-width:100px"><div class="stock-muted">장기 타겟</div><div style="font-size:1.8rem;font-weight:800">{first['target']:.1f}<small>/100</small></div></div><div style="flex:1;min-width:100px"><div class="stock-muted">현재 진입</div><div style="font-size:1.8rem;font-weight:800">{first['entry']:.1f}<small>/100</small></div></div><div style="flex:1;min-width:100px"><div class="stock-muted">미국 테마 신호</div><div style="font-size:1.5rem;font-weight:750">{first['us']:.1f}/100</div></div></div><b>판단: {first['action']}</b><div class="stock-muted">20일 {first['ret20']:+.1f}% · 60일 {first['ret60']:+.1f}% · 시장 대비 20일 {first['rs20']:+.1f}%p</div></div>''',unsafe_allow_html=True)
        if first["code"] not in st.session_state.watchlist:
            if st.button("⭐ 관심 종목 등록",use_container_width=True): st.session_state.watchlist.append(first["code"]); save_watchlist(); st.success("관심 종목에 등록했습니다.")
        st.subheader(f"다른 추천 후보 (최대 14개 · 현재 {max(0,len(shortlist)-1)}개)")
        for rank,x in enumerate(shortlist[1:],2):
            with st.expander(f"#{rank} {x['name']} · 타겟 {x['target']:.1f} / 진입 {x['entry']:.1f}"):
                c1,c2,c3=st.columns(3); c1.metric("테마",x["theme"]); c2.metric("미국장 신호",f"{x['us']:.1f}" if np.isfinite(x['us']) else "자료 부족"); c3.metric("현재가",f"{x['price']:,.0f}원")
                st.write(f"**판단:** {x['action']} · **20일 수익률:** {x['ret20']:+.1f}% · **60일 수익률:** {x['ret60']:+.1f}%")
                st.write(f"**시장 대비 강도:** 20일 {x['rs20']:+.1f}%p · 60일 {x['rs60']:+.1f}%p · **위험 감점:** {x['risk']}점")
                if x['code'] not in st.session_state.watchlist:
                    if st.button("관심 종목 등록",key=f"watch_{x['code']}"): st.session_state.watchlist.append(x['code']); save_watchlist(); st.success("등록했습니다.")
        with st.expander("미국장 선행신호 상세"):
            st.write("테마별 미국 상장 비교종목의 20일·60일 가격 흐름을 단순 점수화한 참고 신호입니다.")
            st.dataframe(pd.DataFrame([{"테마":k,"미국장 점수":round(v,1)} for k,v in us_scores.items()]).sort_values("미국장 점수",ascending=False),use_container_width=True,hide_index=True)
        st.caption("점수는 우선순위 지표이며 수익을 보장하지 않습니다. 실제 매수 전 공시·실적·거래대금·변동성을 확인하세요.")
else:
    st.subheader("📊 내 종목")
    st.caption("관심·보유 종목을 선택해 현재가, 추세, 진입 판단을 확인합니다.")
    master=fetch_stock_master(300)
    with st.expander("＋ 관심 종목 추가", expanded=not bool(st.session_state.watchlist)):
        search=st.text_input("종목명 또는 6자리 코드", placeholder="예: 삼성전자 또는 005930", key="my_stock_search")
        if search.strip():
            q=search.strip().lower()
            matches=[(c,n) for c,n in master.items() if q in n.lower() or q==c]
            if matches:
                options=[c for c,n in matches[:30]]
                chosen=st.selectbox("검색 결과", options, format_func=lambda c:f"{master.get(c,c)} · {c}", key="my_stock_match")
                if st.button("관심 종목에 추가", use_container_width=True, key="add_my_stock"):
                    if chosen not in st.session_state.watchlist:
                        st.session_state.watchlist.append(chosen); save_watchlist()
                    st.rerun()
            else:
                st.caption("검색 목록에 없으면 종목코드로 직접 추가할 수 있습니다.")
        manual=st.text_input("종목코드 직접 입력", placeholder="예: 005930", key="manual_stock_code")
        if st.button("코드로 추가", use_container_width=True, key="manual_add_stock"):
            c=re.sub(r"\D", "", manual)
            if len(c)==6:
                if c not in st.session_state.watchlist: st.session_state.watchlist.append(c); save_watchlist()
                st.rerun()
            else: st.warning("국내 주식 6자리 종목코드를 입력하세요.")

    if not st.session_state.watchlist:
        st.info("관심 종목이 없습니다. 위의 ‘관심 종목 추가’에서 종목을 등록하세요.")
    else:
        labels={c:master.get(c,c) for c in st.session_state.watchlist}
        selected=st.selectbox("내 종목 선택", st.session_state.watchlist,
                              format_func=lambda c:f"{labels.get(c,c)} · {c}", key="selected_my_stock")
        name=labels.get(selected, selected)
        with st.spinner(f"{name} 가격과 추세를 분석하는 중입니다…"):
            us_scores,_=us_theme_scores(); bench=fetch_history("069500"); item=calc_stock_score(selected,name,us_scores,bench); hist=fetch_history(selected)
        if hist.empty or item is None:
            st.error(f"{name}({selected})의 가격 이력이 부족해 분석할 수 없습니다. 데이터 제공처에서 해당 종목을 지원하는지 확인해 주세요.")
        else:
            prev=float(pd.to_numeric(hist["Close"],errors="coerce").dropna().iloc[-2]) if len(hist)>=2 else item["price"]
            change=item["price"]-prev; change_pct=(change/prev*100) if prev else 0
            date_text=pd.to_datetime(hist.index[-1]).strftime("%Y-%m-%d")
            us_text=f"{item['us']:.1f}" if np.isfinite(item["us"]) else "자료 부족"
            color="#48d597" if change>=0 else "#ff7777"
            card=(f'<div class="stock-card"><div class="stock-muted">내 종목 · {html.escape(selected)} · 기준일 {date_text}</div>'
                  f'<div class="stock-title">{html.escape(name)}</div><div style="font-size:1.8rem;font-weight:850;color:#fff">'
                  f'{item["price"]:,.0f}원 <span style="font-size:1rem;color:{color}">{change:+,.0f}원 ({change_pct:+.2f}%)</span></div><hr>'
                  f'<div style="display:flex;gap:10px;flex-wrap:wrap">'
                  f'<div style="flex:1;min-width:90px;background:#122137;border-radius:10px;padding:12px"><div class="stock-muted">장기 타겟</div><div style="font-size:1.5rem;font-weight:800">{item["target"]:.1f}<small>/100</small></div></div>'
                  f'<div style="flex:1;min-width:90px;background:#122137;border-radius:10px;padding:12px"><div class="stock-muted">현재 진입</div><div style="font-size:1.5rem;font-weight:800">{item["entry"]:.1f}<small>/100</small></div></div>'
                  f'<div style="flex:1;min-width:90px;background:#122137;border-radius:10px;padding:12px"><div class="stock-muted">미국 테마</div><div style="font-size:1.35rem;font-weight:800">{us_text}<small>/100</small></div></div></div>'
                  f'<p style="font-size:1.05rem;font-weight:800;margin:.9rem 0 .35rem">판단: {html.escape(item["action"])}</p>'
                  f'<div class="stock-muted">{html.escape(item["theme"])} · 20일 {item["ret20"]:+.1f}% · 60일 {item["ret60"]:+.1f}% · 시장 대비 20일 {item["rs20"]:+.1f}%p</div></div>')
            st.markdown(card, unsafe_allow_html=True)
            held=st.radio("보유 상태", ["관심 종목", "보유 중"], index=1 if selected in st.session_state.held_stocks else 0, horizontal=True, key=f"held_{selected}")
            if held=="보유 중": st.session_state.held_stocks[selected]=True
            else: st.session_state.held_stocks.pop(selected,None)
            st.markdown("### 📌 행동 가이드")
            if item["action"]=="관심 매수 후보":
                st.success("추세와 상대강도가 양호한 후보입니다. 한 번에 진입하기보다 가격·거래대금과 변동성을 확인하세요.")
            elif item["action"]=="관심 유지·눌림 대기":
                st.warning("관심은 유지하되 추격매수는 피하고, 눌림 이후 추세 회복 여부를 확인하세요.")
            else:
                st.info("현재 점수만으로 진입을 서두르지 말고 추세 회복과 상대강도 개선을 기다리세요.")
            st.markdown("### 📈 최근 6개월 가격 흐름")
            chart=hist.copy()
            if isinstance(chart.columns,pd.MultiIndex): chart.columns=chart.columns.get_level_values(0)
            if "Close" in chart.columns:
                chart["종가"] = pd.to_numeric(chart["Close"], errors="coerce")
                chart["20일선"] = chart["종가"].rolling(20).mean()
                chart["60일선"] = chart["종가"].rolling(60).mean()
                st.line_chart(chart[["종가","20일선","60일선"]].tail(130), use_container_width=True)
            with st.expander("상세 분석 근거"):
                a,b=st.columns(2)
                a.metric("20일 수익률",f"{item['ret20']:+.1f}%")
                b.metric("60일 수익률",f"{item['ret60']:+.1f}%")
                a.metric("시장 대비 20일 강도",f"{item['rs20']:+.1f}%p")
                b.metric("위험 감점",f"{item['risk']}점")
                st.write(f"테마 분류: {item['theme']}")
                st.write(f"미국 선행신호: {item['us']:.1f}/100" if np.isfinite(item['us']) else "미국 선행신호: 자료 부족")
        st.divider()
        st.markdown("### 관심 종목 목록")
        for c in st.session_state.watchlist:
            c1,c2=st.columns([4,1])
            with c1:
                flag=" · 보유 중" if c in st.session_state.held_stocks else ""
                st.write(f"**{master.get(c,c)}** · {c}{flag}")
            with c2:
                if st.button("삭제", key=f"remove_{c}", use_container_width=True):
                    st.session_state.watchlist=[x for x in st.session_state.watchlist if x!=c]
                    st.session_state.held_stocks.pop(c,None); save_watchlist(); st.rerun()
        if st.button("관심 목록 전체 초기화", key="clear_watchlist", use_container_width=True):
            st.session_state.watchlist=[]; st.session_state.held_stocks={}; save_watchlist(); st.rerun()
