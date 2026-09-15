import FinanceDataReader as fdr

# 삼성전자 종목 코드 '005930'을 넣고 최근 주가 데이터를 불러옵니다.
df = fdr.DataReader("005930")

# 가장 최근에 거래된 주가 데이터 5일치를 화면에 출력합니다.
print(df.tail())

df.to_excel("samsung_stock.xlsx", index=True)  # 인덱스 포함하여 엑셀로 저장