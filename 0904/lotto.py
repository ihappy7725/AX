# 로또v1
# 로또v2vwerwerwerwer

import streamlit as st
import random
from datetime import datetime       

st.title('🎱로또 번호 자동 생성기')
st.caption('버튼을 누르면 1~45 사이의 중복 없는 번호 6개짜리 세트를 5개 만들어줍니다.')
#smvnkdjsfksd fjklsdflk
def lotto_one_set() -> list:                                 
    """1~45에서 중복없이 번호 6개 뽑아 정렬된 리스트로 반환"""    
    
    number = set() # 👈 [int] 없이 깔끔하게 빈 주머니 생성
    while len(number) < 6 :                   
        number.add(random.randint(1,45))      
    return sorted(number)

st.markdown('---')
lotto_btn = st.button('🍀5세트 번호 생성하기', key='lotto_btn')

# 💡 'if lotto_btn:' = "만약 로또 버튼이 눌렸다면 아래 일들을 해라!"
if lotto_btn:
    # 1. 시간 보여주기
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")         
    st.write(f'생성 시각: **{now_str}**')

    st.markdown("---") # 줄 한 번 예쁘게 그어주기

    # 2. 5세트 반복해서 뽑기
    for set_index in range(1, 6):      
        lotto_num = lotto_one_set()  # 번호 6개 뽑아서 리스트로 받기
        
        # 3. 뽑힌 번호들에 색깔 공 달아주기
        colored_balls = []
        for num in lotto_num:
            if num <= 10:
                ball = f"🟡 {num}" # 1~10 노랑
            elif num <= 20:
                ball = f"🔵 {num}" # 11~20 파랑
            elif num <= 30:
                ball = f"🔴 {num}" # 21~30 빨강
            elif num <= 40:
                ball = f"⚫ {num}" # 31~40 검정
            else:
                ball = f"🟢 {num}" # 41~45 초록
            
            colored_balls.append(ball) # 꾸며진 공을 새 바구니에 담기
            
        # 4. 공들을 보기 좋게 띄어쓰기로 연결해서 화면에 출력!
        final_text = "  ".join(colored_balls)
        st.subheader(f"{set_index}세트: {final_text}")