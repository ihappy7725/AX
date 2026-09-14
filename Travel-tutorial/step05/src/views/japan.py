from src.components.country_card import render_country_page

japan_destinations = [
    {
        "name": "도쿄 (Tokyo)",
        "img": "assets/japan_tokyo.jpg",
        "desc": "신주쿠, 시부야의 번화가와 아키하바라, 긴자 등 다채로운 매력이 모여 있는 메트로폴리스입니다."
    },
    {
        "name": "교토 (Kyoto)",
        "img": "assets/japan_kyoto.jpg",
        "desc": "기요미즈데라(청수사), 후시미 이나리 신사 등 일본 전통 사찰과 신사가 보존된 고도(古都)입니다."
    },
    {
        "name": "오사카 (Osaka)",
        "img": "assets/japan_osaka.jpg",
        "desc": "도톤보리 거리, 오사카성을 중심으로 정겨운 분위기와 타코야키 등 풍부한 식문화를 자랑합니다."
    }
]

render_country_page(
    flag="🇯🇵",
    country_name="일본 (Japan)",
    country_description="""
- **수도**: 도쿄 (Tokyo)
- **주요 특징**: 스시, 라멘 등 정갈한 미식 문화와 온천(료칸), 만화·게임 콘텐츠가 발달한 섬나라입니다.
""",
    country_url="https://www.japan.travel/ko/kr/",
    destinations=japan_destinations
)