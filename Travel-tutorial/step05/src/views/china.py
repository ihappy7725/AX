from src.components.country_card import render_country_page

china_destinations = [
    {
        "name": "베이징 (Beijing)",
        "img": "assets/china_beijing.jpg",
        "desc": "만리장성, 자금성(고궁박물원), 이화원 등 웅장한 역사 문화유산이 집중된 수도입니다."
    },
    {
        "name": "상하이 (Shanghai)",
        "img": "assets/china_shanghai.jpg",
        "desc": "와이탄의 근대 건축물과 동방명주 타워가 어우러진 현대 경제·무역 중심지입니다."
    },
    {
        "name": "장자제 (Zhangjiajie)",
        "img": "assets/china_zhangjiajie.jpg",
        "desc": "영화 '아바타'의 모티브가 된 기암괴석 봉우리와 원가계 절경을 자랑하는 자연 명소입니다."
    }
]

render_country_page(
    flag="🇨🇳",
    country_name="중국 (China)",
    country_description="""
- **수도**: 베이징 (Beijing)
- **주요 특징**: 수천 년 역사의 고대 유적지와 초현대식 메가시티가 공존하는 거대한 영토의 국가입니다.
""",
    country_url="https://www.travelchina.gov.cn",
    destinations=china_destinations
)