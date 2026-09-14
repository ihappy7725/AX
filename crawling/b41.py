from bs4 import BeautifulSoup
import requests
import pandas as pd

# 해당 주소의 데이터를 읽어다가 텍스트로 변환하여 parser로 잘라서 soup에 담겠다. 
response = requests.get("https://startcoding.pythonanywhere.com/basic")
html = response.text
soup = BeautifulSoup(html, "html.parser")

logo = soup.select_one("").text
subtitle = soup.select_one("").text

print(logo, subtitle)

