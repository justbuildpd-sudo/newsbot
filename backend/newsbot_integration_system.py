#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NewsBot.kr 통합 시스템
22대 출마자 데이터를 NewsBot.kr에 통합하여 검색 및 팝업 기능을 제공합니다.
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NewsBotIntegrationSystem:
    """NewsBot.kr 통합 시스템 클래스"""
    
    def __init__(self):
        self.current_assembly_members = []  # 현직 국회의원 (298명)
        self.election_candidates = []       # 22대 출마자 (693명)
        self.integrated_politicians = []    # 통합된 정치인 데이터
        self.search_index = {}              # 검색 인덱스
        self.integration_results = {
            'statistics': {},
            'categories': {},
            'search_data': {},
            'popup_data': {}
        }
    
    def load_current_assembly_data(self) -> bool:
        """현직 국회의원 데이터를 로드합니다."""
        file_paths = [
            "enhanced_298_members_with_contact.json",
            "updated_298_current_assembly.json",
            "final_298_current_assembly.json"
        ]
        
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        self.current_assembly_members = data
                    elif isinstance(data, dict) and 'members' in data:
                        self.current_assembly_members = data['members']
                    
                    logger.info(f"✅ 현직 국회의원 데이터 로드 완료: {len(self.current_assembly_members)}명 ({file_path})")
                    return True
                    
            except Exception as e:
                logger.warning(f"❌ {file_path} 로드 실패: {str(e)}")
                continue
        
        logger.error("❌ 현직 국회의원 데이터를 로드할 수 없습니다")
        return False
    
    def load_election_candidates_data(self) -> bool:
        """22대 출마자 데이터를 로드합니다."""
        try:
            with open("politician_classification_results.json", 'r', encoding='utf-8') as f:
                classification_data = json.load(f)
            
            # 모든 후보자 (당선자 + 낙선자)
            winners = classification_data.get('current_assembly_members', [])
            losers = classification_data.get('former_politicians', [])
            
            self.election_candidates = winners + losers
            
            logger.info(f"✅ 22대 출마자 데이터 로드 완료: {len(self.election_candidates)}명")
            logger.info(f"   - 당선자: {len(winners)}명, 낙선자: {len(losers)}명")
            return True
            
        except Exception as e:
            logger.error(f"❌ 22대 출마자 데이터 로드 실패: {str(e)}")
            return False
    
    def normalize_politician_data(self, politician: Dict, category: str) -> Dict:
        """정치인 데이터를 표준화합니다."""
        normalized = {
            # 기본 정보
            'id': f"{category}_{politician.get('name', 'unknown')}_{politician.get('district', 'unknown')}",
            'name': politician.get('name', '').strip(),
            'category': category,  # 'current_member' 또는 'election_candidate'
            'party': politician.get('party', '').strip(),
            'district': politician.get('district', '').strip(),
            
            # 개인 정보
            'age': politician.get('age'),
            'gender': politician.get('sexDistinction') or politician.get('gender'),
            'birthday': politician.get('birthday'),
            
            # 학력 및 경력
            'education': politician.get('academicCareerDetail') or politician.get('academic_career'),
            'career': politician.get('career', ''),
            'occupation': politician.get('occupationDetail') or politician.get('occupation'),
            
            # 연락처 정보 (현직 의원만)
            'email': politician.get('email_personal') or politician.get('email'),
            'homepage': politician.get('homepage'),
            'phone': politician.get('phone_office') or politician.get('phone'),
            'office_room': politician.get('office_room'),
            
            # 선거 정보 (22대 출마자만)
            'vote_count': politician.get('vote_count'),
            'vote_rate': politician.get('vote_rate'),
            'is_elected': politician.get('is_elected', False),
            'election_symbol': politician.get('electionSymbol'),
            'candidate_type': politician.get('candidate_type'),
            'vote_grade': politician.get('vote_grade'),
            
            # 정치 경험
            'political_experience': politician.get('political_experience', []),
            'is_incumbent': politician.get('is_incumbent', category == 'current_member'),
            'age_group': politician.get('age_group'),
            
            # 메타 정보
            'data_source': 'current_assembly' if category == 'current_member' else '22nd_election_lod',
            'last_updated': datetime.now().isoformat(),
            
            # 기사 검색 공간 (미리 확보)
            'news_articles': [],  # 추후 정치인+국회의원 기사검색 결과
            'recent_news_count': 0,
            'news_last_updated': None,
            
            # 입법 정보 공간 (현직 의원만, 추후 확장)
            'legislation_info': {} if category == 'current_member' else None
        }
        
        # 빈 값 정리
        for key, value in list(normalized.items()):
            if value == '' or value == 'null' or value is None:
                if key in ['news_articles', 'political_experience']:
                    normalized[key] = []
                elif key in ['recent_news_count']:
                    normalized[key] = 0
                else:
                    normalized[key] = None
        
        return normalized
    
    def build_search_index(self) -> Dict:
        """검색 인덱스를 구축합니다."""
        search_index = {
            'by_name': {},
            'by_party': {},
            'by_district': {},
            'by_category': {
                'current_member': [],
                'election_candidate': []
            },
            'fuzzy_search': []
        }
        
        for politician in self.integrated_politicians:
            name = politician['name']
            party = politician['party']
            district = politician['district']
            category = politician['category']
            
            # 이름별 인덱스
            if name:
                search_index['by_name'][name.lower()] = politician
            
            # 정당별 인덱스
            if party:
                if party not in search_index['by_party']:
                    search_index['by_party'][party] = []
                search_index['by_party'][party].append(politician)
            
            # 선거구별 인덱스
            if district:
                if district not in search_index['by_district']:
                    search_index['by_district'][district] = []
                search_index['by_district'][district].append(politician)
            
            # 카테고리별 인덱스
            search_index['by_category'][category].append(politician)
            
            # 퍼지 검색용 (이름, 정당, 선거구 조합)
            fuzzy_terms = [name, party, district]
            fuzzy_terms = [term for term in fuzzy_terms if term]
            search_index['fuzzy_search'].append({
                'politician': politician,
                'search_terms': ' '.join(fuzzy_terms).lower()
            })
        
        logger.info("✅ 검색 인덱스 구축 완료")
        return search_index
    
    def create_popup_data(self) -> Dict:
        """팝업용 데이터를 생성합니다."""
        popup_data = {}
        
        for politician in self.integrated_politicians:
            politician_id = politician['id']
            
            popup_data[politician_id] = {
                # 기본 정보
                'basic_info': {
                    'name': politician['name'],
                    'category': politician['category'],
                    'party': politician['party'],
                    'district': politician['district'],
                    'age': politician['age'],
                    'gender': politician['gender'],
                    'education': politician['education'],
                    'career': politician['career']
                },
                
                # 선거 정보 (22대 출마자만)
                'election_info': {
                    'vote_count': politician['vote_count'],
                    'vote_rate': politician['vote_rate'],
                    'is_elected': politician['is_elected'],
                    'election_symbol': politician['election_symbol'],
                    'vote_grade': politician['vote_grade']
                } if politician['category'] == 'election_candidate' else None,
                
                # 연락처 정보 (현직 의원만)
                'contact_info': {
                    'email': politician['email'],
                    'homepage': politician['homepage'],
                    'phone': politician['phone'],
                    'office_room': politician['office_room']
                } if politician['category'] == 'current_member' else None,
                
                # 기사 검색 공간 (미리 확보)
                'news_section': {
                    'articles': politician['news_articles'],
                    'count': politician['recent_news_count'],
                    'last_updated': politician['news_last_updated'],
                    'placeholder_message': f"{politician['name']} 관련 최신 기사를 불러오는 중..."
                },
                
                # 입법 정보 공간 (현직 의원만)
                'legislation_section': politician['legislation_info'],
                
                # 메타 정보
                'meta': {
                    'data_source': politician['data_source'],
                    'last_updated': politician['last_updated']
                }
            }
        
        logger.info("✅ 팝업 데이터 생성 완료")
        return popup_data
    
    def run_integration(self) -> Dict:
        """전체 통합 작업을 실행합니다."""
        logger.info("🚀 NewsBot.kr 통합 시스템 시작")
        
        # 1. 데이터 로드
        if not self.load_current_assembly_data():
            return None
        
        if not self.load_election_candidates_data():
            return None
        
        # 2. 데이터 표준화 및 통합
        logger.info("🔄 데이터 표준화 및 통합 시작")
        
        # 현직 국회의원 표준화
        for member in self.current_assembly_members:
            normalized = self.normalize_politician_data(member, 'current_member')
            self.integrated_politicians.append(normalized)
        
        # 22대 출마자 표준화
        for candidate in self.election_candidates:
            normalized = self.normalize_politician_data(candidate, 'election_candidate')
            self.integrated_politicians.append(normalized)
        
        # 3. 중복 제거 (이름+선거구 기준)
        unique_politicians = {}
        for politician in self.integrated_politicians:
            key = f"{politician['name']}_{politician['district']}"
            
            # 현직 의원 우선 (더 완전한 데이터)
            if key not in unique_politicians or politician['category'] == 'current_member':
                unique_politicians[key] = politician
        
        self.integrated_politicians = list(unique_politicians.values())
        
        # 4. 검색 인덱스 구축
        self.search_index = self.build_search_index()
        
        # 5. 팝업 데이터 생성
        popup_data = self.create_popup_data()
        
        # 6. 통계 생성
        statistics = {
            'total_politicians': len(self.integrated_politicians),
            'current_members': len([p for p in self.integrated_politicians if p['category'] == 'current_member']),
            'election_candidates': len([p for p in self.integrated_politicians if p['category'] == 'election_candidate']),
            'parties_count': len(self.search_index['by_party']),
            'districts_count': len(self.search_index['by_district']),
            'integration_timestamp': datetime.now().isoformat()
        }
        
        # 7. 카테고리 분석
        categories = {
            'current_members': {
                'count': statistics['current_members'],
                'description': '현직 22대 국회의원',
                'features': ['입법정보', '연락처', '기사검색']
            },
            'election_candidates': {
                'count': statistics['election_candidates'],
                'description': '22대 국회의원선거 출마자',
                'features': ['선거결과', '득표정보', '기사검색']
            }
        }
        
        # 결과 정리
        self.integration_results = {
            'statistics': statistics,
            'categories': categories,
            'search_data': self.search_index,
            'popup_data': popup_data,
            'integrated_politicians': self.integrated_politicians
        }
        
        logger.info("✅ NewsBot.kr 통합 완료")
        return self.integration_results
    
    def generate_integration_report(self) -> str:
        """통합 결과 리포트를 생성합니다."""
        stats = self.integration_results['statistics']
        categories = self.integration_results['categories']
        
        report = f"""
🏛️ NewsBot.kr 통합 시스템 결과 리포트
{'='*60}

📊 통합 통계:
- 전체 정치인: {stats['total_politicians']}명
- 현직 국회의원: {stats['current_members']}명
- 22대 출마자: {stats['election_candidates']}명
- 정당 수: {stats['parties_count']}개
- 선거구 수: {stats['districts_count']}개

🏷️ 카테고리 분석:
📍 현직 국회의원 ({categories['current_members']['count']}명):
   - {categories['current_members']['description']}
   - 기능: {', '.join(categories['current_members']['features'])}

📍 22대 출마자 ({categories['election_candidates']['count']}명):
   - {categories['election_candidates']['description']}
   - 기능: {', '.join(categories['election_candidates']['features'])}

🔍 검색 시스템:
- 이름별 검색: {len(self.integration_results['search_data']['by_name'])}명
- 정당별 검색: {stats['parties_count']}개 정당
- 선거구별 검색: {stats['districts_count']}개 선거구
- 퍼지 검색: {len(self.integration_results['search_data']['fuzzy_search'])}개 항목

💬 팝업 시스템:
- 팝업 데이터: {len(self.integration_results['popup_data'])}명
- 기사 검색 공간: 모든 정치인에게 확보
- 입법 정보 공간: 현직 의원에게만 확보

"""
        
        return report
    
    def save_results(self):
        """통합 결과를 파일로 저장합니다."""
        try:
            # 전체 통합 결과
            with open("newsbot_integration_results.json", 'w', encoding='utf-8') as f:
                json.dump(self.integration_results, f, ensure_ascii=False, indent=2)
            
            # 검색용 데이터 (경량화)
            search_data = {
                'politicians': [
                    {
                        'id': p['id'],
                        'name': p['name'],
                        'category': p['category'],
                        'party': p['party'],
                        'district': p['district']
                    }
                    for p in self.integrated_politicians
                ],
                'search_index': self.search_index
            }
            
            with open("newsbot_search_data.json", 'w', encoding='utf-8') as f:
                json.dump(search_data, f, ensure_ascii=False, indent=2)
            
            # 팝업용 데이터
            with open("newsbot_popup_data.json", 'w', encoding='utf-8') as f:
                json.dump(self.integration_results['popup_data'], f, ensure_ascii=False, indent=2)
            
            logger.info("✅ 통합 결과 파일 저장 완료")
            
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {str(e)}")

def main():
    """메인 실행 함수"""
    logger.info("=== NewsBot.kr 통합 시스템 시작 ===")
    
    integration_system = NewsBotIntegrationSystem()
    
    # 통합 실행
    results = integration_system.run_integration()
    
    if not results:
        logger.error("❌ 통합 시스템 실행 실패")
        return False
    
    # 결과 저장
    integration_system.save_results()
    
    # 리포트 생성 및 출력
    report = integration_system.generate_integration_report()
    print(report)
    
    # 리포트 파일 저장
    with open("newsbot_integration_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info("✅ NewsBot.kr 통합 시스템 완료")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ 통합 시스템 실행 완료")
    else:
        logger.error("❌ 통합 시스템 실행 실패")

