#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
확장 통합 시스템
현직 국회의원 + 22대 출마자 + 지방의회의원을 통합하여 완전한 정치인 데이터베이스를 구축합니다.
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

class ExtendedIntegrationSystem:
    """확장 통합 시스템 클래스"""
    
    def __init__(self):
        self.current_assembly_members = []  # 현직 국회의원 (298명)
        self.election_candidates = []       # 22대 출마자 (693명)
        self.local_politicians = []         # 지방의회의원 (48명)
        self.integrated_politicians = []    # 통합된 정치인 데이터
        self.search_index = {}              # 검색 인덱스
        self.integration_results = {}
    
    def load_all_data(self) -> bool:
        """모든 데이터를 로드합니다."""
        logger.info("🔄 모든 데이터 로드 시작")
        
        # 1. 현직 국회의원 데이터
        assembly_files = [
            "enhanced_298_members_with_contact.json",
            "updated_298_current_assembly.json",
            "final_298_current_assembly.json"
        ]
        
        for file_path in assembly_files:
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        self.current_assembly_members = data
                    elif isinstance(data, dict) and 'members' in data:
                        self.current_assembly_members = data['members']
                    
                    logger.info(f"✅ 현직 국회의원: {len(self.current_assembly_members)}명")
                    break
            except Exception as e:
                continue
        
        # 2. 22대 출마자 데이터
        try:
            with open("politician_classification_results.json", 'r', encoding='utf-8') as f:
                classification_data = json.load(f)
            
            winners = classification_data.get('current_assembly_members', [])
            losers = classification_data.get('former_politicians', [])
            self.election_candidates = winners + losers
            
            logger.info(f"✅ 22대 출마자: {len(self.election_candidates)}명")
        except Exception as e:
            logger.warning(f"22대 출마자 데이터 로드 실패: {str(e)}")
        
        # 3. 지방의회의원 데이터
        try:
            with open("20th_local_election_full.json", 'r', encoding='utf-8') as f:
                local_data = json.load(f)
            
            self.local_politicians = local_data.get('candidates', [])
            logger.info(f"✅ 지방의회의원: {len(self.local_politicians)}명")
        except Exception as e:
            logger.warning(f"지방의회의원 데이터 로드 실패: {str(e)}")
        
        total_loaded = len(self.current_assembly_members) + len(self.election_candidates) + len(self.local_politicians)
        logger.info(f"📊 전체 로드 완료: {total_loaded}명")
        
        return total_loaded > 0
    
    def normalize_politician_data(self, politician: Dict, category: str) -> Dict:
        """정치인 데이터를 표준화합니다."""
        # 카테고리별 고유 ID 생성
        name = politician.get('name', 'unknown').strip()
        district = politician.get('district', 'unknown').strip()
        
        if category == 'current_member':
            politician_id = f"assembly_{name}_{district}"
        elif category == 'election_candidate':
            politician_id = f"22nd_{name}_{district}"
        elif category == 'local_politician':
            politician_id = f"local_{name}_{district}"
        else:
            politician_id = f"unknown_{name}_{district}"
        
        normalized = {
            # 기본 정보
            'id': politician_id,
            'name': name,
            'category': category,
            'party': politician.get('party', '').strip() or None,
            'district': district or None,
            
            # 개인 정보
            'age': politician.get('age'),
            'gender': politician.get('sexDistinction') or politician.get('gender'),
            'birthday': politician.get('birthday'),
            
            # 학력 및 경력
            'education': politician.get('academicCareerDetail') or politician.get('academic_career') or politician.get('education'),
            'career': politician.get('career', ''),
            'occupation': politician.get('occupationDetail') or politician.get('occupation'),
            
            # 연락처 정보 (현직 의원만)
            'contact_info': {
                'email': politician.get('email_personal') or politician.get('email'),
                'homepage': politician.get('homepage'),
                'phone': politician.get('phone_office') or politician.get('phone'),
                'office_room': politician.get('office_room')
            } if category == 'current_member' else None,
            
            # 선거 정보
            'election_data': {
                'vote_count': politician.get('vote_count'),
                'vote_rate': politician.get('vote_rate'),
                'is_elected': politician.get('is_elected', False),
                'election_symbol': politician.get('electionSymbol') or politician.get('election_symbol'),
                'candidate_type': politician.get('candidate_type'),
                'vote_grade': politician.get('vote_grade'),
                'election_info': politician.get('election_info', {})
            },
            
            # 정치 경험
            'political_profile': {
                'political_experience': politician.get('political_experience', []),
                'is_incumbent': politician.get('is_incumbent', category == 'current_member'),
                'age_group': politician.get('age_group'),
                'political_level': self._determine_political_level(category, politician)
            },
            
            # 기사 검색 공간 (모든 정치인)
            'news_section': {
                'articles': [],
                'count': 0,
                'last_updated': None,
                'search_keywords': [name, politician.get('party', ''), '정치인', '의원'],
                'placeholder_message': f"{name} 관련 최신 기사를 불러오는 중..."
            },
            
            # 입법 정보 공간 (현직 의원만)
            'legislation_section': {
                'bills': [],
                'proposals_count': 0,
                'recent_activity': None,
                'last_updated': None
            } if category == 'current_member' else None,
            
            # 메타 정보
            'meta': {
                'data_source': self._get_data_source(category, politician),
                'category_description': self._get_category_description(category),
                'last_updated': datetime.now().isoformat(),
                'search_priority': self._get_search_priority(category, politician)
            }
        }
        
        # 빈 값 정리
        for key, value in list(normalized.items()):
            if value == '' or value == 'null':
                normalized[key] = None
        
        return normalized
    
    def _determine_political_level(self, category: str, politician: Dict) -> str:
        """정치인의 정치 수준을 결정합니다."""
        if category == 'current_member':
            return '국회의원'
        elif category == 'election_candidate':
            if politician.get('is_elected', False):
                return '국회의원 당선자'
            else:
                return '국회의원 출마자'
        elif category == 'local_politician':
            if politician.get('is_elected', False):
                return '지방의회의원'
            else:
                return '지방의회의원 출마자'
        else:
            return '정치인'
    
    def _get_data_source(self, category: str, politician: Dict) -> str:
        """데이터 소스를 결정합니다."""
        if category == 'current_member':
            return 'current_assembly_csv'
        elif category == 'election_candidate':
            return '22nd_election_lod'
        elif category == 'local_politician':
            return '20th_local_election_lod'
        else:
            return 'unknown'
    
    def _get_category_description(self, category: str) -> str:
        """카테고리 설명을 반환합니다."""
        descriptions = {
            'current_member': '현직 22대 국회의원',
            'election_candidate': '22대 국회의원선거 출마자',
            'local_politician': '20대 시·도의회의원선거 출마자'
        }
        return descriptions.get(category, '정치인')
    
    def _get_search_priority(self, category: str, politician: Dict) -> int:
        """검색 우선순위를 결정합니다."""
        if category == 'current_member':
            return 100  # 최고 우선순위
        elif category == 'election_candidate':
            if politician.get('is_elected', False):
                return 90  # 22대 당선자
            else:
                return 70  # 22대 낙선자
        elif category == 'local_politician':
            if politician.get('is_elected', False):
                return 60  # 지방의회의원 당선자
            else:
                return 50  # 지방의회의원 낙선자
        else:
            return 30
    
    def build_extended_search_index(self) -> Dict:
        """확장된 검색 인덱스를 구축합니다."""
        search_index = {
            'by_name': {},
            'by_party': {},
            'by_district': {},
            'by_category': {
                'current_member': [],
                'election_candidate': [],
                'local_politician': []
            },
            'by_political_level': {},
            'fuzzy_search': []
        }
        
        for politician in self.integrated_politicians:
            name = politician['name']
            party = politician['party']
            district = politician['district']
            category = politician['category']
            political_level = politician['political_profile']['political_level']
            
            # 이름별 인덱스 (우선순위 고려)
            if name:
                name_key = name.lower()
                if name_key not in search_index['by_name']:
                    search_index['by_name'][name_key] = []
                search_index['by_name'][name_key].append(politician)
                
                # 우선순위 정렬
                search_index['by_name'][name_key].sort(
                    key=lambda x: x['meta']['search_priority'], 
                    reverse=True
                )
            
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
            
            # 정치 수준별 인덱스
            if political_level not in search_index['by_political_level']:
                search_index['by_political_level'][political_level] = []
            search_index['by_political_level'][political_level].append(politician)
            
            # 퍼지 검색용
            search_terms = [name, party, district, political_level]
            search_terms = [term for term in search_terms if term]
            search_index['fuzzy_search'].append({
                'politician': politician,
                'search_terms': ' '.join(search_terms).lower()
            })
        
        logger.info("✅ 확장 검색 인덱스 구축 완료")
        return search_index
    
    def run_extended_integration(self) -> Dict:
        """확장 통합 작업을 실행합니다."""
        logger.info("🚀 확장 통합 시스템 시작")
        
        # 1. 모든 데이터 로드
        if not self.load_all_data():
            logger.error("❌ 데이터 로드 실패")
            return None
        
        # 2. 데이터 표준화 및 통합
        logger.info("🔄 데이터 표준화 및 통합")
        
        # 현직 국회의원
        for member in self.current_assembly_members:
            normalized = self.normalize_politician_data(member, 'current_member')
            self.integrated_politicians.append(normalized)
        
        # 22대 출마자
        for candidate in self.election_candidates:
            normalized = self.normalize_politician_data(candidate, 'election_candidate')
            self.integrated_politicians.append(normalized)
        
        # 지방의회의원
        for local_pol in self.local_politicians:
            normalized = self.normalize_politician_data(local_pol, 'local_politician')
            self.integrated_politicians.append(normalized)
        
        # 3. 중복 제거 (이름 기준, 우선순위 고려)
        unique_politicians = {}
        for politician in self.integrated_politicians:
            name = politician['name']
            
            if name not in unique_politicians:
                unique_politicians[name] = politician
            else:
                # 우선순위가 높은 것으로 교체
                existing_priority = unique_politicians[name]['meta']['search_priority']
                new_priority = politician['meta']['search_priority']
                
                if new_priority > existing_priority:
                    unique_politicians[name] = politician
        
        self.integrated_politicians = list(unique_politicians.values())
        
        # 4. 확장 검색 인덱스 구축
        self.search_index = self.build_extended_search_index()
        
        # 5. 통계 생성
        statistics = {
            'total_politicians': len(self.integrated_politicians),
            'current_members': len([p for p in self.integrated_politicians if p['category'] == 'current_member']),
            'election_candidates': len([p for p in self.integrated_politicians if p['category'] == 'election_candidate']),
            'local_politicians': len([p for p in self.integrated_politicians if p['category'] == 'local_politician']),
            'parties_count': len(self.search_index['by_party']),
            'districts_count': len(self.search_index['by_district']),
            'political_levels': len(self.search_index['by_political_level']),
            'integration_timestamp': datetime.now().isoformat()
        }
        
        # 6. 카테고리 분석
        categories = {
            'current_member': {
                'count': statistics['current_members'],
                'name': '현직 국회의원',
                'description': '현직 22대 국회의원',
                'features': ['입법정보', '연락처', '기사검색', '연결성분석'],
                'priority': 100
            },
            'election_candidate': {
                'count': statistics['election_candidates'],
                'name': '22대 출마자',
                'description': '22대 국회의원선거 출마자',
                'features': ['선거결과', '득표정보', '기사검색'],
                'priority': 80
            },
            'local_politician': {
                'count': statistics['local_politicians'],
                'name': '지방의원 출마자',
                'description': '20대 시·도의회의원선거 출마자',
                'features': ['지방선거결과', '득표정보', '기사검색'],
                'priority': 60
            }
        }
        
        # 결과 정리
        self.integration_results = {
            'statistics': statistics,
            'categories': categories,
            'search_index': self.search_index,
            'integrated_politicians': self.integrated_politicians
        }
        
        logger.info("✅ 확장 통합 완료")
        return self.integration_results
    
    def generate_extended_report(self) -> str:
        """확장 통합 결과 리포트를 생성합니다."""
        stats = self.integration_results['statistics']
        categories = self.integration_results['categories']
        
        report = f"""
🏛️ NewsBot.kr 확장 통합 시스템 결과
{'='*70}

📊 통합 통계:
- 전체 정치인: {stats['total_politicians']:,}명
- 현직 국회의원: {stats['current_members']:,}명
- 22대 출마자: {stats['election_candidates']:,}명  
- 지방의원 출마자: {stats['local_politicians']:,}명
- 정당 수: {stats['parties_count']:,}개
- 선거구 수: {stats['districts_count']:,}개
- 정치 수준: {stats['political_levels']:,}개

🏷️ 카테고리 분석:
"""
        
        for cat_id, cat_data in categories.items():
            report += f"""
📍 {cat_data['name']} ({cat_data['count']:,}명):
   - {cat_data['description']}
   - 기능: {', '.join(cat_data['features'])}
   - 우선순위: {cat_data['priority']}
"""
        
        report += f"""
🔍 검색 시스템 확장:
- 이름별 검색: {len(self.integration_results['search_index']['by_name']):,}명
- 정당별 검색: {stats['parties_count']:,}개 정당
- 선거구별 검색: {stats['districts_count']:,}개 선거구
- 정치수준별 검색: {stats['political_levels']:,}개 수준
- 퍼지 검색: {len(self.integration_results['search_index']['fuzzy_search']):,}개 항목

💬 팝업 시스템 확장:
- 현직 의원: 완전한 정보 (입법+연락처+기사)
- 22대 출마자: 선거정보 + 기사검색
- 지방의원: 지방선거정보 + 기사검색
- 모든 카테고리: 동등한 수준의 상세 정보 제공

🚀 다음 선거 DB 통합 준비 완료!
- 확장 가능한 카테고리 시스템
- 표준화된 데이터 형식
- 우선순위 기반 검색 시스템

"""
        
        return report
    
    def save_extended_results(self):
        """확장 통합 결과를 저장합니다."""
        try:
            # 전체 통합 결과
            with open("newsbot_extended_integration.json", 'w', encoding='utf-8') as f:
                json.dump(self.integration_results, f, ensure_ascii=False, indent=2)
            
            # 검색용 데이터 (경량화)
            search_data = {
                'politicians': [
                    {
                        'id': p['id'],
                        'name': p['name'],
                        'category': p['category'],
                        'party': p['party'],
                        'district': p['district'],
                        'political_level': p['political_profile']['political_level'],
                        'search_priority': p['meta']['search_priority']
                    }
                    for p in self.integrated_politicians
                ],
                'categories': self.integration_results['categories'],
                'search_index': self.search_index
            }
            
            with open("newsbot_extended_search.json", 'w', encoding='utf-8') as f:
                json.dump(search_data, f, ensure_ascii=False, indent=2)
            
            # 팝업용 데이터 (카테고리별 분리)
            popup_data = {
                'current_members': {},
                'election_candidates': {},
                'local_politicians': {}
            }
            
            for politician in self.integrated_politicians:
                category = politician['category']
                politician_id = politician['id']
                
                if category == 'current_member':
                    popup_data['current_members'][politician_id] = politician
                elif category == 'election_candidate':
                    popup_data['election_candidates'][politician_id] = politician
                elif category == 'local_politician':
                    popup_data['local_politicians'][politician_id] = politician
            
            with open("newsbot_extended_popup.json", 'w', encoding='utf-8') as f:
                json.dump(popup_data, f, ensure_ascii=False, indent=2)
            
            logger.info("✅ 확장 통합 결과 파일 저장 완료")
            
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {str(e)}")

def main():
    """메인 실행 함수"""
    logger.info("=== NewsBot.kr 확장 통합 시스템 시작 ===")
    
    integration_system = ExtendedIntegrationSystem()
    
    # 확장 통합 실행
    results = integration_system.run_extended_integration()
    
    if not results:
        logger.error("❌ 확장 통합 시스템 실행 실패")
        return False
    
    # 결과 저장
    integration_system.save_extended_results()
    
    # 리포트 생성 및 출력
    report = integration_system.generate_extended_report()
    print(report)
    
    # 리포트 파일 저장
    with open("newsbot_extended_integration_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info("✅ NewsBot.kr 확장 통합 시스템 완료")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ 확장 통합 시스템 실행 완료")
    else:
        logger.error("❌ 확장 통합 시스템 실행 실패")

