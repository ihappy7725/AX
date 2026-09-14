import streamlit as st

pg = st.set_page_config(page_title="세계 여행 포털", page_icon="🌏", layout="centered")

home_page=st.Page("view/home.py", title="홈", icon="🏠", default=True)
usa=st.Page("view/usa.py", title="미국", icon="🗽")
china=st.Page("view/china.py", title="중국", icon="🀄")
japan=st.Page("view/japan.py", title="일본", icon="🎌")
vietnam=st.Page("view/vietnam.py", title="베트남", icon="⛰️")


# 네비게이션
pg=st.navigation([home_page, usa, china, japan, vietnam])
pg.run()
