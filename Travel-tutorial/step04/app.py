

import streamlit as st

st.set_page_config(page_title="세계 여행 포털", page_icon="🌏", layout="centered")

# 소문자 st.page -> 대문자 st.Page 로 수정
home_page = st.Page("view/home.py", title='홈', icon='🏠', default=True)
usa_page = st.Page("view/USA.py", title='미국', icon='🗽')  # 파일명이 USA.py라면 대소문자 일치 필요
china_page = st.Page("view/china.py", title='중국', icon='🀄')
japan_page = st.Page('view/japan.py', title='일본', icon='🎌')
vietnam_page = st.Page('view/vietnam.py', title='베트남', icon='⛰️')

# 네비게이션 등록 및 실행
pg = st.navigation([home_page, usa_page, china_page, japan_page, vietnam_page])
pg.run()