from src.components.country_card import render_country_page

home_destinations = [
    {
        "name": "서울 (Seoul)",
        "img": "assets/home_seoul.jpg",
        "desc": "경복궁, 북촌 한옥마을의 전통미와 K-컬처 및 쇼핑을 즐길 수 있는 트렌디한 수도입니다."
    },
    {
        "name": "부산 (Busan)",
        "img": "assets/home_busan.jpg",
        "desc": "해운대, 광안리 해변과 풍성한 해산물 미식을 즐길 수 있는 제2의 해양 도시입니다."
    },
    {
        "name": "제주 (Jeju)",
        "img": "assets/home_jeju.jpg",
        "desc": "성산일출봉, 한라산 등 유네스코 세계자연유산으로 지정된 천혜의 휴양 화산섬입니다."
    }
]

render_country_page(
    flag="🇰🇷",
    country_name="대한민국 (Republic of Korea)",
    country_description="""
- **수도**: 서울 (Seoul)
- **주요 특징**: 반도체·IT 첨단 기술력과 K-팝, K-콘텐츠 등 글로벌 문화 트렌드를 선도하는 국가입니다.
""",
    country_url="https://korean.visitkorea.or.kr",
    destinations=home_destinations
)