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
import plotly.express as px
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
    """yfinance를 활용하여 전일 대비 환율 등락을 계산합니다."""
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
st.title("🌍 실시간 날씨 및 환율 조회 서비스")

# --- 1. 날씨 섹션 ---
st.header("🌤️ 현재 날씨 및 위치")
city = st.text_input("도시 이름 (예: Seoul, Tokyo, London, Xiamen)", "Seoul")

if st.button("날씨 확인"):
    if not WEATHER_API_KEY:
        st.error("날씨 API 키를 찾을 수 없습니다.")
    else:
        with st.spinner("날씨 및 지도 정보를 가져오는 중..."):
            weather_data = get_weather(city)
            if weather_data:
                # 1) 날씨 메트릭 출력
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(label="현재 온도", value=f"{weather_data['main']['temp']}°C")
                with col2:
                    st.metric(label="체감 온도", value=f"{weather_data['main']['feels_like']}°C")
                with col3:
                    st.metric(label="습도", value=f"{weather_data['main']['humidity']}%")
                with col4:
                    st.metric(label="날씨", value=weather_data['weather'][0]['description'])
                
                # 2) 3D 지구본 지도 출력
                lat = weather_data['coord']['lat']
                lon = weather_data['coord']['lon']
                
                df_loc = pd.DataFrame({'lat': [lat], 'lon': [lon], 'city': [weather_data['name']]})
                
                # orthographic 투영법을 사용하여 3D 지구본 형태로 렌더링
                fig = px.scatter_geo(
                    df_loc, lat='lat', lon='lon', hover_name='city', 
                    projection="orthographic"
                )
                
                # 지도 디자인 설정
                fig.update_geos(
                    showcountries=True, countrycolor="black",
                    showland=True, landcolor="#E5E5E5",
                    showocean=True, oceancolor="#C6E2FF",
                    showlakes=True, lakecolor="#C6E2FF",
                    resolution=50
                )
                fig.update_traces(marker=dict(size=12, color="red", symbol="circle"))
                fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("날씨 정보를 가져오는 데 실패했습니다.")

st.divider()

# --- 2. 환율 섹션 ---
st.header("💱 실시간 환율 및 주요 통화 등락")
col_base, col_target = st.columns(2)
with col_base:
    base_currency = st.selectbox("기준 통화", ["USD", "EUR", "JPY", "KRW", "CNY"], index=0)
with col_target:
    target_currency = st.selectbox("대상 통화", ["KRW", "USD", "EUR", "JPY", "CNY"], index=0)

if st.button("환율 확인"):
    if not EXCHANGE_API_KEY:
        st.error("환율 API 키를 찾을 수 없습니다.")
    else:
        with st.spinner("환율 및 등락 정보를 가져오는 중..."):
            exchange_data = get_exchange_rate(base_currency)
            if exchange_data and target_currency in exchange_data['conversion_rates']:
                rate = exchange_data['conversion_rates'][target_currency]
                st.success(f"현재 1 **{base_currency}** = **{rate:,.2f} {target_currency}** 입니다.")
                
                st.markdown("### 주요 통화 대비 원화(KRW) 등락")
                # 주요 통화의 yfinance 티커 심볼 (예: 달러-원 환율은 KRW=X)
                tickers = {"미국 달러 (USD)": "KRW=X", "유로 (EUR)": "EURKRW=X", "일본 엔 (JPY)": "JPYKRW=X", "중국 위안 (CNY)": "CNYKRW=X"}
                
                metric_cols = st.columns(4)
                for i, (label, ticker) in enumerate(tickers.items()):
                    current_val, diff_val = get_fluctuation(ticker)
                    
                    with metric_cols[i]:
                        if current_val is not None and diff_val is not None:
                            # st.metric의 delta 속성을 사용하면 화살표와 함께 등락이 자동으로 색상 표시됩니다.
                            st.metric(
                                label=label, 
                                value=f"{current_val:,.2f} 원", 
                                delta=f"{diff_val:,.2f} 원"
                            )
                        else:
                            st.metric(label=label, value="데이터 없음")
            else:
                st.error("환율 정보를 가져오는 데 실패했습니다.")