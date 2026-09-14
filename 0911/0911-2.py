# OpenAI + streamlit 앱
# 질문 하나를 입력하면, OpenAI chat에서 Completions API 한번 호출
# 답변을 받아오는 가장 단순한 방법
# 대화 기록을 기억하지 않는 단발성 질문-답변
# streamlit run 0911-2.py

import streamlit as st
from openai import OpenAI

# 페이지 기본 설정
st.set_page_config(page_title="나의 첫번째 챗봇", page_icon="🤖")
st.title("예제1️⃣: 나의 첫번째 챗봇")
st.caption("질문 하나 입력하면 OpenAI chat completions API 한번 호출, 답변을 받아오는 가장 단순한 방법")

# ------------- 사이드바 API 모델 -------------
with st.sidebar:
    st.header("설정")
    api_key = st.text_input("OpenAI API Key", type="password", help="sk-로 시작하는 OpenAI API key를 입력하세요.")
    model = st.selectbox("모델 선택", ["gpt-4o-mini", "gpt-4o"], index=0)
    st.markdown("[API 발급받기](https://platform.openai.com/home)")

# ------------- 메인 화면 --------------
question = st.text_input("질문을 입력하세요", placeholder="예) 오늘 날씨가 어떤가요?")

if st.button("질문하기", type="primary"):
    if not api_key:
        st.error("OpenAI API Key를 입력하세요.")
    elif not question:
        st.error("질문을 입력하세요.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            
            # 답변 생성 대기 스피너
            with st.spinner("답변을 생각하는 중..."):
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "당신은 항상 '주인님'이라는 호칭으로 말을 시작하는 매우 공손하고 친절한 AI 비서입니다."
                        },
                        {
                            "role": "user",
                            "content": question
                        }
                    ]
                )

            # 1. 답변 출력
            answer = response.choices[0].message.content
            st.success("답변이 완료되었습니다!")
            st.markdown(answer)

            # 2. 토큰 사용량 정보 표시
            usage = response.usage
            st.divider()
            st.caption("📊 이번 질문에 소모된 토큰 수")
            col1, col2, col3 = st.columns(3)
            col1.metric("입력 토큰", f"{usage.prompt_tokens:,}")
            col2.metric("출력 토큰", f"{usage.completion_tokens:,}")
            col3.metric("총 토큰 수", f"{usage.total_tokens:,}")

        except Exception as e:
            # API 키 오류, 네트워크 오류 등 예외 처리
            st.error(f"오류가 발생했습니다: {e}")