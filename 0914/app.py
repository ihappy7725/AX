import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
import os
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Seoul Tourist Map", layout="wide")

# 1. 국가별 언어 및 통화 매핑
LANG_CONFIG = {
    "한국어": {"code": "ko", "currency": "USD"},
    "English": {"code": "en", "currency": "USD"},
    "中文 (중국어)": {"code": "zh-CN", "currency": "CNY"},
    "日本語 (일본어)": {"code": "ja", "currency": "JPY"},
    "Español (스페인어)": {"code": "es", "currency": "EUR"},
    "العربية (아랍어)": {"code": "ar", "currency": "AED"},
    "Русский (러시아어)": {"code": "ru", "currency": "RUB"}
}

selected_lang_key = st.selectbox("🌐 Language / 언어 설정", list(LANG_CONFIG.keys()))
lang_code = LANG_CONFIG[selected_lang_key]["code"]
currency_code = LANG_CONFIG[selected_lang_key]["currency"]

# UI 텍스트용 실시간 단일 번역 (몇 단어 안 되므로 속도에 지장 없음)
@st.cache_data(show_spinner=False)
def trans_ui(text, target_lang):
    if target_lang == "ko" or not text: return text
    try: return GoogleTranslator(source='ko', target=target_lang).translate(text)
    except: return text

# 2. 실시간 날씨 및 환율 (캐싱 적용)
@st.cache_data(ttl=3600)
def get_weather_and_exchange(target_currency):
    weather_desc, temp, krw_rate = "Unknown", "-", "-"
    try:
        w_res = requests.get("https://wttr.in/Seoul?format=j1", timeout=3).json()
        temp = w_res['current_condition'][0]['temp_C']
        base_desc = w_res['current_condition'][0]['weatherDesc'][0]['value']
        weather_desc = trans_ui(base_desc, lang_code)
    except: pass
    
    try:
        e_res = requests.get(f"https://open.er-api.com/v6/latest/{target_currency}", timeout=3).json()
        krw_rate = f"{e_res['rates']['KRW']:,.2f}"
    except: pass
    return f"{temp}°C ({weather_desc})", krw_rate

# 3. 글로벌 CSV 데이터 로드
@st.cache_data
def load_data():
    if not os.path.exists("places_global.csv"):
        st.error("places_global.csv 파일이 없습니다. 1단계 스크립트를 실행해 주세요.")
        st.stop()
    return pd.read_csv("places_global.csv", encoding="utf-8-sig")

df = load_data()

# 선택된 언어에 맞춰 사용할 열(Column) 동적 할당
col_gu = "gu" if lang_code == "ko" else f"gu_{lang_code}"
col_name = "name" if lang_code == "ko" else f"name_{lang_code}"

# 4. 사이드바 UI
txt_all = trans_ui("전체", lang_code)
st.sidebar.title(trans_ui("📍 명소 찾기", lang_code))

# 사이드바 1: 구 선택
display_gus = [txt_all] + sorted(df[col_gu].unique().tolist())
selected_gu = st.sidebar.selectbox(trans_ui("방문할 지역을 선택하세요", lang_code), display_gus)

if selected_gu == txt_all:
    filtered_df = df
else:
    filtered_df = df[df[col_gu] == selected_gu]

# 사이드바 2: 명소 선택
display_places = [txt_all] + filtered_df[col_name].tolist()
selected_place = st.sidebar.selectbox(trans_ui("가볼 명소를 선택하세요", lang_code), display_places)

if selected_place == txt_all:
    final_df = filtered_df
else:
    final_df = filtered_df[filtered_df[col_name] == selected_place]

# 5. 메인 화면 대시보드
st.title(trans_ui("🗺️ 서울 관광명소 맵", lang_code))
weather_info, krw_rate = get_weather_and_exchange(currency_code)

col1, col2, col3 = st.columns(3)
col1.metric(label=trans_ui("🌤️ 현재 서울 날씨", lang_code), value=weather_info)
col2.metric(label=trans_ui(f"💵 환율 (1 {currency_code} -> KRW)", lang_code), value=f"₩ {krw_rate}")
col3.metric(label=trans_ui("🚩 표시된 명소 수", lang_code), value=f"{len(final_df)}")
st.divider()

# 6. 지도 렌더링
seoul_center = [37.5665, 126.9780]
if len(final_df) == 1:
    lat, lon = final_df.iloc[0]["lat"], final_df.iloc[0]["lon"]
    map_center = [lat, lon] if pd.notna(lat) else seoul_center
    zoom_level = 15
else:
    map_center = seoul_center
    zoom_level = 11 if selected_gu == txt_all else 13

m = folium.Map(location=map_center, zoom_start=zoom_level, max_zoom=19, tiles=None)

folium.TileLayer(
    tiles="https://xdworld.vworld.kr/2d/Base/service/{z}/{x}/{y}.png",
    attr="&copy; 국토교통부 VWorld",
    max_zoom=19, min_zoom=6
).add_to(m)

for index, row in final_df.iterrows():
    if pd.notna(row["lat"]) and pd.notna(row["lon"]):
        popup_html = f"<b>{row[col_name]}</b><br>{row[col_gu]}"
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=row[col_name],
            icon=folium.Icon(color="red" if len(final_df) == 1 else "blue", icon="info-sign")
        ).add_to(m)

st_folium(m, width="100%", height=500)
st.divider()

# 7. 하단 상세 정보 (단일 명소 선택 시에만 설명과 경로를 실시간 번역)
st.subheader(trans_ui("📖 명소 상세 정보", lang_code))

if selected_place == txt_all:
    st.info(trans_ui("👉 상세 정보를 보려면 왼쪽 사이드바에서 특정 명소를 선택해 주세요.", lang_code))
else:
    # 1개만 선택되었으므로 번역 API를 호출해도 무리가 없음
    row = final_df.iloc[0]
    with st.expander(f"📌 {row[col_name]}", expanded=True):
        info_col1, info_col2 = st.columns([1, 2])
        with info_col1:
            st.image(row["img"], use_container_width=True)
        with info_col2:
            t_desc = trans_ui(row['desc'], lang_code)
            t_dir = trans_ui(row['directions'], lang_code)
            st.markdown(f"**{trans_ui('📝 설명:', lang_code)}** {t_desc}")
            st.markdown(f"**{trans_ui('🚶 가는 방법:', lang_code)}** {t_dir}")