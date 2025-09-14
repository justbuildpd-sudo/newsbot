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
        self.base_url = "https://apis.data.go.kr/9710000/NationalAssemblyInfoService"
        self.api_key = "RoSdWk52fty0NNpB6SxxmgXiC2vEXOpOSw1bHPcRxuBEmcXi91fT52waWOMDo67trsxWJcm59pVGNYExnLOa8A=="
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 3600  # 1시간 캐시
    
    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """API 요청 실행"""
        try:
            url = f"{self.base_url}/{endpoint}"
            params['serviceKey'] = self.api_key
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # XML 파싱
            root = ET.fromstring(response.content)
            
            # 결과 추출
            result = {}
            for item in root.findall('.//item'):
                item_data = {}
                for child in item:
                    item_data[child.tag] = child.text
                result[item.tag] = item_data
            
            return result
            
        except Exception as e:
            print(f"API 요청 오류 ({endpoint}): {e}")
            return None
    
    def get_member_list(self) -> List[Dict]:
        """국회의원 현황 조회"""
        cache_key = "member_list"
        
        # 캐시 확인
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            params = {
                'numOfRows': 1000,
                'pageNo': 1
            }
            
            result = self._make_request('getMemberCurrStateList', params)
            
            if result:
                members = []
                for item in result.get('items', []):
                    member = {
                        'id': item.get('empno', ''),
                        'name': item.get('empNm', ''),
                        'name_hanja': item.get('hanjaNm', ''),
                        'party': item.get('polyNm', ''),
                        'district': item.get('origNm', ''),
                        'committee': item.get('shrtNm', ''),
                        'terms': item.get('reeleGbnNm', ''),
                        'office': item.get('secretNm', ''),
                        'phone': item.get('telno', ''),
                        'email': item.get('email', ''),
                        'website': item.get('homepage', ''),
                        'image_url': item.get('jpgLink', ''),
                        'political_orientation': self._get_political_orientation(item.get('polyNm', '')),
                        'key_issues': self._get_key_issues(item.get('shrtNm', '')),
                        'description': f"{item.get('origNm', '')} 지역구 {item.get('polyNm', '')} 소속",
                        'mention_count': 0,
                        'influence_score': 0
                    }
                    members.append(member)
                
                # 캐시 저장
                self.cache[cache_key] = members
                self.cache_expiry[cache_key] = time.time() + self.cache_duration
                
                print(f"✅ 국회의원 {len(members)}명 데이터 로드 완료")
                return members
            else:
                return []
                
        except Exception as e:
            print(f"❌ 국회의원 목록 조회 오류: {e}")
            return []
    
    def get_member_detail(self, member_id: str) -> Optional[Dict]:
        """국회의원 상세 정보 조회"""
        cache_key = f"member_detail_{member_id}"
        
        # 캐시 확인
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            params = {
                'dept_cd': member_id
            }
            
            result = self._make_request('getMemberDetailInfoList', params)
            
            if result:
                # 캐시 저장
                self.cache[cache_key] = result
                self.cache_expiry[cache_key] = time.time() + self.cache_duration
                
                return result
            else:
                return None
                
        except Exception as e:
            print(f"❌ 국회의원 상세 정보 조회 오류: {e}")
            return None
    
    def get_members_by_party(self, party_name: str) -> List[Dict]:
        """소속정당별 국회의원 목록 조회"""
        try:
            params = {
                'polyNm': party_name,
                'numOfRows': 1000,
                'pageNo': 1
            }
            
            result = self._make_request('getMemberPartyInfoList', params)
            
            if result:
                members = []
                for item in result.get('items', []):
                    member = {
                        'id': item.get('empno', ''),
                        'name': item.get('empNm', ''),
                        'party': item.get('polyNm', ''),
                        'district': item.get('origNm', ''),
                        'committee': item.get('shrtNm', ''),
                        'mention_count': 0,
                        'influence_score': 0
                    }
                    members.append(member)
                
                return members
            else:
                return []
                
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

# 전역 인스턴스
assembly_api = AssemblyAPIService()
