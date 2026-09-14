# csv, txt, md 파일 등을 업로드 하고 그것을 분석하는 프로그램
# 1. 중복 출력 현상 해결 (st.empty 컨테이너 활용)
# 2. DALL-E 모델 자동 폴백(dall-e-3 -> dall-e-2) 및 친절한 권한 가이드 제공
# streamlit run 0911-4.py

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from openai import OpenAI

# ------------- 페이지 기본 설정 -------------
st.set_page_config(page_title="문서 분석 & 시각화 앱", page_icon="📑", layout="wide")
st.title("📑 예제3: 스마트 문서 분석 & 시각화 요약 앱")
st.caption("문서를 업로드하고 핵심 요약본 저장 및 직관적인 다이어그램/인포그래픽을 확인하세요.")

# 세션 상태 초기화
if "summary_result" not in st.session_state:
    st.session_state.summary_result = ""
if "visual_diagram" not in st.session_state:
    st.session_state.visual_diagram = ""
if "visual_image_url" not in st.session_state:
    st.session_state.visual_image_url = ""

# Mermaid 렌더링 함수
def render_mermaid(code: str, height: int = 450):
    html_code = f"""
    <div class="mermaid" style="text-align: center;">
    {code}
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
    </script>
    """
    components.html(html_code, height=height, scrolling=True)

# ------------- 사이드바 설정 -------------
with st.sidebar:
    st.header("⚙️ 설정 및 옵션")
    api_key = st.text_input("OpenAI API Key", type="password", help="sk-로 시작하는 OpenAI API key를 입력하세요.")
    model = st.selectbox("모델 선택", ["gpt-4o-mini", "gpt-4o"], index=0)

    st.divider()
    st.subheader("📝 요약 옵션")
    summary_length = st.radio("요약 길이", ["짧게 (1~2줄 핵심)", "보통 (3~5개 불릿포인트)", "자세히 (상세 분석 및 시사점)"], index=1)
    summary_style = st.selectbox("요약 스타일", ["개조식 (보고서 형태)", "친절한 설명체", "비즈니스 요약본", "핵심 키워드 중심"], index=0)

    st.markdown("[API 키 발급/크레딧 확인](https://platform.openai.com/account/billing/overview)")

# ------------- 메인 화면: 파일 업로드 -------------
uploaded_file = st.file_uploader(
    "요약할 파일을 업로드하세요 (지원 형식: CSV, TXT, MD, JSON 등)",
    type=["csv", "txt", "md", "json", "py"]
)

preview_placeholder = st.empty()
file_content = ""

if uploaded_file is not None:
    try:
        file_name = uploaded_file.name
        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            file_content = df.to_string()
            with preview_placeholder.container():
                st.subheader("📄 문서 미리보기 (데이터프레임)")
                st.dataframe(df.head(50), use_container_width=True)
                st.caption(f"총 행 수: {len(df)}개, 총 열 수: {len(df.columns)}개 (최대 50행 표시)")
        else:
            file_content = uploaded_file.read().decode("utf-8", errors="ignore")
            with preview_placeholder.container():
                st.subheader("📄 문서 미리보기")
                st.text_area("문서 내용", value=file_content[:3000], height=180, disabled=True, label_visibility="collapsed")
                if len(file_content) > 3000:
                    st.caption("⚠️ 파일 용량이 커 앞부분 3,000자만 미리보기에 표시합니다.")
    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
else:
    with preview_placeholder.container():
        st.info("📌 위 영역에 문서를 업로드하면 내용 분석 및 시각화가 가능해집니다.")

st.divider()

# ------------- 탭 인터페이스 -------------
tab_summary, tab_visual = st.tabs(["📝 문서 요약 및 다운로드", "🎨 그림으로 한눈에 알아보기"])

# ==========================================
# 탭 1: 문서 요약 및 다운로드 (중복 출력 해결)
# ==========================================
with tab_summary:
    start_summary = st.button("🚀 문서 요약하기", type="primary")

    # 결과를 표시할 전용 자리(Placeholder) 생성
    summary_box = st.empty()

    if start_summary:
        if not api_key:
            st.warning("⚠️ 사이드바에 먼저 OpenAI API Key를 입력해 주세요.")
        elif not file_content:
            st.error("요약할 문서를 먼저 업로드하세요.")
        else:
            try:
                client = OpenAI(api_key=api_key)
                prompt = f"""다음 문서를 주어진 조건에 맞추어 한국어로 요약 및 분석해 주세요.

[요약 조건]
- 요약 길이: {summary_length}
- 요약 스타일: {summary_style}

[문서 내용]
{file_content[:20000]}
"""
                with st.spinner("AI가 문서를 분석하고 요약하는 중입니다..."):
                    stream_response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "당신은 문서 분석 및 요약 전문가입니다. 지침에 맞춰 간결하고 구조화된 요약을 작성합니다."},
                            {"role": "user", "content": prompt}
                        ],
                        stream=True
                    )
                    # 중복 방지: summary_box 내부에서만 스트리밍하고 바로 session_state에 저장
                    with summary_box.container():
                        st.session_state.summary_result = st.write_stream(stream_response)

            except Exception as e:
                st.error(f"요약 처리 중 오류가 발생했습니다: {e}")

    # 이전에 요약된 결과가 있고 방금 버튼을 누른 게 아니라면 기존 결과 표시
    elif st.session_state.summary_result:
        with summary_box.container():
            st.markdown(st.session_state.summary_result)

    # 요약 결과가 있을 때만 다운로드 버튼 노출
    if st.session_state.summary_result:
        st.divider()
        st.download_button(
            label="💾 요약본 텍스트(.txt)로 저장하기",
            data=st.session_state.summary_result,
            file_name="문서요약_결과.txt",
            mime="text/plain",
            use_container_width=True
        )

