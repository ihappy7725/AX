# 반복되는 화면 디자인을 붕어빵 틀(템플릿)처럼 찍어내기 위해 만드는 공통함수. 
# 화면을 그리는 규칙을 딱 한 번 만들어 두고, 각 나라 파일은 데이터(재료)만 전달한다. 


import streamlit as st


# flag, country_name, country_description, country_url 만 넘겨주면, 
def render_country_page(flag: str, country_name: str, country_description: str, country_url: str):

    # 알아서 st.title, st.write, st.link_button 으로 그려주겠다. 
    st.title(f"{flag} {country_name}")
    st.write(country_description) 
    st.link_button(
        label=f"{country_name} 공식 관광청 방문",
        url=country_url
    )