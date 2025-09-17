#!/usr/bin/env python3
"""
API 응답 테스트 스크립트
"""

import requests
import xml.etree.ElementTree as ET
from api_key_config import API_KEYS, API_CONFIG, HEADERS, ENDPOINTS

def test_api_response():
    """API 응답 테스트"""
    
    # API 설정
    api_key = API_KEYS[0]  # 첫 번째 키 사용
    base_url = API_CONFIG["base_url"]
    endpoint = ENDPOINTS["bills"]  # ALLBILL
    
    # 요청 파라미터 (BILL_NO 파라미터 추가)
    params = {
        'KEY': api_key,
        'Type': 'xml',
        'pIndex': 1,
        'pSize': 10,
        'BILL_NO': '2200001'  # 22대 첫 번째 법안 번호
    }
    
    url = f"{base_url}/{endpoint}"
    
    print(f"요청 URL: {url}")
    print(f"요청 파라미터: {params}")
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=30)
        print(f"응답 상태 코드: {response.status_code}")
        print(f"응답 내용 (처음 1000자):")
        print(response.text[:1000])
        
        if response.status_code == 200:
            # XML 파싱 시도
            try:
                root = ET.fromstring(response.text)
                print(f"\nXML 루트 태그: {root.tag}")
                
                # 결과 코드 확인
                result_code = root.find('.//resultCode')
                if result_code is not None:
                    print(f"결과 코드: {result_code.text}")
                
                # 메시지 확인
                result_msg = root.find('.//resultMsg')
                if result_msg is not None:
                    print(f"결과 메시지: {result_msg.text}")
                
                # 데이터 행 수 확인
                rows = root.findall('.//row')
                print(f"데이터 행 수: {len(rows)}")
                
                if len(rows) > 0:
                    print(f"첫 번째 행 데이터:")
                    for child in rows[0]:
                        print(f"  {child.tag}: {child.text}")
                
            except ET.ParseError as e:
                print(f"XML 파싱 오류: {e}")
        
    except Exception as e:
        print(f"요청 실패: {e}")

if __name__ == "__main__":
    test_api_response()
