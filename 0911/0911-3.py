# 대화 기록을 기록하는 멀티턴 챗봇(스트리밍 응답)
# st.session_state에 대화 기록을 저장해서, 이전 대화 맥락을 기억하는 챗봇
# st.chat_message / st.chat_input 같은 Streamlit의 채팅 전용 위젯 사용
# stream=True 옵션으로 답변이 실시간으로 타이핑되듯 출력
# streamlit run 0911-3.py

import streamlit as st
from openai import OpenAI

# 페이지 기본 설정
st.set_page_config(page_title="멀티턴 스트리밍 챗봇", page_icon="🤖")
st.title("🤖 멀티턴 스트리밍 챗봇")
st.caption("대화 맥락을 기억하며, 실시간 타이핑 효과(Streaming)로 답변하는 챗봇입니다.")

# ------------- 사이드바 설정 -------------
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("OpenAI API Key", type="password", help="sk-로 시작하는 OpenAI API key를 입력하세요.")
    model = st.selectbox("모델 선택", ["gpt-4o-mini", "gpt-4o"], index=0)
    
    # 1. 시스템 프롬프트 직접 설정
    system_prompt = st.text_area(
        "시스템 프롬프트 (AI 역할 설정)",
        value="당신은 항상 '주인님'이라는 호칭으로 말을 시작하는 매우 공손하고 친절한 AI 비서입니다.",
        help="AI의 성격, 말투, 규칙을 자유롭게 지정하세요."
    )
    
    # 2. 대화 기록 초기화 버튼
    if st.button("대화 기록 초기화", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("[API 발급받기](https://platform.openai.com/home)")

# ------------- 세션 상태(대화 기록) 초기화 -------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 내역 화면에 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------- 채팅 입력 및 응답 처리 -------------
user_input = st.chat_input("메시지를 입력하세요...")

if user_input:
    if not api_key:
        st.error("먼저 사이드바에 OpenAI API Key를 입력하세요.")
    else:
        # 1. 사용자 입력을 세션 및 화면에 추가
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. OpenAI 호출 및 실시간 스트리밍 출력
        with st.chat_message("assistant"):
            try:
                client = OpenAI(api_key=api_key)

                # API에 전송할 메시지 조합 (시스템 프롬프트 + 이전 대화 기록)
                api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

                stream_response = client.chat.completions.create(
                    model=model,
                    messages=api_messages,
                    stream=True  # 실시간 토큰 스트리밍 활성화
                )

                # st.write_stream을 활용하여 타이핑 효과 자동 구현 및 텍스트 캡처
                full_response = st.write_stream(stream_response)

                # 3. 완성된 어시스턴트 답변을 세션에 저장
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")