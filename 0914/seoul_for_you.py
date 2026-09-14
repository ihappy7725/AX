import base64
import math
import os
from io import BytesIO
from pathlib import Path

import folium
import pandas as pd
import requests
import re
import textwrap
import streamlit as st
import streamlit.components.v1 as components
from deep_translator import GoogleTranslator

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
from streamlit_folium import st_folium


# ============================================================
# 1. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Seoul for You",
    page_icon="🗺️",
    layout="wide",
)



# ============================================================
# LOCAL FONT HELPERS
# These functions must be defined before the hero/font CSS uses them.
# ============================================================

def find_local_asset(filename):
    """
    Search for a font/image file in:
    1) the same folder as seoul_for_you.py
    2) one folder above
    3) ./fonts
    4) ../fonts
    """
    script_dir = Path(__file__).resolve().parent

    candidates = [
        script_dir / filename,
        script_dir.parent / filename,
        script_dir / "fonts" / filename,
        script_dir.parent / "fonts" / filename,
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    return None


@st.cache_data(show_spinner=False)
def font_to_data_uri(path_str):
    """
    Convert a local .ttf/.otf font into a Base64 data URI
    so the browser can actually use the local font.
    """
    font_path = Path(path_str)

    if not font_path.exists():
        return None, None

    encoded = base64.b64encode(font_path.read_bytes()).decode("utf-8")

    if font_path.suffix.lower() == ".ttf":
        mime_type = "font/ttf"
        font_format = "truetype"
    else:
        mime_type = "font/otf"
        font_format = "opentype"

    data_uri = f"data:{mime_type};base64,{encoded}"

    return data_uri, font_format


def apply_language_font(language_code):
    """
    Apply the uploaded Chinese/Japanese font to the Streamlit app.
    """
    font_paths = []
    css_families = []

    if language_code == "zh-CN":
        chinese_font = find_local_asset("DaMengXiuKai-Regular-2.ttf")

        if chinese_font is not None:
            font_paths.append(("SeoulChinese", chinese_font))
            css_families.append("'SeoulChinese'")

    elif language_code == "ja":
        japanese_p_font = find_local_asset("ipamp.ttf")
        japanese_font = find_local_asset("ipam.ttf")

        if japanese_p_font is not None:
            font_paths.append(("SeoulJapaneseP", japanese_p_font))
            css_families.append("'SeoulJapaneseP'")

        if japanese_font is not None:
            font_paths.append(("SeoulJapanese", japanese_font))
            css_families.append("'SeoulJapanese'")

    # English uses the normal site font.
    if not font_paths:
        return

    font_face_rules = []

    for family_name, font_path in font_paths:
        data_uri, font_format = font_to_data_uri(str(font_path))

        if data_uri is None:
            continue

        font_face_rules.append(
            f"""
            @font-face {{
                font-family: '{family_name}';
                src: url('{data_uri}') format('{font_format}');
                font-style: normal;
                font-weight: normal;
                font-display: swap;
            }}
            """
        )

    if not font_face_rules:
        return

    font_stack = ", ".join(css_families + ["sans-serif"])

    st.markdown(
        f"""
        <style>
        {''.join(font_face_rules)}

        [data-testid="stAppViewContainer"],
        [data-testid="stSidebar"],
        .stMarkdown,
        .stCaption,
        .stButton button,
        .stSelectbox,
        .stRadio,
        .stMetric,
        .stExpander,
        input,
        textarea,
        select,
        button,
        p,
        span,
        label,
        li,
        a,
        h1,
        h2,
        h3,
        h4,
        h5,
        h6 {{
            font-family: {font_stack} !important;
        }}

        /* Keep the English poster wordmark visually consistent. */
        .poster-wordmark,
        .top-brand,
        .poster-caption-small {{
            font-family: Arial Black, Arial, Helvetica, sans-serif !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )



# ============================================================
# 2. POSTER-STYLE SEOUL DESIGN
#    Palette inspired by the uploaded Korea/Seoul poster:
#    sage green + soft coral + warm cream + muted traditional green
# ============================================================

st.markdown(
    """
    <style>
        :root {
            --sfy-sage: #F8F9EC;
            --sfy-sage-deep: #EEF1D8;
            --sfy-coral: #EFC1AE;
            --sfy-coral-strong: #E9A996;
            --sfy-cream: #FBF6E9;
            --sfy-cream-light: #FFFDF6;
            --sfy-green: #596E58;
            --sfy-green-soft: #879780;
            --sfy-ink: #39483B;
            --sfy-line: rgba(57, 72, 59, 0.24);
        }

        html, body,
        [data-testid="stAppViewContainer"],
        .stApp {
            background: var(--sfy-sage) !important;
            color: var(--sfy-ink) !important;
        }

        [data-testid="stHeader"] {
            background: rgba(248, 249, 236, 0.96) !important;
            backdrop-filter: blur(8px);
        }

        [data-testid="stToolbar"] {
            right: 0.8rem;
        }

        .block-container {
            max-width: 1420px;
            padding-top: 3.8rem !important;
            padding-bottom: 4rem;
        }


        /* Keep the app content below Streamlit's fixed toolbar. */
        [data-testid="stHeader"] {
            min-height: 2.75rem !important;
        }

        /* ---------- Top brand bar ---------- */
        .top-brand {
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 0.78rem;
            font-weight: 900;
            letter-spacing: 0.16em;
            color: var(--sfy-green);
            text-transform: uppercase;
            padding: 0.35rem 0 0.5rem 0;
            line-height: 1.45;
            min-height: 1.8rem;
            overflow: visible !important;
        }

        .top-brand-dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            background: var(--sfy-coral-strong);
            display: inline-block;
        }

        /* ---------- Main poster hero ---------- */
        .poster-hero {
            position: relative;
            min-height: 430px;
            overflow: hidden;
            margin: 0.25rem 0 1.6rem 0;
            border: 1.5px solid var(--sfy-line);
            border-radius: 26px;
            background:
                radial-gradient(circle at 76% 28%, rgba(238,228,199,0.36), transparent 28%),
                linear-gradient(145deg, #DCE4A7 0%, #D3DC97 100%);
        }

        .poster-topline {
            position: absolute;
            top: 25px;
            left: 0;
            right: 0;
            z-index: 4;
            text-align: center;
            font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif !important;
            color: var(--sfy-coral-strong);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
        }

        .poster-wordmark {
            position: absolute;
            left: 4.5%;
            top: 58px;
            z-index: 1;
            font-family: Arial Black, Arial, Helvetica, sans-serif !important;
            font-size: clamp(5.3rem, 10vw, 9rem);
            font-weight: 900;
            line-height: 0.79;
            letter-spacing: -0.075em;
            color: var(--sfy-coral);
            text-transform: uppercase;
            user-select: none;
        }

        .poster-wordmark .for-you {
            padding-left: 0.02em;
        }

        .poster-gate {
            position: absolute;
            z-index: 3;
            width: min(430px, 44vw);
            left: 54%;
            top: 50%;
            transform: translate(-50%, -45%);
            filter: drop-shadow(0 8px 0 rgba(89,110,88,0.06));
        }

        .poster-seal {
            position: absolute;
            right: 4.5%;
            top: 55px;
            z-index: 4;
            width: 70px;
            height: 70px;
            border: 1.5px solid var(--sfy-green);
            border-radius: 50%;
            display: grid;
            place-items: center;
            color: var(--sfy-green);
            background: rgba(238,228,199,0.5);
            font-family: "Malgun Gothic", sans-serif !important;
            font-size: 1rem;
            line-height: 1.1;
            font-weight: 800;
            text-align: center;
        }

        .poster-caption {
            position: absolute;
            left: 5%;
            right: 5%;
            bottom: 24px;
            z-index: 5;
            display: flex;
            justify-content: space-between;
            align-items: end;
            gap: 1rem;
            color: var(--sfy-green);
        }

        .poster-caption-main {
            max-width: 760px;
            font-size: 0.98rem;
            line-height: 1.55;
            font-weight: 650;
        }

        .poster-caption-small {
            font-family: Arial, Helvetica, sans-serif !important;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.13em;
            white-space: nowrap;
            text-transform: uppercase;
        }


        /* ---------- Compact Seoul AI sidebar ---------- */
        .ai-guide-card {
            background: rgba(255, 253, 246, 0.78);
            border: 1px solid rgba(89, 110, 88, 0.18);
            border-radius: 16px;
            padding: 0.9rem 0.95rem 0.8rem 0.95rem;
            margin-bottom: 0.7rem;
        }

        .ai-guide-kicker {
            color: var(--sfy-coral-strong);
            font-size: 0.66rem;
            font-weight: 900;
            letter-spacing: 0.12em;
            margin-bottom: 0.22rem;
        }

        .ai-guide-title {
            color: var(--sfy-green);
            font-size: 1.02rem;
            line-height: 1.3;
            font-weight: 850;
            margin-bottom: 0.28rem;
        }

        .ai-guide-subtitle {
            color: var(--sfy-green-soft);
            font-size: 0.78rem;
            line-height: 1.45;
        }

        [data-testid="stSidebar"] div[data-testid="stForm"] {
            border: 0 !important;
            padding: 0 !important;
            background: transparent !important;
        }

        /* ---------- Sidebar ---------- */
        [data-testid="stSidebar"] {
            background: var(--sfy-sage-deep) !important;
            border-right: 1.5px solid var(--sfy-line);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.2rem;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: var(--sfy-green) !important;
            letter-spacing: -0.02em;
        }

        [data-testid="stSidebar"] hr {
            border-color: var(--sfy-line) !important;
        }

        /* ---------- Selects / inputs ---------- */
        div[data-baseweb="select"] > div,
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stTextArea"] textarea {
            background: var(--sfy-cream-light) !important;
            border: 1.3px solid var(--sfy-line) !important;
            border-radius: 13px !important;
            color: var(--sfy-ink) !important;
            box-shadow: none !important;
        }

        div[data-baseweb="popover"] {
            color: var(--sfy-ink) !important;
        }

        ul[role="listbox"] {
            background: var(--sfy-cream-light) !important;
        }

        li[role="option"] {
            color: var(--sfy-ink) !important;
        }

        /* ---------- Language selector pills ---------- */
        div[data-testid="stRadio"] div[role="radiogroup"] {
            display: flex !important;
            justify-content: flex-end !important;
            flex-wrap: nowrap !important;
            gap: 0.42rem !important;
            width: 100% !important;
            overflow: visible !important;
        }

        div[data-testid="stRadio"] label {
            background: rgba(238,228,199,0.76);
            border: 1px solid var(--sfy-line);
            border-radius: 999px;
            padding: 0.18rem 0.45rem;
            white-space: nowrap !important;
            font-size: 0.88rem !important;
            transition: 0.18s ease;
        }

        div[data-testid="stRadio"] label:hover {
            background: var(--sfy-coral);
        }

        /* ---------- Buttons ---------- */
        .stButton > button,
        [data-testid="stBaseButton-primary"],
        [data-testid="stBaseButton-secondary"] {
            background: var(--sfy-coral) !important;
            color: var(--sfy-ink) !important;
            border: 1.3px solid var(--sfy-green) !important;
            border-radius: 999px !important;
            font-weight: 750 !important;
            box-shadow: none !important;
            transition: transform 0.15s ease, background 0.15s ease;
        }

        .stButton > button:hover,
        [data-testid="stBaseButton-primary"]:hover,
        [data-testid="stBaseButton-secondary"]:hover {
            background: var(--sfy-coral-strong) !important;
            transform: translateY(-1px);
        }

        /* ---------- Metrics ---------- */
        div[data-testid="stMetric"] {
            background: var(--sfy-cream);
            border: 1.3px solid var(--sfy-line);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            min-height: 108px;
        }

        div[data-testid="stMetricLabel"] {
            color: var(--sfy-green) !important;
            font-weight: 700;
        }

        div[data-testid="stMetricValue"] {
            color: var(--sfy-ink) !important;
            font-weight: 850;
        }


        /* ---------- Cards ---------- */
        .place-card {
            border: 1.3px solid var(--sfy-line);
            border-radius: 18px;
            padding: 16px;
            margin-bottom: 10px;
            min-height: 180px;
            background: var(--sfy-cream);
        }

        .tag {
            display: inline-block;
            padding: 0.18rem 0.5rem;
            margin: 0.1rem 0.12rem 0.1rem 0;
            border-radius: 999px;
            border: 1px solid rgba(89,110,88,0.28);
            background: rgba(214,222,158,0.65);
            color: var(--sfy-green);
            font-size: 0.78rem;
            font-weight: 650;
        }

        .image-placeholder {
            border: 1.4px dashed rgba(89,110,88,0.38);
            border-radius: 16px;
            padding: 48px 18px;
            text-align: center;
            color: var(--sfy-green);
            background: rgba(238,228,199,0.65);
        }

        .small-muted {
            color: var(--sfy-green-soft);
            font-size: 0.88rem;
        }

        /* ---------- Alerts ---------- */
        div[data-testid="stAlert"] {
            background: rgba(238,228,199,0.9) !important;
            border: 1.3px solid var(--sfy-line) !important;
            border-left: 6px solid var(--sfy-coral-strong) !important;
            border-radius: 14px !important;
            color: var(--sfy-ink) !important;
        }

        /* ---------- Expanders ---------- */
        div[data-testid="stExpander"] {
            background: var(--sfy-cream);
            border: 1.3px solid var(--sfy-line) !important;
            border-radius: 18px !important;
            overflow: hidden;
        }

        /* ---------- Headings / dividers ---------- */
        h1, h2, h3 {
            color: var(--sfy-green) !important;
            letter-spacing: -0.025em;
        }

        hr {
            border-color: var(--sfy-line) !important;
        }

        /* ---------- Map frame ---------- */
        iframe {
            border-radius: 20px !important;
        }

        [data-testid="stIFrame"] {
            border: 1.3px solid var(--sfy-line);
            border-radius: 20px;
            overflow: hidden;
            background: var(--sfy-cream);
        }


        /* ---------- Top header: prevent clipping ---------- */
        .sfy-topbar {
            width: 100%;
            display: flex;
            align-items: flex-start;
            justify-content: flex-start;
            margin: 0.35rem 0 0.25rem 0;
            padding-top: 0.35rem;
            overflow: visible !important;
        }

        .sfy-brand-wrap {
            min-width: 0;
            overflow: visible !important;
        }

        .sfy-mini-title {
            color: var(--sfy-green);
            font-size: clamp(1.55rem, 3vw, 2.3rem);
            line-height: 1.12;
            font-weight: 850;
            letter-spacing: -0.035em;
            margin-top: 0.05rem;
            white-space: normal;
            word-break: keep-all;
            overflow: visible !important;
        }

        /* Language switch gets its own row instead of sharing title space */
        div[data-testid="stRadio"] {
            width: 100% !important;
            overflow: visible !important;
            margin: 0.15rem 0 0.9rem 0 !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] {
            width: 100% !important;
            display: flex !important;
            justify-content: flex-end !important;
            align-items: center !important;
            flex-wrap: wrap !important;
            gap: 0.45rem !important;
            overflow: visible !important;
        }

        div[data-testid="stRadio"] label {
            flex: 0 0 auto !important;
            min-width: fit-content !important;
            max-width: none !important;
            white-space: nowrap !important;
            overflow: visible !important;
            padding: 0.32rem 0.72rem !important;
            border-radius: 999px !important;
        }

        div[data-testid="stRadio"] label p {
            white-space: nowrap !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }

        /* ---------- Responsive ---------- */
        @media (max-width: 900px) {
            .poster-hero {
                min-height: 390px;
            }

            .poster-wordmark {
                left: 4%;
                top: 70px;
                font-size: clamp(4.2rem, 15vw, 7.3rem);
            }

            .poster-gate {
                width: min(360px, 58vw);
                left: 60%;
            }

            .poster-seal {
                width: 58px;
                height: 58px;
                right: 3.5%;
            }

            .poster-caption-small {
                display: none;
            }
        }

        @media (max-width: 620px) {

            .sfy-mini-title {
                font-size: 1.45rem;
            }

            div[data-testid="stRadio"] div[role="radiogroup"] {
                justify-content: flex-start !important;
                gap: 0.35rem !important;
            }

            div[data-testid="stRadio"] label {
                padding: 0.28rem 0.58rem !important;
                font-size: 0.82rem !important;
            }
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .poster-hero {
                min-height: 360px;
                border-radius: 20px;
            }

            .poster-topline {
                font-size: 0.67rem;
                padding: 0 1rem;
            }

            .poster-wordmark {
                top: 76px;
                font-size: clamp(3.9rem, 18vw, 5.3rem);
                line-height: 0.83;
            }

            .poster-gate {
                width: min(300px, 74vw);
                left: 58%;
                top: 54%;
            }

            .poster-seal {
                display: none;
            }

            .poster-caption {
                bottom: 18px;
            }

            .poster-caption-main {
                font-size: 0.84rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. LANGUAGE / CURRENCY CONFIG
# ============================================================

LANG_CONFIG = {
    "English": {"code": "en", "currency": "USD", "flag": "🇺🇸"},
    "中文": {"code": "zh-CN", "currency": "CNY", "flag": "🇨🇳"},
    "日本語": {"code": "ja", "currency": "JPY", "flag": "🇯🇵"},
}

UI = {
    "en": {
        "tagline": "Eight journeys, one city. Find the Seoul story you want to walk into.",
        "language": "Language",
        "ai_title": "Ask Seoul AI",
        "ai_subtitle": "Ask about routes, food, transport, neighborhoods, and local tips.",
        "ai_placeholder": "e.g. Where should I go on a rainy afternoon?",
        "ai_send": "Ask Seoul AI",
        "ai_clear": "Clear chat",
        "ai_api_missing": "Connect an API key to use Seoul AI.",
        "ai_api_key": "OpenAI API key",
        "ai_error": "I couldn't answer that just now. Please try again.",
        "ai_install": "Install the `openai` package to use the travel chat.",
        "weather": "Seoul weather",
        "exchange": "Exchange rate",
        "shown": "Places shown",
        "today_tip": "Today's travel tip",
        "filters": "Find your Seoul",
        "theme": "Choose a journey",
        "time": "Time available",
        "budget": "Budget",
        "style": "Travel style",
        "situation": "Situation",
        "area": "Area",
        "place": "Place",
        "all": "All",
        "auto_weather": "Auto from weather",
        "any": "Any",
        "two_hours": "About 2 hours",
        "half_day": "Half day",
        "full_day": "Full day",
        "free": "Free only",
        "under_10k": "Free / low-cost",
        "under_30k": "Up to mid-range",
        "solo": "Solo",
        "couple": "Couple",
        "friends": "Friends",
        "family": "Family",
        "rainy": "Rainy day",
        "hot": "Hot day",
        "night": "Night",
        "indoor": "Indoor",
        "map_title": "Explore on the map",
        "recommended": "Recommended for you",
        "recommended_sub": "Results are ranked from your theme, time, budget, travel style and current conditions.",
        "details": "Place details",
        "description": "Why visit",
        "directions": "How to get there",
        "duration": "Suggested time",
        "cost": "Budget fit",
        "best_time": "Best time",
        "indoor_label": "Indoor option",
        "yes": "Yes",
        "no": "No",
        "add_trip": "Add to My Trip",
        "added": "Added to My Trip",
        "nearby": "Nearby places",
        "distance": "Distance",
        "my_trip": "My Seoul Trip",
        "my_trip_empty": "Save places you like and build a simple route.",
        "route_note": "The route follows the order you saved places; it is not an optimized transit route.",
        "remove": "Remove",
        "clear": "Clear trip",
        "survival": "Seoul Travel Essentials",
        "select_detail": "Choose a specific place to see full details, nearby spots and trip controls.",
        "no_results": "No places match these filters. Try widening one or two filters.",
        "image_unavailable": "Image unavailable",
        "translation_unavailable": "Translation temporarily unavailable. Please try again in a moment.",
        "open_map": "View details",
        "rain_tip": "Rain is in the forecast, so indoor museums, malls and covered attractions are prioritized.",
        "hot_tip": "It is hot in Seoul, so indoor and riverside options are prioritized.",
        "normal_tip": "Conditions look suitable for a broad mix of indoor and outdoor sightseeing.",
        "free_label": "Mostly free",
        "low_label": "Low-cost",
        "mid_label": "Mid-range",
        "premium_label": "Premium",
        "morning": "Morning",
        "afternoon": "Afternoon",
        "evening": "Evening / Night",
        "anytime": "Anytime",
        "theme_all": "All themes",
        "traditional": "Traditional Seoul",
        "kculture": "K-Culture",
        "food": "Food & Market",
        "night_seoul": "Night Seoul",
        "nature": "Nature & Healing",
        "trendy": "Trendy Seoul",
        "shopping": "Shopping",
        "photo": "Photo Spots",
        "results": "recommendations",
        "survival_body": """
**🚇 Getting around**  
Use Seoul's subway and buses with a rechargeable transit card such as T-money. Check your last train time when staying out late.

**💳 Money**  
Cards are widely accepted, but carrying a small amount of Korean won is useful for traditional markets and small shops.

**📱 Connectivity**  
An eSIM, SIM card or portable Wi-Fi makes navigation and translation much easier.

**🧳 Luggage**  
Major stations and tourist areas often have lockers or luggage-storage services. Check operating hours before relying on them.

**🚨 Help**  
Police: **112** · Fire/ambulance: **119** · Korea Travel Helpline: **1330**.

**💬 Handy Korean**  
안녕하세요 = Hello · 감사합니다 = Thank you · 화장실 어디예요? = Where is the restroom? · 이거 주세요 = This one, please.
""",
    },
    "zh-CN": {
        "tagline": "八段旅程，一座城市。走进属于你的首尔故事。",
        "language": "语言",
        "ai_title": "问问 Seoul AI",
        "ai_subtitle": "路线、美食、交通、街区和本地旅行建议都可以问。",
        "ai_placeholder": "例如：下雨的下午去哪里比较好？",
        "ai_send": "询问首尔 AI",
        "ai_clear": "清空对话",
        "ai_api_missing": "连接 API 密钥后即可使用 Seoul AI。",
        "ai_api_key": "OpenAI API 密钥",
        "ai_error": "暂时无法回答，请稍后再试。",
        "ai_install": "请安装 `openai` 套件以使用旅行问答。",
        "weather": "首尔天气",
        "exchange": "汇率",
        "shown": "显示景点",
        "today_tip": "今日旅行提示",
        "filters": "找到你的首尔",
        "theme": "选择一段旅程",
        "time": "可用时间",
        "budget": "预算",
        "style": "旅行方式",
        "situation": "当前需求",
        "area": "区域",
        "place": "景点",
        "all": "全部",
        "auto_weather": "根据天气自动推荐",
        "any": "不限",
        "two_hours": "约2小时",
        "half_day": "半天",
        "full_day": "一整天",
        "free": "仅免费",
        "under_10k": "免费 / 低预算",
        "under_30k": "中等预算以内",
        "solo": "独自旅行",
        "couple": "情侣",
        "friends": "朋友",
        "family": "家庭",
        "rainy": "雨天",
        "hot": "炎热天气",
        "night": "夜间",
        "indoor": "室内",
        "map_title": "在地图上探索",
        "recommended": "为你推荐",
        "recommended_sub": "根据主题、时间、预算、旅行方式和当前情况综合排序。",
        "details": "景点详情",
        "description": "推荐理由",
        "directions": "如何前往",
        "duration": "建议停留",
        "cost": "预算",
        "best_time": "最佳时间",
        "indoor_label": "室内景点",
        "yes": "是",
        "no": "否",
        "add_trip": "加入我的行程",
        "added": "已加入我的行程",
        "nearby": "附近景点",
        "distance": "距离",
        "my_trip": "我的首尔行程",
        "my_trip_empty": "收藏喜欢的景点，建立简单旅行路线。",
        "route_note": "路线按收藏顺序连接，并非最优公共交通路线。",
        "remove": "删除",
        "clear": "清空行程",
        "survival": "首尔旅行实用指南",
        "select_detail": "请选择一个具体景点，以查看完整介绍、附近景点和行程功能。",
        "no_results": "没有符合条件的景点，请放宽一两个筛选条件。",
        "image_unavailable": "暂时无法显示图片",
        "translation_unavailable": "暂时无法翻译。请稍后再试。",
        "open_map": "查看详情",
        "rain_tip": "预计有雨，已优先推荐博物馆、商场等室内景点。",
        "hot_tip": "首尔天气炎热，已优先推荐室内和河边景点。",
        "normal_tip": "目前天气适合安排室内与户外相结合的行程。",
        "free_label": "基本免费",
        "low_label": "低预算",
        "mid_label": "中等预算",
        "premium_label": "高预算",
        "morning": "上午",
        "afternoon": "下午",
        "evening": "傍晚 / 夜间",
        "anytime": "不限",
        "theme_all": "全部主题",
        "traditional": "传统首尔",
        "kculture": "K-Culture",
        "food": "美食与市场",
        "night_seoul": "首尔夜景",
        "nature": "自然与疗愈",
        "trendy": "潮流首尔",
        "shopping": "购物",
        "photo": "拍照打卡",
        "results": "个推荐",
        "survival_body": """
**🚇 交通**  
可使用 T-money 等交通卡乘坐首尔地铁和公交。夜间出行时建议提前确认末班车时间。

**💳 支付**  
大多数地方可以刷卡，但传统市场和小店建议准备少量韩元现金。

**📱 网络**  
使用 eSIM、SIM 卡或移动 Wi-Fi，可以更方便地使用地图和翻译服务。

**🧳 行李**  
主要车站和旅游区通常设有寄存柜或行李寄存服务，使用前请确认营业时间。

**🚨 求助**  
报警 **112** · 消防/急救 **119** · 韩国旅游咨询热线 **1330**。

**💬 实用韩语**  
안녕하세요 = 你好 · 감사합니다 = 谢谢 · 화장실 어디예요? = 洗手间在哪里？ · 이거 주세요 = 请给我这个。
""",
    },
    "ja": {
        "tagline": "場所を探すだけでなく、あなたのソウルを見つけよう。",
        "language": "言語",
        "ai_title": "Seoul AI に聞く",
        "ai_subtitle": "ルート、グルメ、交通、街歩き、現地のコツを質問できます。",
        "ai_placeholder": "例：雨の午後はどこがおすすめ？",
        "ai_send": "ソウル AI に聞く",
        "ai_clear": "チャットを消去",
        "ai_api_missing": "OpenAI API キーが設定されていません。",
        "ai_api_key": "OpenAI API キー",
        "ai_error": "現在回答できません。もう一度お試しください。",
        "ai_install": "旅行チャットを使うには `openai` パッケージをインストールしてください。",
        "weather": "ソウルの天気",
        "exchange": "為替レート",
        "shown": "表示スポット数",
        "today_tip": "今日の旅行ヒント",
        "filters": "あなたのソウルを探す",
        "theme": "旅のテーマを選ぶ",
        "time": "滞在時間",
        "budget": "予算",
        "style": "旅行スタイル",
        "situation": "シチュエーション",
        "area": "エリア",
        "place": "スポット",
        "all": "すべて",
        "auto_weather": "天気から自動選択",
        "any": "指定なし",
        "two_hours": "約2時間",
        "half_day": "半日",
        "full_day": "1日",
        "free": "無料のみ",
        "under_10k": "無料 / 低予算",
        "under_30k": "中程度の予算まで",
        "solo": "ひとり旅",
        "couple": "カップル",
        "friends": "友人",
        "family": "家族",
        "rainy": "雨の日",
        "hot": "暑い日",
        "night": "夜",
        "indoor": "屋内",
        "map_title": "地図で探す",
        "recommended": "おすすめスポット",
        "recommended_sub": "テーマ・時間・予算・旅行スタイル・現在の状況からおすすめ順に表示します。",
        "details": "スポット詳細",
        "description": "おすすめポイント",
        "directions": "アクセス",
        "duration": "おすすめ滞在時間",
        "cost": "予算",
        "best_time": "おすすめ時間帯",
        "indoor_label": "屋内スポット",
        "yes": "はい",
        "no": "いいえ",
        "add_trip": "My Trip に追加",
        "added": "My Trip に追加済み",
        "nearby": "周辺スポット",
        "distance": "距離",
        "my_trip": "My Seoul Trip",
        "my_trip_empty": "気になる場所を保存して、簡単な旅行ルートを作れます。",
        "route_note": "保存した順番で線を結びます。最適化された交通ルートではありません。",
        "remove": "削除",
        "clear": "行程をクリア",
        "survival": "ソウル旅行の基本情報",
        "select_detail": "詳しい説明、周辺スポット、行程機能を見るにはスポットを1つ選択してください。",
        "no_results": "条件に合うスポットがありません。フィルターを少し広げてください。",
        "image_unavailable": "画像を表示できません",
        "translation_unavailable": "翻訳を一時的に利用できません。しばらくしてからもう一度お試しください。",
        "open_map": "詳細を見る",
        "rain_tip": "雨の予報のため、博物館・モールなど屋内スポットを優先しています。",
        "hot_tip": "ソウルは暑いため、屋内や川沿いのスポットを優先しています。",
        "normal_tip": "現在は屋内・屋外の観光をバランスよく楽しみやすい天候です。",
        "free_label": "ほぼ無料",
        "low_label": "低予算",
        "mid_label": "中程度",
        "premium_label": "高め",
        "morning": "午前",
        "afternoon": "午後",
        "evening": "夕方 / 夜",
        "anytime": "いつでも",
        "theme_all": "すべてのテーマ",
        "traditional": "伝統ソウル",
        "kculture": "K-Culture",
        "food": "グルメ & 市場",
        "night_seoul": "夜のソウル",
        "nature": "自然 & ヒーリング",
        "trendy": "トレンドソウル",
        "shopping": "ショッピング",
        "photo": "フォトスポット",
        "results": "件",
        "survival_body": """
**🚇 移動**  
T-money などの交通カードで地下鉄・バスを利用できます。夜遅くまで出かける場合は終電時間を確認してください。

**💳 支払い**  
カードは広く利用できますが、伝統市場や小さなお店のために少額の韓国ウォンを持っておくと便利です。

**📱 通信**  
eSIM、SIMカード、ポケットWi-Fiがあると地図や翻訳を使いやすくなります。

**🧳 荷物**  
主要駅や観光エリアにはコインロッカーや荷物預かりサービスがあります。営業時間を事前に確認してください。

**🚨 困ったとき**  
警察 **112** · 消防/救急 **119** · 韓国観光案内 **1330**。

**💬 便利な韓国語**  
안녕하세요 = こんにちは · 감사합니다 = ありがとうございます · 화장실 어디예요? = トイレはどこですか？ · 이거 주세요 = これをください。
""",
    },
}

THEME_KEYS = {
    "traditional": "🏯",
    "kculture": "🎤",
    "food": "🍜",
    "night_seoul": "🌃",
    "nature": "🌿",
    "trendy": "☕",
    "shopping": "🛍️",
    "photo": "📸",
}


# Documentary-style journey themes.
# These are story-led filters layered on top of the verified CSV metadata.
JOURNEY_COPY = {
    "en": {
        "journey_all": ("🧭 All Seoul Stories", "Start wide and let the city surprise you."),
        "royal_seoul": ("👑 왕의 길, 서울 · Palaces & Royal Seoul", "Walk the ceremonial roads, palace courtyards, old gates and traces of Joseon Seoul."),
        "alley_temperature": ("🏘️ 골목의 온도 · Hanok & Hidden Streets", "Follow intimate lanes where hanok, cafés, murals and everyday Seoul overlap."),
        "seoul_bite": ("🥢 서울 한입 · Markets & Street Food", "Meet Seoul through sizzling market stalls, local snacks and neighborhoods shaped by food."),
        "han_river_night": ("🌙 한강에 밤이 오면 · River & City Lights", "Watch the Han River turn into a ribbon of bridges, towers, reflections and late-night Seoul."),
        "seoul_now": ("🎧 지금, 서울 · K-Pop to Seongsu", "Step into the Seoul of right now—music, fashion, cafés, pop culture and fast-changing neighborhoods."),
        "mountain_city": ("⛰️ 산이 품은 도시 · Hike the City", "Climb above the rooftops and see how mountains live inside the rhythm of the capital."),
        "art_city": ("🎨 도시가 예술이 될 때 · Art, Design & Architecture", "Read the city through museums, design landmarks, contemporary art and creative districts."),
        "slow_seoul": ("🌿 느리게 걷는 서울 · Parks & Slow Travel", "Leave the checklist behind for forests, riverside paths, parks and a slower Seoul."),
    },
    "zh-CN": {
        "journey_all": ("🧭 首尔的全部故事", "先从整座城市开始，让首尔给你一点惊喜。"),
        "royal_seoul": ("👑 왕의 길, 서울 · 王城首尔", "沿着宫殿庭院、古老城门与礼仪之路，走进朝鲜王朝的首尔。"),
        "alley_temperature": ("🏘️ 골목의 온도 · 韩屋与隐秘小巷", "穿过韩屋、咖啡馆、壁画与日常生活交叠的首尔小巷。"),
        "seoul_bite": ("🥢 서울 한입 · 市场与街头美食", "从热气腾腾的市场摊位、地方小吃与美食街区，一口一口认识首尔。"),
        "han_river_night": ("🌙 한강에 밤이 오면 · 汉江与城市夜色", "看汉江在夜里变成由桥梁、塔楼、倒影与城市灯火组成的风景。"),
        "seoul_now": ("🎧 지금, 서울 · 从K-Pop到圣水", "走进当下的首尔：音乐、时尚、咖啡馆、流行文化与快速变化的街区。"),
        "mountain_city": ("⛰️ 산이 품은 도시 · 山环抱的城市", "登上城市里的山，从屋顶之上重新理解山与首尔日常生活的关系。"),
        "art_city": ("🎨 도시가 예술이 될 때 · 艺术、设计与建筑", "从博物馆、设计地标、当代艺术与创意街区阅读这座城市。"),
        "slow_seoul": ("🌿 느리게 걷는 서울 · 公园与慢旅行", "暂时放下打卡清单，在森林、河边与公园里慢下来。"),
    },
    "ja": {
        "journey_all": ("🧭 ソウルのすべての物語", "まずは街全体から。ソウルそのものに旅先を選んでもらいましょう。"),
        "royal_seoul": ("👑 왕의 길, 서울 · 王の道、ソウル", "宮殿の中庭、古い城門、儀礼の道をたどり、朝鮮王朝のソウルを歩く。"),
        "alley_temperature": ("🏘️ 골목의 온도 · 韓屋と路地裏", "韓屋、カフェ、壁画、日常が重なる細い路地を歩く旅。"),
        "seoul_bite": ("🥢 서울 한입 · 市場とストリートフード", "湯気の立つ市場の屋台やローカルフードから、ひと口ずつソウルを知る。"),
        "han_river_night": ("🌙 한강에 밤이 오면 · 漢江と夜の街", "橋、タワー、水面の光が重なる、夜の漢江とソウルへ。"),
        "seoul_now": ("🎧 지금, 서울 · K-Popから聖水まで", "音楽、ファッション、カフェ、ポップカルチャーで“今のソウル”を歩く。"),
        "mountain_city": ("⛰️ 산이 품은 도시 · 山に抱かれた都市", "街の中の山へ登り、山と日常が共存するソウルを屋根の上から眺める。"),
        "art_city": ("🎨 도시가 예술이 될 때 · アート、デザイン、建築", "美術館、デザイン建築、現代アート、創作街区から都市を読み解く。"),
        "slow_seoul": ("🌿 느리게 걷는 서울 · 公園とスロートラベル", "観光リストから少し離れ、森、川辺、公園でゆっくり歩く。"),
    },
}

ALLEY_PLACES = {
    "북촌한옥마을", "익선동 한옥마을", "서촌마을", "정동길", "이화벽화마을",
    "한남동 카페거리", "해방촌", "경리단길", "연남동 경의선숲길",
    "상수동 카페거리", "합정동 골목", "성수동 카페거리", "문래 창작촌",
    "샤로수길", "이화여대길",
}

HAN_NIGHT_PLACES = {
    "이촌 한강공원", "잠실 한강공원", "난지한강공원", "망원 한강공원",
    "뚝섬 한강공원", "여의도 한강공원", "뚝섬유원지",
    "반포대교 달빛무지개분수", "세빛섬", "남산서울타워", "서울스카이",
    "롯데월드타워", "응봉산 팔각정", "낙산공원", "청계천 모전교",
}

MOUNTAIN_PLACES = {
    "아차산", "안산 자락길", "응봉산 팔각정", "하늘공원", "낙산공원",
    "남산서울타워", "남산골한옥마을",
}

ART_PLACES = {
    "동대문디자인플라자(DDP)", "국립중앙박물관", "전쟁기념관", "리움미술관",
    "국립한글박물관", "코엑스 별마당도서관", "한성백제박물관",
    "서울함 공원", "언더스탠드에비뉴", "성수연방", "예술의전당",
    "문래 창작촌", "서울시립미술관 남서울관", "커먼그라운드",
}


# ============================================================
# 4. SESSION STATE
# ============================================================

if "my_trip" not in st.session_state:
    st.session_state.my_trip = []

if "language_key" not in st.session_state:
    st.session_state.language_key = "English"

if "place_filter" not in st.session_state:
    st.session_state.place_filter = "__ALL__"


if "seoul_chat" not in st.session_state:
    st.session_state.seoul_chat = []


# ============================================================
# 5. TOP-RIGHT LANGUAGE SWITCH
# ============================================================

# ============================================================
# 5. TOP HEADER
#    Title and language selector are separated so neither gets clipped.
# ============================================================

st.markdown(
    """
    <div class="sfy-topbar">
        <div class="sfy-brand-wrap">
            <div class="top-brand">
                <span class="top-brand-dot"></span>
                SEOUL FOR YOU · 서울
            </div>
            <div class="sfy-mini-title">
                Find your Seoul story
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

language_options = ["English", "中文", "日本語"]

if st.session_state.language_key not in language_options:
    st.session_state.language_key = "English"

selected_lang_key = st.radio(
    "Language",
    options=language_options,
    index=language_options.index(st.session_state.language_key),
    key="language_switch",
    horizontal=True,
    label_visibility="collapsed",
    format_func=lambda x: {
        "English": "🇺🇸 EN",
        "中文": "🇨🇳 中文",
        "日本語": "🇯🇵 日本語",
    }.get(x, x),
)

if selected_lang_key != st.session_state.language_key:
    st.session_state.language_key = selected_lang_key
    st.rerun()

lang_code = LANG_CONFIG[st.session_state.language_key]["code"]
currency_code = LANG_CONFIG[st.session_state.language_key]["currency"]
txt = UI[lang_code]

# Apply the selected Chinese/Japanese local font.
apply_language_font(lang_code)

# Full-width editorial poster hero
# Rendered inside a Streamlit HTML component so Markdown never interprets
# nested <div> / <svg> blocks as code.

def build_hero_font_css(language_code):
    """Embed the selected CJK font inside the hero iframe."""
    if language_code == "zh-CN":
        font_path = find_local_asset("DaMengXiuKai-Regular-2.ttf")
        if font_path is not None:
            data_uri, font_format = font_to_data_uri(str(font_path))
            if data_uri is None:
                return "", "Arial, Helvetica, sans-serif"
            return (
                f"""
                @font-face {{
                    font-family: 'HeroCJK';
                    src: url('{data_uri}') format('{font_format}');
                    font-weight: normal;
                    font-style: normal;
                    font-display: swap;
                }}
                """,
                "'HeroCJK', sans-serif",
            )

    if language_code == "ja":
        font_path = (
            find_local_asset("ipamp.ttf")
            or find_local_asset("ipam.ttf")
        )
        if font_path is not None:
            data_uri, font_format = font_to_data_uri(str(font_path))
            if data_uri is None:
                return "", "Arial, Helvetica, sans-serif"
            return (
                f"""
                @font-face {{
                    font-family: 'HeroCJK';
                    src: url('{data_uri}') format('{font_format}');
                    font-weight: normal;
                    font-style: normal;
                    font-display: swap;
                }}
                """,
                "'HeroCJK', serif",
            )

    return "", "Arial, Helvetica, sans-serif"


hero_font_face, hero_body_font = build_hero_font_css(lang_code)

hero_component_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{hero_font_face}

:root {{
    --sage: #F8F9EC;
    --sage-deep: #EEF1D8;
    --coral: #EFC1AE;
    --coral-strong: #E9A996;
    --cream: #EEE4C7;
    --green: #596E58;
    --green-soft: #879780;
    --ink: #39483B;
}}

* {{
    box-sizing: border-box;
}}

html,
body {{
    margin: 0;
    padding: 0;
    background: transparent;
    overflow: hidden;
}}

.poster-hero {{
    position: relative;
    width: 100%;
    height: 430px;
    overflow: hidden;
    border: 1.5px solid rgba(57,72,59,0.24);
    border-radius: 26px;
    background:
        radial-gradient(
            circle at 76% 28%,
            rgba(238,228,199,0.38),
            transparent 28%
        ),
        linear-gradient(
            145deg,
            #F8F9EB 0%,
            #EFF2D8 100%
        );
}}

.poster-topline {{
    position: absolute;
    top: 24px;
    left: 20px;
    right: 20px;
    z-index: 4;
    text-align: center;
    color: var(--coral-strong);
    font-family:
        "Malgun Gothic",
        "Apple SD Gothic Neo",
        sans-serif;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.08em;
}}

.poster-wordmark {{
    position: absolute;
    left: 4.5%;
    top: 58px;
    z-index: 1;
    font-family:
        Arial Black,
        Arial,
        Helvetica,
        sans-serif;
    font-size: clamp(82px, 10vw, 142px);
    font-weight: 900;
    line-height: 0.79;
    letter-spacing: -0.075em;
    color: var(--coral);
    text-transform: uppercase;
    user-select: none;
}}

.poster-gate {{
    position: absolute;
    z-index: 3;
    width: min(430px, 44vw);
    left: 54%;
    top: 50%;
    transform: translate(-50%, -45%);
    filter: drop-shadow(0 8px 0 rgba(89,110,88,0.06));
}}

.poster-seal {{
    position: absolute;
    right: 4.5%;
    top: 55px;
    z-index: 4;
    width: 70px;
    height: 70px;
    border: 1.5px solid var(--green);
    border-radius: 50%;
    display: grid;
    place-items: center;
    color: var(--green);
    background: rgba(238,228,199,0.5);
    font-family:
        "Malgun Gothic",
        "Apple SD Gothic Neo",
        sans-serif;
    font-size: 16px;
    line-height: 1.1;
    font-weight: 800;
    text-align: center;
}}

.poster-caption {{
    position: absolute;
    left: 5%;
    right: 5%;
    bottom: 24px;
    z-index: 5;
    display: flex;
    justify-content: space-between;
    align-items: end;
    gap: 18px;
    color: var(--green);
}}

.poster-caption-main {{
    max-width: 760px;
    font-family: {hero_body_font};
    font-size: 15px;
    line-height: 1.55;
    font-weight: 650;
}}

.poster-caption-small {{
    font-family:
        Arial,
        Helvetica,
        sans-serif;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.13em;
    white-space: nowrap;
    text-transform: uppercase;
}}

@media (max-width: 900px) {{
    .poster-wordmark {{
        top: 68px;
        font-size: clamp(68px, 14vw, 112px);
    }}

    .poster-gate {{
        width: min(360px, 58vw);
        left: 60%;
    }}

    .poster-seal {{
        width: 58px;
        height: 58px;
        font-size: 14px;
        right: 3.5%;
    }}
}}

@media (max-width: 620px) {{
    .poster-hero {{
        height: 360px;
        border-radius: 20px;
    }}

    .poster-topline {{
        font-size: 10px;
    }}

    .poster-wordmark {{
        top: 76px;
        font-size: clamp(58px, 18vw, 84px);
        line-height: 0.83;
    }}

    .poster-gate {{
        width: min(300px, 74vw);
        left: 58%;
        top: 54%;
    }}

    .poster-seal {{
        display: none;
    }}

    .poster-caption {{
        bottom: 17px;
    }}

    .poster-caption-main {{
        font-size: 13px;
    }}

    .poster-caption-small {{
        display: none;
    }}
}}
</style>
</head>

<body>
<div class="poster-hero">
    <div class="poster-topline">
        한국의 오래된 시간과 오늘을 걸어보세요
    </div>

    <div class="poster-wordmark">
        SEOUL<br>
        <span>FOR YOU</span><br>
        SEOUL
    </div>

    <div class="poster-gate">
        <svg
            viewBox="0 0 520 330"
            width="100%"
            xmlns="http://www.w3.org/2000/svg"
            aria-label="Korean pavilion illustration"
        >
            <path
                d="M55 116 Q260 22 465 116 Q408 102 354 105 Q307 107 260 125 Q213 107 166 105 Q112 102 55 116Z"
                fill="#596E58"
            />
            <path
                d="M92 118 Q260 73 428 118 L399 141 Q260 121 121 141Z"
                fill="#879780"
            />

            <rect x="133" y="137" width="254" height="82" rx="5" fill="#EEE4C7"/>
            <rect x="155" y="151" width="210" height="55" fill="#E9A996"/>

            <rect x="170" y="151" width="15" height="55" fill="#596E58"/>
            <rect x="220" y="151" width="15" height="55" fill="#596E58"/>
            <rect x="285" y="151" width="15" height="55" fill="#596E58"/>
            <rect x="335" y="151" width="15" height="55" fill="#596E58"/>

            <path
                d="M85 215 Q260 155 435 215 Q386 204 338 206 Q298 207 260 222 Q222 207 182 206 Q134 204 85 215Z"
                fill="#596E58"
            />
            <path
                d="M115 217 Q260 181 405 217 L382 237 Q260 224 138 237Z"
                fill="#879780"
            />

            <rect x="153" y="233" width="214" height="62" rx="4" fill="#EEE4C7"/>
            <rect x="178" y="246" width="164" height="42" fill="#E9A996"/>

            <rect x="191" y="246" width="14" height="42" fill="#596E58"/>
            <rect x="246" y="246" width="14" height="42" fill="#596E58"/>
            <rect x="315" y="246" width="14" height="42" fill="#596E58"/>

            <path
                d="M115 294 H405 L431 315 H89 Z"
                fill="#EEE4C7"
            />
        </svg>
    </div>

    <div class="poster-seal">
        서울<br>旅
    </div>

    <div class="poster-caption">
        <div class="poster-caption-main">
            {txt["tagline"]}
        </div>

        <div class="poster-caption-small">
            KOREA · SEOUL · YOUR STORY
        </div>
    </div>
</div>
</body>
</html>
"""

components.html(
    hero_component_html,
    height=445,
    scrolling=False,
)


# ============================================================
# 6. TRANSLATION HELPERS
# ============================================================

@st.cache_data(show_spinner=False, ttl=60 * 60 * 24 * 30)
def translate_single(text, target_lang, source_lang="auto"):
    """Translate UI/detail text with a two-step fallback.

    1) deep_translator.GoogleTranslator
    2) Google public translate endpoint via requests

    Unlike the old version, this function does not silently treat a failed
    translation as a successful one when Korean text is still present.
    """
    if text is None:
        return ""

    text = str(text).strip()
    if not text or text.lower() == "nan":
        return ""

    if target_lang in (None, "ko"):
        return text

    target_map = {
        "en": "en",
        "zh-CN": "zh-CN",
        "ja": "ja",
    }
    target = target_map.get(target_lang, target_lang)

    # Detect whether Korean remains in the result. For an English/Chinese/
    # Japanese translation, a full Korean sentence generally means the call
    # failed or returned the source unchanged.
    def still_korean(value):
        return bool(re.search(r"[가-힣]", str(value)))

    # 1) deep-translator
    try:
        source = "ko" if source_lang == "ko" else "auto"
        result = GoogleTranslator(source=source, target=target).translate(text)
        if result and (not still_korean(result) or not still_korean(text)):
            return str(result).strip()
    except Exception:
        pass

    # 2) HTTP fallback. Keep chunks comfortably below common query limits.
    try:
        response = requests.get(
            "https://translate.googleapis.com/translate_a/single",
            params={
                "client": "gtx",
                "sl": "ko" if source_lang == "ko" else "auto",
                "tl": target,
                "dt": "t",
                "q": text,
            },
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=12,
        )
        response.raise_for_status()
        payload = response.json()
        translated = "".join(
            part[0]
            for part in payload[0]
            if part and part[0]
        ).strip()
        if translated and (not still_korean(translated) or not still_korean(text)):
            return translated
    except Exception:
        pass

    # Do not pretend Korean is a successful foreign-language translation.
    return None


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24 * 30)
def batch_translate(texts, target_lang, chunk_size=20):
    texts = ["" if x is None else str(x) for x in texts]
    return [
        translate_single(text, target_lang) or text
        for text in texts
    ]


# ============================================================
# 7. WEATHER / EXCHANGE RATE
# ============================================================

@st.cache_data(ttl=1800, show_spinner=False)
def get_weather():
    try:
        response = requests.get(
            "https://wttr.in/Seoul?format=j1",
            timeout=6,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        data = response.json()["current_condition"][0]
        return {
            "temp": int(data["temp_C"]),
            "desc": data["weatherDesc"][0]["value"],
        }
    except Exception:
        return {"temp": None, "desc": "Unavailable"}


@st.cache_data(ttl=3600, show_spinner=False)
def get_exchange_rate(currency):
    try:
        response = requests.get(
            f"https://open.er-api.com/v6/latest/{currency}",
            timeout=6,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        data = response.json()
        return float(data["rates"]["KRW"])
    except Exception:
        return None


weather = get_weather()
exchange_rate = get_exchange_rate(currency_code)

weather_desc_display = translate_single(weather["desc"], lang_code)
weather_value = (
    f"{weather['temp']}°C · {weather_desc_display}"
    if weather["temp"] is not None
    else weather_desc_display
)
exchange_value = (
    f"1 {currency_code} = ₩{exchange_rate:,.0f}"
    if exchange_rate is not None
    else "—"
)


# ============================================================
# 8. LOAD CSV
# ============================================================

@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "places_global.csv")

    if not os.path.exists(csv_path):
        st.error("places_global.csv was not found in the same folder as this app.")
        st.stop()

    df = pd.read_csv(csv_path, encoding="utf-8-sig")

    required = {"gu", "name", "desc", "directions", "img", "lat", "lon"}
    missing = required - set(df.columns)
    if missing:
        st.error(f"Missing CSV columns: {', '.join(sorted(missing))}")
        st.stop()

    return df


df = load_data()


# ============================================================
# 9. FALLBACK TRAVEL METADATA
#    Existing CSV works even without extra columns.
#    If you later add these columns manually, your CSV values win.
# ============================================================

def contains_any(text, words):
    return any(word in text for word in words)


def infer_themes(row):
    text = f"{row['name']} {row['desc']}"
    themes = []

    if contains_any(text, [
        "궁", "종묘", "한옥", "숭례문", "성당", "조계사", "선릉", "정릉",
        "역사", "전통", "백제", "사육신", "형무소", "기념관"
    ]):
        themes.append("traditional")

    if contains_any(text, [
        "K-Star", "홍대", "강남역", "압구정", "청담", "DDP", "한류",
        "K-", "공연", "예술의전당", "문래", "성수"
    ]):
        themes.append("kculture")

    if contains_any(text, [
        "시장", "먹자", "맛의거리", "수산", "먹거리", "음식", "골목"
    ]):
        themes.append("food")

    if contains_any(text, [
        "야경", "타워", "서울스카이", "63", "달빛", "세빛", "한강공원",
        "청계천", "DDP", "낙산공원", "응봉산", "석촌호수"
    ]):
        themes.append("night_seoul")

    if contains_any(text, [
        "공원", "산", "숲", "한강", "양재천", "청계천", "호수", "자락길",
        "유원지", "가족공원", "선유도", "하늘공원"
    ]):
        themes.append("nature")

    if contains_any(text, [
        "카페", "성수", "연남", "익선", "서촌", "해방촌", "경리단",
        "가로수길", "로데오", "샤로수길", "합정", "상수", "커먼그라운드",
        "언더스탠드", "성수연방", "문래", "이태원"
    ]):
        themes.append("trendy")

    if contains_any(text, [
        "쇼핑", "시장", "더현대", "IFC몰", "코엑스", "명동", "가로수길",
        "로데오", "청담", "커먼그라운드", "쌈지길"
    ]):
        themes.append("shopping")

    if contains_any(text, [
        "궁", "한옥", "타워", "전망", "벽화", "DDP", "호수", "공원", "산",
        "숲", "다리", "분수", "세빛", "서울로", "성당", "정동길"
    ]):
        themes.append("photo")

    if not themes:
        themes = ["trendy"]

    return "|".join(dict.fromkeys(themes))


def infer_duration_hours(row):
    name = row["name"]
    text = f"{name} {row['desc']}"

    if "롯데월드 어드벤처" in name:
        return 6.0
    if contains_any(text, ["국립중앙박물관", "올림픽공원", "서울어린이대공원"]):
        return 4.0
    if contains_any(text, ["궁", "박물관", "미술관", "전쟁기념관", "예술의전당", "한강공원", "서울숲"]):
        return 2.5
    if contains_any(text, ["산", "자락길", "하늘공원", "월드컵공원"]):
        return 3.0
    if contains_any(text, ["시장", "거리", "마을", "카페", "골목", "공원", "호수"]):
        return 2.0
    return 1.5


def infer_cost_rank(row):
    name = row["name"]
    text = f"{name} {row['desc']}"

    if contains_any(name, ["롯데월드 어드벤처"]):
        return 3
    if contains_any(name, ["서울스카이", "63스퀘어", "남산서울타워"]):
        return 2
    if contains_any(text, ["궁", "미술관", "박물관", "전망대", "전시"]):
        return 1
    return 0


def infer_indoor(row):
    text = f"{row['name']} {row['desc']}"
    return contains_any(text, [
        "박물관", "미술관", "도서관", "몰", "더현대", "코엑스", "예술의전당",
        "DDP", "롯데월드 어드벤처", "시장", "쌈지길", "성당"
    ])


def infer_night(row):
    themes = row["themes"].split("|")
    return "night_seoul" in themes


def infer_best_time(row):
    name = row["name"]
    text = f"{name} {row['desc']}"

    if infer_night(row):
        return "evening"
    if contains_any(text, ["궁", "시장", "산", "자락길"]):
        return "morning"
    if infer_indoor(row):
        return "anytime"
    return "afternoon"


def infer_styles(row):
    text = f"{row['name']} {row['desc']}"
    styles = ["solo", "couple", "friends"]

    if contains_any(text, [
        "공원", "박물관", "미술관", "롯데월드", "도서관", "한강", "서울숲",
        "가족", "어린이", "올림픽공원", "석촌호수"
    ]):
        styles.append("family")

    return "|".join(dict.fromkeys(styles))


def infer_situations(row):
    situations = []
    if row["indoor"]:
        situations.extend(["rainy", "indoor", "hot"])
    if row["night_ok"]:
        situations.append("night")
    if "nature" in row["themes"].split("|"):
        situations.append("hot")
    return "|".join(dict.fromkeys(situations))


if "themes" not in df.columns:
    df["themes"] = df.apply(infer_themes, axis=1)

if "duration_hours" not in df.columns:
    df["duration_hours"] = df.apply(infer_duration_hours, axis=1)

if "cost_rank" not in df.columns:
    df["cost_rank"] = df.apply(infer_cost_rank, axis=1)

if "indoor" not in df.columns:
    df["indoor"] = df.apply(infer_indoor, axis=1)

if "night_ok" not in df.columns:
    df["night_ok"] = df.apply(infer_night, axis=1)

if "best_time" not in df.columns:
    df["best_time"] = df.apply(infer_best_time, axis=1)

if "styles" not in df.columns:
    df["styles"] = df.apply(infer_styles, axis=1)

if "situations" not in df.columns:
    df["situations"] = df.apply(infer_situations, axis=1)


# ============================================================
# 10. MULTILINGUAL PLACE / DISTRICT NAMES
#     places_global.csv is the source of truth for names.
#     Description/directions use a translated column if present,
#     otherwise they fall back to cached Google translation.
# ============================================================

LANG_SUFFIX = {
    "en": "en",
    "zh-CN": "zh-CN",
    "ja": "ja",
}


def localized_column_value(row, base_field, language_code):
    suffix = LANG_SUFFIX.get(language_code)

    if suffix:
        column_name = f"{base_field}_{suffix}"
        if column_name in row.index:
            value = row[column_name]
            if pd.notna(value) and str(value).strip():
                return str(value).strip()

    original = row.get(base_field, "")
    if pd.isna(original):
        return ""
    return str(original).strip()


# Stable, pre-translated names from places_global.csv
name_column = f"name_{LANG_SUFFIX[lang_code]}"
gu_column = f"gu_{LANG_SUFFIX[lang_code]}"

if name_column in df.columns:
    df["display_name"] = df[name_column].fillna(df["name"]).astype(str)
else:
    df["display_name"] = df["name"].astype(str)

if gu_column in df.columns:
    df["display_gu"] = df[gu_column].fillna(df["gu"]).astype(str)
else:
    df["display_gu"] = df["gu"].astype(str)

# Maps are still useful for filtering by the Korean canonical value.
name_map = dict(zip(df["name"].astype(str), df["display_name"].astype(str)))
gu_map = dict(zip(df["gu"].astype(str), df["display_gu"].astype(str)))


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24 * 30)
def translate_korean_detail(text, target_lang):
    if text is None:
        return ""

    text = str(text).strip()
    if not text or text.lower() == "nan":
        return ""

    translated = translate_single(
        text,
        target_lang,
        source_lang="ko",
    )
    return translated


def localized_detail(row, field, language_code):
    """Use static translated CSV fields first, then live translation."""
    suffix = LANG_SUFFIX.get(language_code)

    if suffix:
        translated_column = f"{field}_{suffix}"
        if translated_column in row.index:
            value = row[translated_column]
            if pd.notna(value) and str(value).strip():
                return str(value).strip()

    original = row.get(field, "")
    if pd.isna(original):
        return ""

    # English / Chinese / Japanese detail copy is generated only when needed.
    translated = translate_korean_detail(original, language_code)
    return translated


# ============================================================
# 11. IMAGE LOADER + WIKIMEDIA FALLBACK
# ============================================================

IMAGE_HEADERS = {
    "User-Agent": "SeoulForYou/1.0 (educational Seoul tourism map; Streamlit)",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
}


def fetch_image_bytes(image_source):
    """Read one image URL/local path. Returns None immediately on failure."""
    if image_source is None:
        return None

    source = str(image_source).strip()
    if not source or source.lower() == "nan":
        return None

    try:
        if source.startswith(("http://", "https://")):
            response = requests.get(
                source,
                timeout=12,
                allow_redirects=True,
                headers=IMAGE_HEADERS,
            )
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "").lower()
            if "image" not in content_type:
                return None
            if len(response.content) < 1000:
                return None
            return response.content

        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = source if os.path.isabs(source) else os.path.join(current_dir, source)
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            data = f.read()
        return data if len(data) >= 1000 else None

    except Exception:
        return None


@st.cache_data(ttl=604800, show_spinner=False)
def find_wikipedia_image_url(place_name):
    """Try Korean Wikipedia first: exact page, then search results."""
    if not place_name:
        return None

    api_url = "https://ko.wikipedia.org/w/api.php"
    common = {
        "action": "query",
        "format": "json",
        "formatversion": 2,
        "prop": "pageimages",
        "piprop": "thumbnail",
        "pithumbsize": 1400,
        "pilicense": "free",
        "redirects": 1,
    }

    # 1) Exact Korean page title
    try:
        params = dict(common)
        params["titles"] = str(place_name)
        res = requests.get(api_url, params=params, headers=IMAGE_HEADERS, timeout=8)
        res.raise_for_status()
        pages = res.json().get("query", {}).get("pages", [])
        for page in pages:
            thumb = page.get("thumbnail", {}).get("source")
            if thumb:
                return thumb
    except Exception:
        pass

    # 2) Korean Wikipedia search, useful for names such as DDP / Seoul Sky
    try:
        params = dict(common)
        params.update({
            "generator": "search",
            "gsrsearch": f"{place_name} 서울",
            "gsrnamespace": 0,
            "gsrlimit": 5,
        })
        res = requests.get(api_url, params=params, headers=IMAGE_HEADERS, timeout=8)
        res.raise_for_status()
        pages = res.json().get("query", {}).get("pages", [])
        pages = sorted(pages, key=lambda x: x.get("index", 999))
        for page in pages:
            thumb = page.get("thumbnail", {}).get("source")
            if thumb:
                return thumb
    except Exception:
        pass

    return None


@st.cache_data(ttl=604800, show_spinner=False)
def find_commons_image_url(place_name):
    """Search Wikimedia Commons when Wikipedia has no suitable lead image."""
    if not place_name:
        return None

    api_url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "formatversion": 2,
        "generator": "search",
        "gsrsearch": f"{place_name} Seoul",
        "gsrnamespace": 6,
        "gsrlimit": 8,
        "prop": "imageinfo",
        "iiprop": "url|mime",
        "iiurlwidth": 1400,
    }

    blocked_words = (
        "logo", "icon", "map", "route", "diagram", "symbol", "flag",
        "seal", "emblem", "plan", "floor", "sign.svg", "locator",
    )

    try:
        res = requests.get(api_url, params=params, headers=IMAGE_HEADERS, timeout=10)
        res.raise_for_status()
        pages = res.json().get("query", {}).get("pages", [])
        pages = sorted(pages, key=lambda x: x.get("index", 999))

        for page in pages:
            title = str(page.get("title", "")).lower()
            if any(word in title for word in blocked_words):
                continue

            infos = page.get("imageinfo", [])
            if not infos:
                continue

            info = infos[0]
            mime = str(info.get("mime", "")).lower()
            if not mime.startswith("image/"):
                continue
            if mime == "image/svg+xml":
                continue

            return info.get("thumburl") or info.get("url")

    except Exception:
        pass

    return None


@st.cache_data(ttl=604800, show_spinner=False)
def load_place_image_bytes(place_name, csv_image_source):
    """
    Image priority:
    1) CSV image
    2) Korean Wikipedia lead image
    3) Wikimedia Commons image search
    """

    # Existing curated CSV image first.
    original = fetch_image_bytes(csv_image_source)
    if original is not None:
        return original, "csv"

    # Stable Wikipedia thumbnail.
    wiki_url = find_wikipedia_image_url(str(place_name))
    wiki_image = fetch_image_bytes(wiki_url)
    if wiki_image is not None:
        return wiki_image, "wikipedia"

    # Last-resort Commons search.
    commons_url = find_commons_image_url(str(place_name))
    commons_image = fetch_image_bytes(commons_url)
    if commons_image is not None:
        return commons_image, "commons"

    return None, None


# ============================================================
# 12. HELPERS
# ============================================================

def cost_label(rank):
    return {
        0: txt["free_label"],
        1: txt["low_label"],
        2: txt["mid_label"],
        3: txt["premium_label"],
    }.get(int(rank), txt["mid_label"])


def best_time_label(key):
    return txt.get(key, key)


def duration_label(hours):
    if hours <= 2:
        return txt["two_hours"]
    if hours <= 4:
        return txt["half_day"]
    return txt["full_day"]


def theme_label(theme_key):
    return f"{THEME_KEYS.get(theme_key, '📍')} {txt.get(theme_key, theme_key)}"


def journey_label(journey_key):
    return JOURNEY_COPY[lang_code][journey_key][0]


def journey_description(journey_key):
    return JOURNEY_COPY[lang_code][journey_key][1]


def matches_journey_theme(row, journey_key):
    if journey_key == "journey_all":
        return True

    # places_global.csv can explicitly assign documentary-style story themes.
    if "journeys" in row.index and pd.notna(row["journeys"]):
        explicit_journeys = set(str(row["journeys"]).split("|"))
        return journey_key in explicit_journeys

    name = str(row["name"])
    themes = set(str(row["themes"]).split("|"))

    if journey_key == "royal_seoul":
        return "traditional" in themes
    if journey_key == "alley_temperature":
        return name in ALLEY_PLACES
    if journey_key == "seoul_bite":
        return "food" in themes
    if journey_key == "han_river_night":
        return name in HAN_NIGHT_PLACES
    if journey_key == "seoul_now":
        return "kculture" in themes or ("trendy" in themes and "shopping" in themes)
    if journey_key == "mountain_city":
        return name in MOUNTAIN_PLACES
    if journey_key == "art_city":
        return name in ART_PLACES
    if journey_key == "slow_seoul":
        return "nature" in themes and name not in MOUNTAIN_PLACES

    return True


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def add_to_trip(place_name):
    if place_name not in st.session_state.my_trip:
        st.session_state.my_trip.append(place_name)


def remove_from_trip(place_name):
    if place_name in st.session_state.my_trip:
        st.session_state.my_trip.remove(place_name)


def clear_trip():
    st.session_state.my_trip = []


def select_place(place_name):
    st.session_state.place_filter = place_name



# ============================================================
# 12-1. SEOUL AI TRAVEL GUIDE
# ============================================================

def get_openai_api_key():
    """Read the API key from Streamlit secrets or environment variables."""
    try:
        secret_key = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        secret_key = ""

    return secret_key or os.getenv("OPENAI_API_KEY", "")


def get_openai_model():
    """Read model from Streamlit secrets/environment, with a safe default."""
    try:
        secret_model = st.secrets.get("OPENAI_MODEL", "")
    except Exception:
        secret_model = ""

    return secret_model or os.getenv("OPENAI_MODEL", "gpt-5.6-luna")


def explain_openai_error(error):
    """
    Convert OpenAI/SDK exceptions into a useful message without exposing
    the API key or other secrets.
    """
    error_text = str(error).strip()
    error_lower = error_text.lower()

    status_code = getattr(error, "status_code", None)
    body = getattr(error, "body", None)

    error_code = None
    if isinstance(body, dict):
        body_error = body.get("error", body)
        if isinstance(body_error, dict):
            error_code = body_error.get("code") or body_error.get("type")

    # Old SDK / Responses API unavailable
    if (
        isinstance(error, AttributeError)
        or "has no attribute 'responses'" in error_lower
        or "object has no attribute 'responses'" in error_lower
    ):
        return (
            "OpenAI Python package is too old for the Responses API. "
            "In the VS Code terminal, run: `pip install -U openai`, "
            "then completely restart Streamlit."
        )

    # Authentication / invalid key
    if status_code == 401 or "invalid_api_key" in error_lower or "incorrect api key" in error_lower:
        return (
            "The API key was rejected (401). Check that the full key was pasted "
            "without spaces, and that it belongs to an active OpenAI API project."
        )

    # Billing / quota
    billing_codes = {
        "insufficient_quota",
        "credit_balance_exhausted",
        "organization_usage_limit_exceeded",
        "organization_spend_limit_exceeded",
        "project_spend_limit_exceeded",
    }
    if (
        status_code == 429
        or error_code in billing_codes
        or "insufficient_quota" in error_lower
        or "credit balance" in error_lower
        or "spend limit" in error_lower
    ):
        return (
            "The API request reached a billing/quota limit. Creating a new API key "
            "does not add API credits. Check API Platform billing, prepaid credits, "
            "and the project/organization spend limit."
        )

    # Model unavailable / permissions
    if (
        status_code == 404
        or "model_not_found" in error_lower
        or ("model" in error_lower and "access" in error_lower)
    ):
        return (
            f"The selected model (`{get_openai_model()}`) is not available to this API project. "
            "Try a model that your project can access, or check the project permissions."
        )

    # Network
    if (
        "connection" in error_lower
        or "timeout" in error_lower
        or "timed out" in error_lower
    ):
        return (
            "The app could not reach the OpenAI API. Check the internet connection, "
            "VPN/firewall, and then try again."
        )

    # Generic but still useful
    short_error = error_text[:500] if error_text else error.__class__.__name__
    return f"OpenAI API error: `{short_error}`"


def build_seoul_ai_context(question, max_places=12):
    """
    Select a compact set of relevant places from the local curated CSV.
    This keeps requests small while grounding recommendations in this app.
    """
    q = str(question).lower().strip()
    scored = []

    rainy_terms = ["rain", "rainy", "비", "雨", "下雨"]
    night_terms = ["night", "evening", "야경", "밤", "夜"]
    food_terms = ["food", "eat", "market", "먹", "맛집", "美食", "吃", "グルメ", "食"]
    nature_terms = ["nature", "park", "hike", "mountain", "공원", "산", "自然", "公园", "山", "公園"]

    wants_rain = any(term in q for term in rainy_terms)
    wants_night = any(term in q for term in night_terms)
    wants_food = any(term in q for term in food_terms)
    wants_nature = any(term in q for term in nature_terms)

    for _, row in df.iterrows():
        searchable = " ".join([
            str(row.get("name", "")),
            str(row.get("display_name", "")),
            str(row.get("gu", "")),
            str(row.get("display_gu", "")),
            str(row.get("themes", "")),
            str(row.get("journeys", "")),
            str(row.get("desc", ""))[:300],
        ]).lower()

        score = 0
        for token in re.findall(r"[\w가-힣一-龥ぁ-んァ-ン]+", q):
            if len(token) >= 2 and token in searchable:
                score += 3

        if wants_rain and bool(row.get("indoor", False)):
            score += 4
        if wants_night and bool(row.get("night_ok", False)):
            score += 4
        if wants_food and "food" in str(row.get("themes", "")):
            score += 4
        if wants_nature and "nature" in str(row.get("themes", "")):
            score += 4

        scored.append((score, row))

    scored.sort(key=lambda item: item[0], reverse=True)
    selected = [row for score, row in scored[:max_places] if score > 0]

    if not selected:
        selected = [row for _, row in scored[:max_places]]

    lines = []
    for row in selected:
        lines.append(
            " | ".join([
                f"Name: {row.get('display_name', row.get('name', ''))}",
                f"District: {row.get('display_gu', row.get('gu', ''))}",
                f"Themes: {row.get('themes', '')}",
                f"Suggested stay: {row.get('duration_hours', '')}h",
                f"Indoor: {row.get('indoor', '')}",
                f"Night: {row.get('night_ok', '')}",
                f"Description: {str(row.get('desc', ''))[:220]}",
            ])
        )

    return "\n".join(lines)


def ask_seoul_travel_ai(question, api_key):
    """Ask OpenAI's Responses API for a concise Seoul-travel answer."""
    if OpenAI is None:
        raise RuntimeError("openai package is not installed.")

    language_name = {
        "en": "English",
        "zh-CN": "Simplified Chinese",
        "ja": "Japanese",
    }.get(lang_code, "English")

    local_context = build_seoul_ai_context(question)

    recent_history = st.session_state.seoul_chat[-6:]
    history_text = "\n".join(
        f"{item['role'].upper()}: {item['content']}"
        for item in recent_history
    )

    instructions = f"""
You are the AI travel guide inside 'Seoul for You', a Seoul travel map for international visitors.
Always answer in {language_name}.
Be practical, concise, friendly, and specific.
Use the curated Seoul place context when relevant.
For opening hours, ticket prices, temporary closures, reservations, or other real-time facts,
tell the traveler to verify the latest information on the official venue or Visit Seoul site
unless the information is explicitly present in the provided context.
Do not invent transit exits, prices, or opening times.
When useful, suggest 2-4 places rather than overwhelming the traveler.
"""

    prompt = f"""
CURATED MAP CONTEXT:
{local_context}

RECENT CONVERSATION:
{history_text}

TRAVELER QUESTION:
{question}
"""

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=get_openai_model(),
        instructions=instructions,
        input=prompt,
    )

    answer = getattr(response, "output_text", "")
    if not answer:
        raise RuntimeError("Empty response from OpenAI.")
    return answer.strip()


