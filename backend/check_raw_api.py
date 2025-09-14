#!/usr/bin/env python3
"""
원본 API 응답 확인
"""

import requests
import xml.etree.ElementTree as ET

def check_raw_api():
    """원본 API 응답 확인"""
    api_key = "RoSdWk52fty0NNpB6SxxmgXiC2vEXOpOSw1bHPcRxuBEmcXi91fT52waWOMDo67trsxJcm59pVGNYExnLOa8A=="
    base_url = "https://apis.data.go.kr/9710000/NationalAssemblyInfoService"
    
    print("=== 원본 API 응답 확인 ===")
    
    # getMemberCurrStateList 호출
    url = f"{base_url}/getMemberCurrStateList"
    params = {
        'serviceKey': api_key,
        'numOfRows': 5,
        'pageNo': 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"상태 코드: {response.status_code}")
        print(f"응답 내용 (처음 1000자):")
        print(response.text[:1000])
        
        if response.status_code == 200:
            # XML 파싱
            root = ET.fromstring(response.content)
            items = root.findall('.//item')
            print(f"\n조회된 항목 수: {len(items)}")
            
            if items:
                print("\n첫 번째 항목의 원본 필드들:")
                first_item = items[0]
                for child in first_item:
                    print(f"  {child.tag}: {child.text}")
                
                # empno 필드 확인
                empno = first_item.find('empno')
                if empno is not None:
                    print(f"\nempno 필드 발견: {empno.text}")
                else:
                    print("\nempno 필드 없음")
                
                # 다른 ID 관련 필드들 확인
                id_fields = ['empno', 'dept_cd', 'hgNm', 'empNm']
                for field in id_fields:
                    element = first_item.find(field)
                    if element is not None and element.text:
                        print(f"{field}: {element.text}")
                    else:
                        print(f"{field}: 없음 또는 비어있음")
        
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    check_raw_api()
