content = """# 무역 직무 MBTI 진단 (Trade Job MBTI Assessment)

## 프로젝트 개요
사용자의 성향을 20개의 질문을 통해 분석하고, 6가지 무역 관련 직무 중 가장 적합한 직무를 추천해주는 Streamlit 기반 웹 애플리케이션입니다.

## 주요 기능
- **20개 문항의 성향 진단 테스트**: 사용자의 업무 스타일, 문제 해결 방식, 의사소통 성향 등을 직관적으로 파악합니다.
- **6개 무역 직무 매칭**: 진단 결과를 바탕으로 아래 6가지 직무 중 가장 적합한 직무를 추천합니다.
  1. 해외 영업 (Overseas Sales)
  2. 무역 물류/오퍼레이션 (Trade Logistics/Operations)
  3. 무역 사무/지원 (Trade Administration/Support)
  4. 글로벌 소싱/구매 (Global Sourcing/Purchasing)
  5. 해외 마케팅 (Overseas Marketing)
  6. 관세/통관 (Customs/Clearance)
- **결과 리포트 제공**: 추천된 직무의 주요 업무, 필요 역량, 그리고 사용자의 성향과 잘 맞는 이유를 설명해 줍니다.

## 기술 스택
- **Language**: Python
- **Framework**: Streamlit

## 설치 및 실행 방법

1. 필요한 패키지를 설치합니다.
   ```bash
   pip install streamlit