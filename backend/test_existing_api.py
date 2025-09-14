#!/usr/bin/env python3
"""
기존 assembly_api_service 테스트
"""

from assembly_api_service import assembly_api

def test_existing_api():
    """기존 API 서비스 테스트"""
    print("=== 기존 Assembly API 서비스 테스트 ===")
    
    # 1. 국회의원 목록 조회
    print("\n1. 국회의원 목록 조회...")
    members = assembly_api.get_member_list()
    print(f"조회된 의원 수: {len(members)}")
    
    if members:
        print("첫 번째 의원 정보:")
        first_member = members[0]
        for key, value in first_member.items():
            print(f"  {key}: {value}")
        
        # 2. 상세 정보 조회 (첫 번째 의원)
        print(f"\n2. {first_member['name']} 상세 정보 조회...")
        detail = assembly_api.get_member_detail(first_member['id'])
        if detail:
            print("상세 정보:")
            print(detail)
        else:
            print("상세 정보 조회 실패")
        
        # 3. 정당별 조회
        print(f"\n3. {first_member['party']} 정당별 조회...")
        party_members = assembly_api.get_members_by_party(first_member['party'])
        print(f"{first_member['party']} 소속 의원 수: {len(party_members)}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_existing_api()
