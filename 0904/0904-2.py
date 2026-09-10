# 만들 것
# 설문조사 앱
# 버튼, 체크박스, 라디오단추, 셀렉트박스, 멀티셀렉트박스, 슬라이더
# 위젯

import streamlit as st

st.title('📝미니 선호도 조사')
st.caption("위젯을 조작하면 화면 아래 '실시간 응답 요약'이 바로 바뀝니다.")
st.markdown('---')

# 1) 텍스트 입력 위젯 : Key를 지정해서 다른 위젯과 이름이 겹치지 않게 한다.
name = st.text_input('1) 이름을 입력하세요.', value="홍길동", key='widget_name')   

# 2) 슬라이더 위젯 : 최소/최대/기본값 지정해 숫자로 선택하게 한다. 
age = st.slider('2) 나이를 입력하세요.', min_value=10, max_value=80, value=25, key='widget_age')

# 3) 라디오 버튼 : 여러 선택지 중에서 하나만 고를 때 사용한다. 
job = st.radio(
    "3) 직군을 선택하세요.",
    options=['학생','직장인','취업준비생','기타'],
    key='widget_job',
    index=1    #기본값 설정. 여기서는 1번으로 설정했기 때문에 리스트 순서값=1인 '직장인'이 기본으로 들어감.
)

# 4) 셀렉트 박스(드롭다운) : 라디오와 비슷하지만, 목록이 길 때 공간을 절약할 수 있다. 
country = st.selectbox(
    "4) 가장 관심있는 무역 상대국은?",
    options=['중국','일본','대만','베트남','미국','멕시코','브라질','영국','프랑스','독일','호주'],
    key='widget_country'
)

# 5) 멀티 셀렉트 박스(드롭다운) 
interest = st.multiselect(
    '5) 관심 있는 데이터 분야를 모두 고르세요.',
    options=['무역통계','환율','주가','날짜','인구통계'],
    key='widget_interest', 
    default=['무역통계']    #리스트 내에서 기본값으로 가져오고 싶은 것 써놓기 
)

# 6) 체크 박스: 참/거짓 값 하나를 받을 때
agree = st.checkbox('6) 강의 내용에 만족하시나요?', key='widget_agree')

# 7) 슬라이더
score = st.slider('7) 이 강의 만족도 점수', min_value=1, max_value=5, value=4, key='widget_score')

# 8) 텍스트 영역(여러 줄) : 여러 줄의 입력이 필요할 때 (의견 자유 입력 등)
feedback = st.text_area('8) 자유롭게 의견을 남겨주세요.', key='widget_feedback')

# 9) 버튼 : 클릭 여부 (true / false) 를 반환한다. 클릭 했을 때만 아래 코드가 실행된다. 
sumitted = st.button('✅제출하기', key='widget_submit_btn')


st.markdown('---')
st.subheader=('📊실시간 응답 요약')

#위젯 값들이 버튼을 누르지 않아도 조작하는 즉시 갱신된다. 
# if 조건식:
#     조건식 참일때 처리문
# else:
#     거짓일때 처리문

if sumitted:
    st.write(f"- 이름: **{name}** / 나이: **{age}**")
    st.write(f"- 직군: **{job}** / 관심 국가: **{country}**")
    st.write(f"- 관심 분야: **{', '.join(interest) if interest else '선택없음'}**")              #리스트 내 문자를 일반 문자열로 가져오고, 단어들을 쉼표(, )로 연결한다. 
    st.write(f"- 강의 만족 여부: **{'만족' if agree else '미체크'}** / 만족도 점수: **{score}**")   #f-string은 두번째 큰따옴표가 나오는 순간 그 문장이 끝났다고 생각함. 
    st.write(f"- 자유 의견: **{feedback if feedback else '미응답'}**")
else: 
    st.write('위의 항목을 입력한 뒤 제출하기 버튼을 눌러주세요.')

