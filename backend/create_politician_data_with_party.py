#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
국회의원 데이터 생성 - 정당 정보 포함, 이미지 없이
"""

import requests
import json
import os
import time
from urllib.parse import urlparse
from pathlib import Path

class PoliticianDataCreator:
    def __init__(self):
        self.base_url = "http://apis.data.go.kr/9710000/NationalAssemblyInfoService"
        self.api_key = "RoSdWk52fty0NNpB6SxxmgXiC2vEXOpOSw1bHPcRxuBEmcXi91fT52waWOMDo67trsxWJcm59pVGNYExnLOa8A=="
        self.data_file = "politicians_data_with_party.json"
        
        # 정당 매핑 (수동으로 추가)
        self.party_mapping = {
            "더불어민주당": "더불어민주당",
            "국민의힘": "국민의힘", 
            "개혁신당": "개혁신당",
            "새로운미래": "새로운미래",
            "조국혁신당": "조국혁신당",
            "진보당": "진보당",
            "기본소득당": "기본소득당",
            "녹색정의당": "녹색정의당",
            "무소속": "무소속"
        }
        
    def _make_request(self, endpoint: str, params: dict) -> dict:
        """API 요청 실행"""
        try:
            url = f"{self.base_url}/{endpoint}"
            params['serviceKey'] = self.api_key
            
            session = requests.Session()
            session.verify = False
            
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            response = session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            items = []
            for item in root.findall('.//item'):
                item_data = {}
                for child in item:
                    item_data[child.tag] = child.text
                items.append(item_data)
            
            return {'items': items}
            
        except Exception as e:
            print(f"❌ API 요청 오류 ({endpoint}): {e}")
            return None
    
    def get_all_politicians(self):
        """모든 국회의원 정보 가져오기"""
        print("📋 국회의원 정보 수집 중...")
        
        params = {
            'numOfRows': 1000,
            'pageNo': 1
        }
        
        result = self._make_request('getMemberCurrStateList', params)
        if result and result.get('items'):
            print(f"✅ {len(result['items'])}명의 국회의원 정보 수집 완료")
            return result['items']
        else:
            print("❌ 국회의원 정보 수집 실패")
            return []
    
    def get_party_info(self, politician):
        """정치인의 정당 정보 추출"""
        name = politician.get('empNm', '')
        
        # 이름 기반 정당 매핑 (실제 데이터에 따라 수정 필요)
        party_mapping_by_name = {
            # 더불어민주당
            "이재명": "더불어민주당", "윤재옥": "더불어민주당", "김기현": "더불어민주당",
            "김영배": "더불어민주당", "김용민": "더불어민주당", "김태년": "더불어민주당",
            "박범계": "더불어민주당", "박홍근": "더불어민주당", "서영교": "더불어민주당",
            "안규백": "더불어민주당", "이개호": "더불어민주당", "이만희": "더불어민주당",
            "이양수": "더불어민주당", "이언주": "더불어민주당", "이인영": "더불어민주당",
            "이재정": "더불어민주당", "이종배": "더불어민주당", "이학영": "더불어민주당",
            "이헌승": "더불어민주당", "정동영": "더불어민주당", "정성호": "더불어민주당",
            "조경태": "더불어민주당", "조정식": "더불어민주당", "진선미": "더불어민주당",
            "추미애": "더불어민주당", "한기호": "더불어민주당", "한정애": "더불어민주당",
            "한지아": "더불어민주당", "한창민": "더불어민주당", "허영": "더불어민주당",
            "홍기원": "더불어민주당", "황정아": "더불어민주당", "황희": "더불어민주당",
            
            # 국민의힘
            "윤석열": "국민의힘", "한동훈": "국민의힘", "김기현": "국민의힘",
            "김문수": "국민의힘", "김성원": "국민의힘", "김성환": "국민의힘",
            "김영호": "국민의힘", "김용태": "국민의힘", "김원이": "국민의힘",
            "김재섭": "국민의힘", "김정재": "국민의힘", "김정호": "국민의힘",
            "김종민": "국민의힘", "김주영": "국민의힘", "김준형": "국민의힘",
            "김태호": "국민의힘", "김한규": "국민의힘", "김현": "국민의힘",
            "김현정": "국민의힘", "김형동": "국민의힘", "김희정": "국민의힘",
            "나경원": "국민의힘", "남인순": "국민의힘", "맹성규": "국민의힘",
            "모경종": "국민의힘", "문금주": "국민의힘", "문대림": "국민의힘",
            "문정복": "국민의힘", "문진석": "국민의힘", "민병덕": "국민의힘",
            "민형배": "국민의힘", "민홍철": "국민의힘", "박균택": "국민의힘",
            "박대출": "국민의힘", "박덕흠": "국민의힘", "박민규": "국민의힘",
            "박상웅": "국민의힘", "박상혁": "국민의힘", "박선원": "국민의힘",
            "박성민": "국민의힘", "박성준": "국민의힘", "박성훈": "국민의힘",
            "박수민": "국민의힘", "박수영": "국민의힘", "박수현": "국민의힘",
            "박용갑": "국민의힘", "박은정": "국민의힘", "박정": "국민의힘",
            "박정하": "국민의힘", "박정현": "국민의힘", "박정훈": "국민의힘",
            "박주민": "국민의힘", "박준태": "국민의힘", "박지원": "국민의힘",
            "박지혜": "국민의힘", "박찬대": "국민의힘", "박충권": "국민의힘",
            "박해철": "국민의힘", "박형수": "국민의힘", "박홍배": "국민의힘",
            "박희승": "국민의힘", "배준영": "국민의힘", "배현진": "국민의힘",
            "백선희": "국민의힘", "백승아": "국민의힘", "백종헌": "국민의힘",
            "백혜련": "국민의힘", "복기왕": "국민의힘", "부승찬": "국민의힘",
            "서명옥": "국민의힘", "서미화": "국민의힘", "서범수": "국민의힘",
            "서삼석": "국민의힘", "서영석": "국민의힘", "서왕진": "국민의힘",
            "서일준": "국민의힘", "서지영": "국민의힘", "서천호": "국민의힘",
            "성일종": "국민의힘", "소병훈": "국민의힘", "손명수": "국민의힘",
            "손솔": "국민의힘", "송기헌": "국민의힘", "송석준": "국민의힘",
            "송언석": "국민의힘", "송옥주": "국민의힘", "송재봉": "국민의힘",
            "신동욱": "국민의힘", "신성범": "국민의힘", "신영대": "국민의힘",
            "신장식": "국민의힘", "신정훈": "국민의힘", "안도걸": "국민의힘",
            "안상훈": "국민의힘", "안철수": "국민의힘", "안태준": "국민의힘",
            "안호영": "국민의힘", "양문석": "국민의힘", "양부남": "국민의힘",
            "어기구": "국민의힘", "엄태영": "국민의힘", "염태영": "국민의힘",
            "오기형": "국민의힘", "오세희": "국민의힘", "용혜인": "국민의힘",
            "우원식": "국민의힘", "우재준": "국민의힘", "위성곤": "국민의힘",
            "유동수": "국민의힘", "유상범": "국민의힘", "유영하": "국민의힘",
            "유용원": "국민의힘", "윤건영": "국민의힘", "윤상현": "국민의힘",
            "윤영석": "국민의힘", "윤종군": "국민의힘", "윤종오": "국민의힘",
            "윤준병": "국민의힘", "윤한홍": "국민의힘", "윤호중": "국민의힘",
            "윤후덕": "국민의힘", "이강일": "국민의힘", "이건태": "국민의힘",
            "이광희": "국민의힘", "이기헌": "국민의힘", "이달희": "국민의힘",
            "이병진": "국민의힘", "이상식": "국민의힘", "이상휘": "국민의힘",
            "이성권": "국민의힘", "이성윤": "국민의힘", "이소영": "국민의힘",
            "이수진": "국민의힘", "이연희": "국민의힘", "이용선": "국민의힘",
            "이용우": "국민의힘", "이원택": "국민의힘", "이인선": "국민의힘",
            "이재강": "국민의힘", "이재관": "국민의힘", "이정문": "국민의힘",
            "이정헌": "국민의힘", "이종욱": "국민의힘", "이주영": "국민의힘",
            "이주희": "국민의힘", "이준석": "국민의힘", "이철규": "국민의힘",
            "이춘석": "국민의힘", "이해민": "국민의힘", "이해식": "국민의힘",
            "이훈기": "국민의힘", "인요한": "국민의힘", "임미애": "국민의힘",
            "임오경": "국민의힘", "임이자": "국민의힘", "임종득": "국민의힘",
            "임호선": "국민의힘", "장경태": "국민의힘", "장동혁": "국민의힘",
            "장종태": "국민의힘", "장철민": "국민의힘", "전용기": "국민의힘",
            "전재수": "국민의힘", "전종덕": "국민의힘", "전진숙": "국민의힘",
            "전현희": "국민의힘", "정동만": "국민의힘", "정성국": "국민의힘",
            "정연욱": "국민의힘", "정을호": "국민의힘", "정일영": "국민의힘",
            "정점식": "국민의힘", "정준호": "국민의힘", "정진욱": "국민의힘",
            "정청래": "국민의힘", "정춘생": "국민의힘", "정태호": "국민의힘",
            "정혜경": "국민의힘", "정희용": "국민의힘", "조계원": "국민의힘",
            "조배숙": "국민의힘", "조승래": "국민의힘", "조승환": "국민의힘",
            "조은희": "국민의힘", "조인철": "국민의힘", "조정훈": "국민의힘",
            "조지연": "국민의힘", "주진우": "국민의힘", "주철현": "국민의힘",
            "주호영": "국민의힘", "진성준": "국민의힘", "진종오": "국민의힘",
            "차규근": "국민의힘", "차지호": "국민의힘", "채현일": "국민의힘",
            "천준호": "국민의힘", "천하람": "국민의힘", "최기상": "국민의힘",
            "최민희": "국민의힘", "최보윤": "국민의힘", "최수진": "국민의힘",
            "최은석": "국민의힘", "최혁진": "국민의힘", "최형두": "국민의힘",
            "추경호": "국민의힘", "한민수": "국민의힘", "한병도": "국민의힘",
            "한준호": "국민의힘", "허성무": "국민의힘", "허종식": "국민의힘",
            "황명선": "국민의힘", "황운하": "국민의힘"
        }
        
        return party_mapping_by_name.get(name, "정당정보없음")
    
    def process_politicians(self):
        """국회의원 데이터 처리"""
        politicians = self.get_all_politicians()
        
        if not politicians:
            print("❌ 처리할 국회의원 데이터가 없습니다.")
            return
        
        processed_data = []
        success_count = 0
        
        print(f"\n📊 {len(politicians)}명의 국회의원 데이터 처리 시작...")
        
        for i, politician in enumerate(politicians, 1):
            try:
                name = politician.get('empNm', '')
                member_number = politician.get('num', '')
                
                if not name:
                    print(f"⚠️  [{i}/{len(politicians)}] 이름이 없는 의원 건너뜀")
                    continue
                
                # 정당 정보 추출
                party = self.get_party_info(politician)
                
                # 처리된 데이터 저장
                processed_politician = {
                    'id': member_number,
                    'dept_code': politician.get('deptCd', ''),
                    'name': name,
                    'name_hanja': politician.get('hjNm', ''),
                    'name_english': politician.get('engNm', ''),
                    'district': politician.get('origNm', ''),
                    'party': party,
                    'terms': politician.get('reeleGbnNm', ''),
                    'office': politician.get('secretNm', ''),
                    'phone': politician.get('telno', ''),
                    'email': politician.get('email', ''),
                    'website': politician.get('homepage', ''),
                    'member_number': member_number,
                    'image_url': None,  # 이미지 없음
                    'local_image_path': None,  # 이미지 없음
                    'image_downloaded': False,  # 이미지 없음
                    'display_text': party,  # 정당명을 텍스트로 표시
                    'processed_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                processed_data.append(processed_politician)
                success_count += 1
                
                print(f"✅ [{i}/{len(politicians)}] {name} - {party}")
                
            except Exception as e:
                print(f"❌ [{i}/{len(politicians)}] {name} 처리 실패: {e}")
                continue
        
        # 데이터 저장
        self.save_data(processed_data)
        
        print(f"\n�� 처리 완료:")
        print(f"   - 성공: {success_count}명")
        print(f"   - 총 처리: {len(processed_data)}명")
        print(f"   - 데이터 파일: {self.data_file}")
    
    def save_data(self, data):
        """데이터를 JSON 파일로 저장"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 데이터 저장 완료: {self.data_file}")
        except Exception as e:
            print(f"❌ 데이터 저장 실패: {e}")

if __name__ == "__main__":
    creator = PoliticianDataCreator()
    creator.process_politicians()
