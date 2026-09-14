# folium으로 지도에 마커를 표시하는 예제 코드 
# import folium  -->  pip install folium 
# 서울 시내 명소 4곳의 좌표(위도/경도)와 이름을 리스트로 받아 folium 지도를 만들고 
# 각 좌표에 이름표가 붙은 마커를 찍은 뒤, basic_map.html 파일로 저장하는 예제 코드입니다. 
# 저장된 basic_map.html 파일을 웹 브라우저로 열어서 확인 
# 실행(streamlit 아님) : python 0914-1.py

import folium

# 서울 시내 명소 4곳의 이름, 위도(lat), 경도(lon) 데이터 정의
places = [
    {"name": "서울시청", "lat": 37.5665, "lon": 126.9780},
    {"name": "경복궁", "lat": 37.5796, "lon": 126.9770},
    {"name": "남산서울타워", "lat": 37.5512, "lon": 126.9882},
    {"name": "강남역", "lat": 37.4979, "lon": 127.0276}
]

# 지도의 시작 중심 좌표 (서울시청 기준) 지정해서 folium 지도 객체 생성 
# 숫자가 클수록 더 가깝게 보여준다. 
seoul_center = [37.5665, 126.9780]

# 1. 기본 배경 없이 베이스 맵 생성 (최대 줌 레벨 19까지 허용)
map = folium.Map(
    location=seoul_center, 
    zoom_start=13,
    max_zoom=19,
    tiles=None
)

# 2. VWorld 고화질 공공 타일 레이어 추가 (워터마크 없음, 국내 상세 데이터 19레벨 지원)
folium.TileLayer(
    tiles="https://xdworld.vworld.kr/2d/Base/service/{z}/{x}/{y}.png",
    attr="&copy; 국토교통부 VWorld",
    name="VWorld Base Map",
    max_zoom=19,
    min_zoom=6
).add_to(map)

# 3. 리스트에 담긴 장소들을 하나씩 꺼내면서 지도 위에 마커 추가
for place in places:
    popup_text = f"<b>{place['name']}</b><br>위도: {place['lat']}<br>경도: {place['lon']}"
    folium.Marker(
        location=[place["lat"], place["lon"]],
        popup=folium.Popup(popup_text, max_width=250),
        tooltip=f"{place['name']} (클릭하여 좌표 보기)",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(map)

# 지도 객체를 html 파일로 저장
output_path = "basic_map.html"
map.save(output_path)

print(f"'{output_path}' 파일로 지도가 성공적으로 저장되었습니다.")