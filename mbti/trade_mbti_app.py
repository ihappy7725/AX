import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import os
import base64
from PIL import Image

def get_image_path(filename):
    rel_path = os.path.join("images", filename)
    if os.path.exists(rel_path):
        return rel_path
    abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", filename)
    if os.path.exists(abs_path):
        return abs_path
    return None

def main():
    st.set_page_config(page_title="무역 직무 MBTI 진단", layout="centered", page_icon="🚢")
    
    if "page" not in st.session_state:
        st.session_state.page = "start"
    if "scores" not in st.session_state:
        st.session_state.scores = None
    if "effects_shown" not in st.session_state:
        st.session_state.effects_shown = False
    if "selected_job" not in st.session_state:
        st.session_state.selected_job = None

    jobs_info = {
        "해외 영업": {
            "mbti_name": "글로벌 개척가형 (Global Pioneer)",
            "image_file": "sales.png",
            "desc": "해외 바이어를 발굴하고 인코텀즈(Incoterms) 및 결제 조건을 조율하여 수출입 계약을 성사시킵니다. 해외 전시회에 참가하거나 B2B 세일즈 전략을 기획하여 기업의 글로벌 매출 목표를 달성하는 최전선 역할입니다.",
            "skills": "뛰어난 비즈니스 외국어 구사력, B2B 협상 및 설득력, 이문화 커뮤니케이션 능력, 위기관리 및 돌파력",
            "reason": "처음 보는 사람과도 주도적으로 네트워킹을 이끌어가며, 개인의 성과가 뚜렷하게 보상으로 연결되는 역동적인 환경에서 강력한 동기부여를 받는 성향입니다."
        },
        "물류/오퍼레이션": {
            "mbti_name": "운송 마스터형 (Logistics Master)",
            "image_file": "logistics.png",
            "desc": "포워딩 및 선사를 수배하고 수출입 화물의 전체 운송 스케줄을 통제합니다. 선하증권(B/L) 발행, 화물 추적, 하역, 보관까지 물리적인 물류 흐름을 관리하며 지연 및 파손 이슈에 즉각 대응합니다.",
            "skills": "수출입 물류 프로세스에 대한 깊은 이해, 다중 이해관계자 조율 능력, 신속한 문제해결 및 상황 대처력",
            "reason": "예상치 못한 돌발 변수가 발생해도 당황하지 않고 플랜 B를 즉각 가동하며, 실시간으로 얽혀있는 복잡한 일정을 매끄럽게 풀어내는 실무 해결 능력이 탁월합니다."
        },
        "무역 사무/지원": {
            "mbti_name": "서류 완벽주의자형 (Document Perfectionist)",
            "image_file": "office.png",
            "desc": "상업송장, 포장명세서, 신용장(L/C) 네고 서류 등 무역 대금 결제와 선적에 필요한 핵심 서류를 작성하고 검토합니다. ERP 시스템 데이터 입력 및 마감 업무를 지원합니다.",
            "skills": "무역 결제 방식(T/T, L/C 등)에 대한 실무 지식, 오탈자를 잡아내는 고도의 꼼꼼함, 데이터 관리 및 엑셀 활용 능력",
            "reason": "명확한 규정과 매뉴얼 내에서 움직이는 것을 선호하며, 작은 실수 하나가 큰 사고로 이어질 수 있는 무역 서류 업무에서 묵묵하고 정확하게 안정감을 창출해 냅니다."
        },
        "글로벌 소싱/구매": {
            "mbti_name": "전략적 협상가형 (Strategic Negotiator)",
            "image_file": "sourcing.png",
            "desc": "전 세계 공급망을 분석하여 경쟁력 있는 단가와 품질을 갖춘 원부자재 및 상품을 발굴합니다. 공급사 평가, 납기 관리, 원가 계산 및 구매 계약 조건 협상을 주도합니다.",
            "skills": "글로벌 시장 및 원자재 동향 분석력, 재무 및 원가(이익률) 분석 능력, 공급사를 쥐락펴락하는 논리적인 협상력",
            "reason": "감보다는 객관적인 데이터와 수치를 바탕으로 상황을 분석하고, 팽팽한 밀당을 통해 회사에 가장 유리한 조건을 쟁취하는 데에서 흥미와 성취감을 느낍니다."
        },
        "해외 마케팅": {
            "mbti_name": "트렌드 크리에이터형 (Trend Creator)",
            "image_file": "marketing.png",
            "desc": "타겟 국가의 소비 문화와 시장 트렌드를 분석하여 디지털 마케팅 캠페인을 기획합니다. 카탈로그, 홍보 영상, SNS 콘텐츠를 제작하여 글로벌 시장에서 인지도를 제고합니다.",
            "skills": "글로벌 마케팅 트렌드 캐치 능력, 창의적인 아이디어 기획 및 콘텐츠 제작 능력, 데이터 기반의 퍼포먼스 분석력",
            "reason": "새로운 문화와 트렌드를 흡수하여 매력적인 시각 자료나 기획안으로 구체화하는 것을 즐기며, 텍스트보다는 직관적인 메시지로 사람들의 마음을 움직이는 데 뛰어납니다."
        },
        "관세/통관": {
            "mbti_name": "규정 수호자형 (Compliance Guardian)",
            "image_file": "customs.png",
            "desc": "수출입 물품의 정확한 품목분류(HS Code)를 판정하고 관세법, 대외무역법에 따른 적법한 통관 절차를 수행합니다. FTA 원산지 증명 발급, 사후 검증 대응 등 리스크를 방어합니다.",
            "skills": "관세법 및 FTA 협정문에 대한 깊은 전문 지식, 복잡한 법률 및 규정 해석 능력, 높은 윤리 의식과 논리적 사고",
            "reason": "복잡하고 딱딱한 법률 문서를 다루는 데 거부감이 없으며, 명확한 근거와 논리를 바탕으로 회사의 리스크를 예방하는 원칙주의자적인 성향에 가장 부합합니다."
        }
    }

    questions = [
        {"q": "1. 처음 만나는 바이어나 관계자에게 먼저 다가가 대화를 주도하는 편입니까?", "yes": ["해외 영업", "해외 마케팅"], "no": ["무역 사무/지원", "관세/통관"]},
        {"q": "2. 정해진 매뉴얼과 절차가 갖춰진 상태에서 업무를 진행하는 것을 선호합니까?", "yes": ["무역 사무/지원", "관세/통관"], "no": ["해외 마케팅", "글로벌 소싱/구매"]},
        {"q": "3. 선박 지연 등 돌발 변수가 발생했을 때, 당황하지 않고 즉각적인 대안(플랜B)을 찾아냅니까?", "yes": ["물류/오퍼레이션", "해외 영업"], "no": ["무역 사무/지원", "관세/통관"]},
        {"q": "4. 직관보다는 시장 데이터나 수치를 분석하여 객관적인 결론을 도출하는 것을 좋아합니까?", "yes": ["글로벌 소싱/구매", "관세/통관"], "no": ["해외 영업", "해외 마케팅"]},
        {"q": "5. B/L이나 서류의 미세한 오탈자나 금액/날짜 오류를 단번에 찾아내는 꼼꼼함이 있습니까?", "yes": ["무역 사무/지원", "관세/통관"], "no": ["해외 마케팅", "해외 영업"]},
        {"q": "6. 논리적인 근거를 바탕으로 상대방을 설득해 내가 원하는 결과를 얻어내는 데 능숙합니까?", "yes": ["해외 영업", "글로벌 소싱/구매"], "no": ["물류/오퍼레이션", "무역 사무/지원"]},
        {"q": "7. 타 국가의 최신 트렌드나 독특한 소비 문화를 조사하고 비즈니스에 적용하는 상상을 즐깁니까?", "yes": ["해외 마케팅", "해외 영업"], "no": ["무역 사무/지원", "관세/통관"]},
        {"q": "8. 여러 가지 다른 성격의 실무가 동시에 쏟아져도 우선순위를 정해 매끄럽게 처리(멀티태스킹)합니까?", "yes": ["물류/오퍼레이션", "해외 마케팅"], "no": ["관세/통관", "글로벌 소싱/구매"]},
        {"q": "9. 가격 협상 테이블에서 팽팽한 밀당을 통해 유리한 조건을 쟁취하는 과정이 흥미롭습니까?", "yes": ["글로벌 소싱/구매", "해외 영업"], "no": ["무역 사무/지원", "관세/통관"]},
        {"q": "10. 법률, 협정문 등 복잡하고 딱딱한 문서를 읽고 정확하게 해석하여 적용하는 데 거부감이 없습니까?", "yes": ["관세/통관", "무역 사무/지원"], "no": ["해외 마케팅", "해외 영업"]},
        {"q": "11. 무에서 유를 창조하는 기획안을 작성하거나, 창의적인 아이디어를 구상하는 것을 좋아합니까?", "yes": ["해외 마케팅"], "no": ["물류/오퍼레이션", "무역 사무/지원"]},
        {"q": "12. 책상에 앉아 문서만 보기보다는 현장 상황을 직접 확인하고 즉각적으로 행동하는 편입니까?", "yes": ["물류/오퍼레이션", "해외 영업"], "no": ["무역 사무/지원", "관세/통관"]},
        {"q": "13. 변화가 많은 환경보다 주기적이고 반복적인 업무 사이클 내에서 안정감과 성취감을 느낍니까?", "yes": ["무역 사무/지원", "관세/통관"], "no": ["해외 마케팅", "해외 영업"]},
        {"q": "14. 환율 변동, 운임, 원가 및 이익률 등 복잡한 숫자를 계산하고 다루는 업무에 자신이 있습니까?", "yes": ["글로벌 소싱/구매", "관세/통관"], "no": ["해외 마케팅", "물류/오퍼레이션"]},
        {"q": "15. 타 부서나 외부 협력사 사이에서 입장을 조율하고 커뮤니케이션 병목을 잘 풀어냅니까?", "yes": ["물류/오퍼레이션", "글로벌 소싱/구매"], "no": ["무역 사무/지원"]},
        {"q": "16. 나의 개인적인 실적과 달성률이 숫자로 명확하게 증명되는 환경에서 더 큰 동기부여를 받습니까?", "yes": ["해외 영업", "글로벌 소싱/구매"], "no": ["무역 사무/지원", "물류/오퍼레이션"]},
        {"q": "17. 텍스트 나열보다 매력적인 시각 자료(디자인, 영상 등)를 통해 사람의 시선을 끄는 것에 관심이 많습니까?", "yes": ["해외 마케팅"], "no": ["관세/통관", "무역 사무/지원"]},
        {"q": "18. 화물의 이동 경로나 전체적인 서플라이 체인(Supply Chain)의 구조를 파악하는 데 흥미가 있습니까?", "yes": ["물류/오퍼레이션", "글로벌 소싱/구매"], "no": ["해외 마케팅", "무역 사무/지원"]},
        {"q": "19. 주장을 관철시키기 위해 관련 법규나 조사 자료 등 객관적인 '팩트'를 수집하는 데 집요한 편입니까?", "yes": ["글로벌 소싱/구매", "관세/통관"], "no": ["해외 영업"]},
        {"q": "20. 다소 스트레스가 있더라도 변화무쌍하고 다이내믹하며 활동적인 업무 환경을 원하십니까?", "yes": ["해외 영업", "물류/오퍼레이션"], "no": ["무역 사무/지원", "관세/통관"]}
    ]

    def make_card(title, content, icon):
        return f"""
        <div style='border: 1px solid #E0E0E0; border-top: 4px solid #2196F3; border-radius: 8px; padding: 15px; height: 100%; background-color: #FAFAFA;'>
            <h4 style='color: #333; margin-top: 0;'>{icon} {title}</h4>
            <p style='font-size: 1.0em; color: #555; line-height: 1.6;'>{content}</p>
        </div>
        """

    def get_image_base64(img_path):
        if img_path and os.path.exists(img_path):
            with open(img_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return None

    def fire_confetti():
        confetti_js = """
        <script>
        const doc = window.parent.document;
        if (!doc.getElementById('confetti-script')) {
            const script = doc.createElement('script');
            script.id = 'confetti-script';
            script.src = 'https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js';
            script.onload = function() {
                window.parent.confetti({particleCount: 200, spread: 120, origin: {y: 0.5}});
            };
            doc.head.appendChild(script);
        } else {
            window.parent.confetti({particleCount: 200, spread: 120, origin: {y: 0.5}});
        }
        </script>
        """
        components.html(confetti_js, height=0, width=0)

    # ------------------ 세련된 시작(랜딩) 페이지 ------------------
    if st.session_state.page == "start":
        st.markdown("""
        <div style='text-align: center; padding: 40px 20px;'>
            <h1 style='color: #1E3A8A; font-size: 2.8em; margin-bottom: 10px;'>🚢 무역 직무 MBTI 성향 진단</h1>
            <p style='color: #6B7280; font-size: 1.2em;'>내 성향에 딱 맞는 최적의 글로벌 무역 커리어를 찾아보세요!</p>
        </div>
        """, unsafe_allow_html=True)

        # 깔끔한 카드 디자인으로 안내 구성
        st.markdown("""
        <div style='display: flex; gap: 15px; margin-bottom: 25px;'>
            <div style='flex: 1; background: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; text-align: center;'>
                <div style='font-size: 1.8em; margin-bottom: 8px;'>🎯</div>
                <h4 style='margin: 0 0 8px 0; color: #1E293B;'>실무 밀착형 20문항</h4>
                <p style='font-size: 0.9em; color: #64748B; margin: 0;'>해외영업부터 관세통관까지 현업 기준 분석</p>
            </div>
            <div style='flex: 1; background: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; text-align: center;'>
                <div style='font-size: 1.8em; margin-bottom: 8px;'>📊</div>
                <h4 style='margin: 0 0 8px 0; color: #1E293B;'>정교한 5점 척도</h4>
                <p style='font-size: 0.9em; color: #64748B; margin: 0;'>내 성향의 강도를 섬세하게 반영한 매칭</p>
            </div>
            <div style='flex: 1; background: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; text-align: center;'>
                <div style='font-size: 1.8em; margin-bottom: 8px;'>🏆</div>
                <h4 style='margin: 0 0 8px 0; color: #1E293B;'>커스텀 페르소나</h4>
                <p style='font-size: 0.9em; color: #64748B; margin: 0;'>나만의 무역 직무 캐릭터와 상세 리포트 제공</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("📌 진단 전 필독 주의사항 (클릭하여 확인)"):
            st.markdown("""
            - 정답이 있는 테스트가 아닙니다. 너무 오래 고민하지 마시고 **3초 이내에 떠오르는 직관적인 느낌**으로 선택해 주세요.
            - 1점(전혀 그렇지 않다)부터 5점(매우 그렇다) 사이의 슬라이더를 활용해 성향을 체크합니다.
            - 솔직하게 답변할수록 내게 가장 잘 맞는 무역 직무를 정확하게 찾을 수 있습니다.
            """)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # 버튼을 강조하는 마크다운 래퍼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 테스트 시작하기", use_container_width=True, type="primary"):
                st.session_state.page = "survey"
                st.rerun()

    # ------------------ 설문조사 페이지 ------------------
    elif st.session_state.page == "survey":
        st.header("📝 성향 진단 테스트")
        st.markdown("각 문항을 읽고 본인의 성향과 일치하는 정도를 선택해 주세요.")
        st.markdown("---")
        
        with st.form(key="mbti_form"):
            responses = []
            for i, q_data in enumerate(questions):
                st.markdown(f"**{q_data['q']}**")
                choice = st.select_slider(
                    f"질문 {i+1}",
                    options=[1, 2, 3, 4, 5],
                    value=3, 
                    label_visibility="collapsed"
                )
                responses.append(choice)
                st.markdown("---")
            
            submit_button = st.form_submit_button(label="진단 결과 보기")

        if submit_button:
            scores = {job: 0 for job in jobs_info.keys()}
            for i, resp in enumerate(responses):
                q_data = questions[i]
                yes_pts = resp
                no_pts = 6 - resp
                for job in q_data["yes"]: scores[job] += yes_pts
                for job in q_data["no"]: scores[job] += no_pts
            
            st.session_state.scores = scores
            st.session_state.page = "result"
            st.rerun()

    # ------------------ 결과 확인 페이지 ------------------
    elif st.session_state.page == "result":
        if not st.session_state.effects_shown:
            fire_confetti()
            st.session_state.effects_shown = True

        scores = st.session_state.scores
        sorted_jobs = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        top_1 = sorted_jobs[0][0]
        top_2 = sorted_jobs[1][0]
        top_3 = sorted_jobs[2][0]

        # 1. 상단에 사용자 결과 먼저 배치
        img_path = get_image_path(jobs_info[top_1]['image_file'])
        img_base64 = get_image_base64(img_path)
        
        if img_base64:
            img_html = f"<img src='data:image/png;base64,{img_base64}' style='width: 200px; display: block; margin: 0 auto 15px auto;'>"
        else:
            img_html = f"<div style='color: #FFEB3B; margin-bottom: 15px;'>[이미지를 찾을 수 없습니다: images 폴더에 {jobs_info[top_1]['image_file']} 가 있는지 확인하세요]</div>"

        st.markdown(f"""
        <div style='background-color: #2196F3; padding: 30px; border-radius: 15px; text-align: center; color: white; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            {img_html}
            <h1 style='margin: 0; font-size: 2.2em;'>당신은 <b>'{jobs_info[top_1]['mbti_name']}'</b> 입니다!</h1>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("💡 당신에게 가장 잘 맞는 무역 직무")
        
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.markdown(make_card("주요 업무", jobs_info[top_1]['desc'], "📌"), unsafe_allow_html=True)
        with col_c2:
            st.markdown(make_card("필요 역량", jobs_info[top_1]['skills'], "💪"), unsafe_allow_html=True)
        with col_c3:
            st.markdown(make_card("추천 이유", jobs_info[top_1]['reason'], "🎯"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("### 🥈 & 🥉 다음으로 잘 맞는 직무")
        col_rank2, col_rank3 = st.columns(2)
        
        with col_rank2:
            st.info(f"**2순위: {jobs_info[top_2]['mbti_name']}**")
            st.caption(jobs_info[top_2]["desc"])
            
        with col_rank3:
            st.info(f"**3순위: {jobs_info[top_3]['mbti_name']}**")
            st.caption(jobs_info[top_3]["desc"])

        st.markdown("---")

        st.markdown("## 📊 직무별 적합도 분석 그래프")
        df_scores = pd.DataFrame(sorted_jobs, columns=["직무", "점수"])
        fig = px.pie(
            df_scores, values="점수", names="직무", 
            title="나의 6대 무역 직무 성향 비율",
            color_discrete_sequence=px.colors.sequential.Blues_r, hole=0.3 
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # 2. 하단에 다른 무역 직무 살펴보기 배치
        st.subheader("🔍 다른 무역 직무 MBTI 살펴보기")
        other_jobs = [job for job in jobs_info.keys() if job != top_1]
        cols = st.columns(len(other_jobs))
        
        for idx, job in enumerate(other_jobs):
            with cols[idx]:
                img_path2 = get_image_path(jobs_info[job]['image_file'])
                if img_path2:
                    st.image(Image.open(img_path2), use_container_width=True)
                else:
                    st.warning("이미지 누락")
                    
                st.markdown(f"<div style='text-align:center; font-size:0.9em; font-weight:bold;'>{job}</div>", unsafe_allow_html=True)
                if st.button("상세보기", key=f"btn_{job}", use_container_width=True):
                    st.session_state.selected_job = job
                    st.session_state.page = "detail"
                    st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 처음으로 돌아가기"):
            st.session_state.page = "start"
            st.session_state.scores = None
            st.session_state.effects_shown = False
            st.rerun()

    # ------------------ 개별 직무 상세 확인 페이지 ------------------
    elif st.session_state.page == "detail":
        job = st.session_state.selected_job
        info = jobs_info[job]
        
        detail_img_path = get_image_path(info['image_file'])
        detail_img_base64 = get_image_base64(detail_img_path)
        
        if detail_img_base64:
            detail_img_html = f"<img src='data:image/png;base64,{detail_img_base64}' style='width: 200px; display: block; margin: 0 auto 15px auto;'>"
        else:
            detail_img_html = "<div style='color: #FFEB3B; margin-bottom: 15px;'>[이미지를 찾을 수 없습니다]</div>"

        st.markdown(f"""
        <div style='background-color: #2196F3; padding: 30px; border-radius: 15px; text-align: center; color: white; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            {detail_img_html}
            <h2 style='margin: 0;'>🔍 <b>{info['mbti_name']}</b> 파헤치기</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.markdown(make_card("주요 업무", info['desc'], "📌"), unsafe_allow_html=True)
        with col_c2:
            st.markdown(make_card("필요 역량", info['skills'], "💪"), unsafe_allow_html=True)
        with col_c3:
            st.markdown(make_card("추천 이유", info['reason'], "🎯"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔙 내 결과로 돌아가기", use_container_width=True):
                st.session_state.page = "result"
                st.rerun()
        with col2:
            if st.button("🔄 처음부터 다시 테스트하기", use_container_width=True):
                st.session_state.page = "start"
                st.session_state.scores = None
                st.session_state.effects_shown = False
                st.session_state.selected_job = None
                st.rerun()

if __name__ == "__main__":
    main()