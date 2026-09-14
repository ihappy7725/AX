import streamlit as st

st.set_page_config(page_title="세계 여행 포털", page_icon="🌏", layout="centered")

# 사이드바 메뉴 구성
menu = st.sidebar.radio("메뉴", ["홈", "미국", "중국", "일본", "베트남"])

# 1. 홈 (대한민국)
if menu == "홈":
    st.title("🇰🇷 대한민국 (Republic of Korea)")
    st.markdown("""
    * **수도 및 기본 정보**: 수도는 서울이며, 동아시아 한반도 남부에 위치해 있습니다.
    * **산업 및 문화**: 첨단 IT, 반도체 제조 강국이자 K-컬처(K-Pop, K-Drama, K-Food)로 세계적인 문화 영향력을 지닙니다.
    * **추천 여행 포인트**: 경복궁과 북촌 한옥마을의 전통미, 남산타워와 해운대의 현대적인 도시 매력을 함께 즐길 수 있습니다.
    """)
    st.link_button("🌐 대한민국 공식 관광 사이트 (Visit Korea)", "https://korean.visitkorea.or.kr")

# 2. 미국
elif menu == "미국":
    st.title("🇺🇸 미국 (United States of America)")
    st.markdown("""
    * **수도 및 기본 정보**: 수도는 워싱턴 D.C.이며, 50개 주와 광대한 영토를 가진 연방 공화국입니다.
    * **경제 및 문화**: 세계 최대 경제 규모를 자랑하며, 할리우드와 브로드웨이 등 글로벌 엔터테인먼트의 중심지입니다.
    * **추천 여행 포인트**: 뉴욕 타임스퀘어, 서부의 그랜드 캐니언 국립공원, 옐로스톤 등 압도적인 대자연과 도시 문화를 자랑합니다.
    """)
    st.link_button("🌐 미국 공식 관광청 (Brand USA / GoUSA)", "https://www.gousa.or.kr")

# 3. 중국
elif menu == "중국":
    st.title("🇨🇳 중국 (People's Republic of China)")
    st.markdown("""
    * **수도 및 기본 정보**: 수도는 베이징이며, 광활한 대륙 영토와 56개 다민족으로 구성된 국가입니다.
    * **역사 및 발전**: 5,000년의 깊은 역사 유적과 함께 상하이, 선전 등 초현대적 메가시티가 공존합니다.
    * **추천 여행 포인트**: 유네스코 세계유산인 만리장성과 자금성, 병마용, 자연 비경인 장자제(장가계)가 대표적입니다.
    """)
    st.link_button("🌐 중국 문화여유부 공식 사이트", "https://www.mct.gov.cn")

# 4. 일본
elif menu == "일본":
    st.title("🇯🇵 일본 (Japan)")
    st.markdown("""
    * **수도 및 기본 정보**: 수도는 도쿄이며, 홋카이도부터 오키나와까지 남북으로 길게 뻗은 열도 국가입니다.
    * **문화 및 특색**: 정갈한 미식 문화(스시, 라멘), 애니메이션·게임 산업, 고유의 온천(료칸) 문화가 발달했습니다.
    * **추천 여행 포인트**: 도쿄의 트렌디한 도심, 교토의 고즈넉한 신사와 사찰, 삿포로의 겨울 설경이 여행객에게 인기입니다.
    """)
    st.link_button("🌐 일본정부관광국 (JNTO)", "https://www.japan.travel/ko/kr/")

# 5. 베트남
elif menu == "베트남":
    st.title("🇻🇳 베트남 (Socialist Republic of Vietnam)")
    st.markdown("""
    * **수도 및 기본 정보**: 수도는 하노이이며, 경제 중심지는 남부의 호찌민 시입니다.
    * **매력 및 생활**: 쌀국수와 반미, 풍미 깊은 연유 커피로 대표되는 미식과 친절하고 활기찬 길거리 문화가 유명합니다.
    * **추천 여행 포인트**: 에메랄드빛 카르스트 지형의 하롱베이, 유서 깊은 항구 도시 호이안, 다낭과 푸꾸옥의 아름다운 해변 휴양지가 대표적입니다.
    """)
    st.link_button("🌐 베트남 국립관광국 공식 사이트 (Vietnam Tourism)", "https://vietnam.travel")