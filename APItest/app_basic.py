# 날씨 API 실습

# OpenWheatherMap 현재 날씨 API 로 특정 도시의 날씨를 가져와 출력한다. 
# 사전 준비: OpenWheaterMap 회원 가입 후 API 발급
# pip install requests python-dotenv
# .env 파일을 생성하고 이곳에 OPENWHEATHER_API_KEY=발급받은_API_KEY
# .env.example OPENWHEATHER_API_KEY=your_key
# .env.example 받아서 .env로 이름 바꾸고 본인의 API를 채운다. 


import os 
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv(dotenv_path="../.env") 

WEATHER_API_KEY = os.getenv("OPENWHEATHER_API_KEY")
EXCHANGE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")

def get_weather(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric&lang=kr"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_exchange_rate(base_currency):
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/{base_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_fluctuation(ticker):
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="2d")
        if len(hist) >= 2:
            prev_close = hist['Close'].iloc[0]
            current = hist['Close'].iloc[1]
            diff = current - prev_close
            return current, diff
    except:
        pass
    return None, None

st.set_page_config(page_title="종합 정보 앱", layout="wide")

# --- 사이드바: 도시 선택 영역 (key 추가로 중복 ID 오류 방지) ---
st.sidebar.header("🌍 지역 선택 설정")
city_options = {
    "서울 (대한민국)": "Seoul",
    "도쿄 (일본)": "Tokyo",
    "베이징 (중국)": "Beijing",
    "샤먼 (중국)": "Xiamen",
    "뉴욕 (미국)": "New York",
    "런던 (영국)": "London",
    "파리 (프랑스)": "Paris",
    "싱가포르 (싱가포르)": "Singapore"
}

selected_city_label = st.sidebar.selectbox("주요 도시 선택", list(city_options.keys()), key="sidebar_city_select")
city = city_options[selected_city_label]

custom_city = st.sidebar.text_input("또는 직접 도시 영문명 입력", "", key="custom_city_input")
if custom_city:
    city = custom_city

st.title("🌍 실시간 날씨 및 환율 조회 서비스")

# --- 1. 날씨 섹션 ---
st.header(f"🌤️ 현재 날씨 및 위치 ({selected_city_label})")

if not WEATHER_API_KEY:
    st.error("날씨 API 키를 찾을 수 없습니다.")
else:
    with st.spinner("날씨 및 지도 정보를 가져오는 중..."):
        weather_data = get_weather(city)
        if weather_data:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(label="현재 온도", value=f"{weather_data['main']['temp']}°C")
            with col2:
                st.metric(label="체감 온도", value=f"{weather_data['main']['feels_like']}°C")
            with col3:
                st.metric(label="습도", value=f"{weather_data['main']['humidity']}%")
            with col4:
                st.metric(label="날씨", value=weather_data['weather'][0]['description'])
            
            lat = weather_data['coord']['lat']
            lon = weather_data['coord']['lon']
            city_name = weather_data['name']
            
            # Folium 지도 생성
            m = folium.Map(location=[lat, lon], zoom_start=11)
            
            folium.Marker(
                [lat, lon],
                popup=city_name,
                tooltip=f"📍 {selected_city_label}",
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)
            
            st_folium(m, width=None, height=450)
            
        else:
            st.error("날씨 정보를 가져오는 데 실패했습니다. 도시 이름을 확인해주세요.")

st.divider()

# --- 2. 환율 섹션 ---
st.header("💱 실시간 환율 및 주요 통화 등락")
col_base, col_target = st.columns(2)
with col_base:
    base_currency = st.selectbox("기준 통화", ["USD", "EUR", "JPY", "KRW", "CNY"], index=0, key="exchange_base")
with col_target:
    target_currency = st.selectbox("대상 통화", ["KRW", "USD", "EUR", "JPY", "CNY"], index=0, key="exchange_target")

if st.button("환율 확인", key="btn_check_exchange"):
    if not EXCHANGE_API_KEY:
        st.error("환율 API 키를 찾을 수 없습니다.")
    else:
        with st.spinner("환율 및 등락 정보를 가져오는 중..."):
            exchange_data = get_exchange_rate(base_currency)
            if exchange_data and target_currency in exchange_data['conversion_rates']:
                rate = exchange_data['conversion_rates'][target_currency]
                st.success(f"현재 1 **{base_currency}** = **{rate:,.2f} {target_currency}** 입니다.")
                
                st.markdown("### 주요 통화 대비 원화(KRW) 등락")
                tickers = {
                    "미국 달러 (USD)": "KRW=X", 
                    "유로 (EUR)": "EURKRW=X", 
                    "일본 엔 (JPY)": "JPYKRW=X", 
                    "중국 위안 (CNY)": "CNYKRW=X"
                }
                
                metric_cols = st.columns(4)
                for i, (label, ticker) in enumerate(tickers.items()):
                    current_val, diff_val = get_fluctuation(ticker)
                    with metric_cols[i]:
                        if current_val is not None and diff_val is not None:
                            st.metric(
                                label=label, 
                                value=f"{current_val:,.2f} 원", 
                                delta=f"{diff_val:,.2f} 원"
                            )
                        else:
                            st.metric(label=label, value="데이터 없음")
            else:
                st.error("환율 정보를 가져오는 데 실패했습니다.")

st.divider()

# --- 3. 실시간 환율 계산기 섹션 ---
st.header("🧮 실시간 환율 계산기")
st.write("원하는 금액을 입력하여 다른 통화로 변환해 보세요.")

col_calc1, col_calc2 = st.columns(2)
with col_calc1:
    calc_base = st.selectbox("변환할 기준 통화", ["USD", "KRW", "EUR", "JPY", "CNY"], index=0, key="calc_base_select")
with col_calc2:
    calc_target = st.selectbox("변환될 대상 통화", ["KRW", "USD", "EUR", "JPY", "CNY"], index=0, key="calc_target_select")

amount = st.number_input("변환할 금액 입력", min_value=0.0, value=100.0, step=10.0, key="calc_amount_input")

if st.button("계산하기", key="btn_calc_execute"):
    if not EXCHANGE_API_KEY:
        st.error("환율 API 키를 찾을 수 없습니다.")
    else:
        calc_data = get_exchange_rate(calc_base)
        if calc_data and calc_target in calc_data['conversion_rates']:
            conversion_rate = calc_data['conversion_rates'][calc_target]
            converted_amount = amount * conversion_rate
            st.info(f"💡 **{amount:,.2f} {calc_base}** = **{converted_amount:,.2f} {calc_target}** (적용 환율: 1 {calc_base} = {conversion_rate:,.4f} {calc_target})")
        else:
            st.error("환율 계산 중 오류가 발생했습니다.")