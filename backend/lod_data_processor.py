#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOD 데이터 처리기
제22대 국회의원선거 LOD 데이터에서 후보자 정보를 추출하고 처리합니다.
"""

import xml.etree.ElementTree as ET
import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lod_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LODDataProcessor:
    """LOD 데이터 처리 클래스"""
    
    def __init__(self, lod_file_path: str):
        self.lod_file_path = lod_file_path
        self.namespaces = {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'no': 'http://data.nec.go.kr/ontology/',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'
        }
        self.candidates = []
        self.election_districts = []
        self.resign_candidates = []
        
    def parse_lod_file(self) -> Dict:
        """LOD XML 파일을 파싱하여 데이터를 추출합니다."""
        logger.info(f"LOD 파일 파싱 시작: {self.lod_file_path}")
        
        try:
            tree = ET.parse(self.lod_file_path)
            root = tree.getroot()
            
            # 선거 정보 추출
            election_info = self._extract_election_info(root)
            
            # 후보자 URI 추출
            candidate_uris = self._extract_candidate_uris(root)
            
            # 선거구 URI 추출
            district_uris = self._extract_district_uris(root)
            
            # 사퇴 후보자 URI 추출
            resign_uris = self._extract_resign_candidate_uris(root)
            
            result = {
                'election_info': election_info,
                'candidate_uris': candidate_uris,
                'district_uris': district_uris,
                'resign_candidate_uris': resign_uris,
                'total_candidates': len(candidate_uris),
                'total_districts': len(district_uris),
                'total_resign_candidates': len(resign_uris),
                'parsing_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"파싱 완료 - 후보자: {len(candidate_uris)}명, 선거구: {len(district_uris)}개, 사퇴자: {len(resign_uris)}명")
            return result
            
        except Exception as e:
            logger.error(f"LOD 파일 파싱 오류: {str(e)}")
            raise
    
    def _extract_election_info(self, root) -> Dict:
        """선거 기본 정보를 추출합니다."""
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
        
        # 정렬 순서
        sort_order_elem = election_element.find('.//no:sortOrder', self.namespaces)
        if sort_order_elem is not None:
            info['sort_order'] = sort_order_elem.text
        
        logger.info(f"선거 정보 추출 완료: {info.get('name', 'Unknown')}")
        return info
    
    def _extract_candidate_uris(self, root) -> List[str]:
        """후보자 URI들을 추출합니다."""
        candidate_elements = root.findall('.//no:hasCandidate', self.namespaces)
        uris = []
        
        for element in candidate_elements:
            resource = element.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
            if resource:
                uris.append(resource)
        
        logger.info(f"후보자 URI {len(uris)}개 추출 완료")
        return uris
    
    def _extract_district_uris(self, root) -> List[str]:
        """선거구 URI들을 추출합니다."""
        district_elements = root.findall('.//no:hasElectionDistrict', self.namespaces)
        uris = []
        
        for element in district_elements:
            resource = element.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
            if resource:
                uris.append(resource)
        
        logger.info(f"선거구 URI {len(uris)}개 추출 완료")
        return uris
    
    def _extract_resign_candidate_uris(self, root) -> List[str]:
        """사퇴 후보자 URI들을 추출합니다."""
        resign_elements = root.findall('.//no:hasResignCandidate', self.namespaces)
        uris = []
        
        for element in resign_elements:
            resource = element.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
            if resource:
                uris.append(resource)
        
        logger.info(f"사퇴 후보자 URI {len(uris)}개 추출 완료")
        return uris
    
    def fetch_candidate_details(self, candidate_uris: List[str], max_requests: int = 10) -> List[Dict]:
        """후보자 상세 정보를 가져옵니다. (테스트용으로 제한된 수량)"""
        logger.info(f"후보자 상세 정보 수집 시작 (테스트: {max_requests}명)")
        
        candidates = []
        failed_requests = []
        
        for i, uri in enumerate(candidate_uris[:max_requests]):
            try:
                logger.info(f"처리 중: {i+1}/{max_requests} - {uri}")
                
                # RDF 형식으로 요청 (올바른 URL 패턴 사용)
                rdf_url = uri.replace('/resource/', '/data/') + "?output=rdfxml"
                
                response = requests.get(rdf_url, timeout=30)
                
                if response.status_code == 200:
                    candidate_data = self._parse_candidate_rdf(response.content, uri)
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
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ 요청 실패 {uri}: {str(e)}")
                failed_requests.append(uri)
                continue
        
        logger.info(f"상세 정보 수집 완료 - 성공: {len(candidates)}명, 실패: {len(failed_requests)}명")
        
        return {
            'candidates': candidates,
            'failed_requests': failed_requests,
            'success_count': len(candidates),
            'failure_count': len(failed_requests)
        }
    
    def _parse_candidate_rdf(self, rdf_content: bytes, uri: str) -> Optional[Dict]:
        """후보자 RDF 데이터를 파싱합니다."""
        try:
            root = ET.fromstring(rdf_content)
            
            # 후보자 정보 추출 (실제 RDF 구조에 따라 조정 필요)
            candidate_data = {
                'uri': uri,
                'name': None,
                'party': None,
                'district': None,
                'vote_count': None,
                'rank': None,
                'is_elected': False,
                'extraction_timestamp': datetime.now().isoformat()
            }
            
            # 이름 추출 시도
            name_patterns = [
                './/no:candidateName',
                './/no:name', 
                './/rdfs:label',
                './/foaf:name'
            ]
            
            for pattern in name_patterns:
                name_elem = root.find(pattern, self.namespaces)
                if name_elem is not None and name_elem.text:
                    candidate_data['name'] = name_elem.text.strip()
                    break
            
            # 정당 추출 시도
            party_resource_elem = root.find('.//no:positionPoliticalParty', self.namespaces)
            if party_resource_elem is not None:
                party_resource = party_resource_elem.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
                if party_resource:
                    candidate_data['party_resource'] = party_resource
                    # 정당명은 별도 요청으로 가져와야 함
                    candidate_data['party'] = self._fetch_party_name(party_resource)
            
            # 선거구 추출 시도
            district_resource_elem = root.find('.//no:hasElectionDistrict', self.namespaces)
            if district_resource_elem is not None:
                district_resource = district_resource_elem.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
                if district_resource:
                    candidate_data['district_resource'] = district_resource
                    # 선거구명은 별도 요청으로 가져와야 함
                    candidate_data['district'] = self._fetch_district_name(district_resource)
            
            # 득표수 추출 시도
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
            
            # 당선 여부 추출 (WinCandidate 클래스인지 확인)
            candidate_elem = root.find('.//no:WinCandidate', self.namespaces)
            if candidate_elem is not None:
                candidate_data['is_elected'] = True
                candidate_data['candidate_type'] = 'WinCandidate'
            else:
                # 일반 후보자인지 확인
                candidate_elem = root.find('.//no:Candidate', self.namespaces)
                if candidate_elem is not None:
                    candidate_data['is_elected'] = False
                    candidate_data['candidate_type'] = 'Candidate'
            
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
                
                # 정당명 추출 시도
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
                
                # 선거구명 추출 시도
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
    logger.info("=== LOD 데이터 처리 시작 ===")
    
    # LOD 파일 경로
    lod_file = "/Users/hopidaay/Downloads/Elec_220240410"
    
    try:
        # LOD 프로세서 초기화
        processor = LODDataProcessor(lod_file)
        
        # 1단계: LOD 파일 파싱
        logger.info("🔧 1단계: LOD XML 파싱")
        parsing_result = processor.parse_lod_file()
        
        # 파싱 결과 저장
        processor.save_results(parsing_result, "lod_parsing_result.json")
        
        # 2단계: 후보자 상세 정보 수집 (전체 693명)
        logger.info("🔍 2단계: 후보자 상세 정보 수집 (전체)")
        candidate_details = processor.fetch_candidate_details(
            parsing_result['candidate_uris'], 
            max_requests=693
        )
        
        # 상세 정보 저장
        processor.save_results(candidate_details, "candidate_details_full.json")
        
        # 결과 요약
        logger.info("=== 처리 결과 요약 ===")
        logger.info(f"📊 전체 후보자: {parsing_result['total_candidates']}명")
        logger.info(f"📊 전체 선거구: {parsing_result['total_districts']}개")
        logger.info(f"📊 사퇴 후보자: {parsing_result['total_resign_candidates']}명")
        logger.info(f"🎯 전체 수집: {candidate_details['success_count']}명 성공, {candidate_details['failure_count']}명 실패")
        
        return True
        
    except Exception as e:
        logger.error(f"처리 중 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ LOD 데이터 처리 완료")
    else:
        logger.error("❌ LOD 데이터 처리 실패")
