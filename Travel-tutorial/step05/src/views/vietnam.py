from src.components.country_card import render_country_page

vietnam_destinations = [
    {
        "name": "다낭 & 호이안 (Da Nang & Hoi An)",
        "img": "assets/vietnam_danang.jpg",
        "desc": "미케비치 해변 휴양과 유네스코 세계문화유산인 호이안 구시가지의 등불 야경을 즐길 수 있습니다."
    },
    {
        "name": "하노이 & 하롱베이 (Hanoi & Ha Long Bay)",
        "img": "assets/vietnam_hanoi.jpg",
        "desc": "천년 고도의 수도 하노이와 3,000여 개 섬이 바다에 떠 있는 비경 하롱베이를 탐방합니다."
    },
    {
        "name": "푸꾸옥 (Phu Quoc)",
        "img": "assets/vietnam_phuquoc.jpg",
        "desc": "에메랄드빛 해변과 고급 리조트, 빈원더스 테마파크가 있는 베트남 남부의 대표 휴양 섬입니다."
    }
]

render_country_page(
    flag="🇻🇳",
    country_name="베트남 (Vietnam)",
    country_description="""
- **수도**: 하노이 (Hanoi)
- **주요 특징**: 쌀국수(포)와 반미 등 친숙한 미식, 합리적인 물가와 따뜻한 기후의 해안 도시를 갖춘 국가입니다.
""",
    country_url="https://vietnam.travel",
    destinations=vietnam_destinations
)