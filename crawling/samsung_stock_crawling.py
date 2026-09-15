import pandas as pd
import yfinance as yf

# 야후 파이낸스용 종목 코드 (한국 코스피는 뒤에 .KS 붙임)
stocks = {
    '삼성전자': '005930.KS',
    'SK하이닉스': '000660.KS',
    'LG에너지솔루션': '373220.KS',
}

data = []

for name, code in stocks.items():
  try:
    # 야후 파이낸스로 종목 정보 가져오기
    ticker = yf.Ticker(code)
    # 최신 일일 데이터(History) 가져오기
    todays_data = ticker.history(period='1d')

    if not todays_data.empty:
      # 가장 최근 종가 추출
      price = todays_data['Close'].iloc[0]
      formatted_price = f'{price:,.0f}'

      data.append({'종목명': name, '종목코드': code, '현재가': f'{formatted_price}원'})
      print(f'{name} 현재가: {formatted_price}원')
    else:
      print(f'{name} 데이터를 찾지 못했습니다.')
  except Exception as e:
    print(f'{name} 데이터 수집 중 오류 발생: {e}')

# 엑셀 파일로 저장
if data:
  df = pd.DataFrame(data)
  file_name = 'samsung_stock_crawling.xlsx'
  df.to_excel(file_name, index=False)
  print(f'\n크롤링 완료! [{file_name}] 파일로 저장되었습니다.')
else:
  print('\n가져온 데이터가 없습니다.')