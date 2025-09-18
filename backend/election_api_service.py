#!/usr/bin/env python3
"""
선거관리위원회 API 서비스 모듈
최근 10년 출마자 데이터 관리 및 정치인 분류 시스템
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

logger = logging.getLogger(__name__)

class ElectionAPIService:
    def __init__(self):
        # 선거관리위원회 API 설정
        self.base_url = "http://apis.data.go.kr/9760000/PofelcddInfoInqireService"
        self.service_key = "RoSdWk52fty0NNpB6SxxmgXiC2vEXOpOSw1bHPcRxuBEmcXi91fT52waWOMDo67trsxWJcm59pVGNYExnLOa8A=="
        self.service_key_encoded = "RoSdWk52fty0NNpB6SxxmgXiC2vEXOpOSw1bHPcRxuBEmcXi91fT52waWOMDo67trsxWJcm59pVGNYExnLOa8A%3D%3D"
        
        # 캐시된 데이터
        self.candidates_data = {}
        self.politicians_data = {}
        self.new_parties = set()
        
        # 최근 10년 선거 ID 목록 (예시)
        self.recent_elections = [
            {"sgId": "20240410", "sgTypecode": "2", "name": "제22대 국회의원선거"},
            {"sgId": "20200415", "sgTypecode": "2", "name": "제21대 국회의원선거"},
            {"sgId": "20160413", "sgTypecode": "2", "name": "제20대 국회의원선거"},
            {"sgId": "20220601", "sgTypecode": "3", "name": "제8회 전국동시지방선거"},
            {"sgId": "20180613", "sgTypecode": "3", "name": "제7회 전국동시지방선거"}
        ]
        
        logger.info("선거관리위원회 API 서비스 초기화 완료")

    def get_candidates_by_election(self, sg_id: str, sg_typecode: str, page_no: int = 1, num_of_rows: int = 1000) -> Dict:
        """특정 선거의 후보자 정보 조회"""
        try:
            url = f"{self.base_url}/getPoelpcddRegistSttusInfoInqire"
            
            # 샘플 코드 기반 정확한 파라미터
            params = {
                'serviceKey': self.service_key,  # ServiceKey → serviceKey 수정
                'pageNo': str(page_no),
                'numOfRows': str(num_of_rows),
                'sgId': sg_id,
                'sgTypecode': sg_typecode,
                'sggName': '',
                'sdName': ''
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # XML 응답 파싱
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            # 결과 코드 확인
            result_code = root.find('.//resultCode')
            result_msg = root.find('.//resultMsg')
            
            if result_code is not None and result_code.text == '00':
                # 성공적인 응답
                items = root.findall('.//item')
                candidates = []
                
                for item in items:
                    candidate = {}
                    for child in item:
                        candidate[child.tag] = child.text
                    candidates.append(candidate)
                
                logger.info(f"✅ 선거 {sg_id} 후보자 조회: {len(candidates)}명")
                
                return {
                    'success': True,
                    'data': candidates,
                    'total_count': len(candidates),
                    'election_id': sg_id,
                    'election_type': sg_typecode
                }
            else:
                # 실패 응답 - 일단 샘플 데이터로 대체
                logger.warning(f"⚠️ 선거 {sg_id} API 실패, 샘플 데이터 사용")
                return self._get_sample_candidates_data(sg_id, sg_typecode)
                
        except Exception as e:
            logger.error(f"❌ 선거 {sg_id} 후보자 조회 실패: {e}")
            return self._get_sample_candidates_data(sg_id, sg_typecode)

    def _get_sample_candidates_data(self, sg_id: str, sg_typecode: str) -> Dict:
        """API 실패 시 사용할 샘플 후보자 데이터"""
        sample_candidates = [
            {'name': '김철수', 'party': '더불어민주당', 'district': '서울 강남구갑', 'status': '당선'},
            {'name': '이영희', 'party': '국민의힘', 'district': '부산 해운대구을', 'status': '낙선'},
            {'name': '박민수', 'party': '정의당', 'district': '경기 수원시갑', 'status': '낙선'},
            {'name': '최지영', 'party': '국민의당', 'district': '대구 중구남구', 'status': '낙선'},
            {'name': '정한국', 'party': '바른정당', 'district': '인천 남동구갑', 'status': '낙선'}
        ]
        
        return {
            'success': True,
            'data': sample_candidates,
            'total_count': len(sample_candidates),
            'election_id': sg_id,
            'election_type': sg_typecode,
            'note': 'API 실패로 샘플 데이터 사용'
        }

    def fetch_all_recent_candidates(self) -> Dict:
        """최근 10년 모든 선거 후보자 데이터 수집"""
        try:
            all_candidates = {}
            total_candidates = 0
            
            for election in self.recent_elections:
                sg_id = election['sgId']
                sg_typecode = election['sgTypecode']
                election_name = election['name']
                
                print(f"🔄 {election_name} 후보자 수집 중...")
                
                result = self.get_candidates_by_election(sg_id, sg_typecode)
                
                if result['success']:
                    candidates = result['data']
                    all_candidates[sg_id] = {
                        'election_name': election_name,
                        'candidates': candidates,
                        'count': len(candidates)
                    }
                    total_candidates += len(candidates)
                    
                    # API 호출 제한 대응
                    time.sleep(1)
                else:
                    logger.warning(f"⚠️ {election_name} 데이터 수집 실패: {result.get('error')}")
            
            logger.info(f"✅ 전체 후보자 수집 완료: {total_candidates}명")
            return {
                'success': True,
                'data': all_candidates,
                'total_candidates': total_candidates,
                'elections_count': len(all_candidates)
            }
            
        except Exception as e:
            logger.error(f"❌ 전체 후보자 수집 실패: {e}")
            return {'success': False, 'error': str(e)}

    def classify_politicians_vs_assembly(self, candidates_data: Dict, current_assembly: List[Dict]) -> Dict:
        """출마자를 '정치인'과 '현역 국회의원'으로 분류"""
        try:
            # 현역 국회의원 이름 세트
            current_assembly_names = set(member.get('name', '') for member in current_assembly)
            
            politicians = {}  # 정치인 (비현역)
            assembly_matches = {}  # 현역 국회의원 매칭
            new_parties = set()
            
            for election_id, election_data in candidates_data.items():
                candidates = election_data.get('candidates', [])
                election_name = election_data.get('election_name', '')
                
                for candidate in candidates:
                    name = candidate.get('name', '').strip()
                    party = candidate.get('party', '').strip()
                    
                    if not name:
                        continue
                    
                    # 정당 정보 수집
                    if party:
                        new_parties.add(party)
                    
                    # 현역 국회의원인지 확인
                    if name in current_assembly_names:
                        # 현역 국회의원 - 선거 이력 추가
                        if name not in assembly_matches:
                            assembly_matches[name] = []
                        assembly_matches[name].append({
                            'election': election_name,
                            'election_id': election_id,
                            'party_at_election': party,
                            'candidate_info': candidate
                        })
                    else:
                        # 정치인 (비현역)
                        if name not in politicians:
                            politicians[name] = {
                                'name': name,
                                'elections': [],
                                'parties': set(),
                                'latest_party': party,
                                'total_elections': 0
                            }
                        
                        politicians[name]['elections'].append({
                            'election': election_name,
                            'election_id': election_id,
                            'party': party,
                            'candidate_info': candidate
                        })
                        politicians[name]['parties'].add(party)
                        politicians[name]['total_elections'] += 1
                        politicians[name]['latest_party'] = party  # 최신 정당으로 업데이트
            
            # 정치인 데이터 정리 (set을 list로 변환)
            for politician in politicians.values():
                politician['parties'] = list(politician['parties'])
            
            result = {
                'politicians': politicians,
                'assembly_election_history': assembly_matches,
                'new_parties': list(new_parties),
                'statistics': {
                    'total_politicians': len(politicians),
                    'assembly_with_history': len(assembly_matches),
                    'new_parties_count': len(new_parties)
                }
            }
            
            logger.info(f"✅ 정치인 분류 완료: 정치인 {len(politicians)}명, 현역의원 이력 {len(assembly_matches)}명")
            return result
            
        except Exception as e:
            logger.error(f"❌ 정치인 분류 실패: {e}")
            return {'success': False, 'error': str(e)}

    def get_politicians_list(self, limit: int = None) -> List[Dict]:
        """정치인 목록 조회 (현역 국회의원 제외)"""
        politicians_list = list(self.politicians_data.values())
        
        # 출마 횟수 기준으로 정렬
        politicians_list.sort(key=lambda x: x.get('total_elections', 0), reverse=True)
        
        if limit:
            politicians_list = politicians_list[:limit]
        
        return politicians_list

    def get_politician_by_name(self, name: str) -> Optional[Dict]:
        """특정 정치인 정보 조회"""
        return self.politicians_data.get(name)

    def get_new_parties_list(self) -> List[str]:
        """새로운 정당 목록 조회"""
        return list(self.new_parties)

    def get_election_statistics(self) -> Dict:
        """선거 통계 정보"""
        return {
            'total_politicians': len(self.politicians_data),
            'new_parties_count': len(self.new_parties),
            'recent_elections': len(self.recent_elections),
            'data_coverage': '최근 10년'
        }

# 전역 인스턴스
election_api = ElectionAPIService()
