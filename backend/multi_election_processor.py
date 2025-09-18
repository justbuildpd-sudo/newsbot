#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
다중 선거 데이터 처리기
여러 선거의 LOD 데이터를 처리하여 통합 정치인 데이터베이스를 구축합니다.
"""

import xml.etree.ElementTree as ET
import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin
import logging
from datetime import datetime
import os

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_election_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MultiElectionProcessor:
    """다중 선거 데이터 처리 클래스"""
    
    def __init__(self):
        self.namespaces = {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'no': 'http://data.nec.go.kr/ontology/',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'foaf': 'http://xmlns.com/foaf/0.1/'
        }
        self.elections = []
        self.all_candidates = []
        
    def analyze_election_file(self, file_path: str) -> Dict:
        """선거 파일을 분석하여 기본 정보를 추출합니다."""
        logger.info(f"선거 파일 분석 시작: {file_path}")
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # 선거 정보 추출
            election_element = root.find('.//no:Election', self.namespaces)
            
            if election_element is None:
                logger.warning("선거 정보를 찾을 수 없습니다")
                return {}
            
            info = {}
            
            # 선거 ID
            election_id_elem = election_element.find('.//no:electionId', self.namespaces)
            if election_id_elem is not None:
                info['election_id'] = election_id_elem.text
            
            # 선거명
            name_elem = election_element.find('.//no:name', self.namespaces)
            if name_elem is not None:
                info['name'] = name_elem.text
            
            # 선거일
            election_day_elem = election_element.find('.//no:electionDay', self.namespaces)
            if election_day_elem is not None:
                info['election_day'] = election_day_elem.text
            
            # 선거 타입
            election_type_elem = election_element.find('.//no:hasElectionType', self.namespaces)
            if election_type_elem is not None:
                type_resource = election_type_elem.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
                if type_resource:
                    info['election_type'] = type_resource.split('_')[-1]
            
            # 후보자 URI들 추출
            candidate_elements = root.findall('.//no:hasCandidate', self.namespaces)
            candidate_uris = []
            
            for element in candidate_elements:
                resource = element.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
                if resource:
                    candidate_uris.append(resource)
            
            info['candidate_uris'] = candidate_uris
            info['candidate_count'] = len(candidate_uris)
            
            # 선거구 URI들 추출
            district_elements = root.findall('.//no:hasElectionDistrict', self.namespaces)
            district_uris = []
            
            for element in district_elements:
                resource = element.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
                if resource:
                    district_uris.append(resource)
            
            info['district_uris'] = district_uris
            info['district_count'] = len(district_uris)
            
            logger.info(f"선거 분석 완료: {info.get('name', 'Unknown')} - 후보자 {info['candidate_count']}명")
            return info
            
        except Exception as e:
            logger.error(f"선거 파일 분석 오류: {str(e)}")
            return {}
    
    def fetch_candidate_details(self, candidate_uris: List[str], election_info: Dict, max_requests: int = None) -> List[Dict]:
        """후보자 상세 정보를 가져옵니다."""
        if max_requests is None:
            max_requests = len(candidate_uris)
        
        logger.info(f"후보자 상세 정보 수집 시작: {min(max_requests, len(candidate_uris))}명")
        
        candidates = []
        failed_requests = []
        
        for i, uri in enumerate(candidate_uris[:max_requests]):
            try:
                logger.info(f"처리 중: {i+1}/{min(max_requests, len(candidate_uris))} - {uri}")
                
                # RDF 형식으로 요청
                rdf_url = uri.replace('/resource/', '/data/') + "?output=rdfxml"
                
                response = requests.get(rdf_url, timeout=30)
                
                if response.status_code == 200:
                    candidate_data = self._parse_candidate_rdf(response.content, uri, election_info)
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
            'election_info': election_info
        }
    
    def _parse_candidate_rdf(self, rdf_content: bytes, uri: str, election_info: Dict) -> Optional[Dict]:
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
                    'election_id': election_info.get('election_id'),
                    'election_name': election_info.get('name'),
                    'election_day': election_info.get('election_day'),
                    'election_type': election_info.get('election_type')
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
                    candidate_data['party_resource'] = party_resource
                    candidate_data['party'] = self._fetch_party_name(party_resource)
            
            # 선거구 정보 추출
            district_resource_elem = root.find('.//no:hasElectionDistrict', self.namespaces)
            if district_resource_elem is not None:
                district_resource = district_resource_elem.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
                if district_resource:
                    candidate_data['district_resource'] = district_resource
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
            
            birthday_elem = root.find('.//no:birthday', self.namespaces)
            if birthday_elem is not None and birthday_elem.text:
                candidate_data['birthday'] = birthday_elem.text.strip()
            
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
    
    def process_election(self, file_path: str, max_candidates: int = None) -> Dict:
        """단일 선거 데이터를 처리합니다."""
        logger.info(f"=== 선거 데이터 처리 시작: {file_path} ===")
        
        # 1. 선거 파일 분석
        election_info = self.analyze_election_file(file_path)
        
        if not election_info:
            logger.error("선거 정보 추출 실패")
            return None
        
        # 2. 후보자 상세 정보 수집
        candidate_results = self.fetch_candidate_details(
            election_info['candidate_uris'], 
            election_info,
            max_candidates
        )
        
        # 3. 결과 정리
        result = {
            'election_info': election_info,
            'candidates': candidate_results['candidates'],
            'statistics': {
                'total_candidates': election_info['candidate_count'],
                'processed_candidates': candidate_results['success_count'],
                'failed_candidates': candidate_results['failure_count'],
                'success_rate': (candidate_results['success_count'] / election_info['candidate_count']) * 100 if election_info['candidate_count'] > 0 else 0,
                'total_districts': election_info['district_count']
            },
            'processing_timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"=== 선거 데이터 처리 완료: {election_info.get('name', 'Unknown')} ===")
        return result
    
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
    logger.info("=== 다중 선거 데이터 처리기 시작 ===")
    
    # 20대 시·도의회의원선거 처리
    processor = MultiElectionProcessor()
    
    election_file = "/Users/hopidaay/Downloads/Elec_520180613"
    
    try:
        # 선거 데이터 처리 (전체 1,886명)
        logger.info("🔍 제7회 전국동시지방선거 시·도의회의원선거 처리 (전체)")
        result = processor.process_election(election_file, max_candidates=1886)
        
        if result:
            # 결과 저장
            processor.save_results(result, "metro_council_election_full.json")
            
            # 결과 요약
            stats = result['statistics']
            logger.info("=== 처리 결과 요약 ===")
            logger.info(f"📊 선거: {result['election_info']['name']}")
            logger.info(f"📊 전체 후보자: {stats['total_candidates']}명")
            logger.info(f"📊 처리 완료: {stats['processed_candidates']}명")
            logger.info(f"📊 성공률: {stats['success_rate']:.1f}%")
            logger.info(f"📊 선거구: {stats['total_districts']}개")
            
            return True
        else:
            logger.error("선거 데이터 처리 실패")
            return False
        
    except Exception as e:
        logger.error(f"처리 중 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ 다중 선거 데이터 처리 완료")
    else:
        logger.error("❌ 다중 선거 데이터 처리 실패")
