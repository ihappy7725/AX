# 3단계: 공식 멀티페이지 기능으로 파일 나누기 

## 
- st.page("파일 경로", "title", "icon=....", default=True)
- st.navigation([...]) + pg.run()

폴더 구조 : app.py 를 기준으로 보면, app.py 는 조립만 하며, 실제 화면 내용은 view에 있는 파일이 담당한다. 

## 실행
"""
bash
    cd step03   
    streamlit run app.py 
"""