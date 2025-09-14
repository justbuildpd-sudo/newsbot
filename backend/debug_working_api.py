#!/usr/bin/env python3
"""
작동하는 API 서비스 디버깅
"""

from assembly_api_service import assembly_api
import json

def debug_working_api():
    """작동하는 API 서비스 디버깅"""
    print("=== 작동하는 API 서비스 디버깅 ===")
    
    # 1. get_member_list() 내부 동작 확인
    print("\n1. get_member_list() 내부 동작 확인...")
    
    # 캐시 초기화
    assembly_api.cache = {}
    assembly_api.cache_expiry = {}
    
    # 직접 API 호출
    try:
        params = {
            'numOfRows': 1000,
            'pageNo': 1
        }
        
        result = assembly_api._make_request('getMemberCurrStateList', params)
        print(f"API 호출 결과: {result is not None}")
        
        if result:
            print(f"응답 키: {list(result.keys())}")
            print(f"items 수: {len(result.get('items', []))}")
            
            if result.get('items'):
                first_item = result['items'][0]
                print(f"첫 번째 항목 키: {list(first_item.keys())}")
                print(f"첫 번째 항목 내용:")
                for key, value in first_item.items():
                    print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"API 호출 오류: {e}")
    
    # 2. get_member_list() 결과 확인
    print("\n2. get_member_list() 결과 확인...")
    members = assembly_api.get_member_list()
    print(f"조회된 의원 수: {len(members)}")
    
    if members:
        print("첫 번째 의원의 원본 데이터:")
        first_member = members[0]
        for key, value in first_member.items():
            print(f"  {key}: {value}")
        
        # 원본 데이터에서 ID 찾기
        print("\n원본 데이터에서 ID 관련 필드 찾기:")
        # assembly_api_service.py의 get_member_list()에서 사용하는 필드들 확인
        print("empno 필드 확인...")
        
        # 직접 API 응답에서 empno 찾기
        try:
            result = assembly_api._make_request('getMemberCurrStateList', {'numOfRows': 5, 'pageNo': 1})
            if result and result.get('items'):
                raw_item = result['items'][0]
                print(f"원본 empno: {raw_item.get('empno', '없음')}")
                print(f"원본 dept_cd: {raw_item.get('dept_cd', '없음')}")
                print(f"원본 hgNm: {raw_item.get('hgNm', '없음')}")
        except Exception as e:
            print(f"원본 데이터 확인 오류: {e}")

if __name__ == "__main__":
    debug_working_api()
