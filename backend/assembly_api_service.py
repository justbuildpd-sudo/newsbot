#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
국회의원 API 서비스
공공데이터포털 국회의원 정보 API 연동
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import time
from datetime import datetime

class AssemblyAPIService:
    def __init__(self):
        self.base_url = "http://apis.data.go.kr/9710000/NationalAssemblyInfoService"
        self.api_key = "RoSdWk52fty0NNpB6SxxmgXiC2vEXOpOSw1bHPcRxuBEmcXi91fT52waWOMDo67trsxWJcm59pVGNYExnLOa8A=="
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 3600  # 1시간 캐시
        self.party_mapping = {}  # 정당 코드 -> 정당명 매핑
    
    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """API 요청 실행"""
        try:
            url = f"{self.base_url}/{endpoint}"
            params['serviceKey'] = self.api_key
            
            # SSL 검증 비활성화 및 세션 사용
            session = requests.Session()
            session.verify = False
            
            # SSL 경고 무시
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            response = session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # XML 파싱
            root = ET.fromstring(response.content)
            
            # 결과 추출
            items = []
            for item in root.findall('.//item'):
                item_data = {}
                for child in item:
                    item_data[child.tag] = child.text
                items.append(item_data)
            
            return {'items': items}
            
        except Exception as e:
            print(f"API 요청 오류 ({endpoint}): {e}")
            return None
    
    def get_member_list(self) -> List[Dict]:
        """국회의원 현황 조회 (실시간 API + 정당 정보 결합)"""
        cache_key = "member_list"
        
        # 캐시 확인
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            # 실시간 API에서 기본 정보 가져오기
            params = {
                'numOfRows': 1000,
                'pageNo': 1
            }
            
            result = self._make_request('getMemberCurrStateList', params)
            
            if result:
                # 정당 정보가 포함된 기존 데이터 로드
                import json
                import os
                
                processed_file = os.path.join(os.path.dirname(__file__), 'processed_assembly_members.json')
                party_data = {}
                if os.path.exists(processed_file):
                    with open(processed_file, 'r', encoding='utf-8') as f:
                        processed_members = json.load(f)
                        # 이름으로 매칭하기 위한 딕셔너리 생성
                        for member in processed_members:
                            party_data[member.get('name', '')] = {
                                'party': member.get('party', ''),
                                'committee': member.get('committee', ''),
                                'political_orientation': member.get('political_orientation', '중도성향'),
                                'key_issues': member.get('key_issues', ['정치', '국정', '의정'])
                            }
                
                members = []
                for item in result.get('items', []):
                    name = item.get('empNm', '')
                    party_info = party_data.get(name, {})
                    
                    # 정당 정보 가져오기 (수동 매핑 사용 - API에서 정당 정보 제공 안함)
                    manual_party = self._get_manual_party_info(name)
                    
                    # 상임위원회 정보 가져오기 (API 사용)
                    dept_cd = item.get('deptCd', '')
                    api_committee = self.get_member_committee(dept_cd) if dept_cd else ''
                    
                    member = {
                        'id': item.get('num', ''),  # 식별코드가 실제 의원 ID
                        'dept_code': dept_cd,  # 부서코드
                        'name': name,
                        'name_hanja': item.get('hjNm', ''),
                        'name_english': item.get('engNm', ''),
                        'party': party_info.get('party', manual_party),
                        'district': item.get('origNm', ''),
                        'committee': party_info.get('committee', api_committee),
                        'terms': item.get('reeleGbnNm', ''),
                        'office': item.get('secretNm', ''),
                        'phone': item.get('telno', ''),
                        'email': item.get('email', ''),
                        'website': item.get('homepage', ''),
                        'image_url': item.get('jpgLink', ''),
                        'member_number': item.get('num', ''),
                        'political_orientation': party_info.get('political_orientation', self._get_political_orientation(party_info.get('party', manual_party))),
                        'key_issues': party_info.get('key_issues', self._get_key_issues(party_info.get('committee', api_committee))),
                        'description': f"{item.get('origNm', '')} 지역구 {party_info.get('party', manual_party)} 소속",
                        'mention_count': 0,
                        'influence_score': 0
                    }
                    members.append(member)
                
                # 캐시 저장
                self.cache[cache_key] = members
                self.cache_expiry[cache_key] = time.time() + self.cache_duration
                
                print(f"✅ 국회의원 {len(members)}명 데이터 로드 완료 (실시간 API + 정당 정보)")
                return members
            else:
                print("❌ API 응답이 비어있습니다")
                return []
                
        except Exception as e:
            print(f"❌ 국회의원 목록 조회 오류: {e}")
            return []
    
    def get_member_detail(self, member_id: str) -> Optional[Dict]:
        """특정 국회의원 상세 정보 조회 (전체 목록에서 검색)"""
        try:
            # 전체 국회의원 목록에서 해당 ID 검색
            all_members = self.get_member_list()
            for member in all_members:
                if member.get('id') == member_id or member.get('member_number') == member_id:
                    return member
            return None
        except Exception as e:
            print(f"❌ 국회의원 상세 정보 조회 오류: {e}")
            return None
    
    def get_members_by_party(self, party_name: str) -> List[Dict]:
        """소속정당별 국회의원 목록 조회"""
        try:
            # 전체 목록에서 해당 정당 필터링
            all_members = self.get_member_list()
            filtered_members = [member for member in all_members if member.get('party') == party_name]
            
            return filtered_members
                
        except Exception as e:
            print(f"❌ 정당별 국회의원 조회 오류: {e}")
            return []
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """캐시 유효성 확인"""
        if cache_key in self.cache and cache_key in self.cache_expiry:
            return time.time() < self.cache_expiry[cache_key]
        return False
    
    def _get_political_orientation(self, party: str) -> str:
        """정당에 따른 정치 성향 판단"""
        progressive_parties = ["더불어민주당", "정의당", "진보당"]
        conservative_parties = ["국민의힘", "새누리당", "자유한국당"]
        
        if party in progressive_parties:
            return "진보성향"
        elif party in conservative_parties:
            return "보수성향"
        else:
            return "중도성향"
    
    def _get_key_issues(self, committee: str) -> List[str]:
        """위원회에 따른 주요 이슈 추출"""
        issue_mapping = {
            "환경노동위원회": ["환경보호", "노동권익", "기후변화"],
            "기획재정위원회": ["경제정책", "예산", "재정"],
            "과학기술정보방송통신위원회": ["과학기술", "정보통신", "방송"],
            "교육위원회": ["교육정책", "학교", "학생"],
            "문화체육관광위원회": ["문화", "체육", "관광"],
            "보건복지위원회": ["보건", "복지", "의료"],
            "법제사법위원회": ["법제", "사법", "인권"],
            "행정안전위원회": ["행정", "안전", "지방자치"]
        }
        
        for key, issues in issue_mapping.items():
            if key in committee:
                return issues
        
        return ["정치", "국정", "의정"]
    
    def _load_party_mapping(self):
        """정당 코드 -> 정당명 매핑 로드"""
        if self.party_mapping:
            return
        
        try:
            params = {'numOfRows': 100, 'pageNo': 1}
            result = self._make_request('getPolySearch', params)
            if result:
                for item in result.get('items', []):
                    party_code = item.get('polyCd', '')
                    party_name = item.get('polyNm', '')
                    if party_code and party_name:
                        self.party_mapping[party_code] = party_name
                print(f"✅ 정당 매핑 로드 완료: {len(self.party_mapping)}개 정당")
        except Exception as e:
            print(f"❌ 정당 매핑 로드 실패: {e}")
    
    def _get_party_name_by_code(self, party_code: str) -> str:
        """정당 코드로 정당명 조회"""
        self._load_party_mapping()
        return self.party_mapping.get(party_code, '')
    
    def get_committee_activities(self, dept_cd: str, dae_num: str = '22') -> List[Dict]:
        """특정 의원의 상임위원회 활동 조회"""
        try:
            params = {
                'numOfRows': 100,
                'pageNo': 1,
                'dept_cd': dept_cd,
                'dae_num': dae_num
            }
            result = self._make_request('getCommitAction', params)
            if result:
                activities = []
                for item in result.get('items', []):
                    activity = {
                        'committee': item.get('commName', ''),
                        'meeting_date': item.get('confDate', ''),
                        'session': item.get('sesNum', ''),
                        'degree': item.get('degreeNum', ''),
                        'matter_link': item.get('matterlink', ''),
                        'reg_date': item.get('regDate', '')
                    }
                    activities.append(activity)
                return activities
            return []
        except Exception as e:
            print(f"❌ 상임위원회 활동 조회 오류: {e}")
            return []
    
    def get_member_committee(self, dept_cd: str) -> str:
        """의원의 소속 상임위원회 조회 (가장 최근 활동 기준)"""
        try:
            activities = self.get_committee_activities(dept_cd)
            if activities:
                # 가장 최근 활동의 위원회 반환
                latest_activity = max(activities, key=lambda x: x.get('meeting_date', ''))
                return latest_activity.get('committee', '')
            return ''
        except Exception as e:
            print(f"❌ 의원 상임위원회 조회 오류: {e}")
            return ''
    
    def get_bill_list(self, num_of_rows: int = 100) -> List[Dict]:
        """의안발의 목록 조회 (열린국회정보 API 사용)"""
        try:
            # 열린국회정보 API 사용
            bill_api_url = "https://open.assembly.go.kr/portal/openapi/ALLBILL"
            bill_api_key = "e9b6c7dcdd04446094d5bbfdff7fc930"
            
            # 여러 의안번호로 조회 (연속된 의안번호 사용)
            bills = []
            start_bill_no = 2123836  # 시작 의안번호
            
            for i in range(min(num_of_rows, 20)):  # 최대 20개까지 조회
                bill_no = str(start_bill_no + i)
                
                params = {
                    'KEY': bill_api_key,
                    'Type': 'json',
                    'pIndex': 1,
                    'pSize': 1,
                    'BILL_NO': bill_no
                }
                
                try:
                    response = requests.get(bill_api_url, params=params, timeout=30)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if 'ALLBILL' in data and len(data['ALLBILL']) > 1:
                        if 'row' in data['ALLBILL'][1] and len(data['ALLBILL'][1]['row']) > 0:
                            item = data['ALLBILL'][1]['row'][0]
                            bill = {
                                'bill_id': item.get('BILL_ID', ''),
                                'bill_no': item.get('BILL_NO', ''),
                                'bill_name': item.get('BILL_NM', ''),
                                'bill_kind': item.get('BILL_KND', ''),
                                'proposer': item.get('PPSR_NM', ''),
                                'proposer_kind': item.get('PPSR_KND', ''),
                                'propose_date': item.get('PPSL_DT', ''),
                                'committee': item.get('JRCMIT_NM', ''),
                                'committee_result': item.get('JRCMIT_PROC_RSLT', ''),
                                'assembly_result': item.get('RGS_CONF_RSLT', ''),
                                'link_url': item.get('LINK_URL', '')
                            }
                            bills.append(bill)
                except Exception as e:
                    print(f"❌ 의안 {bill_no} 조회 오류: {e}")
                    continue
                
                # API 호출 간격 조절
                time.sleep(0.1)
            
            print(f"✅ 의안발의 목록 조회 성공: {len(bills)}개")
            return bills
                
        except Exception as e:
            print(f"❌ 의안발의 목록 조회 오류: {e}")
            return []
    
    def get_recent_bills(self, days: int = 30) -> List[Dict]:
        """최근 N일간의 의안발의 조회"""
        try:
            # 최근 의안발의 조회 (실제 API 문서에 따라 수정 필요)
            params = {
                'numOfRows': 50,
                'pageNo': 1,
                'days': days
            }
            
            result = self._make_request('getRecentBills', params)
            
            if result:
                bills = []
                for item in result.get('items', []):
                    bill = {
                        'bill_id': item.get('billId', ''),
                        'bill_name': item.get('billName', ''),
                        'bill_kind': item.get('billKind', ''),
                        'proposer': item.get('proposer', ''),
                        'proposer_party': item.get('proposerParty', ''),
                        'propose_date': item.get('proposeDate', ''),
                        'status': item.get('status', ''),
                        'summary': item.get('summary', ''),
                        'url': item.get('url', '')
                    }
                    bills.append(bill)
                
                print(f"✅ 최근 {days}일간 의안발의 조회 성공: {len(bills)}개")
                return bills
            else:
                print("❌ 최근 의안발의 조회 실패")
                return []
                
        except Exception as e:
            print(f"❌ 최근 의안발의 조회 오류: {e}")
            return []
    
    def get_member_bills(self, member_id: str) -> List[Dict]:
        """특정 의원의 의안발의 조회"""
        try:
            params = {
                'numOfRows': 100,
                'pageNo': 1,
                'memberId': member_id
            }
            
            result = self._make_request('getMemberBills', params)
            
            if result:
                bills = []
                for item in result.get('items', []):
                    bill = {
                        'bill_id': item.get('billId', ''),
                        'bill_name': item.get('billName', ''),
                        'bill_kind': item.get('billKind', ''),
                        'proposer': item.get('proposer', ''),
                        'proposer_party': item.get('proposerParty', ''),
                        'propose_date': item.get('proposeDate', ''),
                        'status': item.get('status', ''),
                        'summary': item.get('summary', ''),
                        'url': item.get('url', '')
                    }
                    bills.append(bill)
                
                print(f"✅ 의원 {member_id}의 의안발의 조회 성공: {len(bills)}개")
                return bills
            else:
                print(f"❌ 의원 {member_id}의 의안발의 조회 실패")
                return []
                
        except Exception as e:
            print(f"❌ 의원 {member_id}의 의안발의 조회 오류: {e}")
            return []
    
    def _get_manual_party_info(self, name: str) -> str:
        """수동 정당 정보 매핑 (API에서 정당 정보를 제공하지 않음)"""
        party_mapping = {
            # 더불어민주당
            '전현희': '더불어민주당',
            '추미애': '더불어민주당',
            '김병기': '더불어민주당',
            '정태호': '더불어민주당',
            '강득구': '더불어민주당',
            '강선영': '더불어민주당',
            '강선우': '더불어민주당',
            '강승규': '더불어민주당',
            '강준현': '더불어민주당',
            '고동진': '더불어민주당',
            
            # 국민의힘
            '강대식': '국민의힘',
            '강명구': '국민의힘',
            '강민국': '국민의힘',
            
            # 조국혁신당
            '강경숙': '조국혁신당',
            
            # 기타 정당들 (필요시 추가)
        }
        return party_mapping.get(name, '')

# 전역 인스턴스
assembly_api = AssemblyAPIService()
