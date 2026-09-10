# random 모듈을 이용해서 1~45중 중복 없는 번호 6개를 뽑고 
# 자료 구조 set(중복x), 버튼을 누르면 5세트를 한번에 생성 
# datetime 으로 생성 시간도 함께 보여준다



import streamlit as st
import random
from datetime import datetime       #해당 함수(datetime)만 호출

# sefsdfsdfsdfsdf?

st.title('🎱로또 번호 자동 생성기')
st.caption('버튼을 누르면 1~45 사이의 중복 없는 번호 6개짜리 세트를 5개 만들어줍니다.')

def lotto_one_set() -> list:                                 #함수를 정의하고 리스트에 담는다. 
    """1~45에서 중복없이 번호 6개 뽑아 정렬된 리스트로 반환"""     #함수 부연설명

    number = set[int]()
    while len(number) < 6 :                   #number의 개수를 세서 6보다 작을 동안 반복
        number.add(random.randint(1,45))      #1이상 ~ 45이하 정수 하나 뽑아서 number 변수에 만들어두었던 set 자리에 넣어라  
    return sorted(number)

# while 조건식:
#     참일때 처리문
# return 


st.markdown('---')
lotto_btn = st.button('🍀5세트 번호 생성하기', key='lotto_btn')
now_str = datetime.now().strftime("%Y-%m-%d %H:%M")         #현재 시간 불러오고 읽을 수 있는 형태로 바꿔줌
st.wrtie(f'생성 시각: **{now_str}**')


for set_index in range(1,6):      #1이상 6미만 범위에서 반복
    lotto_num = lotto_one_set()   #함수 호출에서 호출된 결과를 lotto_num에 담는다 
    st.write(f"{set_index}세트: {lotto_num}")