# download_images.py
# [보조 도구] 필요한 정적 자원을 자동 수급하는 유틸리티 

import urllib.request
import os

# assets 폴더가 없으면 생성
os.makedirs("assets", exist_ok=True)

# Unsplash의 저작권 무료 고화질 대표 여행 이미지 URL 목록
image_urls = {
    "assets/korea.jpg": "https://images.unsplash.com/photo-1517154421773-0529f29ea451?w=800&q=80",      # 서울 경복궁
    "assets/usa.jpg": "https://images.unsplash.com/photo-1485738422979-f5c462d49f74?w=800&q=80",        # 뉴욕 자유의 여신상
    "assets/china.jpg": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800&q=80",      # 만리장성
    "assets/japan.jpg": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80",      # 교토/후지산 풍경
    "assets/vietnam.jpg": "https://images.unsplash.com/photo-1528127269322-539801943592?w=800&q=80"    # 하롱베이
}

headers = {"User-Agent": "Mozilla/5.0"}

for path, url in image_urls.items():
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response, open(path, "wb") as out_file:
            out_file.write(response.read())
        print(f"다운로드 성공: {path}")
    except Exception as e:
        print(f"다운로드 실패 ({path}): {e}")

print("모든 이미지 다운로드 작업 완료!")