# [메인 제어] 진입점 및 전체 페이지 라우팅

import streamlit as st

st.set_page_config(
    page_title="세계 여행 포털",
    page_icon="🌏",
    layout="centered"
)

# 페이지 라우팅 객체 정의 (st.Page 사용)
home_page = st.Page("src/views/home.py", title="홈 (대한민국)", icon="🏠", default=True)
china_page = st.Page("src/views/china.py", title="중국", icon="🇨🇳")
japan_page = st.Page("src/views/japan.py", title="일본", icon="🇯🇵")
usa_page = st.Page("src/views/usa.py", title="미국", icon="🇺🇸")
vietnam_page = st.Page("src/views/vietnam.py", title="베트남", icon="🇻🇳")

# 네비게이션 등록 및 실행
pg = st.navigation({
    "포털": [home_page],
    "아시아 여행지": [china_page, japan_page, vietnam_page],
    "아메리카 여행지": [usa_page]
})

pg.run()