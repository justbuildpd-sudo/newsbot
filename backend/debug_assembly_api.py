#!/usr/bin/env python3
"""
국회 API 디버깅 스크립트
"""

import requests
import json
import xml.etree.ElementTree as ET

def test_assembly_api():
    """국회 API 테스트"""
    api_key = "RoSdWk52fty0NNpB6SxxmgXiC2vEXOpOSw1bHPcRxuBEmcXi91fT52waWOMDo67trsxJcm59pVGNYExnLOa8A=="
    base_url = "https://apis.data.go.kr/9710000/NationalAssemblyInfoService"
    
    print("=== 국회 API 테스트 ===")
    
    # 1. 기본 정보 조회 테스트
    print("\n1. 기본 정보 조회 테스트...")
    try:
        url = f"{base_url}/getMemberList"
        params = {
            'serviceKey': api_key,
            'numOfRows': 10,
            'pageNo': 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        print(f"상태 코드: {response.status_code}")
        print(f"응답 헤더: {dict(response.headers)}")
        print(f"응답 내용 (처음 500자): {response.text[:500]}")
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            items = root.findall('.//item')
            print(f"조회된 항목 수: {len(items)}")
            
            if items:
                print("첫 번째 항목:")
                for child in items[0]:
                    print(f"  {child.tag}: {child.text}")
        
    except Exception as e:
        print(f"오류: {e}")
    
    # 2. 상세 정보 조회 테스트 (테스트용 ID)
    print("\n2. 상세 정보 조회 테스트...")
    try:
        url = f"{base_url}/getMemberDetailInfo"
        params = {
            'serviceKey': api_key,
            'dept_cd': '9770001'  # 테스트용 ID
        }
        
        response = requests.get(url, params=params, timeout=10)
        print(f"상태 코드: {response.status_code}")
        print(f"응답 내용 (처음 500자): {response.text[:500]}")
        
    except Exception as e:
        print(f"오류: {e}")
    
    # 3. 다른 엔드포인트 테스트
    print("\n3. 다른 엔드포인트 테스트...")
    endpoints = [
        'getMemberList',
        'getMemberDetailInfo', 
        'getMemberCurrStateList',
        'getMemberPartyList'
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}/{endpoint}"
            params = {
                'serviceKey': api_key,
                'numOfRows': 5,
                'pageNo': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            print(f"{endpoint}: {response.status_code}")
            
        except Exception as e:
            print(f"{endpoint}: 오류 - {e}")

if __name__ == "__main__":
    test_assembly_api()
