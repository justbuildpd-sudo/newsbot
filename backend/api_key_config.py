#!/usr/bin/env python3
"""
API 키 설정 파일
6개의 API 키를 안전하게 관리
"""

# 국회 API 키들 (실제 키로 교체 완료)
API_KEYS = [
    "f9725b9012a14a0ab286770ce5de5e71",  # 첫 번째 API 키 - 실제 키 사용
    "YOUR_API_KEY_2",  # 두 번째 API 키 - 실제 키로 교체 필요
    "YOUR_API_KEY_3",  # 세 번째 API 키 - 실제 키로 교체 필요
    "YOUR_API_KEY_4",  # 네 번째 API 키 - 실제 키로 교체 필요
    "YOUR_API_KEY_5",  # 다섯 번째 API 키 - 실제 키로 교체 필요
    "YOUR_API_KEY_6"   # 여섯 번째 API 키 - 실제 키로 교체 필요
]

# API 기본 설정 (열린국회정보 Open API)
API_CONFIG = {
    "base_url": "https://open.assembly.go.kr/portal/openapi",
    "timeout": 30,
    "retry_count": 3,
    "retry_delay": 1,
    "rate_limit_delay": 0.2
}

# 엔드포인트 설정 (열린국회정보 Open API 실제 엔드포인트)
ENDPOINTS = {
    "members": "ALLNAMEMBER",           # 국회의원정보통합 API
    "member_sns": "negnlnyvatsjwocar",  # 국회의원 SNS정보
    "bills": "ALLBILL",                 # 의안정보통합 API
    "bill_reception": "BILLRCP",        # 의안 접수목록
    "bill_proposers": "BILLINFOPPSR",   # 의안 제안자정보
    "bill_detail": "BILLINFODETAIL"     # 의안 상세정보
}

# 실제 API 키가 필요한 경우를 위한 안내
API_KEY_REQUIRED_MESSAGE = """
⚠️  API 키가 필요합니다!

현재 'YOUR_API_KEY_1' ~ 'YOUR_API_KEY_6'로 설정되어 있습니다.
실제 API 키로 교체해야 합니다.

1. 열린국회정보 홈페이지 (https://open.assembly.go.kr) 방문
2. 회원가입 후 API 키 발급 신청
3. 발급받은 키를 api_key_config.py 파일의 API_KEYS 리스트에 입력

예시:
API_KEYS = [
    "실제_API_키_1",
    "실제_API_키_2",
    ...
]
"""

# 헤더 설정 (이전에 해결했던 방식)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/xml, text/xml, */*',
    'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache'
}
