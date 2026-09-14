# src/components/country_card.py
# [부품/템플릿] 공통 레이아웃을 찍어내는 함수 

import streamlit as st
import os
from PIL import Image

def render_country_page(
    flag: str, 
    country_name: str, 
    country_description: str, 
    country_url: str, 
    destinations: list[dict] = None
):
    """
    destinations 예시:
    [
        {"name": "서울", "img": "assets/korea_seoul.jpg", "desc": "경복궁과 도심 야경"},
        {"name": "부산", "img": "assets/korea_busan.jpg", "desc": "해운대와 광안대교"},
        {"name": "제주", "img": "assets/korea_jeju.jpg", "desc": "성산일출봉과 한라산"}
    ]
    """
    st.title(f"{flag} {country_name}")
    st.markdown(country_description)
    st.divider()

    # 지역별 여행지 탭 생성
    if destinations:
        st.subheader("📍 주요 여행지 둘러보기")
        
        # 지역 이름으로 탭 목록 생성
        tab_names = [f"📌 {item['name']}" for item in destinations]
        tabs = st.tabs(tab_names)

        for i, dest in enumerate(destinations):
            with tabs[i]:
                img_path = dest.get("img")
                # 이미지 유효성 검사 및 렌더링
                if img_path and os.path.exists(img_path) and os.path.getsize(img_path) > 0:
                    st.image(img_path, caption=dest["name"], use_container_width=True)
                else:
                    st.info(f"📷 {dest['name']} 이미지를 준비 중입니다.")
                
                st.write(dest.get("desc", ""))

    st.write("")
    st.link_button(
        label=f"🌐 {country_name} 공식 관광청 방문",
        url=country_url,
        use_container_width=True
    )