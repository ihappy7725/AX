# raw_trade_data.csv 파일 활용
# HS 코드가 85로 시작 (반도체류) 
# + 국가명 미국 또는 베트남 
# + 수출금액은 0보다 큰 수 (실제 수출실적이 있는) 행만 
# 다중 조건으로 필터링 한 뒤 수출금액 상위 10건을 화면에 보여주고 report.csv 로 저장
# streamlit 사용 streamlit run 0908-1.py

import os
import pandas as pd
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="반도체 수출 실적 분석",
    page_icon="📈",
    layout="wide"
)

# 파일 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
<<<<<<< HEAD
csv_path = os.path.join(current_dir, "dummy", "raw_trade_data.csv")
=======
csv_path = os.path.join(current_dir, "..", "dummy", "raw_trade_data.csv")
>>>>>>> d93f7a8765559adf513b70af34ca2a6dde792d1a
report_path = os.path.join(current_dir, "report.csv")

st.title("📈 반도체(HS 85) 미국 및 베트남 수출 실적 분석")
st.markdown("""
이 대시보드는 `raw_trade_data.csv` 파일을 분석하여 아래 조건에 맞는 수출 실적을 필터링합니다.
* **HS 코드**: 85로 시작 (반도체류)
* **대상 국가**: 미국 또는 베트남
* **수출 금액**: 0보다 큰 실적 (실제 수출실적이 존재하는 행)
""")

# 데이터 로드
@st.cache_data
def load_data(path):
    if not os.path.exists(path):
        return None
    # hs_code를 문자열로 명시적으로 읽어 앞자리 '85' 필터링이 누락되지 않도록 함
    df = pd.read_csv(path, dtype={'hs_code': str})
    return df

df = load_data(csv_path)

if df is not None:
    # 1. HS 코드가 85로 시작하는 조건
    cond_hs = df['hs_code'].str.startswith('85', na=False)
    
    # 2. 국가명이 미국 또는 베트남인 조건
    cond_country = df['국가명'].isin(['미국', '베트남'])
    
    # 3. 수출금액이 0보다 큰 조건
    df['수출금액'] = pd.to_numeric(df['수출금액'], errors='coerce')
    cond_export = df['수출금액'] > 0
    
    # 다중 조건 필터링 적용
    filtered_df = df[cond_hs & cond_country & cond_export].copy()
    
    # 수출금액 상위 10건 정렬
    top_10 = filtered_df.sort_values(by='수출금액', ascending=False).head(10)
    
    # report.csv 파일로 자동 저장
    top_10.to_csv(report_path, index=False, encoding='utf-8-sig')
    
    # 레이아웃 구성: 주요 지표(Metrics) 표시
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("필터링된 총 수출 건수", f"{len(filtered_df):,} 건")
    with col2:
        st.metric("상위 10건 총 수출액", f"${top_10['수출금액'].sum():,} (USD)")
    with col3:
        st.metric("상위 10건 평균 수출액", f"${int(top_10['수출금액'].mean()):,} (USD)")
        
    st.markdown("---")
    
    # 화면 분할 (좌측: 데이터프레임, 우측: 시각화 차트)
    left_col, right_col = st.columns([1.2, 1])
    
    with left_col:
        st.subheader("🏆 수출금액 상위 10건 목록")
        st.dataframe(
            top_10.style.format({
                '수출금액': '{:,.0f}',
                '중량': '{:,.2f}'
            }),
            use_container_width=True
        )
        
        st.success("✅ 조건에 맞는 상위 10건의 데이터를 성공적으로 필터링하여 `report.csv` 파일로 저장했습니다.")
        
        csv_data = top_10.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 report.csv 직접 다운로드",
            data=csv_data,
            file_name="report.csv",
            mime="text/csv"
        )

    # 우측 컬럼: 차트 출력 부분 추가
    with right_col:
        st.subheader("📊 상위 10건 수출금액 비교")
        # HS코드와 국가명을 조합한 라벨 생성 후 차트 출력
        chart_df = top_10[['hs_code', '국가명', '수출금액']].copy()
        chart_df['구분'] = chart_df['국가명'] + " (" + chart_df['hs_code'] + ")"
        
        st.bar_chart(
            data=chart_df,
            x='구분',
            y='수출금액',
            color='국가명',
            use_container_width=True
        )
else:
    st.error("`raw_trade_data.csv` 파일을 찾을 수 없습니다. 파일 위치를 확인해주세요.")
