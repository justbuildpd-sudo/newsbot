#!/usr/bin/env python3
"""
국회의원 데이터 필드 확인
"""

from assembly_api_service import assembly_api

def check_member_data():
    """국회의원 데이터 필드 확인"""
    print("=== 국회의원 데이터 필드 확인 ===")
    
    members = assembly_api.get_member_list()
    print(f"총 의원 수: {len(members)}")
    
    if members:
        print("\n첫 번째 의원의 모든 필드:")
        first_member = members[0]
        for key, value in first_member.items():
            print(f"  {key}: {value}")
        
        print(f"\nID가 있는 의원 수: {len([m for m in members if m.get('id')])}")
        print(f"empno가 있는 의원 수: {len([m for m in members if m.get('empno')])}")
        print(f"name이 있는 의원 수: {len([m for m in members if m.get('name')])}")
        
        # empno 필드가 있는 의원들 확인
        empno_members = [m for m in members if m.get('empno')]
        if empno_members:
            print(f"\nempno 필드가 있는 첫 번째 의원:")
            empno_member = empno_members[0]
            for key, value in empno_member.items():
                print(f"  {key}: {value}")
            
            # empno로 상세 정보 조회 테스트
            print(f"\nempno {empno_member['empno']}로 상세 정보 조회 테스트...")
            detail = assembly_api.get_member_detail(empno_member['empno'])
            if detail:
                print("상세 정보 조회 성공!")
                print(f"상세 정보 키: {list(detail.keys())}")
                if detail.get('items'):
                    print(f"상세 정보 항목 수: {len(detail['items'])}")
                else:
                    print("상세 정보 항목이 비어있음")
            else:
                print("상세 정보 조회 실패")

if __name__ == "__main__":
    check_member_data()