# ==========================================
# 탭 2: 시각적 구조도 & 이미지 생성
# ==========================================
with tab_visual:
    st.subheader("📊 문서 핵심 시각화")
    visual_option = st.radio(
        "시각화 방식을 선택하세요:",
        ["구조도 다이어그램 (순서도/마인드맵 - 추천)", "AI 인포그래픽 이미지 (DALL-E)"],
        horizontal=True
    )

    if st.button("✨ 시각화 자료 생성하기", type="primary"):
        if not api_key:
            st.warning("⚠️ 사이드바에 먼저 OpenAI API Key를 입력해 주세요.")
        elif not file_content:
            st.error("분석할 문서를 먼저 업로드하세요.")
        else:
            client = OpenAI(api_key=api_key)

            # 1. Mermaid 다이어그램
            if "구조도" in visual_option:
                try:
                    with st.spinner("문서 핵심 구조를 다이어그램으로 변환하는 중..."):
                        res = client.chat.completions.create(
                            model=model,
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "당신은 정보 시각화 전문가입니다. 사용자의 문서를 읽고 핵심 구조를 보여주는 mermaid 코드를 작성하세요. "
                                        "반드시 'graph TD' 또는 'flowchart TD'로 시작하고 특수기호나 따옴표 오류가 없도록 간결하게 작성하세요. "
                                        "마크다운 코드 블록(```mermaid ... ```)만 출력하세요."
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": f"다음 문서의 핵심 구조도를 작성해줘:\n\n{file_content[:8000]}"
                                }
                            ]
                        )
                        raw = res.choices[0].message.content
                        st.session_state.visual_diagram = raw.replace("```mermaid", "").replace("```", "").strip()
                except Exception as e:
                    st.error(f"다이어그램 생성 오류: {e}")

            # 2. DALL-E 이미지 (자동 폴백 처리)
            else:
                try:
                    with st.spinner("이미지 생성 프롬프트 구체화 중..."):
                        p_res = client.chat.completions.create(
                            model=model,
                            messages=[
                                {
                                    "role": "system",
                                    "content": "Create a prompt for an infographic illustrating the core topic. Modern vector style, minimal text."
                                },
                                {
                                    "role": "user",
                                    "content": f"Text:\n\n{file_content[:2000]}"
                                }
                            ]
                        )
                        img_prompt = p_res.choices[0].message.content

                    # dall-e-3 우선 시도 후 실패 시 dall-e-2로 폴백
                    with st.spinner("이미지 생성 중 (OpenAI 호출)..."):
                        try:
                            img_res = client.images.generate(
                                model="dall-e-3",
                                prompt=img_prompt,
                                size="1024x1024",
                                quality="standard",
                                n=1
                            )
                        except Exception:
                            # dall-e-3 권한이 없을 경우 dall-e-2로 재시도
                            img_res = client.images.generate(
                                model="dall-e-2",
                                prompt=img_prompt[:900],
                                size="512x512",
                                n=1
                            )
                        st.session_state.visual_image_url = img_res.data[0].url

                except Exception as e:
                    st.error("⚠️ 이미지 모델 호출 실패")
                    st.info(
                        "현재 사용 중인 API Key는 DALL-E 호출 권한이 없거나 선불 충전 잔액이 부족합니다.\n\n"
                        "💡 **해결 방법:**\n"
                        "1. 상단의 **'구조도 다이어그램'** 옵션을 선택하시면 별도 권한/비용 없이 바로 시각화가 가능합니다.\n"
                        "2. 이미지를 사용하시려면 [OpenAI Billing](https://platform.openai.com/account/billing/overview)에서 \$5 이상 크레딧을 충전하고 Project 권한에서 DALL-E 모델이 켜져 있는지 확인해 주세요."
                    )

    # 시각화 결과 노출
    if st.session_state.visual_diagram and "구조도" in visual_option:
        st.markdown("#### 🗺️ 문서 핵심 구조도")
        render_mermaid(st.session_state.visual_diagram)
        with st.expander("다이어그램 소스 코드"):
            st.code(st.session_state.visual_diagram, language="mermaid")

    if st.session_state.visual_image_url and "AI 인포그래픽" in visual_option:
        st.markdown("#### 🖼️ AI 생성 인포그래픽")
        st.image(st.session_state.visual_image_url, caption="문서 요약 인포그래픽", use_container_width=True)