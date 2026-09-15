# 파이썬을 이용해 웹사이트의 상품 정보(카테고리, 상품명, 링크, 가격)를 자동으로 긁어오기 (크롤링)


from bs4 import BeautifulSoup
import requests
import pandas as pd
import openpyxl   # 엑셀로 내보낼 수 있음

# 수집한 데이터를 차곡차곡 담아둘 빈 리스트(상자)를 준비합니다.
data = []

# 1부터 4까지 총 4번 반복합니다. (페이지를 여러 번 순회하며 데이터를 모을 때 사용합니다)
for i in range(1, 5):
    # 1. 지정한 웹 주소(URL)로 서버에 요청을 보내고 응답을 받습니다.
    response = requests.get(f"https://startcoding.pythonanywhere.com/basic?page={i}")
    
    # 2. 받아온 응답에서 HTML 소스코드만 텍스트 형태로 꺼냅니다.
    html = response.text
    
    # 3. BeautifulSoup을 사용해 HTML 코드를 컴퓨터가 이해하기 쉬운 구조로 분석(파싱)합니다.
    soup = BeautifulSoup(html, "html.parser")
    
    # 4. 웹페이지 안에서 상품 정보가 담긴 영역(.product 클래스)을 모두 찾아 리스트로 가져옵니다.
    items = soup.select(".product")

    # 5. 이번 반복에서 몇 개의 상품을 찾았는지 화면에 출력해 줍니다.
    print(f"가져온 상품 개수: {len(items)}개 \n" + "-" * 30)

    # 6. 찾은 상품들(items) 중에서 하나씩(item) 꺼내어 세부 정보를 추출합니다.
    for item in items:
        category = item.select_one(".product-category").text  # 상품의 카테고리 텍스트를 가져옴
        category_name = item.select_one(".product-name").text  # 상품의 이름 텍스트를 가져옴
        category_link = item.select_one(".product-name > a")['href']    # 상품 이름 태그 안에 있는 상세 페이지 주소(href 속성)를 가져옴
        price = item.select_one(".product-price").text.split("원")[0].replace(",", "")  # 상품의 가격 텍스트를 가져옴
        data.append([category, category_name, category_link, price])  # 수집한 정보를 리스트에 담음
        print(category, category_name, category_link, price)

# 수집한 데이터를 데이터프레임으로 변환
df = pd.DataFrame(data, columns=["카테고리", "상품명", "상세페이지링크", "가격"])  

# 데이터프레임을 엑셀 파일로 저장
df.to_excel("products.xlsx", index=False)  