# ============================================================
# 13. WEATHER-BASED AUTO SITUATION
# ============================================================

weather_text_lower = str(weather["desc"]).lower()

if any(word in weather_text_lower for word in ["rain", "drizzle", "shower", "storm"]):
    auto_situation = "rainy"
    today_tip = txt["rain_tip"]
elif weather["temp"] is not None and weather["temp"] >= 29:
    auto_situation = "hot"
    today_tip = txt["hot_tip"]
else:
    auto_situation = "any"
    today_tip = txt["normal_tip"]


# ============================================================
# 14. SIDEBAR: SEOUL AI + FILTERS
# ============================================================

with st.sidebar:
    st.markdown(
        f"""
        <div class="ai-guide-card">
            <div class="ai-guide-kicker">SEOUL AI GUIDE</div>
            <div class="ai-guide-title">💬 {txt["ai_title"]}</div>
            <div class="ai-guide-subtitle">{txt["ai_subtitle"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    api_key = get_openai_api_key()

    # Only show API setup UI when no key is already configured.
    if not api_key:
        with st.expander("⚙️ AI setup", expanded=False):
            api_key = st.text_input(
                txt["ai_api_key"],
                type="password",
                key="openai_key_input",
                placeholder="sk-...",
                help=(
                    "Used only for this Streamlit session unless "
                    "OPENAI_API_KEY is stored in Streamlit secrets or your environment."
                ),
            )
            if not api_key:
                st.caption(txt["ai_api_missing"])

    if OpenAI is None:
        st.warning(txt["ai_install"])

    # Keep previous answers visible, but avoid a large empty chat panel.
    if st.session_state.seoul_chat:
        chat_box = st.container(height=220, border=True)
        with chat_box:
            for message in st.session_state.seoul_chat[-6:]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    with st.form("seoul_ai_form", clear_on_submit=True):
        question = st.text_input(
            txt["ai_placeholder"],
            key="seoul_ai_question",
            label_visibility="collapsed",
        )
        ask_clicked = st.form_submit_button(
            txt["ai_send"],
            width="stretch",
        )

    if ask_clicked and question.strip():
        st.session_state.seoul_chat.append(
            {"role": "user", "content": question.strip()}
        )

        if OpenAI is None:
            st.session_state.seoul_chat.append(
                {"role": "assistant", "content": txt["ai_install"]}
            )
        elif not api_key:
            st.session_state.seoul_chat.append(
                {"role": "assistant", "content": txt["ai_api_missing"]}
            )
        else:
            try:
                with st.spinner("Seoul AI..."):
                    answer = ask_seoul_travel_ai(question.strip(), api_key)
                st.session_state.seoul_chat.append(
                    {"role": "assistant", "content": answer}
                )
            except Exception as e:
                diagnostic_message = explain_openai_error(e)
                st.session_state.seoul_chat.append(
                    {
                        "role": "assistant",
                        "content": (
                            f"{txt['ai_error']}\n\n"
                            f"**Diagnostic:** {diagnostic_message}"
                        ),
                    }
                )

        st.rerun()

    if st.session_state.seoul_chat:
        if st.button(
            txt["ai_clear"],
            key="clear_seoul_ai",
            width="stretch",
        ):
            st.session_state.seoul_chat = []
            st.rerun()

    st.divider()

st.sidebar.title(txt["filters"])

JOURNEY_OPTIONS = [
    "journey_all",
    "royal_seoul",
    "alley_temperature",
    "seoul_bite",
    "han_river_night",
    "seoul_now",
    "mountain_city",
    "art_city",
    "slow_seoul",
]
selected_theme = st.sidebar.selectbox(
    txt["theme"],
    JOURNEY_OPTIONS,
    format_func=journey_label,
)
st.sidebar.caption(journey_description(selected_theme))

TIME_OPTIONS = {
    txt["any"]: None,
    txt["two_hours"]: 2.0,
    txt["half_day"]: 4.0,
    txt["full_day"]: 8.0,
}
selected_time_label = st.sidebar.selectbox(txt["time"], list(TIME_OPTIONS.keys()))
selected_time_max = TIME_OPTIONS[selected_time_label]

BUDGET_OPTIONS = {
    txt["any"]: 3,
    txt["free"]: 0,
    txt["under_10k"]: 1,
    txt["under_30k"]: 2,
}
selected_budget_label = st.sidebar.selectbox(txt["budget"], list(BUDGET_OPTIONS.keys()))
selected_budget_rank = BUDGET_OPTIONS[selected_budget_label]

STYLE_OPTIONS = {
    txt["any"]: "any",
    txt["solo"]: "solo",
    txt["couple"]: "couple",
    txt["friends"]: "friends",
    txt["family"]: "family",
}
selected_style_label = st.sidebar.selectbox(txt["style"], list(STYLE_OPTIONS.keys()))
selected_style = STYLE_OPTIONS[selected_style_label]

SITUATION_OPTIONS = {
    txt["auto_weather"]: "auto",
    txt["any"]: "any",
    txt["rainy"]: "rainy",
    txt["hot"]: "hot",
    txt["night"]: "night",
    txt["indoor"]: "indoor",
}
selected_situation_label = st.sidebar.selectbox(txt["situation"], list(SITUATION_OPTIONS.keys()))
selected_situation = SITUATION_OPTIONS[selected_situation_label]
if selected_situation == "auto":
    selected_situation = auto_situation

AREA_OPTIONS = ["__ALL__"] + sorted(
    df["gu"].dropna().astype(str).unique().tolist()
)
selected_area = st.sidebar.selectbox(
    txt["area"],
    AREA_OPTIONS,
    format_func=lambda x: txt["all"] if x == "__ALL__" else gu_map.get(x, x),
)


# ============================================================
# 15. FILTERING + RECOMMENDATION SCORE
# ============================================================

filtered = df.copy()

if selected_theme != "journey_all":
    filtered = filtered[filtered.apply(lambda row: matches_journey_theme(row, selected_theme), axis=1)]

if selected_time_max is not None:
    filtered = filtered[filtered["duration_hours"] <= selected_time_max]

filtered = filtered[filtered["cost_rank"] <= selected_budget_rank]

if selected_style != "any":
    filtered = filtered[filtered["styles"].apply(lambda x: selected_style in str(x).split("|"))]

if selected_situation != "any":
    filtered = filtered[filtered["situations"].apply(lambda x: selected_situation in str(x).split("|"))]

if selected_area != "__ALL__":
    filtered = filtered[filtered["gu"] == selected_area]


def recommendation_score(row):
    score = 0
    themes = str(row["themes"]).split("|")
    situations = str(row["situations"]).split("|")
    styles = str(row["styles"]).split("|")

    if selected_theme != "journey_all" and matches_journey_theme(row, selected_theme):
        score += 4
    if selected_situation != "any" and selected_situation in situations:
        score += 3
    if selected_style != "any" and selected_style in styles:
        score += 2
    if row["cost_rank"] <= selected_budget_rank:
        score += 1
    if selected_time_max is None or row["duration_hours"] <= selected_time_max:
        score += 1

    # Gentle weather boost even if the user did not use Auto.
    if auto_situation in situations:
        score += 1

    return score


if len(filtered) > 0:
    filtered = filtered.copy()
    filtered["score"] = filtered.apply(recommendation_score, axis=1)
    filtered = filtered.sort_values(["score", "name"], ascending=[False, True])


# ============================================================
# 16. PLACE SELECTOR AFTER FILTERS
# ============================================================

available_names = filtered["name"].tolist()
place_options = ["__ALL__"] + available_names

if st.session_state.place_filter not in place_options:
    st.session_state.place_filter = "__ALL__"

selected_place = st.sidebar.selectbox(
    txt["place"],
    place_options,
    key="place_filter",
    format_func=lambda x: txt["all"] if x == "__ALL__" else name_map.get(x, x),
)

if selected_place == "__ALL__":
    final_df = filtered
else:
    final_df = filtered[filtered["name"] == selected_place]





# ============================================================
# 17. DASHBOARD SUMMARY
# ============================================================

metric1, metric2, metric3 = st.columns(3)
metric1.metric(txt["weather"], weather_value)
metric2.metric(txt["exchange"], exchange_value)
metric3.metric(txt["shown"], str(len(final_df)))

st.info(f"**{txt['today_tip']}:** {today_tip}")


# ============================================================
# 18. FOLIUM MAP
# ============================================================

st.subheader(txt["map_title"])

seoul_center = [37.5665, 126.9780]

if len(final_df) == 1 and pd.notna(final_df.iloc[0]["lat"]) and pd.notna(final_df.iloc[0]["lon"]):
    map_center = [float(final_df.iloc[0]["lat"]), float(final_df.iloc[0]["lon"])]
    zoom_start = 15
elif selected_area != "__ALL__" and len(final_df) > 0:
    map_center = [float(final_df["lat"].mean()), float(final_df["lon"].mean())]
    zoom_start = 13
else:
    map_center = seoul_center
    zoom_start = 11

m = folium.Map(
    location=map_center,
    zoom_start=zoom_start,
    tiles="OpenStreetMap",
    control_scale=True,
)

for _, row in final_df.iterrows():
    if pd.isna(row["lat"]) or pd.isna(row["lon"]):
        continue

    theme_chips = " · ".join(
        txt.get(theme, theme)
        for theme in str(row["themes"]).split("|")[:3]
    )

    popup_html = f"""
    <div style='width:220px'>
        <b style='font-size:15px'>{row['display_name']}</b><br>
        <span>{row['display_gu']}</span><br>
        <span style='font-size:12px;color:#666'>{theme_chips}</span>
    </div>
    """

    marker_radius = 9 if len(final_df) == 1 else 6.5

    folium.CircleMarker(
        location=[float(row["lat"]), float(row["lon"])],
        radius=marker_radius,
        tooltip=row["display_name"],
        popup=folium.Popup(popup_html, max_width=260),
        color="#596E58",
        weight=2,
        fill=True,
        fill_color="#E9A996",
        fill_opacity=0.96,
    ).add_to(m)

st_folium(
    m,
    height=520,
    use_container_width=True,
    returned_objects=[],
    key=f"main_map_{selected_theme}_{selected_area}_{selected_place}_{lang_code}",
)


# ============================================================
# 19. RECOMMENDED PLACES
# ============================================================

st.subheader(txt["recommended"])
st.caption(txt["recommended_sub"])

if len(filtered) == 0:
    st.warning(txt["no_results"])
else:
    top_places = filtered.head(6)
    cols = st.columns(3)

    for i, (_, row) in enumerate(top_places.iterrows()):
        with cols[i % 3]:
            themes_html = "".join(
                f'<span class="tag">{theme_label(t)}</span>'
                for t in str(row["themes"]).split("|")[:3]
            )

            st.markdown(
                f"""
                <div class="place-card">
                    <div style="font-size:1.05rem;font-weight:750">{row['display_name']}</div>
                    <div class="small-muted">{row['display_gu']}</div>
                    <div style="margin-top:8px">{themes_html}</div>
                    <div style="margin-top:12px;font-size:0.9rem">
                        ⏱ {duration_label(float(row['duration_hours']))}<br>
                        💰 {cost_label(int(row['cost_rank']))}<br>
                        🕒 {best_time_label(row['best_time'])}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.button(
                txt["open_map"],
                key=f"view_{row['name']}_{i}",
                width="stretch",
                on_click=select_place,
                args=(row["name"],),
            )


# ============================================================
# 20. DETAIL VIEW
# ============================================================

st.divider()
st.subheader(txt["details"])

if selected_place == "__ALL__":
    st.info(txt["select_detail"])
else:
    row = final_df.iloc[0]

    detail_left, detail_right = st.columns([1.05, 1.8])

    with detail_left:
        image_bytes, image_source_kind = load_place_image_bytes(
            row["name"],
            row.get("img"),
        )
        if image_bytes is not None:
            try:
                st.image(
                    BytesIO(image_bytes),
                    caption=row["display_name"],
                    width="stretch",
                )
                if image_source_kind in {"wikipedia", "commons"}:
                    st.caption("Photo: Wikimedia")
            except Exception:
                st.markdown(
                    f'<div class="image-placeholder">🖼️<br>{txt["image_unavailable"]}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                f'<div class="image-placeholder">🖼️<br>{txt["image_unavailable"]}</div>',
                unsafe_allow_html=True,
            )

    with detail_right:
        st.markdown(f"## {row['display_name']}")
        st.caption(row["display_gu"])

        theme_line = " ".join(
            f"`{theme_label(t)}`"
            for t in str(row["themes"]).split("|")
        )
        st.markdown(theme_line)

        detail_facts = " · ".join([
            f"⏱ {duration_label(float(row['duration_hours']))}",
            f"💰 {cost_label(int(row['cost_rank']))}",
            f"🕒 {best_time_label(row['best_time'])}",
            f"🏠 {txt['yes'] if bool(row['indoor']) else txt['no']}",
        ])
        st.caption(detail_facts)

        translated_desc = localized_detail(row, "desc", lang_code)
        translated_directions = localized_detail(row, "directions", lang_code)

        # If translation service is temporarily unavailable, show an explicit
        # status instead of silently presenting Korean as foreign-language copy.
        if not translated_desc:
            translated_desc = txt.get("translation_unavailable", "Translation temporarily unavailable.")
        if not translated_directions:
            translated_directions = txt.get("translation_unavailable", "Translation temporarily unavailable.")

        st.markdown(f"### {txt['description']}")
        st.write(translated_desc)

        st.markdown(f"### {txt['directions']}")
        st.write(translated_directions)

        if row["name"] in st.session_state.my_trip:
            st.success(txt["added"])
        else:
            st.button(
                f"♡ {txt['add_trip']}",
                width="stretch",
                on_click=add_to_trip,
                args=(row["name"],),
                key=f"add_{row['name']}",
            )


    # --------------------------------------------------------
    # Nearby places
    # --------------------------------------------------------

    st.markdown(f"### {txt['nearby']}")

    if pd.notna(row["lat"]) and pd.notna(row["lon"]):
        nearby = df[df["name"] != row["name"]].copy()
        nearby = nearby[pd.notna(nearby["lat"]) & pd.notna(nearby["lon"])]
        nearby["distance_km"] = nearby.apply(
            lambda x: haversine_km(
                float(row["lat"]),
                float(row["lon"]),
                float(x["lat"]),
                float(x["lon"]),
            ),
            axis=1,
        )
        nearby = nearby.sort_values("distance_km").head(4)

        near_cols = st.columns(4)
        for i, (_, nrow) in enumerate(nearby.iterrows()):
            with near_cols[i]:
                st.markdown(f"**{nrow['display_name']}**")
                st.caption(f"{nrow['display_gu']} · {nrow['distance_km']:.1f} km")
                st.button(
                    txt["open_map"],
                    key=f"near_{nrow['name']}_{i}",
                    width="stretch",
                    on_click=select_place,
                    args=(nrow["name"],),
                )


# ============================================================
# 21. MY SEOUL TRIP
# ============================================================

st.divider()
st.subheader(f"♡ {txt['my_trip']}")

if not st.session_state.my_trip:
    st.info(txt["my_trip_empty"])
else:
    trip_df = df[df["name"].isin(st.session_state.my_trip)].copy()
    order_map = {name: i for i, name in enumerate(st.session_state.my_trip)}
    trip_df["trip_order"] = trip_df["name"].map(order_map)
    trip_df = trip_df.sort_values("trip_order")

    for _, trip_row in trip_df.iterrows():
        c1, c2, c3 = st.columns([0.5, 5, 1])
        with c1:
            st.write(f"**{int(trip_row['trip_order']) + 1}**")
        with c2:
            st.write(f"**{trip_row['display_name']}**  ·  {trip_row['display_gu']}")
        with c3:
            st.button(
                txt["remove"],
                key=f"remove_{trip_row['name']}",
                on_click=remove_from_trip,
                args=(trip_row["name"],),
            )

    st.button(txt["clear"], on_click=clear_trip, key="clear_trip_button")
    st.caption(txt["route_note"])

    valid_trip = trip_df[pd.notna(trip_df["lat"]) & pd.notna(trip_df["lon"])]

    if len(valid_trip) >= 1:
        trip_center = [float(valid_trip["lat"].mean()), float(valid_trip["lon"].mean())]
        trip_map = folium.Map(location=trip_center, zoom_start=12, tiles="OpenStreetMap")

        route_points = []
        for _, trip_row in valid_trip.iterrows():
            point = [float(trip_row["lat"]), float(trip_row["lon"])]
            route_points.append(point)
            number = int(trip_row["trip_order"]) + 1
            folium.CircleMarker(
                point,
                radius=9,
                tooltip=f"{number}. {trip_row['display_name']}",
                color="#596E58",
                weight=2,
                fill=True,
                fill_color="#E9A996",
                fill_opacity=1,
            ).add_to(trip_map)

        if len(route_points) >= 2:
            folium.PolyLine(
                route_points,
                weight=4,
                opacity=0.86,
                color="#596E58",
            ).add_to(trip_map)

        st_folium(
            trip_map,
            height=420,
            use_container_width=True,
            returned_objects=[],
            key=f"trip_map_{len(st.session_state.my_trip)}_{lang_code}",
        )


# ============================================================
# 22. SEOUL TRAVEL ESSENTIALS
# ============================================================

st.divider()
with st.expander(f"🧭 {txt['survival']}"):
    st.markdown(txt["survival_body"])


# ============================================================
# 23. SMALL FOOTNOTE
# ============================================================

st.caption(
    "Seoul for You · Recommendation tags are generated from the current CSV. "
    "Names and districts come from places_global.csv; descriptions and directions use cached translation unless pre-translated columns are present."
)
