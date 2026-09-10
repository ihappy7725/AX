import streamlit as st
import pandas as pd
import os

# 경로가 중요하다. 
# 1. os : '운영체제(윈도우, 맥 등 내 컴퓨터)'를 뜻하는 가장 큰 마법 상자
# 2. path : os 상자 안에 들어있는 '폴더나 주소(경로) 찾기 전용' 서랍
# 3. join : path 서랍 안에서 꺼낸 '접착제' 도구. 흩어진 단어를 주소로 합쳐줘요.
# 4. dirname : path 서랍 안에서 꺼낸 '가위'. 파일명은 싹둑 자르고 폴더 위치만 남겨요.
# __file__ : 지금 실행하고 있는 이 파이썬 파일이 컴퓨터의 어디에 있는지 알려주는 현재 내 위치

CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'dummy', 'raw_trade_data.csv' )

# 환율샘플 데이터 
# 딕셔너리로 표 만들기 -->  {} 넣어서 Key : Value 
exchange_data = {
    '통화' : ['USD','EUR','JPY(100엔)','CNY'],
    '환율(KRW)' : [1390.5000, 1503.2000, 930.8000, 191.3000],
    '전일대비' : [5.2000, -3.1000, 1.0000, -0.4000],
}

df_exchange = pd.DataFrame(exchange_data)

st.title("💱오늘의 환율 대시보드")
st.caption('아래 데이터는 실제 환율이 아닌 실습용 샘플 데이터입니다.')

st.subheader('1) 환율 표 보기')
st.write('▶ st.dataframe (상호작용 가능한 표)')                     # 특수문자 쓰기: ㅁ+한자키
st.dataframe(df_exchange, use_container_width=True)               # use_container_width=True 하면 전체 표 고정 길이가 화면에 맞춰짐 (기본값이 True)
st.write('▶ st.table (정적인 표)')
st.table(df_exchange)
st.markdown("---")
#eojfseofpofop/
st.subheader('2) 주요 환율 카드(st.metric)')
col1, col2, col3 = st.columns(3)                                  # 화면을 3개로 나누어주고, 각각 이름을 col1, col2, col3으로 설정할게 

# st.metric(label='', value='', delta='')                         
with col1 : 
    st.metric(label='USD/KRW', value='1,4500.5', delta='+5.2')
with col2 : 
    st.metric(label='EUR/KRW', value='1,503.2', delta='-3.1')
with col3 : 
    st.metric(label='JPY(100엔)/KRW', value='930.8', delta='+1.0')

st.markdown("---")

st.subheader('3) 보너스: 무역 원본 데이터 미리보기')
st.write('공용 데이터 파일 raw_trade_data.csv를 읽어온 상위 5행입니다.')
df_trade_raw = pd.read_csv(CSV_PATH, encoding='utf-8')
st.dataframe(df_trade_raw.head(5), use_container_width=True)
