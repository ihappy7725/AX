import os 
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib import font_manager

st.title("📊 인코딩 자동 감지 + 한글 폰트 막대 그래프")
st.caption("여러 인코딩을 순서대로 시도해서 파일을 읽고, 객실 등급별 생존율을 그래프로 그립니다.")

# 파일 경로 세팅
# (여기서 쓸 타이타닉 데이터와 폰트가 여기 있다)
CSV_PATH = os.path.join(os.path.dirname(__file__), "titanic_cleaned.csv")
FONT_PATH = os.path.join(os.path.dirname(__file__), "JetBrainsMono-Medium.ttf")

# 함수 정의 
# 파일 주소(file_path)를 넘겨주면 작동하는 함수를 만들겠다. 
def read_csv_with_auto_encoding(file_path):
    """여러 인코딩을 순서대로 시도해서 csv 파일을 안전하게 읽어오는 함수"""

    encodings = ['utf-8', 'utf-8-sig', 'cp949', 'euc-kr', 'latin-1']

    # encodings에서 꺼내서 다 쓸 때까지 반복
    for encoding in encodings:

        # 어떻게 쓸 건지 -> 하나씩 사용해서 판다스로 파일 열어보기
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            st.toast(f"성공! '{encoding}' 방식으로 파일을 열었습니다. 🎉")

            # 함수의 최종 결과물 받기, 함수 종료.
            return df

        # 인코딩 오류가 난다면 (글자가 깨지는 오류: UnicodeDecodeError)
        except UnicodeDecodeError:

            # file_path가 seek(되감기) 버튼을 가진 파일 테이프라면
            if hasattr(file_path, 'seek'):

                #파일을 읽던 재생 커서를 맨 처음 위치(0초)로 되감아놔라.
                file_path.seek(0)

            # for문의 처음으로 돌아가서 계속 진행(다음 열쇠 꺼내기)    
            continue 

    # 요소를 모두 사용했는데도 에러가 뜨고 for문이 끝나버리면 실패 알리기
    st.error("준비된 모든 인코딩 방식으로도 파일을 읽을 수 없습니다. 😭")

    # 파일을 못 열었으니 빈 상자(None)를 건네주면서 종료함. 
    return None


st.subheader("1) 데이터 불러오기 (인코딩 자동 감지)")

# 함수 사용해서 위에 경로 설정한 파일을 연다. 
# 무사히 열린 데이터는 df 변수에 넣어둔다. 
df = read_csv_with_auto_encoding(CSV_PATH)

st.markdown('---')

# 컬럼 - 객실등급(Pclass)별 생존율 집계
# Survived 사망0 / 생존1 등급별 평균을 내면 그대로가 등급의 생존 비율이 된다. 
# 10명 남3 여7
# 1000 생존300 --> 300/1000 30%
 
# 1. 그룹별로 묶어주기: 객실등급을 기준으로 묶고, 각 그룹의 Survived(생존 여부) 컬럼만 뽑아내서, 평군식을 구하고 인덱스 순서대로 정렬해라. 
pclass_survival_rate = df.groupby("Pclass")["Survived"].mean().sort_index()

# 2. 데이터 다듬기
formatted_rate = (pclass_survival_rate * 100).round(1).rename("생존율(%)")

# 3. 다듬어진 완벽한 요리를 화면에 전시하기 (그릇에 담기)
st.subheader("2) 객실 등급별 생존율")
st.dataframe(formatted_rate)

st.markdown('---')

st.subheader("3) 객실 등급별 생존율 막대그래프")

# 글꼴 지정하기
try:
    # matplotlib font_manager에 폰트를 등록하고, 전역 폰트로 설정
    font_prop = font_manager.FontProperties(fname=FONT_PATH)
    font_manager.fontManager.addfont(FONT_PATH)
    plt.rcParams["font.family"] = font_prop.get_name()
    st.write("JetBrainsMono-Medium 폰트를 적용했습니다.")

# 폰트 파일이 없으면 FileNotFoundError 발생
except FileNotFoundError:
    st.warning("JetBrainsMono-Medium 폰트 파일을 찾을 수 없습니다.")

# fig = 바깥 영역, ax = 도화지 영역
# figsize=(8,5) : 가로 8, 세로 5 크기의 그림을 그릴 것
fig, ax = plt.subplots(figsize=(8,5))

# plot(kind="bar") : 원형 막대 그래프 (bar)로 그릴 것임
(pclass_survival_rate * 100).plot(kind="bar", color="blue", ax=ax)
ax.set_title("Survival Rate by Class")
ax.set_xlabel("Passenger Class")
ax.set_ylabel("Survival Rate(%)")

# 그림을 streamlit으로 뿌려주는 명령어
st.pyplot(fig)

# 파일 내보내기
output_png = output_path = os.path.join(os.path.dirname(__file__), "chart.png")
fig.savefig(output_png)
st.toast("차트 파일 저장 성공🎉")