# -*- coding: utf-8 -*-

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import json
import os
import html
import ast
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, date
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None


# ============================================================
# STOCK RADAR
# Stable Mobile Financial Dashboard
# ============================================================

st.set_page_config(
    page_title="STOCK RADAR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# HTML ESCAPE
# ============================================================

def esc(value):
    """동적 문자열의 HTML 깨짐 방지"""
    return html.escape(str(value))


# ============================================================
# CSS
# ============================================================

CSS = r"""
<style>

/* ==========================================================
   GLOBAL
   ========================================================== */

:root {
    --bg: #07111f;
    --bg2: #091522;
    --panel: #0d1928;
    --panel2: #111f31;
    --panel3: #16263a;

    --text: #e3eaf2;
    --text2: #c3cfdb;
    --muted: #8193a7;

    --blue: #62aef2;
    --green: #39c99a;
    --red: #ef6678;
    --yellow: #d5ae58;

    --border: #22384d;
    --border2: #29445d;
}


/* ==========================================================
   STREAMLIT BACKGROUND
   ========================================================== */

html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background: #07111f !important;
    color: #e3eaf2 !important;
}

[data-testid="stHeader"] {
    background: #07111f !important;
}

[data-testid="stToolbar"] {
    background: #07111f !important;
}

[data-testid="stSidebar"] {
    background: #091522 !important;
}

[data-testid="stSidebar"] * {
    color: #d7e1eb !important;
}


/* ==========================================================
   MAIN
   ========================================================== */

.block-container {
    max-width: 1180px !important;
    padding: 10px 12px 32px !important;
}


/* ==========================================================
   TEXT
   ========================================================== */

.stApp p {
    color: #c7d2de;
}

.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp h5,
.stApp h6 {
    color: #e3eaf2 !important;
}


/* ==========================================================
   INPUT
   ========================================================== */

div[data-baseweb="input"],
div[data-baseweb="input"] > div {
    background: #0c1928 !important;
    border-color: #294159 !important;
    color: #dce5ee !important;
}

div[data-baseweb="input"] input {
    background: transparent !important;
    color: #e3eaf2 !important;
    -webkit-text-fill-color: #e3eaf2 !important;
    caret-color: #62aef2 !important;
}

div[data-baseweb="input"] input::placeholder {
    color: #71859a !important;
    opacity: 1 !important;
}


/* ==========================================================
   SELECTBOX
   ========================================================== */

div[data-baseweb="select"],
div[data-baseweb="select"] > div {
    background: #0c1928 !important;
    color: #e3eaf2 !important;
    border-color: #294159 !important;
}

div[data-baseweb="select"] span {
    color: #dce5ee !important;
}

div[data-baseweb="popover"] {
    background: #0b1725 !important;
    border: 1px solid #294159 !important;
}

div[data-baseweb="menu"],
ul[role="listbox"] {
    background: #0b1725 !important;
}

li[role="option"] {
    background: #0b1725 !important;
    color: #dce5ee !important;
}

li[role="option"]:hover {
    background: #16283b !important;
    color: #ffffff !important;
}


/* ==========================================================
   RADIO
   ========================================================== */

div[data-testid="stRadio"] label,
div[data-testid="stRadio"] p {
    color: #c8d4df !important;
}


/* ==========================================================
   BUTTON
   ========================================================== */

.stButton > button {
    background: #122236 !important;
    color: #dce5ee !important;
    border: 1px solid #29445d !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    min-height: 36px !important;
    box-shadow: none !important;
}

.stButton > button:hover {
    background: #18314a !important;
    border-color: #4a7fa8 !important;
    color: #ffffff !important;
}

.stButton > button:disabled {
    background: #0d1928 !important;
    color: #5f7082 !important;
    border-color: #1d3043 !important;
}


/* ==========================================================
   ALERT
   ========================================================== */

[data-testid="stAlert"] {
    background: #0d1928 !important;
    border: 1px solid #263d53 !important;
    color: #cbd6e1 !important;
}

[data-testid="stAlert"] p {
    color: #cbd6e1 !important;
}


/* ==========================================================
   CAPTION
   ========================================================== */

[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
    color: #72869b !important;
}


/* ==========================================================
   APP HEADER
   ========================================================== */

.app-header {
    padding: 3px 0 10px;
}

.app-title {
    font-size: 1.45rem;
    line-height: 1.1;
    font-weight: 850;
    color: #e5edf5 !important;
}

.app-subtitle {
    font-size: 0.74rem;
    color: #74889d !important;
    margin-top: 3px;
}


/* ==========================================================
   HERO
   ========================================================== */

.hero {
    background: #0d1928;
    border: 1px solid #263e54;
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 10px;
}

.hero-name {
    font-size: 1.16rem;
    line-height: 1.35;
    font-weight: 800;
    color: #e0e8f0 !important;
}

.hero-code {
    font-size: 0.70rem;
    color: #73879b !important;
    margin-top: 2px;
}

.quote-row {
    display: flex;
    gap: 12px;
    align-items: baseline;
    margin-top: 9px;
}

.quote-price {
    font-size: 1.72rem;
    line-height: 1;
    font-weight: 850;
    color: #e6edf4 !important;
}

.quote-change {
    font-size: 0.84rem;
    font-weight: 750;
}

.hero-date {
    font-size: 0.68rem;
    color: #71859a !important;
    margin-top: 7px;
}


/* ==========================================================
   COLORS
   ========================================================== */

.positive {
    color: #39c99a !important;
}

.negative {
    color: #ef6678 !important;
}

.neutral {
    color: #a8b7c6 !important;
}


/* ==========================================================
   SECTION
   ========================================================== */

.section-title {
    font-size: 0.90rem;
    font-weight: 800;
    color: #cdd8e3 !important;
    margin: 15px 0 7px;
}


/* ==========================================================
   EVIDENCE
   ========================================================== */

.evidence-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
    margin: 6px 0 9px;
}

.evidence-box {
    background: #0b1725;
    border: 1px solid #20374c;
    border-radius: 8px;
    padding: 8px;
}

.evidence-label {
    font-size: 0.64rem;
    color: #74879b !important;
}

.evidence-value {
    font-size: 0.86rem;
    font-weight: 800;
    color: #cdd8e3 !important;
    margin-top: 2px;
}

.evidence-sub {
    font-size: 0.62rem;
    color: #71859a !important;
    margin-top: 2px;
}


/* ==========================================================
   JUDGMENT / ACTION
   ========================================================== */

.judgment-box,
.action-box {
    background: #0d1928;
    border: 1px solid #22394e;
    border-radius: 9px;
    padding: 11px;
    min-height: 112px;
}

.judgment-box {
    border-left: 3px solid #4b8bbd;
}

.action-box {
    border-left: 3px solid #90763c;
}

.judgment-title,
.action-title {
    font-size: 0.66rem;
    color: #75899d !important;
    font-weight: 750;
}

.action-title {
    color: #b59a5a !important;
}

.judgment-main {
    font-size: 0.96rem;
    line-height: 1.3;
    font-weight: 800;
    color: #d6e0e9 !important;
    margin-top: 4px;
}

.judgment-reason,
.action-main {
    font-size: 0.74rem;
    line-height: 1.48;
    color: #aab9c8 !important;
    margin-top: 7px;
}

.reason-label {
    color: #6f8499 !important;
    font-size: 0.64rem;
    font-weight: 750;
    margin-bottom: 3px;
}

.action-reason-label {
    color: #a48b50 !important;
    font-size: 0.64rem;
    font-weight: 750;
    margin-bottom: 3px;
}


/* ==========================================================
   SCENARIO
   ========================================================== */

.scenario-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
}

.scenario-card {
    background: #0b1725;
    border: 1px solid #20374c;
    border-radius: 8px;
    padding: 9px;
}

.scenario-label {
    font-size: 0.63rem;
    color: #74879a !important;
}

.scenario-price {
    font-size: 0.92rem;
    font-weight: 800;
    color: #d1dce6 !important;
    margin-top: 3px;
}

.scenario-desc {
    font-size: 0.63rem;
    line-height: 1.38;
    color: #899bab !important;
    margin-top: 4px;
}


/* ==========================================================
   HOLDING
   ========================================================== */

.holding-box {
    background: #0b1725;
    border: 1px solid #20374c;
    border-radius: 8px;
    padding: 9px;
}

.holding-value {
    font-size: 0.84rem;
    font-weight: 800;
    color: #ccd7e1 !important;
}

.holding-detail {
    font-size: 0.69rem;
    color: #8294a7 !important;
    margin-top: 3px;
}


/* ==========================================================
   FUTURE THEME
   ========================================================== */

.theme-card {
    background: #0d1928;
    border: 1px solid #22394e;
    border-radius: 10px;
    padding: 11px;
    margin-bottom: 7px;
}

.theme-stage {
    font-size: 0.65rem;
    color: #7199b8 !important;
    font-weight: 750;
}

.theme-title {
    font-size: 0.98rem;
    font-weight: 800;
    color: #d2dde7 !important;
    margin-top: 2px;
}

.theme-reason {
    font-size: 0.71rem;
    color: #899bab !important;
    line-height: 1.42;
    margin: 4px 0 8px;
}

.theme-etf-box {
    background: #0b1725;
    border: 1px solid #1f3549;
    border-radius: 8px;
    padding: 9px;
    min-height: 145px;
}

.theme-stock-name {
    font-size: 0.76rem;
    line-height: 1.3;
    font-weight: 800;
    color: #d0dbe5 !important;
}

.theme-stock-code {
    font-size: 0.62rem;
    color: #708398 !important;
    margin-top: 2px;
}

.theme-data-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 4px;
    margin-top: 7px;
}

.theme-data-item {
    background: #091522;
    border-radius: 5px;
    padding: 5px;
}

.theme-data-label {
    font-size: 0.57rem;
    color: #6f8296 !important;
}

.theme-data-value {
    font-size: 0.70rem;
    font-weight: 800;
    color: #bdcad6 !important;
    margin-top: 1px;
}


/* ==========================================================
   FUTURE ANALYSIS
   ========================================================== */

.future-analysis {
    background: #0d1928;
    border: 1px solid #31516c;
    border-radius: 11px;
    padding: 12px;
    margin: 12px 0 10px;
}

.future-analysis-title {
    font-size: 0.68rem;
    color: #6ea7d1 !important;
    font-weight: 800;
}

.future-analysis-name {
    font-size: 1.02rem;
    font-weight: 800;
    color: #e0e8ef !important;
    margin-top: 2px;
}

.future-analysis-code {
    font-size: 0.64rem;
    color: #72879b !important;
}


/* ==========================================================
   FUTURE THEME PRIORITY / OUTLOOK
   ========================================================== */

.theme-stage-wrap {
    display:flex;
    align-items:center;
    gap:6px;
    margin-bottom:5px;
}

.theme-stage-badge {
    display:inline-block;
    padding:3px 7px;
    border-radius:999px;
    font-size:.60rem;
    font-weight:800;
    border:1px solid transparent;
}

.stage-core { background:#173b32; color:#55d7ad !important; border-color:#2d8068; }
.stage-next { background:#17324a; color:#6db8f2 !important; border-color:#35688f; }
.stage-interest { background:#3b3219; color:#e0bd63 !important; border-color:#80692e; }
.stage-early { background:#32223b; color:#c59ae8 !important; border-color:#694b7c; }

.theme-outlook {
    margin-top:7px;
    padding:7px 8px;
    border-radius:7px;
    background:#0a1522;
    border-left:3px solid #3d6584;
    color:#b9c7d4 !important;
    font-size:.67rem;
    line-height:1.45;
}

.theme-outlook strong { color:#e0e8ef !important; }

.theme-summary-card {
    background:#0b1725;
    border:1px solid #20374c;
    border-radius:9px;
    padding:9px;
    margin-bottom:7px;
}

.theme-summary-title {
    font-size:.72rem;
    font-weight:800;
    color:#e0e8ef !important;
}

.theme-summary-meta {
    font-size:.64rem;
    color:#8295a8 !important;
    margin-top:3px;
}

.theme-summary-outlook {
    font-size:.68rem;
    color:#bdcad6 !important;
    margin-top:6px;
    line-height:1.45;
}

/* ==========================================================
   SUMMARY TABLE
   ========================================================== */

.summary-table-wrap {
    width: 100%;
    overflow-x: auto;
    background: #0b1725;
    border: 1px solid #20374c;
    border-radius: 9px;
}

.summary-table {
    width: 100%;
    border-collapse: collapse;
    min-width: 500px;
}

.summary-table th {
    background: #101f31;
    color: #7f94a9;
    font-size: 0.64rem;
    font-weight: 750;
    text-align: left;
    padding: 8px 7px;
    border-bottom: 1px solid #233a50;
}

.summary-table td {
    background: #0b1725;
    color: #c4d0db;
    font-size: 0.68rem;
    padding: 8px 7px;
    border-bottom: 1px solid #172c40;
}

.summary-table tr:last-child td {
    border-bottom: none;
}


/* ==========================================================
   STREAMLIT CONTAINERS
   ========================================================== */

[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="column"] {
    background: transparent !important;
}


/* ==========================================================
   EXPANDER
   ========================================================== */

[data-testid="stExpander"] {
    background: #0d1928 !important;
    border: 1px solid #22384d !important;
}

[data-testid="stExpander"] summary {
    color: #cbd7e2 !important;
}


/* ==========================================================
   TABS
   ========================================================== */

button[data-baseweb="tab"] {
    color: #8da0b3 !important;
    background: transparent !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #dce6ef !important;
}


/* ==========================================================
   MOBILE
   ========================================================== */

@media (max-width: 700px) {

    .block-container {
        padding: 7px 8px 24px !important;
    }

    .app-title {
        font-size: 1.30rem;
    }

    .hero {
        padding: 12px;
    }

    .hero-name {
        font-size: 1.05rem;
    }

    .quote-price {
        font-size: 1.58rem;
    }

    .quote-change {
        font-size: 0.78rem;
    }

    .evidence-grid {
        gap: 5px;
    }

    .evidence-box {
        padding: 7px;
    }

    .evidence-value {
        font-size: 0.80rem;
    }

    .scenario-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .judgment-box,
    .action-box {
        min-height: auto;
    }

    .theme-data-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}




/* ==========================================================
   FINAL TARGET
   ========================================================== */
.final-target-hero { background: linear-gradient(135deg, #10263a, #0b1725); border:1px solid #39627f; border-radius:13px; padding:13px; margin:8px 0 12px; }
.final-target-title { font-size:1.12rem; font-weight:900; color:#e5edf4 !important; }
.final-target-sub { font-size:.70rem; color:#8ea6ba !important; margin-top:4px; line-height:1.45; }
.final-target-rank { font-size:.66rem; font-weight:850; color:#70b8e8 !important; }
.final-horizon-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:6px; margin-top:8px; }
.final-horizon-box { background:#091522; border:1px solid #20374c; border-radius:8px; padding:7px; }
.final-horizon-label { font-size:.58rem; color:#70859a !important; }
.final-horizon-value { font-size:.72rem; font-weight:850; color:#d4e0ea !important; margin-top:2px; }
@media (max-width: 640px) { .final-horizon-grid { grid-template-columns:1fr; } }

/* ==========================================================
   MARKET RADAR
   ========================================================== */
.radar-card { background:#0d1928; border:1px solid #263e54; border-radius:10px; padding:11px; margin-bottom:7px; }
.radar-title { font-size:.92rem; font-weight:850; color:#dce6ef !important; }
.final-target-name { font-size:1.02rem !important; margin:2px 0 5px !important; }
.final-target-name + * { }
.radar-sub { font-size:.67rem; color:#7f93a7 !important; margin-top:3px; line-height:1.45; }
.radar-score { font-size:1.35rem; font-weight:900; color:#69b5ed !important; }
.radar-label { font-size:.62rem; color:#74899d !important; }
.radar-value { font-size:.75rem; font-weight:800; color:#cbd7e2 !important; }
.radar-badge { display:inline-block; padding:3px 7px; border-radius:999px; font-size:.58rem; font-weight:800; margin-right:4px; border:1px solid #29445d; background:#122236; color:#9fb3c6 !important; }
.radar-badge-hot { background:#3a211f; border-color:#78463f; color:#ef8c80 !important; }
.radar-badge-op { background:#16362f; border-color:#2c7965; color:#5dd3ae !important; }
.radar-badge-hold { background:#26321f; border-color:#596d3d; color:#c8d982 !important; }
.radar-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:5px; margin-top:8px; }
.radar-metric { background:#091522; border-radius:6px; padding:6px; }
.radar-note { margin-top:7px; padding:7px 8px; background:#0a1522; border-left:3px solid #3e6685; border-radius:6px; color:#aebdcb !important; font-size:.65rem; line-height:1.45; }
@media(max-width:700px){ .radar-grid{grid-template-columns:repeat(2,1fr);} }
.radar-trade-title { margin-top:10px; padding-top:9px; border-top:1px solid #22384d; font-size:.76rem; font-weight:900; color:#dce6ef !important; }
.radar-action { margin-top:5px; padding:8px 9px; border-radius:7px; background:#0a1826; border-left:3px solid #4f8eb8; color:#e1eaf2 !important; font-size:.78rem; font-weight:850; line-height:1.4; }
.radar-trade-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:5px; margin-top:7px; }
.radar-trade-item { background:#091522; border:1px solid #1d3347; border-radius:7px; padding:7px; }
.radar-trade-price { font-size:.91rem; font-weight:900; color:#e8eff5 !important; margin-top:3px; }
.radar-trade-desc { font-size:.62rem; color:#8296a9 !important; margin-top:2px; }
.radar-follow { margin-top:6px; padding:7px 8px; background:#0a1522; border-radius:6px; color:#aebdca !important; font-size:.68rem; line-height:1.4; }
.radar-follow b { color:#dce6ef !important; }
@media(max-width:700px){ .radar-trade-grid{grid-template-columns:repeat(2,1fr);} .radar-trade-price{font-size:.84rem;} .radar-action{font-size:.75rem;} }

/* ==========================================================
   READABILITY V2
   결과값을 우선 확대하고 기존 섹션 머리글은 유지합니다.
   ========================================================== */
.evidence-value { font-size: 1.00rem !important; color:#e3ebf3 !important; }
.evidence-sub { font-size: .72rem !important; color:#a8b8c8 !important; }
.judgment-main { font-size: 1.08rem !important; color:#e5edf5 !important; }
.judgment-reason, .action-main { font-size: .84rem !important; color:#c3cfda !important; }
.reason-label, .action-reason-label { font-size: .69rem !important; color:#91a5b8 !important; }
.scenario-price { font-size: 1.08rem !important; color:#e4ecf3 !important; }
.scenario-desc { font-size: .74rem !important; color:#aab9c8 !important; }
.holding-value { font-size: .98rem !important; color:#e0e8ef !important; }
.holding-detail { font-size: .76rem !important; color:#a1b1c1 !important; }
.theme-stock-name { font-size: .88rem !important; color:#e5edf5 !important; }
.theme-stock-code { font-size: .70rem !important; color:#8fa3b6 !important; }
.theme-data-label { font-size: .66rem !important; color:#8fa3b6 !important; }
.theme-data-value { font-size: .82rem !important; color:#e0e8ef !important; }
.theme-outlook { font-size: .80rem !important; color:#c7d3de !important; }
.theme-summary-title { font-size: .86rem !important; color:#e5edf5 !important; }
.theme-summary-meta { font-size: .74rem !important; color:#aab9c8 !important; }
.theme-summary-outlook { font-size: .78rem !important; color:#c4d0db !important; }
.summary-table td { font-size: .80rem !important; color:#d0dbe5 !important; }
.radar-value { font-size: .86rem !important; color:#e0e8ef !important; }
.radar-sub { font-size: .74rem !important; color:#a0b0c0 !important; }
.radar-label { font-size: .67rem !important; color:#91a5b8 !important; }
.radar-note { font-size: .74rem !important; color:#c1ced9 !important; }
.future-analysis-name { font-size: 1.12rem !important; color:#e6edf4 !important; }
.future-analysis-code { font-size: .72rem !important; color:#8fa3b6 !important; }

/* 자동판정의 핵심 결과값 */
.future-analysis .theme-outlook strong { color:#e6edf4 !important; }

/* ==========================================================
   DECISION UI V3
   운용전략 결과를 최우선으로 강조하고 가격 기준은 압축합니다.
   ========================================================== */
.strategy-section-title {
    font-size: 1.14rem !important;
    font-weight: 900 !important;
    color: #f0f5fa !important;
    margin: 17px 0 8px !important;
}
.strategy-result {
    background: #0d1d2d;
    border: 1px solid #416b8d;
    border-left: 4px solid #5da8d8;
    border-radius: 12px;
    padding: 13px 14px;
    margin-bottom: 10px;
}
.strategy-mode { font-size:.70rem; color:#a9bfd2 !important; font-weight:800; margin-bottom:2px; }
.strategy-main { font-size:1.34rem; line-height:1.25; font-weight:900; color:#f3f7fa !important; margin:2px 0 9px; }
.strategy-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:7px; }
.strategy-grid div { background:#091522; border-radius:8px; padding:8px; }
.strategy-grid span { display:block; font-size:.67rem; color:#91a7ba !important; margin-bottom:3px; }
.strategy-grid b { display:block; font-size:.91rem; color:#e6eef5 !important; line-height:1.3; }
.strategy-reason { margin-top:8px; font-size:.76rem; line-height:1.45; color:#b7c7d5 !important; }
.trade-section-title { font-size:.82rem !important; font-weight:850 !important; color:#cbd7e2 !important; margin:13px 0 5px !important; }
.trade-card-label { font-size:.68rem; color:#94a8ba !important; font-weight:800; }
.trade-card-price { font-size:.92rem; font-weight:900; color:#e6eef5 !important; margin-top:4px; }
.trade-card-price.small { font-size:.86rem; }
.trade-card-desc { font-size:.67rem; line-height:1.35; color:#aabac8 !important; margin-top:3px; }
[data-testid="stMetricValue"] { font-size:1.18rem !important; color:#edf4f8 !important; }
[data-testid="stMetricLabel"] { font-size:.68rem !important; color:#9db0c0 !important; }


@media (max-width:700px) {
    .evidence-value { font-size: .94rem !important; }
    .judgment-main { font-size: 1.00rem !important; }
    .judgment-reason, .action-main { font-size: .80rem !important; }
    .scenario-price { font-size: 1.02rem !important; }
    .scenario-desc { font-size: .72rem !important; }
    .theme-stock-name { font-size: .84rem !important; }
    .theme-data-value { font-size: .79rem !important; }
    .theme-summary-title { font-size: .84rem !important; }
    .theme-summary-meta { font-size: .72rem !important; }
    .theme-summary-outlook { font-size: .76rem !important; }
    .radar-value { font-size: .82rem !important; }
    .radar-sub { font-size: .72rem !important; }
    .future-analysis-name { font-size: 1.04rem !important; }
    .theme-outlook { font-size: .78rem !important; }
    .strategy-section-title { font-size: 1.06rem !important; }
    .strategy-main { font-size: 1.18rem !important; }
    .strategy-grid b { font-size: .84rem !important; }
    .strategy-grid { gap:5px; }
    .trade-card-price { font-size:.86rem !important; }
    [data-testid="stMetricValue"] { font-size:1.08rem !important; }
}


/* ==========================================================
   READABILITY V3 · MY 주식 / FUTURE THEME
   모바일 결과값 가독성 우선
   ========================================================== */
.strategy-mode { font-size:.90rem !important; }
.strategy-main { font-size:1.65rem !important; }
.strategy-grid span { font-size:.86rem !important; }
.strategy-grid b { font-size:1.16rem !important; }
.strategy-reason { font-size:.96rem !important; }
.trade-section-title { font-size:.76rem !important; }
.trade-card-label { font-size:.82rem !important; }
.trade-card-price { font-size:.88rem !important; }
.trade-card-desc { font-size:.82rem !important; }
[data-testid="stMetricValue"] { font-size:1.42rem !important; }
[data-testid="stMetricLabel"] { font-size:.78rem !important; }

.theme-card .theme-stage-badge { font-size:.82rem !important; }
.theme-card .theme-title { font-size:1.42rem !important; }
.theme-card .theme-reason { font-size:1.00rem !important; line-height:1.55 !important; }
.theme-card .theme-outlook { font-size:1.00rem !important; line-height:1.55 !important; }
.theme-stock-name { font-size:1.30rem !important; line-height:1.35 !important; }
.theme-stock-code { font-size:.88rem !important; }
.theme-data-label { font-size:.82rem !important; }
.theme-data-value { font-size:1.08rem !important; }
.theme-etf-box > div:last-child { font-size:.84rem !important; color:#a9bac9 !important; }
.theme-summary-title { font-size:1.20rem !important; }
.theme-summary-meta { font-size:.94rem !important; }
.theme-summary-outlook { font-size:.98rem !important; line-height:1.55 !important; }
.future-analysis-title { font-size:.92rem !important; }
.future-analysis-name { font-size:1.42rem !important; }
.future-analysis-code { font-size:.90rem !important; }
.quote-price { font-size:1.35rem !important; }
.quote-change { font-size:.98rem !important; }

/* 미래테마는 기존 포맷 유지. 종목 분석 + 관심등록 두 버튼만 한 줄 */
.future-theme-buttons { display:flex !important; gap:.45rem !important; width:100% !important; }
.future-theme-buttons > div { flex:1 1 0 !important; min-width:0 !important; }

@media(max-width:700px){
  .strategy-main { font-size:1.48rem !important; }
  .strategy-grid span { font-size:.80rem !important; }
  .strategy-grid b { font-size:1.05rem !important; }
  .strategy-reason { font-size:.90rem !important; }
  .trade-card-label { font-size:.76rem !important; }
  .trade-card-price { font-size:.82rem !important; }
  .trade-card-desc { font-size:.76rem !important; }
  [data-testid="stMetricValue"] { font-size:1.28rem !important; }
  .theme-card .theme-title { font-size:1.28rem !important; }
  .theme-card .theme-reason, .theme-card .theme-outlook { font-size:.92rem !important; }
  .theme-stock-name { font-size:1.10rem !important; }
  .theme-stock-code { font-size:.82rem !important; }
  .theme-data-label { font-size:.76rem !important; }
  .theme-data-value { font-size:.98rem !important; }
  .theme-summary-title { font-size:1.08rem !important; }
  .theme-summary-meta { font-size:.86rem !important; }
  .theme-summary-outlook { font-size:.88rem !important; }
  .future-analysis-name { font-size:1.22rem !important; }
}


/* ==========================================================
   DECISION UI V4 · 상태별 단일 행동영역 + 미보유 가독성 강화
   ========================================================== */
.trade-section-title {
    font-size: 1.38rem !important;
    font-weight: 900 !important;
    color: #eef5fa !important;
    margin: 16px 0 7px !important;
}
.trade-card-label {
    font-size: 1.02rem !important;
    color: #b5c6d5 !important;
    font-weight: 900 !important;
}
.trade-card-price {
    font-size: 1.42rem !important;
    font-weight: 900 !important;
    color: #f0f6fa !important;
    margin-top: 5px !important;
}
.trade-card-price.small {
    font-size: 1.14rem !important;
}
.trade-card-desc {
    font-size: 1.00rem !important;
    line-height: 1.42 !important;
    color: #c0cfdb !important;
    margin-top: 4px !important;
}
@media(max-width:700px){
    .trade-section-title { font-size: 1.30rem !important; }
    .trade-card-label { font-size: .98rem !important; }
    .trade-card-price { font-size: 1.34rem !important; }
    .trade-card-price.small { font-size: 1.14rem !important; }
    .trade-card-desc { font-size: .94rem !important; }
}

/* ==========================================================
   FINAL UI FIX — ownership split + future theme 6-group layout
   ========================================================== */
.trade-section-title{font-size:1.18rem !important;font-weight:900 !important;color:#eef5fb !important;margin:16px 0 8px !important;}
.trade-card-label{font-size:.86rem !important;color:#cbd8e4 !important;}
.trade-card-price{font-size:1.20rem !important;color:#edf4f9 !important;font-weight:900 !important;}
.trade-card-price.small{font-size:1.08rem !important;}
.future-group-title{font-size:1.18rem !important;font-weight:900 !important;margin:18px 0 9px !important;padding:9px 12px !important;border-radius:10px !important;border:1px solid #416b8d !important;color:#f0f5fa !important;}
.future-group-priority{background:#152b3c !important;border-color:#4f86a9 !important;}
.future-group-secondary{background:#202a35 !important;border-color:#64778a !important;}
.future-group-watch{background:#252b31 !important;border-color:#66717b !important;}
.future-theme-headbox{border-radius:12px !important;padding:11px 13px !important;margin:8px 0 7px !important;}
.future-theme-headbox.future-group-priority{background:#102637 !important;border:1px solid #477fa4 !important;}
.future-theme-headbox.future-group-secondary{background:#18242f !important;border:1px solid #5d7182 !important;}
.future-theme-headbox.future-group-watch{background:#20272d !important;border:1px solid #66717b !important;}
.future-stock-card{background:#101b25 !important;border:1px solid #30485b !important;border-radius:11px !important;padding:12px !important;margin-bottom:7px !important;}
.future-rank-badge{display:inline-block !important;font-size:.82rem !important;font-weight:900 !important;color:#dfeaf3 !important;margin-bottom:4px !important;}
.future-etf-action{font-size:.90rem !important;font-weight:800 !important;color:#d6e4ee !important;margin:4px 0 7px !important;}
.future-stock-card .theme-stock-name{font-size:1.00rem !important;color:#edf4f9 !important;font-weight:900 !important;}
.future-stock-card .theme-stock-code{font-size:.78rem !important;color:#9eb1c2 !important;}
.future-stock-card .theme-data-label{font-size:.73rem !important;color:#9eb0c0 !important;}
.future-stock-card .theme-data-value{font-size:.92rem !important;color:#e3edf4 !important;font-weight:800 !important;}
[data-testid="stMetricValue"]{font-size:1.28rem !important;color:#edf5fa !important;}
@media(max-width:700px){.trade-section-title{font-size:1.10rem !important}.trade-card-price{font-size:1.10rem !important}.future-group-title{font-size:1.08rem !important}.future-stock-card .theme-stock-name{font-size:.94rem !important}.future-stock-card .theme-data-value{font-size:.86rem !important}.future-etf-action{font-size:.84rem !important}}

/* 미래테마 버튼 2개를 모바일에서도 한 행에 고정 */
div[data-testid="stHorizontalBlock"]:has([class*="st-key-future_an_"]) ,
div[data-testid="stHorizontalBlock"]:has([class*="st-key-future_watch_"]) {
    display:flex !important;
    flex-direction:row !important;
    flex-wrap:nowrap !important;
    width:100% !important;
    align-items:stretch !important;
    gap:.5rem !important;
}
div[data-testid="stHorizontalBlock"]:has([class*="st-key-future_an_"]) > div,
div[data-testid="stHorizontalBlock"]:has([class*="st-key-future_watch_"]) > div {
    min-width:0 !important;
    width:50% !important;
    flex:1 1 50% !important;
}
div[data-testid="stHorizontalBlock"]:has([class*="st-key-future_an_"]) button,
div[data-testid="stHorizontalBlock"]:has([class*="st-key-future_watch_"]) button {
    width:100% !important;
    white-space:nowrap !important;
}
/* C/D 미래테마 핵심 결과 가독성 */
.priority-theme-card .theme-stock-title { font-size:1.14rem !important; color:#ffffff !important; }
.priority-theme-card .theme-summary-meta { font-size:.80rem !important; color:#b9c7d4 !important; }
.priority-theme-card .theme-summary-outlook { font-size:.82rem !important; color:#d0dbe5 !important; }
.priority-theme-card .cd-item .theme-summary-title { font-size:1.00rem !important; color:#ffffff !important; }
.priority-theme-card .cd-item .theme-summary-meta { font-size:.82rem !important; color:#d0dbe5 !important; line-height:1.65 !important; }
.theme-summary-card .theme-stock-title { font-size:1.04rem !important; color:#ffffff !important; }
.theme-summary-card .theme-summary-meta { font-size:.78rem !important; color:#b1c0ce !important; }
.theme-summary-card .theme-summary-outlook { font-size:.80rem !important; color:#c8d4df !important; }

/* 미래테마: 테마명 + 최우선 주식 + C/D 가이드를 하나의 강조 박스로 묶음 */
.priority-theme-card {
    background:linear-gradient(180deg,#132b3d 0%,#0f1d29 100%) !important;
    border:1px solid #4d86ab !important;
    border-radius:14px !important;
    padding:14px !important;
    margin:10px 0 10px !important;
    box-shadow:0 2px 8px rgba(0,0,0,.22) !important;
}
.priority-theme-card .priority-theme-head {
    background:#1a3a50 !important;
    border:1px solid #5b93b7 !important;
    border-radius:10px !important;
    padding:11px 13px !important;
    margin-bottom:9px !important;
}
.priority-theme-card .priority-theme-head .theme-title {
    font-size:1.28rem !important; font-weight:900 !important; color:#ffffff !important;
}
.priority-theme-card .theme-summary-card {
    background:#101f2c !important; border:1px solid #36566d !important;
    border-radius:10px !important; padding:11px 13px !important;
}
.priority-theme-card .cd-item {
    background:#172a39 !important; border:1px solid #45667e !important;
    border-radius:10px !important; padding:11px 13px !important; margin-top:9px !important;
}
@media(max-width:700px){
 .priority-theme-card .priority-theme-head .theme-title{font-size:1.18rem !important;}
 .priority-theme-card .theme-stock-title{font-size:1.12rem !important;}
 .priority-theme-card .theme-summary-meta{font-size:.88rem !important;}
 .priority-theme-card .theme-summary-outlook{font-size:.90rem !important;}
 .priority-theme-card .cd-item .theme-summary-meta{font-size:.90rem !important;}
}
/* FINAL TARGET V5 */
.final-target-primary{background:linear-gradient(145deg,#173b52 0%,#0d2232 58%,#0b1725 100%) !important;border:2px solid #5aa8d8 !important;border-radius:16px !important;padding:16px !important;margin:8px 0 14px !important;box-shadow:0 4px 18px rgba(45,120,170,.18) !important;}
.final-target-primary .final-target-rank{font-size:.84rem !important;color:#7ec8f5 !important;}
.final-target-primary .final-target-name-main{font-size:1.55rem !important;line-height:1.25 !important;font-weight:950 !important;color:#ffffff !important;margin-top:5px !important;}
.final-target-primary .final-target-code{font-size:.86rem !important;color:#a9bfd0 !important;margin-top:3px !important;}
.final-target-primary .final-target-score{font-size:2.15rem !important;font-weight:950 !important;color:#74c5f4 !important;line-height:1 !important;}
.final-target-primary .final-target-horizon{font-size:.94rem !important;font-weight:900 !important;color:#f0d36d !important;}
.final-target-primary .final-target-reason{margin-top:9px !important;padding:8px 9px !important;background:#0a1826 !important;border-radius:8px !important;color:#d2dee8 !important;font-size:.78rem !important;line-height:1.5 !important;}
.final-secondary-target{background:#0d1928 !important;border:1px solid #30485b !important;border-radius:11px !important;padding:11px !important;margin:7px 0 !important;}
.final-secondary-target .final-target-name-main{font-size:1.08rem !important;font-weight:900 !important;color:#edf4f9 !important;}
.final-secondary-target .final-target-code{font-size:.72rem !important;color:#93a9bb !important;}
.final-secondary-target .final-target-score{font-size:1.20rem !important;font-weight:900 !important;color:#69b5ed !important;}
.final-secondary-target .final-target-horizon{font-size:.76rem !important;font-weight:850 !important;color:#e0c768 !important;}
.final-target-divider{height:1px;background:#2b4559;margin:12px 0 !important;}
.final-horizon-box .final-horizon-label{font-size:.90rem !important;font-weight:900 !important;color:#b8c9d8 !important;}
.final-horizon-box .final-horizon-value{font-size:1.12rem !important;font-weight:950 !important;color:#f0f6fa !important;}
.radar-score-block .radar-score{font-size:1.85rem !important;}
.radar-score-code{font-size:.74rem !important;color:#8ea5b8 !important;margin-top:3px !important;}
@media(max-width:700px){
.final-target-primary{padding:14px !important;}
.final-target-primary .final-target-name-main{font-size:1.38rem !important;}
.final-target-primary .final-target-score{font-size:1.95rem !important;}
.final-target-primary .final-target-horizon{font-size:.86rem !important;}
.final-horizon-box .final-horizon-label{font-size:.86rem !important;}
.final-horizon-box .final-horizon-value{font-size:1.04rem !important;}
.radar-score-block .radar-score{font-size:1.65rem !important;}
}
</style>
"""

if hasattr(st, "html"):
    st.html(CSS)
else:
    st.markdown(CSS, unsafe_allow_html=True)


# ============================================================
# FILES
# ============================================================

WATCHLIST_FILE = "stock_watchlist.json"
HOLDINGS_FILE = "stock_holdings.json"


# ============================================================
# BASE 주식
# ============================================================

# ============================================================
# LIVE 주식 MASTER
# 종목코드/종목명은 KRX + Naver Finance에서 실시간으로 구성합니다.
# 하드코딩된 주식 종목명 목록은 사용하지 않습니다.
# ============================================================

BASE_주식S = {}


DEFAULT_WATCHLIST = [
    "005930",  # 삼성전자
    "000660",  # SK하이닉스
    "042700",  # 한미반도체
    "034020",  # 두산에너빌리티
    "329180",  # HD현대중공업
    "012450",  # 한화에어로스페이스
]


# ============================================================
# FUTURE THEME AUTO-UNIVERSE
# 고정 5개 테마를 사용하지 않고 전체 주식 이름에서 테마 후보를 자동 발굴합니다.
# 동의어 사전은 테마를 찾기 위한 최소한의 언어 기준이며, 실제 표시 여부와 순위는
# 현재 주식 유니버스와 가격 데이터로 결정됩니다.
THEME_LEXICON = {
    "AI 반도체": ["반도체", "AI반도체", "AI 반도체", "HBM", "메모리", "시스템반도체", "반도체장비", "반도체소부장"],
    "로봇": ["로봇", "로보틱스", "휴머노이드", "로보틱", "스마트팩토리"],
    "방산": ["방산", "방위산업", "K방산", "국방", "우주항공방산"],
    "2차전지": ["2차전지", "이차전지", "배터리", "전고체", "양극재", "음극재", "리튬", "배터리소재"],
    "전기차": ["전기차", "EV", "전기자동차", "자율주행", "모빌리티"],
    "조선": ["조선", "조선업", "선박", "LNG선", "해운", "선박기자재"],
    "원자력": ["원자력", "원전", "SMR", "소형모듈원전", "핵융합"],
    "전력 인프라": ["전력", "전력인프라", "전력설비", "전력망", "변압기", "전선", "송배전", "전기설비"],
    "데이터센터·AI 인프라": ["데이터센터", "AI인프라", "AI 인프라", "서버", "네트워크", "클라우드", "IDC"],
    "냉각·열관리": ["냉각", "열관리", "액침냉각", "수랭", "칠러", "열교환", "냉동공조"],
    "바이오": ["바이오", "헬스케어", "제약", "신약", "항암", "면역", "의료기기", "유전체"],
    "우주항공": ["우주", "우주항공", "항공우주", "위성", "발사체", "UAM"],
    "AI 소프트웨어": ["AI", "인공지능", "생성AI", "AI소프트웨어", "소프트웨어", "빅데이터"],
    "클라우드": ["클라우드", "SaaS", "데이터센터"],
    "보안": ["보안", "사이버보안", "정보보안", "보안솔루션"],
    "5G·통신": ["5G", "6G", "통신", "네트워크", "위성통신"],
    "신재생에너지": ["태양광", "태양광발전", "풍력", "신재생", "친환경에너지", "수소"],
    "수소": ["수소", "수소경제", "수소연료전지", "연료전지"],
    "친환경·탄소": ["탄소", "탄소중립", "친환경", "ESG", "폐기물", "리사이클", "재활용"],
    "금융": ["은행", "금융", "증권", "보험", "고배당", "배당"],
    "자동차": ["자동차", "자동차부품", "차량", "모빌리티"],
    "화장품·K뷰티": ["화장품", "K뷰티", "뷰티", "미용"],
    "음식료·소비": ["음식료", "식품", "소비재", "유통", "소비"],
    "건설·인프라": ["건설", "인프라", "SOC", "건설기계", "시멘트"],
    "철강·금속": ["철강", "금속", "구리", "알루미늄", "비철금속"],
    "원자재": ["원자재", "상품", "원유", "천연가스", "커머디티"],
    "금·귀금속": ["금", "골드", "귀금속", "은", "실버"],
    "중국": ["중국", "차이나", "CSI", "홍콩", "상하이"],
    "미국 기술": ["나스닥", "미국테크", "미국기술", "S&P500", "테크"],
    "반도체 장비·소부장": ["반도체장비", "반도체장비주", "소부장", "소재부품장비", "장비"],
}


# ============================================================
# AUTO THEME DISCOVERY V2
# 주식 MASTER가 갱신되면 종목명에서 반복되는 산업/기술 키워드를 자동 발굴합니다.
# 기존 THEME_LEXICON은 seed로 유지하고, 신규 후보는 최소 주식 수/빈도/노이즈 필터를 통과한 것만 사용합니다.
# ============================================================
_AUTO_THEME_STOP = {
    "etf","인버스","레버리지","커버드콜","채권","국채","단기채","월배당","배당","액티브",
    "증권","미국","한국","글로벌","코리아","선진국","신흥국","TOP","TOP10","TOP5",
    "혼합","파생","환헤지","합성","TR","H","PLUS","TIGER","KODEX","ACE","RISE","SOL","TIMEFOLIO",
    "HANARO","KOSEF","KBSTAR","WOORI","ARIRANG","FOCUS","UNICORN","TREX","KIWOOM"
}

@st.cache_data(ttl=1800, show_spinner=False)
def discover_auto_theme_lexicon(universe_items):
    """종목명 자체에서 반복되는 후보 테마를 발견합니다. 가격 데이터는 사용하지 않습니다."""
    from collections import Counter
    counts=Counter()
    samples={}
    for code,name in universe_items:
        text=re.sub(r"[^0-9A-Za-z가-힣]", " ", str(name or ""))
        # 한글 2~7글자 연속 구간에서 n-gram 후보를 추출
        words=re.findall(r"[가-힣]{2,8}", text)
        seen=set()
        for w in words:
            if w in _AUTO_THEME_STOP or len(w)<2: continue
            pieces={w}
            if len(w)>=4:
                for n in (2,3,4):
                    for i in range(0,len(w)-n+1): pieces.add(w[i:i+n])
            for term in pieces:
                if term in _AUTO_THEME_STOP or len(term)<2: continue
                if term in seen: continue
                seen.add(term); counts[term]+=1; samples.setdefault(term,[]).append((code,name))
    # 기존 사전과 겹치거나 지나치게 일반적인 단어 제거
    existing_kw=set()
    for kws in THEME_LEXICON.values(): existing_kw.update(map(str,kws))
    ranked=[]
    for term,n in counts.items():
        if n<3 or term in existing_kw: continue
        if term in {"투자","산업","기업","시장","전략","포트","미래","테마","성장","수익","인덱스","코스피","코스닥"}: continue
        # 너무 짧은 후보는 최소 3개 주식, 긴 후보는 2개 이상이어야 안정적
        if len(term)==2 and n<4: continue
        ranked.append((n, len(term), term))
    ranked.sort(key=lambda x:(x[0],x[1]), reverse=True)
    out={}
    for n,_,term in ranked[:35]:
        # 동일 후보가 기존 키워드의 부분문자열이면 새 테마로 만들지 않음
        if any(term in k or k in term for k in existing_kw if len(k)>=2):
            continue
        out[f"자동·{term}"]=[term]
        if len(out)>=18: break
    return out


def get_dynamic_theme_lexicon(universe):
    items=tuple(sorted((str(k),str(v)) for k,v in universe.items()))
    auto=discover_auto_theme_lexicon(items)
    merged=dict(THEME_LEXICON)
    merged.update(auto)
    return merged

# 네트워크가 일시적으로 실패해도 핵심 대형주 이름과 미래테마 연결이 끊기지 않도록 하는 최소 fallback입니다.
CORE_STOCK_NAMES = {
    "005930":"삼성전자", "000660":"SK하이닉스", "042700":"한미반도체",
    "034020":"두산에너빌리티", "329180":"HD현대중공업", "012450":"한화에어로스페이스",
    "009150":"삼성전기", "035420":"NAVER", "035720":"카카오", "068270":"셀트리온",
    "207940":"삼성바이오로직스", "005380":"현대차", "000270":"기아",
    "267260":"HD현대일렉트릭", "298040":"효성중공업", "010120":"LS ELECTRIC",
    "010140":"삼성중공업", "042660":"한화오션", "064350":"현대로템",
    "079550":"LIG넥스원", "047810":"한국항공우주", "272210":"한화시스템",
    "454910":"두산로보틱스", "277810":"레인보우로보틱스", "108490":"로보티즈",
    "373220":"LG에너지솔루션", "006400":"삼성SDI", "096770":"SK이노베이션",
    "247540":"에코프로비엠", "086520":"에코프로", "003670":"포스코퓨처엠",
    "066970":"엘앤에프", "028300":"HLB", "196170":"알테오젠",
    "000100":"유한양행", "128940":"한미약품", "004170":"신세계",
    "090430":"아모레퍼시픽", "051910":"LG화학", "032830":"삼성생명",
    "105560":"KB금융", "055550":"신한지주", "086790":"하나금융지주",
}

STOCK_THEME_ALIASES = {
    "AI 반도체":["삼성전자","SK하이닉스","한미반도체","HPSP","테크윙","주성엔지니어링","이오테크닉스","리노공업","원익IPS","DB하이텍"],
    "로봇":["두산로보틱스","레인보우로보틱스","로보티즈","뉴로메카","에스피지","유진로봇"],
    "방산":["한화에어로스페이스","현대로템","LIG넥스원","한국항공우주","한화시스템","풍산"],
    "2차전지":["LG에너지솔루션","삼성SDI","SK이노베이션","에코프로비엠","에코프로","포스코퓨처엠","엘앤에프","금양"],
    "조선":["HD현대중공업","HD한국조선해양","한화오션","삼성중공업","현대미포조선"],
    "원자력":["두산에너빌리티","한전기술","한전KPS","우진","비에이치아이","우리기술"],
    "전력 인프라":["HD현대일렉트릭","효성중공업","LS ELECTRIC","LS","대한전선","일진전기","산일전기"],
    "데이터센터·AI 인프라":["SK하이닉스","삼성전자","LS ELECTRIC","HD현대일렉트릭","가온전선","대한전선"],
    "냉각·열관리":["GST","케이엔솔","신성이엔지","3S","유니셈","한온시스템"],
    "바이오":["삼성바이오로직스","셀트리온","유한양행","한미약품","알테오젠","리가켐바이오","HLB"],
    "우주항공":["한국항공우주","한화에어로스페이스","쎄트렉아이","AP위성","인텔리안테크"],
    "자동차":["현대차","기아","현대모비스","HL만도","현대위아"],
    "화장품·K뷰티":["아모레퍼시픽","LG생활건강","한국콜마","코스맥스","브이티","실리콘투"],
    "금융":["KB금융","신한지주","하나금융지주","우리금융지주","메리츠금융지주","삼성생명"],
}
for _theme,_names in STOCK_THEME_ALIASES.items():
    THEME_LEXICON.setdefault(_theme,[])
    THEME_LEXICON[_theme]=list(dict.fromkeys(THEME_LEXICON[_theme]+_names))

THEME_REASONS = {
    "AI 반도체":"AI 연산과 데이터 처리 수요 확대에 직접 연결되는 반도체 산업 흐름입니다.",
    "로봇":"자동화·휴머노이드·스마트팩토리 투자 확대와 연결되는 산업 흐름입니다.",
    "방산":"국방비 확대와 글로벌 방산 수요 변화에 연결되는 산업 흐름입니다.",
    "2차전지":"전기차·ESS·배터리 기술 변화와 연결되는 배터리 산업 흐름입니다.",
    "전기차":"전동화와 미래 모빌리티 투자 흐름을 추적합니다.",
    "조선":"선박 발주와 친환경·고부가 선박 수요에 연결되는 산업 흐름입니다.",
    "원자력":"원전·SMR 등 장기 전력 수요와 에너지 투자 흐름을 추적합니다.",
    "전력 인프라":"전력수요 증가와 송배전·변압기·전선 설비 투자 흐름입니다.",
    "데이터센터·AI 인프라":"AI 확산에 따른 데이터센터·서버·네트워크 투자 흐름입니다.",
    "냉각·열관리":"고집적 서버와 산업설비 확대에 따른 냉각·열관리 수요 흐름입니다.",
}

THEMES = {}
FUTURE_CHAIN = []

# JSON
# ============================================================

def read_json(path, default):
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return default


def write_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


# ============================================================
# 주식 UNIVERSE
# ============================================================

def _normalize_stock_code(code):
    code = str(code or "").strip().upper()
    if code.isdigit():
        return code.zfill(6)
    return code


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_naver_stock_master():
    """KRX 실패 시 사용하는 네이버 KOSPI/KOSDAQ 종목 목록 fallback."""
    headers={"User-Agent":"Mozilla/5.0","Referer":"https://finance.naver.com/sise/sise_market_sum.naver"}
    result={}
    try:
        for sosok in (0,1):
            for page in range(1,101):
                url=f"https://finance.naver.com/sise/sise_market_sum.naver?sosok={sosok}&page={page}"
                r=requests.get(url,headers=headers,timeout=10); r.raise_for_status()
                text=r.content.decode("euc-kr",errors="ignore")
                found=re.findall(r"(?:main\.naver\?code=|item/main\.naver\?code=)(\d{6})[^>]*>(.*?)</a>",text,re.S)
                if not found: break
                before=len(result)
                for code,raw_name in found:
                    name=re.sub(r"<[^>]+>","",raw_name).strip()
                    if name: result[code]=safe_stock_name(code,html.unescape(name))
                if len(result)==before: break
    except Exception:
        pass
    return result


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_krx_stock_master():
    """KRX 전종목 기본정보에서 KOSPI/KOSDAQ 개별주 유니버스를 구성합니다."""
    url="https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
    headers={"User-Agent":"Mozilla/5.0","Accept":"application/json,text/plain,*/*","Referer":"https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd","Origin":"https://data.krx.co.kr"}
    payload={"bld":"dbms/MDC/STAT/standard/MDCSTAT01901","locale":"ko_KR","mktId":"ALL","share":"1","csvxls_isNo":"false"}
    try:
        r=requests.post(url,headers=headers,data=payload,timeout=20); r.raise_for_status(); data=r.json()
        rows=data.get("OutBlock_1") or data.get("output") or []
        result={}
        for x in rows:
            code=_normalize_stock_code(x.get("ISU_SRT_CD") or x.get("isu_srt_cd"))
            name=x.get("ISU_ABBRV") or x.get("ISU_NM") or x.get("isu_abrv")
            market=str(x.get("MKT_TP_NM") or "")
            security=str(x.get("SECUGRP_NM") or x.get("KIND_STKCERT_DIV_NM") or "")
            if code and len(code)==6 and name and market in ("KOSPI","KOSDAQ"):
                # 일반 주식의 SECUGRP_NM이 '주식/주권'으로 내려오는 경우가 있어
                # '주식'을 제외 조건으로 사용하면 전 종목이 사라집니다.
                # ETF/ETN/ELW 등만 제외하고 일반 KOSPI/KOSDAQ 주식은 모두 유지합니다.
                sec_upper=security.upper()
                if any(k in sec_upper for k in ("ETF","ETN","ELW")):
                    continue
                result[code]=safe_stock_name(code,name)
        return result
    except Exception:
        return {}


def load_stock_universe():
    """KRX를 1순위로 사용하고 네이버를 fallback으로 보완하는 국내 개별주 유니버스."""
    krx=fetch_krx_stock_master(); naver=fetch_naver_stock_master()
    universe=dict(krx)
    for code,name in naver.items():
        if code not in universe or not universe[code] or universe[code].startswith("주식 "):
            universe[code]=name
    for code,name in CORE_STOCK_NAMES.items():
        universe.setdefault(code,name)
    return universe

# ============================================================
# STATE
# ============================================================

def init_state():
    if "watchlist" not in st.session_state:
        saved = read_json(WATCHLIST_FILE, DEFAULT_WATCHLIST.copy())
        if isinstance(saved, list):
            st.session_state.watchlist = [_normalize_stock_code(x) for x in saved]
        else:
            st.session_state.watchlist = DEFAULT_WATCHLIST.copy()

    if "holdings" not in st.session_state:
        saved = read_json(HOLDINGS_FILE, {})
        st.session_state.holdings = saved if isinstance(saved, dict) else {}

    if "stock_universe" not in st.session_state:
        st.session_state.stock_universe = load_stock_universe()
        if not st.session_state.stock_universe:
            st.session_state.stock_universe = {}

    if "price_cache" not in st.session_state:
        st.session_state.price_cache = {}

    if "theme_cache" not in st.session_state:
        st.session_state.theme_cache = {}

    if "selected_code" not in st.session_state:
        st.session_state.selected_code = (
            st.session_state.watchlist[0]
            if st.session_state.watchlist
            else "005930"
        )

    if "main_page" not in st.session_state:
        st.session_state.main_page = "🏆 최종 타겟"

    if "future_detail_code" not in st.session_state:
        st.session_state.future_detail_code = None

    if "future_detail_theme" not in st.session_state:
        st.session_state.future_detail_theme = None

    if "radar_cache" not in st.session_state:
        st.session_state.radar_cache = None

    if "radar_mode" not in st.session_state:
        st.session_state.radar_mode = "🎯 유망후보"

    if "future_engine_cache" not in st.session_state:
        st.session_state.future_engine_cache = None


# ============================================================
# BASIC HELPERS
# ============================================================


def _name_has_hangul(text):
    return any("가" <= ch <= "힣" for ch in str(text))


def _looks_mojibake(text):
    t = str(text)
    bad = ("Ã", "Â", "â", "ê", "ë", "ì", "í", "î", "ï", "ð", "ñ", "�", "�")
    return any(x in t for x in bad)


def safe_stock_name(code, name=None):
    code = str(code).zfill(6)
    # 일부 캐시에는 주식 레코드 전체가 문자열로 저장되어 있습니다.
    # 예: {'name': 'KODEX TRF3070', 'ticker': '329650.KS', 'themes': []}
    # 이 레코드 자체를 이름으로 표시하지 않고 name 필드만 추출합니다.
    if isinstance(name, dict):
        name = name.get("name") or name.get("etf_name") or name.get("title")

    text = html.unescape(str(name or "")).strip()
    if text.startswith("{") and "'name'" in text:
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, dict):
                text = str(parsed.get("name") or parsed.get("etf_name") or parsed.get("title") or "").strip()
        except Exception:
            # JSON/파이썬 dict 문자열이 완전하지 않은 경우에는 정규식으로 name만 추출
            m = re.search(r"['\"]name['\"]\s*:\s*['\"]([^'\"]+)['\"]", text)
            if m:
                text = m.group(1).strip()

    # HTML 엔티티가 남아 있거나 레코드 구조가 그대로 노출되는 경우도 차단합니다.
    text = html.unescape(text).strip()
    if not text or _looks_mojibake(text) or text.startswith("{") or "'ticker'" in text or '"ticker"' in text:
        return f"주식 {code}"
    return text


def get_stock_name(code):
    code = str(code).zfill(6)
    name=safe_stock_name(code, st.session_state.stock_universe.get(code))
    if name.startswith("주식 "):
        name=CORE_STOCK_NAMES.get(code,name)
    return name


def normalize_df(df):
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        new_columns = []
        for col in df.columns:
            if isinstance(col, tuple):
                found = None
                for item in col:
                    item_str = str(item)
                    if item_str.lower() in ["open", "high", "low", "close", "volume"]:
                        found = item_str.title()
                        break
                new_columns.append(found if found else str(col[0]))
            else:
                new_columns.append(str(col))
        df.columns = new_columns

    rename_map = {}
    for col in df.columns:
        key = str(col).lower()
        if key == "open":
            rename_map[col] = "Open"
        elif key == "high":
            rename_map[col] = "High"
        elif key == "low":
            rename_map[col] = "Low"
        elif key == "close":
            rename_map[col] = "Close"
        elif key == "volume":
            rename_map[col] = "Volume"

    df = df.rename(columns=rename_map)
    required = ["Open", "High", "Low", "Close", "Volume"]
    if not all(col in df.columns for col in required):
        return pd.DataFrame()

    df = df[required].copy()
    for col in required:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Close"])
    if getattr(df.index, "tz", None) is not None:
        try:
            df.index = df.index.tz_localize(None)
        except Exception:
            pass
    return df


# ============================================================
# PRICE DATA
# ============================================================

def fetch_naver_history(code, count=600):
    """Yahoo에서 제공하지 않는 국내 개별주 코드를 위한 Naver 가격 fallback."""
    code = _normalize_stock_code(code)
    url = f"https://fchart.stock.naver.com/sise.nhn?symbol={code}&timeframe=day&count={count}&requestType=0"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=12)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        rows = []
        for item in root.findall(".//item"):
            raw = item.attrib.get("data", "")
            parts = raw.split("|")
            if len(parts) < 6:
                continue
            rows.append(parts[:6])
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["Date", "Close"]).set_index("Date")
        return normalize_df(df)
    except Exception:
        return pd.DataFrame()


def fetch_yahoo(code):
    code = _normalize_stock_code(code)
    for suffix in (".KS", ".KQ"):
        try:
            df=yf.download(f"{code}{suffix}",period="2y",interval="1d",auto_adjust=False,progress=False,threads=False)
            df=normalize_df(df)
            if not df.empty and len(df)>=5:
                return df
        except Exception:
            pass
    return fetch_naver_history(code)

def load_price_data(code, force=False):
    code = str(code).zfill(6)
    now = datetime.now()
    cached = st.session_state.price_cache.get(code)
    if cached and not force:
        age = (now - cached["time"]).total_seconds()
        if age < 300:
            return cached["data"]

    df = fetch_yahoo(code)
    if not df.empty:
        st.session_state.price_cache[code] = {
            "time": now,
            "data": df
        }
    return df


# ============================================================
# INDICATORS
# ============================================================

def calculate_indicators(df):
    if df.empty:
        return pd.DataFrame()
    d = df.copy()

    d["MA20"] = d["Close"].rolling(20).mean()
    d["MA60"] = d["Close"].rolling(60).mean()
    d["MA120"] = d["Close"].rolling(120).mean()
    d["MA200"] = d["Close"].rolling(200).mean()

    delta = d["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta).clip(upper=0).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    d["RSI14"] = 100 - (100 / (1 + rs))

    d["VOL20"] = d["Volume"].rolling(20).mean()
    d["VOL_RATIO"] = d["Volume"] / d["VOL20"].replace(0, np.nan)
    tr = pd.concat([
        d["High"] - d["Low"],
        (d["High"] - d["Close"].shift(1)).abs(),
        (d["Low"] - d["Close"].shift(1)).abs(),
    ], axis=1).max(axis=1)
    d["ATR14"] = tr.rolling(14).mean()
    d["TRADING_VALUE"] = d["Close"] * d["Volume"]

    d["RET5"] = d["Close"].pct_change(5) * 100
    d["RET20"] = d["Close"].pct_change(20) * 100
    d["RET60"] = d["Close"].pct_change(60) * 100
    d["RET120"] = d["Close"].pct_change(120) * 100
    d["RET250"] = d["Close"].pct_change(250) * 100

    d["HIGH20"] = d["High"].rolling(20).max()
    d["LOW20"] = d["Low"].rolling(20).min()
    d["HIGH60"] = d["High"].rolling(60).max()
    d["LOW60"] = d["Low"].rolling(60).min()

    return d


# ============================================================
# HELPERS
# ============================================================

def safe_float(value, default=0.0):
    """숫자 변환 + NaN/±inf 방어. ML/점수 계산에 비정상값이 전파되지 않게 합니다."""
    try:
        if pd.isna(value):
            return default
        v = float(value)
        if not np.isfinite(v):
            return default
        # 극단적인 API/계산 이상치도 ML 입력으로 전달하지 않습니다.
        if abs(v) > 1e12:
            return default
        return v
    except Exception:
        return default


def money(value):
    value = safe_float(value)
    if abs(value) >= 1000:
        return f"{value:,.0f}원"
    return f"{value:,.2f}원"


# ============================================================
# JUDGMENT
# ============================================================

def get_judgment(d):
    if d.empty:
        return {
            "title": "데이터 부족",
            "reasons": ["가격 데이터를 확인하지 못했습니다."],
            "action": "가격 데이터를 다시 확인해 주세요.",
            "ma_state": "확인 불가",
            "rsi_state": "확인 불가",
            "vol_state": "확인 불가",
            "rsi": 0,
            "vol_ratio": 0,
            "ret20": 0
        }

    row = d.iloc[-1]
    current = safe_float(row["Close"])
    ma20 = safe_float(row["MA20"], current)
    ma60 = safe_float(row["MA60"], current)
    rsi = safe_float(row["RSI14"], 50)
    vol_ratio = safe_float(row["VOL_RATIO"], 1)
    ret20 = safe_float(row["RET20"], 0)

    above20 = current >= ma20
    above60 = current >= ma60

    ma_state = "20일선 상회" if above20 else "20일선 하회"

    if rsi >= 70:
        rsi_state = "과열권"
    elif rsi >= 60:
        rsi_state = "강세권"
    elif rsi >= 45:
        rsi_state = "중립권"
    elif rsi >= 30:
        rsi_state = "약세권"
    else:
        rsi_state = "과매도권"

    if vol_ratio >= 1.5:
        vol_state = "거래량 강한 확대"
    elif vol_ratio >= 1.1:
        vol_state = "거래량 증가"
    elif vol_ratio >= 0.8:
        vol_state = "평균 수준"
    else:
        vol_state = "거래량 감소"

    if above20 and above60 and rsi >= 70:
        title = "상승 추세 · 추격 주의"
        action = "추세는 양호하지만 과열 가능성이 있습니다. 신규 매수는 현재가 추격보다 눌림 확인을 우선합니다."
    elif above20 and above60:
        title = "상승 추세 유지"
        action = "20일선과 60일선 위입니다. 보유자는 추세를 확인하고 신규 매수는 돌파 추격보다 눌림을 우선합니다."
    elif above60 and not above20:
        title = "단기 조정 · 중기 추세 확인"
        action = "20일선 아래지만 60일선 위입니다. 20일선 회복 여부를 확인하면서 지지구간의 거래량을 봅니다."
    elif not above60 and rsi <= 40:
        title = "중기 약세 · 방어 우선"
        action = "60일선 아래이고 RSI도 약합니다. 지지 형성과 거래량 회복을 먼저 확인합니다."
    else:
        title = "방향 확인 구간"
        action = "추세가 명확하지 않습니다. 20일선 회복 또는 최근 고점 돌파와 거래량 동반 여부를 확인합니다."

    reasons = [
        f"현재가 {money(current)} · 20일선 {money(ma20)} · {ma_state}",
        f"60일선 {money(ma60)} · {'중기 추세 유지' if above60 else '중기 추세 약화'}",
        f"RSI14 {rsi:.1f} · {rsi_state}",
        f"거래량 {vol_ratio:.2f}배 · {vol_state} · 최근 20일 {ret20:+.2f}%"
    ]

    return {
        "title": title,
        "reasons": reasons,
        "action": action,
        "ma_state": ma_state,
        "rsi_state": rsi_state,
        "vol_state": vol_state,
        "rsi": rsi,
        "vol_ratio": vol_ratio,
        "ret20": ret20
    }


# ============================================================
# HORIZON / VALIDATED C-D ENGINE
# ============================================================

def leading_signal(row, benchmark_ret20=0):
    current=safe_float(row.get("Close",0)); ma20=safe_float(row.get("MA20",current),current); ma60=safe_float(row.get("MA60",current),current)
    ret5=safe_float(row.get("RET5",row.get("R5",0)),0); ret20=safe_float(row.get("RET20",row.get("R20",0)),0)
    vr=safe_float(row.get("VOL_RATIO",row.get("VR",1)),1); rsi=safe_float(row.get("RSI14",row.get("RSI",50)),50)
    dist20=(current/ma20-1)*100 if ma20 else 0; rs20=ret20-benchmark_ret20; accel=ret5-ret20/4
    early_price=92 if -1<=dist20<=3 else 82 if dist20<=5 else 65 if dist20<8 else 35
    early_rsi=92 if 48<=rsi<=62 else 84 if 43<=rsi<68 else 68 if rsi<72 else 35
    flow=92 if 1.10<=vr<=1.70 else 82 if 1.0<=vr<1.10 else 76 if 0.9<=vr<1.0 else 58 if vr<2.2 else 38
    accel_score=90 if 0.5<=accel<=5 else 78 if 0<=accel<0.5 else 68 if accel>5 else 52
    rel=88 if rs20>=6 else 80 if rs20>=3 else 70 if rs20>=0 else 48
    structure=90 if current>=ma60 and ma20>=ma60 else 78 if current>=ma60 else 55 if current>=ma20 else 35
    score=round(early_price*.22+early_rsi*.18+flow*.22+accel_score*.16+rel*.14+structure*.08)
    early_buy=score>=72 and vr>=1.05 and rsi<70 and dist20<7 and rs20>=-1
    return {"score":int(np.clip(score,0,100)),"early_buy":bool(early_buy),"rs20":rs20,"dist20":dist20,"rsi":rsi,"vr":vr,"accel":accel}


def theme_score(theme_rows, bench_ret20=0, bench_ret60=0):
    if len(theme_rows)<2: return None
    vals=[]
    for r in theme_rows:
        r20=safe_float(r.get("ret20",r.get("R20")),np.nan); r60=safe_float(r.get("ret60",r.get("R60")),np.nan)
        if pd.isna(r20) or pd.isna(r60): continue
        sig=leading_signal(r,bench_ret20)
        vals.append({"r20":r20,"r60":r60,"rs20":sig["rs20"],"rs60":r60-bench_ret60,"vr":safe_float(r.get("vr",r.get("VR",1)),1),"ma60gap":safe_float(r.get("ma60_gap",0),0),"accel":sig["accel"],"rsi":sig["rsi"],"lead":sig["score"],"early":sig["early_buy"]})
    if len(vals)<1: return None
    x=pd.DataFrame(vals)
    def clip_score(v,lo,hi): return float(np.clip((v-lo)/(hi-lo)*100,0,100))
    r20=clip_score(x["r20"].mean(),-10,15); r60=clip_score(x["r60"].mean(),-15,30); rs20=clip_score(x["rs20"].mean(),-10,12); rs60=clip_score(x["rs60"].mean(),-15,20)
    vr=clip_score(x["vr"].mean(),.8,2); breadth=float((x["r20"]>-2).mean()*100); ma60=clip_score(x["ma60gap"].mean(),-10,15); accel=clip_score(x["accel"].mean(),-5,6)
    rsi=float(np.clip(100-abs(float(x["rsi"].mean())-58)*2.5,0,100))
    score=r20*.15+r60*.15+rs20*.15+rs60*.10+vr*.15+breadth*.15+ma60*.05+accel*.05+rsi*.05
    lead_theme=float(x["lead"].mean())*.55+breadth*.25+float(x["early"].mean())*100*.20
    heat=(12 if float(x["rsi"].mean())>=75 else 0)+(10 if float(x["r20"].mean())>=12 else 0)+(8 if float(x["ma60gap"].mean())>=15 else 0)
    return float(np.clip((score*.70+lead_theme*.30)-heat,0,100))


def validated_price_zone(row):
    c=safe_float(row.get("Close")); ma20=safe_float(row.get("MA20"),c); ma60=safe_float(row.get("MA60"),c); low20=safe_float(row.get("LOW20"),c)
    support=max(low20,ma20*.985); ideal_top=ma20*1.025; invalid=min(ma60*.97,support*.97)
    if c<=ideal_top and c>=invalid and c>=ma60*.98: state="매수구간"
    elif c<invalid: state="무효"
    elif c>ma20*1.07: state="추격금지"
    else: state="눌림대기"
    return {"state":state,"support":support,"ideal_top":ideal_top,"invalid":invalid}


def validated_cd_signal(row,tscore,benchmark_ret20=0):
    lead=leading_signal(row,benchmark_ret20); zone=validated_price_zone(row); c_pass=safe_float(tscore)>=60 and lead["early_buy"]; d_pass=c_pass and zone["state"]=="매수구간"
    if d_pass: state="D · 매수구간"
    elif c_pass and zone["state"]=="눌림대기": state="C · 눌림대기"
    elif c_pass and zone["state"]=="추격금지": state="C · 추격금지"
    elif c_pass: state="C · 관심"
    elif safe_float(tscore)>=60: state="테마 통과 · 선행 미통과"
    else: state="C 미통과"
    return {**lead,**zone,"theme_score":safe_float(tscore),"c_pass":c_pass,"d_pass":d_pass,"state":state}


def long_term_horizon(d):
    """V4 장기판정.

    V4 원칙
    1) 장기적합성은 미래수익률 예측점수가 아니라 계속 보유할 만한 구조인지 판단.
    2) 최근 252일의 장기추세 지속성을 가장 크게 반영.
    3) 현재 장기추세와 구조적 훼손은 장기적합성과 별도 축으로 판단.
    4) 장기 적합성 재검토는 매도 신호가 아니며, 구조적 훼손일 때만 신규매수를 중단.
    """
    if d.empty or len(d) < 252:
        return {
            "suitability":"데이터 부족", "trend":"확인 불가", "score":0,
            "structural_break":False,
            "reason":"장기 구조를 판단할 252일 데이터가 부족합니다."
        }

    r=d.iloc[-1]
    close=safe_float(r["Close"])
    ma120=safe_float(r["MA120"],close)
    ma200=safe_float(r["MA200"],close)
    ma200_60=safe_float(d["MA200"].iloc[-61],ma200) if len(d)>=61 else ma200
    ma120_60=safe_float(d["MA120"].iloc[-61],ma120) if len(d)>=61 else ma120
    r120=safe_float(r.get("RET120"),0)
    r252=safe_float(r.get("RET250"),0)

    # 최근 252일 동안 장기 이동평균 위에서 머문 비율
    w=d.iloc[-252:]
    above200=float((w["Close"] >= w["MA200"]).mean())*100
    above120=float((w["Close"] >= w["MA120"]).mean())*100
    ma200_up=ma200 > ma200_60
    ma120_up=ma120 > ma120_60

    # V4 장기적합성: 지속성 중심
    suitability=(
        above200*0.40
        + above120*0.20
        + (25 if ma200_up else 0)
        + (15 if r252 > 0 else 7 if r252 > -15 else 0)
    )
    suitability=float(np.clip(suitability,0,100))

    if suitability >= 78:
        fit_state="🟢 장기 핵심보유"
    elif suitability >= 62:
        fit_state="🟢 장기 보유"
    elif suitability >= 48:
        fit_state="🟡 장기 보유 + 추세 확인"
    else:
        fit_state="🔴 장기 적합성 재검토"

    # V4 장기추세: 현재 가격보다 장기 추세 방향을 우선
    trend_score=0
    trend_score += 30 if ma200_up else 0
    trend_score += 25 if ma120_up else 0
    trend_score += 20 if ma120 > ma200 else 0
    trend_score += 15 if r120 > 0 else 0
    trend_score += 10 if close > ma200 else 0

    if trend_score >= 75:
        trend_state="🟢 장기 상승추세"
    elif trend_score >= 50:
        trend_state="🟡 장기 조정/추세 확인"
    else:
        trend_state="🔴 장기 하락추세"

    # 단순 MA200 하회는 구조적 훼손으로 보지 않음.
    # 장기 지속성 자체가 동시에 무너진 경우에만 신규매수 중단 신호.
    structural_break=(
        above200 < 45 and above120 < 50 and
        r252 < 0 and r120 < 0 and
        not ma200_up and not ma120_up and
        ma120 < ma200 and close < ma200
    )

    reason=(
        f"장기적합성 {suitability:.0f}/100 · 최근 252일 200일선 위 {above200:.0f}% · "
        f"120일선 위 {above120:.0f}% · 120일 {r120:+.1f}% · 250일 {r252:+.1f}% · "
        f"장기추세 {trend_score}/100"
    )
    if structural_break:
        reason += " · 구조적 훼손 확인"
    else:
        reason += " · 구조적 훼손 아님"

    return {
        "suitability":fit_state,
        "trend":trend_state,
        "score":int(round(suitability)),
        "trend_score":int(trend_score),
        "structural_break":bool(structural_break),
        "reason":reason,
    }


def _find_theme_for_etf(code):
    # 내 주식 첫 진입 시 전체 미래테마 엔진을 다시 돌리지 않습니다.
    # 이미 생성된 캐시가 있으면 그대로 사용하고, 없으면 현재 주식와 직접
    # 연관된 테마만 빠르게 계산하여 초기 로딩 지연을 줄입니다.
    code=str(code).zfill(6)
    try:
        cached=st.session_state.get("future_engine_cache")
        if cached:
            for theme,info in cached.get("data",{}).get("details",{}).items():
                rows=info.get("rows",[])
                if any(str(x.get("code")).zfill(6)==code for x in rows):
                    return theme,rows

        name=get_stock_name(code)
        matched_themes=[]
        for theme,keywords in THEME_LEXICON.items():
            hits=_theme_match(name,keywords)
            if hits:
                matched_themes.append((hits,theme,keywords))
        if not matched_themes:
            return None,[]
        matched_themes.sort(reverse=True)
        _,theme,keywords=matched_themes[0]
        universe=st.session_state.get("stock_universe",{})
        if not universe:
            universe=load_stock_universe(); st.session_state.stock_universe=universe
        candidates=[]
        for c,n in universe.items():
            h=_theme_match(n,keywords)
            if h:
                candidates.append((h,_normalize_stock_code(c),safe_stock_name(c,n)))
        candidates.sort(key=lambda x:(x[0],x[2]),reverse=True)
        rows=[]
        benchmark=_benchmark_snapshot()
        for _,c,n in candidates[:5]:
            df=load_price_data(c)
            if df.empty: continue
            d=calculate_indicators(df)
            if len(d)<65: continue
            r=d.iloc[-1]; close=d["Close"]
            ret20=safe_float(r.get("RET20")); ret60=safe_float(close.pct_change(60).iloc[-1]*100)
            ma20=safe_float(r.get("MA20"),safe_float(r.get("Close"))); ma60=safe_float(r.get("MA60"),safe_float(r.get("Close")))
            current=safe_float(r.get("Close")); ret5=safe_float(r.get("RET5")); vr=safe_float(r.get("VOL_RATIO"),1); rsi=safe_float(r.get("RSI14"),50)
            accel=ret5-(ret20/4 if np.isfinite(ret20) else 0)
            prev=d.iloc[-21] if len(d)>=86 else None
            if prev is not None:
                prev_close=safe_float(prev.get("Close"),0); prev_ma20=safe_float(prev.get("MA20"),prev_close)
                prev_ret20=safe_float(prev.get("RET20"),0); prev_ret5=safe_float(prev.get("RET5"),0)
                prev_breadth=100.0 if prev_close>=prev_ma20 else 0.0
                prev_accel=prev_ret5-(prev_ret20/4 if np.isfinite(prev_ret20) else 0)
                prev_rs20=prev_ret20-safe_float(benchmark.get("ret20"),0)
            else:
                prev_ret20=ret20; prev_breadth=100.0 if current>=ma20 else 0.0; prev_accel=accel; prev_rs20=ret20-safe_float(benchmark.get("ret20"),0)
            rows.append({"code":c,"name":n,"price":current,"rsi":rsi,"vr":vr,"ret20":ret20,"ret60":ret60,"ret5":ret5,"trend":"상승" if current>=ma20 else "조정","ma60_gap":((current/ma60-1)*100 if ma60 else 0),"breadth":(100.0 if current>=ma20 else 0.0),"accel":accel,"rs20":ret20-safe_float(benchmark.get("ret20"),0),"ret20_prev":prev_ret20,"breadth_prev":prev_breadth,"accel_prev":prev_accel,"rs20_prev":prev_rs20})
        return (theme,rows) if rows else (None,[])
    except Exception:
        return None,[]



def integrated_decision_engine(d, code):
    """미래테마→선행→가격→보유→매도 통합 상태 엔진. 현재 데이터만 사용."""
    if d is None or d.empty or len(d) < 252:
        return {"state":"데이터 부족","action":"관찰","theme_score":0,"lead_score":0,"price_score":0,"hold_score":0,"exit_score":0}
    bench=_benchmark_snapshot()
    theme, rows=_find_theme_for_etf(code)
    tscore=theme_score(rows,bench.get("ret20",0),bench.get("ret60",0)) if rows else 0.0
    lifecycle=_theme_lifecycle(rows,bench) if rows else {"score":0.0,"state":"관찰"}
    r=d.iloc[-1]; current=safe_float(r.get("Close"),0)
    ma20=safe_float(r.get("MA20"),current); ma60=safe_float(r.get("MA60"),current); ma120=safe_float(r.get("MA120"),current)
    r5=safe_float(r.get("RET5"),0); r20=safe_float(r.get("RET20"),0); r60=safe_float(r.get("RET60"),0); rsi=safe_float(r.get("RSI14"),50); vr=safe_float(r.get("VOL_RATIO"),1)
    rs20=r20-safe_float(bench.get("ret20"),0)
    ts=float(np.clip(tscore or 0,0,100)); theme_state="주도" if ts>=78 else "상승확산" if ts>=64 else "초기확대" if ts>=50 else "관찰" if ts>0 else "미분류"
    lead=leading_signal(r,safe_float(bench.get("ret20"),0)); lead_score=float(lead["score"])
    zone=validated_price_zone(r); price_score={"매수구간":92,"눌림대기":70,"추격금지":25,"무효":10}.get(zone["state"],10)
    long=long_term_horizon(d); hold_score=float(long.get("score",0)); structural=bool(long.get("structural_break",False))
    mid_score=(25 if current>ma60 else 0)+(20 if ma20>ma60 else 0)+(20 if ma60>ma120 else 0)+(20 if r60>0 else 0)+(15 if rs20>0 else 0)
    mid_state="중기 상승" if mid_score>=75 else "중기 확인" if mid_score>=55 else "중기 약세"
    dist20=(current/ma20-1)*100 if ma20 else 0
    overheat=radar_overheat_score({"rsi":rsi,"ret5":r5,"dist20":dist20,"vr":vr})
    theme_fading=ts<50 or lifecycle.get("state")=="쇠퇴"; lead_fading=lead_score<55 and rs20<0; trend_break=current<ma60 and ma20<ma60 and r60<0
    if structural: exit_score,exit_state=95,"구조적 훼손"
    elif theme_fading and lead_fading: exit_score,exit_state=88,"테마·선행 동시 약화"
    elif trend_break and lead_fading: exit_score,exit_state=78,"중기 추세 이탈"
    elif overheat>=65: exit_score,exit_state=62,"과열·분할익절"
    elif overheat>=45: exit_score,exit_state=40,"과열 주의"
    else: exit_score,exit_state=15,"정상"
    if structural: state,action="EXIT / REASSESS","🔴 구조적 훼손 · 신규매수 중단 · 보유비중 재검토"
    elif theme_fading and lead_fading: state,action="REDUCE","🔴 테마와 선행성 동시 약화 · 신규매수 중단 · 비중축소 검토"
    elif trend_break and lead_fading: state,action="REDUCE","🟠 중기 추세 이탈 · 신규매수 중단 · 반등 확인"
    elif overheat>=65: state,action="TRIM","🟡 과열구간 · 신규추격 금지 · 분할익절/추적관리"
    elif ts>=64 and lifecycle.get("state") not in {"쇠퇴","과열"} and lead_score>=72 and price_score>=85: state,action="BUY","🟢 미래테마 + 선행 주식 + 매수가격 일치 · 분할매수 후보"
    elif ts>=64 and lead_score>=72: state,action="WATCH_BUY","🟢 미래테마·선행성 양호 · 가격 확인 후 접근"
    elif hold_score>=78 and mid_score>=55: state,action="HOLD","🟢 장기 핵심보유 유지 · 중기 추세 관리"
    elif hold_score>=62: state,action="HOLD_WATCH","🟡 장기보유 가능 · 중기 추세 확인"
    else: state,action="WATCH","⚪ 관찰 · 방향 확인 전 신규매수 보류"
    return {"state":state,"action":action,"theme":theme or "미분류","theme_score":round(ts,1),"theme_state":theme_state,"lifecycle_score":float(lifecycle.get("score",0)),"lifecycle_state":lifecycle.get("state","관찰"),"lead_score":round(lead_score,1),"price_score":round(price_score,1),"hold_score":round(hold_score,1),"mid_score":int(mid_score),"mid_state":mid_state,"exit_score":int(exit_score),"exit_state":exit_state,"overheat":int(overheat),"price_zone":zone["state"],"theme_fading":theme_fading,"lead_fading":lead_fading,"structural_break":structural}

def horizon_engine(d,code):
    long=long_term_horizon(d)
    if d.empty: return {"long":long,"operation":"확인 불가","cd":None,"final":"확인 불가"}
    bench=_benchmark_snapshot(); theme,rows=_find_theme_for_etf(code); tscore=theme_score(rows,bench.get("ret20",0),bench.get("ret60",0)) if rows else None
    cd=validated_cd_signal(d.iloc[-1],tscore,bench.get("ret20",0)) if tscore is not None else None
    title=get_judgment(d)["title"]
    operation={"상승 추세 · 추격 주의":"🔥 단기 강세 · 추격 주의","상승 추세 유지":"🟢 보유·운용","단기 조정 · 중기 추세 확인":"🟡 눌림·추세 확인","중기 약세 · 방어 우선":"🔴 방어 우선"}.get(title,"⚪ 매수대기·방향 확인")
    integrated=integrated_decision_engine(d,code)
    return {"long":long,"operation":operation,"cd":cd,"theme":theme,"final":cd["state"] if cd else "C/D 산출 대기","integrated":integrated}


def _forward_reach_rate(d, target_ratio, horizon_days):
    """과거 시점에서 현재 목표수익률(target_ratio)을 향후 도달한 비율.
    각 과거 시점에서는 그 시점 이후 데이터만 사용하므로 미래누수가 없습니다.
    """
    try:
        close=d["Close"].astype(float).values
        high=d["High"].astype(float).values
        n=len(close)
        if n < horizon_days + 30 or target_ratio <= 1:
            return np.nan
        hits=[]
        for i in range(20, n-horizon_days):
            if not np.isfinite(close[i]) or close[i] <= 0:
                continue
            future=np.nanmax(high[i+1:i+1+horizon_days])
            hits.append(1.0 if np.isfinite(future) and future/close[i] >= target_ratio else 0.0)
        return float(np.mean(hits)) if hits else np.nan
    except Exception:
        return np.nan


def _forward_score_text(rate):
    if not np.isfinite(rate):
        return "과거 표본 부족"
    if rate >= .70:
        return f"도달 가능성 높음 · 과거 {rate*100:.0f}%"
    if rate >= .55:
        return f"도달 가능성 보통 이상 · 과거 {rate*100:.0f}%"
    if rate >= .40:
        return f"도달 가능성 보통 · 과거 {rate*100:.0f}%"
    return f"도달 가능성 낮음 · 과거 {rate*100:.0f}%"


def trade_levels(d, held=False, avg_price=0.0, horizon="중기"):
    """투자기간별 실제 운용 가격.

    핵심 원칙:
    1) 손절은 고정 %가 아니라 구조적 무효선과 ATR 정상변동폭을 결합합니다.
    2) 익절은 R 배수 하나로 정하지 않고 실제 저항 + 과거 Forward 도달률을 함께 봅니다.
    3) 장기는 전고점을 돌파하면 고정 2차 익절을 두지 않고 추세추적합니다.
    """
    if d.empty:
        return None
    c=safe_float(d["Close"].iloc[-1],0)
    if c<=0:
        return None
    ma20=safe_float(d["MA20"].iloc[-1],c)
    ma60=safe_float(d["MA60"].iloc[-1],c)
    low20=safe_float(d["LOW20"].iloc[-1],c)
    low60=safe_float(d["LOW60"].iloc[-1],c)

    prior20=float(d["High"].rolling(20).max().shift(1).iloc[-1]) if len(d)>=21 else np.nan
    prior60=float(d["High"].rolling(60).max().shift(1).iloc[-1]) if len(d)>=61 else np.nan
    prior120=float(d["High"].rolling(120).max().shift(1).iloc[-1]) if len(d)>=121 else np.nan
    prior252=float(d["High"].rolling(252).max().shift(1).iloc[-1]) if len(d)>=253 else np.nan
    prior20=prior20 if np.isfinite(prior20) and prior20>c else np.nan
    prior60=prior60 if np.isfinite(prior60) and prior60>c else np.nan
    prior120=prior120 if np.isfinite(prior120) and prior120>c else np.nan
    prior252=prior252 if np.isfinite(prior252) and prior252>c else np.nan

    tr=pd.concat([(d["High"]-d["Low"]).abs(),
                  (d["High"]-d["Close"].shift(1)).abs(),
                  (d["Low"]-d["Close"].shift(1)).abs()],axis=1).max(axis=1)
    atr14=safe_float(tr.rolling(14).mean().iloc[-1],c*.02)
    ref=avg_price if held and avg_price>0 else c
    atr_pct=float(np.clip(atr14/ref,0.005,0.20))

    if horizon=="단기":
        horizon_days=20; atr_mult=1.6; max_loss=0.09
        structural=max(low20*0.985,ma20*0.985)
        trail="20일선과 최근 스윙저점 중 더 강한 방어선 추적"
    elif horizon=="중기":
        horizon_days=40; atr_mult=2.2; max_loss=0.12
        structural=max(low60*0.985,ma60*0.985)
        trail="20일선 → 60일선 순으로 추세 훼손 여부 추적"
    else:
        horizon_days=60; atr_mult=2.8; max_loss=0.15
        structural=max(low60*0.98,ma60*0.98)
        trail="전고점 돌파 후 60일선·최근 저점 추적"

    # 정상 변동폭보다 좁은 손절을 피하되, 구조선이 지나치게 멀면 최대손실 한도에서 제한.
    volatility_floor=max(atr14*atr_mult, ref*atr_pct*atr_mult)
    if held and avg_price>0:
        entry=avg_price
        gain=c/entry-1 if entry>0 else 0
        adaptive_cap=min(max_loss, max(0.07, atr_pct*4.0))
        # 수익권에서는 본전/수익 보호를 우선하되 하루 변동폭보다 좁아지지 않게 함.
        if gain>0:
            protect=max(entry, c-volatility_floor)
            stop=max(structural, protect)
        else:
            stop=max(structural, entry-volatility_floor)
        hard_floor=entry*(1-adaptive_cap)
        stop=max(stop,hard_floor)
        stop=min(stop,entry*0.995)
        mode="보유중"
    else:
        entry=max(ma20*1.01,c*0.99)
        mode="미보유"
        stop=max(structural,entry-volatility_floor)
        adaptive_cap=min(max_loss,max(0.07,atr_pct*4.0))
        stop=max(stop,entry*(1-adaptive_cap))
        stop=min(stop,entry*0.995)

    support=max(low20*0.995,ma20*0.995)

    def resistance_candidates():
        vals=[]
        for x,label in [(prior20,"20일 저항"),(prior60,"60일 저항"),(prior120,"120일 저항"),(prior252,"52주 전고점")]:
            if np.isfinite(x) and x>c*1.01:
                vals.append((x,label))
        return sorted(vals,key=lambda z:z[0])

    cands=resistance_candidates()
    tp1=None; tp2=None; tp1_label=""; tp2_label=""
    # 현재 추천기간의 미래도달 가능성을 계산해 가장 현실적인 저항을 선택.
    scored=[]
    for price,label in cands:
        ratio=price/c
        rate=_forward_reach_rate(d,ratio,horizon_days)
        scored.append((price,label,rate))
    viable=[x for x in scored if np.isfinite(x[2]) and x[2]>=0.55]
    if viable:
        tp1,lab,rate=min(viable,key=lambda x:x[0])
        tp1_label=f"{lab} · {_forward_score_text(rate)}"
        later=[x for x in scored if x[0]>tp1*1.01 and (not np.isfinite(x[2]) or x[2]>=0.40)]
        if horizon!="장기" and later:
            tp2,lab2,rate2=min(later,key=lambda x:x[0])
            tp2_label=f"{lab2} · {_forward_score_text(rate2)}"
    else:
        # 실제 저항이 없거나 과거 도달률 표본이 약한 경우 임의의 큰 목표를 만들지 않음.
        # 가장 가까운 저항이 너무 멀면 '목표 재산정'으로 둡니다.
        if cands and cands[0][0] <= c*1.12:
            tp1,lab=cands[0][0],cands[0][1]
            rate=_forward_reach_rate(d,tp1/c,horizon_days)
            tp1_label=f"{lab} · {_forward_score_text(rate)}"
        else:
            tp1=None
            tp1_label="유효한 1차 목표 부족 · 돌파/추세 확인 후 재산정"

    if horizon=="장기":
        breakout=bool(np.isfinite(prior252) and c>prior252)
        if breakout:
            tp1=None
            tp2=None
            tp1_label="52주 전고점 돌파 상태 · 고정 익절 없음"
        tp2_label="고정 2차 익절 없음 · 돌파 후 추세추적"
    elif tp1 is not None and tp2 is None:
        # 2차를 억지로 만들지 않고, 1차 돌파 후 재산정.
        tp2_label="1차 돌파 후 다음 저항을 재산정"

    return {
        "entry":entry,"tp1":tp1,"tp2":tp2,"stop":stop,
        "support":support,"low60":low60,"prior20":prior20,
        "prior60":prior60,"prior252":prior252,"mode":mode,
        "horizon":horizon,"trail":trail,"tp1_label":tp1_label,
        "tp2_label":tp2_label,"max_loss":adaptive_cap if 'adaptive_cap' in locals() else max_loss,
        "atr_pct":atr_pct,"atr14":atr14,"volatility_floor":volatility_floor,
    }

def _recommended_horizon(d, code):
    """현재 주식 상태에서 앱이 우선 추천할 투자기간을 하나만 결정합니다."""
    h=_final_horizon_snapshot(d,code)
    focus=h.get("focus","관찰 중심")
    mapping={
        "장기 중심":("장기","🟢 장기추천","6~12개월"),
        "중기 중심":("중기","🔵 중기추천","1~3개월"),
        "단기 중심":("단기","🟡 단기추천","1~4주"),
    }
    if focus in mapping:
        return mapping[focus],h
    # 관찰 중심일 때도 무작정 세 전략을 동시에 제시하지 않고,
    # 현재 점수가 가장 높은 실질 운용축 하나만 선택합니다.
    scores={
        "장기":safe_float(h.get("long_score"),0),
        "중기":safe_float(h.get("mid_score"),0),
        "단기":safe_float(h.get("lead_score"),0),
    }
    best=max(scores,key=scores.get)
    meta={"장기":("장기","🟢 장기 우선검토","6~12개월"),
          "중기":("중기","🔵 중기 우선검토","1~3개월"),
          "단기":("단기","🟡 단기 우선검토","1~4주")}
    return meta[best],h


def _render_trade_cards(lv, avg_price=0.0, qty=0.0):
    """선택된 투자기간의 목표·방어 가격과 근거를 표시합니다."""
    def pnl(price):
        if price is None or avg_price<=0:
            return ""
        pct=(price/avg_price-1)*100
        amt=(price-avg_price)*qty if qty>0 else None
        return f"{pct:+.1f}%" + (f" · {amt:+,.0f}원" if amt is not None else "")

    tp1=money(lv["tp1"]) if lv.get("tp1") is not None else "재산정"
    tp2=money(lv["tp2"]) if lv.get("tp2") is not None else "고정 2차 없음"
    stop=money(lv["stop"])
    cards=[
        ("🎯 1차 익절",tp1,lv.get("tp1_label","") + ((" · "+pnl(lv.get("tp1"))) if lv.get("tp1") is not None else "")),
        ("🎯 2차 익절",tp2,lv.get("tp2_label","") + ((" · "+pnl(lv.get("tp2"))) if lv.get("tp2") is not None else "")),
        ("🛡️ 방어/손절",stop,("구조 + 변동성 기반" + ((" · "+pnl(lv.get("stop"))) if avg_price>0 else ""))),
    ]
    cols=st.columns(3)
    for col,(title,price,desc) in zip(cols,cards):
        with col:
            with st.container(border=True):
                st.markdown(f'<div class="trade-card-label">{esc(title)}</div><div class="trade-card-price small">{esc(price)}</div><div class="trade-card-desc">{esc(desc)}</div>',unsafe_allow_html=True)
    st.caption(f"운용: {lv['trail']} · ATR14 {lv.get('atr_pct',0)*100:.1f}%")

def render_horizon_strategy(d,code):
    """내 주식의 추천기간 중심 실제 운용전략.

    앱이 현재 상태를 보고 장기/중기/단기 중 하나를 추천하고,
    사용자는 그 추천기간의 매수·익절·손절 기준을 우선 사용합니다.
    다른 기간은 별도 접기에서만 확인할 수 있습니다.
    """
    hmeta,h=_recommended_horizon(d,code)
    rec_horizon,rec_label,rec_period=hmeta
    holding=st.session_state.holdings.get(code) or {}
    held_widget=st.session_state.get(f"held_{code}", "보유중" if holding else "미보유")
    held=held_widget=="보유중"
    avg_price=safe_float(st.session_state.get(f"avg_{code}", holding.get("avg_price",0)),0) if held else 0
    qty=safe_float(st.session_state.get(f"qty_{code}", holding.get("quantity",0)),0) if held else 0

    st.markdown('<div class="strategy-section-title">🎯 실제 매수 · 익절 · 손절 전략</div>',unsafe_allow_html=True)
    st.markdown(
        f'<div class="trade-recommendation-banner"><b>{esc(rec_label)}</b> · 추천기간 {esc(rec_period)}</div>',
        unsafe_allow_html=True
    )

    lv=trade_levels(d,held,avg_price,rec_horizon)
    if not lv:
        st.warning("현재 가격 데이터로 전략을 계산할 수 없습니다.")
        return

    if not held:
        st.caption("현재 미보유 상태입니다. 앱이 추천한 투자기간을 기준으로 매수·무효 가격을 제시합니다.")
        cols=st.columns(3)
        cards=[
            ("🎯 매수금액",money(lv["entry"]),f"{rec_period} 추천 진입"),
            ("🟡 눌림 기준",money(lv["support"]),"핵심 지지 확인"),
            ("🛑 무효금액",money(lv["stop"]),"이탈 시 매수 취소"),
        ]
        for col,(title,price,desc) in zip(cols,cards):
            with col:
                with st.container(border=True):
                    st.markdown(f'<div class="trade-card-label">{esc(title)}</div><div class="trade-card-price">{esc(price)}</div><div class="trade-card-desc">{esc(desc)}</div>',unsafe_allow_html=True)
        return

    st.caption(f"보유중 · 평균매수가 {money(avg_price)} · 보유수량 {qty:,.0f}주")
    _render_trade_cards(lv,avg_price,qty)

    other=[("장기","🟢 장기 · 6~12개월"),("중기","🔵 중기 · 1~3개월"),("단기","🟡 단기 · 1~4주")]
    others=[x for x in other if x[0]!=rec_horizon]
    with st.expander("다른 투자기간 전략 보기",expanded=False):
        for horizon,label in others:
            lv2=trade_levels(d,True,avg_price,horizon)
            if not lv2: continue
            st.markdown(f"**{label}**")
            _render_trade_cards(lv2,avg_price,qty)

# ============================================================
# PRICE LEVELS
# ============================================================

def calculate_levels(d):
    if d.empty:
        return None
    current = safe_float(d["Close"].iloc[-1])
    ma20 = safe_float(d["MA20"].iloc[-1], current)
    ma60 = safe_float(d["MA60"].iloc[-1], current)
    high20 = safe_float(d["HIGH20"].iloc[-1], current)
    low20 = safe_float(d["LOW20"].iloc[-1], current)
    low60 = safe_float(d["LOW60"].iloc[-1], current)

    return {
        "first": ma20,
        "support": min(ma60, low20),
        "breakout": high20,
        "risk": min(ma60, low20, low60)
    }


# ============================================================
# JUDGMENT UI
# ============================================================

def render_judgment(d):
    judgment = get_judgment(d)
    st.markdown('<div class="section-title">현재판단 · 지금대응</div>', unsafe_allow_html=True)

    rsi = judgment["rsi"]
    vr = judgment["vol_ratio"]

    ma_color = "positive" if judgment["ma_state"] == "20일선 상회" else "negative"
    rsi_color = "positive" if rsi >= 60 else ("negative" if rsi < 40 else "neutral")
    vol_color = "positive" if vr >= 1.1 else ("negative" if vr < 0.8 else "neutral")

    st.markdown(
        f"""
        <div class="evidence-grid">
            <div class="evidence-box">
                <div class="evidence-label">20일선</div>
                <div class="evidence-value {ma_color}">{esc(judgment["ma_state"])}</div>
                <div class="evidence-sub">단기 추세</div>
            </div>
            <div class="evidence-box">
                <div class="evidence-label">RSI14</div>
                <div class="evidence-value {rsi_color}">{rsi:.1f}</div>
                <div class="evidence-sub">{esc(judgment["rsi_state"])}</div>
            </div>
            <div class="evidence-box">
                <div class="evidence-label">거래량</div>
                <div class="evidence-value {vol_color}">{vr:.2f}배</div>
                <div class="evidence-sub">{esc(judgment["vol_state"])}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)
    with c1:
        reasons_html = "<br>".join(esc(x) for x in judgment["reasons"])
        st.markdown(
            f"""
            <div class="judgment-box">
                <div class="judgment-title">현재판단</div>
                <div class="judgment-main">{esc(judgment["title"])}</div>
                <div class="reason-label">판단근거</div>
                <div class="judgment-reason">{reasons_html}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="action-box">
                <div class="action-title">지금대응</div>
                <div class="action-main">{esc(judgment["action"])}</div>
                <div class="action-reason-label">대응근거</div>
                <div class="judgment-reason">현재 추세·RSI·거래량을 기준으로 신규 매수는 추격보다 눌림 또는 확인 후 대응하도록 설정했습니다.</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# SCENARIOS
# ============================================================

def render_scenarios(d):
    levels = calculate_levels(d)
    if not levels:
        return

    current = safe_float(d["Close"].iloc[-1])
    ma20 = safe_float(d["MA20"].iloc[-1], current)
    ma60 = safe_float(d["MA60"].iloc[-1], current)
    high20 = safe_float(d["HIGH20"].iloc[-1], current)
    low20 = safe_float(d["LOW20"].iloc[-1], current)
    rsi = safe_float(d["RSI14"].iloc[-1], 50)
    vol_ratio = safe_float(d["VOL_RATIO"].iloc[-1], 1.0)

    st.markdown("### 핵심가격 · 대응 시나리오")
    st.caption("현재가를 기준으로 눌림 · 지지 · 돌파 · 위험 구간을 나누고, 각 가격에서 확인할 조건과 대응 방법을 제시합니다.")

    # --------------------------------------------------------
    # 1. 핵심 가격 4단계
    # HTML을 사용하지 않고 Streamlit 기본 컴포넌트만 사용합니다.
    # --------------------------------------------------------
    cards = [
        {
            "label": "① 1차 관심",
            "price": levels["first"],
            "condition": "20일선 부근 눌림",
            "meaning": "단기 상승 추세가 유지되는지 확인하는 첫 번째 가격대입니다.",
            "action": "급락 중 바로 매수하지 말고 가격이 20일선에서 멈추는지 확인합니다."
        },
        {
            "label": "② 핵심 지지",
            "price": levels["support"],
            "condition": "중기 추세 방어",
            "meaning": "최근 저점과 중기 이동평균을 기준으로 추세의 방어력을 확인합니다.",
            "action": "지지 + 거래량 안정이 확인될 때 분할 대응을 검토합니다."
        },
        {
            "label": "③ 돌파 기준",
            "price": levels["breakout"],
            "condition": "최근 20일 고점 돌파",
            "meaning": "최근 매물 부담을 넘어 새로운 단기 고점을 만드는 기준입니다.",
            "action": "가격만 돌파하지 말고 거래량 증가가 동반되는지 확인합니다."
        },
        {
            "label": "④ 위험 가격",
            "price": levels["risk"],
            "condition": "핵심 지지 이탈",
            "meaning": "중기 추세가 약해질 수 있어 신규 진입보다 방어가 우선되는 가격대입니다.",
            "action": "지지 회복 전까지 신규 매수는 보수적으로 접근합니다."
        }
    ]

    cols = st.columns(4)
    for col, card in zip(cols, cards):
        with col:
            with st.container(border=True):
                st.markdown(f"**{card['label']}**")
                st.markdown(f"### {money(card['price'])}")
                st.caption(card["condition"])
                st.markdown(f"**의미**  \n{card['meaning']}")
                st.markdown(f"**대응**  \n{card['action']}")

    st.divider()

    # --------------------------------------------------------
    # 2. 현재가 위치 판정
    # --------------------------------------------------------
    if current < levels["risk"]:
        state = "핵심 지지 하회"
        state_desc = "현재가는 위험 가격 아래에 있습니다. 지금은 신규 진입보다 지지 회복 여부를 먼저 확인하는 구간입니다."
        action = "신규매수 보류 · 지지 회복 확인"
        trigger = f"{money(levels['risk'])} 회복 여부"
    elif current <= levels["support"] * 1.015:
        state = "핵심 지지 접근"
        state_desc = "핵심 지지구간에 접근했습니다. 가격이 지지를 지키고 거래량이 안정되는지가 중요합니다."
        action = "분할매수 검토 · 지지 확인"
        trigger = f"{money(levels['support'])} 지지 + 거래량 안정"
    elif current < levels["first"] * 1.015:
        state = "1차 관심구간"
        state_desc = "20일선 부근에서 눌림을 확인할 수 있는 구간입니다. 급등 추격보다 지지 확인이 유리합니다."
        action = "눌림매수 검토 · 추격 자제"
        trigger = f"20일선 {money(ma20)} 지지 확인"
    elif current >= levels["breakout"]:
        state = "돌파구간"
        state_desc = "최근 20일 고점 기준을 넘어선 상태입니다. 거래량이 동반되면 돌파의 신뢰도를 높일 수 있습니다."
        action = "돌파 확인 · 거래량 체크"
        trigger = f"거래량 {vol_ratio:.2f}배 이상 여부"
    else:
        state = "추세 유지구간"
        state_desc = "현재가는 주요 지지와 돌파 기준 사이에 있습니다. 방향이 확정되기 전에는 추격보다 눌림을 기다리는 전략이 적합합니다."
        action = "보유 관찰 · 눌림 대기"
        trigger = f"20일선 {money(ma20)} / 고점 {money(high20)}"

    # --------------------------------------------------------
    # 3. 현재 대응 + 판단 근거
    # --------------------------------------------------------
    st.markdown("#### 지금은 어떻게 대응할까?")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("현재가", money(current))
        st.markdown(f"**현재 위치**  \n{state}")
        st.markdown(f"**권장 대응**  \n{action}")
    with c2:
        st.info(state_desc)
        st.markdown(f"**핵심 확인조건:** {trigger}")

        evidence = []
        evidence.append(f"20일선 {money(ma20)} · {'상회' if current >= ma20 else '하회'}")
        evidence.append(f"60일선 {money(ma60)} · {'상회' if current >= ma60 else '하회'}")
        evidence.append(f"RSI14 {rsi:.1f} · {'과열권' if rsi >= 70 else ('약세권' if rsi <= 40 else '중립권')}")
        evidence.append(f"거래량 {vol_ratio:.2f}배 · {'증가' if vol_ratio >= 1.1 else ('감소' if vol_ratio < 0.8 else '평균권')}")
        st.caption(" · ".join(evidence))

    # --------------------------------------------------------
    # 4. 매매 시나리오를 한 줄로 정리
    # --------------------------------------------------------
    st.markdown("#### 가격대별 행동 기준")
    scenario_cols = st.columns(3)
    with scenario_cols[0]:
        st.markdown("**눌림 시나리오**")
        st.write(f"20일선 {money(ma20)} 부근까지 조정 → 지지 확인 → 거래량 안정 시 분할 접근")
    with scenario_cols[1]:
        st.markdown("**돌파 시나리오**")
        st.write(f"최근 고점 {money(high20)} 돌파 → 거래량 증가 확인 → 돌파 유지 여부 확인")
    with scenario_cols[2]:
        st.markdown("**이탈 시나리오**")
        st.write(f"위험 가격 {money(levels['risk'])} 이탈 → 신규매수 보류 → 지지 회복 여부 재확인")


# ============================================================
# CHART
# ============================================================

def render_chart(d):
    if d.empty:
        st.warning("차트 데이터를 확인하지 못했습니다.")
        return

    chart_df = d.tail(126).copy()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.025, row_heights=[0.75, 0.25])

    fig.add_trace(
        go.Candlestick(
            x=chart_df.index,
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            increasing_line_color="#39c99a",
            increasing_fillcolor="#39c99a",
            decreasing_line_color="#ef6678",
            decreasing_fillcolor="#ef6678",
            name="가격",
            showlegend=False
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(x=chart_df.index, y=chart_df["MA20"], mode="lines", line=dict(color="#4f86b5", width=1.4), name="20일선"),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(x=chart_df.index, y=chart_df["MA60"], mode="lines", line=dict(color="#a58c52", width=1.3), name="60일선"),
        row=1, col=1
    )

    if "MA200" in chart_df.columns:
        fig.add_trace(
            go.Scatter(x=chart_df.index, y=chart_df["MA200"], mode="lines", line=dict(color="#7b6fa8", width=1.1), name="200일선"),
            row=1, col=1
        )

    volume_colors = np.where(chart_df["Close"] >= chart_df["Open"], "#327f69", "#9b4653")

    fig.add_trace(
        go.Bar(x=chart_df.index, y=chart_df["Volume"], marker_color=volume_colors, opacity=0.5, name="거래량", showlegend=False),
        row=2, col=1
    )

    fig.update_xaxes(fixedrange=True, showgrid=False, rangeslider_visible=False)
    fig.update_yaxes(fixedrange=True, gridcolor="#17283a", tickfont=dict(color="#73879b", size=9), row=1, col=1)
    fig.update_yaxes(fixedrange=True, showticklabels=False, showgrid=False, row=2, col=1)

    fig.update_layout(
        height=390,
        margin=dict(l=4, r=4, t=18, b=4),
        paper_bgcolor="#0d1928",
        plot_bgcolor="#0d1928",
        font=dict(color="#aab8c7"),
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right", font=dict(size=9, color="#8ea0b3")),
        dragmode=False,
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False, "scrollZoom": False, "doubleClick": False, "responsive": True, "staticPlot": True}
    )


# ============================================================
# SEARCH
# ============================================================

def lookup_live_stock(code):
    """신규/누락 주식은 KRX → Naver → Yahoo 순으로 이름을 확인합니다."""
    code = _normalize_stock_code(code)
    if not code:
        return ""

    for source in (fetch_krx_stock_master(), fetch_naver_stock_master()):
        name = source.get(code)
        if name and not name.startswith("주식 "):
            st.session_state.stock_universe[code] = name
            return name

    # 종목마스터 전체 조회가 일시 실패해도 개별 종목 페이지에서는 이름을 복구합니다.
    try:
        url=f"https://finance.naver.com/item/main.naver?code={code}"
        r=requests.get(url,headers={"User-Agent":"Mozilla/5.0","Referer":"https://finance.naver.com/"},timeout=10)
        r.raise_for_status()
        text=r.content.decode("euc-kr",errors="ignore")
        m=re.search(r"<title>\s*(.*?)\s*:\s*네이버 금융\s*</title>",text,re.S)
        if m:
            name=re.sub(r"<[^>]+>","",html.unescape(m.group(1))).strip()
            name=safe_stock_name(code,name)
            if name and not name.startswith("주식 "):
                st.session_state.stock_universe[code]=name
                return name
    except Exception:
        pass

    try:
        info = yf.Ticker(f"{code}.KS").info
        name = info.get("shortName") or info.get("longName") or ""
        name = safe_stock_name(code, name)
        if name and not name.startswith("주식 "):
            st.session_state.stock_universe[code] = name
            return name
    except Exception:
        pass

    return f"주식 {code}"


def lookup_yahoo_stock_name(code):
    # 기존 함수명 호환. 실제 조회는 KRX/Naver를 먼저 사용합니다.
    return lookup_live_stock(code)


def search_stocks(query):
    # 검색 결과는 항상 내부 코드 + 안전하게 정제된 종목명으로 구성합니다.
    # 특히 최신 주식은 캐시 파일에 아직 없어도 '종목코드 직접 검색'으로 찾을 수 있어야 합니다.
    query_raw = (query or "").strip()
    query = query_raw.lower()
    if not query:
        return []

    results = []
    seen = set()

    # 1) 기존 주식 universe 검색
    for raw_code, raw_name in st.session_state.stock_universe.items():
        code = str(raw_code).strip().upper()
        # 숫자 코드는 6자리로 정규화하고, 신규 영문+숫자 코드는 그대로 유지합니다.
        if code.isdigit():
            code = code.zfill(6)
        name = get_stock_name(code)
        if code in seen:
            continue

        search_name = str(name).strip().lower()
        if query in code.lower() or query in search_name:
            results.append({"code": code, "name": name})
            seen.add(code)

    # 2) universe에 아직 없는 신규 주식도 정확한 종목코드로 직접 검색
    # 예: 490490, 0173Y0
    compact = query_raw.replace(".", "").replace("-", "").strip().upper()
    if re.fullmatch(r"[0-9A-Z]{6}", compact):
        code = compact
        if code not in seen:
            name = lookup_yahoo_stock_name(code)
            results.insert(0, {"code": code, "name": name})
            st.session_state.stock_universe[code] = name
            seen.add(code)

    return results[:30]


# ============================================================
# WATCHLIST
# ============================================================

def add_watch(code):
    code = _normalize_stock_code(code)
    if code not in st.session_state.watchlist:
        st.session_state.watchlist.append(code)
        write_json(WATCHLIST_FILE, st.session_state.watchlist)
    st.session_state.selected_code = code


# ============================================================
# STOCK FINDER
# ============================================================

def render_stock_finder():
    st.markdown('<div class="section-title">주식 찾기</div>', unsafe_allow_html=True)
    query = st.text_input("종목명 또는 종목코드", placeholder="예: 삼성전자 / 005930 / 반도체", label_visibility="collapsed", key="search_q")
    results = search_stocks(query)

    if results:
        result_map = {str(x["code"]).zfill(6): x for x in results}
        result_codes = list(result_map.keys())
        selected_code = st.selectbox(
            "검색 결과",
            result_codes,
            format_func=lambda code: f'{get_stock_name(code)} · {code}',
            key="search_result"
        )
        item = result_map[str(selected_code).zfill(6)]

        c1, c2 = st.columns([4, 1])
        with c1:
            st.caption(f'선택: {item["name"]} ({item["code"]})')
        with c2:
            already = item["code"] in st.session_state.watchlist
            if st.button("추가" if not already else "등록됨", disabled=already, use_container_width=True, key=f'add_{item["code"]}'):
                add_watch(item["code"])
                st.rerun()
    elif query:
        st.caption("검색 결과가 없습니다.")


# ============================================================
# WATCHLIST UI
# ============================================================

def render_watchlist():
    st.markdown('<div class="section-title">관심종목</div>', unsafe_allow_html=True)
    watchlist = st.session_state.watchlist
    if not watchlist:
        st.info("관심종목이 없습니다.")
        return

    current = st.session_state.selected_code
    default_index = watchlist.index(current) if current in watchlist else 0

    selected_code = st.selectbox(
        "관심종목 선택",
        watchlist,
        index=default_index,
        format_func=lambda code: f'{get_stock_name(code)} · {code}',
        key="watch_select"
    )
    code = str(selected_code).zfill(6)
    st.session_state.selected_code = code

    if st.button("현재 주식 관심종목에서 삭제", use_container_width=True, key="remove_watch"):
        watchlist.remove(code)
        write_json(WATCHLIST_FILE, watchlist)
        st.session_state.selected_code = watchlist[0] if watchlist else "395160"
        st.rerun()


# ============================================================
# HOLDINGS
# ============================================================

def render_holdings(code, current):
    st.markdown('<div class="section-title">보유 상태</div>', unsafe_allow_html=True)
    old = st.session_state.holdings.get(code)

    held = st.radio("보유 여부", ["미보유", "보유중"], index=1 if old else 0, horizontal=True, key=f"held_{code}")

    if held == "보유중":
        c1, c2 = st.columns(2)
        with c1:
            avg = st.number_input("평균매수가", min_value=0.0, value=float(old.get("avg_price", 0) if old else 0), step=100.0, key=f"avg_{code}")
        with c2:
            qty = st.number_input("보유수량", min_value=0.0, value=float(old.get("quantity", 0) if old else 0), step=1.0, key=f"qty_{code}")

        if st.button("보유정보 저장", key=f"save_{code}", use_container_width=True):
            st.session_state.holdings[code] = {"avg_price": avg, "quantity": qty}
            write_json(HOLDINGS_FILE, st.session_state.holdings)
            st.rerun()

        if avg > 0:
            pnl = (current / avg - 1) * 100
            cls = "positive" if pnl >= 0 else "negative"
            st.markdown(
                f"""
                <div class="holding-box">
                    <div class="holding-value">보유 {qty:,.0f}주</div>
                    <div class="holding-detail">평균매수가 {money(avg)} · 현재 수익률 <span class="{cls}">{pnl:+.2f}%</span></div>
                </div>
                """,
                unsafe_allow_html=True
            )
    elif old:
        if st.button("보유정보 삭제", key=f"del_{code}", use_container_width=True):
            del st.session_state.holdings[code]
            write_json(HOLDINGS_FILE, st.session_state.holdings)
            st.rerun()


# ============================================================
# MY 주식
# ============================================================

def render_my_etf():
    render_stock_finder()
    render_watchlist()

    code = st.session_state.selected_code
    name = get_stock_name(code)
    df = load_price_data(code)

    if df.empty:
        st.error("가격 데이터를 불러오지 못했습니다. 종목코드 또는 인터넷 연결을 확인해 주세요.")
        return

    d = calculate_indicators(df)
    if d.empty:
        st.error("분석 데이터를 만들지 못했습니다.")
        return

    current = safe_float(d["Close"].iloc[-1])
    previous = safe_float(d["Close"].iloc[-2]) if len(d) >= 2 else current
    change = current - previous
    change_pct = change / previous * 100 if previous != 0 else 0
    cls = "positive" if change > 0 else ("negative" if change < 0 else "neutral")
    date_text = d.index[-1].strftime("%Y-%m-%d")

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-name">{esc(name)}</div>
            <div class="hero-code">{esc(code)}</div>
            <div class="quote-row">
                <div class="quote-price">{money(current)}</div>
                <div class="quote-change {cls}">{money(change)} ({change_pct:+.2f}%)</div>
            </div>
            <div class="hero-date">기준일 {esc(date_text)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    render_holdings(code, current)

    # 관심종목의 보유 여부에 따라 실제 매수/익절/손절 전략을 바로 표시합니다.
    # 과거 버전에서 이 호출이 빠지면서 내 주식의 전략 영역이 사라지는 문제가 있었습니다.
    render_horizon_strategy(d, code)

    st.markdown('<div class="section-title">가격 흐름 · 최근 6개월</div>', unsafe_allow_html=True)
    render_chart(d)


# ============================================================
# FUTURE THEME ENGINE
# ============================================================

def _theme_match(name, keywords):
    text = str(name or "").replace(" ", "").lower()
    return sum(1 for k in keywords if str(k).replace(" ", "").lower() in text)


def _theme_lifecycle(rows, benchmark):
    """테마 생애주기 점수. 현재 강도보다 '강해지는 방향'을 별도 평가합니다.

    현재 시점과 20거래일 전의 상대강도·확산도·가속도 변화를 사용하므로
    미래 데이터를 참조하지 않습니다.
    """
    if not rows:
        return {"score":0.0,"state":"관찰","delta_rs":0.0,"delta_breadth":0.0,"delta_accel":0.0}

    def avg(key, default=0.0):
        vals=[safe_float(x.get(key),np.nan) for x in rows]
        vals=[v for v in vals if np.isfinite(v)]
        return float(np.mean(vals)) if vals else default

    rs_now=avg("rs20")
    rs_prev=avg("rs20_prev")
    breadth_now=avg("breadth")
    breadth_prev=avg("breadth_prev", breadth_now)
    accel_now=avg("accel")
    accel_prev=avg("accel_prev", accel_now)
    vr=avg("vr")
    rsi=avg("rsi")

    d_rs=rs_now-rs_prev
    d_breadth=breadth_now-breadth_prev
    d_accel=accel_now-accel_prev

    # 변화량을 0~100으로 정규화
    rs_score=float(np.clip((d_rs+5)/15*100,0,100))
    breadth_score=float(np.clip((d_breadth+10)/40*100,0,100))
    accel_score=float(np.clip((d_accel+2)/8*100,0,100))
    flow_score=100 if 1.05<=vr<=1.8 else 75 if 0.9<=vr<1.05 else 65 if vr>1.8 else 40

    # 과열은 '좋은 테마'와 별개로 생애주기 후반으로 이동시키는 요인
    heat_penalty=0
    if rsi>=75: heat_penalty+=30
    elif rsi>=70: heat_penalty+=15
    if avg("ret20")>=15: heat_penalty+=20
    elif avg("ret20")>=10: heat_penalty+=10

    score=(rs_score*.35+breadth_score*.25+accel_score*.25+flow_score*.15)-heat_penalty
    score=float(np.clip(score,0,100))

    if heat_penalty>=30 or (rsi>=72 and score<55):
        state="과열"
    elif d_rs < -2 and d_breadth < -12 and d_accel < -1:
        state="쇠퇴"
    elif score>=72 and d_rs>=2 and d_breadth>=5:
        state="주도 강화"
    elif score>=55 and (d_rs>0 or d_breadth>0 or d_accel>0):
        state="상승 확산"
    elif score>=42:
        state="초기 확대"
    else:
        state="관찰"

    return {"score":round(score,1),"state":state,"delta_rs":round(d_rs,2),
            "delta_breadth":round(d_breadth,1),"delta_accel":round(d_accel,2)}


def _theme_stage(score, rank, total, lifecycle=None):
    """현재 강도 + 생애주기를 결합한 화면용 단계."""
    lc=lifecycle or {}
    state=lc.get("state","")
    if state=="쇠퇴":
        return "쇠퇴"
    if state=="과열":
        return "과열"
    if score >= 78 and lc.get("score",0)>=60:
        return "현재 주도"
    if score >= 64 and lc.get("score",0)>=50:
        return "상승 확산"
    if lc.get("score",0)>=45 or score>=50:
        return "초기 확대"
    return "초기 관심"


@st.cache_data(ttl=300, show_spinner=False)
def load_market_benchmark():
    """개별주 레이더의 시장 기준선: KOSPI 지수(^KS11)."""
    try:
        d=yf.download("^KS11",period="2y",interval="1d",auto_adjust=False,progress=False,threads=False)
        return normalize_df(d)
    except Exception:
        return pd.DataFrame()


def _benchmark_snapshot():
    df = load_market_benchmark()
    if df.empty:
        return {"ret20":0.0,"ret60":0.0}
    d = calculate_indicators(df)
    if d.empty:
        return {"ret20":0.0,"ret60":0.0}
    close = d["Close"]
    return {
        "ret20": safe_float(d["RET20"].iloc[-1]),
        "ret60": safe_float(close.pct_change(60).iloc[-1] * 100),
    }


def _score_theme(rows, benchmark):
    if not rows:
        return 0.0
    def avg(key):
        vals=[safe_float(x.get(key), np.nan) for x in rows]
        vals=[x for x in vals if np.isfinite(x)]
        return float(np.mean(vals)) if vals else 0.0
    ret20=avg("ret20"); ret60=avg("ret60"); vr=avg("vr")
    rs20=ret20-benchmark["ret20"]; rs60=ret60-benchmark["ret60"]
    breadth=avg("breadth"); ma60=avg("ma60_gap"); accel=avg("accel")
    rsi=avg("rsi")
    # 100점: 수익률보다 상대강도·확산·거래량·추세를 균형 있게 반영
    s=0.0
    s += np.clip((ret20+10)/30*100,0,100)*0.15
    s += np.clip((ret60+15)/50*100,0,100)*0.15
    s += np.clip((rs20+10)/30*100,0,100)*0.15
    s += np.clip((rs60+15)/50*100,0,100)*0.10
    s += np.clip((vr-0.6)/1.4*100,0,100)*0.15
    s += np.clip(breadth,0,100)*0.15
    s += np.clip((ma60+10)/30*100,0,100)*0.05
    s += np.clip((accel+10)/30*100,0,100)*0.05
    # RSI는 지나친 과열을 감점하되 강세권은 가점
    if 52 <= rsi <= 68: rsi_score=100
    elif 45 <= rsi < 52 or 68 < rsi <= 73: rsi_score=75
    elif 40 <= rsi < 45 or 73 < rsi <= 78: rsi_score=45
    else: rsi_score=20
    s += rsi_score*0.05
    return float(np.clip(s,0,100))


def build_future_theme_engine(force=False):
    cached=st.session_state.get("future_engine_cache")
    if cached and not force:
        if (datetime.now()-cached["time"]).total_seconds() < 1800:
            return cached["data"]

    universe=st.session_state.get("stock_universe",{})
    if not universe:
        universe=load_stock_universe()
        st.session_state.stock_universe=universe
    benchmark=_benchmark_snapshot()
    candidates=[]

    # 기존 seed 테마 + 종목명에서 자동 발굴한 신규 테마를 함께 평가합니다.
    dynamic_lexicon = get_dynamic_theme_lexicon(universe)
    for theme, keywords in dynamic_lexicon.items():
        matched=[]
        for code,name in universe.items():
            hits=_theme_match(name,keywords)
            if hits:
                matched.append((hits, _normalize_stock_code(code), safe_stock_name(code,name)))
        matched.sort(key=lambda x:(x[0],x[2]), reverse=True)
        # 같은 테마가 주식 하나뿐이면 통계적으로 불안정하므로 제외합니다.
        if len(matched)<2:
            continue
        # 특정 주식/키워드 히트수에만 표본이 몰리는 것을 줄이기 위해
        # 상위 매칭 4개 + 나머지 구간에서 균등하게 최대 4개를 추가합니다.
        if len(matched) <= 8:
            sampled = matched
        else:
            sampled = matched[:4]
            rest = matched[4:]
            idxs = np.linspace(0, len(rest)-1, 4, dtype=int).tolist()
            sampled.extend(rest[i] for i in idxs if rest[i] not in sampled)
        rows=[]
        for hits,code,name in sampled:
            df=load_price_data(code)
            if df.empty: continue
            d=calculate_indicators(df)
            if len(d)<65: continue
            r=d.iloc[-1]; close=d["Close"]
            ret20=safe_float(r.get("RET20")); ret60=safe_float(close.pct_change(60).iloc[-1]*100)
            ma20=safe_float(r.get("MA20"),safe_float(r.get("Close"))); ma60v=safe_float(r.get("MA60"),safe_float(r.get("Close")))
            current=safe_float(r.get("Close"))
            ret5=safe_float(r.get("RET5")); vr=safe_float(r.get("VOL_RATIO"),1); rsi=safe_float(r.get("RSI14"),50)
            breadth=100.0 if current>=ma20 else 0.0
            ma60_gap=(current/ma60v-1)*100 if ma60v else 0
            accel=ret5-(ret20/4 if np.isfinite(ret20) else 0)
            # 20거래일 전 상태를 함께 저장해 테마가 실제로 확산 중인지 판별
            prev=d.iloc[-21] if len(d)>=86 else None
            if prev is not None:
                prev_close=safe_float(prev.get("Close"),0)
                prev_ma20=safe_float(prev.get("MA20"),prev_close)
                prev_ma60=safe_float(prev.get("MA60"),prev_close)
                prev_ret20=safe_float(prev.get("RET20"),0)
                prev_ret60=safe_float(close.pct_change(60).iloc[-21]*100,0)
                prev_ret5=safe_float(prev.get("RET5"),0)
                prev_breadth=100.0 if prev_close>=prev_ma20 else 0.0
                prev_accel=prev_ret5-(prev_ret20/4 if np.isfinite(prev_ret20) else 0)
                prev_rs20=prev_ret20-safe_float(benchmark.get("ret20"),0)
            else:
                prev_ret20=ret20; prev_ret60=ret60; prev_breadth=breadth; prev_accel=accel; prev_rs20=ret20-safe_float(benchmark.get("ret20"),0)
            rows.append({"code":code,"name":name,"price":current,"rsi":rsi,"vr":vr,"ret":ret20,"ret20":ret20,"ret60":ret60,"ret5":ret5,"trend":"상승" if current>=ma20 else "조정","ma60_gap":ma60_gap,"breadth":breadth,"accel":accel,"hits":hits,
                         "rs20":ret20-safe_float(benchmark.get("ret20"),0),"ret20_prev":prev_ret20,"ret60_prev":prev_ret60,"breadth_prev":prev_breadth,"accel_prev":prev_accel,"rs20_prev":prev_rs20})
        if len(rows)<2: continue
        score=_score_theme(rows,benchmark)
        # 종목간 평균으로 다시 확산도를 계산하여 단일 급등 종목의 왜곡을 줄입니다.
        breadth=sum(1 for x in rows if x["ret20"]>0)/len(rows)*100
        breadth_prev=sum(1 for x in rows if x.get("ret20_prev",0)>0)/len(rows)*100
        for x in rows:
            x["breadth"]=breadth
            x["breadth_prev"]=breadth_prev
        score=_score_theme(rows,benchmark)
        lifecycle=_theme_lifecycle(rows,benchmark)
        # 기존 점수 75% + 생애주기 25%: 검증된 가격/강도 체계를 유지하면서
        # '지금 강한 테마'보다 '지금 막 강해지는 테마'를 조금 더 앞세웁니다.
        final_score=float(np.clip(score*.75+lifecycle["score"]*.25,0,100))
        candidates.append({"theme":theme,"score":final_score,"base_score":score,"lifecycle":lifecycle,"rows":rows,"count":len(rows)})

    candidates.sort(key=lambda x:x["score"],reverse=True)
    # 너무 작은/약한 테마는 미래테마에서 제외하고 상위 10개까지만 표시합니다.
    candidates=[x for x in candidates if x["score"]>=42][:10]
    chain=[]
    details={}
    total=len(candidates)
    for rank,item in enumerate(candidates,1):
        stage=_theme_stage(item["score"],rank,total,item.get("lifecycle"))
        item["stage"]=stage; item["rank"]=rank
        item["reason"]=THEME_REASONS.get(item["theme"],"전체 주식 시장에서 가격·거래량·상대강도·추세가 함께 개선되는 테마를 자동 선별합니다.")
        chain.append((item["theme"],stage))
        details[item["theme"]]=item
    data={"chain":chain,"details":details,"benchmark":benchmark,"updated":datetime.now().strftime("%Y-%m-%d %H:%M")}
    st.session_state.future_engine_cache={"time":datetime.now(),"data":data}
    return data


def get_future_chain(force=False):
    return build_future_theme_engine(force).get("chain",[])


def future_theme_info(theme):
    return build_future_theme_engine().get("details",{}).get(theme,{})


def theme_candidates(theme):
    return [{"code":x["code"],"name":x["name"]} for x in future_theme_info(theme).get("rows",[])]


def theme_snapshot(theme):
    info=future_theme_info(theme)
    rows=info.get("rows",[])
    return rows


# ============================================================

# INLINE FUTURE 주식 ANALYSIS
# ============================================================

def render_future_inline_analysis():
    code = st.session_state.future_detail_code
    if not code:
        return

    theme = st.session_state.future_detail_theme
    df = load_price_data(code)
    if df.empty:
        st.warning("선택한 주식의 가격 데이터를 확인하지 못했습니다.")
        return

    d = calculate_indicators(df)
    if d.empty:
        return

    name = get_stock_name(code)
    current = safe_float(d["Close"].iloc[-1])
    previous = safe_float(d["Close"].iloc[-2]) if len(d) > 1 else current
    change = current - previous
    pct = change / previous * 100 if previous else 0
    cls = "positive" if change > 0 else ("negative" if change < 0 else "neutral")

    st.markdown(
        f"""
        <div class="future-analysis">
            <div class="future-analysis-title">미래테마 안에서 분석 · {esc(theme or "선택 주식")}</div>
            <div class="future-analysis-name">{esc(name)}</div>
            <div class="future-analysis-code">{esc(code)}</div>
            <div class="quote-row">
                <div class="quote-price">{money(current)}</div>
                <div class="quote-change {cls}">{money(change)} ({pct:+.2f}%)</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    render_judgment(d)
    st.markdown('<div class="section-title">가격 흐름 · 최근 6개월</div>', unsafe_allow_html=True)
    render_chart(d)


# ============================================================
# FUTURE THEME
# ============================================================

def future_stage_class(stage):
    if "현재 주도" in stage: return "stage-core"
    if "다음 수혜" in stage: return "stage-next"
    if "관심 확대" in stage: return "stage-interest"
    return "stage-early"


def future_outlook(theme, rows):
    if not rows: return "현재 가격 데이터를 충분히 확보하지 못했습니다."
    avg20=float(np.mean([x["ret20"] for x in rows])); avg60=float(np.mean([x["ret60"] for x in rows]))
    avg_rsi=float(np.mean([x["rsi"] for x in rows])); avg_vol=float(np.mean([x["vr"] for x in rows]))
    rising=sum(1 for x in rows if x["trend"]=="상승"); total=len(rows)
    return f"구성 주식 {rising}/{total}개가 20일선 위이며 20일 {avg20:+.1f}%, 60일 {avg60:+.1f}%, RSI {avg_rsi:.1f}, 거래량 {avg_vol:.2f}배입니다. 가격 상승뿐 아니라 확산도와 거래량을 함께 확인합니다."


def _theme_stock_rank(item, benchmark_ret20=0):
    """미래테마 내 주식 순위 계산.
    기존 테마 엔진의 선행점수/가격구간 로직을 그대로 사용합니다.
    """
    ranked = []
    for row in item.get("rows", []):
        code = row.get("code")
        df = load_price_data(code) if code else pd.DataFrame()
        if df.empty:
            continue
        d = calculate_indicators(df)
        if d.empty:
            continue
        r = d.iloc[-1]
        sig = leading_signal(r, benchmark_ret20)
        zone = validated_price_zone(r)
        score = float(sig["score"]) * 0.65 + float(item.get("score", 0)) * 0.35
        ranked.append({
            **row,
            "signal_score": round(score),
            "zone": zone,
            "lead": sig,
            "raw": r,
            "rsi": safe_float(sig.get("rsi"), 50),
            "ret20": safe_float(row.get("ret20", r.get("RET20", 0)), 0),
        })
    ranked.sort(
        key=lambda x: (x["signal_score"], x.get("ret20", -999)),
        reverse=True
    )
    return ranked


DOMESTIC_IMPLEMENTATION = {
    "QQQ": [{"name":"TIGER 미국나스닥100", "code":"133690", "match":"나스닥100 직접 추종", "horizon":"장기 코어 후보", "confidence":"높음"}],
    "XLK": [{"name":"TIGER 미국테크TOP10 INDXX", "code":"381170", "match":"미국 대형 기술주 집중", "horizon":"장기 코어 + 중기 운용", "confidence":"중간"}],
    "SMH": [{"name":"TIGER 미국필라델피아반도체나스닥", "code":"381180", "match":"미국 반도체 섹터", "horizon":"중기 + 장기 위성", "confidence":"높음"}],
    "SOXX": [{"name":"TIGER 미국필라델피아반도체나스닥", "code":"381180", "match":"미국 반도체 섹터", "horizon":"중기 + 장기 위성", "confidence":"높음"}],
    "BOTZ": [{"name":"TIGER 글로벌AI&로보틱스 INDXX", "code":"464310", "match":"AI·로봇 관련 글로벌 혁신기업", "horizon":"중기 위성", "confidence":"중간"}],
    "ARKQ": [{"name":"TIGER 글로벌AI&로보틱스 INDXX", "code":"464310", "match":"AI·로봇 관련 글로벌 혁신기업", "horizon":"중기 위성", "confidence":"중간"}],
    "GLD": [{"name":"TIGER 골드선물(H)", "code":"319640", "match":"금 가격", "horizon":"장기 분산자산", "confidence":"높음"}],
    "TLT": [{"name":"TIGER 미국30년국채스트립액티브(합성 H)", "code":"458250", "match":"미국 장기국채", "horizon":"중장기 방어자산", "confidence":"중간"}],
}

DOMESTIC_IMPLEMENTATION_CODES = {v["code"] for vals in DOMESTIC_IMPLEMENTATION.values() for v in vals}

def get_domestic_implementation(code):
    return DOMESTIC_IMPLEMENTATION.get(str(code).upper(), [])


def _user_trade_guide(x):
    r = x.get("raw") if isinstance(x, dict) else None
    if r is None:
        return None
    c = safe_float(r.get("Close"), np.nan)
    ma20 = safe_float(r.get("MA20"), c)
    low20 = safe_float(r.get("LOW20"), c)
    ma60 = safe_float(r.get("MA60"), c)
    if not np.isfinite(c) or c <= 0:
        return None
    support = max(low20, ma20 * 0.985)
    buy_top = ma20 * 1.025
    invalid = min(ma60 * 0.97, support * 0.97)
    if invalid <= 0:
        invalid = c * 0.92
    risk = max(buy_top - invalid, c * 0.05)
    return {
        "buy1": buy_top,
        "buy2": (buy_top + invalid) / 2,
        "buy3": invalid,
        "stop": invalid,
        "tp1": buy_top + risk,
        "tp2": buy_top + risk * 2,
    }


def _render_theme_etf_card(theme, item, rank, guide=False, theme_score=None):
    name=item.get("name",item.get("code","-")); code=item.get("code","")
    domestic=get_domestic_implementation(code); dom=domestic[0] if domestic else None
    label={1:"🥇 최우선",2:"🥈 우선",3:"👀 관찰"}.get(rank,f"{rank}순위")
    price=item.get("price",np.nan); zone=item.get("zone",{}).get("state","")
    action=("지금 매수 검토" if zone=="매수구간" else
            "매수 대기" if zone=="눌림대기" else
            "추격매수 주의" if zone=="추격금지" else "관찰")
    display=dom["name"] if dom else name
    price_text=money(price) if np.isfinite(price) else "-"
    sig_score=safe_float(item.get("signal_score"),0)

    if guide:
        g=_user_trade_guide(item)
        st.markdown(
            f'<div class="priority-theme-card">'
            f'<div class="priority-theme-head">'
            f'<div class="theme-title">{esc(theme)}</div>'
            f'<div class="theme-summary-meta">테마점수 {safe_float(theme_score,0):.0f} · C/D 선행점수 {sig_score:.0f} · 최우선 주식</div>'
            f'</div>'
            f'<div class="theme-summary-card">'
            f'<div class="theme-stage-wrap"><span class="theme-stage-badge">{label}</span>'
            f'<span class="theme-stage-badge">{action}</span></div>'
            f'<div class="theme-stock-title">{esc(display)}</div>'
            f'<div class="theme-summary-meta">{esc(theme)} · C/D 선행점수 {sig_score:.0f} · 현재가 {price_text}</div>'
            f'<div class="theme-summary-outlook">미국 선행 주식 · {esc(code)} · 20일 {safe_float(item.get("ret20"),0):+.2f}% · RSI {safe_float(item.get("rsi"),0):.1f}</div>'
            f'</div>'
            + (f'<div class="cd-item"><div class="theme-summary-title">매수·매도 가이드</div>'
               f'<div class="theme-summary-meta">1차 40% · {money(g["buy1"])} 이하</div>'
               f'<div class="theme-summary-meta">2차 30% · {money(g["buy2"])} 이하</div>'
               f'<div class="theme-summary-meta">3차 30% · {money(g["buy3"])} 이하</div>'
               f'<div class="theme-summary-meta">손절 {money(g["stop"])} · 1차 익절 {money(g["tp1"])} · 2차 익절 {money(g["tp2"])}</div></div>' if g else '')
            + '</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="theme-summary-card">'
            f'<div class="theme-stage-wrap"><span class="theme-stage-badge">{label}</span>'
            f'<span class="theme-stage-badge">{action}</span></div>'
            f'<div class="theme-stock-title">{esc(display)}</div>'
            f'<div class="theme-summary-meta">{esc(theme)} · C/D 선행점수 {sig_score:.0f} · 현재가 {price_text}</div>'
            f'<div class="theme-summary-outlook">미국 선행 주식 · {esc(code)} · 20일 {safe_float(item.get("ret20"),0):+.2f}% · RSI {safe_float(item.get("rsi"),0):.1f}</div>'
            f'</div>', unsafe_allow_html=True)

    # 미래테마에서 내 주식로 바로 이동할 수 있는 두 버튼을 한 행에 배치
    b1,b2=st.columns(2)
    is_open=st.session_state.get("future_detail_code")==code
    with b1:
        if st.button("분석 닫기" if is_open else "종목 분석", use_container_width=True,
                     key=f"future_an_{theme}_{rank}_{code}"):
            st.session_state.future_detail_code=None if is_open else code
            st.session_state.future_detail_theme=None if is_open else theme
            st.rerun()
    with b2:
        already=code in st.session_state.watchlist
        if st.button("⭐ 관심등록" if not already else "⭐ 등록됨", disabled=already,
                     use_container_width=True, key=f"future_watch_{theme}_{rank}_{code}"):
            add_watch(code)
            st.session_state.selected_code=code
            st.rerun()
    if is_open:
        render_future_inline_analysis()


def render_future_theme():
    st.caption("🔄 주식 MASTER 기반 자동 테마 발굴 · 기존 테마 + 신규 종목명 반복 키워드 자동 반영")
    st.markdown('<div class="hero"><div class="hero-name">미래테마</div><div class="hero-code">유망 테마 TOP 10 · 강한 테마부터 압축 선별</div></div>',unsafe_allow_html=True)
    c1,c2=st.columns([1,1])
    with c1:
        if st.button("🔄 미래테마 업데이트",use_container_width=True,key="future_theme_refresh"):
            st.session_state.theme_cache={}; st.session_state.price_cache={}; st.session_state.future_engine_cache=None; st.rerun()
    with c2:
        auto_update=st.checkbox("⚡ 자동 업데이트 · 30분",value=False,key="future_auto_update")
        if auto_update and st_autorefresh is not None: st_autorefresh(interval=30*60*1000,key="future_theme_autorefresh")

    with st.spinner("테마와 주식을 계산하는 중입니다…"):
        engine=build_future_theme_engine()
    chain=engine.get("chain",[])[:10]
    if not chain:
        st.warning("현재 가격 데이터에서 테마 후보를 찾지 못했습니다.")
        return
    bench=engine.get("benchmark",{})
    details=engine.get("details",{})
    st.caption(f'기준시각 {engine.get("updated","-")} · 전체 테마를 계산한 뒤 상위 10개만 화면에 표시합니다.')

    # 미래테마 화면 순위는 테마점수/선행점수(C/D)를 기준으로 압축한 TOP10입니다.
    # 화면 단계만 1~2위 / 3~4위 / 5~6위로 구분하며 C/D 계산식 자체는 변경하지 않습니다.
    groups=[("🥇 최우선",chain[:2],"future-group-priority"),
            ("🥈 우선",chain[2:6],"future-group-secondary"),
            ("👀 관찰",chain[6:10],"future-group-watch")]

    for group_label,items,group_cls in groups:
        if not items:
            continue
        st.markdown(f'<div class="future-group-title {group_cls}">{group_label}</div>',unsafe_allow_html=True)
        for theme,stage in items:
            info=details.get(theme,{})
            ranked=_theme_stock_rank(info,bench.get("ret20",0))
            if not ranked:
                continue
            score=safe_float(info.get("score",0),0)
            # 최우선/우선 테마는 테마 + 최우선 주식 + C/D 가이드를 하나로 강조
            is_priority_theme=group_label in {"🥇 최우선","🥈 우선"}
            if is_priority_theme:
                _render_theme_etf_card(theme,ranked[0],1,guide=True,theme_score=score)
                for i,x in enumerate(ranked[1:3],2):
                    _render_theme_etf_card(theme,x,i,guide=False,theme_score=score)
            else:
                st.markdown(
                    f'<div class="theme-card"><div class="theme-title">{esc(theme)}</div>'
                    f'<div class="theme-summary-meta">테마점수 {score:.0f} · 주식 {len(ranked)}개</div></div>',
                    unsafe_allow_html=True)
                for i,x in enumerate(ranked[:3],1):
                    _render_theme_etf_card(theme,x,i,guide=False,theme_score=score)
            if len(ranked)>3:
                with st.expander(f"{theme} 나머지 주식 {len(ranked)-3}개 보기"):
                    for i,x in enumerate(ranked[3:],4):
                        _render_theme_etf_card(theme,x,i,guide=False,theme_score=score)


# FINAL TARGET
# ============================================================

def _future_theme_selected_map(benchmark_ret20=0):
    """
    미래테마 TOP 순위와 테마 내부 주식 순위를 분리해서 보관합니다.
    기존에는 `rank` 하나만 저장하여 '미래테마 #1'과 '그 테마의 주식 #1'이
    혼용될 수 있었습니다. 최종타겟에서는 반드시 두 순위를 별도로 사용합니다.
    """
    selected = {}
    try:
        for theme_rank, (theme, _stage) in enumerate(get_future_chain(), 1):
            info = future_theme_info(theme)
            ranked = _theme_stock_rank(info, benchmark_ret20)
            for stock_rank, x in enumerate(ranked[:3], 1):
                code = _normalize_stock_code(x.get('code'))
                if not code:
                    continue
                rec = {
                    'theme': theme,
                    'theme_rank': theme_rank,
                    'stock_rank': stock_rank,
                    'signal_score': safe_float(x.get('signal_score'), 0),
                    'theme_score': safe_float(info.get('score'), 0),
                }
                prev = selected.get(code)
                # 같은 주식이 복수 테마에 걸리면 미래테마 우선순위가 높은 연결을 사용합니다.
                if prev is None or (
                    rec['theme_rank'], rec['stock_rank'], -rec['signal_score']
                ) < (
                    prev['theme_rank'], prev['stock_rank'], -prev['signal_score']
                ):
                    selected[code] = rec
    except Exception:
        pass
    return selected


def _final_horizon_snapshot(d, code):
    if d is None or d.empty:
        return {'long':'데이터 부족','long_score':0,'mid':'데이터 부족','mid_score':0,'short':'데이터 부족','lead_score':0,'price_zone':'확인','focus':'확인 불가','structural_break':False}
    long = long_term_horizon(d)
    r=d.iloc[-1]
    c=safe_float(r.get('Close'),0); ma20=safe_float(r.get('MA20'),c); ma60=safe_float(r.get('MA60'),c); ma120=safe_float(r.get('MA120'),c)
    r60=safe_float(r.get('RET60'),0); bench=_benchmark_snapshot(); rs20=safe_float(r.get('RET20'),0)-safe_float(bench.get('ret20'),0)
    mid_score=(25 if c>ma60 else 0)+(20 if ma20>ma60 else 0)+(20 if ma60>ma120 else 0)+(20 if r60>0 else 0)+(15 if rs20>0 else 0)
    mid='🟢 중기 상승' if mid_score>=75 else '🟡 중기 확인' if mid_score>=55 else '🔴 중기 약세'
    lead=leading_signal(r,safe_float(bench.get('ret20'),0)); zone=validated_price_zone(r)
    overheat=radar_overheat_score({'rsi':safe_float(r.get('RSI14'),50),'ret5':safe_float(r.get('RET5'),0),'dist20':((c/ma20-1)*100 if ma20 else 0),'vr':safe_float(r.get('VOL_RATIO'),1)})
    if zone['state']=='매수구간' and lead['score']>=72 and overheat<65: short='🔥 단기 진입 우위'
    elif zone['state']=='눌림대기': short='🟢 단기 눌림대기'
    elif zone['state']=='추격금지': short='🔴 단기 추격금지'
    elif zone['state']=='무효': short='🔴 단기 무효'
    else: short='🟡 단기 확인'
    if long.get('score',0)>=78 and mid_score>=55: focus='장기 중심'
    elif mid_score>=75: focus='중기 중심'
    elif lead['score']>=72 and zone['state'] in {'매수구간','눌림대기'}: focus='단기 중심'
    else: focus='관찰 중심'
    return {'long':long.get('suitability','확인 불가'),'long_score':int(long.get('score',0)),'mid':mid,'mid_score':int(mid_score),'short':short,'lead_score':int(lead.get('score',0)),'price_zone':zone.get('state','확인'),'focus':focus,'structural_break':bool(long.get('structural_break',False))}


def render_final_target_horizon(code):
    df=load_price_data(code)
    if df.empty: st.info('장기·중기·단기 판정에 필요한 가격 데이터를 확인하지 못했습니다.'); return
    d=calculate_indicators(df)
    if d.empty: st.info('장기·중기·단기 판정에 필요한 지표를 계산하지 못했습니다.'); return
    h=_final_horizon_snapshot(d,code)
    with st.expander('📆 투자기간별 전략 보기', expanded=False):
        st.markdown(f'''<div class="final-horizon-grid">
        <div class="final-horizon-box"><div class="final-horizon-label">6~12개월 · 장기</div><div class="final-horizon-value">{esc(h['long'])} · {h['long_score']}/100</div></div>
        <div class="final-horizon-box"><div class="final-horizon-label">1~3개월 · 중기</div><div class="final-horizon-value">{esc(h['mid'])} · {h['mid_score']}/100</div></div>
        <div class="final-horizon-box"><div class="final-horizon-label">1~4주 · 단기</div><div class="final-horizon-value">{esc(h['short'])}</div></div></div>''', unsafe_allow_html=True)
        st.caption(f"장기 = 6~12개월 · 중기 = 1~3개월 · 단기 = 1~4주 | 현재 우선축: {h['focus']} · 선행점수 {h['lead_score']}/100 · 가격구간 {h['price_zone']}")
        if h['structural_break']: st.warning('장기 구조적 훼손이 확인되어 신규매수보다 구조 재검토를 우선합니다.')


def build_final_targets(radar_data):
    """
    최종타겟은 '현재 강한 주식'를 뽑는 것이 아니라
    미래테마 우선순위 + 현재 시장조건을 교차해서 결정합니다.

    핵심:
      - 미래테마 순위: 미래 방향성의 앵커
      - cross_score: 현재 투자조건
      - 주식 내부 순위: 같은 테마 안에서의 대표성
    따라서 방산처럼 현재 모멘텀이 강하더라도 미래테마 순위가 낮으면
    무조건 AI/반도체를 밀어내지 못하게 합니다.
    """
    rows = radar_data.get('rows', []) if radar_data else []
    benchmark = radar_data.get('benchmark', {}) if radar_data else {}
    selected = _future_theme_selected_map(safe_float(benchmark.get('ret20'), 0))
    targets = []

    for item in rows:
        code = _normalize_stock_code(item.get('code'))
        rel = selected.get(code)
        if not rel:
            continue

        if item.get('opportunity', 0) < 55:
            continue
        if item.get('rsi', 100) >= 72 or item.get('ret5', 999) >= 8:
            continue
        if item.get('price_zone') == '무효':
            continue

        x = dict(item)
        theme_rank = int(rel.get('theme_rank', 99))
        stock_rank = int(rel.get('stock_rank', 99))
        theme_score = safe_float(rel.get('theme_score'), 0)
        cross_score = safe_float(x.get('cross_score'), 0)

        # 미래테마 순위를 '방향성 앵커'로 사용합니다.
        # 1위=100, 이후 8점씩 감점하여 현재 모멘텀이 좋아도
        # 미래테마 순위가 크게 낮은 종목의 과도한 역전을 방지합니다.
        future_anchor = max(40.0, 100.0 - (theme_rank - 1) * 8.0)

        # 역할을 분리합니다.
        # 현재 레이더 70% + 미래테마 20% + 테마순위 앵커 10%.
        # cross_score 자체에는 미래테마 원점수가 중복으로 들어가지 않습니다.
        final_score = (
            cross_score * 0.70 +
            theme_score * 0.20 +
            future_anchor * 0.10
        )

        # 같은 테마에서는 대표 주식을 약간 우선합니다.
        final_score -= max(0, stock_rank - 1) * 1.5

        # 미래 1위 테마가 현재도 충분히 좋은 경우에는 강한 우선권을 줍니다.
        if theme_rank == 1 and cross_score >= 70:
            final_score += 4.0
        elif theme_rank >= 4 and cross_score < 85:
            final_score -= 3.0

        x.update({
            'future_theme_selected': True,
            'future_theme': rel['theme'],
            'future_theme_rank': theme_rank,
            'future_stock_rank': stock_rank,
            'future_theme_score': theme_score,
            'future_theme_anchor': round(future_anchor, 1),
            'future_theme_lead': rel['signal_score'],
            'final_score': round(float(np.clip(final_score, 0, 100)), 1),
        })
        targets.append(x)

    targets.sort(
        key=lambda x: (
            x.get('final_score', 0),
            x.get('cross_score', 0),
            -x.get('future_theme_rank', 99),
            x.get('opportunity', 0),
            x.get('rs20', -999),
        ),
        reverse=True
    )

    for i, x in enumerate(targets, 1):
        fs = safe_float(x.get('final_score'), 0)
        cross = safe_float(x.get('cross_score'), 0)
        theme_rank = int(x.get('future_theme_rank', 99))

        if fs >= 82 and cross >= 75 and x.get('price_zone') == '매수구간' and x.get('overheat', 0) < 65:
            state = '🔥 최종 타겟'
        elif fs >= 72:
            state = '🟢 최종 우선'
        elif fs >= 60:
            state = '🟡 최종 관찰'
        else:
            state = '⚪ 대기'

        x['final_rank'] = i
        x['final_state'] = state
        x['final_reason'] = (
            f"미래테마 #{theme_rank} · 미래성 {x.get('future_theme_score',0):.0f} · "
            f"현재조건 {cross:.0f} · 가격구간 {x.get('price_zone','확인')}"
        )

    return targets



def render_final_target_trade_strategy(code,item=None):
    """최종 타겟 각 주식의 추천기간 하나를 기준으로 실제 행동전략을 표시합니다."""
    try:
        df=load_price_data(code); d=calculate_indicators(df)
    except Exception:
        return
    if d.empty: return

    holding=st.session_state.holdings.get(code) or {}
    held=bool(holding)
    avg=safe_float(holding.get("avg_price",0),0) if held else 0
    qty=safe_float(holding.get("quantity",0),0) if held else 0
    hmeta,h=_recommended_horizon(d,code)
    rec_horizon,rec_label,rec_period=hmeta

    with st.expander("💰 실제 매수·익절·손절 전략", expanded=False):
        st.markdown(f"**{esc(rec_label)} · 추천기간 {esc(rec_period)}**")
        lv=trade_levels(d,held,avg,rec_horizon)
        if not lv:
            st.info("현재 가격 데이터로 전략을 계산할 수 없습니다.")
            return

        if not held:
            st.caption("미보유 · 추천기간 기준")
            cols=st.columns(3)
            cards=[
                ("🎯 매수금액",money(lv["entry"]),f"{rec_period} 추천 진입"),
                ("🟡 눌림기준",money(lv["support"]),"핵심 지지 확인"),
                ("🛑 무효금액",money(lv["stop"]),"이탈 시 매수 취소"),
            ]
            for col,(title,price,desc) in zip(cols,cards):
                with col:
                    with st.container(border=True):
                        st.markdown(f'<div class="trade-card-label">{esc(title)}</div><div class="trade-card-price">{esc(price)}</div><div class="trade-card-desc">{esc(desc)}</div>',unsafe_allow_html=True)
        else:
            st.caption(f"보유중 · 평균매수가 {money(avg)}" + (f" · {qty:,.0f}주" if qty>0 else ""))
            _render_trade_cards(lv,avg,qty)
            with st.expander("다른 투자기간 전략 보기",expanded=False):
                for horizon,label in [("장기","🟢 장기 · 6~12개월"),("중기","🔵 중기 · 1~3개월"),("단기","🟡 단기 · 1~4주")]:
                    if horizon==rec_horizon: continue
                    lv2=trade_levels(d,True,avg,horizon)
                    st.markdown(f"**{label}**")
                    _render_trade_cards(lv2,avg,qty)

def render_final_target():
    if st_autorefresh is not None:
        st_autorefresh(interval=10*60*1000, key="final_target_autorefresh")
    st.markdown('<div class="hero"><div class="hero-name">🏆 최종 타겟</div><div class="hero-code">미래테마 × 현재 모멘텀 × 가격구간을 모두 통과한 최종 투자 후보</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="final-target-hero"><div class="final-target-title">무엇을 살 것인가 → 언제 접근할 것인가</div><div class="final-target-sub">미래테마 우선순위를 방향성 앵커로 두고, 현재 시장조건·선행성·가격구간을 교차 검증합니다. 여러 종목이 조건을 통과하면 점수순으로 표시하며 1위는 가장 크게 강조합니다.</div></div>', unsafe_allow_html=True)
    if st.button("🔄 최종 타겟 새로고침", use_container_width=True, key="final_target_refresh"):
        st.session_state.radar_cache=None; st.session_state.future_engine_cache=None; st.session_state.price_cache={}; st.rerun()
    with st.spinner("미래테마와 시장레이더의 최종 교차 후보를 계산하는 중입니다…"):
        data=build_radar_data(); targets=build_final_targets(data)
    if not targets:
        st.info("현재 시점에는 미래테마와 시장레이더 조건을 동시에 통과한 최종 타겟이 없습니다. 조건 미충족이면 억지로 후보를 만들지 않습니다.")
        # 원인 진단: 후보를 억지로 만들지 않고 어느 단계에서 탈락했는지만 표시합니다.
        try:
            radar_rows = (data or {}).get("rows", [])
            selected_codes = set(_future_theme_selected_map_v2(0).keys())
            overlap = [r for r in radar_rows if _normalize_stock_code(r.get("code")) in selected_codes]
            st.caption(f"진단 · 레이더 후보 {len(radar_rows)}개 · 미래테마 TOP3 교집합 {len(overlap)}개 · 최종 게이트 통과 0개")
            if overlap:
                fails = []
                for r in overlap:
                    code=_normalize_stock_code(r.get("code")); rel=_future_theme_selected_map_v2(0).get(code)
                    if not rel: continue
                    calc=common_target_score_v9(r.get("raw",r), benchmark_snapshot_for_stock(code), safe_float(rel.get("theme_score"),50), int(rel.get("theme_rank",99)), int(rel.get("stock_rank",99)), safe_float(r.get("lifecycle_score"),50), r.get("lifecycle_state","관찰"))
                    if not common_target_gate_v9(calc,r):
                        fails.append(f"{r.get('name',code)}: 유동성 {calc['liquidity_score']:.0f} / 기회 {calc['opportunity']:.0f} / RSI {safe_float(r.get('rsi'),100):.1f} / 5일 {safe_float(r.get('ret5'),999):+.1f}% / 가격 {calc['price_zone']}")
                if fails:
                    with st.expander("최종타겟 미충족 원인 보기", expanded=False):
                        for f in fails[:10]: st.write("• " + f)
        except Exception:
            pass
        return
    top=targets[:5]
    st.caption(f"최종 타겟 {len(targets)}개 · 상위 {len(top)}개 표시 · 기준시각 {data.get('time')}")
    primary=top[0]; code=_normalize_stock_code(primary["code"]); already=code in st.session_state.watchlist
    try:
        _df=load_price_data(code); _d=calculate_indicators(_df)
        h=_final_horizon_snapshot(_d,code) if not _d.empty else {"focus":"관찰 중심"}
    except Exception:
        h={"focus":"관찰 중심"}
    horizon={"장기 중심":"🟢 장기추천","중기 중심":"🔵 중기추천","단기 중심":"🟡 단기추천"}.get(h.get("focus","관찰 중심"),"⚪ 관찰")
    primary_price = safe_float(primary.get("price"), 0)
    st.markdown(f'<div class="final-target-primary"><div class="final-target-rank">🥇 최종 타겟 1위 · {esc(primary["final_state"])} · 미래테마 #{primary.get("future_theme_rank","-")}</div><div style="display:flex;align-items:baseline;justify-content:space-between;gap:12px;flex-wrap:wrap;"><div class="final-target-name-main">{esc(primary["name"])}</div><div style="font-size:1.18rem;font-weight:800;white-space:nowrap;">현재가&nbsp; {money(primary_price)}</div></div><div class="final-target-code">종목코드 {esc(primary["code"])} · {esc(primary.get("future_theme","미래테마 미연결"))} · 테마 내 주식 #{primary.get("future_stock_rank","-")}</div><div style="display:flex;justify-content:space-between;align-items:end;margin-top:12px;gap:10px;"><div><div class="radar-label">최종 점수</div><div class="final-target-score">{primary.get("final_score",0):.0f}</div></div><div style="text-align:right;"><div class="radar-label">추천 보유축</div><div class="final-target-horizon">{horizon}</div></div></div><div class="final-target-reason">{esc(primary.get("final_reason",""))}</div></div>', unsafe_allow_html=True)
    wcol,_=st.columns([2.2,4.8])
    with wcol:
        if st.button("⭐ 등록됨" if already else "⭐ 관심등록",disabled=already,use_container_width=True,key=f"final_watch_primary_{code}"):
            add_watch(code); st.session_state.selected_code=code; st.rerun()
    render_final_target_trade_strategy(primary["code"], primary)
    if len(top)>1:
        st.markdown('<div class="final-target-divider"></div>',unsafe_allow_html=True)
        st.markdown('<div class="section-title">🥈 함께 통과한 차순위 후보</div>',unsafe_allow_html=True)
    for item in top[1:]:
        code=_normalize_stock_code(item["code"]); already=code in st.session_state.watchlist
        try:
            _df=load_price_data(code); _d=calculate_indicators(_df)
            h=_final_horizon_snapshot(_d,code) if not _d.empty else {"focus":"관찰 중심"}
        except Exception:
            h={"focus":"관찰 중심"}
        horizon={"장기 중심":"🟢 장기추천","중기 중심":"🔵 중기추천","단기 중심":"🟡 단기추천"}.get(h.get("focus","관찰 중심"),"⚪ 관찰")
        c1,c2=st.columns([5.6,1.4])
        with c1:
            item_price = safe_float(item.get("price"), 0)
            st.markdown(f'<div class="final-secondary-target"><div class="final-target-rank">#{item["final_rank"]} · {esc(item["final_state"])} · 미래테마 #{item.get("future_theme_rank","-")}</div><div style="display:flex;align-items:baseline;justify-content:space-between;gap:10px;flex-wrap:wrap;"><div class="final-target-name-main">{esc(item["name"])}</div><div style="font-size:1.02rem;font-weight:800;white-space:nowrap;">현재가&nbsp; {money(item_price)}</div></div><div class="final-target-code">종목코드 {esc(item["code"])} · {esc(item.get("future_theme","미래테마 미연결"))} · <span class="final-target-score">최종 {item.get("final_score",0):.0f}</span> · <span class="final-target-horizon">{horizon}</span></div></div>',unsafe_allow_html=True)
        with c2:
            if st.button("⭐ 등록됨" if already else "⭐ 관심등록",disabled=already,use_container_width=True,key=f"final_watch_{code}_{item.get('final_rank',0)}"):
                add_watch(code); st.session_state.selected_code=code; st.rerun()
        render_final_target_trade_strategy(code, item)


# MARKET RADAR
# ============================================================

def get_benchmark_metrics():
    df = load_market_benchmark()
    if df.empty:
        return {"ret20": 0.0, "ret5": 0.0}
    d = calculate_indicators(df)
    if d.empty:
        return {"ret20": 0.0, "ret5": 0.0}
    row = d.iloc[-1]
    return {"ret20": safe_float(row.get("RET20", 0)), "ret5": safe_float(row.get("RET5", 0))}


def radar_theme_for(code, name):
    text=f"{code} {name}"
    best=None; hits=0
    for theme,keywords in THEME_LEXICON.items():
        h=_theme_match(text,keywords)
        if h>hits: best,hits=theme,h
    return best or "기타"


def radar_stage_for(theme):
    for t, stage in get_future_chain():
        if t == theme:
            return stage
    return "기타"


def radar_score(row):
    score = 0
    if row["above20"]: score += 12
    if row["above60"]: score += 13
    rs = row["rs20"]
    if rs >= 5: score += 20
    elif rs >= 2: score += 16
    elif rs > 0: score += 11
    elif rs > -3: score += 5
    vr = row["vr"]
    if 1.15 <= vr <= 2.0: score += 15
    elif 1.0 <= vr < 1.15: score += 9
    elif vr > 2.0: score += 7
    r20, r5 = row["ret20"], row["ret5"]
    if 2 <= r20 <= 15: score += 12
    elif 0 <= r20 < 2: score += 8
    elif r20 > 15: score += 5
    if -2 <= r5 <= 5: score += 8
    elif 5 < r5 <= 8: score += 4
    rsi, dist = row["rsi"], row["dist20"]
    if 50 <= rsi <= 68: score += 12
    elif 45 <= rsi < 50 or 68 < rsi <= 72: score += 7
    elif rsi < 40 or rsi > 78: score += 2
    if dist <= 4: score += 8
    elif dist <= 7: score += 5
    elif dist <= 10: score += 2
    return int(min(100, max(0, score)))


def radar_overheat_score(row):
    score = 0
    if row["rsi"] >= 75: score += 30
    elif row["rsi"] >= 70: score += 22
    elif row["rsi"] >= 67: score += 10
    if row["ret5"] >= 10: score += 25
    elif row["ret5"] >= 7: score += 18
    elif row["ret5"] >= 5: score += 10
    if row["dist20"] >= 12: score += 25
    elif row["dist20"] >= 8: score += 18
    elif row["dist20"] >= 5: score += 8
    if row["vr"] >= 2.0: score += 20
    elif row["vr"] >= 1.5: score += 14
    elif row["vr"] >= 1.2: score += 7
    return int(min(100, score))


def radar_target_stocks():
    """시장레이더는 미래테마 후보 + 보유 주식를 중심으로 분석합니다.
    전체 주식의 가격데이터를 매번 조회하지 않도록 후보군을 제한합니다.
    """
    targets = {}

    # 미래테마 TOP 10에 포함된 주식만 레이더 후보로 사용합니다.
    # build_future_theme_engine() 결과는 자체 캐시를 사용하므로 매번 재계산하지 않습니다.
    try:
        engine = build_future_theme_engine()
        details = engine.get("details", {}) if engine else {}
        for info in details.values():
            for row in info.get("rows", []):
                code = _normalize_stock_code(row.get("code"))
                if not code:
                    continue
                name = row.get("name") or get_stock_name(code)
                if name and not str(name).startswith("주식 "):
                    targets[code] = name
    except Exception:
        pass

    # 보유 주식는 미래테마에 없더라도 항상 포함합니다.
    for raw_code in st.session_state.get("holdings", []):
        code = _normalize_stock_code(raw_code)
        if not code:
            continue
        name = get_stock_name(code)
        if not name or name.startswith("주식 "):
            name = lookup_live_stock(code) or name
        targets[code] = name

    return targets

def build_radar_data(force=False):
    now = datetime.now()
    cached = st.session_state.get("radar_cache")
    targets = radar_target_stocks()
    target_key = tuple(sorted(targets.keys()))
    if cached and not force:
        try:
            age = (now - cached["time"]).total_seconds()
            if age < 300 and cached.get("target_key") == target_key and "rows" in cached:
                return cached
        except Exception:
            pass

    benchmark = get_benchmark_metrics()
    rows = []
    for code, target_name in targets.items():
        name = target_name or get_stock_name(code)
        if not name or str(name).startswith("주식 "):
            continue
        df = load_price_data(code)
        if df.empty or len(df) < 65:
            continue
        try:
            d = calculate_indicators(df)
            if d.empty:
                continue
            r = d.iloc[-1]
        except Exception:
            continue
        current = safe_float(r["Close"])
        ma20 = safe_float(r["MA20"], current)
        ma60 = safe_float(r["MA60"], current)
        item = {
            "code": code, "name": name, "price": current,
            "rsi": safe_float(r["RSI14"], 50),
            "vr": safe_float(r["VOL_RATIO"], 1),
            "atr14": safe_float(r.get("ATR14"), 0),
            "atr_pct": (safe_float(r.get("ATR14"),0) / current * 100) if current else 0,
            "trading_value": safe_float(r.get("TRADING_VALUE"),0),
            "ret5": safe_float(r["RET5"], 0),
            "ret20": safe_float(r["RET20"], 0),
            "dist20": (current / ma20 - 1) * 100 if ma20 else 0,
            "above20": current >= ma20,
            "above60": current >= ma60,
            # 유망후보 가격가이드가 실제 최신 지표를 사용하도록 원본 행을 함께 보관
            "raw": r.to_dict(),
        }
        item["rs20"] = item["ret20"] - benchmark["ret20"]
        item["theme"] = radar_theme_for(code, name)
        item["stage"] = radar_stage_for(item["theme"])
        item["opportunity"] = radar_score(item)
        liq = item.get("trading_value",0)
        atrp = item.get("atr_pct",0)
        if liq >= 5e10: item["opportunity"] += 3
        elif liq >= 1e10: item["opportunity"] += 1
        if 1.0 <= atrp <= 6.0: item["opportunity"] += 2
        elif atrp > 12.0: item["opportunity"] -= 3
        item["opportunity"] = int(np.clip(item["opportunity"],0,100))
        item["overheat"] = radar_overheat_score(item)

        # 미래테마 × 시장레이더 교차검증
        # 레이더 단독 점수가 아니라 테마 생애주기·선행성·가격 위치까지 함께 평가합니다.
        try:
            bench20 = safe_float(benchmark.get("ret20"), 0)
            bench60 = safe_float(benchmark.get("ret60"), 0)
            theme_name, theme_members = _find_theme_for_etf(code)
            item["future_theme"] = theme_name if theme_members else "미래테마 미연결"
            item["future_theme_related"] = bool(theme_members)
            tscore = theme_score(theme_members, bench20, bench60) if theme_members else 0.0
            lc = _theme_lifecycle(theme_members, benchmark) if theme_members else {"score":0.0,"state":"관찰"}
            lead = leading_signal(r, bench20)
            zone = validated_price_zone(r)
            pscore = {"매수구간":100,"눌림대기":70,"추격금지":25,"무효":0}.get(zone.get("state"),0)
            # 레이더 점수는 '현재 시장조건'만 평가합니다.
            # 미래테마 점수는 최종타겟에서 별도로 결합하여 중복 가중치를 줄입니다.
            cross = (
                float(np.clip(lead.get("score",0),0,100)) * 0.40 +
                float(np.clip(item["opportunity"],0,100)) * 0.30 +
                float(np.clip(pscore,0,100)) * 0.20 +
                float(np.clip(lc.get("score",0),0,100)) * 0.10
            )
            # 현재 시장의 쇠퇴·과열은 레이더에서도 명시적으로 감점합니다.
            if lc.get("state") == "쇠퇴":
                cross -= 12
            elif lc.get("state") == "과열":
                cross -= 8
            if item["overheat"] >= 65:
                cross -= 10
            item["theme_score"] = round(float(tscore),1)
            item["lifecycle_score"] = round(float(lc.get("score",0)),1)
            item["lifecycle_state"] = lc.get("state","관찰")
            item["lead_score"] = round(float(lead.get("score",0)),1)
            item["price_zone"] = zone.get("state","확인")
            item["cross_score"] = int(np.clip(round(cross),0,100))
            if item["cross_score"] >= 80 and item["price_zone"] == "매수구간" and item["overheat"] < 65:
                item["cross_state"] = "🔥 최우선 후보"
            elif item["cross_score"] >= 70:
                item["cross_state"] = "🟢 우선 관찰"
            elif item["cross_score"] >= 55:
                item["cross_state"] = "🟡 확인 필요"
            else:
                item["cross_state"] = "⚪ 대기"
        except Exception:
            item.update({"theme_score":0.0,"lifecycle_score":0.0,"lifecycle_state":"관찰",
                         "lead_score":0.0,"price_zone":"확인","cross_score":0,"cross_state":"⚪ 대기",
                         "future_theme":"미래테마 미연결","future_theme_related":False})

        item["held"] = code in st.session_state.holdings
        rows.append(item)
    data = {"time": now, "rows": rows, "benchmark": benchmark, "target_key": target_key}
    st.session_state.radar_cache = data
    return data


def render_radar_card(item, mode, hide_title=False):
    # 시장 레이더 카드: 기회검색에서는 기존 후보선별을 유지하면서 실제 매매가격까지 표시.
    if mode == "🎯 유망후보":
        score = item.get("cross_score", item["opportunity"])
        state = item.get("cross_state", "기회 후보")
        badge = '<span class="radar-badge radar-badge-op">'+esc(state)+'</span>'
        title = "미래테마·선행성·시장레이더·가격구간을 모두 통과한 유망 후보"
    else:
        score = item["overheat"]
        badge = '<span class="radar-badge radar-badge-hot">과열 주의</span>'
        title = "단기 상승폭·RSI·이격·거래량을 함께 확인"
    held = '<span class="radar-badge radar-badge-hold">보유중</span>' if item["held"] else ''
    theme_text = f'{item["theme"]} · {item["stage"]}' if item["theme"] != "기타" else "테마 미분류"
    position = "20/60일선 위" if item["above20"] and item["above60"] else ("20일선 위 · 60일선 아래" if item["above20"] else "20일선 아래")
    guide_html = ""
    if mode == "🎯 유망후보":
        raw = item.get("raw") if isinstance(item, dict) else None
        if raw is None:
            raw = {}
        c = safe_float(raw.get("Close"), item.get("price", np.nan))
        ma20 = safe_float(raw.get("MA20"), c)
        ma60 = safe_float(raw.get("MA60"), c)
        low20 = safe_float(raw.get("LOW20"), c)
        if np.isfinite(c) and c > 0 and np.isfinite(ma20) and ma20 > 0 and np.isfinite(ma60) and ma60 > 0:
            support = max(low20, ma20 * 0.985)
            buy1 = ma20 * 1.025
            invalid = min(ma60 * 0.97, support * 0.97)
            if invalid <= 0: invalid = c * 0.92
            buy2 = (buy1 + invalid) / 2
            risk = max(buy1 - invalid, c * 0.05)
            tp1 = buy1 + risk
            tp2 = buy1 + risk * 2
            chase = ma20 * 1.07
            zone = item.get("price_zone", "확인")
            if zone == "매수구간": action = "🔥 지금 1차 매수 검토"
            elif zone == "눌림대기": action = "🟢 지금 추격하지 말고 눌림 2차 매수 대기"
            elif zone == "추격금지": action = "🔴 지금 매수 금지 · 눌림 대기"
            else: action = "🔴 매수 보류 · 가격구간 무효"
            guide_html = f'''<div class="radar-trade-title">실제 행동 / 가격</div>
  <div class="radar-action">{esc(action)}</div>
  <div class="radar-trade-grid">
    <div class="radar-trade-item"><div class="radar-label">1차 매수</div><div class="radar-trade-price">{money(buy1)}</div><div class="radar-trade-desc">20일선 + 2.5%</div></div>
    <div class="radar-trade-item"><div class="radar-label">2차 매수</div><div class="radar-trade-price">{money(buy2)}</div><div class="radar-trade-desc">눌림 구간</div></div>
    <div class="radar-trade-item"><div class="radar-label">추격 금지</div><div class="radar-trade-price">{money(chase)}</div><div class="radar-trade-desc">이상 매수 금지</div></div>
    <div class="radar-trade-item"><div class="radar-label">손절 / 무효</div><div class="radar-trade-price">{money(invalid)}</div><div class="radar-trade-desc">가격 이탈 시 재평가</div></div>
    <div class="radar-trade-item"><div class="radar-label">1차 익절</div><div class="radar-trade-price">{money(tp1)}</div><div class="radar-trade-desc">1R</div></div>
    <div class="radar-trade-item"><div class="radar-label">2차 익절</div><div class="radar-trade-price">{money(tp2)}</div><div class="radar-trade-desc">2R</div></div>
  </div>
  <div class="radar-follow">이후: <b>20일선 추적</b> · 1차/2차 익절 후 잔여 물량은 20일선 이탈 여부를 우선 확인</div>'''
    title_html = "" if hide_title else f'<div class="radar-title">{esc(item["name"])} · {esc(item["code"])}</div>'
    st.markdown(f'''<div class="radar-card">
  <div>{badge}{held}</div>
  {title_html}
  <div class="radar-sub">{esc(title)} · {esc(theme_text)}</div>
  <div style="display:flex;justify-content:space-between;align-items:center;margin-top:7px;">
     <div class="radar-score-block"><div class="radar-label">레이더 점수</div><div class="radar-score">{score}</div><div class="radar-score-code">{esc(item["code"])}</div></div>
    <div style="text-align:right"><div class="radar-label">현재가</div><div class="radar-value">{money(item["price"])}</div></div>
  </div>
  <div class="radar-grid">
    <div class="radar-metric"><div class="radar-label">테마</div><div class="radar-value">{item.get("theme_score",0):.0f}</div></div>
    <div class="radar-metric"><div class="radar-label">선행</div><div class="radar-value">{item.get("lead_score",0):.0f}</div></div>
    <div class="radar-metric"><div class="radar-label">가격</div><div class="radar-value">{esc(item.get("price_zone","확인"))}</div></div>
    <div class="radar-metric"><div class="radar-label">생애주기</div><div class="radar-value">{esc(item.get("lifecycle_state","관찰"))}</div></div>
  </div>
  <div class="radar-note">20일선 대비 <b>{item["dist20"]:+.1f}%</b> · {position} · 미래테마×레이더 교차점수 <b>{item.get("cross_score",0)}</b> · 최근 5일 <b>{item["ret5"]:+.1f}%</b> · RSI <b>{item["rsi"]:.1f}</b></div>
  <div class="radar-note">미래테마 연결: <b>{("🟢 실제 후보 · " + str(item.get("future_theme")) + " · 주식 순위 #" + str(item.get("future_theme_rank"))) if item.get("future_theme_selected") else (("🟡 연관테마 · " + str(item.get("future_theme"))) if item.get("future_theme_related") else "⚪ 현재 미래테마 엔진과 직접 연결되지 않음")}</b></div>
</div>''', unsafe_allow_html=True)

    if mode == "🎯 유망후보":
        with st.expander("💰 실제 행동 / 매수가·손절·익절 보기", expanded=False):
            if guide_html:
                st.markdown(guide_html, unsafe_allow_html=True)
            else:
                st.info("현재 가격 데이터로 행동 가격을 계산할 수 없습니다.")


def render_market_radar():
    st.markdown('<div class="hero"><div class="hero-name">🔥 시장 레이더</div><div class="hero-code">수급에 가까운 거래량 · 추세 · 상대강도 · 과열을 한 화면에서 확인</div></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("🔄 레이더 새로고침", use_container_width=True, key="radar_refresh"):
            st.session_state.radar_cache = None
            st.session_state.price_cache = {}
            st.rerun()
    with c2:
        st.caption("레이더는 내 주식 + 현재 미래테마 주식만 분석합니다. 결과는 5분 캐시로 재사용합니다.")
    radar_modes = ["🎯 유망후보", "⚠️ 과열검색", "🔄 테마순환"]
    # 모바일에서 radio의 선택 상태가 잘 보이지 않거나 터치가 씹히는 문제를 피하기 위해
    # Streamlit segmented_control을 우선 사용합니다. (구버전 Streamlit은 radio로 자동 fallback)
    if hasattr(st, "segmented_control"):
        mode = st.segmented_control(
            "레이더 모드",
            options=radar_modes,
            default=st.session_state.get("radar_mode", radar_modes[0]),
            key="radar_mode",
            label_visibility="collapsed"
        )
    else:
        mode = st.radio(
            "레이더 모드",
            radar_modes,
            horizontal=True,
            key="radar_mode",
            label_visibility="collapsed"
        )
    if not mode:
        mode = st.session_state.get("radar_mode", radar_modes[0])

    with st.spinner("시장 레이더 데이터를 계산하는 중입니다…"):
        data = build_radar_data()
    rows = data["rows"]
    if not rows:
        st.warning("레이더에 사용할 가격 데이터가 없습니다.")
        return
    if mode == "🔄 테마순환":
        st.markdown("### 테마순환")
        theme_rows = []
        for theme, stage in get_future_chain():
            members = [x for x in rows if x["theme"] == theme]
            if not members:
                continue
            vals5 = [x["ret5"] for x in members if np.isfinite(x["ret5"])]
            vals20 = [x["ret20"] for x in members if np.isfinite(x["ret20"])]
            valsvr = [x["vr"] for x in members if np.isfinite(x["vr"])]
            if not vals5 or not vals20 or not valsvr:
                continue
            avg5 = float(np.mean(vals5))
            avg20 = float(np.mean(vals20))
            avgvr = float(np.mean(valsvr))
            breadth = sum(1 for x in members if x["ret5"] >= 0) / len(members) * 100
            strength = avg5 * 0.45 + avg20 * 0.25 + (avgvr - 1) * 10 + breadth * 0.10
            theme_rows.append({"theme":theme,"stage":stage,"avg5":avg5,"avg20":avg20,"avgvr":avgvr,"breadth":breadth,"strength":strength,"n":len(members)})
        theme_rows.sort(key=lambda x:x["strength"], reverse=True)
        for x in theme_rows:
            cls = "positive" if x["avg5"] >= 0 else "negative"
            st.markdown(f'<div class="radar-card"><span class="radar-badge">{esc(x["stage"])}</span><div class="radar-title">{esc(x["theme"])}</div><div class="radar-sub">구성 {x["n"]}개 · 단기 상승 비율 {x["breadth"]:.0f}%</div><div class="radar-grid"><div class="radar-metric"><div class="radar-label">5일 평균</div><div class="radar-value {cls}">{x["avg5"]:+.2f}%</div></div><div class="radar-metric"><div class="radar-label">20일 평균</div><div class="radar-value">{x["avg20"]:+.2f}%</div></div><div class="radar-metric"><div class="radar-label">거래량</div><div class="radar-value">{x["avgvr"]:.2f}배</div></div><div class="radar-metric"><div class="radar-label">상승비율</div><div class="radar-value">{x["breadth"]:.0f}%</div></div></div></div>', unsafe_allow_html=True)
        st.caption("테마순환은 각 테마 구성 주식의 평균 수익률·거래량·상승 종목 비율을 이용한 상대 비교입니다.")
        return
    if mode == "🎯 유망후보":
        candidates = [x for x in rows if x["opportunity"] >= 55 and x["rsi"] < 72 and x["ret5"] < 8]
        candidates.sort(key=lambda x:(x.get("cross_score",0), x["opportunity"], x["rs20"], -x["ret5"]), reverse=True)
        st.markdown("### 🔥 아직 안 오른 강세 유망 후보")
        st.caption("미래테마가 살아 있고 → 테마가 확산되고 → 주식이 선행하고 → 시장레이더도 잡히면서 → 아직 단기 급등하지 않은 후보입니다. 아래에서 바로 매수·손절·익절 가격과 행동을 확인합니다.")
        if not candidates:
            st.info("현재 조건을 동시에 만족하는 후보가 없습니다.")
        for item in candidates[:10]:
            render_radar_card(item, mode)
    else:
        candidates = [x for x in rows if x["overheat"] >= 35]
        candidates.sort(key=lambda x:(x["overheat"], x["ret5"]), reverse=True)
        st.markdown("### 단기 과열 후보")
        st.caption("RSI·단기 상승률·20일선 이격·거래량 급증을 함께 확인합니다. 과열은 상승 지속 여부와 별개의 경고 신호입니다.")
        if not candidates:
            st.info("현재 과열 조건을 강하게 충족하는 주식이 없습니다.")
        for item in candidates[:10]:
            render_radar_card(item, mode)


# ============================================================
# 통합 백테스트 LAB
# ============================================================

BT_POOL = {
    "QQQ": "나스닥100",
    "XLK": "미국기술",
    "SMH": "반도체",
    "SOXX": "반도체",
    "BOTZ": "로봇AI",
    "ARKQ": "자동화로봇",
    "HACK": "사이버보안",
    "ITA": "방산",
    "PAVE": "인프라",
    "URA": "원전우라늄",
    "LIT": "2차전지",
    "XBI": "바이오",
    "INDA": "인도",
    "EWY": "한국",
    "EWJ": "일본",
    "EEM": "신흥국",
    "GLD": "금",
    "TLT": "미국장기채",
}

BT_BENCH = "SPY"

BT_THEME_GROUPS = {
    "미국기술": ["QQQ", "XLK"],
    "반도체": ["SMH", "SOXX"],
    "로봇AI": ["BOTZ", "ARKQ"],
    "위험선호": ["QQQ", "XLK", "SMH", "SOXX", "BOTZ", "ARKQ"],
    "방어자산": ["GLD", "TLT"],
    "글로벌": ["INDA", "EWY", "EWJ", "EEM"],
}

def bt_download_prices(tickers, start, end):
    symbols = list(dict.fromkeys(list(tickers) + [BT_BENCH]))
    x = yf.download(
        symbols,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        threads=True,
        group_by="ticker",
    )
    out = {}
    for t in symbols:
        try:
            if len(symbols) == 1:
                d = x.copy()
            else:
                d = x[t].copy()
            if not d.empty:
                d.columns = [str(c) for c in d.columns]
                out[t] = d
        except Exception:
            continue
    return out

def bt_indicators(d):
    d = d.copy()
    if "Close" not in d.columns:
        return pd.DataFrame()
    d["Close"] = pd.to_numeric(d["Close"], errors="coerce")
    d["Volume"] = pd.to_numeric(d.get("Volume", np.nan), errors="coerce")
    d = d.dropna(subset=["Close"])

    d["MA20"] = d["Close"].rolling(20).mean()
    d["MA60"] = d["Close"].rolling(60).mean()
    d["MA120"] = d["Close"].rolling(120).mean()
    d["MA200"] = d["Close"].rolling(200).mean()
    d["R5"] = d["Close"].pct_change(5) * 100
    d["R20"] = d["Close"].pct_change(20) * 100
    d["R60"] = d["Close"].pct_change(60) * 100
    d["R120"] = d["Close"].pct_change(120) * 100
    d["R252"] = d["Close"].pct_change(252) * 100
    d["HIGH252"] = d["Close"].rolling(252).max()
    d["VR"] = d["Volume"] / d["Volume"].rolling(20).mean()

    delta = d["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    d["RSI"] = 100 - 100 / (1 + rs)

    d["VOL20"] = d["Volume"].rolling(20).mean()
    d["LOW20"] = d["Close"].rolling(20).min()
    d["HIGH20"] = d["Close"].rolling(20).max()
    # TRUE-WF에서도 LIVE와 동일한 유동성/변동성 입력을 사용한다.
    tr = pd.concat([
        d["High"] - d["Low"],
        (d["High"] - d["Close"].shift(1)).abs(),
        (d["Low"] - d["Close"].shift(1)).abs()
    ], axis=1).max(axis=1)
    d["ATR14"] = tr.rolling(14).mean()
    d["ATR_PCT"] = d["ATR14"] / d["Close"].replace(0, np.nan) * 100
    d["TRADING_VALUE"] = d["Close"] * d["Volume"]
    d["TV20"] = d["TRADING_VALUE"].rolling(20).mean()
    return d

def bt_leading_signal(row, benchmark_ret20=0):
    current = float(row.get("Close", 0) or 0)
    ma20 = float(row.get("MA20", current) or current)
    ma60 = float(row.get("MA60", current) or current)
    ret5 = float(row.get("R5", 0) or 0)
    ret20 = float(row.get("R20", 0) or 0)
    vr = float(row.get("VR", 1) or 1)
    rsi = float(row.get("RSI", 50) or 50)

    dist20 = (current / ma20 - 1) * 100 if ma20 else 0
    rs20 = ret20 - benchmark_ret20
    accel = ret5 - ret20 / 4

    early_price = 92 if -1 <= dist20 <= 3 else 82 if dist20 <= 5 else 65 if dist20 < 8 else 35
    early_rsi = 92 if 48 <= rsi <= 62 else 84 if 43 <= rsi < 68 else 68 if rsi < 72 else 35
    flow = 92 if 1.10 <= vr <= 1.70 else 82 if 1.0 <= vr < 1.10 else 76 if 0.9 <= vr < 1.0 else 58 if vr < 2.2 else 38
    accel_score = 90 if 0.5 <= accel <= 5 else 78 if 0 <= accel < 0.5 else 68 if accel > 5 else 52
    rel = 88 if rs20 >= 6 else 80 if rs20 >= 3 else 70 if rs20 >= 0 else 48
    structure = 90 if current >= ma60 and ma20 >= ma60 else 78 if current >= ma60 else 55 if current >= ma20 else 35

    score = round(
        early_price * 0.22
        + early_rsi * 0.18
        + flow * 0.22
        + accel_score * 0.16
        + rel * 0.14
        + structure * 0.08
    )

    early_buy = score >= 72 and vr >= 1.05 and rsi < 70 and dist20 < 7 and rs20 >= -1

    return {
        "score": int(max(0, min(100, score))),
        "early_buy": bool(early_buy),
        "rs20": rs20,
        "dist20": dist20,
        "rsi": rsi,
        "vr": vr,
        "accel": accel,
    }

def bt_theme_score(theme_rows, bench_ret20=0, bench_ret60=0):
    if len(theme_rows) < 2:
        return None

    vals = []
    for r in theme_rows:
        if pd.isna(r.get("R20")) or pd.isna(r.get("R60")):
            continue
        sig = bt_leading_signal(r, bench_ret20)
        vals.append({
            "r20": float(r["R20"]),
            "r60": float(r["R60"]),
            "rs20": sig["rs20"],
            "rs60": float(r["R60"]) - bench_ret60,
            "vr": float(r.get("VR", 1) if pd.notna(r.get("VR", 1)) else 1),
            "ma60gap": ((float(r["Close"]) / float(r["MA60"]) - 1) * 100) if pd.notna(r.get("MA60")) and r["MA60"] else 0,
            "accel": sig["accel"],
            "rsi": sig["rsi"],
            "lead": sig["score"],
            "early": sig["early_buy"],
        })

    if len(vals) < 2:
        return None

    x = pd.DataFrame(vals)

    def clip_score(v, lo, hi):
        return float(np.clip((v - lo) / (hi - lo) * 100, 0, 100))

    r20 = clip_score(x["r20"].mean(), -10, 15)
    r60 = clip_score(x["r60"].mean(), -15, 30)
    rs20 = clip_score(x["rs20"].mean(), -10, 12)
    rs60 = clip_score(x["rs60"].mean(), -15, 20)
    vr = clip_score(x["vr"].mean(), 0.8, 2.0)
    breadth = float((x["r20"] > -2).mean() * 100)
    ma60 = clip_score(x["ma60gap"].mean(), -10, 15)
    accel = clip_score(x["accel"].mean(), -5, 6)
    rsi = 100 - abs(float(x["rsi"].mean()) - 58) * 2.5
    rsi = float(np.clip(rsi, 0, 100))

    score = (
        r20 * 0.15
        + r60 * 0.15
        + rs20 * 0.15
        + rs60 * 0.10
        + vr * 0.15
        + breadth * 0.15
        + ma60 * 0.05
        + accel * 0.05
        + rsi * 0.05
    )

    early_count = int(x["early"].sum())
    early_ratio = early_count / len(x)
    lead_avg = float(x["lead"].mean())

    # 기존 앱의 선행 테마 개념을 반영
    lead_theme = lead_avg * 0.55 + breadth * 0.25 + early_ratio * 100 * 0.20
    final = score * 0.70 + lead_theme * 0.30

    # 과열 패널티: 너무 많이 오른 테마는 미래테마 후보에서 감점
    heat = 0
    if float(x["rsi"].mean()) >= 75:
        heat += 12
    if float(x["r20"].mean()) >= 12:
        heat += 10
    if float(x["ma60gap"].mean()) >= 15:
        heat += 8

    final = float(np.clip(final - heat, 0, 100))

    if final >= 78:
        stage = "현재 주도"
    elif final >= 64:
        stage = "다음 수혜"
    elif final >= 50:
        stage = "관심 확대"
    else:
        stage = "초기 관심"

    return {
        "score": final,
        "stage": stage,
        "breadth": breadth,
        "lead_avg": lead_avg,
        "early_count": early_count,
        "members": len(x),
        "heat": heat,
    }

def bt_build_snapshot(all_data, date_i):
    bench = all_data.get(BT_BENCH)
    if bench is None or bench.empty:
        return None

    b = bench.iloc[: date_i + 1]
    if len(b) < 65:
        return None
    br = b.iloc[-1]
    bench_ret20 = float(br.get("R20", np.nan))
    bench_ret60 = float(br.get("R60", np.nan))
    if not np.isfinite(bench_ret20) or not np.isfinite(bench_ret60):
        return None

    theme_results = []
    for theme, members in BT_THEME_GROUPS.items():
        rows = []
        for t in members:
            d = all_data.get(t)
            if d is None or d.empty or len(d) <= date_i:
                continue
            r = d.iloc[date_i]
            if pd.isna(r.get("MA60")) or pd.isna(r.get("R20")) or pd.isna(r.get("R60")):
                continue
            rr = r.to_dict()
            rr["주식"] = t
            rows.append(rr)
        ts = bt_theme_score(rows, bench_ret20, bench_ret60)
        if ts:
            ts["theme"] = theme
            ts["rows"] = rows
            theme_results.append(ts)

    if not theme_results:
        return None

    theme_results.sort(key=lambda z: z["score"], reverse=True)
    top = theme_results[0]
    candidates = []
    for r in top["rows"]:
        sig = bt_leading_signal(r, bench_ret20)
        heat = 0
        c = float(r["Close"])
        ma20 = float(r["MA20"])
        rsi = sig["rsi"]
        dist20 = sig["dist20"]
        if rsi >= 78:
            heat += 32
        elif rsi >= 72:
            heat += 24
        elif rsi >= 68:
            heat += 12
        if float(r["R5"]) >= 10:
            heat += 25
        elif float(r["R5"]) >= 7:
            heat += 18
        elif float(r["R5"]) >= 5:
            heat += 10
        if dist20 >= 12:
            heat += 23
        elif dist20 >= 8:
            heat += 16
        elif dist20 >= 5:
            heat += 8
        if sig["vr"] >= 2:
            heat += 15
        elif sig["vr"] >= 1.5:
            heat += 10
        elif sig["vr"] >= 1.2:
            heat += 5
        candidates.append({"주식": r["주식"], "sig": sig, "heat": min(100, heat), "close": c, "ma20": ma20})

    if not candidates:
        return None

    # 선행점수 - 과열패널티를 적용해 테마 대표 주식을 선정
    candidates.sort(key=lambda z: z["sig"]["score"] - z["heat"] * 0.35, reverse=True)
    winner = candidates[0]

    return {
        "theme": top["theme"],
        "bt_theme_score": top["score"],
        "theme_stage": top["stage"],
        "winner": winner,
        "themes": theme_results,
    }

def bt_price_zone(r):
    c = float(r["Close"])
    ma20 = float(r["MA20"])
    ma60 = float(r["MA60"])
    low20 = float(r["LOW20"])

    # 매수 가능: MA20 부근/최근 저점 부근 + 추세 훼손 전
    support = max(low20, ma20 * 0.985)
    ideal_top = ma20 * 1.025
    invalid = min(ma60 * 0.97, support * 0.97)

    if c <= ideal_top and c >= invalid and c >= ma60 * 0.98:
        state = "매수구간"
    elif c < invalid:
        state = "무효"
    elif c > ma20 * 1.07:
        state = "추격금지"
    else:
        state = "눌림대기"

    return {"state": state, "support": support, "ideal_top": ideal_top, "invalid": invalid}

def bt_run_strategy_backtest(start, end, tickers, step_days=5):
    download_start = (pd.Timestamp(start) - pd.Timedelta(days=140)).strftime("%Y-%m-%d")
    download_end = (pd.Timestamp(end) + pd.Timedelta(days=80)).strftime("%Y-%m-%d")

    raw = bt_download_prices(tickers, download_start, download_end)
    data = {k: bt_indicators(v) for k, v in raw.items()}
    data = {k: v for k, v in data.items() if not v.empty}

    if BT_BENCH not in data:
        raise RuntimeError("SPY 벤치마크 데이터를 가져오지 못했습니다.")

    common = data[BT_BENCH].index
    for t in tickers:
        if t in data:
            common = common.intersection(data[t].index)
    common = common.sort_values()
    common = common[(common >= pd.Timestamp(start)) & (common <= pd.Timestamp(end))]

    rows = []
    dates_used = []

    # 5거래일 간격으로 검사하여 실행시간을 줄이고 과도한 중복신호를 완화
    for pos in range(0, len(common) - 61, max(1, step_days)):
        dt = common[pos]
        hist_pos = data[BT_BENCH].index.get_loc(dt)
        snap = bt_build_snapshot(data, hist_pos)
        if snap is None:
            continue

        winner = snap["winner"]
        t = winner["주식"]
        d = data[t]
        if hist_pos + 60 >= len(d):
            continue

        # 신호 당일 종가가 아닌 다음 거래일 종가 진입
        entry_i = hist_pos + 1
        entry = d.iloc[entry_i]
        entry_price = float(entry["Close"])
        if not np.isfinite(entry_price) or entry_price <= 0:
            continue

        # 전략 A: 선택된 테마의 대표 주식을 무조건 보유
        # 전략 B: 선행점수 >=72
        # 전략 C: 미래테마 + 선행 주식
        # 전략 D: 미래테마 + 선행 주식 + 가격구간
        sig = winner["sig"]
        zone = bt_price_zone(d.iloc[hist_pos])

        # A: 단순 테마 대표 주식
        a_ok = True
        # B: 개별 선행점수만 통과
        b_ok = sig["score"] >= 72 and sig["early_buy"]
        # C: 미래테마 + 선행 주식
        c_ok = snap["bt_theme_score"] >= 60 and b_ok
        # D: C + 가격구간
        d_ok = c_ok and zone["state"] == "매수구간"

        future = d.iloc[entry_i + 0 : entry_i + 60]
        if len(future) < 60:
            continue

        rec = {
            "날짜": dt.date(),
            "테마": snap["theme"],
            "테마점수": round(snap["bt_theme_score"], 1),
            "테마단계": snap["theme_stage"],
            "주식": t,
            "선행점수": sig["score"],
            "과열점수": winner["heat"],
            "가격상태": zone["state"],
            "매수가": entry_price,
            "A_단순테마": a_ok,
            "B_선행점수": b_ok,
            "C_미래테마선행": c_ok,
            "D_미래테마선행가격": d_ok,
        }

        for n in [5, 20, 60]:
            ret = (float(future.iloc[n - 1]["Close"]) / entry_price - 1) * 100
            dd = (float(future.iloc[:n]["Close"].min()) / entry_price - 1) * 100
            rec[f"{n}일수익"] = ret
            rec[f"{n}일최저낙폭"] = dd

        # 전략별 활성 여부에 따른 결과도 별도 저장
        rows.append(rec)
        dates_used.append(dt)

    return pd.DataFrame(rows), data

def bt_strategy_summary(r, flag, horizon):
    x = r.loc[r[flag], f"{horizon}일수익"].dropna()
    dd = r.loc[r[flag], f"{horizon}일최저낙폭"].dropna()
    if x.empty:
        return {
            "신호수": 0,
            "승률": np.nan,
            "평균수익": np.nan,
            "중앙값": np.nan,
            "평균낙폭": np.nan,
            "최고": np.nan,
            "최대손실": np.nan,
        }
    return {
        "신호수": len(x),
        "승률": (x > 0).mean() * 100,
        "평균수익": x.mean(),
        "중앙값": x.median(),
        "평균낙폭": dd.mean() if not dd.empty else np.nan,
        "최고": x.max(),
        "최대손실": x.min(),
    }

def bt_simulate_equity_curve(r, data, initial_cash=1_000_000, hold_days=20,
                          fee_per_side=0.0010, slippage_per_side=0.0005):
    """D 전략을 실제 포트폴리오처럼 1회 1포지션으로 순차 시뮬레이션.
    - 신호일 이후 다음 거래일 종가 진입
    - D 조건만 사용
    - 보유 중 새 신호는 무시
    - 기본은 hold_days 후 청산
    - 수수료+슬리피지를 매수/매도 각각 반영
    """
    if r is None or r.empty:
        return pd.DataFrame(), {}
    rr = r.loc[r["D_미래테마선행가격"] == True].copy()
    rr["날짜"] = pd.to_datetime(rr["날짜"])
    rr = rr.sort_values("날짜").reset_index(drop=True)

    cash = float(initial_cash)
    equity_rows = []
    trades = []
    next_available = pd.Timestamp.min
    n_days = 0
    wins = 0

    for _, sig in rr.iterrows():
        signal_date = pd.Timestamp(sig["날짜"])
        if signal_date < next_available:
            continue
        ticker = sig["주식"]
        d = data.get(ticker)
        if d is None or d.empty:
            continue
        idx = d.index.searchsorted(signal_date)
        entry_i = idx + 1
        exit_i = entry_i + int(hold_days) - 1
        if entry_i >= len(d) or exit_i >= len(d):
            continue
        entry_date = d.index[entry_i]
        exit_date = d.index[exit_i]
        entry_raw = float(d.iloc[entry_i]["Close"])
        exit_raw = float(d.iloc[exit_i]["Close"])
        if not np.isfinite(entry_raw) or not np.isfinite(exit_raw) or entry_raw <= 0:
            continue

        # 매수/매도 슬리피지를 불리하게 적용
        buy_price = entry_raw * (1 + slippage_per_side)
        sell_price = exit_raw * (1 - slippage_per_side)
        gross_ret = sell_price / buy_price - 1
        net_ret = gross_ret - fee_per_side * 2
        start_cash = cash
        cash = cash * (1 + net_ret)
        wins += int(net_ret > 0)
        n_days += max(1, (exit_date - entry_date).days)
        next_available = exit_date + pd.Timedelta(days=1)

        trades.append({
            "신호일": signal_date.date(), "진입일": entry_date.date(), "청산일": exit_date.date(),
            "테마": sig["테마"], "주식": ticker, "테마점수": sig["테마점수"],
            "선행점수": sig["선행점수"], "가격상태": sig["가격상태"],
            "진입가격": entry_raw, "청산가격": exit_raw,
            "순수익률": net_ret * 100, "거래후자산": cash,
        })
        equity_rows.append({"날짜": exit_date, "자산": cash})

    trades_df = pd.DataFrame(trades)
    curve = pd.DataFrame(equity_rows)
    if curve.empty:
        return curve, {"초기자산": initial_cash, "최종자산": initial_cash, "총수익률": 0.0,
                       "승률": np.nan, "거래수": 0, "최대낙폭": 0.0, "연환산": np.nan}
    curve = curve.sort_values("날짜").drop_duplicates("날짜", keep="last")
    curve["고점"] = curve["자산"].cummax()
    curve["낙폭"] = (curve["자산"] / curve["고점"] - 1) * 100
    final_cash = float(curve.iloc[-1]["자산"])
    total_ret = (final_cash / initial_cash - 1) * 100
    days = max(1, (pd.Timestamp(curve.iloc[-1]["날짜"]) - pd.Timestamp(curve.iloc[0]["날짜"])).days)
    annualized = ((final_cash / initial_cash) ** (365.25 / days) - 1) * 100 if final_cash > 0 else -100
    metrics = {
        "초기자산": initial_cash, "최종자산": final_cash, "총수익률": total_ret,
        "승률": (wins / len(trades_df) * 100) if len(trades_df) else np.nan,
        "거래수": len(trades_df), "최대낙폭": float(curve["낙폭"].min()), "연환산": annualized,
        "평균거래수익": float(trades_df["순수익률"].mean()) if not trades_df.empty else np.nan,
    }
    return curve, {**metrics, "trades": trades_df}

def bt_simulate_buy_hold(ticker, data, initial_cash=1_000_000):
    d = data.get(ticker)
    if d is None or d.empty:
        return pd.DataFrame(), {}
    x = d.dropna(subset=["Close"]).copy()
    if len(x) < 2:
        return pd.DataFrame(), {}
    p0 = float(x.iloc[0]["Close"])
    curve = pd.DataFrame({"날짜": x.index, "자산": initial_cash * x["Close"] / p0})
    curve["고점"] = curve["자산"].cummax()
    curve["낙폭"] = (curve["자산"] / curve["고점"] - 1) * 100
    final_cash = float(curve.iloc[-1]["자산"])
    days = max(1, (x.index[-1] - x.index[0]).days)
    annualized = ((final_cash / initial_cash) ** (365.25 / days) - 1) * 100
    return curve, {"초기자산": initial_cash, "최종자산": final_cash,
                   "총수익률": (final_cash / initial_cash - 1) * 100,
                   "최대낙폭": float(curve["낙폭"].min()), "연환산": annualized}

def bt_horizon_judgment_backtest_row(d, i):
    """시점 i까지의 정보만 사용해 장기/단기 판정을 만들고
    이후 20/60/120/250 거래일 성과를 별도로 기록한다.
    미래 데이터는 판정 계산에 사용하지 않는다.
    """
    if i < 200 or i + 250 >= len(d):
        return None

    r = d.iloc[i]
    close = float(r["Close"])
    ma60 = float(r["MA60"])
    ma120 = float(r["MA120"])
    ma200 = float(r["MA200"])
    r60 = float(r["R60"])
    r20 = float(r["R20"])
    r5 = float(r["R5"])
    rsi = float(r["RSI"])
    vr = float(r["VR"]) if np.isfinite(r["VR"]) else 1.0

    # 장기 보유 판단: 장기 추세 + 장기 모멘텀 + 장기 추세 훼손 여부
    long_score = 0
    long_score += 25 if close > ma200 else 0
    long_score += 20 if ma120 > ma200 else 0
    long_score += 15 if ma60 > ma120 else 0
    long_score += 15 if r60 > 10 else 8 if r60 > 0 else 0
    long_score += 15 if ma200 >= float(d.iloc[i-21]["MA200"]) else 0
    long_score += 10 if ma120 >= float(d.iloc[i-21]["MA120"]) else 0

    if long_score >= 80:
        long_state = "🟢 장기 핵심보유"
    elif long_score >= 65:
        long_state = "🟢 장기 보유"
    elif long_score >= 50:
        long_state = "🟡 추세 확인"
    else:
        long_state = "🔴 장기 재검토"

    # 단기 운용 판단: 최근 모멘텀 + MA20/60 + RSI + 거래량
    short_score = 0
    short_score += 25 if r5 > 0 else 0
    short_score += 20 if r20 > 2 else 10 if r20 > 0 else 0
    short_score += 20 if close > float(r["MA20"]) else 0
    short_score += 15 if float(r["MA20"]) > ma60 else 0
    short_score += 10 if 50 <= rsi <= 68 else 5 if 45 <= rsi <= 72 else 0
    short_score += 10 if vr >= 1.05 else 5 if vr >= 0.9 else 0

    if short_score >= 75:
        short_state = "🔥 단기 강세"
    elif short_score >= 60:
        short_state = "🟢 보유/운용"
    elif short_score >= 45:
        short_state = "🟡 매수 대기"
    else:
        short_state = "⚪ 단기 관찰"

    if long_score >= 80 and short_score >= 75:
        final_state = "🟢 장기 핵심보유 + 적극 운용"
    elif long_score >= 65 and short_score >= 60:
        final_state = "🟢 장기 보유 + 운용"
    elif long_score >= 65:
        final_state = "🟢 장기 보유 + 신규매수 대기"
    elif long_score < 50 and short_score < 50:
        final_state = "🔴 장기 재검토 + 단기 관찰"
    else:
        final_state = "🟡 혼합/추세 확인"

    entry_i = i + 1
    entry_price = float(d.iloc[entry_i]["Close"])
    out = {
        "신호일": d.index[i].date(),
        "진입일": d.index[entry_i].date(),
        "장기점수": long_score,
        "장기판정": long_state,
        "단기점수": short_score,
        "단기판정": short_state,
        "최종판정": final_state,
        "진입가": entry_price,
    }
    for h in [20, 60, 120, 250]:
        exit_price = float(d.iloc[entry_i + h - 1]["Close"])
        out[f"{h}일후수익률"] = (exit_price / entry_price - 1) * 100
    return out

def bt_run_horizon_backtest(start, end, tickers, step_days=5):
    download_start = (pd.Timestamp(start) - pd.Timedelta(days=420)).strftime("%Y-%m-%d")
    download_end = (pd.Timestamp(end) + pd.Timedelta(days=420)).strftime("%Y-%m-%d")
    raw = bt_download_prices(tickers, download_start, download_end)
    data = {k: bt_indicators(v) for k, v in raw.items()}
    rows = []
    for ticker in tickers:
        d = data.get(ticker)
        if d is None or len(d) < 451:
            continue
        dates = d.index[(d.index >= pd.Timestamp(start)) & (d.index <= pd.Timestamp(end))]
        for dt in dates[::max(1, int(step_days))]:
            i = d.index.get_loc(dt)
            rec = bt_horizon_judgment_backtest_row(d, i)
            if rec is not None:
                rec["주식"] = ticker
                rec["종목명"] = BT_POOL.get(ticker, ticker)
                rows.append(rec)
    return pd.DataFrame(rows), data

def bt_summarize_horizon_backtest(df):
    if df is None or df.empty:
        return pd.DataFrame()
    rows = []
    for state_col in ["장기판정", "단기판정", "최종판정"]:
        for state, g in df.groupby(state_col):
            rows.append({
                "구분": state_col,
                "판정": state,
                "건수": len(g),
                "20일 평균": g["20일후수익률"].mean(),
                "60일 평균": g["60일후수익률"].mean(),
                "120일 평균": g["120일후수익률"].mean(),
                "250일 평균": g["250일후수익률"].mean(),
                "20일 승률": (g["20일후수익률"] > 0).mean() * 100,
                "120일 승률": (g["120일후수익률"] > 0).mean() * 100,
                "250일 승률": (g["250일후수익률"] > 0).mean() * 100,
            })
    return pd.DataFrame(rows)

def bt_horizon_judgment_v2(d, i):
    """시점 i 이전 데이터만 사용.
    V1의 문제였던 '일시적 조정 = 장기 재검토'를 줄이고,
    장기 재검토는 구조적 추세 훼손이 확인될 때만 발생하도록 설계한다.
    """
    if i < 252 or i + 250 >= len(d):
        return None
    r=d.iloc[i]
    close=float(r["Close"]); ma60=float(r["MA60"]); ma120=float(r["MA120"]); ma200=float(r["MA200"])
    ma200_60=float(d.iloc[i-60]["MA200"]); ma120_20=float(d.iloc[i-20]["MA120"])
    r60=float(r["R60"]); r120=float(r["R120"])
    high252=float(r["HIGH252"]) if np.isfinite(r["HIGH252"]) else close
    dd252=(close/high252-1)*100 if high252>0 else 0

    # 장기 적합도: 한 번의 조정으로 급락하지 않도록 '구조'에 더 높은 가중치
    score=0
    score += 30 if close > ma200 else 0
    score += 20 if ma120 > ma200 else 0
    score += 15 if ma60 > ma120 else 0
    score += 15 if ma200 > ma200_60 else 0
    score += 10 if ma120 > ma120_20 else 0
    score += 5 if r120 > 0 else 0
    score += 5 if dd252 > -20 else 0

    # 구조적 훼손: 단순 조정이 아니라 여러 조건이 동시에 무너진 경우만 재검토
    structural_break = (
        close < ma200 and
        ma120 < ma200 and
        ma200 <= ma200_60 and
        r120 < 0
    )

    # 20거래일 이상 MA200 아래에 있었는지도 확인
    below20 = int((d["Close"].iloc[i-19:i+1] < d["MA200"].iloc[i-19:i+1]).sum()) >= 15
    structural_break = structural_break and below20

    if structural_break:
        long_state="🔴 장기 재검토"
    elif score >= 80:
        long_state="🟢 장기 핵심보유"
    elif score >= 65:
        long_state="🟢 장기 보유"
    else:
        long_state="🟡 추세 확인"

    # 단기 운용은 기존 V1과 동일한 구조를 유지
    r20=float(r["R20"]); r5=float(r["R5"]); rsi=float(r["RSI"])
    vr=float(r["VR"]) if np.isfinite(r["VR"]) else 1.0
    short_score=0
    short_score += 25 if r5 > 0 else 0
    short_score += 20 if r20 > 2 else 10 if r20 > 0 else 0
    short_score += 20 if close > float(r["MA20"]) else 0
    short_score += 15 if float(r["MA20"]) > ma60 else 0
    short_score += 10 if 50 <= rsi <= 68 else 5 if 45 <= rsi <= 72 else 0
    short_score += 10 if vr >= 1.05 else 5 if vr >= 0.9 else 0
    if short_score >= 75: short_state="🔥 단기 강세"
    elif short_score >= 60: short_state="🟢 보유/운용"
    elif short_score >= 45: short_state="🟡 매수 대기"
    else: short_state="⚪ 단기 관찰"

    if long_state == "🔴 장기 재검토":
        final_state="🔴 장기 재검토"
    elif long_state == "🟢 장기 핵심보유" and short_state == "🔥 단기 강세":
        final_state="🟢 장기 핵심보유 + 적극 운용"
    elif long_state in ("🟢 장기 핵심보유","🟢 장기 보유"):
        final_state="🟢 장기 보유 + 현재 추세 확인"
    else:
        final_state="🟡 장기 보유 가능 + 추세 확인"

    entry_i=i+1; entry_price=float(d.iloc[entry_i]["Close"])
    out={"신호일":d.index[i].date(),"진입일":d.index[entry_i].date(),
         "장기점수V2":score,"장기판정V2":long_state,"단기점수":short_score,
         "단기판정":short_state,"최종판정V2":final_state,"진입가":entry_price,
         "구조적훼손":structural_break,"252일고점대비":dd252}
    for h in [20,60,120,250]:
        ep=float(d.iloc[entry_i+h-1]["Close"])
        out[f"{h}일후수익률"]=(ep/entry_price-1)*100
    return out

def bt_run_horizon_backtest_v2(start,end,tickers,step_days=5):
    download_start=(pd.Timestamp(start)-pd.Timedelta(days=520)).strftime("%Y-%m-%d")
    download_end=(pd.Timestamp(end)+pd.Timedelta(days=420)).strftime("%Y-%m-%d")
    raw=bt_download_prices(tickers,download_start,download_end)
    data={k:bt_indicators(v) for k,v in raw.items()}
    rows=[]
    for ticker in tickers:
        d=data.get(ticker)
        if d is None or len(d)<520: continue
        dates=d.index[(d.index>=pd.Timestamp(start))&(d.index<=pd.Timestamp(end))]
        for dt in dates[::max(1,int(step_days))]:
            i=d.index.get_loc(dt); rec=bt_horizon_judgment_v2(d,i)
            if rec is not None:
                rec["주식"]=ticker; rec["종목명"]=BT_POOL.get(ticker,ticker); rows.append(rec)
    return pd.DataFrame(rows),data

def bt_summarize_horizon_v2(df):
    if df is None or df.empty: return pd.DataFrame()
    rows=[]
    for col in ["장기판정V2","단기판정","최종판정V2"]:
        for state,g in df.groupby(col):
            rows.append({"구분":col,"판정":state,"건수":len(g),
                "20일 평균":g["20일후수익률"].mean(),"60일 평균":g["60일후수익률"].mean(),
                "120일 평균":g["120일후수익률"].mean(),"250일 평균":g["250일후수익률"].mean(),
                "20일 승률":(g["20일후수익률"]>0).mean()*100,
                "120일 승률":(g["120일후수익률"]>0).mean()*100,
                "250일 승률":(g["250일후수익률"]>0).mean()*100})
    return pd.DataFrame(rows)

def bt_horizon_judgment_v3(d, i):
    """시점 i 이전 데이터만 사용.

    V3 원칙
    1) 장기적합성: 일시적 조정 때문에 장기보유 주식를 탈락시키지 않는다.
    2) 장기추세: 현재 가격이 MA200 아래인지보다 장기 추세의 방향을 우선한다.
    3) 구조적훼손: 장기수익률/MA200/MA120이 동시에 약해질 때만 경고한다.
    4) 현재운용: 단기 점수는 장기적합성과 별도로 판단한다.
    """
    if i < 252 or i + 250 >= len(d):
        return None
    r=d.iloc[i]
    close=float(r["Close"])
    ma20=float(r["MA20"]); ma60=float(r["MA60"])
    ma120=float(r["MA120"]); ma200=float(r["MA200"])
    ma200_60=float(d.iloc[i-60]["MA200"])
    ma120_60=float(d.iloc[i-60]["MA120"])
    r60=float(r["R60"]); r120=float(r["R120"]); r252=float(r["R252"])
    high252=float(r["HIGH252"]) if np.isfinite(r["HIGH252"]) else close
    dd252=(close/high252-1)*100 if high252>0 else 0

    # --------------------------------------------------------
    # A. 장기적합성
    # 핵심은 '현재 가격 위치'보다 장기 추세의 지속성.
    # --------------------------------------------------------
    suitability=0
    suitability += 25 if r252 > 15 else 18 if r252 > 0 else 8 if r252 > -15 else 0
    suitability += 20 if ma200 > ma200_60 else 0
    suitability += 15 if ma120 > ma120_60 else 0
    suitability += 15 if r120 > 10 else 10 if r120 > 0 else 4 if r120 > -10 else 0
    suitability += 15 if ma120 > ma200 else 7 if ma120 >= ma200*0.98 else 0
    suitability += 10 if r60 > 0 else 4 if r60 > -8 else 0

    # 장기적합성은 일시적 가격조정만으로 핵심보유를 박탈하지 않음.
    if suitability >= 75:
        fit_state="🟢 장기 핵심보유"
    elif suitability >= 55:
        fit_state="🟢 장기 보유"
    elif suitability >= 40:
        fit_state="🟡 장기 보유 + 추세 확인"
    else:
        fit_state="🔴 장기 적합성 재검토"

    # --------------------------------------------------------
    # B. 장기추세 상태
    # --------------------------------------------------------
    trend_score=0
    trend_score += 30 if ma200 > ma200_60 else 0
    trend_score += 25 if ma120 > ma120_60 else 0
    trend_score += 20 if ma120 > ma200 else 0
    trend_score += 15 if r120 > 0 else 0
    trend_score += 10 if close > ma200 else 0
    if trend_score >= 75:
        trend_state="🟢 장기 상승추세"
    elif trend_score >= 50:
        trend_state="🟡 장기 추세 확인"
    else:
        trend_state="🔴 장기 하락추세"

    # --------------------------------------------------------
    # C. 구조적 훼손
    # 단순 MA200 하회는 훼손으로 보지 않는다.
    # 장기수익률 음수 + MA200 하락 + MA120 하락 + MA120<MA200
    # 네 조건이 동시에 확인될 때만 장기 경고.
    # --------------------------------------------------------
    below20=int((d["Close"].iloc[i-19:i+1] < d["MA200"].iloc[i-19:i+1]).sum()) >= 15
    structural_break=(
        r252 < 0 and r120 < 0 and
        ma200 <= ma200_60 and ma120 <= ma120_60 and
        ma120 < ma200 and close < ma200 and below20
    )

    # --------------------------------------------------------
    # D. 현재 운용 — V2의 단기 구조 유지
    # --------------------------------------------------------
    r20=float(r["R20"]); r5=float(r["R5"]); rsi=float(r["RSI"])
    vr=float(r["VR"]) if np.isfinite(r["VR"]) else 1.0
    short_score=0
    short_score += 25 if r5 > 0 else 0
    short_score += 20 if r20 > 2 else 10 if r20 > 0 else 0
    short_score += 20 if close > ma20 else 0
    short_score += 15 if ma20 > ma60 else 0
    short_score += 10 if 50 <= rsi <= 68 else 5 if 45 <= rsi <= 72 else 0
    short_score += 10 if vr >= 1.05 else 5 if vr >= 0.9 else 0
    if short_score >= 75: short_state="🔥 단기 강세"
    elif short_score >= 60: short_state="🟢 보유/운용"
    elif short_score >= 45: short_state="🟡 매수 대기"
    else: short_state="⚪ 단기 관찰"

    # --------------------------------------------------------
    # E. 최종 행동
    # 장기적합성/장기추세/현재운용을 섞지 않고 순서대로 표시.
    # --------------------------------------------------------
    if structural_break:
        action="🔴 장기 추세 훼손 · 신규매수 중단"
    elif fit_state == "🟢 장기 핵심보유" and short_state == "🔥 단기 강세":
        action="🟢 핵심보유 + 적극 운용"
    elif fit_state in ("🟢 장기 핵심보유","🟢 장기 보유") and short_state in ("🟢 보유/운용","🔥 단기 강세"):
        action="🟢 장기보유 + 현재 운용"
    elif fit_state in ("🟢 장기 핵심보유","🟢 장기 보유"):
        action="🟡 장기보유 유지 + 신규매수 대기"
    else:
        action="🟡 추세 확인 후 운용"

    entry_i=i+1
    entry_price=float(d.iloc[entry_i]["Close"])
    out={
        "신호일":d.index[i].date(),"진입일":d.index[entry_i].date(),
        "장기적합성점수V3":suitability,"장기적합성V3":fit_state,
        "장기추세점수V3":trend_score,"장기추세V3":trend_state,
        "단기점수V3":short_score,"단기운용V3":short_state,
        "최종행동V3":action,"진입가":entry_price,
        "구조적훼손V3":structural_break,"252일고점대비":dd252,
    }
    for h in [20,60,120,250]:
        ep=float(d.iloc[entry_i+h-1]["Close"])
        out[f"{h}일후수익률"]=(ep/entry_price-1)*100
    return out

def bt_run_horizon_backtest_v3(start,end,tickers,step_days=5):
    download_start=(pd.Timestamp(start)-pd.Timedelta(days=520)).strftime("%Y-%m-%d")
    download_end=(pd.Timestamp(end)+pd.Timedelta(days=420)).strftime("%Y-%m-%d")
    raw=bt_download_prices(tickers,download_start,download_end)
    data={k:bt_indicators(v) for k,v in raw.items()}
    rows=[]
    for ticker in tickers:
        d=data.get(ticker)
        if d is None or len(d)<520: continue
        dates=d.index[(d.index>=pd.Timestamp(start))&(d.index<=pd.Timestamp(end))]
        for dt in dates[::max(1,int(step_days))]:
            i=d.index.get_loc(dt)
            rec=bt_horizon_judgment_v3(d,i)
            if rec is not None:
                rec["주식"]=ticker; rec["종목명"]=BT_POOL.get(ticker,ticker); rows.append(rec)
    return pd.DataFrame(rows),data

def bt_summarize_horizon_v3(df):
    if df is None or df.empty: return pd.DataFrame()
    rows=[]
    for col in ["장기적합성V3","장기추세V3","단기운용V3","최종행동V3"]:
        for state,g in df.groupby(col):
            rows.append({"구분":col,"판정":state,"건수":len(g),
                "20일 평균":g["20일후수익률"].mean(),"60일 평균":g["60일후수익률"].mean(),
                "120일 평균":g["120일후수익률"].mean(),"250일 평균":g["250일후수익률"].mean(),
                "20일 승률":(g["20일후수익률"]>0).mean()*100,
                "120일 승률":(g["120일후수익률"]>0).mean()*100,
                "250일 승률":(g["250일후수익률"]>0).mean()*100})
    return pd.DataFrame(rows)

def bt_horizon_judgment_v4(d, i):
    """시점 i 이전 데이터만 사용.

    V4 원칙
    - 장기적합성은 미래수익률을 예측하는 점수가 아니라 '계속 보유할 만한 구조인가'를 판단.
    - 단기 조정/고점 대비 하락만으로 장기 핵심보유를 박탈하지 않음.
    - 장기적합성에는 최근 1년 동안 장기추세가 유지된 '지속성'을 가장 크게 반영.
    - 현재 추세와 단기운용은 별도 축으로 판단.
    - 구조적 훼손만 실제 신규매수 중단 사유로 사용.
    """
    if i < 300 or i + 250 >= len(d): return None
    r=d.iloc[i]
    close=float(r["Close"]); ma20=float(r["MA20"]); ma60=float(r["MA60"])
    ma120=float(r["MA120"]); ma200=float(r["MA200"])
    ma200_60=float(d.iloc[i-60]["MA200"]); ma120_60=float(d.iloc[i-60]["MA120"])
    r20=float(r["R20"]); r60=float(r["R60"]); r120=float(r["R120"]); r252=float(r["R252"])
    high252=float(r["HIGH252"]) if np.isfinite(r["HIGH252"]) else close
    dd252=(close/high252-1)*100 if high252>0 else 0

    # ① 장기 지속성: 최근 252일 중 장기추세 위에서 머문 비율
    w=d.iloc[i-251:i+1]
    above200=float((w["Close"] >= w["MA200"]).mean())*100
    above120=float((w["Close"] >= w["MA120"]).mean())*100
    ma200_up=ma200 > ma200_60
    ma120_up=ma120 > ma120_60

    # ② 장기적합성: 현재 가격의 단기 위치보다 추세 지속성을 우선
    suitability=(
        above200*0.40
        + above120*0.20
        + (25 if ma200_up else 0)
        + (15 if r252>0 else 7 if r252>-15 else 0)
    )
    suitability=float(np.clip(suitability,0,100))

    if suitability >= 78:
        fit_state="🟢 장기 핵심보유"
    elif suitability >= 62:
        fit_state="🟢 장기 보유"
    elif suitability >= 48:
        fit_state="🟡 장기 보유 + 추세 확인"
    else:
        fit_state="🔴 장기 적합성 재검토"

    # ③ 장기추세: 현재 위치를 포함해 '지금의 추세'를 별도 판단
    trend_score=0
    trend_score += 30 if ma200_up else 0
    trend_score += 25 if ma120_up else 0
    trend_score += 20 if ma120 > ma200 else 0
    trend_score += 15 if r120 > 0 else 0
    trend_score += 10 if close > ma200 else 0
    if trend_score >= 75: trend_state="🟢 장기 상승추세"
    elif trend_score >= 50: trend_state="🟡 장기 조정/추세 확인"
    else: trend_state="🔴 장기 하락추세"

    # ④ 구조적 훼손: 지속성 자체가 무너졌을 때만
    structural_break=(
        above200 < 45 and above120 < 50 and
        r252 < 0 and r120 < 0 and
        not ma200_up and not ma120_up and
        ma120 < ma200 and close < ma200
    )

    # ⑤ 현재 운용 — 기존 단기 구조 유지
    rsi=float(r["RSI"]); vr=float(r["VR"]) if np.isfinite(r["VR"]) else 1.0
    short_score=0
    short_score += 25 if float(r["R5"]) > 0 else 0
    short_score += 20 if r20 > 2 else 10 if r20 > 0 else 0
    short_score += 20 if close > ma20 else 0
    short_score += 15 if ma20 > ma60 else 0
    short_score += 10 if 50 <= rsi <= 68 else 5 if 45 <= rsi <= 72 else 0
    short_score += 10 if vr >= 1.05 else 5 if vr >= 0.9 else 0
    if short_score >= 75: short_state="🔥 단기 강세"
    elif short_score >= 60: short_state="🟢 보유/운용"
    elif short_score >= 45: short_state="🟡 매수 대기"
    else: short_state="⚪ 단기 관찰"

    # ⑥ 최종 행동: 장기 보유 판단과 매매 타이밍을 분리
    if structural_break:
        action="🔴 구조적 추세 훼손 · 신규매수 중단"
    elif fit_state == "🟢 장기 핵심보유" and short_state == "🔥 단기 강세":
        action="🟢 핵심보유 + 적극 운용"
    elif fit_state in ("🟢 장기 핵심보유","🟢 장기 보유") and short_state in ("🟢 보유/운용","🔥 단기 강세"):
        action="🟢 장기보유 + 현재 운용"
    elif fit_state in ("🟢 장기 핵심보유","🟢 장기 보유"):
        action="🟡 장기보유 유지 + 신규매수 대기"
    elif trend_state == "🟡 장기 조정/추세 확인":
        action="🟡 장기 추세 확인 후 운용"
    else:
        action="⚪ 관찰"

    entry_i=i+1; entry_price=float(d.iloc[entry_i]["Close"])
    out={
        "신호일":d.index[i].date(),"진입일":d.index[entry_i].date(),
        "장기적합성점수V4":round(suitability,1),"장기적합성V4":fit_state,
        "장기추세점수V4":trend_score,"장기추세V4":trend_state,
        "단기점수V4":short_score,"단기운용V4":short_state,
        "장기추세지속성V4":round(above200,1),"구조적훼손V4":structural_break,
        "최종행동V4":action,"진입가":entry_price,"252일고점대비":dd252,
    }
    for h in [20,60,120,250]:
        ep=float(d.iloc[entry_i+h-1]["Close"]); out[f"{h}일후수익률"]=(ep/entry_price-1)*100
    return out

def bt_run_horizon_backtest_v4(start,end,tickers,step_days=5):
    download_start=(pd.Timestamp(start)-pd.Timedelta(days=560)).strftime("%Y-%m-%d")
    download_end=(pd.Timestamp(end)+pd.Timedelta(days=420)).strftime("%Y-%m-%d")
    raw=bt_download_prices(tickers,download_start,download_end)
    data={k:bt_indicators(v) for k,v in raw.items()}
    rows=[]
    for ticker in tickers:
        d=data.get(ticker)
        if d is None or len(d)<560: continue
        dates=d.index[(d.index>=pd.Timestamp(start))&(d.index<=pd.Timestamp(end))]
        for dt in dates[::max(1,int(step_days))]:
            i=d.index.get_loc(dt); rec=bt_horizon_judgment_v4(d,i)
            if rec is not None:
                rec["주식"]=ticker; rec["종목명"]=BT_POOL.get(ticker,ticker); rows.append(rec)
    return pd.DataFrame(rows),data

def bt_summarize_horizon_v4(df):
    if df is None or df.empty: return pd.DataFrame()
    rows=[]
    for col in ["장기적합성V4","장기추세V4","단기운용V4","최종행동V4"]:
        for state,g in df.groupby(col):
            rows.append({"구분":col,"판정":state,"건수":len(g),
                "20일 평균":g["20일후수익률"].mean(),"60일 평균":g["60일후수익률"].mean(),
                "120일 평균":g["120일후수익률"].mean(),"250일 평균":g["250일후수익률"].mean(),
                "20일 승률":(g["20일후수익률"]>0).mean()*100,
                "120일 승률":(g["120일후수익률"]>0).mean()*100,
                "250일 승률":(g["250일후수익률"]>0).mean()*100})
    return pd.DataFrame(rows)

def bt_trade_levels_v6(d, signal_i, entry_price):
    """신호일의 정보만 사용해 다음 거래일 진입 기준을 계산한다."""
    r = d.iloc[signal_i]
    c = float(r["Close"])
    ma20 = float(r["MA20"])
    ma60 = float(r["MA60"])
    low20 = float(r["LOW20"])
    support = max(low20, ma20 * 0.985)
    stop1 = min(ma60 * 0.97, support * 0.97)
    stop2 = min(stop1, low20 * 0.98)
    if not np.isfinite(stop1) or stop1 <= 0:
        stop1 = entry_price * 0.95
    if not np.isfinite(stop2) or stop2 <= 0:
        stop2 = stop1
    risk = max(entry_price - stop1, entry_price * 0.02)
    tp1 = entry_price + risk
    tp2 = entry_price + risk * 2.0
    return {"entry": entry_price, "support": support, "stop1": stop1,
            "stop2": stop2, "risk": risk, "tp1": tp1, "tp2": tp2,
            "signal_close": c}

def bt_simulate_cd_trade_v7(r, data, initial_cash=1_000_000,
                         fee_per_side=0.0010, slippage_per_side=0.0005,
                         max_hold_days=250):
    """V7 실전형 C/D 체결 시뮬레이션.

    C/D 선정 로직은 변경하지 않고 청산 구조만 개선한다.
    1) D 신호 다음 거래일 시가 진입.
    2) 1R에서 50% 익절.
    3) 2R에서 남은 물량의 50%(전체의 25%) 익절.
    4) 2R 도달 이후 남은 25%는 20일선 추적손절.
    5) 1차 손절은 보유물량의 50%, 2차 손절은 잔여물량 전량.
    6) 같은 봉에서 손절과 익절이 충돌하면 보수적으로 손절 우선.
    7) 최대 보유기간 종료 시 잔여물량 종가 청산.
    8) 보유 중 새 D 신호는 무시.
    """
    if r is None or r.empty:
        return pd.DataFrame(), {"거래수": 0}

    signals = r.loc[r["D_미래테마선행가격"] == True].copy()
    if signals.empty:
        return pd.DataFrame(), {"거래수": 0}
    signals["날짜"] = pd.to_datetime(signals["날짜"])
    signals = signals.sort_values("날짜").reset_index(drop=True)

    cash = float(initial_cash)
    trades = []
    next_available = pd.Timestamp.min

    def px(v, fallback):
        try:
            v = float(v)
            return v if np.isfinite(v) and v > 0 else fallback
        except Exception:
            return fallback

    for _, sig in signals.iterrows():
        signal_date = pd.Timestamp(sig["날짜"])
        if signal_date < next_available:
            continue

        ticker = sig["주식"]
        d = data.get(ticker)
        if d is None or d.empty:
            continue

        idx = d.index.searchsorted(signal_date)
        if idx >= len(d) or d.index[idx] != signal_date:
            continue
        entry_i = idx + 1
        if entry_i >= len(d):
            continue

        entry_row = d.iloc[entry_i]
        raw_entry = px(entry_row.get("Open", np.nan),
                       px(entry_row.get("Close", np.nan), np.nan))
        if not np.isfinite(raw_entry) or raw_entry <= 0:
            continue

        entry_fill = raw_entry * (1 + slippage_per_side)
        lv = bt_trade_levels_v6(d, idx, entry_fill)
        stop1 = float(lv["stop1"])
        stop2 = float(lv["stop2"])
        tp1 = float(lv["tp1"])
        tp2 = float(lv["tp2"])

        # 전체 포지션을 1.0으로 두고 부분청산한다.
        remaining = 1.0
        realized = 0.0
        tp1_hit = False
        tp2_hit = False
        stop1_hit = False
        stop2_hit = False
        trail_hit = False
        trail_active = False
        exit_reason = ""

        last_i = min(len(d) - 1, entry_i + int(max_hold_days) - 1)
        exit_i = last_i

        def net_return(fill, weight):
            # entry_fill은 진입 슬리피지를 이미 반영.
            # 각 부분청산에는 청산 슬리피지와 양쪽 비용을 보수적으로 반영.
            return weight * ((fill / entry_fill - 1) - fee_per_side * 2)

        for j in range(entry_i, last_i + 1):
            bar = d.iloc[j]
            close_j = px(bar.get("Close", np.nan), np.nan)
            high_j = px(bar.get("High", np.nan), close_j)
            low_j = px(bar.get("Low", np.nan), close_j)
            ma20_j = px(bar.get("MA20", np.nan), np.nan)
            if not np.isfinite(close_j):
                continue

            # ① 2R 이후에는 구조적 손절보다 20일선 추적손절을 우선 적용한다.
            #    2R 이후 남은 25%는 별도의 runner로 취급한다.
            #    같은 봉에서 추적손절과 다른 손절이 함께 닿으면 더 높은 가격의
            #    추적손절이 먼저 체결되는 것으로 처리한다.
            if trail_active and remaining > 0 and np.isfinite(ma20_j) and ma20_j > 0:
                trail_stop = ma20_j * 0.99
                if low_j <= trail_stop:
                    fill = trail_stop * (1 - slippage_per_side)
                    realized += net_return(fill, remaining)
                    trail_hit = True
                    exit_reason = "20일선 추적손절"
                    remaining = 0.0
                    exit_i = j
                    break

            # ② 추적손절이 활성화되기 전에는 구조적 손절을 적용한다.
            if (not trail_active) and remaining > 0 and low_j <= stop2:
                fill = stop2 * (1 - slippage_per_side)
                realized += net_return(fill, remaining)
                stop2_hit = True
                exit_reason = "2차 손절"
                remaining = 0.0
                exit_i = j
                break

            if (not trail_active) and remaining > 0 and (not stop1_hit) and low_j <= stop1:
                fill = stop1 * (1 - slippage_per_side)
                cut = min(0.5, remaining)
                realized += net_return(fill, cut)
                remaining -= cut
                stop1_hit = True
                # 같은 봉의 TP는 인정하지 않는다.
                if j == last_i and remaining > 0:
                    fill = close_j * (1 - slippage_per_side)
                    realized += net_return(fill, remaining)
                    remaining = 0.0
                    exit_reason = "1차 손절·기간만료"
                    exit_i = j
                    break
                continue

            # ③ 1R: 최초 물량의 절반 익절.
            #    같은 봉에서 2R까지 도달해도 실제 가격 경로상 1R이 먼저 체결된다.
            if remaining > 0 and (not tp1_hit) and high_j >= tp1:
                fill = tp1 * (1 - slippage_per_side)
                cut = min(0.5, remaining)
                realized += net_return(fill, cut)
                remaining -= cut
                tp1_hit = True

            # ④ 2R: 남은 물량의 절반(초기 포지션 기준 25%)만 익절.
            #    2R 이후 잔여 25%는 다음 봉부터 20일선 추적손절을 적용한다.
            if remaining > 0 and tp1_hit and (not tp2_hit) and high_j >= tp2:
                fill = tp2 * (1 - slippage_per_side)
                cut = min(0.25, remaining)
                realized += net_return(fill, cut)
                remaining -= cut
                tp2_hit = True
                trail_active = remaining > 0
                # 같은 봉의 추적손절은 장중 순서를 알 수 없으므로 다음 봉부터 적용.
                continue

            if remaining <= 0:
                exit_reason = "2R 익절" if tp2_hit else "1R 익절"
                exit_i = j
                break

            # ⑤ 최대 보유기간 종료.
            if j == last_i and remaining > 0:
                fill = close_j * (1 - slippage_per_side)
                realized += net_return(fill, remaining)
                remaining = 0.0
                if trail_active:
                    exit_reason = "추적손절·기간만료"
                elif tp2_hit:
                    exit_reason = "2R 후 기간만료"
                elif tp1_hit:
                    exit_reason = "1R 후 기간만료"
                else:
                    exit_reason = "기간만료"
                exit_i = j
                break

        cash *= (1 + realized)
        exit_date = d.index[exit_i]
        next_available = exit_date + pd.Timedelta(days=1)

        trades.append({
            "신호일": signal_date.date(),
            "진입일": d.index[entry_i].date(),
            "청산일": exit_date.date(),
            "주식": ticker,
            "테마": sig["테마"],
            "테마점수": float(sig["테마점수"]),
            "선행점수": int(sig["선행점수"]),
            "진입가": entry_fill,
            "1차익절": tp1,
            "2차익절": tp2,
            "1차손절": stop1,
            "2차손절": stop2,
            "R": lv["risk"],
            "1R도달": tp1_hit,
            "2R도달": tp2_hit,
            "1차손절도달": stop1_hit,
            "2차손절도달": stop2_hit,
            "20일선추적손절": trail_hit,
            "청산사유": exit_reason,
            "보유거래일": int(exit_i - entry_i + 1),
            "순수익률": realized * 100,
            "거래후자산": cash,
        })

    td = pd.DataFrame(trades)
    if td.empty:
        return td, {
            "초기자산": initial_cash, "최종자산": initial_cash,
            "총수익률": 0.0, "거래수": 0, "승률": np.nan,
            "최대낙폭": 0.0, "연환산": np.nan,
        }

    curve = td[["청산일", "거래후자산"]].copy()
    curve["청산일"] = pd.to_datetime(curve["청산일"])
    curve["고점"] = curve["거래후자산"].cummax()
    curve["낙폭"] = (curve["거래후자산"] / curve["고점"] - 1) * 100

    final_cash = float(td.iloc[-1]["거래후자산"])
    total_ret = (final_cash / initial_cash - 1) * 100
    days = max(1, (curve["청산일"].iloc[-1] - curve["청산일"].iloc[0]).days)
    annualized = ((final_cash / initial_cash) ** (365.25 / days) - 1) * 100 if final_cash > 0 else -100

    wins = int((td["순수익률"] > 0).sum())
    avg_win = td.loc[td["순수익률"] > 0, "순수익률"].mean()
    avg_loss = td.loc[td["순수익률"] <= 0, "순수익률"].mean()
    gross_profit = td.loc[td["순수익률"] > 0, "순수익률"].sum()
    gross_loss = -td.loc[td["순수익률"] < 0, "순수익률"].sum()

    metrics = {
        "초기자산": initial_cash,
        "최종자산": final_cash,
        "총수익률": total_ret,
        "연환산": annualized,
        "거래수": len(td),
        "승률": wins / len(td) * 100,
        "평균승리": avg_win,
        "평균손실": avg_loss,
        "손익비": (abs(avg_win / avg_loss) if pd.notna(avg_win) and pd.notna(avg_loss) and avg_loss != 0 else np.nan),
        "ProfitFactor": (gross_profit / gross_loss if gross_loss > 0 else np.inf),
        "기대값": td["순수익률"].mean(),
        "최대낙폭": float(curve["낙폭"].min()),
        "1R도달률": td["1R도달"].mean() * 100,
        "2R도달률": td["2R도달"].mean() * 100,
        "1차손절률": td["1차손절도달"].mean() * 100,
        "2차손절률": td["2차손절도달"].mean() * 100,
        "추적손절률": td["20일선추적손절"].mean() * 100,
        "평균보유일": td["보유거래일"].mean(),
    }
    return td, metrics

def bt_market_filter_pass(signal_date, spy, mode):
    if spy is None or spy.empty:
        return False
    try:
        dt = pd.Timestamp(signal_date)
        idx = spy.index.searchsorted(dt)
        if idx >= len(spy) or spy.index[idx] != dt:
            return False
        r = spy.iloc[idx]
        close = float(r.get("Close", np.nan))
        ma60 = float(r.get("MA60", np.nan))
        ma120 = float(r.get("MA120", np.nan))
        ma200 = float(r.get("MA200", np.nan))
        r20 = float(r.get("R20", r.get("RET20", np.nan)))
        r60 = float(r.get("R60", r.get("RET60", np.nan)))
        if not all(np.isfinite(v) for v in [close, ma60, ma120, ma200, r20, r60]):
            return False
        if mode == "완화":
            return close >= ma120 and r20 >= -3.0
        if mode == "기본":
            return close >= ma60 and r20 >= 0.0
        if mode == "엄격":
            return close >= ma200 and r60 >= 0.0
        return True
    except Exception:
        return False

def bt_filtered_signal_rows(r, data, mode):
    if r is None or r.empty or mode == "기본 V7":
        return r.copy() if r is not None else pd.DataFrame()
    spy = data.get(BT_BENCH)
    if spy is None or spy.empty:
        return pd.DataFrame(columns=r.columns)
    x = r.copy()
    x["시장필터통과"] = x["날짜"].apply(lambda d: bt_market_filter_pass(d, spy, mode))
    return x[x["시장필터통과"] == True].copy()

def bt_run_market_filter_comparison(r, data, initial_cash=1_000_000, fee=0.001, slip=0.0005, hold=250):
    rows = []
    for mode in ["기본 V7", "완화", "기본", "엄격"]:
        rr = bt_filtered_signal_rows(r, data, mode)
        trades, m = bt_simulate_cd_trade_v7(rr, data, initial_cash=initial_cash,
                                         fee_per_side=fee, slippage_per_side=slip,
                                         max_hold_days=hold)
        rows.append({
            "시장필터": mode,
            "신호수": int((rr["D_미래테마선행가격"] == True).sum()) if not rr.empty and "D_미래테마선행가격" in rr else 0,
            "필터통과신호": int(len(rr)),
            "거래수": int(m.get("거래수", 0)),
            "최종자산": float(m.get("최종자산", initial_cash)),
            "총수익률": float(m.get("총수익률", 0)),
            "승률": float(m.get("승률", 0)),
            "MDD": float(m.get("최대낙폭", 0)),
            "평균손익": float(m.get("기대값", 0)),
            "2차손절률": float(m.get("2차손절률", 0)),
            "추적손절률": float(m.get("추적손절률", 0)),
        })
    return pd.DataFrame(rows)

def bt_strict_market_pass_with_condition(signal_date, row, data, condition):
    spy = data.get(BT_BENCH)
    if spy is None or spy.empty or row is None:
        return False
    try:
        dt = pd.Timestamp(signal_date)
        idx = spy.index.searchsorted(dt)
        if idx >= len(spy) or spy.index[idx] != dt:
            return False
        sr = spy.iloc[idx]
        if not all(np.isfinite(float(sr.get(k, np.nan))) for k in ["Close","MA200","R60"]):
            return False
        # 현재 채택 후보인 엄격 시장환경 필터는 고정한다.
        if float(sr["Close"]) < float(sr["MA200"]) or float(sr["R60"]) < 0:
            return False

        if condition == "A · 엄격 기준선":
            return True

        close = float(row.get("Close", np.nan))
        ma20 = float(row.get("MA20", np.nan))
        ma60 = float(row.get("MA60", np.nan))
        r5 = float(row.get("R5", np.nan))
        r20 = float(row.get("R20", np.nan))
        vr = float(row.get("VR", np.nan))
        rsi = float(row.get("RSI", np.nan))
        vals = [close, ma20, ma60, r5, r20, vr, rsi]
        if not all(np.isfinite(v) for v in vals):
            return False

        if condition == "B · 개별 주식 추세확인":
            # 기존 C/D의 선행진입을 지나치게 훼손하지 않는 완화형 개별추세 확인.
            # 진입 직전 종가가 MA20/MA60 부근에 있고 중기수익률이 급락 상태가 아닌지만 확인한다.
            trend_ok = (
                close >= ma60 * 0.98
                and ma20 >= ma60 * 0.98
                and r20 >= -3.0
            )
            return bool(trend_ok)

        if condition == "C · 거래량/모멘텀 확인":
            # 거래량·RSI가 정상 범위이고 단기 급락 상태만 제외한다.
            flow_ok = 0.90 <= vr <= 2.20
            momentum_ok = 40 <= rsi <= 72 and r5 >= -5.0
            return bool(flow_ok and momentum_ok)

        return False
    except Exception:
        return False

def bt_run_3condition_comparison(r, data, initial_cash=1_000_000, fee=0.001, slip=0.0005, hold=250):
    rows = []
    trade_details = {}
    names = ["A · 엄격 기준선", "B · 개별 주식 추세확인", "C · 거래량/모멘텀 확인"]

    for name in names:
        selected = []
        if r is not None and not r.empty:
            for _, rr in r.iterrows():
                if not bool(rr.get("D_미래테마선행가격", False)):
                    continue
                if bt_strict_market_pass_with_condition(rr.get("날짜"), rr, data, name):
                    selected.append(rr)
        rrdf = pd.DataFrame(selected, columns=r.columns if r is not None else [])
        trades, m = bt_simulate_cd_trade_v7(
            rrdf, data,
            initial_cash=initial_cash,
            fee_per_side=fee,
            slippage_per_side=slip,
            max_hold_days=hold,
        )
        if trades is None:
            trades = pd.DataFrame()
        td = trades.copy()
        if not td.empty:
            td.insert(0, "추가조건", name)
        trade_details[name] = td
        rows.append({
            "추가조건": name,
            "통과신호": len(rrdf),
            "거래수": int(m.get("거래수", 0)),
            "최종자산": float(m.get("최종자산", initial_cash)),
            "총수익률": float(m.get("총수익률", 0)),
            "승률": float(m.get("승률", 0)),
            "MDD": float(m.get("최대낙폭", 0)),
            "평균손익": float(m.get("기대값", 0)),
            "2차손절률": float(m.get("2차손절률", 0)),
            "추적손절률": float(m.get("추적손절률", 0)),
        })
    return pd.DataFrame(rows), trade_details


# ============================================================
# STOCK RADAR 통합 백테스트 LAB
# 기존 실시간 STOCK RADAR 로직은 유지하고, 백테스트 엔진만 별도 네임스페이스로 연결한다.
# ============================================================


# ============================================================
# 조건 기여도 비교 백테스트
# ============================================================

def bt_condition_contribution_flags(r, data):
    """동일한 D 기준에서 각 추가조건의 독립/복합 기여도를 계산한다.
    - BASE = 미래테마 + 선행점수 + 가격구간(D)
    - TREND = Close > MA20 > MA60 and R20 > 0
    - MOMVOL = VR 1.05~2.50 and RSI 50~72 and R5 > 0
    - MARKET = SPY Close >= MA60, Close >= MA120, R20 >= 0
    모든 조건은 신호일의 정보만 사용한다.
    """
    if r is None or r.empty:
        return pd.DataFrame()
    x=r.copy()
    if "D_미래테마선행가격" not in x.columns:
        return pd.DataFrame()

    trend=[]; momvol=[]; market=[]
    spy=data.get(BT_BENCH)
    if spy is not None and not spy.empty:
        spy=bt_indicators(spy.copy()) if "MA120" not in spy.columns else spy

    for _, row in x.iterrows():
        ticker=row.get("주식")
        dt=pd.Timestamp(row.get("날짜"))
        d=data.get(ticker)
        tr=mv=False
        if d is not None and not d.empty:
            pos=d.index.searchsorted(dt)
            if pos < len(d) and d.index[pos] == dt:
                z=d.iloc[pos]
                close=float(z.get("Close",np.nan)); ma20=float(z.get("MA20",np.nan)); ma60=float(z.get("MA60",np.nan))
                r20=float(z.get("R20",np.nan)); r5=float(z.get("R5",np.nan)); rsi=float(z.get("RSI",np.nan))
                vr=float(z.get("VR",np.nan)) if np.isfinite(z.get("VR",np.nan)) else np.nan
                tr=bool(np.isfinite(close) and np.isfinite(ma20) and np.isfinite(ma60) and np.isfinite(r20) and close>ma20>ma60 and r20>0)
                mv=bool(np.isfinite(vr) and np.isfinite(rsi) and np.isfinite(r5) and 1.05<=vr<=2.50 and 50<=rsi<=72 and r5>0)
        mk=False
        if spy is not None and not spy.empty:
            pos=spy.index.searchsorted(dt)
            if pos < len(spy) and spy.index[pos] == dt:
                z=spy.iloc[pos]
                close=float(z.get("Close",np.nan)); ma60=float(z.get("MA60",np.nan)); ma120=float(z.get("MA120",np.nan)); r20=float(z.get("R20",np.nan))
                mk=bool(np.isfinite(close) and np.isfinite(ma60) and np.isfinite(ma120) and np.isfinite(r20) and close>=ma60 and close>=ma120 and r20>=0)
        trend.append(tr); momvol.append(mv); market.append(mk)

    x["조건_추세"]=trend
    x["조건_거래량모멘텀"]=momvol
    x["조건_시장환경"]=market
    base=x["D_미래테마선행가격"].fillna(False).astype(bool)
    x["BASE"]=base
    x["BASE_추세"]=base & x["조건_추세"]
    x["BASE_거래량모멘텀"]=base & x["조건_거래량모멘텀"]
    x["BASE_시장환경"]=base & x["조건_시장환경"]
    x["BASE_추세_거래량모멘텀"]=base & x["조건_추세"] & x["조건_거래량모멘텀"]
    x["BASE_추세_거래량모멘텀_시장환경"]=base & x["조건_추세"] & x["조건_거래량모멘텀"] & x["조건_시장환경"]
    return x


def bt_simulate_contribution_strategy(r, data, flag, initial_cash=1_000_000, hold_days=60,
                                      fee_per_side=0.0010, slippage_per_side=0.0005):
    """조건 기여도 비교 전용 동일 체결엔진.
    모든 전략에 동일하게 다음 거래일 시가 진입/고정 보유기간/비용을 적용한다.
    신호가 중복되면 보유 종료일까지 새 신호를 무시한다.
    """
    if r is None or r.empty or flag not in r.columns:
        return pd.DataFrame(), {"거래수":0,"총수익률":0.0,"CAGR":np.nan,"MDD":0.0,"승률":np.nan,"Profit Factor":np.nan}
    sigs=r.loc[r[flag].fillna(False).astype(bool)].copy()
    if sigs.empty:
        return pd.DataFrame(), {"거래수":0,"총수익률":0.0,"CAGR":np.nan,"MDD":0.0,"승률":np.nan,"Profit Factor":np.nan}
    sigs["날짜"]=pd.to_datetime(sigs["날짜"])
    sigs=sigs.sort_values("날짜").reset_index(drop=True)
    cash=float(initial_cash); peak=float(initial_cash); next_available=pd.Timestamp.min
    trades=[]; curve=[]
    for _,sig in sigs.iterrows():
        signal_date=pd.Timestamp(sig["날짜"])
        if signal_date < next_available: continue
        d=data.get(sig["주식"])
        if d is None or d.empty: continue
        idx=d.index.searchsorted(signal_date)
        if idx>=len(d) or d.index[idx]!=signal_date: continue
        entry_i=idx+1; exit_i=entry_i+int(hold_days)-1
        if exit_i>=len(d): continue
        er=d.iloc[entry_i]; xr=d.iloc[exit_i]
        entry=float(er.get("Open",er.get("Close",np.nan))); exitp=float(xr.get("Close",np.nan))
        if not np.isfinite(entry) or not np.isfinite(exitp) or entry<=0: continue
        buy=entry*(1+slippage_per_side); sell=exitp*(1-slippage_per_side)
        net=(sell/buy-1)-fee_per_side*2
        before=cash; cash*=1+net; peak=max(peak,cash)
        curve.append({"날짜":d.index[exit_i],"자산":cash})
        trades.append({"신호일":signal_date.date(),"진입일":d.index[entry_i].date(),"청산일":d.index[exit_i].date(),"주식":sig["주식"],"순수익률":net*100,"거래후자산":cash})
        next_available=d.index[exit_i]+pd.Timedelta(days=1)
    td=pd.DataFrame(trades); cv=pd.DataFrame(curve)
    if cv.empty:
        return td,{"거래수":0,"총수익률":0.0,"CAGR":np.nan,"MDD":0.0,"승률":np.nan,"Profit Factor":np.nan}
    cv=cv.sort_values("날짜").drop_duplicates("날짜",keep="last")
    cv["고점"]=cv["자산"].cummax(); cv["낙폭"]=(cv["자산"]/cv["고점"]-1)*100
    final=float(cv.iloc[-1]["자산"]); total=(final/initial_cash-1)*100
    days=max(1,(pd.Timestamp(cv.iloc[-1]["날짜"])-pd.Timestamp(cv.iloc[0]["날짜"])).days)
    cagr=((final/initial_cash)**(365.25/days)-1)*100 if final>0 else -100
    wins=int((td["순수익률"]>0).sum()); losses=td.loc[td["순수익률"]<0,"순수익률"]
    gains=float(td.loc[td["순수익률"]>0,"순수익률"].sum()); loss_abs=float(abs(losses.sum()))
    pf=(gains/loss_abs) if loss_abs>0 else np.inf if gains>0 else np.nan
    return td,{"거래수":len(td),"총수익률":total,"CAGR":cagr,"MDD":float(cv["낙폭"].min()),"승률":wins/len(td)*100 if len(td) else np.nan,"Profit Factor":pf,"평균거래수익":float(td["순수익률"].mean()) if not td.empty else np.nan}


def bt_annual_contribution(trades):
    if trades is None or trades.empty: return pd.DataFrame()
    t=trades.copy(); t["청산일"]=pd.to_datetime(t["청산일"]); t["연도"]=t["청산일"].dt.year
    rows=[]
    for y,g in t.groupby("연도"):
        wins=(g["순수익률"]>0).sum(); losses=g.loc[g["순수익률"]<0,"순수익률"]
        gain=g.loc[g["순수익률"]>0,"순수익률"].sum(); loss=abs(losses.sum())
        rows.append({"연도":int(y),"거래수":len(g),"승률":wins/len(g)*100 if len(g) else np.nan,"평균거래수익":g["순수익률"].mean(),"누적거래수익률":g["순수익률"].sum(),"Profit Factor":gain/loss if loss>0 else np.inf if gain>0 else np.nan})
    return pd.DataFrame(rows)


def bt_run_condition_contribution(r,data,initial_cash=1_000_000,hold_days=60,fee=0.001,slip=0.0005):
    x=bt_condition_contribution_flags(r,data)
    if x.empty: return pd.DataFrame(),{},{}
    flags=[
        ("BASE","D 기본"),
        ("BASE_추세","BASE + 주식 추세"),
        ("BASE_거래량모멘텀","BASE + 거래량/모멘텀"),
        ("BASE_시장환경","BASE + 시장환경"),
        ("BASE_추세_거래량모멘텀","BASE + 추세 + 거래량/모멘텀"),
        ("BASE_추세_거래량모멘텀_시장환경","BASE + 추세 + 거래량/모멘텀 + 시장환경"),
    ]
    rows=[]; details={}; annual={}
    for flag,name in flags:
        td,m=bt_simulate_contribution_strategy(x,data,flag,initial_cash,hold_days,fee,slip)
        details[name]=td; annual[name]=bt_annual_contribution(td)
        rows.append({"전략":name,"신호수":int(x[flag].sum()),**{k:m.get(k,np.nan) for k in ["거래수","총수익률","CAGR","MDD","승률","Profit Factor","평균거래수익"]}})
    return pd.DataFrame(rows),details,annual

def bt_run_final_strategy_compare(r, data, initial_cash=1_000_000, hold_days=60, fee=0.001, slip=0.0005):
    """최종 후보 3개만 동일 체결엔진으로 비교한다.
    C = 미래테마 + 선행점수
    D = C + 가격구간
    D+M = D + 시장환경
    """
    x = bt_condition_contribution_flags(r, data)
    if x.empty:
        return pd.DataFrame(), {}, {}

    specs = [
        ("C_미래테마선행", "C · 미래테마+선행"),
        ("D_미래테마선행가격", "D · 미래테마+선행+가격"),
        ("BASE_시장환경", "D+M · D+시장환경"),
    ]
    rows, details, annual = [], {}, {}
    for flag, name in specs:
        td, m = bt_simulate_contribution_strategy(
            x, data, flag, initial_cash, hold_days, fee, slip
        )
        details[name] = td
        annual[name] = bt_annual_contribution(td)
        rows.append({
            "전략": name,
            "신호수": int(x[flag].fillna(False).sum()),
            "거래수": int(m.get("거래수", 0)),
            "총수익률": m.get("총수익률", np.nan),
            "CAGR": m.get("CAGR", np.nan),
            "MDD": m.get("MDD", np.nan),
            "승률": m.get("승률", np.nan),
            "Profit Factor": m.get("Profit Factor", np.nan),
            "평균거래수익": m.get("평균거래수익", np.nan),
        })
    return pd.DataFrame(rows), details, annual




# ============================================================
# 미래테마 · 선행 주식 검증 실험실
# 기존 D는 BASELINE으로 고정하고 새 주식 선정 로직만 단계별 검증한다.
# ============================================================

def _bt_row_market_features(row, data, bench_df=None):
    """신호일 현재까지 공개된 가격정보만 사용해 주식 선행/미반영 특성을 계산."""
    ticker = row.get("주식")
    dt = pd.Timestamp(row.get("날짜"))
    d = data.get(ticker)
    if d is None or d.empty:
        return {}
    pos = d.index.searchsorted(dt)
    if pos >= len(d) or d.index[pos] != dt:
        return {}
    z = d.iloc[pos]
    def f(k, default=np.nan):
        try:
            v=float(z.get(k, default)); return v if np.isfinite(v) else default
        except Exception: return default
    close=f("Close"); ma20=f("MA20"); ma60=f("MA60"); r20=f("R20", f("RET20")); r5=f("R5", f("RET5"))
    rsi=f("RSI", f("RSI14", 50)); vr=f("VR", f("VOL_RATIO", 1))
    dist20=(close/ma20-1)*100 if np.isfinite(close) and np.isfinite(ma20) and ma20 else np.nan
    rs20=r20
    if bench_df is not None and not bench_df.empty:
        bp=bench_df.index.searchsorted(dt)
        if bp < len(bench_df) and bench_df.index[bp] == dt:
            bz=bench_df.iloc[bp]
            br20=bz.get("R20", bz.get("RET20", np.nan))
            try:
                if np.isfinite(float(br20)) and np.isfinite(r20): rs20=r20-float(br20)
            except Exception: pass
    trend=1.0 if np.isfinite(close) and np.isfinite(ma20) and np.isfinite(ma60) and close>=ma20>=ma60 else (0.65 if np.isfinite(close) and np.isfinite(ma60) and close>=ma60 else 0.35)
    not_hot=100.0
    if np.isfinite(rsi): not_hot -= max(0.0, rsi-62)*2.0
    if np.isfinite(dist20): not_hot -= max(0.0, dist20-4)*4.0
    if np.isfinite(r20): not_hot -= max(0.0, r20-10)*2.0
    not_hot=float(np.clip(not_hot,0,100))
    # "미반영도"는 약한 종목을 찾는 점수가 아니라, 선행조건은 양호하면서 가격 과열이 낮은 상태를 선호한다.
    lead_raw=safe_float(row.get("선행점수", row.get("선행점수", 0)),0)
    if not np.isfinite(lead_raw): lead_raw=0
    lead_norm=float(np.clip(lead_raw,0,100))
    rel_score=50.0 if not np.isfinite(rs20) else float(np.clip(50+rs20*4,0,100))
    accel_score=50.0
    if np.isfinite(r5) and np.isfinite(r20): accel_score=float(np.clip(50+(r5-r20/4)*8,0,100))
    flow_score=50.0 if not np.isfinite(vr) else float(np.clip(50+(vr-1)*35,0,100))
    early_score=0.35*lead_norm + 0.20*rel_score + 0.15*trend*100 + 0.10*accel_score + 0.10*flow_score + 0.10*not_hot
    # 미반영도: 선행강도와 비과열도를 결합. 너무 약한 주식은 자동으로 낮아진다.
    underpriced=float(np.clip(0.60*lead_norm + 0.40*not_hot,0,100))
    return {"lead":lead_norm,"rsi":rsi,"vr":vr,"r20":r20,"r5":r5,"dist20":dist20,
            "rs20":rs20,"trend":trend*100,"not_hot":not_hot,"early_score":early_score,"underpriced":underpriced}

def bt_build_early_selection_flags(r, data):
    """D0~D3을 같은 D 신호군에서 파생한다. 기존 D 계산식은 변경하지 않는다."""
    if r is None or r.empty or "D_미래테마선행가격" not in r.columns:
        return pd.DataFrame()
    x=r.copy()
    bench=data.get(BT_BENCH)
    if bench is not None and not bench.empty and "MA60" not in bench.columns:
        bench=bt_indicators(bench.copy())
    feats=[]
    for _,row in x.iterrows():
        feats.append(_bt_row_market_features(row,data,bench))
    f=pd.DataFrame(feats,index=x.index)
    for c in f.columns: x["검증_"+c]=f[c]
    base=x["D_미래테마선행가격"].fillna(False).astype(bool)
    # 날짜별 cross-section percentile. 특정 시대의 절대값 변화에 덜 민감하게 한다.
    for c in ["early_score","underpriced","lead","not_hot"]:
        x["검증_"+c+"_pct"]=x.groupby("날짜")["검증_"+c].rank(pct=True)*100
    x["D0_기존"] = base
    x["D1_선행강세"] = base & (x["검증_early_score_pct"]>=60)
    x["D2_선행_미반영"] = base & (x["검증_early_score_pct"]>=60) & (x["검증_underpriced_pct"]>=60)
    x["D3_선행_미반영_과열회피"] = base & (x["검증_early_score_pct"]>=60) & (x["검증_underpriced_pct"]>=60) & (x["검증_not_hot_pct"]>=40)
    return x

def bt_simulate_selection_validation(r, data, flag, initial_cash=1_000_000, hold_days=60, fee_per_side=0.001, slippage_per_side=0.0005):
    """동일한 고정 보유기간 체결엔진 + MFE/MAE. 다음 거래일 시가 진입."""
    if r is None or r.empty or flag not in r.columns: return pd.DataFrame(), {}
    sigs=r.loc[r[flag].fillna(False).astype(bool)].copy().sort_values("날짜")
    if sigs.empty: return pd.DataFrame(), {}
    cash=float(initial_cash); peak=float(initial_cash); next_available=pd.Timestamp.min; trades=[]; curve=[]
    for _,sig in sigs.iterrows():
        signal_date=pd.Timestamp(sig["날짜"]);
        if signal_date < next_available: continue
        d=data.get(sig["주식"]);
        if d is None or d.empty: continue
        idx=d.index.searchsorted(signal_date)
        entry_i=idx+1; exit_i=entry_i+int(hold_days)-1
        if idx>=len(d) or d.index[idx]!=signal_date or exit_i>=len(d): continue
        er=d.iloc[entry_i]; xr=d.iloc[exit_i]
        entry=float(er.get("Open",er.get("Close",np.nan))); exitp=float(xr.get("Close",np.nan))
        if not np.isfinite(entry) or entry<=0 or not np.isfinite(exitp): continue
        path=d.iloc[entry_i:exit_i+1]
        highs=pd.to_numeric(path.get("High",path.get("Close")),errors="coerce")
        lows=pd.to_numeric(path.get("Low",path.get("Close")),errors="coerce")
        mfe=(float(highs.max())/entry-1)*100 if highs.notna().any() else np.nan
        mae=(float(lows.min())/entry-1)*100 if lows.notna().any() else np.nan
        buy=entry*(1+slippage_per_side); sell=exitp*(1-slippage_per_side); net=(sell/buy-1)-fee_per_side*2
        cash*=1+net; peak=max(peak,cash); curve.append({"날짜":d.index[exit_i],"자산":cash})
        trades.append({"전략":flag,"신호일":signal_date.date(),"진입일":d.index[entry_i].date(),"청산일":d.index[exit_i].date(),"주식":sig["주식"],
                       "테마":sig.get("테마",""),"테마점수":sig.get("테마점수",np.nan),"선행점수":sig.get("선행점수",np.nan),
                       "검증_선행점수":sig.get("검증_lead",np.nan),"검증_선행강세점수":sig.get("검증_early_score",np.nan),
                       "검증_미반영점수":sig.get("검증_underpriced",np.nan),"검증_비과열점수":sig.get("검증_not_hot",np.nan),
                       "20일수익":sig.get("20일수익",np.nan),"60일수익":sig.get("60일수익",np.nan),"MFE":mfe,"MAE":mae,"순수익률":net*100,"거래후자산":cash})
        next_available=d.index[exit_i]+pd.Timedelta(days=1)
    td=pd.DataFrame(trades); cv=pd.DataFrame(curve)
    if td.empty or cv.empty: return td,{"거래수":0,"총수익률":0,"CAGR":np.nan,"MDD":0,"승률":np.nan,"Profit Factor":np.nan,"평균MFE":np.nan,"平均MAE":np.nan}
    cv=cv.sort_values("날짜").drop_duplicates("날짜",keep="last"); cv["고점"]=cv["자산"].cummax(); cv["낙폭"]=(cv["자산"]/cv["고점"]-1)*100
    final=float(cv.iloc[-1]["자산"]); total=(final/initial_cash-1)*100; days=max(1,(pd.Timestamp(cv.iloc[-1]["날짜"])-pd.Timestamp(cv.iloc[0]["날짜"])).days)
    cagr=((final/initial_cash)**(365.25/days)-1)*100 if final>0 else -100
    wins=int((td["순수익률"]>0).sum()); loss_abs=abs(float(td.loc[td["순수익률"]<0,"순수익률"].sum())); gains=float(td.loc[td["순수익률"]>0,"순수익률"].sum())
    pf=gains/loss_abs if loss_abs>0 else (np.inf if gains>0 else np.nan)
    return td,{"거래수":len(td),"총수익률":total,"CAGR":cagr,"MDD":float(cv["낙폭"].min()),"승률":wins/len(td)*100 if len(td) else np.nan,
               "Profit Factor":pf,"평균거래수익":float(td["순수익률"].mean()),"평균MFE":float(td["MFE"].mean()),"평균MAE":float(td["MAE"].mean()),
               "MFE_중앙값":float(td["MFE"].median()),"MAE_중앙값":float(td["MAE"].median())}

def bt_run_early_selection_validation(r,data,initial_cash=1_000_000,hold_days=60,fee=0.001,slip=0.0005):
    x=bt_build_early_selection_flags(r,data)
    if x.empty: return pd.DataFrame(),{},{}
    specs=[("D0_기존","D0 · 기존 D"),("D1_선행강세","D1 · D + 선행강세"),("D2_선행_미반영","D2 · D + 선행 + 미반영"),("D3_선행_미반영_과열회피","D3 · D + 선행 + 미반영 + 과열회피")]
    rows=[]; details={}; annual={}
    for flag,name in specs:
        td,m=bt_simulate_selection_validation(x,data,flag,initial_cash,hold_days,fee,slip); details[name]=td
        if not td.empty:
            z=td.copy(); z["청산일"]=pd.to_datetime(z["청산일"]); z["연도"]=z["청산일"].dt.year
            annual[name]=z.groupby("연도").agg(거래수=("순수익률","size"),평균수익=("순수익률","mean"),승률=("순수익률",lambda s:(s>0).mean()*100),평균MFE=("MFE","mean"),평균MAE=("MAE","mean")).reset_index()
        else: annual[name]=pd.DataFrame()
        rows.append({"전략":name,"신호수":int(x[flag].sum()),**m})
    cmp=pd.DataFrame(rows)
    if not cmp.empty:
        base=cmp.iloc[0]
        for col in ["CAGR","Profit Factor","승률","MDD","평균MFE","평균MAE"]:
            cmp["기준대비_"+col]=cmp[col]-base[col] if col in cmp.columns else np.nan
    return cmp,details,annual

def render_backtest_lab():
    """백테스트 LAB - 최종 화면 5개 섹션만 표시."""
    st.markdown(
        '<div class="hero"><div class="hero-name">🧪 백테스트 LAB</div>'
        '<div class="hero-code">기존 전략 검증 · 미래테마 · 선행 주식 · 미반영 · 과열회피</div></div>',
        unsafe_allow_html=True,
    )
    st.info(
        "연구용 백테스트입니다. 신호일 이후 데이터가 섞이지 않도록 다음 거래일 진입을 사용합니다. "
        "실제 주문체결·세금·배당·환전비용은 완전히 반영되지 않습니다."
    )

    # ========================================================
    # ① 설정 / 실행
    # ========================================================
    st.markdown("### ① 백테스트 설정 / 실행")

    c1, c2, c3 = st.columns(3)
    with c1:
        start = st.date_input("시작일", date(2018, 1, 1), key="bt_start")
    with c2:
        end = st.date_input("종료일", date.today(), key="bt_end")
    with c3:
        step = st.select_slider(
            "검사 간격", options=[1, 3, 5, 10], value=5, key="bt_step",
            format_func=lambda x: "매일" if x == 1 else f"{x}거래일마다"
        )

    defaults = [
        "QQQ", "XLK", "SMH", "SOXX", "BOTZ", "ARKQ",
        "GLD", "TLT", "INDA", "EWY", "EWJ", "EEM"
    ]
    # BT_POOL 변경으로 기본값이 사라져도 앱이 멈추지 않도록 교집합 처리
    defaults = [x for x in defaults if x in BT_POOL]
    selected = st.multiselect(
        "검증 주식", list(BT_POOL.keys()), defaults,
        key="bt_selected",
        format_func=lambda x: f"{x} · {BT_POOL[x]}"
    )

    v1, v2, v3 = st.columns(3)
    with v1:
        initial_cash = st.number_input(
            "초기자산", min_value=100000, value=1000000,
            step=100000, key="bt_final_cash"
        )
    with v2:
        hold_days = st.number_input(
            "보유기간", min_value=5, max_value=500, value=60,
            step=5, key="bt_final_hold"
        )
    with v3:
        fee = st.number_input(
            "편도 수수료", min_value=0.0, max_value=0.01, value=0.001,
            step=0.0001, format="%.4f", key="bt_final_fee"
        )
    slip = st.number_input(
        "편도 슬리피지", min_value=0.0, max_value=0.01, value=0.0005,
        step=0.0001, format="%.4f", key="bt_final_slip"
    )

    if st.button(
        "🚀 최종 3전략 백테스트 실행",
        type="primary", use_container_width=True, key="bt_run_final3"
    ):
        if start >= end:
            st.error("시작일은 종료일보다 빨라야 합니다.")
        elif len(selected) < 4:
            st.error("테마 비교를 위해 주식을 4개 이상 선택하십시오.")
        else:
            with st.spinner("가격·지표·미래테마·선행신호를 계산하는 중입니다…"):
                try:
                    result, data = bt_run_strategy_backtest(start, end, selected, step)
                    st.session_state["strategy_result"] = result
                    st.session_state["strategy_data"] = data
                    st.session_state["final_compare"] = None
                    st.session_state["final_details"] = None
                    st.session_state["final_annual"] = None
                    st.session_state["bt_last_config"] = {
                        "start": str(start), "end": str(end),
                        "selected": selected, "step": step,
                        "hold_days": hold_days, "fee": fee, "slip": slip,
                    }
                    st.success(f"검사 완료 · {len(result):,}개 검사 시점")
                except Exception as ex:
                    st.error("백테스트 실행 중 오류가 발생했습니다.")
                    st.exception(ex)

    r = st.session_state.get("strategy_result")
    data = st.session_state.get("strategy_data")

    if r is None or data is None:
        st.caption("①의 실행 버튼을 누르면 ②~⑤ 결과가 표시됩니다.")
        return
    if r.empty:
        st.warning("백테스트 결과가 없습니다.")
        return

    # ========================================================
    # ② 최종 전략 비교
    # ========================================================
    st.markdown("---")
    st.markdown("### ② 최종 전략 비교 — C / D / D+시장환경")
    st.caption(
        "C = 미래테마 + 선행점수 / D = C + 가격구간 / D+M = D + 시장환경. "
        "동일한 진입일·보유기간·비용 조건으로 비교합니다."
    )

    if st.button(
        "🔬 C / D / D+시장환경 비교 실행",
        type="primary", use_container_width=True, key="bt_run_final_compare"
    ):
        with st.spinner("최종 후보 3전략을 동일 조건으로 비교하는 중입니다…"):
            try:
                final_cmp, final_details, final_annual = bt_run_final_strategy_compare(
                    r, data,
                    initial_cash=initial_cash,
                    hold_days=hold_days,
                    fee=fee,
                    slip=slip,
                )
                st.session_state["final_compare"] = final_cmp
                st.session_state["final_details"] = final_details
                st.session_state["final_annual"] = final_annual
            except Exception as ex:
                st.error("최종 전략 비교 중 오류가 발생했습니다.")
                st.exception(ex)

    final_cmp = st.session_state.get("final_compare")
    final_details = st.session_state.get("final_details")
    final_annual = st.session_state.get("final_annual")

    if isinstance(final_cmp, pd.DataFrame) and not final_cmp.empty:
        st.dataframe(final_cmp, use_container_width=True, hide_index=True)
        st.download_button(
            "📥 최종 3전략 비교 CSV",
            final_cmp.to_csv(index=False).encode("utf-8-sig"),
            "주식_RADAR_FINAL_3_STRATEGY_COMPARISON.csv",
            "text/csv;charset=utf-8",
            use_container_width=True,
            key="bt_download_final_compare",
        )
    else:
        st.info("②의 비교 실행 버튼을 누르면 C / D / D+시장환경 결과가 표시됩니다.")

    # ========================================================
    # ③ 연도별 성과
    # ========================================================
    st.markdown("---")
    st.markdown("### ③ 연도별 성과")
    st.caption("최종 3전략의 연도별 거래 수와 수익률을 비교합니다.")

    if isinstance(final_annual, dict) and final_annual:
        annual_frames = []
        for name, df in final_annual.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                z = df.copy()
                z.insert(0, "전략", name)
                annual_frames.append(z)
        if annual_frames:
            annual_all = pd.concat(annual_frames, ignore_index=True)
            st.dataframe(annual_all, use_container_width=True, hide_index=True)
            st.download_button(
                "📥 연도별 성과 CSV",
                annual_all.to_csv(index=False).encode("utf-8-sig"),
                "주식_RADAR_FINAL_3_STRATEGY_ANNUAL.csv",
                "text/csv;charset=utf-8",
                use_container_width=True,
                key="bt_download_final_annual",
            )
        else:
            st.info("연도별 성과 데이터가 없습니다.")
    else:
        st.info("②의 최종 전략 비교를 먼저 실행하면 연도별 성과가 표시됩니다.")

    # ========================================================
    # ④ 거래 상세
    # ========================================================
    st.markdown("---")
    st.markdown("### ④ 거래 상세")
    st.caption("최종 3전략에서 실제로 발생한 진입·청산 거래를 확인합니다.")

    all_detail = None
    if isinstance(final_details, dict) and final_details:
        detail_frames = []
        for name, df in final_details.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                z = df.copy()
                z.insert(0, "전략", name)
                detail_frames.append(z)
        if detail_frames:
            all_detail = pd.concat(detail_frames, ignore_index=True)

    if isinstance(all_detail, pd.DataFrame) and not all_detail.empty:
        with st.expander("📋 거래 상세 열기", expanded=False):
            st.dataframe(
                all_detail,
                use_container_width=True,
                hide_index=True,
                height=420,
            )
        st.download_button(
            "📥 최종 전략 거래상세 CSV",
            all_detail.to_csv(index=False).encode("utf-8-sig"),
            "주식_RADAR_FINAL_3_STRATEGY_TRADES.csv",
            "text/csv;charset=utf-8",
            use_container_width=True,
            key="bt_download_final_trades",
        )
    else:
        st.info("②의 최종 전략 비교를 먼저 실행하면 거래 상세가 표시됩니다.")

    # ========================================================
    # ⑤ 원본 검사시점
    # ========================================================
    st.markdown("---")
    st.markdown("### ⑤ 원본 검사시점")
    st.caption(
        f"전체 {len(r):,}개 검사 시점 · 화면에는 최근 300개만 표시하며, "
        "전체 데이터는 CSV로 받을 수 있습니다."
    )

    with st.expander("📋 원본 검사시점 전체 데이터 열기", expanded=False):
        st.dataframe(
            r.tail(300),
            use_container_width=True,
            hide_index=True,
            height=420,
        )

    st.download_button(
        "📥 원본 검사시점 전체 CSV",
        r.to_csv(index=False).encode("utf-8-sig"),
        "주식_RADAR_BACKTEST_SIGNAL_DETAIL.csv",
        "text/csv;charset=utf-8",
        use_container_width=True,
        key="bt_download_signal",
    )

    # ========================================================
    # ⑥ 미래테마 · 선행 주식 검증
    # ========================================================
    st.markdown("---")
    st.markdown("### ⑥ 미래테마 · 선행 주식 검증")
    st.caption(
        "기존 D를 BASELINE으로 고정하고, 같은 검사시점·다음 거래일 시가·동일 보유기간·동일 비용으로 "
        "선행강세 → 미반영 → 과열회피를 한 단계씩 추가합니다. "
        "신호일 이후 OHLC로 MFE/MAE를 계산하며, 기존 D 계산식은 변경하지 않습니다."
    )

    if st.button("🧪 D0 / D1 / D2 / D3 검증 실행", type="primary", use_container_width=True, key="bt_run_early_validation"):
        with st.spinner("선행강세·미반영·과열회피와 MFE/MAE를 검증하는 중입니다…"):
            try:
                vc,vd,va=bt_run_early_selection_validation(r,data,initial_cash,hold_days,fee,slip)
                st.session_state["early_validation_cmp"]=vc
                st.session_state["early_validation_details"]=vd
                st.session_state["early_validation_annual"]=va
            except Exception as ex:
                st.error("선행 주식 검증 중 오류가 발생했습니다.")
                st.exception(ex)

    vc=st.session_state.get("early_validation_cmp")
    vd=st.session_state.get("early_validation_details")
    va=st.session_state.get("early_validation_annual")
    if isinstance(vc,pd.DataFrame) and not vc.empty:
        display_cols=["전략","신호수","거래수","총수익률","CAGR","MDD","승률","Profit Factor","평균거래수익","평균MFE","평균MAE","MFE_중앙값","MAE_중앙값"]
        st.dataframe(vc[[c for c in display_cols if c in vc.columns]],use_container_width=True,hide_index=True)
        st.download_button("📥 D0-D3 검증 비교 CSV",vc.to_csv(index=False).encode("utf-8-sig"),"주식_RADAR_D0_D3_EARLY_SELECTION_VALIDATION.csv","text/csv;charset=utf-8",use_container_width=True,key="bt_download_early_cmp")

        st.markdown("#### 판정 기준")
        st.info("D1~D3는 D0보다 거래수가 지나치게 줄면서 성과가 좋아진 경우를 별도로 봐야 합니다. CAGR·PF만 상승했다고 채택하지 않고 MDD, 승률, MFE/MAE, 연도별 재현성을 함께 확인합니다.")

        if isinstance(vd,dict) and vd:
            frames=[]
            for name,td in vd.items():
                if isinstance(td,pd.DataFrame) and not td.empty:
                    frames.append(td)
            if frames:
                all_v=pd.concat(frames,ignore_index=True)
                with st.expander("📋 D0-D3 거래별 MFE / MAE",expanded=False):
                    st.dataframe(all_v,use_container_width=True,hide_index=True,height=420)
                st.download_button("📥 D0-D3 거래 상세 CSV",all_v.to_csv(index=False).encode("utf-8-sig"),"주식_RADAR_D0_D3_EARLY_SELECTION_TRADES.csv","text/csv;charset=utf-8",use_container_width=True,key="bt_download_early_trades")

        if isinstance(va,dict) and va:
            af=[]
            for name,df in va.items():
                if isinstance(df,pd.DataFrame) and not df.empty:
                    z=df.copy(); z.insert(0,"전략",name); af.append(z)
            if af:
                annual_all=pd.concat(af,ignore_index=True)
                with st.expander("📊 D0-D3 연도별 검증",expanded=False):
                    st.dataframe(annual_all,use_container_width=True,hide_index=True)
                st.download_button("📥 D0-D3 연도별 CSV",annual_all.to_csv(index=False).encode("utf-8-sig"),"주식_RADAR_D0_D3_EARLY_SELECTION_ANNUAL.csv","text/csv;charset=utf-8",use_container_width=True,key="bt_download_early_annual")

        st.markdown("#### 핵심 해석")
        st.write("• D1: 기존 D에서 선행강세가 실제로 추가가치를 만드는지 확인")
        st.write("• D2: 선행조건이 좋으면서 아직 가격에 덜 반영된 주식이 더 좋은지 확인")
        st.write("• D3: D2에서 과열 주식을 제거해 손실/MDD가 개선되는지 확인")
        st.write("• MFE가 커지고 MAE가 덜 나빠지면서 PF/CAGR가 개선되고, 여러 연도에서 반복되어야 최종 채택 후보입니다.")
    else:
        st.info("⑥의 검증 실행 버튼을 누르면 새 주식 선정 로직을 기존 D와 동일 조건으로 비교합니다.")


# ============================================================
# TRUE WALK-FORWARD VALIDATION
# 실제 앱의 THEME_LEXICON / 주식 MASTER / 선행 주식 / 가격구간 로직을
# 과거 날짜별로 재생하는 화면형 검증 엔진
# ============================================================

WF_BENCH = "^KS11"
WF_HOLD_DAYS = 60
WF_FEE = 0.0010
WF_SLIPPAGE = 0.0005
WF_OOS_YEAR = 2024
WF_MAX_MEMBERS = 5


def wf_indicator(df):
    if df is None or df.empty:
        return pd.DataFrame()
    return bt_indicators(df.copy())


def wf_fetch_one(code):
    code = _normalize_stock_code(code)
    try:
        ticker = code if str(code).startswith("^") else f"{code}.KS"
        if not str(code).startswith("^"):
            d = yf.download(ticker, period="max", interval="1d", auto_adjust=False, progress=False, threads=False)
            if d is None or d.empty:
                d = yf.download(f"{code}.KQ", period="max", interval="1d", auto_adjust=False, progress=False, threads=False)
        else:
            d = yf.download(ticker, period="max", interval="1d", auto_adjust=False, progress=False, threads=False)
        d = normalize_df(d)
        if not d.empty:
            return code, d
    except Exception:
        pass
    try:
        d = fetch_naver_history(code, count=2000)
        return code, d
    except Exception:
        return code, pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def wf_download_history(codes):
    codes = tuple(sorted(set(_normalize_stock_code(x) for x in codes if x)))
    out = {}
    # 병렬 다운로드. 실패한 종목은 조용히 제외합니다.
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(wf_fetch_one, c) for c in codes]
        for f in as_completed(futures):
            try:
                code, d = f.result()
                if d is not None and not d.empty:
                    out[code] = wf_indicator(d)
            except Exception:
                continue
    return out


def wf_build_universe():
    universe = st.session_state.get("stock_universe") or load_stock_universe()
    if not universe:
        raise RuntimeError("주식 MASTER를 가져오지 못했습니다.")
    st.session_state.stock_universe = universe
    theme_members = {}
    codes = {WF_BENCH, "^KQ11"}
    for theme, keywords in THEME_LEXICON.items():
        matched = []
        for code, name in universe.items():
            hits = _theme_match(name, keywords)
            if hits:
                matched.append((hits, _normalize_stock_code(code), safe_stock_name(code, name)))
        matched.sort(key=lambda x: (x[0], x[2]), reverse=True)
        if len(matched) >= 1:
            members = matched[:WF_MAX_MEMBERS]
            theme_members[theme] = [(x[1], x[2], x[0]) for x in members]
            codes.update(x[1] for x in members)
    return universe, theme_members, sorted(codes)


def wf_row_at(d, dt):
    if d is None or d.empty:
        return None
    pos = d.index.searchsorted(pd.Timestamp(dt), side="right") - 1
    if pos < 0 or pos >= len(d):
        return None
    return d.iloc[pos]


def wf_snapshot(data, theme_members, dt):
    """현재 실전 미래테마/레이더/최종타겟 산식을 과거 날짜에 그대로 재생합니다."""
    bench = data.get(WF_BENCH)
    br = wf_row_at(bench, dt)
    if br is None:
        return None
    bench_ret20 = float(br.get("R20", np.nan))
    bench_ret60 = float(br.get("R60", np.nan))
    if not np.isfinite(bench_ret20) or not np.isfinite(bench_ret60):
        return None

    theme_results = []
    for theme, members in theme_members.items():
        rows = []
        for code, name, hits in members:
            d = data.get(code)
            r = wf_row_at(d, dt)
            if r is None:
                continue
            needed = ["Close", "MA20", "MA60", "R5", "R20", "R60", "VR", "RSI", "LOW20"]
            if any(not np.isfinite(float(r.get(k, np.nan))) for k in needed):
                continue
            rr = r.to_dict()
            current = float(rr["Close"])
            ma20 = float(rr["MA20"])
            ma60 = float(rr["MA60"])
            ret20 = float(rr["R20"])
            ret60 = float(rr["R60"])
            ret5 = float(rr["R5"])
            vr = float(rr["VR"])
            rsi = float(rr["RSI"])
            accel = ret5 - ret20 / 4
            breadth = 100.0 if current >= ma20 else 0.0
            prev = None
            if d is not None and len(d) >= 86:
                pos = d.index.searchsorted(pd.Timestamp(dt), side="right") - 1
                if pos >= 21:
                    prev = d.iloc[pos - 20]
            if prev is not None:
                prev_close = safe_float(prev.get("Close"), 0)
                prev_ma20 = safe_float(prev.get("MA20"), prev_close)
                prev_ret20 = safe_float(prev.get("R20"), ret20)
                prev_ret5 = safe_float(prev.get("R5"), ret5)
                prev_breadth = 100.0 if prev_close >= prev_ma20 else 0.0
                prev_accel = prev_ret5 - prev_ret20 / 4
                prev_rs20 = prev_ret20 - bench_ret20
            else:
                prev_ret20 = ret20
                prev_breadth = breadth
                prev_accel = accel
                prev_rs20 = ret20 - bench_ret20
            rr.update({
                "주식": code, "Name": name, "hits": hits,
                "ret20": ret20, "ret60": ret60, "ret5": ret5,
                "vr": vr, "rsi": rsi,
                "ma60_gap": (current / ma60 - 1) * 100 if ma60 else 0,
                "breadth": breadth, "accel": accel,
                "rs20": ret20 - bench_ret20,
                "ret20_prev": prev_ret20, "breadth_prev": prev_breadth,
                "accel_prev": prev_accel, "rs20_prev": prev_rs20,
            })
            rows.append(rr)

        if len(rows) < 2:
            continue
        raw_score = theme_score(rows, bench_ret20, bench_ret60)
        if raw_score is None:
            continue
        lifecycle = _theme_lifecycle(rows, {"ret20": bench_ret20, "ret60": bench_ret60})
        final_score = float(np.clip(raw_score * 0.75 + lifecycle["score"] * 0.25, 0, 100))
        stage = _theme_stage(final_score, 0, 0, lifecycle)
        theme_results.append({
            "theme": theme,
            "score": final_score,
            "base_score": raw_score,
            "lifecycle": lifecycle,
            "rows": rows,
            "stage": stage,
            "heat": max(0, 100 - lifecycle["score"]),
        })

    if not theme_results:
        return None

    # 실전 미래테마 엔진과 동일하게 점수 기준으로 테마 순위를 만듭니다.
    theme_results.sort(key=lambda x: x["score"], reverse=True)
    theme_results = [x for x in theme_results if x["score"] >= 42][:8]
    if not theme_results:
        return None

    # 실전 _theme_stock_rank와 동일한 개념으로 각 테마의 대표 주식을 과거 시점에서 계산합니다.
    selected = []
    for theme_rank, top in enumerate(theme_results, 1):
        ranked = []
        for row in top["rows"]:
            sig = leading_signal(row, bench_ret20)
            zone = validated_price_zone(row)
            signal_score = float(sig["score"]) * 0.65 + float(top["score"]) * 0.35
            ranked.append({
                "row": row,
                "sig": sig,
                "zone": zone,
                "signal_score": signal_score,
            })
        ranked.sort(key=lambda z: (z["signal_score"], safe_float(z["row"].get("ret20"), -999)), reverse=True)

        for stock_rank, cand in enumerate(ranked[:3], 1):
            row = cand["row"]
            sig = cand["sig"]
            zone = cand["zone"]
            radar = {
                "above20": float(row["Close"]) >= float(row["MA20"]),
                "above60": float(row["Close"]) >= float(row["MA60"]),
                "rs20": sig["rs20"],
                "vr": sig["vr"], "ret20": float(row["R20"]), "ret5": float(row["R5"]),
                "rsi": sig["rsi"], "dist20": sig["dist20"],
            }
            opportunity = radar_score(radar)
            overheat = radar_overheat_score(radar)
            pscore = {"매수구간":100, "눌림대기":70, "추격금지":25, "무효":0}.get(zone["state"], 0)
            cross = (
                float(np.clip(top["base_score"], 0, 100)) * 0.30
                + float(np.clip(top["lifecycle"]["score"], 0, 100)) * 0.20
                + float(np.clip(cand["sig"]["score"], 0, 100)) * 0.30
                + float(np.clip(opportunity, 0, 100)) * 0.10
                + float(np.clip(pscore, 0, 100)) * 0.10
            )
            # 현재 앱 build_radar_data와 동일한 쇠퇴/과열 감점.
            if top["lifecycle"].get("state") == "쇠퇴":
                cross -= 18
            elif top["lifecycle"].get("state") == "과열":
                cross -= 10
            if overheat >= 65:
                cross -= 10
            cross_score = int(np.clip(round(cross), 0, 100))

            selected.append({
                "row": row, "theme": top["theme"], "theme_rank": theme_rank,
                "stock_rank": stock_rank, "theme_score": top["score"],
                "lifecycle_score": top["lifecycle"]["score"],
                "lifecycle_state": top["lifecycle"]["state"],
                "lead_score": sig["score"], "price_zone": zone["state"],
                "opportunity": opportunity, "overheat": overheat,
                "cross_score": cross_score,
            })

    # 현재 build_final_targets의 필터와 최종점수식을 그대로 적용합니다.
    targets = []
    for x in selected:
        if x["opportunity"] < 55:
            continue
        if x["row"]["RSI"] >= 72 or x["row"]["R5"] >= 8:
            continue
        if x["price_zone"] == "무효":
            continue
        future_anchor = max(40.0, 100.0 - (x["theme_rank"] - 1) * 8.0)
        final_score = (
            x["cross_score"] * 0.62
            + x["theme_score"] * 0.18
            + future_anchor * 0.20
        )
        final_score -= max(0, x["stock_rank"] - 1) * 1.5
        if x["theme_rank"] == 1 and x["cross_score"] >= 70:
            final_score += 4.0
        elif x["theme_rank"] >= 4 and x["cross_score"] < 85:
            final_score -= 3.0
        x["final_score"] = float(np.clip(final_score, 0, 100))
        targets.append(x)

    # 검증 신호는 FINAL 통과 여부와 분리한다.
    # FINAL 게이트를 통과한 날짜만 신호로 인정하면 과거 표본 자체가 0개가 될 수 있다.
    # 따라서 선정 가능한 대표 후보는 항상 보존하고, C/D/DM/FINAL은 별도 flag로 기록한다.
    if targets:
        targets.sort(key=lambda x: (x["final_score"], x["cross_score"], -x["theme_rank"], x["opportunity"]), reverse=True)
        winner = targets[0]
    else:
        # 엄격 FINAL 게이트를 통과하지 못한 경우에도 가장 강한 과거 후보를 검증 표본으로 남긴다.
        # 이 후보는 FINAL=True로 만들지 않는다. 이후 전략별 flag에서 자연스럽게 탈락한다.
        if not selected:
            return None
        fallback = sorted(selected, key=lambda x: (x["cross_score"], x["theme_score"], x["opportunity"]), reverse=True)[0]
        future_anchor = max(40.0, 100.0 - (fallback["theme_rank"] - 1) * 8.0)
        fallback["final_score"] = float(np.clip(
            fallback["cross_score"] * 0.62 + fallback["theme_score"] * 0.18 + future_anchor * 0.20
            - max(0, fallback["stock_rank"] - 1) * 1.5
            + (4.0 if fallback["theme_rank"] == 1 and fallback["cross_score"] >= 70 else 0.0)
            - (3.0 if fallback["theme_rank"] >= 4 and fallback["cross_score"] < 85 else 0.0), 0, 100
        ))
        winner = fallback
    row = winner["row"]
    market_pass = bool(
        float(br.get("Close", np.nan)) >= float(br.get("MA60", np.nan))
        and float(br.get("Close", np.nan)) >= float(br.get("MA120", np.nan))
        and bench_ret20 >= 0
    )
    return {
        "date": pd.Timestamp(dt),
        "theme": winner["theme"],
        "theme_rank": int(winner["theme_rank"]),
        "theme_score": float(winner["theme_score"]),
        "theme_stage": winner["lifecycle_state"],
        "etf": row["주식"], "name": row.get("Name", row["주식"]),
        "stock_rank": int(winner["stock_rank"]),
        "final_score": float(winner["final_score"]),
        "cross_score": int(winner["cross_score"]),
        "opportunity": int(winner["opportunity"]),
        "overheat": int(winner["overheat"]),
        "lead_score": float(winner["lead_score"]),
        "price_zone": winner["price_zone"],
        "rsi": float(row["RSI"]), "vr": float(row["VR"]),
        "rs20": float(winner["row"]["R20"] - bench_ret20),
        "dist20": float((row["Close"] / row["MA20"] - 1) * 100),
        "market_pass": market_pass,
        "trend_pass": bool(
            float(row.get("Close", np.nan)) > float(row.get("MA20", np.nan)) > float(row.get("MA60", np.nan))
            and float(row.get("R20", np.nan)) > 0
        ),
        "momvol_pass": bool(
            1.05 <= float(row.get("VR", np.nan)) <= 2.50
            and 50 <= float(row.get("RSI", np.nan)) <= 72
            and float(row.get("R5", np.nan)) > 0
        ),
        "C": bool(
            winner["opportunity"] >= 55
            and float(row.get("RSI", np.nan)) < 72
            and float(row.get("R5", np.nan)) < 8
            and winner["price_zone"] != "무효"
            and winner["final_score"] >= 60
        ),
        "D": bool(
            winner["opportunity"] >= 55
            and float(row.get("RSI", np.nan)) < 72
            and float(row.get("R5", np.nan)) < 8
            and winner["price_zone"] == "매수구간"
            and winner["final_score"] >= 72
        ),
        "DM": bool(
            winner["opportunity"] >= 55
            and float(row.get("RSI", np.nan)) < 72
            and float(row.get("R5", np.nan)) < 8
            and winner["price_zone"] == "매수구간"
            and winner["final_score"] >= 72
            and market_pass
        ),
        "FINAL": bool(
            winner["opportunity"] >= 55
            and float(row.get("RSI", np.nan)) < 72
            and float(row.get("R5", np.nan)) < 8
            and winner["price_zone"] != "무효"
            and winner["final_score"] >= 72
        ),
    }


def wf_trade_from_signal(data, sig, strategy):
    # V14: 전략별로 독립된 종목을 사용
    code = sig.get(f"etf_{strategy}") or sig.get("etf")
    if not code:
        return None
    d = data.get(code)
    if d is None or d.empty:
        return None
    dt = pd.Timestamp(sig["date"])
    pos = d.index.searchsorted(dt, side="right")
    if pos >= len(d):
        return None
    entry_i = pos
    exit_i = min(entry_i + WF_HOLD_DAYS, len(d) - 1)
    entry_date = d.index[entry_i]
    exit_date = d.index[exit_i]
    entry = float(d.iloc[entry_i].get("Open", d.iloc[entry_i]["Close"]))
    exit_px = float(d.iloc[exit_i].get("Close", np.nan))
    if not np.isfinite(entry) or entry <= 0 or not np.isfinite(exit_px):
        return None
    ret = (exit_px / entry - 1) * 100
    net = ret - (WF_FEE + WF_SLIPPAGE) * 2 * 100
    return {
        "strategy": strategy, "signal_date": dt.date().isoformat(),
        "entry_date": entry_date.date().isoformat(), "exit_date": exit_date.date().isoformat(),
        "주식": code, "종목명": sig.get(f"name_{strategy}", sig.get("name", code)),
        "테마": sig.get(f"theme_{strategy}", sig.get("theme", "")),
        "테마점수": round(float(sig.get(f"theme_score_{strategy}", sig.get("theme_score",0))),2),
        "선행점수": round(float(sig.get(f"lead_score_{strategy}", sig.get("lead_score",0))),2),
        "가격구간": sig.get(f"price_zone_{strategy}", sig.get("price_zone", "")),
        "시장통과": bool(sig.get(f"market_pass_{strategy}", sig.get("market_pass",False))),
        "진입가": round(entry,4), "청산가": round(exit_px,4),
        "수익률": round(ret,4), "비용차감후수익률": round(net,4),
        "보유거래일": int(exit_i-entry_i),
    }


def wf_make_trades(data, signals, strategy):
    """V16 고정 포트폴리오 거래: 최대 5개 동시보유, 종목당 20%, 동일종목 중복진입 차단."""
    candidates = [s for s in signals if s.get(f"etf_{strategy}") or (strategy=="FINAL" and s.get("FINAL"))]
    trades=[]
    active={}
    for s in sorted(candidates,key=lambda x:x["date"]):
        t=wf_trade_from_signal(data,s,strategy)
        if t is None: continue
        ed=pd.Timestamp(t["entry_date"]); xd=pd.Timestamp(t["exit_date"]); code=t["주식"]
        # 만료 포지션 해제
        active={c:x for c,x in active.items() if pd.Timestamp(x["exit_date"]) >= ed}
        if code in active: continue
        if len(active)>=5: continue
        t["동시보유한도"]=5; t["배분비중"]=20.0; t["포트폴리오슬롯"]=len(active)+1
        trades.append(t); active[code]=t
    return pd.DataFrame(trades)


def wf_portfolio_simulate(data, trades, start_date=None, end_date=None, max_positions=5, allocation=0.20):
    """TRUE-WF 포트폴리오 검증 엔진.
    초기자금 100, 최대 5개 포지션, 포지션당 현재자산의 20%,
    동일종목 중복진입 금지, 실제 보유기간 동안 일별 종가로 평가한다.
    거래비용/슬리피지는 진입·청산 현금흐름에 각각 반영한다.
    """
    if trades is None or trades.empty:
        return {"summary": {"거래수":0,"승률":0,"평균수익률":0,"총수익률":0,"CAGR":0,"MDD":0,"평균동시보유":0,"최대동시보유":0},
                "equity": pd.DataFrame(), "trade_detail": pd.DataFrame()}
    tr=trades.copy()
    tr["entry_date"]=pd.to_datetime(tr["entry_date"])
    tr["exit_date"]=pd.to_datetime(tr["exit_date"])
    tr=tr.sort_values(["entry_date","exit_date"]).reset_index(drop=True)
    if start_date is not None: tr=tr[tr["entry_date"]>=pd.Timestamp(start_date)]
    if end_date is not None: tr=tr[tr["entry_date"]<=pd.Timestamp(end_date)]
    if tr.empty:
        return {"summary": {"거래수":0,"승률":0,"평균수익률":0,"총수익률":0,"CAGR":0,"MDD":0,"평균동시보유":0,"최대동시보유":0},
                "equity": pd.DataFrame(), "trade_detail": tr}

    fee=float(WF_FEE+WF_SLIPPAGE)
    cash=1.0
    positions={}
    completed=[]
    rows=[]
    dates=sorted(set(pd.Timestamp(x) for x in tr["entry_date"]) | set(pd.Timestamp(x) for x in tr["exit_date"]))
    # 가격평가에 필요한 전체 거래기간의 영업일을 합친다.
    all_dates=[]
    for code,g in tr.groupby("주식"):
        d=data.get(code)
        if d is not None and not d.empty:
            lo=max(pd.Timestamp(g["entry_date"].min()), pd.Timestamp(start_date) if start_date else pd.Timestamp(d.index.min()))
            hi=min(pd.Timestamp(g["exit_date"].max()), pd.Timestamp(end_date) if end_date else pd.Timestamp(d.index.max()))
            all_dates.extend([pd.Timestamp(x) for x in d.index if lo<=pd.Timestamp(x)<=hi])
    if not all_dates:
        all_dates=dates
    dates=sorted(set(all_dates))

    # 실제 동시보유 규칙을 다시 적용한다. 거래 파일에 이미 적용되어 있어도 방어적으로 처리한다.
    accepted=[]; active_codes={}
    for _,t in tr.iterrows():
        ed=pd.Timestamp(t["entry_date"]); xd=pd.Timestamp(t["exit_date"]); code=str(t["주식"])
        active_codes={c:e for c,e in active_codes.items() if pd.Timestamp(e)>ed}
        if code in active_codes or len(active_codes)>=max_positions:
            continue
        accepted.append(t.to_dict()); active_codes[code]=xd
    tr=pd.DataFrame(accepted)
    if tr.empty:
        return {"summary": {"거래수":0,"승률":0,"평균수익률":0,"총수익률":0,"CAGR":0,"MDD":0,"평균동시보유":0,"최대동시보유":0},
                "equity": pd.DataFrame(), "trade_detail": tr}

    by_entry={}
    by_exit={}
    for i,t in tr.iterrows():
        by_entry.setdefault(pd.Timestamp(t["entry_date"]),[]).append((i,t))
        by_exit.setdefault(pd.Timestamp(t["exit_date"]),[]).append((i,t))
    trade_state={}

    for dt in dates:
        # 먼저 청산: 당일 종가 기준
        for i,t in by_exit.get(dt,[]):
            code=str(t["주식"])
            pos=positions.pop(code,None)
            if pos is None: continue
            d=data.get(code); px=np.nan
            if d is not None and dt in d.index: px=safe_float(d.loc[dt].get("Close"),np.nan)
            if not np.isfinite(px): px=pos["exit_px"]
            proceeds=pos["shares"]*px*(1-fee)
            cash += proceeds
            net_ret=(proceeds-pos["capital"])/pos["capital"]*100 if pos["capital"] else 0
            trade_state[i]={"포트폴리오수익률":net_ret,"배분금액":pos["capital"],"실현손익":proceeds-pos["capital"]}
        # 신규 진입: 당일 시가. 빈 슬롯이 없으면 건너뜀.
        for i,t in by_entry.get(dt,[]):
            code=str(t["주식"])
            if code in positions or len(positions)>=max_positions: continue
            d=data.get(code); px=np.nan
            if d is not None and dt in d.index: px=safe_float(d.loc[dt].get("Open",d.loc[dt].get("Close")),np.nan)
            if not np.isfinite(px) or px<=0: continue
            equity_now=cash+sum(p["shares"]*p["last_px"] for p in positions.values())
            capital=equity_now*allocation
            if capital<=0 or cash<capital: continue
            entry_px=px*(1+fee)
            shares=capital/entry_px
            cash-=capital
            positions[code]={"shares":shares,"capital":capital,"entry_date":dt,"entry_px":entry_px,
                             "exit_px":safe_float(t.get("청산가"),px),"last_px":px,"trade_index":i}
        # 종가 평가
        equity=cash
        for code,p in positions.items():
            d=data.get(code); px=p["last_px"]
            if d is not None and dt in d.index:
                z=safe_float(d.loc[dt].get("Close"),np.nan)
                if np.isfinite(z): px=z
            p["last_px"]=px
            equity += p["shares"]*px
        rows.append({"date":dt,"equity":equity,"cash":cash,"positions":len(positions)})

    eq=pd.DataFrame(rows).drop_duplicates("date").sort_values("date")
    if eq.empty:
        return {"summary": {"거래수":len(tr),"승률":0,"평균수익률":0,"총수익률":0,"CAGR":0,"MDD":0,"평균동시보유":0,"최대동시보유":0},"equity":eq,"trade_detail":tr}
    peak=eq["equity"].cummax(); dd=eq["equity"]/peak-1
    years=max((eq["date"].iloc[-1]-eq["date"].iloc[0]).days/365.25,1/365.25)
    total=(eq["equity"].iloc[-1]-1)*100
    cagr=(eq["equity"].iloc[-1]**(1/years)-1)*100 if eq["equity"].iloc[-1]>0 else -100
    detail=tr.copy()
    for i,r in detail.iterrows():
        if i in trade_state:
            detail.loc[i,"포트폴리오수익률"]=trade_state[i]["포트폴리오수익률"]
            detail.loc[i,"배분금액"]=trade_state[i]["배분금액"]
            detail.loc[i,"실현손익"]=trade_state[i]["실현손익"]
    rr=pd.to_numeric(detail.get("포트폴리오수익률",pd.Series(dtype=float)),errors="coerce").dropna()
    summary={"거래수":int(len(detail)),"승률":float((rr>0).mean()*100) if len(rr) else 0,
             "평균수익률":float(rr.mean()) if len(rr) else 0,"총수익률":float(total),"CAGR":float(cagr),
             "MDD":float(dd.min()*100),"평균동시보유":float(eq["positions"].mean()),"최대동시보유":int(eq["positions"].max())}
    return {"summary":summary,"equity":eq,"trade_detail":detail}


def wf_portfolio_compare(data, trade_map):
    rows=[]; curves=[]; details=[]
    for strategy in ["C","D","DM","FINAL"]:
        p=wf_portfolio_simulate(data,trade_map.get(strategy,pd.DataFrame()))
        m=p["summary"].copy(); m["전략"]=strategy; rows.append(m)
        if not p["equity"].empty:
            z=p["equity"].copy(); z["전략"]=strategy; curves.append(z)
        if not p["trade_detail"].empty:
            z=p["trade_detail"].copy(); z["전략"]=strategy; details.append(z)
    summary=pd.DataFrame(rows)[["전략","거래수","승률","평균수익률","총수익률","CAGR","MDD","평균동시보유","최대동시보유"]]
    equity=pd.concat(curves,ignore_index=True) if curves else pd.DataFrame()
    detail=pd.concat(details,ignore_index=True) if details else pd.DataFrame()
    return summary,equity,detail


def wf_summary(trades):
    if trades is None or trades.empty:
        return {"거래수":0,"승률":0,"평균수익률":0,"누적복리":0,"MDD":0}
    r = trades["비용차감후수익률"].astype(float) / 100
    equity = (1 + r).cumprod()
    dd = equity / equity.cummax() - 1
    return {
        "거래수": int(len(trades)),
        "승률": float((r > 0).mean() * 100),
        "평균수익률": float(r.mean() * 100),
        "누적복리": float((equity.iloc[-1] - 1) * 100),
        "MDD": float(dd.min() * 100),
    }


def wf_annual(trades):
    if trades is None or trades.empty:
        return pd.DataFrame(columns=["연도","거래수","승률","평균수익률","누적복리"])
    x=trades.copy()
    x["연도"]=pd.to_datetime(x["entry_date"]).dt.year
    rows=[]
    for y,g in x.groupby("연도"):
        rr=g["비용차감후수익률"].astype(float)/100
        rows.append({"연도":int(y),"거래수":len(g),"승률":(rr>0).mean()*100,"평균수익률":rr.mean()*100,"누적복리":((1+rr).prod()-1)*100})
    return pd.DataFrame(rows).sort_values("연도")




# ============================================================
# TRUE WALK-FORWARD V2 — LIVE 개별주 엔진과 동일한 산식 재생
# ============================================================
def wf_snapshot_v2(data, theme_members, dt):
    """V8 검증잠금: 실전 최종타겟과 동일한 가격데이터 기반 산식을 과거 날짜에 재생."""
    results=[]
    for theme,members in theme_members.items():
        rows=[]
        for code,name,hits in members:
            d=data.get(code); r=wf_row_at(d,dt)
            if r is None: continue
            bench_code='^KQ11' if stock_market(code)=='KOSDAQ' else '^KS11'
            br=wf_row_at(data.get(bench_code),dt)
            if br is None: continue
            need=['Close','MA20','MA60','MA120','R5','R20','R60','VR','RSI','ATR14','TRADING_VALUE','TV20']
            if any(not np.isfinite(float(r.get(k,np.nan))) for k in need): continue
            row=(r.to_dict() if hasattr(r, 'to_dict') else dict(r)); row.update({'주식':code,'Name':name,'hits':hits,'RET5':safe_float(r.get('R5'),0),'RET20':safe_float(r.get('R20'),0),'RET60':safe_float(r.get('R60'),0),'RSI14':safe_float(r.get('RSI'),50),'VOL_RATIO':safe_float(r.get('VR'),1)})
            rows.append(row)
        if len(rows)<1: continue
        b20=float(np.mean([safe_float(z.get('RET20'),0) for z in rows])); b60=float(np.mean([safe_float(z.get('RET60'),0) for z in rows]))
        try: tscore=float(theme_score_v2(rows,b20,b60) or 0); life=_theme_lifecycle(rows,{'ret20':b20,'ret60':b60})
        except Exception: continue
        results.append({'theme':theme,'score':float(np.clip(tscore,0,100)),'lifecycle':life,'rows':rows})
    if not results: return None
    results.sort(key=lambda z:z['score'],reverse=True)
    # 실전 테마 임계값(42)을 통과한 테마를 우선 사용하되, 과거 검증에서
    # 해당 날짜의 테마가 하나도 42를 넘지 않는 경우에도 최고 테마를
    # 검증 표본으로 보존합니다. 낮은 점수를 FINAL 신호로 승격시키지는 않습니다.
    strict_results=[z for z in results if z['score']>=42][:10]
    results=strict_results if strict_results else results[:10]
    candidates=[]
    for tr,top in enumerate(results,1):
        for row in top['rows']:
            code=row['주식']; bc='^KQ11' if stock_market(code)=='KOSDAQ' else '^KS11'; br=wf_row_at(data.get(bc),dt)
            if br is None: continue
            bench={'market':stock_market(code),'ret20':safe_float(br.get('R20'),0),'ret60':safe_float(br.get('R60'),0)}
            score,sig,tech,rel,liq,vol=stock_validation_score(row,bench,{})
            zone=validated_price_zone(row); pscore={'매수구간':100,'눌림대기':70,'추격금지':25,'무효':0}.get(zone.get('state'),0)
            opp=float(np.clip(tech*.30+rel*.25+liq*.20+sig['score']*.15+vol*.10,0,100))
            heat=radar_overheat_score({'rsi':sig['rsi'],'ret5':safe_float(row.get('RET5'),0),'dist20':sig['dist20'],'vr':sig['vr']})
            cross=score*.60+pscore*.15+safe_float(top['lifecycle'].get('score'),50)*.10+rel*.10+liq*.05
            if top['lifecycle'].get('state')=='쇠퇴': cross-=10
            elif top['lifecycle'].get('state')=='과열': cross-=7
            if heat>=65: cross-=10
            cross=float(np.clip(cross,0,100))
            if opp<55 or sig['rsi']>=74 or safe_float(row.get('RET5'),999)>=10 or zone.get('state')=='무효': continue
            anchor=max(40,100-(tr-1)*8); final=cross*.65+safe_float(top['score'])*.15+rel*.10+liq*.10+anchor*.05
            final+=3 if tr==1 and cross>=70 else 0
            candidates.append({'theme':top['theme'],'theme_rank':tr,'stock_rank':1,'theme_score':safe_float(top['score']),'lead_score':sig['score'],'opportunity':opp,'overheat':heat,'cross_score':int(round(cross)),'final_score':float(np.clip(final,0,100)),'price_zone':zone.get('state'),'etf':code,'name':row.get('Name',code),'date':pd.Timestamp(dt)})
    if not candidates: return None
    candidates.sort(key=lambda z:(z['final_score'],z['cross_score'],z['opportunity']),reverse=True); w=candidates[0]
    bc='^KQ11' if stock_market(w['etf'])=='KOSDAQ' else '^KS11'; br=wf_row_at(data.get(bc),dt)
    market_pass=bool(br is not None and safe_float(br.get('Close'))>=safe_float(br.get('MA60')) and safe_float(br.get('R20'))>=0)
    w.update({'C':True,'D':w['price_zone']=='매수구간','DM':w['price_zone']=='매수구간' and market_pass,
              'FINAL':bool(final_target_gate_v11(w, w, market_pass, w.get('lifecycle_state','관찰')))})
    return w

def render_true_walk_forward():
    st.markdown('<div class="hero"><div class="hero-name">🧬 TRUE WALK-FORWARD VALIDATION</div><div class="hero-code">실제 STOCK RADAR 미래테마 엔진을 과거 날짜별로 재생 · 다음 거래일 진입 · OOS 검증</div></div>', unsafe_allow_html=True)
    st.info("이 검증은 현재 앱의 THEME_LEXICON + 실시간 주식 MASTER + 테마점수 + 선행 주식 + 가격구간 로직을 사용합니다. 신호일 이후 가격은 신호 계산에 사용하지 않습니다. 단, 현재 주식 MASTER를 과거에 적용하므로 생존편향은 남습니다.")

    c1,c2,c3=st.columns(3)
    with c1:
        start=st.date_input("검증 시작일", date(2022,1,1), key="wf_start")
    with c2:
        end=st.date_input("검증 종료일", date.today(), key="wf_end")
    with c3:
        step=st.select_slider("신호 검사 간격", options=[1,3,5,10], value=1, key="wf_step", format_func=lambda x:"매일" if x==1 else f"{x}거래일마다")

    st.markdown("### 검증 기준")
    st.write("**C** = 미래테마 + 선행 주식 · **D** = C + 매수구간 · **D+M** = D + 시장환경 · **FINAL V16** = C 후보 독립랭킹 + 고정 5종목 포트폴리오 + 일별 Equity Curve")
    run=st.button("🚀 TRUE WALK-FORWARD 실행", type="primary", use_container_width=True, key="wf_run")

    if run:
        if start >= end:
            st.error("시작일은 종료일보다 빨라야 합니다.")
            return
        with st.status("실제 앱 로직을 과거 날짜별로 재생하는 중...", expanded=True) as status:
            try:
                status.write("① 현재 주식 MASTER에서 테마별 주식 후보 구성")
                universe, theme_members, codes = wf_build_universe()
                status.write(f"② 검증 주식 {len(codes)}개 가격 데이터 다운로드")
                data=wf_download_history(tuple(codes))
                data={k:v for k,v in data.items() if v is not None and not v.empty}
                if WF_BENCH not in data:
                    raise RuntimeError("KOSPI 지수 데이터를 가져오지 못했습니다.")
                status.write("③ 과거 날짜별 미래테마 → 선행 주식 → 가격구간 계산")
                bench=data[WF_BENCH]
                dates=bench.index[(bench.index>=pd.Timestamp(start))&(bench.index<=pd.Timestamp(end))]
                signals=[]
                scan_dates=list(dates)[::int(step)]
                total_scan=len(scan_dates)
                progress=st.progress(0.0, text=f"과거 신호 계산 중... 0/{total_scan}")
                for j,dt in enumerate(scan_dates,1):
                    s=wf_snapshot_v3(data,theme_members,dt)
                    if s:
                        signals.append(s)
                    if j==1 or j==total_scan or j%10==0:
                        progress.progress(j/total_scan, text=f"과거 신호 계산 중... {j}/{total_scan}")
                progress.empty()
                if not signals:
                    raise RuntimeError("유효한 과거 신호가 없습니다. 기간을 늘리거나 검사 간격을 줄여주세요.")
                status.write("④ 다음 거래일 진입 + 60거래일 보유 시뮬레이션")
                trade_map={}
                for strategy in ["C","D","DM","FINAL"]:
                    trade_map[strategy]=wf_make_trades(data,signals,strategy)
                summary,equity,portfolio_trades=wf_portfolio_compare(data,trade_map)
                sigdf=pd.DataFrame(signals)
                oos=sigdf[pd.to_datetime(sigdf["date"]).dt.year>=WF_OOS_YEAR].copy()
                alltrades=portfolio_trades if not portfolio_trades.empty else pd.concat([trade_map[x] for x in ["C","D","DM","FINAL"]],ignore_index=True)
                annual=pd.concat([wf_annual(trade_map[x]).assign(전략=x) for x in ["C","D","DM","FINAL"]],ignore_index=True)
                st.session_state["wf_result"]={"summary":summary,"signals":sigdf,"trades":alltrades,"annual":annual,"oos":oos,"equity":equity}
                status.update(label="TRUE WALK-FORWARD 완료",state="complete",expanded=False)
            except Exception as ex:
                status.update(label="검증 실패",state="error",expanded=True)
                st.exception(ex)
                return

    result=st.session_state.get("wf_result")
    if not result:
        return
    summary=result["summary"]
    st.markdown("### 검증 결과")
    st.dataframe(summary, use_container_width=True, hide_index=True)
    c1,c2,c3=st.columns(3)
    with c1:
        st.metric("신호 수", len(result["signals"]))
    with c2:
        st.metric("OOS 신호 수", len(result["oos"]))
    with c3:
        st.metric("전체 거래 수", len(result["trades"]))

    st.markdown("### 실제 포트폴리오 검증 결과")
    st.caption("초기자금 100% · 최대 5종목 · 종목당 20% · 동일종목 중복진입 금지 · 60거래일 · 비용/슬리피지 · 일별 종가 평가")
    st.markdown("### OOS 연도별 결과")
    st.dataframe(result["annual"],use_container_width=True,hide_index=True)
    st.markdown("### 최근 생성된 신호")
    st.dataframe(result["signals"].sort_values("date",ascending=False).head(30),use_container_width=True,hide_index=True)

    files={
        "TRUE_WALK_FORWARD_SUMMARY.csv":result["summary"],
        "TRUE_WALK_FORWARD_SIGNALS.csv":result["signals"],
        "TRUE_WALK_FORWARD_TRADES.csv":result["trades"],
        "TRUE_WALK_FORWARD_ANNUAL.csv":result["annual"],
        "TRUE_WALK_FORWARD_OOS.csv":result["oos"],
        "TRUE_WALK_FORWARD_EQUITY.csv":result.get("equity",pd.DataFrame()),
    }
    st.markdown("### CSV 결과 다운로드")
    cols=st.columns(3)
    for i,(name,df) in enumerate(files.items()):
        with cols[i%3]:
            st.download_button(f"📥 {name}",df.to_csv(index=False,encoding="utf-8-sig").encode("utf-8-sig"),file_name=name,mime="text/csv",use_container_width=True,key="wf_dl_"+name)



# ============================================================
# FINAL VALIDATION LAB
# 매일 신호 + 보유기간별 + 조건 기여도 + OOS
# ============================================================

WF_HORIZONS = [5, 10, 20, 40, 60]


def wf_trade_horizon(data, sig, strategy, hold_days):
    code = sig.get("etf")
    d = data.get(code)
    if d is None or d.empty:
        return None
    dt = pd.Timestamp(sig["date"])
    pos = d.index.searchsorted(dt, side="right")
    if pos >= len(d):
        return None
    entry_i = pos
    exit_i = min(entry_i + int(hold_days), len(d) - 1)
    entry_date = d.index[entry_i]
    exit_date = d.index[exit_i]
    entry = float(d.iloc[entry_i].get("Open", d.iloc[entry_i].get("Close", np.nan)))
    exit_px = float(d.iloc[exit_i].get("Close", np.nan))
    if not np.isfinite(entry) or entry <= 0 or not np.isfinite(exit_px):
        return None
    gross = (exit_px / entry - 1) * 100
    net = gross - (WF_FEE + WF_SLIPPAGE) * 2 * 100
    return {
        "strategy": strategy, "보유기간": int(hold_days),
        "signal_date": dt.date().isoformat(),
        "entry_date": entry_date.date().isoformat(),
        "exit_date": exit_date.date().isoformat(),
        "주식": code, "종목명": sig.get("name", code), "테마": sig.get("theme", ""),
        "테마점수": round(float(sig.get("theme_score", 0)), 2),
        "선행점수": round(float(sig.get("lead_score", 0)), 2),
        "가격구간": sig.get("price_zone", ""),
        "시장통과": bool(sig.get("market_pass", False)),
        "진입가": round(entry, 4), "청산가": round(exit_px, 4),
        "수익률": round(gross, 4), "비용차감후수익률": round(net, 4),
        "보유거래일": int(exit_i-entry_i),
    }


def wf_make_trades_horizon(data, signals, strategy, hold_days):
    candidates = [x for x in signals if x.get(strategy, False)]
    trades=[]; last_exit=None
    for sig in sorted(candidates, key=lambda x: x["date"]):
        t=wf_trade_horizon(data, sig, strategy, hold_days)
        if t is None: continue
        ed=pd.Timestamp(t["entry_date"]); xd=pd.Timestamp(t["exit_date"])
        if last_exit is not None and ed <= last_exit: continue
        trades.append(t); last_exit=xd
    return pd.DataFrame(trades)


def wf_add_final_strategy_flags(signals):
    """D를 기준으로 필터의 독립/복합 기여도를 계산한다."""
    out=[]
    for s in signals:
        x=dict(s)
        d=bool(x.get("D",False)); t=bool(x.get("trend_pass",False)); mv=bool(x.get("momvol_pass",False)); m=bool(x.get("market_pass",False))
        x["BASE_D"]=d
        x["D+TREND"]=d and t
        x["D+MOMVOL"]=d and mv
        x["D+MARKET"]=d and m
        x["D+T+MV"]=d and t and mv
        x["D+T+M"]=d and t and m
        x["D+MV+M"]=d and mv and m
        x["D+T+MV+M"]=d and t and mv and m
        out.append(x)
    return out


def wf_final_summary(trades):
    if trades is None or trades.empty:
        return {"거래수":0,"승률":0,"평균수익률":0,"누적복리":0,"MDD":0}
    r=pd.to_numeric(trades["비용차감후수익률"],errors="coerce").dropna()/100
    if r.empty: return {"거래수":0,"승률":0,"평균수익률":0,"누적복리":0,"MDD":0}
    eq=(1+r).cumprod(); dd=eq/eq.cummax()-1
    return {"거래수":int(len(r)),"승률":float((r>0).mean()*100),"평균수익률":float(r.mean()*100),"누적복리":float((eq.iloc[-1]-1)*100),"MDD":float(dd.min()*100)}



# ============================================================
# FORWARD + ML FUTURE PROBABILITY
# 최종검증 내부에서만 사용. 과거 T의 정보로 T+20/T+40/T+60 결과를 학습합니다.
# sklearn이 없으면 규칙 기반 Forward 결과만 표시하며 앱은 정상 동작합니다.
# ============================================================

def _forward_theme_feature(rows, benchmark_ret20=0.0):
    """Forward/ML용 9개 feature를 항상 유한한 범위로 반환합니다."""
    if not rows:
        return None
    def av(k):
        vals=[]
        for x in rows:
            v=safe_float(x.get(k),0.0)
            if np.isfinite(v):
                vals.append(v)
        return float(np.mean(vals)) if vals else 0.0
    arr=np.asarray([
        av("ret5"), av("ret20"), av("ret60"), av("vr"), av("rsi"),
        av("ma60_gap"), av("breadth"), av("accel"), av("rs20")
    ],dtype=np.float64)
    # 학습 실패를 유발하는 NaN/inf/초대형 값 최종 방어
    arr=np.nan_to_num(arr,nan=0.0,posinf=0.0,neginf=0.0)
    arr=np.clip(arr,-1e6,1e6)
    return arr


def _historical_theme_sample(theme, info, horizon=20, max_samples=18):
    """현재 테마 구성 주식을 사용하되 각 과거 시점의 가격만으로 feature/label을 생성."""
    members=info.get("rows",[])[:8]
    if len(members)<2: return []
    series={}
    for m in members:
        df=load_price_data(m.get("code"))
        if df is not None and not df.empty and len(df)>=150:
            series[m.get("code")]=calculate_indicators(df)
    if len(series)<2: return []
    bench_code=WF_BENCH if 'WF_BENCH' in globals() else '^KS11'
    bdf=series.get(bench_code)
    if bdf is None:
        bdf=load_price_data(bench_code)
        if bdf is not None and not bdf.empty: bdf=calculate_indicators(bdf)
    if bdf is None or bdf.empty: return []
    common=sorted(set.intersection(*[set(x.index) for x in series.values()]))
    common=[x for x in common if x in bdf.index]
    if len(common)<horizon+80: return []
    # 20거래일 간격으로 표본화하여 계산량을 제한
    idxs=list(range(80, len(common)-horizon, max(10, len(common)//max_samples)))
    samples=[]
    for pos in idxs[-max_samples:]:
        dt=common[pos]
        rows=[]
        for code,d in series.items():
            if dt not in d.index: continue
            r=d.loc[dt]
            c=safe_float(r.get('Close'),0); ma20=safe_float(r.get('MA20'),c); ma60=safe_float(r.get('MA60'),c)
            ret20=safe_float(r.get('RET20'),0); ret60=safe_float(r.get('RET60'),0)
            ret5=safe_float(r.get('RET5'),0); vr=safe_float(r.get('VOL_RATIO'),1); rsi=safe_float(r.get('RSI14'),50)
            rows.append({'ret5':ret5,'ret20':ret20,'ret60':ret60,'vr':vr,'rsi':rsi,
                         'ma60_gap':((c/ma60-1)*100 if ma60 else 0),'breadth':100 if c>=ma20 else 0,
                         'accel':ret5-ret20/4,'rs20':ret20-safe_float(bdf.loc[dt].get('RET20'),0)})
        if len(rows)<2: continue
        feat=_forward_theme_feature(rows)
        future_rows=[]
        future_dt=common[pos+horizon]
        for code,d in series.items():
            if future_dt not in d.index: continue
            r=d.loc[future_dt]
            future_rows.append(safe_float(r.get('RET20'),0)-safe_float(bdf.loc[future_dt].get('RET20'),0))
        if not future_rows: continue
        # 미래 20일 상대강도 평균이 +3% 이상이면 '미래 강화' 1
        label=1 if float(np.mean(future_rows))>=3.0 else 0
        samples.append((feat,label))
    return samples


def run_forward_ml():
    engine=build_future_theme_engine()
    details=engine.get('details',{})
    rows=[]
    allX=[]; allY=[]; meta=[]
    # 현재 상위 테마를 기준으로 과거 Forward 샘플 생성
    for theme,info in list(details.items())[:10]:
        for horizon in (20,40,60):
            samples=_historical_theme_sample(theme,info,horizon=horizon,max_samples=12)
            if not samples: continue
            for x,y in samples:
                allX.append(x); allY.append(y); meta.append((theme,horizon))
    result=[]
    try:
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.linear_model import LogisticRegression
        sklearn_ok=True
    except Exception:
        sklearn_ok=False
    if sklearn_ok and len(allX)>=20 and len(set(allY))>=2:
        # ML 직전 전체 학습행렬을 다시 정제합니다.
        X=np.asarray(allX,dtype=np.float64)
        y=np.asarray(allY,dtype=np.int64)
        finite_mask=np.isfinite(X).all(axis=1) & np.isfinite(y)
        X=X[finite_mask]
        y=y[finite_mask]
        X=np.nan_to_num(X,nan=0.0,posinf=0.0,neginf=0.0)
        X=np.clip(X,-1e6,1e6)
        if len(X)<20 or len(np.unique(y))<2:
            sklearn_ok=False
        else:
            model=Pipeline([('scaler',StandardScaler()),('lr',LogisticRegression(max_iter=1000,class_weight='balanced'))])
            model.fit(X,y)
            for theme,info in details.items():
                f=_forward_theme_feature(info.get('rows',[]),safe_float(engine.get('benchmark',{}).get('ret20'),0))
                if f is None or not np.isfinite(f).all():
                    continue
                f=np.nan_to_num(f,nan=0.0,posinf=0.0,neginf=0.0)
                f=np.clip(f,-1e6,1e6)
                prob=float(model.predict_proba([f])[0,1]*100)
                # 20/40/60 학습 샘플을 합쳐 현재 테마의 미래 강화 확률을 계산합니다.
                result.append({'테마':theme,'현재점수':round(safe_float(info.get('score')),1),'ML미래강화확률':round(prob,1),
                               '판정':'🔥 높음' if prob>=70 else '🟢 양호' if prob>=55 else '🟡 보통' if prob>=45 else '🔴 낮음'})
            return pd.DataFrame(result), {'sklearn':True,'samples':len(X),'positive_rate':float(np.mean(y)*100)}
    # sklearn 미설치 또는 표본 부족: ML 대신 Forward 규칙 확률을 표시
    for theme,info in details.items():
        score=safe_float(info.get('score')); life=safe_float(info.get('lifecycle',{}).get('score'))
        p=float(np.clip(score*.65+life*.35,0,100))
        result.append({'테마':theme,'현재점수':round(score,1),'ML미래강화확률':round(p,1),
                       '판정':'⚠️ ML 미실행' if not sklearn_ok else '⚠️ 표본부족'})
    return pd.DataFrame(result), {'sklearn':False,'samples':len(allX),'positive_rate':float(np.mean(allY)*100) if allY else 0}


def render_forward_ml_panel():
    with st.expander('🧠 Forward + ML 미래테마 검증', expanded=False):
        st.caption('과거 T 시점의 정보만 사용해 T+20/T+40/T+60의 테마 강화 여부를 학습합니다. 현재 앱의 미래테마 판단을 대체하지 않고 보조합니다.')
        if st.button('🚀 Forward + ML 실행 / 갱신', type='primary', use_container_width=True, key='forward_ml_run'):
            with st.spinner('과거 Forward 샘플을 구성하고 ML을 학습하는 중...'):
                try:
                    out,meta=run_forward_ml()
                    st.session_state['forward_ml_result']=out
                    st.session_state['forward_ml_meta']=meta
                except Exception as ex:
                    st.error(f'Forward + ML 실행 실패: {ex}')
        out=st.session_state.get('forward_ml_result')
        meta=st.session_state.get('forward_ml_meta')
        if out is None:
            st.info('버튼을 누르면 과거 Forward 결과를 기반으로 미래테마 강화 확률을 계산합니다.')
            return
        if meta:
            a,b,c=st.columns(3)
            a.metric('학습 표본',f"{meta.get('samples',0):,}")
            b.metric('ML 사용', '예' if meta.get('sklearn') else '아니오')
            c.metric('강화 표본 비율',f"{meta.get('positive_rate',0):.1f}%")
        st.dataframe(out.sort_values(['ML미래강화확률','현재점수'],ascending=False),use_container_width=True,hide_index=True)
        st.caption('주의: 현재 주식 MASTER를 과거에 적용하므로 생존편향은 남습니다. 확률은 투자수익 보장이 아니라 후보 우선순위용입니다.')

def render_final_validation():
    st.markdown('<div class="hero"><div class="hero-name">🏁 FINAL VALIDATION LAB</div><div class="hero-code">D+M 최종검증 · 매일 신호 · 보유기간 5/10/20/40/60일 · 조건 기여도 · OOS</div></div>', unsafe_allow_html=True)
    st.info("이 화면은 전략을 새로 만드는 곳이 아닙니다. 현재 D+M 후보를 고정하고 표본 수·보유기간·필터 기여도·OOS를 동시에 검증합니다.")
    render_forward_ml_panel()
    c1,c2,c3=st.columns(3)
    with c1: start=st.date_input("검증 시작일",date(2018,1,1),key="fv_start")
    with c2: end=st.date_input("검증 종료일",date.today(),key="fv_end")
    with c3: oos_year=st.number_input("OOS 시작연도",min_value=2018,max_value=2030,value=2024,step=1,key="fv_oos")
    st.markdown("**검사 간격: 매일(1거래일)** · **비용: 편도 수수료 0.10% + 슬리피지 0.05%**")
    if st.button("🚀 FINAL VALIDATION 실행",type="primary",use_container_width=True,key="fv_run"):
        if start>=end:
            st.error("시작일은 종료일보다 빨라야 합니다."); return
        with st.status("최종 검증을 실행하는 중...",expanded=True) as status:
            try:
                status.write("① 현재 주식 MASTER에서 테마군 구성")
                universe,theme_members,codes=wf_build_universe()
                status.write(f"② 주식 {len(codes)}개 가격 데이터 다운로드")
                data=wf_download_history(tuple(codes)); data={k:v for k,v in data.items() if v is not None and not v.empty}
                if WF_BENCH not in data: raise RuntimeError("KOSPI 지수 데이터를 가져오지 못했습니다.")
                bench=data[WF_BENCH]
                dates=bench.index[(bench.index>=pd.Timestamp(start))&(bench.index<=pd.Timestamp(end))]
                signals=[]
                for i,dt in enumerate(dates):
                    snap=wf_snapshot(data,theme_members,dt)
                    if snap: signals.append(snap)
                if not signals: raise RuntimeError("유효한 신호가 없습니다.")
                signals=wf_add_final_strategy_flags(signals)
                status.write(f"③ 매일 검사 완료: {len(signals):,}개 신호")
                strategy_keys=["BASE_D","D+TREND","D+MOMVOL","D+MARKET","D+T+MV","D+T+M","D+MV+M","D+T+MV+M"]
                labels={"BASE_D":"BASE D","D+TREND":"D + 추세","D+MOMVOL":"D + 모멘텀·거래량","D+MARKET":"D + 시장환경","D+T+MV":"D + 추세 + 모멘텀·거래량","D+T+M":"D + 추세 + 시장환경","D+MV+M":"D + 모멘텀·거래량 + 시장환경","D+T+MV+M":"D + 추세 + 모멘텀·거래량 + 시장환경"}
                all_summary=[]; all_trades=[]
                for hold in WF_HORIZONS:
                    for key in strategy_keys:
                        td=wf_make_trades_horizon(data,signals,key,hold)
                        m=wf_final_summary(td)
                        m.update({"전략":labels[key],"조건키":key,"보유기간":hold})
                        all_summary.append(m)
                        if not td.empty: all_trades.append(td)
                summary=pd.DataFrame(all_summary)
                trades=pd.concat(all_trades,ignore_index=True) if all_trades else pd.DataFrame()
                sigdf=pd.DataFrame(signals)
                oos=sigdf[pd.to_datetime(sigdf["date"]).dt.year>=int(oos_year)].copy()
                # OOS는 거래까지 포함한 표
                oos_rows=[]
                for hold in WF_HORIZONS:
                    for key in strategy_keys:
                        td=wf_make_trades_horizon(data,signals,key,hold)
                        if not td.empty:
                            z=td[pd.to_datetime(td["signal_date"]).dt.year>=int(oos_year)].copy()
                            if not z.empty:
                                m=wf_final_summary(z); m.update({"전략":labels[key],"조건키":key,"보유기간":hold})
                                oos_rows.append(m)
                oos_summary=pd.DataFrame(oos_rows)
                st.session_state["fv_result"]={"summary":summary,"trades":trades,"signals":sigdf,"oos_signals":oos,"oos_summary":oos_summary}
                status.update(label="FINAL VALIDATION 완료",state="complete",expanded=False)
            except Exception as ex:
                status.update(label="최종 검증 실패",state="error",expanded=True); st.exception(ex); return
    r=st.session_state.get("fv_result")
    if not r: return
    st.markdown("### 1. 보유기간별 전체 결과")
    pivot=r["summary"].pivot_table(index="전략",columns="보유기간",values="누적복리",aggfunc="first")
    st.dataframe(pivot.round(2),use_container_width=True)
    st.markdown("### 2. 전체 상세 결과")
    st.dataframe(r["summary"].sort_values(["보유기간","누적복리"],ascending=[True,False]),use_container_width=True,hide_index=True)
    st.markdown("### 3. OOS 결과")
    st.dataframe(r["oos_summary"].sort_values(["보유기간","누적복리"],ascending=[True,False]),use_container_width=True,hide_index=True)
    st.markdown("### 4. 신호 표본")
    st.write(f"전체 신호 {len(r['signals']):,}개 / OOS 신호 {len(r['oos_signals']):,}개")
    st.dataframe(r["signals"].sort_values("date",ascending=False).head(50),use_container_width=True,hide_index=True)
    files={
        "FINAL_VALIDATION_SUMMARY.csv":r["summary"],
        "FINAL_VALIDATION_TRADES.csv":r["trades"],
        "FINAL_VALIDATION_SIGNALS.csv":r["signals"],
        "FINAL_VALIDATION_OOS_SUMMARY.csv":r["oos_summary"],
        "FINAL_VALIDATION_OOS_SIGNALS.csv":r["oos_signals"],
    }
    st.markdown("### 5. CSV 다운로드")
    cols=st.columns(3)
    for i,(name,df) in enumerate(files.items()):
        with cols[i%3]: st.download_button(f"📥 {name}",df.to_csv(index=False,encoding="utf-8-sig").encode("utf-8-sig"),file_name=name,mime="text/csv",use_container_width=True,key="fv_dl_"+name)


# ============================================================
# STOCK-SPECIFIC ENGINE V2
# ETF 공통 기술지표는 유지하되, 개별주 전용 계층을 추가합니다.
# 시장 -> 업종/테마 -> 기업규모/유동성 -> 상대강도 -> 기술 -> 가격
# ============================================================

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_krx_stock_metadata_v2():
    url="https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
    headers={"User-Agent":"Mozilla/5.0","Accept":"application/json,text/plain,*/*",
             "Referer":"https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd",
             "Origin":"https://data.krx.co.kr"}
    payload={"bld":"dbms/MDC/STAT/standard/MDCSTAT01901","locale":"ko_KR","mktId":"ALL","share":"1","csvxls_isNo":"false"}
    out={}
    try:
        r=requests.post(url,headers=headers,data=payload,timeout=20); r.raise_for_status()
        rows=(r.json().get("OutBlock_1") or r.json().get("output") or [])
        for x in rows:
            code=_normalize_stock_code(x.get("ISU_SRT_CD") or x.get("isu_srt_cd"))
            name=safe_stock_name(code,x.get("ISU_ABBRV") or x.get("ISU_NM") or x.get("isu_abrv"))
            market=str(x.get("MKT_TP_NM") or x.get("MKT_TP_NM") or "").strip().upper()
            security=str(x.get("SECUGRP_NM") or x.get("KIND_STKCERT_DIV_NM") or "").strip().upper()
            if not code or len(code)!=6 or name.startswith("주식 ") or market not in {"KOSPI","KOSDAQ"}:
                continue
            if any(k in security for k in ("ETF","ETN","ELW")):
                continue
            def num(*keys):
                for k in keys:
                    v=x.get(k)
                    if v is not None and str(v).strip()!="":
                        try:
                            return float(str(v).replace(",",""))
                        except Exception:
                            pass
                return 0.0
            shares=num("LIST_SHRS","LISTED_SHRS","LIST_SHR","LISTED_SHARES")
            price=num("TDD_CLSPRC","CLSPRC","CLOSE")
            mcap=num("MKTCAP","MKT_CAP","MKTCAP_VAL")
            if mcap<=0 and shares>0 and price>0:
                mcap=shares*price
            sector=""
            for k in ("SECT_TP_NM","INDUTY_NM","UPJONG_NM","SECT_NM","IDX_IND_NM"):
                v=str(x.get(k) or "").strip()
                if v and v.lower() not in {"nan","none"}:
                    sector=v; break
            out[code]={"name":name,"market":market,"security":security,
                       "shares":shares,"price":price,"market_cap":mcap,"sector":sector}
    except Exception:
        return {}
    return out


def stock_metadata(code):
    code=_normalize_stock_code(code)
    cache=st.session_state.setdefault("stock_metadata",{})
    if code in cache:
        return cache[code]
    meta=fetch_krx_stock_metadata_v2().get(code,{})
    if not meta:
        name=get_stock_name(code)
        meta={"name":name,"market":"KOSPI","security":"","shares":0.0,"price":0.0,"market_cap":0.0,"sector":""}
    cache[code]=meta
    return meta


def stock_market(code):
    m=str(stock_metadata(code).get("market") or "KOSPI").upper()
    return "KOSDAQ" if m=="KOSDAQ" else "KOSPI"


@st.cache_data(ttl=900, show_spinner=False)
def load_market_benchmark_v2(market="KOSPI"):
    ticker="^KQ11" if str(market).upper()=="KOSDAQ" else "^KS11"
    try:
        df=yf.download(ticker,period="2y",interval="1d",auto_adjust=False,progress=False,threads=False)
        return normalize_df(df)
    except Exception:
        return pd.DataFrame()


def benchmark_snapshot_for_stock(code):
    market=stock_market(code)
    df=load_market_benchmark_v2(market)
    if df.empty:
        return {"market":market,"ret5":0.0,"ret20":0.0,"ret60":0.0}
    d=calculate_indicators(df)
    if d.empty:
        return {"market":market,"ret5":0.0,"ret20":0.0,"ret60":0.0}
    r=d.iloc[-1]
    return {"market":market,"ret5":safe_float(r.get("RET5"),0),"ret20":safe_float(r.get("RET20"),0),"ret60":safe_float(r.get("RET60"),0)}


def stock_liquidity_score(meta,row):
    tv=safe_float(row.get("TRADING_VALUE"),0)
    # 일평균 거래대금이 없는 경우 현재 거래대금으로 보수적으로 평가
    tv20=safe_float(row.get("TV20"),tv)
    if tv20>=100_000_000_000: s=100
    elif tv20>=50_000_000_000: s=90
    elif tv20>=20_000_000_000: s=78
    elif tv20>=10_000_000_000: s=65
    elif tv20>=5_000_000_000: s=50
    elif tv20>=1_000_000_000: s=30
    else: s=10
    # 소형주에서 거래대금만으로 과대평가되는 것을 방지
    mc=safe_float(meta.get("market_cap"),0)
    if mc>0 and mc<50_000_000_000: s-=15
    elif mc>0 and mc<100_000_000_000: s-=8
    return float(np.clip(s,0,100))


def stock_size_score(meta):
    mc=safe_float(meta.get("market_cap"),0)
    if mc>=10_000_000_000_000: return 100.0
    if mc>=5_000_000_000_000: return 94.0
    if mc>=1_000_000_000_000: return 85.0
    if mc>=500_000_000_000: return 72.0
    if mc>=100_000_000_000: return 55.0
    if mc>0: return 30.0
    return 50.0


def stock_volatility_score(row):
    atrp=safe_float(row.get("ATR_PCT"),0)
    if atrp<=0: return 50.0
    if 1.2<=atrp<=4.5: return 100.0
    if atrp<=6.5: return 85.0
    if atrp<=9: return 65.0
    if atrp<=13: return 40.0
    return 20.0


def stock_relative_score(row, bench):
    rs20=safe_float(row.get("RET20"),0)-safe_float(bench.get("ret20"),0)
    rs60=safe_float(row.get("RET60"),0)-safe_float(bench.get("ret60"),0)
    s20=float(np.clip((rs20+12)/24*100,0,100))
    s60=float(np.clip((rs60+20)/40*100,0,100))
    return float(np.clip(s20*.60+s60*.40,0,100))


def stock_technical_score(row, bench):
    c=safe_float(row.get("Close"),0); ma20=safe_float(row.get("MA20"),c); ma60=safe_float(row.get("MA60"),c); ma120=safe_float(row.get("MA120"),c)
    rsi=safe_float(row.get("RSI14"),50); r5=safe_float(row.get("RET5"),0); r20=safe_float(row.get("RET20"),0); vr=safe_float(row.get("VOL_RATIO"),1)
    trend=(25 if c>=ma20 else 0)+(20 if c>=ma60 else 0)+(15 if ma20>=ma60 else 0)+(10 if ma60>=ma120 else 0)
    rel=stock_relative_score(row,bench)*.25
    momentum=12 if 1<=r20<=18 else 8 if 0<=r20<1 else 6 if r20>18 else 2
    momentum+=8 if -2<=r5<=6 else 4 if r5<=9 else 1
    volume=10 if 1.05<=vr<=2.2 else 6 if .9<=vr<1.05 else 4 if vr>2.2 else 2
    rsi_score=10 if 48<=rsi<=68 else 7 if 42<=rsi<48 or 68<rsi<=72 else 3
    raw=trend+rel+momentum+volume+rsi_score
    return float(np.clip(raw,0,100))


def stock_leading_signal(row, meta=None, benchmark=None):
    meta=meta or {}
    benchmark=benchmark or {"ret20":0,"ret60":0}
    c=safe_float(row.get("Close"),0); ma20=safe_float(row.get("MA20"),c); ma60=safe_float(row.get("MA60"),c)
    dist=(c/ma20-1)*100 if ma20 else 0
    rsi=safe_float(row.get("RSI14"),50); vr=safe_float(row.get("VOL_RATIO"),1)
    ret5=safe_float(row.get("RET5"),0); ret20=safe_float(row.get("RET20"),0)
    accel=ret5-ret20/4
    rs20=ret20-safe_float(benchmark.get("ret20"),0)
    price=95 if -1<=dist<=3 else 86 if dist<=5 else 68 if dist<8 else 35
    rsi_s=94 if 48<=rsi<=63 else 84 if 43<=rsi<68 else 66 if rsi<72 else 30
    volume=92 if 1.05<=vr<=1.8 else 82 if .9<=vr<1.05 else 72 if vr<2.5 else 45
    accel_s=92 if .5<=accel<=5 else 80 if 0<=accel<.5 else 65 if accel>5 else 48
    rel=95 if rs20>=7 else 86 if rs20>=3 else 74 if rs20>=0 else 45
    structure=95 if c>=ma60 and ma20>=ma60 else 82 if c>=ma60 else 55 if c>=ma20 else 30
    liquidity=stock_liquidity_score(meta,row)
    volatility=stock_volatility_score(row)
    score=price*.17+rsi_s*.12+volume*.12+accel_s*.12+rel*.18+structure*.14+liquidity*.10+volatility*.05
    early=score>=72 and rsi<70 and dist<7 and rs20>=-1 and liquidity>=35
    return {"score":int(np.clip(round(score),0,100)),"early_buy":bool(early),"rs20":rs20,"dist20":dist,"rsi":rsi,"vr":vr,"accel":accel,
            "liquidity_score":round(liquidity,1),"volatility_score":round(volatility,1)}


def _stock_theme_match(code,name,meta):
    # 이름만으로 테마를 결정하지 않고 업종/이름/기존 테마를 합쳐 점수화합니다.
    text=f"{name} {meta.get('sector','')}".lower()
    best=[]
    for theme,keywords in THEME_LEXICON.items():
        hits=_theme_match(text,keywords)
        if hits: best.append((hits,theme))
    best.sort(reverse=True)
    return best


def _stock_candidate_gate(meta,row):
    # ETF와 달리 개별주는 유동성/규모를 먼저 거릅니다.
    mc=safe_float(meta.get("market_cap"),0)
    tv20=safe_float(row.get("TV20"),0)
    if mc>0 and mc<30_000_000_000: return False
    if tv20>0 and tv20<500_000_000: return False
    return True

def calculate_indicators_v2(df):
    if df is None or df.empty:
        return pd.DataFrame()
    d=df.copy()
    d["MA20"]=d["Close"].rolling(20).mean()
    d["MA60"]=d["Close"].rolling(60).mean()
    d["MA120"]=d["Close"].rolling(120).mean()
    d["MA200"]=d["Close"].rolling(200).mean()
    delta=d["Close"].diff()
    gain=delta.clip(lower=0).rolling(14).mean(); loss=(-delta).clip(upper=0).rolling(14).mean()
    rs=gain/loss.replace(0,np.nan)
    d["RSI14"]=100-(100/(1+rs))
    d["VOL20"]=d["Volume"].rolling(20).mean()
    d["VOL_RATIO"]=d["Volume"]/d["VOL20"].replace(0,np.nan)
    tr=pd.concat([d["High"]-d["Low"],(d["High"]-d["Close"].shift(1)).abs(),(d["Low"]-d["Close"].shift(1)).abs()],axis=1).max(axis=1)
    d["ATR14"]=tr.rolling(14).mean()
    d["ATR_PCT"]=d["ATR14"]/d["Close"].replace(0,np.nan)*100
    d["TRADING_VALUE"]=d["Close"]*d["Volume"]
    d["TV20"]=d["TRADING_VALUE"].rolling(20).mean()
    d["RET5"]=d["Close"].pct_change(5)*100
    d["RET20"]=d["Close"].pct_change(20)*100
    d["RET60"]=d["Close"].pct_change(60)*100
    d["RET120"]=d["Close"].pct_change(120)*100
    d["RET250"]=d["Close"].pct_change(250)*100
    d["HIGH20"]=d["High"].rolling(20).max(); d["LOW20"]=d["Low"].rolling(20).min()
    d["HIGH60"]=d["High"].rolling(60).max(); d["LOW60"]=d["Low"].rolling(60).min()
    d["VOLAT20"]=d["Close"].pct_change().rolling(20).std()*np.sqrt(252)*100
    return d


def theme_score_v2(theme_rows, bench_ret20=0, bench_ret60=0):
    # 과거 날짜에 한 종목만 유효한 테마도 해당 종목의 실제 당시
    # 수익률/상대강도/거래대금/모멘텀으로 테마 점수를 계산한다.
    # 2개 미만이라는 이유로 테마 전체를 삭제하지 않는다.
    if len(theme_rows)<1: return None
    vals=[]
    for r in theme_rows:
        r20=safe_float(r.get("ret20",r.get("R20")),np.nan); r60=safe_float(r.get("ret60",r.get("R60")),np.nan)
        if pd.isna(r20) or pd.isna(r60): continue
        b20=safe_float(r.get("bench_ret20",bench_ret20),bench_ret20); b60=safe_float(r.get("bench_ret60",bench_ret60),bench_ret60)
        meta=r.get("meta",{}) or {}
        row_raw=r.get("raw",r)
        liq=stock_liquidity_score(meta,row_raw)
        vals.append({"r20":r20,"r60":r60,"rs20":r20-b20,"rs60":r60-b60,
                     "vr":safe_float(r.get("vr",r.get("VR",1)),1),
                     "accel":safe_float(r.get("accel"),0),"rsi":safe_float(r.get("rsi",r.get("RSI",50)),50),
                     "lead":safe_float(r.get("lead_score"),50),"liq":liq})
    if len(vals)<1: return None
    x=pd.DataFrame(vals)
    def cs(v,lo,hi): return float(np.clip((v-lo)/(hi-lo)*100,0,100))
    r20=cs(x.r20.mean(),-10,15); r60=cs(x.r60.mean(),-15,30)
    rs20=cs(x.rs20.mean(),-10,12); rs60=cs(x.rs60.mean(),-15,20)
    vr=cs(x.vr.mean(),.8,2); breadth=float((x.r20>0).mean()*100)
    weighted_breadth=float(np.average((x.r20>0).astype(float)*100,weights=np.maximum(x.liq,10)))
    accel=cs(x.accel.mean(),-5,6); liq=float(x.liq.mean())
    rsi=float(np.clip(100-abs(float(x.rsi.mean())-58)*2.5,0,100))
    score=r20*.12+r60*.10+rs20*.16+rs60*.12+vr*.08+breadth*.10+weighted_breadth*.12+accel*.05+liq*.10+rsi*.05
    heat=(12 if x.rsi.mean()>=75 else 0)+(10 if x.r20.mean()>=12 else 0)
    return float(np.clip(score-heat,0,100))


def build_future_theme_engine_v2(force=False):
    cached=st.session_state.get("future_engine_cache")
    if cached and not force:
        try:
            if (datetime.now()-cached["time"]).total_seconds()<1800:
                return cached["data"]
        except Exception: pass
    universe=st.session_state.get("stock_universe") or load_stock_universe()
    st.session_state.stock_universe=universe
    meta_all=fetch_krx_stock_metadata_v2()
    if not meta_all:
        meta_all={c:stock_metadata(c) for c in list(universe)[:200]}
    benchmark_cache={"KOSPI":benchmark_snapshot_for_stock("005930"),"KOSDAQ":benchmark_snapshot_for_stock("035720")}
    candidates=[]
    for theme,keywords in THEME_LEXICON.items():
        matched=[]
        for code,name in universe.items():
            meta=meta_all.get(code,{})
            text=f"{name} {meta.get('sector','')}"
            hits=_theme_match(text,keywords)
            if hits:
                market=str(meta.get("market") or "KOSPI").upper()
                b=benchmark_cache.get("KOSDAQ" if market=="KOSDAQ" else "KOSPI",{})
                mc=safe_float(meta.get("market_cap"),0)
                matched.append((hits,mc,code,name,meta,b))
        if len(matched)<2: continue
        matched.sort(key=lambda z:(z[0],z[1]),reverse=True)
        rows=[]
        # 테마마다 시총 상위 + 키워드 적합도가 높은 종목을 제한적으로 계산
        for hits,mc,code,name,meta,b in matched[:6]:
            df=load_price_data(code)
            if df.empty or len(df)<65: continue
            d=calculate_indicators_v2(df); r=d.iloc[-1]
            c=safe_float(r.get("Close"),0)
            if not c: continue
            if not _stock_candidate_gate(meta,r): continue
            bench=b or {}
            raw=r.to_dict(); sig=stock_leading_signal(r,meta,bench)
            prev=d.iloc[-21] if len(d)>=86 else r
            prev_c=safe_float(prev.get("Close"),c); prev_ma20=safe_float(prev.get("MA20"),prev_c)
            prev_r20=safe_float(prev.get("RET20"),0); prev_r5=safe_float(prev.get("RET5"),0)
            prev_accel=prev_r5-prev_r20/4
            rows.append({"code":code,"name":name,"price":c,"rsi":safe_float(r.get("RSI14"),50),"vr":safe_float(r.get("VOL_RATIO"),1),
                         "ret20":safe_float(r.get("RET20"),0),"ret60":safe_float(r.get("RET60"),0),"ret5":safe_float(r.get("RET5"),0),
                         "trend":"상승" if c>=safe_float(r.get("MA20"),c) else "조정",
                         "ma60_gap":(c/safe_float(r.get("MA60"),c)-1)*100 if safe_float(r.get("MA60"),c) else 0,
                         "breadth":100 if c>=safe_float(r.get("MA20"),c) else 0,"accel":sig["accel"],"hits":hits,
                         "rs20":safe_float(r.get("RET20"),0)-safe_float(bench.get("ret20"),0),
                         "rs20_prev":prev_r20-safe_float(bench.get("ret20"),0),
                         "ret20_prev":prev_r20,"breadth_prev":100 if prev_c>=prev_ma20 else 0,"accel_prev":prev_accel,
                         "bench_ret20":safe_float(bench.get("ret20"),0),"bench_ret60":safe_float(bench.get("ret60"),0),
                         "lead_score":sig["score"],"meta":meta,"raw":raw})
        if len(rows)<2: continue
        score=theme_score_v2(rows,0,0)
        if score is None: continue
        lifecycle=_theme_lifecycle(rows,{"ret20":np.mean([x["bench_ret20"] for x in rows]),"ret60":np.mean([x["bench_ret60"] for x in rows])})
        final=float(np.clip(score*.75+lifecycle.get("score",0)*.25,0,100))
        if final<42: continue
        candidates.append({"theme":theme,"score":final,"base_score":score,"lifecycle":lifecycle,"rows":rows,"count":len(rows)})
    candidates.sort(key=lambda x:x["score"],reverse=True)
    candidates=candidates[:10]
    chain=[]; details={}; total=len(candidates)
    for rank,item in enumerate(candidates,1):
        stage=_theme_stage(item["score"],rank,total,item.get("lifecycle"))
        item["stage"]=stage; item["rank"]=rank
        item["reason"]=THEME_REASONS.get(item["theme"],"업종·테마 연결성, 상대강도, 거래활동, 추세 확산을 함께 평가합니다.")
        chain.append((item["theme"],stage)); details[item["theme"]]=item
    data={"chain":chain,"details":details,"benchmark":benchmark_cache,"updated":datetime.now().strftime("%Y-%m-%d %H:%M"),"engine":"STOCK_ENGINE_V2"}
    st.session_state.future_engine_cache={"time":datetime.now(),"data":data}
    return data


def _find_theme_for_etf_v2(code):
    code=_normalize_stock_code(code)
    engine=build_future_theme_engine_v2()
    for theme,info in engine.get("details",{}).items():
        if any(_normalize_stock_code(x.get("code"))==code for x in info.get("rows",[])):
            return theme,info.get("rows",[])
    return None,[]


def _theme_stock_rank_v2(item, benchmark_ret20=0):
    ranked=[]
    for row in item.get("rows",[]):
        code=row.get("code")
        df=load_price_data(code) if code else pd.DataFrame()
        if df.empty: continue
        d=calculate_indicators_v2(df); r=d.iloc[-1]
        meta=row.get("meta") or stock_metadata(code)
        b={"ret20":safe_float(row.get("bench_ret20"),benchmark_ret20),"ret60":safe_float(row.get("bench_ret60"),0)}
        sig=stock_leading_signal(r,meta,b); zone=validated_price_zone(r)
        rel=stock_relative_score(r,b); tech=stock_technical_score(r,b); liq=stock_liquidity_score(meta,r); vol=stock_volatility_score(r)
        score=sig["score"]*.40+tech*.25+rel*.15+liq*.10+vol*.10
        ranked.append({**row,"signal_score":round(float(score),1),"zone":zone,"lead":sig,"raw":r,
                       "technical_score":round(tech,1),"relative_score":round(rel,1),"liquidity_score":round(liq,1),"volatility_score":round(vol,1),
                       "rsi":safe_float(r.get("RSI14"),50),"ret20":safe_float(r.get("RET20"),0)})
    ranked.sort(key=lambda x:(x["signal_score"],x.get("ret20",-999)),reverse=True)
    return ranked


def radar_target_stocks_v2():
    targets={}
    try:
        engine=build_future_theme_engine_v2()
        for info in engine.get("details",{}).values():
            for row in info.get("rows",[]):
                code=_normalize_stock_code(row.get("code")); name=row.get("name") or get_stock_name(code)
                if code: targets[code]=name
    except Exception: pass
    # ETF식으로 테마에만 묶이지 않도록 시총/유동성 상위주를 별도 후보군으로 추가
    meta_all=fetch_krx_stock_metadata_v2()
    liquid=[]
    for code,meta in meta_all.items():
        mc=safe_float(meta.get("market_cap"),0)
        if mc>=100_000_000_000:
            liquid.append((mc,code,meta.get("name") or get_stock_name(code)))
    liquid.sort(reverse=True)
    for _,code,name in liquid[:40]: targets[code]=name
    for raw in st.session_state.get("holdings",{}):
        code=_normalize_stock_code(raw); targets[code]=get_stock_name(code)
    return targets


def build_radar_data_v2(force=False):
    now=datetime.now(); cached=st.session_state.get("radar_cache"); targets=radar_target_stocks_v2(); key=tuple(sorted(targets))
    if cached and not force and cached.get("target_key")==key:
        try:
            if (now-cached["time"]).total_seconds()<300: return cached
        except Exception: pass
    rows=[]
    for code,name in targets.items():
        df=load_price_data(code)
        if df.empty or len(df)<65: continue
        d=calculate_indicators_v2(df); r=d.iloc[-1]
        meta=stock_metadata(code); bench=benchmark_snapshot_for_stock(code)
        if not _stock_candidate_gate(meta,r): continue
        current=safe_float(r.get("Close"),0); ma20=safe_float(r.get("MA20"),current); ma60=safe_float(r.get("MA60"),current)
        sig=stock_leading_signal(r,meta,bench); tech=stock_technical_score(r,bench); rel=stock_relative_score(r,bench); liq=stock_liquidity_score(meta,r); size=stock_size_score(meta); vol=stock_volatility_score(r)
        theme_name,theme_members=_find_theme_for_etf_v2(code)
        theme_sc=theme_score_v2(theme_members,bench.get("ret20",0),bench.get("ret60",0)) if theme_members else 0
        lifecycle=_theme_lifecycle(theme_members,bench) if theme_members else {"score":0,"state":"관찰"}
        zone=validated_price_zone(r)
        pscore={"매수구간":100,"눌림대기":70,"추격금지":25,"무효":0}.get(zone.get("state"),0)
        opportunity=float(np.clip(tech*.30+rel*.20+liq*.15+size*.05+sig["score"]*.20+vol*.10,0,100))
        overheat=radar_overheat_score({"rsi":sig["rsi"],"ret5":safe_float(r.get("RET5"),0),"dist20":sig["dist20"],"vr":sig["vr"]})
        cross=sig["score"]*.30+opportunity*.30+pscore*.15+lifecycle.get("score",0)*.10+rel*.10+liq*.05
        if lifecycle.get("state")=="쇠퇴": cross-=10
        if lifecycle.get("state")=="과열": cross-=7
        if overheat>=65: cross-=10
        rows.append({"code":code,"name":name,"price":current,"rsi":sig["rsi"],"vr":sig["vr"],"atr14":safe_float(r.get("ATR14"),0),"atr_pct":safe_float(r.get("ATR_PCT"),0),"trading_value":safe_float(r.get("TRADING_VALUE"),0),
                     "ret5":safe_float(r.get("RET5"),0),"ret20":safe_float(r.get("RET20"),0),"ret60":safe_float(r.get("RET60"),0),"dist20":sig["dist20"],"above20":current>=ma20,"above60":current>=ma60,
                     "rs20":safe_float(r.get("RET20"),0)-bench.get("ret20",0),"theme":theme_name or "기타","stage":(next((s for t,s in get_future_chain() if t==theme_name),"기타") if theme_name else "기타"),
                     "future_theme":theme_name or "미래테마 미연결","future_theme_related":bool(theme_name),"opportunity":int(round(opportunity)),"overheat":int(overheat),"theme_score":round(float(theme_sc or 0),1),
                     "lifecycle_score":round(float(lifecycle.get("score",0)),1),"lifecycle_state":lifecycle.get("state","관찰"),"lead_score":sig["score"],"price_zone":zone.get("state","확인"),"cross_score":int(np.clip(round(cross),0,100)),
                     "cross_state":"🔥 최우선 후보" if cross>=80 and zone.get("state")=="매수구간" and overheat<65 else "🟢 우선 관찰" if cross>=70 else "🟡 확인 필요" if cross>=55 else "⚪ 대기",
                     "market":bench.get("market",stock_market(code)),"market_cap":safe_float(meta.get("market_cap"),0),"liquidity_score":round(liq,1),"size_score":round(size,1),"relative_score":round(rel,1),"technical_score":round(tech,1),"volatility_score":round(vol,1),"raw":r.to_dict(),"held":code in st.session_state.get("holdings",{})})
    data={"time":now,"rows":rows,"benchmark":get_benchmark_metrics(),"target_key":key,"engine":"STOCK_ENGINE_V2"}; st.session_state.radar_cache=data; return data


def _future_theme_selected_map_v2(benchmark_ret20=0):
    selected={}; engine=build_future_theme_engine_v2()
    for theme_rank,(theme,_stage) in enumerate(engine.get("chain",[]),1):
        info=engine.get("details",{}).get(theme,{})
        ranked=_theme_stock_rank_v2(info,benchmark_ret20)
        for stock_rank,x in enumerate(ranked[:3],1):
            code=_normalize_stock_code(x.get("code"))
            if not code: continue
            rec={"theme":theme,"theme_rank":theme_rank,"stock_rank":stock_rank,"signal_score":safe_float(x.get("signal_score")),"theme_score":safe_float(info.get("score")),"meta":x.get("meta",{})}
            prev=selected.get(code)
            if prev is None or (rec["theme_rank"],rec["stock_rank"],-rec["signal_score"])<(prev["theme_rank"],prev["stock_rank"],-prev["signal_score"]): selected[code]=rec
    return selected


def build_final_targets_v2(radar_data):
    rows=radar_data.get("rows",[]) if radar_data else []
    selected=_future_theme_selected_map_v2(0)
    targets=[]
    for item in rows:
        code=_normalize_stock_code(item.get("code")); rel=selected.get(code)
        if not rel: continue
        # 개별주는 ETF보다 유동성/규모를 먼저 통과시킨 뒤 기술·가격을 봅니다.
        if item.get("liquidity_score",0)<35: continue
        if item.get("market_cap",0)>0 and item.get("market_cap",0)<30_000_000_000: continue
        if item.get("opportunity",0)<58 or item.get("rsi",100)>=74 or item.get("ret5",999)>=10 or item.get("price_zone")=="무효": continue
        theme_rank=int(rel["theme_rank"]); stock_rank=int(rel["stock_rank"]); theme_score=safe_float(rel["theme_score"]); cross=safe_float(item.get("cross_score"))
        future_anchor=max(40.0,100-(theme_rank-1)*8)
        # ETF와 달리 개별주에서는 회사 규모/유동성/상대강도를 최종점수에 명시적으로 반영
        final=cross*.55+theme_score*.15+safe_float(item.get("relative_score"))*.10+safe_float(item.get("liquidity_score"))*.10+safe_float(item.get("size_score"))*.05+safe_float(item.get("volatility_score"))*.05+future_anchor*.10
        final-=max(0,stock_rank-1)*1.5
        if theme_rank==1 and cross>=70: final+=3
        x=dict(item); x.update({"future_theme_selected":True,"future_theme":rel["theme"],"future_theme_rank":theme_rank,"future_stock_rank":stock_rank,"future_theme_score":round(theme_score,1),"future_theme_anchor":round(future_anchor,1),"future_theme_lead":rel["signal_score"],"final_score":round(float(np.clip(final,0,100)),1)})
        targets.append(x)
    targets.sort(key=lambda x:(x.get("final_score",0),x.get("cross_score",0),-x.get("future_theme_rank",99),x.get("relative_score",0)),reverse=True)
    for i,x in enumerate(targets,1):
        fs=safe_float(x.get("final_score")); cross=safe_float(x.get("cross_score")); zone=x.get("price_zone"); heat=safe_float(x.get("overheat"))
        state="🔥 최종 타겟" if fs>=82 and cross>=74 and zone=="매수구간" and heat<65 else "🟢 최종 우선" if fs>=72 else "🟡 최종 관찰" if fs>=60 else "⚪ 대기"
        x["final_rank"]=i; x["final_state"]=state; x["final_reason"]=f"시장 {x.get('market','-')} · 업종/테마 {x.get('future_theme','-')} · 상대강도 {x.get('relative_score',0):.0f} · 유동성 {x.get('liquidity_score',0):.0f} · 가격구간 {zone}"
    return targets


def integrated_decision_engine_v2(d,code):
    if d is None or d.empty or len(d)<120: return {"state":"데이터 부족","action":"관찰","theme_score":0,"lead_score":0,"price_score":0,"hold_score":0,"exit_score":0}
    r=d.iloc[-1]; bench=benchmark_snapshot_for_stock(code); meta=stock_metadata(code); theme,rows=_find_theme_for_etf_v2(code)
    ts=theme_score_v2(rows,bench.get("ret20",0),bench.get("ret60",0)) if rows else 0; life=_theme_lifecycle(rows,bench) if rows else {"score":0,"state":"관찰"}
    lead=stock_leading_signal(r,meta,bench); zone=validated_price_zone(r); tech=stock_technical_score(r,bench); rel=stock_relative_score(r,bench); liq=stock_liquidity_score(meta,r)
    long=long_term_horizon(d); overheat=radar_overheat_score({"rsi":lead["rsi"],"ret5":safe_float(r.get("RET5")),"dist20":lead["dist20"],"vr":lead["vr"]})
    structural=bool(long.get("structural_break",False)); trend_break=safe_float(r.get("Close"))<safe_float(r.get("MA60")) and safe_float(r.get("MA20"))<safe_float(r.get("MA60"))
    if structural: state,action,exit_score="EXIT / REASSESS","🔴 장기 구조 훼손 · 신규매수 중단",95
    elif trend_break and lead["score"]<55: state,action,exit_score="REDUCE","🔴 중기 추세·선행 동시 약화",80
    elif overheat>=65: state,action,exit_score="TRIM / WAIT","🟠 과열 · 신규매수보다 분할익절/눌림 확인",62
    elif zone["state"]=="매수구간" and lead["score"]>=72 and rel>=60 and liq>=35: state,action,exit_score="BUY / WATCH_BUY","🟢 개별주 조건 충족 · 가격구간 내 분할접근",15
    elif zone["state"] in {"눌림대기","추격금지"} and lead["score"]>=65: state,action,exit_score="WAIT","🟡 방향은 양호하지만 가격 대기",30
    else: state,action,exit_score="HOLD / OBSERVE","⚪ 조건 확인 중",20
    return {"state":state,"action":action,"theme_score":round(float(ts or 0),1),"lead_score":lead["score"],"price_score":{"매수구간":92,"눌림대기":70,"추격금지":25,"무효":10}.get(zone["state"],10),"hold_score":round(float(long.get("score",0))),"exit_score":exit_score,
            "theme":theme,"lifecycle":life.get("state","관찰"),"relative_score":round(rel,1),"liquidity_score":round(liq,1),"technical_score":round(tech,1),"market":bench.get("market"),"price_zone":zone["state"]}


# ============================================================
# STOCK ENGINE V5 : INVESTOR FLOW + VALUATION LAYER
# ============================================================
try:
    from pykrx import stock as _pykrx_stock
    PYKRX_AVAILABLE = True
except Exception:
    _pykrx_stock = None
    PYKRX_AVAILABLE = False

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_investor_flow_v5(code, days=20):
    """실제 KRX 투자자별 거래실적을 pykrx가 설치된 경우에만 사용.
    데이터가 없으면 0이 아니라 None을 반환하여 '수급 중립'과 '데이터 없음'을 구분합니다.
    """
    code=_normalize_stock_code(code)
    if not PYKRX_AVAILABLE or not code:
        return None
    try:
        end=datetime.now().strftime('%Y%m%d')
        start=(datetime.now()-pd.Timedelta(days=max(days*3,45))).strftime('%Y%m%d')
        x=_pykrx_stock.get_market_trading_value_by_investor(start,end,code)
        if x is None or x.empty:
            return None
        x=x.copy()
        # pykrx 버전별 컬럼명 차이를 흡수
        cols={str(c).strip():c for c in x.columns}
        def pick(*names):
            for n in names:
                if n in cols: return cols[n]
            return None
        inst=pick('기관합계','기관계')
        foreign=pick('외국인')
        if inst is None and foreign is None: return None
        inst_v=float(pd.to_numeric(x[inst],errors='coerce').fillna(0).tail(days).sum()) if inst else 0.0
        foreign_v=float(pd.to_numeric(x[foreign],errors='coerce').fillna(0).tail(days).sum()) if foreign else 0.0
        return {'institution_net20':inst_v,'foreign_net20':foreign_v,'available':True}
    except Exception:
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fundamental_v5(code):
    """KRX/PyKRX에서 확인 가능한 PER/PBR/배당수익률을 보조지표로 사용.
    실적성장률이 없으면 추정하지 않습니다.
    """
    code=_normalize_stock_code(code)
    if not PYKRX_AVAILABLE or not code:
        return {}
    try:
        end=datetime.now().strftime('%Y%m%d')
        start=(datetime.now()-pd.Timedelta(days=10)).strftime('%Y%m%d')
        x=_pykrx_stock.get_market_fundamental_by_date(start,end,code)
        if x is None or x.empty: return {}
        r=x.iloc[-1]
        return {'PER':safe_float(r.get('PER'),np.nan),'PBR':safe_float(r.get('PBR'),np.nan),'DIV':safe_float(r.get('DIV'),np.nan)}
    except Exception:
        return {}

def investor_flow_score_v5(flow, tv20=0):
    if not flow or not flow.get('available'): return 50.0
    scale=max(abs(tv20 or 0)*20,1.0)
    f=flow.get('foreign_net20',0)/scale*100
    i=flow.get('institution_net20',0)/scale*100
    # 특정 투자자 한쪽만 과대평가하지 않도록 완만하게 클리핑
    return float(np.clip(50 + f*0.28 + i*0.32,0,100))

def valuation_score_v5(fund):
    per=safe_float(fund.get('PER'),np.nan); pbr=safe_float(fund.get('PBR'),np.nan)
    if pd.isna(per) and pd.isna(pbr): return 50.0
    scores=[]
    if not pd.isna(per):
        scores.append(float(np.clip(100-(per/40)*100,10,95)) if per>0 else 50.0)
    if not pd.isna(pbr):
        scores.append(float(np.clip(100-(pbr/5)*100,10,95)) if pbr>0 else 50.0)
    return float(np.mean(scores)) if scores else 50.0

def enrich_stock_factors_v5(code, row, meta):
    tv20=safe_float(row.get('TV20'),0)
    flow=fetch_investor_flow_v5(code,20)
    fund=fetch_fundamental_v5(code)
    fs=investor_flow_score_v5(flow,tv20)
    vs=valuation_score_v5(fund)
    return flow,fund,fs,vs

def stock_factor_score_v5(code,row,meta,bench,base_sig,tech,rel,liq,size,vol):
    flow,fund,flow_score,val_score=enrich_stock_factors_v5(code,row,meta)
    # 실적성장 데이터가 없는 상태에서 이를 임의 추정하지 않고
    # 수급 12 + 가치 6을 추가. 나머지는 기존 검증된 기술/상대강도 계층을 유지.
    score=(base_sig['score']*.22 + tech*.20 + rel*.16 + liq*.10 + size*.07 + vol*.07 + flow_score*.12 + val_score*.06)
    return float(np.clip(score,0,100)),flow,fund,flow_score,val_score

# 기존 V2 live 함수들을 V5 factor-aware 함수로 감싼다.
_legacy_build_radar_data_v5 = build_radar_data_v2

def build_radar_data_v5(force=False):
    data=_legacy_build_radar_data_v5(force=force)
    rows=data.get('rows',[])
    for x in rows:
        try:
            code=x.get('code'); r=pd.Series(x.get('raw',{})); meta=stock_metadata(code); bench=benchmark_snapshot_for_stock(code)
            sig=stock_leading_signal(r,meta,bench); tech=safe_float(x.get('technical_score'),50); rel=safe_float(x.get('relative_score'),50); liq=safe_float(x.get('liquidity_score'),50); size=safe_float(x.get('size_score'),50); vol=safe_float(x.get('volatility_score'),50)
            score,flow,fund,flow_score,val_score=stock_factor_score_v5(code,r,meta,bench,sig,tech,rel,liq,size,vol)
            x['flow_score']=round(flow_score,1); x['valuation_score']=round(val_score,1); x['factor_score']=round(score,1)
            x['foreign_net20']=safe_float((flow or {}).get('foreign_net20'),np.nan); x['institution_net20']=safe_float((flow or {}).get('institution_net20'),np.nan)
            x['per']=safe_float((fund or {}).get('PER'),np.nan); x['pbr']=safe_float((fund or {}).get('PBR'),np.nan); x['dividend_yield']=safe_float((fund or {}).get('DIV'),np.nan)
            # 수급/가치 데이터가 실제 존재할 때만 최종 cross에 반영
            if flow and flow.get('available'):
                x['cross_score']=int(np.clip(round(safe_float(x.get('cross_score'),50)*.78+flow_score*.12+val_score*.10),0,100))
        except Exception:
            continue
    data['engine']='STOCK_ENGINE_V5_FLOW_FUNDAMENTAL'; st.session_state.radar_cache=data; return data

_legacy_build_final_targets_v5 = build_final_targets_v2
def build_final_targets_v5(radar_data):
    targets=_legacy_build_final_targets_v5(radar_data)
    for x in targets:
        # 실제 수급이 있는 경우 최종점수에만 추가. 데이터 부재를 0점 처리하지 않음.
        if np.isfinite(safe_float(x.get('flow_score'),np.nan)):
            fs=safe_float(x.get('final_score'),0)
            flow=safe_float(x.get('flow_score'),50); val=safe_float(x.get('valuation_score'),50)
            x['final_score']=round(float(np.clip(fs*.88+flow*.07+val*.05,0,100)),1)
        x['final_reason']=f"시장 {x.get('market','-')} · 미래테마 {x.get('future_theme','-')} · 상대강도 {x.get('relative_score',0):.0f} · 수급 {x.get('flow_score',50):.0f} · 가치 {x.get('valuation_score',50):.0f} · 가격구간 {x.get('price_zone','-')}"
    targets.sort(key=lambda z:(safe_float(z.get('final_score')),safe_float(z.get('cross_score')),safe_float(z.get('relative_score'))),reverse=True)
    return targets



# ============================================================
# V6: EARNINGS / BUSINESS QUALITY LAYER
# ============================================================

@st.cache_data(ttl=21600, show_spinner=False)
def fetch_earnings_quality_v6(code):
    """최근 공시/재무제표에서 확인 가능한 매출·영업이익 성장과 수익성 지표.
    데이터가 없으면 None/NaN으로 유지하여 결측을 감점으로 오인하지 않습니다.
    """
    out={"available":False}
    try:
        ticker=yf.Ticker(_normalize_stock_code(code)+".KS")
        inc=ticker.income_stmt
        bs=ticker.balance_sheet
        if inc is None or inc.empty:
            ticker=yf.Ticker(_normalize_stock_code(code)+".KQ")
            inc=ticker.income_stmt; bs=ticker.balance_sheet
        if inc is None or inc.empty: return out
        def pick(frame,names):
            for n in names:
                if n in frame.index:
                    vals=pd.to_numeric(frame.loc[n],errors='coerce').dropna()
                    if len(vals): return vals
            return pd.Series(dtype=float)
        rev=pick(inc,["Total Revenue","Operating Revenue"])
        op=pick(inc,["Operating Income","Operating Income Loss"])
        net=pick(inc,["Net Income","Net Income Common Stockholders"])
        assets=pick(bs,["Total Assets"])
        equity=pick(bs,["Stockholders Equity","Common Stock Equity","Total Equity Gross Minority Interest"])
        def yoy(v):
            if len(v)<2 or v.iloc[1]==0: return np.nan
            return float((v.iloc[0]/v.iloc[1]-1)*100)
        rev_g=yoy(rev); op_g=yoy(op); net_g=yoy(net)
        op_margin=float(op.iloc[0]/rev.iloc[0]*100) if len(op) and len(rev) and rev.iloc[0] else np.nan
        roe=float(net.iloc[0]/equity.iloc[0]*100) if len(net) and len(equity) and equity.iloc[0] else np.nan
        asset_g=yoy(assets)
        out.update({"available":True,"revenue_growth":rev_g,"operating_income_growth":op_g,
                    "net_income_growth":net_g,"operating_margin":op_margin,"roe":roe,"asset_growth":asset_g})
        return out
    except Exception:
        return out


def earnings_quality_score_v6(e):
    if not e or not e.get("available"): return 50.0
    rg=safe_float(e.get("revenue_growth"),np.nan); og=safe_float(e.get("operating_income_growth"),np.nan)
    ng=safe_float(e.get("net_income_growth"),np.nan); om=safe_float(e.get("operating_margin"),np.nan); roe=safe_float(e.get("roe"),np.nan)
    def scale(v,lo,hi):
        if not np.isfinite(v): return np.nan
        return float(np.clip((v-lo)/(hi-lo)*100,0,100))
    parts=[]; weights=[]
    for v,w,lo,hi in [(rg,.28,-20,30),(og,.30,-30,50),(ng,.17,-30,50),(om,.10,0,25),(roe,.15,-5,25)]:
        z=scale(v,lo,hi)
        if np.isfinite(z): parts.append(z*w); weights.append(w)
    if not parts: return 50.0
    return float(np.clip(sum(parts)/sum(weights),0,100))


def stock_factor_score_v6(code,row,meta,bench,sig,tech,rel,liq,size,vol):
    # 주식 전용 기본 구조: 기술 20 / 상대강도 15 / 선행 15 / 유동성 10 / 규모 5 /
    # 변동성 5 / 수급 10 / 가치 5 / 실적·기업체력 15.
    base,flow,fund,flow_score,val_score=stock_factor_score_v5(code,row,meta,bench,sig,tech,rel,liq,size,vol)
    earn=fetch_earnings_quality_v6(code)
    earn_score=earnings_quality_score_v6(earn)
    score=(sig['score']*.15 + tech*.20 + rel*.15 + liq*.10 + size*.05 + vol*.05
           + flow_score*.10 + val_score*.05 + earn_score*.15)
    return float(np.clip(score,0,100)),flow,fund,flow_score,val_score,earn,earn_score

_legacy_build_radar_data_v5=build_radar_data_v5
def build_radar_data_v6(force=False):
    data=_legacy_build_radar_data_v5(force=force)
    rows=data.get('rows',[])
    for x in rows:
        try:
            code=x.get('code'); r=pd.Series(x.get('raw',{})); meta=stock_metadata(code); bench=benchmark_snapshot_for_stock(code)
            sig=stock_leading_signal(r,meta,bench); tech=safe_float(x.get('technical_score'),50); rel=safe_float(x.get('relative_score'),50); liq=safe_float(x.get('liquidity_score'),50); size=safe_float(x.get('size_score'),50); vol=safe_float(x.get('volatility_score'),50)
            score,flow,fund,flow_score,val_score,earn,earn_score=stock_factor_score_v6(code,r,meta,bench,sig,tech,rel,liq,size,vol)
            x.update({'flow_score':round(flow_score,1),'valuation_score':round(val_score,1),'earnings_score':round(earn_score,1),'factor_score':round(score,1)})
            for k in ['revenue_growth','operating_income_growth','net_income_growth','operating_margin','roe']:
                x[k]=safe_float(earn.get(k),np.nan)
            if flow and flow.get('available'):
                x['cross_score']=int(np.clip(round(safe_float(x.get('cross_score'),50)*.72+flow_score*.10+val_score*.05+earn_score*.13),0,100))
            else:
                x['cross_score']=int(np.clip(round(safe_float(x.get('cross_score'),50)*.87+earn_score*.13),0,100))
        except Exception:
            continue
    data['engine']='STOCK_ENGINE_V6_EARNINGS'; st.session_state.radar_cache=data; return data

_legacy_build_final_targets_v6=build_final_targets_v5
def build_final_targets_v6(radar_data):
    targets=_legacy_build_final_targets_v6(radar_data)
    for x in targets:
        fs=safe_float(x.get('final_score'),0); earn=safe_float(x.get('earnings_score'),50)
        x['final_score']=round(float(np.clip(fs*.85+earn*.15,0,100)),1)
        x['final_reason']=f"시장 {x.get('market','-')} · 미래테마 {x.get('future_theme','-')} · 상대강도 {x.get('relative_score',0):.0f} · 수급 {x.get('flow_score',50):.0f} · 실적체력 {x.get('earnings_score',50):.0f} · 가치 {x.get('valuation_score',50):.0f} · 가격구간 {x.get('price_zone','-')}"
    targets.sort(key=lambda z:(safe_float(z.get('final_score')),safe_float(z.get('cross_score')),safe_float(z.get('relative_score'))),reverse=True)
    for i,x in enumerate(targets,1):
        x['final_rank']=i
    return targets


# Override legacy ETF-shaped live functions with the stock-specific engine.
calculate_indicators = calculate_indicators_v2
load_market_benchmark = load_market_benchmark_v2
build_future_theme_engine = build_future_theme_engine_v2
_find_theme_for_etf = _find_theme_for_etf_v2
_theme_stock_rank = _theme_stock_rank_v2
theme_score = theme_score_v2
radar_target_stocks = radar_target_stocks_v2
build_radar_data = build_radar_data_v6
_future_theme_selected_map = _future_theme_selected_map_v2
build_final_targets = build_final_targets_v6
integrated_decision_engine = integrated_decision_engine_v2



# ============================================================
# V8 VALIDATION-LOCKED STOCK ENGINE
# ============================================================
# 통계적 검증을 위해 현재 시점에서만 알 수 있는 실적/시총/수급을
# 과거 OOS 신호 점수에 섞지 않는다. V6의 실적/수급 값은 화면 보조정보로
# 유지하고, 최종 검증점수는 과거 가격데이터만으로 계산 가능한 공통식으로 고정한다.

def stock_validation_score(row, bench, meta=None):
    meta = meta or {}
    sig = stock_leading_signal(row, meta, bench)
    tech = stock_technical_score(row, bench)
    rel = stock_relative_score(row, bench)
    liq = stock_liquidity_score({}, row)  # 과거 TV20만 사용
    vol = stock_volatility_score(row)
    score = (sig["score"]*.25 + tech*.25 + rel*.20 + liq*.15 + vol*.15)
    return float(np.clip(score,0,100)), sig, tech, rel, liq, vol

def build_radar_data_v8(force=False):
    data = build_radar_data_v2(force=force)
    for x in data.get("rows",[]):
        try:
            r=pd.Series(x.get("raw",{})); code=x.get("code")
            bench=benchmark_snapshot_for_stock(code)
            score,sig,tech,rel,liq,vol=stock_validation_score(r,bench,{})
            x.update({"validation_score":round(score,1),"technical_score":round(tech,1),
                      "relative_score":round(rel,1),"liquidity_score":round(liq,1),
                      "volatility_score":round(vol,1),"lead_score":round(sig["score"],1)})
            # V8 cross = 과거에도 계산 가능한 변수만 사용
            zone=validated_price_zone(r)
            pscore={"매수구간":100,"눌림대기":70,"추격금지":25,"무효":0}.get(zone.get("state"),0)
            life=safe_float(x.get("lifecycle_score"),50)
            cross=score*.60+pscore*.15+life*.10+rel*.10+liq*.05
            if x.get("lifecycle_state")=="쇠퇴": cross-=10
            elif x.get("lifecycle_state")=="과열": cross-=7
            if safe_float(x.get("overheat"),0)>=65: cross-=10
            x["cross_score_v8"]=int(np.clip(round(cross),0,100))
            x["cross_score"]=x["cross_score_v8"]
        except Exception:
            continue
    data["engine"]="STOCK_ENGINE_V8_VALIDATION_LOCKED"
    st.session_state.radar_cache=data
    return data

def build_final_targets_v8(radar_data):
    rows=radar_data.get("rows",[]) if radar_data else []
    selected=_future_theme_selected_map_v2(0)
    targets=[]
    for item in rows:
        code=_normalize_stock_code(item.get("code")); relrec=selected.get(code)
        if not relrec: continue
        if safe_float(item.get("liquidity_score"),0)<30: continue
        if safe_float(item.get("opportunity"),0)<55: continue
        if safe_float(item.get("rsi"),100)>=74 or safe_float(item.get("ret5"),999)>=10: continue
        if item.get("price_zone")=="무효": continue
        tr=int(relrec["theme_rank"]); sr=int(relrec["stock_rank"])
        theme=safe_float(relrec["theme_score"]); anchor=max(40,100-(tr-1)*8)
        cross=safe_float(item.get("cross_score_v8"),50)
        final=cross*.65+theme*.15+safe_float(item.get("relative_score"),50)*.10+safe_float(item.get("liquidity_score"),50)*.10
        final+=anchor*.05-max(0,sr-1)*1.5
        if tr==1 and cross>=70: final+=3
        x=dict(item); x.update({"future_theme_selected":True,"future_theme":relrec["theme"],
            "future_theme_rank":tr,"future_stock_rank":sr,"future_theme_score":round(theme,1),
            "future_theme_anchor":round(anchor,1),"final_score":round(float(np.clip(final,0,100)),1)})
        targets.append(x)
    targets.sort(key=lambda z:(safe_float(z.get("final_score")),safe_float(z.get("cross_score_v8")),safe_float(z.get("relative_score"))),reverse=True)
    for i,x in enumerate(targets,1):
        fs=safe_float(x.get("final_score")); cross=safe_float(x.get("cross_score_v8")); zone=x.get("price_zone"); heat=safe_float(x.get("overheat"))
        x["final_rank"]=i
        x["final_state"]="🔥 최종 타겟" if fs>=82 and cross>=74 and zone=="매수구간" and heat<65 else "🟢 최종 우선" if fs>=72 else "🟡 최종 관찰" if fs>=60 else "⚪ 대기"
        x["final_reason"]=f"시장 {x.get('market','-')} · 미래테마 {x.get('future_theme','-')} · 상대강도 {x.get('relative_score',0):.0f} · 검증점수 {x.get('validation_score',0):.0f} · 가격구간 {zone}"
    return targets

# 실전과 TRUE WF가 동일한 '검증 가능' 산식을 사용하도록 잠금
build_radar_data=build_radar_data_v8
build_final_targets=build_final_targets_v8


# ============================================================
# V9 COMMON ENGINE — LIVE / TRUE-WF 공통 최종타겟 산식
# ============================================================
def common_target_score_v9(row, bench, theme_score, theme_rank, stock_rank, lifecycle_score=50, lifecycle_state="관찰"):
    """현재 실전과 과거 WF가 동일하게 호출하는 개별주 최종타겟 산식.
    입력은 해당 날짜에 실제 알 수 있었던 가격/거래량/시장 데이터만 사용한다.
    """
    row = pd.Series(row if isinstance(row, dict) else row.to_dict())
    bench = bench or {}
    score, sig, tech, rel, liq, vol = stock_validation_score(row, bench, {})
    zone = validated_price_zone(row)
    pscore = {"매수구간":100,"눌림대기":70,"추격금지":25,"무효":0}.get(zone.get("state"),0)
    opp = float(np.clip(tech*.30 + rel*.25 + liq*.20 + sig["score"]*.15 + vol*.10, 0, 100))
    heat = radar_overheat_score({"rsi":sig["rsi"],"ret5":safe_float(row.get("RET5", row.get("R5")),0),"dist20":sig["dist20"],"vr":sig["vr"]})
    cross = score*.60 + pscore*.15 + safe_float(lifecycle_score,50)*.10 + rel*.10 + liq*.05
    if lifecycle_state == "쇠퇴": cross -= 10
    elif lifecycle_state == "과열": cross -= 7
    if heat >= 65: cross -= 10
    cross=float(np.clip(cross,0,100))
    anchor=max(40.0,100-(int(theme_rank)-1)*8)
    final=cross*.65 + safe_float(theme_score,50)*.15 + rel*.10 + liq*.10 + anchor*.05
    final -= max(0,int(stock_rank)-1)*1.5
    if int(theme_rank)==1 and cross>=70: final += 3
    return {
        "validation_score":float(score),"lead_score":float(sig["score"]),"technical_score":float(tech),
        "relative_score":float(rel),"liquidity_score":float(liq),"volatility_score":float(vol),
        "opportunity":float(opp),"overheat":float(heat),"price_zone":zone.get("state"),
        "cross_score":float(cross),"final_score":float(np.clip(final,0,100)),"future_theme_anchor":float(anchor),
    }

def common_target_gate_v9(calc, row):
    # LIVE/WF 공통 기본 게이트. 기존 FINAL의 후보 생성 기준은 유지합니다.
    rsi = safe_float(row.get("rsi", row.get("RSI", row.get("RSI14", 100))), 100)
    ret5 = safe_float(row.get("ret5", row.get("RET5", row.get("R5", 999))), 999)
    return (calc["liquidity_score"] >= 30 and calc["opportunity"] >= 55 and
            rsi < 74 and ret5 < 10 and calc["price_zone"] != "무효")


def final_target_gate_v11(calc, row, market_pass=False, lifecycle_state="관찰"):
    """FINAL V16: D+M을 하드 게이트로 유지하고 FINAL은 랭킹 레이어로 운용."""
    return bool(
        market_pass
        and calc.get("price_zone") == "매수구간"
        and calc.get("liquidity_score", 0) >= 30
        and calc.get("opportunity", 0) >= 55
        and calc.get("final_score", 0) >= 65
        and calc.get("cross_score", 0) >= 60
        and lifecycle_state not in ("쇠퇴",)
    )

def final_target_rank_v11(calc, row, lifecycle_state="관찰"):
    """D+M 후보를 최종타겟 우선순위로 정렬. 과열/추격은 탈락 대신 감점."""
    rsi = safe_float(row.get("rsi", row.get("RSI", row.get("RSI14", 100))), 100)
    ret5 = safe_float(row.get("ret5", row.get("RET5", row.get("R5", 999))), 999)
    score = float(calc.get("final_score", 0))
    if calc.get("price_zone") == "매수구간": score += 8
    if calc.get("cross_score", 0) >= 70: score += 5
    if calc.get("liquidity_score", 0) >= 50: score += 3
    if lifecycle_state == "성장": score += 4
    if lifecycle_state == "과열": score -= 8
    if calc.get("overheat", 100) >= 65: score -= 8
    if rsi >= 72: score -= 6
    if ret5 >= 8: score -= 6
    return float(np.clip(score, 0, 100))



def final_target_gate_v13(calc, row, market_pass=False, lifecycle_state="관찰"):
    """FINAL V16: D 후보를 기반으로 한 최종 선택 게이트.
    시장환경은 탈락 조건이 아니라 랭킹 보너스로 사용한다.
    """
    return bool(
        calc.get("price_zone") == "매수구간"
        and calc.get("liquidity_score", 0) >= 30
        and calc.get("final_score", 0) >= 72
        and calc.get("cross_score", 0) >= 60
        and lifecycle_state not in ("쇠퇴",)
    )

def final_target_rank_v13(calc, row, market_pass=False, lifecycle_state="관찰"):
    """FINAL V16: D 후보 중 실제 최종 우선순위를 산출.
    시장환경/상대강도/가격구간/과열을 종합하되 하드 필터는 최소화한다.
    """
    score=float(calc.get("final_score",0))*.50 + float(calc.get("cross_score",0))*.25
    score += float(calc.get("relative_score",0))*.10 + float(calc.get("liquidity_score",0))*.05
    score += 8 if market_pass else 0
    score += 4 if calc.get("price_zone")=="매수구간" else 0
    heat=float(calc.get("overheat",0))
    if heat>=70: score-=8
    elif heat>=60: score-=4
    if lifecycle_state=="성장": score+=4
    elif lifecycle_state=="과열": score-=6
    return float(np.clip(score,0,100))


def final_target_rank_v16(calc, row, market_pass=False, lifecycle_state="관찰"):
    """FINAL V16: C(미래테마+선행주식) 후보 전체에서 최종 우선순위를 계산.
    D/시장환경/가격구간은 탈락 게이트가 아니라 보조 가점·감점으로 사용합니다.
    """
    score = (
        safe_float(calc.get("final_score"), 0) * 0.45
        + safe_float(calc.get("cross_score"), 0) * 0.20
        + safe_float(calc.get("relative_score"), 0) * 0.15
        + safe_float(calc.get("opportunity"), 0) * 0.10
        + safe_float(calc.get("liquidity_score"), 0) * 0.05
        + safe_float(calc.get("validation_score"), 0) * 0.05
    )
    if market_pass:
        score += 5.0
    if calc.get("price_zone") == "매수구간":
        score += 4.0
    elif calc.get("price_zone") == "눌림대기":
        score += 1.5
    elif calc.get("price_zone") == "추격금지":
        score -= 4.0

    heat = safe_float(calc.get("overheat"), 0)
    if heat >= 75:
        score -= 10.0
    elif heat >= 65:
        score -= 5.0
    elif heat >= 55:
        score -= 2.0

    rsi = safe_float(row.get("rsi", row.get("RSI", row.get("RSI14", 50))), 50)
    ret5 = safe_float(row.get("ret5", row.get("RET5", row.get("R5", 0))), 0)
    if rsi >= 78:
        score -= 6.0
    elif rsi >= 72:
        score -= 3.0
    if ret5 >= 12:
        score -= 6.0
    elif ret5 >= 8:
        score -= 3.0

    if lifecycle_state == "성장":
        score += 4.0
    elif lifecycle_state == "과열":
        score -= 5.0
    elif lifecycle_state == "쇠퇴":
        score -= 8.0

    return float(np.clip(score, 0, 100))

def final_target_rank_v17(calc, row, market_pass=False, lifecycle_state="관찰"):
    """FINAL V18: C 후보를 품질/균형/과열/진입상태 기준으로 재랭킹.
    D/D+M은 하드 게이트가 아니며, 여러 축의 균형을 우선합니다.
    """
    fs=safe_float(calc.get("final_score"),0)
    cross=safe_float(calc.get("cross_score"),0)
    val=safe_float(calc.get("validation_score"),0)
    rel=safe_float(calc.get("relative_score"),0)
    opp=safe_float(calc.get("opportunity"),0)
    liq=safe_float(calc.get("liquidity_score"),0)
    lead=safe_float(calc.get("lead_score"),0)
    theme=safe_float(calc.get("theme_score"),50)
    tr=max(1,int(safe_float(calc.get("theme_rank"),99)))
    sr=max(1,int(safe_float(calc.get("stock_rank"),99)))

    # 한 축의 과대점수보다 검증/상대강도/기회/선행점수의 균형을 중시
    core=(fs*.28 + cross*.22 + val*.14 + rel*.12 + opp*.10 + lead*.07 + liq*.07)
    balance=min(val,rel,opp,lead)
    core += balance*.08
    core += max(0,5-(tr-1)*1.5)
    core += max(0,3-(sr-1)*1.0)
    core += float(np.clip((theme-55)*.08,-3,3))

    if market_pass: core += 3.0

    zone=calc.get("price_zone")
    if zone=="매수구간": core += 4.0
    elif zone=="눌림대기": core += 2.0
    elif zone=="추격금지": core -= 5.0
    elif zone=="무효": core -= 12.0

    heat=safe_float(calc.get("overheat"),0)
    if heat>=75: core-=11.0
    elif heat>=65: core-=6.0
    elif heat>=55: core-=2.5

    rsi=safe_float(row.get("rsi",row.get("RSI",row.get("RSI14",50))),50)
    ret5=safe_float(row.get("ret5",row.get("RET5",row.get("R5",0))),0)
    if rsi>=78: core-=7.0
    elif rsi>=72: core-=3.5
    if ret5>=12: core-=6.0
    elif ret5>=8: core-=3.0

    if lifecycle_state=="성장": core+=4.0
    elif lifecycle_state=="과열": core-=5.0
    elif lifecycle_state=="쇠퇴": core-=9.0
    return float(np.clip(core,0,100))

def final_target_rank_v18(calc, row, market_pass=False, lifecycle_state="관찰"):
    """FINAL V18: C 후보의 균형을 우선하면서 시장/진입/과열 리스크를 정교하게 반영.
    미래 시점의 결과를 사용하지 않고 해당 날짜 계산값만 사용합니다.
    """
    fs=safe_float(calc.get("final_score"),0)
    cross=safe_float(calc.get("cross_score"),0)
    val=safe_float(calc.get("validation_score"),0)
    rel=safe_float(calc.get("relative_score"),0)
    opp=safe_float(calc.get("opportunity"),0)
    liq=safe_float(calc.get("liquidity_score"),0)
    lead=safe_float(calc.get("lead_score"),0)
    theme=safe_float(calc.get("theme_score"),50)
    tr=max(1,int(safe_float(calc.get("theme_rank"),99)))
    sr=max(1,int(safe_float(calc.get("stock_rank"),99)))

    # 핵심 점수 + 다축 균형
    core=(fs*.26 + cross*.20 + val*.15 + rel*.13 + opp*.10 + lead*.09 + liq*.07)
    balance=min(val,rel,opp,lead)
    core += balance*.10

    # 테마/종목 순위는 보조적으로만 반영
    core += max(0,4.5-(tr-1)*1.4)
    core += max(0,2.5-(sr-1)*0.8)
    core += float(np.clip((theme-55)*.06,-2.5,2.5))

    # 시장환경: 게이트가 아니라 가점
    if market_pass: core += 5.0

    # 가격구간: 추격을 강하게 억제하되 완전 배제하지 않음
    zone=calc.get("price_zone")
    if zone=="매수구간": core += 5.0
    elif zone=="눌림대기": core += 2.5
    elif zone=="추격금지": core -= 9.0
    elif zone=="무효": core -= 15.0

    # 과열도
    heat=safe_float(calc.get("overheat"),0)
    if heat>=75: core-=13.0
    elif heat>=65: core-=7.0
    elif heat>=55: core-=3.0
    elif heat>=45: core-=1.0

    # RSI/단기 급등: 과열된 진입을 억제
    rsi=safe_float(row.get("rsi",row.get("RSI",row.get("RSI14",50))),50)
    ret5=safe_float(row.get("ret5",row.get("RET5",row.get("R5",0))),0)
    if rsi>=78: core-=8.0
    elif rsi>=72: core-=4.0
    if ret5>=12: core-=7.0
    elif ret5>=8: core-=3.5

    if lifecycle_state=="성장": core+=4.0
    elif lifecycle_state=="과열": core-=6.0
    elif lifecycle_state=="쇠퇴": core-=10.0

    return float(np.clip(core,0,100))

def final_target_rank_v19(calc, row, market_pass=False, lifecycle_state="관찰",
                          rank_pct=0.5, v18_score=None):
    """FINAL V19: C 후보의 상대순위 기반 최종 점수.
    V18의 위험조정 로직을 유지하되 0~100 절대점수 클리핑을 제거하고,
    동일 날짜 C 후보 사이의 상대적 위치를 최종 선택에 반영합니다.
    """
    fs=safe_float(calc.get("final_score"),0)
    cross=safe_float(calc.get("cross_score"),0)
    val=safe_float(calc.get("validation_score"),0)
    rel=safe_float(calc.get("relative_score"),0)
    opp=safe_float(calc.get("opportunity"),0)
    liq=safe_float(calc.get("liquidity_score"),0)
    lead=safe_float(calc.get("lead_score"),0)
    theme=safe_float(calc.get("theme_score"),50)
    tr=max(1,int(safe_float(calc.get("theme_rank"),99)))
    sr=max(1,int(safe_float(calc.get("stock_rank"),99)))

    # V17 성향: 원점수/선행성/검증력을 유지
    raw=(fs*.28 + cross*.21 + val*.14 + rel*.12 + opp*.10 + lead*.08 + liq*.07)

    # V18 성향: 여러 축이 동시에 좋은 후보를 선호
    balance=min(val,rel,opp,lead)
    raw += balance*.08

    # 미래테마/종목 순위는 보조요소
    raw += max(0,5-(tr-1)*1.5)
    raw += max(0,3-(sr-1)*1.0)
    raw += float(np.clip((theme-55)*.08,-3,3))

    # 시장환경은 가점만
    if market_pass:
        raw += 3.5

    # 가격구간
    zone=calc.get("price_zone")
    if zone=="매수구간": raw += 4.0
    elif zone=="눌림대기": raw += 2.0
    elif zone=="추격금지": raw -= 6.5
    elif zone=="무효": raw -= 14.0

    # 과열
    heat=safe_float(calc.get("overheat"),0)
    if heat>=75: raw-=12.0
    elif heat>=65: raw-=6.5
    elif heat>=55: raw-=2.5
    elif heat>=45: raw-=1.0

    # RSI/단기 급등
    rsi=safe_float(row.get("rsi",row.get("RSI",row.get("RSI14",50))),50)
    ret5=safe_float(row.get("ret5",row.get("RET5",row.get("R5",0))),0)
    if rsi>=78: raw-=7.0
    elif rsi>=72: raw-=3.5
    if ret5>=12: raw-=6.0
    elif ret5>=8: raw-=3.0

    # 생애주기
    if lifecycle_state=="성장": raw+=4.0
    elif lifecycle_state=="과열": raw-=5.0
    elif lifecycle_state=="쇠퇴": raw-=9.0

    # V18 점수는 독립 참고값. 같은 날짜 후보 간 상대순위가 핵심.
    v18=safe_float(v18_score, raw)
    raw = raw*.62 + v18*.38

    # rank_pct는 동일 날짜 C 후보군에서 계산된 0~100 상대순위.
    raw += (safe_float(rank_pct,50)-50.0)*0.16
    return float(raw)

def build_final_targets_v9(radar_data):
    rows=radar_data.get("rows",[]) if radar_data else []
    selected=_future_theme_selected_map_v2(0)
    targets=[]
    for item in rows:
        code=_normalize_stock_code(item.get("code")); relrec=selected.get(code)
        if not relrec: continue
        theme=safe_float(relrec.get("theme_score"),50); tr=int(relrec.get("theme_rank",99)); sr=int(relrec.get("stock_rank",99))
        bench=benchmark_snapshot_for_stock(code) or {}
        calc=common_target_score_v9(item.get("raw",item), bench, theme, tr, sr,
                                    safe_float(item.get("lifecycle_score"),50), item.get("lifecycle_state","관찰"))
        market_pass = bool(
            safe_float(bench.get("Close"), np.nan) >= safe_float(bench.get("MA60"), np.inf)
            and safe_float(bench.get("R20"), -999) >= 0
        )
        life_state=item.get("lifecycle_state","관찰")
        if not final_target_gate_v13(calc, item, market_pass, life_state): continue
        x=dict(item); x.update({"future_theme_selected":True,"future_theme":relrec["theme"],
            "market_pass":market_pass, "final_rank_score":round(final_target_rank_v13(calc, item, market_pass, life_state),1), "final_gate":"D+M + FINAL 랭킹",
            "future_theme_rank":tr,"future_stock_rank":sr,"future_theme_score":round(theme,1),
            **{k:round(v,1) if isinstance(v,float) else v for k,v in calc.items()}})
        targets.append(x)
    targets.sort(key=lambda z:(safe_float(z.get("final_rank_score")),safe_float(z.get("final_score")),safe_float(z.get("cross_score")),safe_float(z.get("relative_score"))),reverse=True)
    for i,x in enumerate(targets,1):
        fs=safe_float(x.get("final_score")); cross=safe_float(x.get("cross_score")); zone=x.get("price_zone"); heat=safe_float(x.get("overheat"))
        x["final_rank"]=i
        x["final_state"]="🔥 최종 타겟" if fs>=82 and cross>=74 and zone=="매수구간" and heat<65 else "🟢 최종 우선" if fs>=72 else "🟡 최종 관찰" if fs>=60 else "⚪ 대기"
        x["final_reason"]=f"시장 {x.get('market','-')} · 미래테마 {x.get('future_theme','-')} · 상대강도 {x.get('relative_score',0):.0f} · 검증점수 {x.get('validation_score',0):.0f} · 가격구간 {zone}"
    return targets

# V9 live override
build_final_targets=build_final_targets_v9

# TRUE-WF V9: 같은 common_target_score_v9를 과거 날짜 데이터에 적용
def wf_snapshot_v3(data, theme_members, dt):
    """TRUE-WF V19. C 후보를 기반으로 FINAL을 상대순위로 선택합니다.
    D/D+M은 하드 게이트가 아니며 동일 날짜 후보 간 상대점수로 변별합니다.
    """
    results=[]
    for theme,members in theme_members.items():
        rows=[]
        for code,name,hits in members:
            d=data.get(code); r=wf_row_at(d,dt)
            if r is None: continue
            bench_code='^KQ11' if stock_market(code)=='KOSDAQ' else '^KS11'
            br=wf_row_at(data.get(bench_code),dt)
            if br is None: continue
            need=['Close','MA20','MA60','MA120','R5','R20','R60','VR','RSI','ATR14','TRADING_VALUE','TV20']
            if any(not np.isfinite(safe_float(r.get(k),np.nan)) for k in need): continue
            row=(r.to_dict() if hasattr(r,'to_dict') else dict(r))
            row.update({'주식':code,'Name':name,'hits':hits,'RET5':safe_float(r.get('R5'),0),
                        'RET20':safe_float(r.get('R20'),0),'RET60':safe_float(r.get('R60'),0),
                        'RSI14':safe_float(r.get('RSI'),50),'VOL_RATIO':safe_float(r.get('VR'),1)})
            rows.append(row)
        if not rows: continue
        b20=float(np.mean([safe_float(z.get('RET20'),0) for z in rows]))
        b60=float(np.mean([safe_float(z.get('RET60'),0) for z in rows]))
        try:
            tscore=float(np.clip(theme_score_v2(rows,b20,b60) or 0,0,100))
        except Exception:
            r20v=np.array([safe_float(z.get('RET20'),0) for z in rows],dtype=float)
            r60v=np.array([safe_float(z.get('RET60'),0) for z in rows],dtype=float)
            vrv=np.array([safe_float(z.get('VR'),1) for z in rows],dtype=float)
            r20s=float(np.clip((float(np.mean(r20v))+10)/25*100,0,100))
            r60s=float(np.clip((float(np.mean(r60v))+15)/45*100,0,100))
            rs=float(np.clip((float(np.mean(r20v))-b20+10)/22*100,0,100))
            flow=float(np.clip((float(np.mean(vrv))-.8)/1.2*100,0,100))
            tscore=float(np.clip(r20s*.30+r60s*.20+rs*.30+flow*.20,0,100))
        try:
            life=_theme_lifecycle(rows,{'ret20':b20,'ret60':b60}) or {'score':50,'state':'관찰'}
        except Exception:
            life={'score':50.0,'state':'관찰'}
        results.append({'theme':theme,'score':tscore,'lifecycle':life,'rows':rows})
    if not results: return None
    results.sort(key=lambda z:z['score'],reverse=True)
    strict_results=[z for z in results if z['score']>=42][:10]
    results=strict_results if strict_results else results[:10]

    candidates=[]
    for tr,top in enumerate(results,1):
        top_rows=sorted(top['rows'],key=lambda z:(safe_float(z.get('RET20'),0),safe_float(z.get('RET5'),0)),reverse=True)[:3]
        for sr,row in enumerate(top_rows,1):
            code=row['주식']; bc='^KQ11' if stock_market(code)=='KOSDAQ' else '^KS11'
            br=wf_row_at(data.get(bc),dt)
            if br is None: continue
            bench={'market':stock_market(code),'ret20':safe_float(br.get('R20'),0),'ret60':safe_float(br.get('R60'),0)}
            calc=common_target_score_v9(row,bench,top['score'],tr,sr,
                                        safe_float(top['lifecycle'].get('score'),50),
                                        top['lifecycle'].get('state','관찰'))
            zone=calc.get('price_zone')
            basic_valid=(safe_float(calc.get('validation_score'),0)>=45 and
                         safe_float(calc.get('relative_score'),0)>=35 and zone!='무효')
            market_pass=bool(safe_float(br.get('Close'),np.nan)>=safe_float(br.get('MA60'),np.nan)
                              and safe_float(br.get('R20'),-999)>=0)
            dm=bool(basic_valid and zone=='매수구간' and calc['final_score']>=72 and market_pass)
            rank_score=final_target_rank_v16(calc,row,market_pass,top['lifecycle'].get('state','관찰'))
            candidates.append({'theme':top['theme'],'theme_rank':tr,'stock_rank':sr,'theme_score':top['score'],**calc,
                               'etf':code,'name':row.get('Name',code),'date':pd.Timestamp(dt),
                               'market':stock_market(code),'BASIC_VALID':bool(basic_valid),
                               'FINAL_PASS':bool(dm),'lifecycle_state':top['lifecycle'].get('state','관찰'),
                               'lifecycle_score':safe_float(top['lifecycle'].get('score'),50),
                               'market_pass':market_pass,'C':bool(basic_valid and calc['final_score']>=60),
                               'D':bool(basic_valid and zone=='매수구간' and calc['final_score']>=72),
                               'DM':dm,'final_rank_score':rank_score})
    if not candidates: return None

    valid=[x for x in candidates if x.get('BASIC_VALID',False)]
    base_pool=valid if valid else candidates
    base_pool.sort(key=lambda z:(
        z.get('final_score',0), z.get('cross_score',0),
        z.get('relative_score',0), z.get('validation_score',0)
    ),reverse=True)
    base=base_pool[0]

    # ========================================================
    # FINAL V19
    # C 후보를 그대로 사용하되, 절대점수(0~100)만으로 순위를 정하지 않습니다.
    # 같은 날짜의 C 후보 전체에서 각 후보의 V18/V19 raw score 상대위치를 계산하여
    # 상위 후보 간 변별력을 확보합니다. D/D+M은 하드 게이트가 아닙니다.
    # ========================================================
    c_pool=[x for x in candidates if x.get('C',False)]
    if c_pool:
        # 먼저 V18 점수와 V17 계열 점수를 계산합니다.
        for x in c_pool:
            x['final_rank_score_v18']=final_target_rank_v18(
                x, x, bool(x.get('market_pass',False)),
                x.get('lifecycle_state','관찰')
            )
            x['final_rank_score_v16']=final_target_rank_v16(
                x, x, bool(x.get('market_pass',False)),
                x.get('lifecycle_state','관찰')
            )
            x['final_rank_score_v17']=final_target_rank_v17(
                x, x, bool(x.get('market_pass',False)),
                x.get('lifecycle_state','관찰')
            )

        # V19 상대순위: V18/V17/핵심 원점수를 0~100 percentile로 변환.
        def _pct(values, value):
            vals=np.asarray(values,dtype=float)
            if len(vals)<=1:
                return 50.0
            order=np.argsort(vals, kind='mergesort')
            ranks=np.empty(len(vals),dtype=float)
            ranks[order]=np.arange(len(vals),dtype=float)
            return float(np.clip(ranks[list(vals).index(value)]/(len(vals)-1)*100,0,100))

        v18vals=[safe_float(x.get('final_rank_score_v18'),0) for x in c_pool]
        v17vals=[safe_float(x.get('final_rank_score_v17'),0) for x in c_pool]
        basevals=[
            safe_float(x.get('final_score'),0)*.45 +
            safe_float(x.get('cross_score'),0)*.25 +
            safe_float(x.get('relative_score'),0)*.15 +
            safe_float(x.get('validation_score'),0)*.15
            for x in c_pool
        ]

        for i,x in enumerate(c_pool):
            p18=_pct(v18vals,v18vals[i])
            p17=_pct(v17vals,v17vals[i])
            pb=_pct(basevals,basevals[i])
            # 세 축의 상대순위를 결합. V18 방어력 + V17 수익성 + 기본 품질.
            rel_rank=p18*.40 + p17*.35 + pb*.25
            x['final_rank_pct_v19']=round(rel_rank,2)
            x['final_rank_score_v19']=final_target_rank_v19(
                x, x, bool(x.get('market_pass',False)),
                x.get('lifecycle_state','관찰'),
                rank_pct=rel_rank,
                v18_score=x.get('final_rank_score_v18')
            )

        c_pool.sort(key=lambda z:(
            z.get('final_rank_score_v19',-1e9),
            z.get('final_rank_pct_v19',0),
            z.get('final_rank_score_v18',-1e9),
            z.get('final_rank_score_v17',-1e9),
            z.get('final_score',0)
        ),reverse=True)
        final_choice=c_pool[0]
    else:
        final_choice=base

    w=dict(final_choice)
    w['FINAL']=bool(bool(c_pool) and w.get('C',False))
    w['FINAL_PASS']=bool(w['FINAL'])
    w['FINAL_V19']=bool(w['FINAL'])
    w['FINAL_V18']=bool(w['FINAL'])
    w['FINAL_V17']=bool(w['FINAL'])
    w['FINAL_V16']=bool(w['FINAL'])
    w['FINAL_C_BASED']=True

    pools={
        'C': [x for x in candidates if x.get('C',False)],
        'D': [x for x in candidates if x.get('D',False)],
        'DM': [x for x in candidates if x.get('DM',False)],
        'FINAL': c_pool,
    }
    for stg,pool in pools.items():
        if pool:
            if stg == 'FINAL':
                pool.sort(key=lambda z:(
                    z.get('final_rank_score_v19',-1e9),
                    z.get('final_rank_pct_v19',0),
                    z.get('final_rank_score_v18',-1e9),
                    z.get('final_rank_score_v17',-1e9)
                ),reverse=True)
            else:
                pool.sort(key=lambda z:(
                    z.get('final_score',0),
                    z.get('cross_score',0),
                    z.get('relative_score',0),
                    z.get('validation_score',0)
                ),reverse=True)
            q=pool[0]
            for k,v in list(q.items()):
                w[f'{k}_{stg}']=v
            w[f'etf_{stg}']=q.get('etf')
            w[f'name_{stg}']=q.get('name',q.get('etf'))
            w[f'theme_{stg}']=q.get('theme','')
            w[f'market_pass_{stg}']=bool(q.get('market_pass',False))
            w[f'price_zone_{stg}']=q.get('price_zone','')
            w[f'final_rank_score_{stg}']=q.get(
                'final_rank_score_v19',
                q.get('final_rank_score_v18',
                      q.get('final_rank_score_v17',
                            q.get('final_rank_score_v16',
                                  q.get('final_rank_score',q.get('final_score',0)))))
            )
        else:
            w[f'etf_{stg}']=None

    # FINAL과 C가 실제로 다른 선택을 했는지 진단용 플래그
    w['FINAL_C_SAME']=bool(
        w.get('etf_FINAL') and w.get('etf_C') and
        str(w.get('etf_FINAL')) == str(w.get('etf_C'))
    )
    return w


# V9 검증 화면에서 V3 snapshot 사용
wf_snapshot_v2=wf_snapshot_v3

# ============================================================
# MAIN
# ============================================================

init_state()

st.markdown(
    """
    <div class="app-header">
        <div class="app-title">STOCK RADAR</div>
        <div class="app-subtitle">개별주 추세 · 모멘텀 · 거래량 · 핵심가격 · 대응 시나리오</div>
    </div>
    """,
    unsafe_allow_html=True
)

nav = st.radio(
    "메뉴",
    ["🏆 최종 타겟", "🚀 미래테마", "📊 내 주식", "🧪 백테스트", "🧬 TRUE 검증", "🏁 최종검증"],
    horizontal=True,
    key="main_page",
    label_visibility="collapsed"
)

if nav == "🏆 최종 타겟":
    render_final_target()
elif nav == "🚀 미래테마":
    render_future_theme()
elif nav == "📊 내 주식":
    render_my_etf()
elif nav == "🧪 백테스트":
    render_backtest_lab()
elif nav == "🧬 TRUE 검증":
    render_true_walk_forward()
elif nav == "🏁 최종검증":
    render_final_validation()
