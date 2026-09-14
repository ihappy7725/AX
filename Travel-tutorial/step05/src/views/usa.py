from src.components.country_card import render_country_page

usa_destinations = [
    {
        "name": "뉴욕 (New York)",
        "img": "assets/usa_newyork.jpg",
        "desc": "타임스퀘어, 센트럴 파크, 브로드웨이 뮤지컬이 자리 잡은 글로벌 경제와 예술의 중심지입니다."
    },
    {
        "name": "로스앤젤레스 (Los Angeles)",
        "img": "assets/usa_la.jpg",
        "desc": "할리우드, 산타모니카 해변, 유니버설 스튜디오 등 온화한 기후와 엔터테인먼트의 도시입니다."
    },
    {
        "name": "라스베이거스 & 그랜드캐니언",
        "img": "assets/usa_vegas.jpg",
        "desc": "화려한 호텔 카지노 쇼와 대자연의 경이로움을 동시에 경험할 수 있는 네바다/애리조나 권역입니다."
    }
]

render_country_page(
    flag="🇺🇸",
    country_name="미국 (United States)",
    country_description="""
- **수도**: 워싱턴 D.C. (Washington, D.C.)
- **주요 특징**: 50개 주의 방대한 영토와 세계 최대 경제력, 다양한 다민족 문화가 결합된 국가입니다.
""",
    country_url="https://www.gousa.or.kr",
    destinations=usa_destinations
)