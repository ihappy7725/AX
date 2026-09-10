"""
타이타닉 데이터 필터링, 결측치 정리
age(나이)가 35 이상인 승객 필터링
sex(설별)별로 필터링
titanic_cleaned.csv로 저장 
실행방법 : streamlit run 0907-3.py
"""

import pandas as pd 
import streamlit as st

st.title("🚢 타이타닉 데이터 필터링 & 결측치 정리")
st.caption("나이, 성별 조건으로 필터링 해보고, 결측치를 제거해 새 csv로 저장합니다.")

CSV_PATH = "Titanic.csv"

# 내가 알려준 주소(CSV_PATH)로 가서 타이타닉 파일(Titanic.csv)을 가져와라
try: 
    df = pd.read_csv(CSV_PATH)   

# 파일을 못찾으면(FileNotFoundError) 에러상황에서 내보낼 문구 설정     
except FileNotFoundError:
    st.error("❌ 파일을 찾을 수 없습니다.")

# try한 일이 에러 없이 성공했을 때, 그다음 실행할 일들 명령
else: 
    st.metric("원본 데이터 행 개수", f"{len(df)}행")

    st.markdown('---')

    # Age 35세 이상 필터링 
    st.subheader("1) 나이 35세 이상 승객")

    # 조건식에 만족하는 자료를 True로 보내서 over_35라는 변수에 넣음 
    over_35 = df[df["Age"]>=35]
    st.write(f"나이 35세 이상 승객수 : **{len(over_35)}명**")
    st.dataframe(over_35[["Name", "Sex", "Age"]].head(10))

    st.markdown('---')

    # 성별 여자 남자 필터링 (2컬럼 사용)
    st.subheader("2) 필터링 결과")
    female_df = df[df["Sex"] == "female"]
    male_df = df[df["Sex"] == "male"]

    col1, col2 = st.columns(2)
    with col1: 
        st.metric("여성 승객 수", f"{len(female_df)}명")
    with col2:
        st.metric("남성 승객 수", f"{len(male_df)}명")

    st.markdown('---')

    # 두 조건을 동시에 만족하는 행(35세 이상 여성)
    st.subheader("3) 35세 이상 & 여성 승객")
    over_35_female = df[(df["Age"]>=35) & (df["Sex"]=="female")]           
    st.write(f"35세 이상 & 여성 승객 수 : **{len(over_35_female)}명**")

    st.markdown('---')

    # 결측치(NaN) 확인 및 dropna 처리
    st.subheader("4) 결측치 처리")
    missing_name_count = df["Name"].isna().sum()
    st.write(f"- Name 열의 결측치 개수 : **{missing_name_count}개**")
    missing_age_count = df["Age"].isna().sum()   #isna()는 결측치(빈 셀)이면 True를 반환한다. 그 데이터의 합을 내어 missing_age_count라는 변수에 넣어 준다. 
    st.write(f"- Age 열의 결측치 개수 : **{missing_age_count}개**")
    missing_sex_count = df["Sex"].isna().sum()
    st.write(f"- Sex 열의 결측치 개수 : **{missing_sex_count}개**")

    # Age 열이 결측치인 행만 골라서 제거한다.
    # subset[""] : 해당 열이 결측인 값만 제거해줘  
    df_clean = df.dropna(subset=["Age"])

    col1, col2 = st.columns(2)
    with col1: 
        st.metric("Age 결측치 제거 전", f"{len(df)}행")
    with col2: 
        st.metric("Age 결측치 제거 후", f"{len(df_clean)}행")

    # 정리된 데이터를 csv 파일로 저장
    output_path = "titanic_cleaned.csv"
    df_clean.to_csv(output_path, index=False)
    st.success("파일을 저장했습니다.")
    st.dataframe(df_clean.head(),use_container_width=True)