#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
계층적 LOD 처리기
상위 선거에서 하위 선거 ID를 추출하고 각 하위 선거의 후보자 데이터를 수집합니다.
"""

import xml.etree.ElementTree as ET
import requests
import json
import time
from typing import Dict, List, Optional
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hierarchical_lod_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HierarchicalLODProcessor:
    """계층적 LOD 처리 클래스"""
    
    def __init__(self):
        self.namespaces = {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'no': 'http://data.nec.go.kr/ontology/',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'foaf': 'http://xmlns.com/foaf/0.1/'
        }
    
    def extract_sub_elections(self, file_path: str) -> Dict:
        """상위 선거 파일에서 하위 선거 ID들을 추출합니다."""
        logger.info(f"상위 선거 파일 분석: {file_path}")
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # 선거 정보 추출
            election_element = root.find('.//no:Election', self.namespaces)
            
            if election_element is None:
                logger.warning("선거 정보를 찾을 수 없습니다")
                return {}
            
            # 기본 정보
            election_info = {}
            
            name_elem = election_element.find('.//no:name', self.namespaces)
            if name_elem is not None:
                election_info['name'] = name_elem.text
            
            election_day_elem = election_element.find('.//no:electionDay', self.namespaces)
            if election_day_elem is not None:
                election_info['election_day'] = election_day_elem.text
            
            # 하위 선거들 추출
            sub_election_elements = election_element.findall('.//no:lowerPartElection', self.namespaces)
            sub_elections = []
            
            for element in sub_election_elements:
                resource = element.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
                if resource:
                    sub_election_id = resource.split('/')[-1]  # Elec_220200415 형태
                    sub_elections.append(sub_election_id)
            
            election_info['sub_elections'] = sub_elections
            election_info['sub_elections_count'] = len(sub_elections)
            
            logger.info(f"상위 선거 분석 완료: {election_info.get('name')} - {len(sub_elections)}개 하위 선거")
            return election_info
            
        except Exception as e:
            logger.error(f"상위 선거 파일 분석 오류: {str(e)}")
            return {}
    
    def get_sub_election_candidates(self, sub_election_id: str) -> List[str]:
        """하위 선거의 후보자 URI들을 가져옵니다."""
        try:
            sub_election_url = f"http://data.nec.go.kr/data/{sub_election_id}?output=rdfxml"
            
            response = requests.get(sub_election_url, timeout=30)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                # 후보자 URI들 추출
                candidate_elements = root.findall('.//no:hasCandidate', self.namespaces)
                candidate_uris = []
                
                for element in candidate_elements:
                    resource = element.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
                    if resource:
                        candidate_uris.append(resource)
                
                logger.info(f"✅ {sub_election_id}: {len(candidate_uris)}명 후보자 URI 추출")
                return candidate_uris
            else:
                logger.warning(f"❌ {sub_election_id}: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ {sub_election_id} 요청 실패: {str(e)}")
            return []
    
    def fetch_candidate_details(self, candidate_uris: List[str], election_info: Dict, sub_election_id: str) -> List[Dict]:
        """후보자 상세 정보를 가져옵니다."""
        logger.info(f"후보자 상세 정보 수집 시작: {len(candidate_uris)}명 ({sub_election_id})")
        
        candidates = []
        failed_requests = []
        
        for i, uri in enumerate(candidate_uris):
            try:
                logger.info(f"처리 중: {i+1}/{len(candidate_uris)} - {uri}")
                
                # RDF 형식으로 요청
                rdf_url = uri.replace('/resource/', '/data/') + "?output=rdfxml"
                
                response = requests.get(rdf_url, timeout=30)
                
                if response.status_code == 200:
                    candidate_data = self._parse_candidate_rdf(response.content, uri, election_info, sub_election_id)
                    if candidate_data:
                        candidates.append(candidate_data)
                        logger.info(f"✅ 성공: {candidate_data.get('name', 'Unknown')}")
                    else:
                        logger.warning(f"❌ 데이터 파싱 실패: {uri}")
                        failed_requests.append(uri)
                else:
                    logger.warning(f"❌ HTTP 오류 {response.status_code}: {uri}")
                    failed_requests.append(uri)
                
                # 요청 간격 조절 (서버 부하 방지)
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ 요청 실패 {uri}: {str(e)}")
                failed_requests.append(uri)
                continue
        
        logger.info(f"상세 정보 수집 완료 - 성공: {len(candidates)}명, 실패: {len(failed_requests)}명")
        
        return {
            'candidates': candidates,
            'failed_requests': failed_requests,
            'success_count': len(candidates),
            'failure_count': len(failed_requests),
            'sub_election_id': sub_election_id,
            'election_info': election_info
        }
    
    def _parse_candidate_rdf(self, rdf_content: bytes, uri: str, election_info: Dict, sub_election_id: str) -> Optional[Dict]:
        """후보자 RDF 데이터를 파싱합니다."""
        try:
            root = ET.fromstring(rdf_content)
            
            # 후보자 정보 추출
            candidate_data = {
                'uri': uri,
                'name': None,
                'party': None,
                'district': None,
                'vote_count': None,
                'vote_rate': None,
                'is_elected': False,
                'election_symbol': None,
                'age': None,
                'gender': None,
                'birthday': None,
                'education': None,
                'career': None,
                'occupation': None,
                'candidate_type': None,
                'election_info': {
                    'parent_election_name': election_info.get('name'),
                    'parent_election_day': election_info.get('election_day'),
                    'sub_election_id': sub_election_id,
                    'election_type': sub_election_id.split('_')[0][-1] if '_' in sub_election_id else None
                },
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            # 이름 추출
            name_patterns = [
                './/foaf:name',
                './/no:name', 
                './/rdfs:label'
            ]
            
            for pattern in name_patterns:
                name_elem = root.find(pattern, self.namespaces)
                if name_elem is not None and name_elem.text:
                    candidate_data['name'] = name_elem.text.strip()
                    break
            
            # 정당 정보 추출
            party_resource_elem = root.find('.//no:positionPoliticalParty', self.namespaces)
            if party_resource_elem is not None:
                party_resource = party_resource_elem.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
                if party_resource:
                    candidate_data['party'] = self._fetch_party_name(party_resource)
            
            # 선거구 정보 추출
            district_resource_elem = root.find('.//no:hasElectionDistrict', self.namespaces)
            if district_resource_elem is not None:
                district_resource = district_resource_elem.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
                if district_resource:
                    candidate_data['district'] = self._fetch_district_name(district_resource)
            
            # 득표수 추출
            vote_count_elem = root.find('.//no:pollingScoreCount', self.namespaces)
            if vote_count_elem is not None and vote_count_elem.text:
                try:
                    candidate_data['vote_count'] = int(vote_count_elem.text.strip())
                except ValueError:
                    pass
            
            # 득표율 추출
            vote_rate_elem = root.find('.//no:pollingScoreRate', self.namespaces)
            if vote_rate_elem is not None and vote_rate_elem.text:
                try:
                    candidate_data['vote_rate'] = float(vote_rate_elem.text.strip())
                except ValueError:
                    pass
            
            # 당선 여부 추출
            win_candidate_elem = root.find('.//no:WinCandidate', self.namespaces)
            if win_candidate_elem is not None:
                candidate_data['is_elected'] = True
                candidate_data['candidate_type'] = 'WinCandidate'
            else:
                candidate_elem = root.find('.//no:Candidate', self.namespaces)
                if candidate_elem is not None:
                    candidate_data['is_elected'] = False
                    candidate_data['candidate_type'] = 'Candidate'
            
            # 기타 정보 추출
            age_elem = root.find('.//no:age', self.namespaces)
            if age_elem is not None and age_elem.text:
                try:
                    candidate_data['age'] = int(age_elem.text.strip())
                except ValueError:
                    pass
            
            gender_elem = root.find('.//no:sexDistinction', self.namespaces)
            if gender_elem is not None and gender_elem.text:
                candidate_data['gender'] = gender_elem.text.strip()
            
            education_elem = root.find('.//no:academicCareerDetail', self.namespaces)
            if education_elem is not None and education_elem.text:
                candidate_data['education'] = education_elem.text.strip()
            
            career_elem = root.find('.//no:career', self.namespaces)
            if career_elem is not None and career_elem.text:
                candidate_data['career'] = career_elem.text.strip()
            
            occupation_elem = root.find('.//no:occupationDetail', self.namespaces)
            if occupation_elem is not None and occupation_elem.text:
                candidate_data['occupation'] = occupation_elem.text.strip()
            
            return candidate_data
            
        except Exception as e:
            logger.error(f"RDF 파싱 오류 {uri}: {str(e)}")
            return None
    
    def _fetch_party_name(self, party_resource: str) -> Optional[str]:
        """정당 리소스에서 정당명을 가져옵니다."""
        try:
            party_rdf_url = party_resource.replace('/resource/', '/data/') + "?output=rdfxml"
            response = requests.get(party_rdf_url, timeout=10)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                name_patterns = [
                    './/no:name',
                    './/rdfs:label', 
                    './/foaf:name'
                ]
                
                for pattern in name_patterns:
                    name_elem = root.find(pattern, self.namespaces)
                    if name_elem is not None and name_elem.text:
                        return name_elem.text.strip()
                        
        except Exception as e:
            logger.warning(f"정당명 조회 실패 {party_resource}: {str(e)}")
        
        return None
    
    def _fetch_district_name(self, district_resource: str) -> Optional[str]:
        """선거구 리소스에서 선거구명을 가져옵니다."""
        try:
            district_rdf_url = district_resource.replace('/resource/', '/data/') + "?output=rdfxml"
            response = requests.get(district_rdf_url, timeout=10)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                name_patterns = [
                    './/no:name',
                    './/rdfs:label',
                    './/no:districtName'
                ]
                
                for pattern in name_patterns:
                    name_elem = root.find(pattern, self.namespaces)
                    if name_elem is not None and name_elem.text:
                        return name_elem.text.strip()
                        
        except Exception as e:
            logger.warning(f"선거구명 조회 실패 {district_resource}: {str(e)}")
        
        return None
    
    def process_hierarchical_election(self, file_path: str, target_sub_elections: List[str] = None) -> Dict:
        """계층적 선거 데이터를 처리합니다."""
        logger.info(f"=== 계층적 선거 처리 시작: {file_path} ===")
        
        # 1. 상위 선거에서 하위 선거 ID들 추출
        election_info = self.extract_sub_elections(file_path)
        
        if not election_info:
            logger.error("상위 선거 정보 추출 실패")
            return None
        
        # 2. 처리할 하위 선거 결정
        sub_elections = election_info.get('sub_elections', [])
        
        if target_sub_elections:
            # 특정 하위 선거만 처리
            sub_elections = [se for se in sub_elections if se in target_sub_elections]
        
        logger.info(f"처리할 하위 선거: {sub_elections}")
        
        # 3. 각 하위 선거의 후보자 데이터 수집
        all_candidates = []
        sub_election_results = {}
        
        for sub_election_id in sub_elections:
            logger.info(f"🔄 하위 선거 처리: {sub_election_id}")
            
            # 후보자 URI들 가져오기
            candidate_uris = self.get_sub_election_candidates(sub_election_id)
            
            if candidate_uris:
                # 후보자 상세 정보 수집
                result = self.fetch_candidate_details(candidate_uris, election_info, sub_election_id)
                
                all_candidates.extend(result['candidates'])
                sub_election_results[sub_election_id] = result
            else:
                logger.warning(f"⚠️ {sub_election_id}: 후보자 없음")
        
        # 4. 결과 정리
        final_result = {
            'parent_election_info': election_info,
            'sub_election_results': sub_election_results,
            'all_candidates': all_candidates,
            'statistics': {
                'total_candidates': len(all_candidates),
                'sub_elections_processed': len(sub_election_results),
                'success_rate': 100.0 if all_candidates else 0.0
            },
            'processing_timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"=== 계층적 선거 처리 완료: {election_info.get('name')} ===")
        logger.info(f"📊 총 후보자: {len(all_candidates)}명")
        
        return final_result
    
    def save_results(self, data: Dict, filename: str):
        """결과를 JSON 파일로 저장합니다."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"결과 저장 완료: {filename}")
        except Exception as e:
            logger.error(f"파일 저장 오류 {filename}: {str(e)}")
            raise

def main():
    """메인 실행 함수"""
    logger.info("=== 계층적 LOD 처리기 시작 ===")
    
    processor = HierarchicalLODProcessor()
    
    # 제6회 전국동시지방선거 처리
    logger.info("🔍 제6회 전국동시지방선거 처리")
    result_6th = processor.process_hierarchical_election(
        "/Users/hopidaay/Downloads/Elec_20140604"
    )
    
    if result_6th:
        processor.save_results(result_6th, "6th_local_election_full.json")
    
    # 결과 요약
    total_candidates = 0
    if result_6th:
        total_candidates += result_6th['statistics']['total_candidates']
    
    logger.info("=== 전체 처리 결과 ===")
    logger.info(f"📊 제6회 전국동시지방선거: {result_6th['statistics']['total_candidates'] if result_6th else 0}명")
    logger.info(f"📊 총 추가 후보자: {total_candidates}명")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ 계층적 LOD 처리 완료")
    else:
        logger.error("❌ 계층적 LOD 처리 실패")
