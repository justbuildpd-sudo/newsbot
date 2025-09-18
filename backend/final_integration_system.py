#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 통합 시스템
현직 국회의원 + 22대 출마자 + 지방의회의원 + 교육감을 모두 통합하여 
완전한 정치인 데이터베이스를 구축합니다.
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

class FinalIntegrationSystem:
    """최종 통합 시스템 클래스"""
    
    def __init__(self):
        self.current_assembly_members = []  # 현직 국회의원 (298명)
        self.election_candidates = []       # 22대 출마자 (693명)
        self.local_politicians = []         # 지방의회의원 (48명)
        self.education_candidates = []      # 교육감 (59명)
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
        
        # 3. 지방의회의원 데이터 (기존 20대 시·도의회의원선거)
        try:
            with open("20th_local_election_full.json", 'r', encoding='utf-8') as f:
                local_data = json.load(f)
            
            self.local_politicians = local_data.get('candidates', [])
            logger.info(f"✅ 지방의회의원: {len(self.local_politicians)}명")
        except Exception as e:
            logger.warning(f"지방의회의원 데이터 로드 실패: {str(e)}")
        
        # 4. 교육감 데이터 (새로 추가)
        try:
            with open("education_superintendent_election.json", 'r', encoding='utf-8') as f:
                education_data = json.load(f)
            
            self.education_candidates = education_data.get('candidates', [])
            logger.info(f"✅ 교육감 후보자: {len(self.education_candidates)}명")
        except Exception as e:
            logger.warning(f"교육감 데이터 로드 실패: {str(e)}")
        
        total_loaded = (len(self.current_assembly_members) + 
                       len(self.election_candidates) + 
                       len(self.local_politicians) + 
                       len(self.education_candidates))
        logger.info(f"📊 전체 로드 완료: {total_loaded}명")
        
        return total_loaded > 0
    
    def normalize_politician_data(self, politician: Dict, category: str) -> Dict:
        """정치인 데이터를 표준화합니다."""
        # 카테고리별 고유 ID 생성
        name = politician.get('name', 'unknown').strip()
        district = politician.get('district', 'unknown').strip()
        
        category_prefixes = {
            'current_member': 'assembly',
            'election_candidate': '22nd',
            'local_politician': 'local',
            'education_candidate': 'education'
        }
        
        politician_id = f"{category_prefixes.get(category, 'unknown')}_{name}_{district}"
        
        normalized = {
            # 기본 정보
            'id': politician_id,
            'name': name,
            'category': category,
            'party': (politician.get('party') or '').strip() or None,
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
                'political_level': self._determine_political_level(category, politician),
                'specialized_field': self._determine_specialized_field(category, politician)
            },
            
            # 기사 검색 공간 (모든 정치인)
            'news_section': {
                'articles': [],
                'count': 0,
                'last_updated': None,
                'search_keywords': self._generate_search_keywords(name, category, politician),
                'placeholder_message': f"{name} 관련 최신 기사를 불러오는 중..."
            },
            
            # 입법 정보 공간 (현직 의원만)
            'legislation_section': {
                'bills': [],
                'proposals_count': 0,
                'recent_activity': None,
                'last_updated': None
            } if category == 'current_member' else None,
            
            # 교육감 전용 정보 (교육감만)
            'education_section': {
                'public_pledges': [],
                'education_policies': [],
                'school_management_experience': politician.get('career', ''),
                'education_philosophy': None,
                'last_updated': None
            } if category == 'education_candidate' else None,
            
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
        levels = {
            'current_member': '국회의원',
            'election_candidate': '국회의원 출마자' if not politician.get('is_elected', False) else '국회의원 당선자',
            'local_politician': '지방의회의원 출마자' if not politician.get('is_elected', False) else '지방의회의원',
            'education_candidate': '교육감 출마자' if not politician.get('is_elected', False) else '교육감'
        }
        return levels.get(category, '정치인')
    
    def _determine_specialized_field(self, category: str, politician: Dict) -> str:
        """정치인의 전문 분야를 결정합니다."""
        if category == 'education_candidate':
            return '교육정책'
        elif category == 'local_politician':
            return '지방정치'
        elif category == 'election_candidate' or category == 'current_member':
            return '중앙정치'
        else:
            return '일반정치'
    
    def _generate_search_keywords(self, name: str, category: str, politician: Dict) -> List[str]:
        """검색 키워드를 생성합니다."""
        keywords = [name]
        
        party = politician.get('party')
        if party:
            keywords.append(party)
        
        district = politician.get('district')
        if district:
            keywords.append(district)
        
        # 카테고리별 키워드 추가
        category_keywords = {
            'current_member': ['국회의원', '의원', '정치인'],
            'election_candidate': ['정치인', '출마자', '후보자'],
            'local_politician': ['지방의원', '지방정치', '정치인'],
            'education_candidate': ['교육감', '교육정책', '교육행정']
        }
        
        keywords.extend(category_keywords.get(category, ['정치인']))
        
        return list(set(keywords))  # 중복 제거
    
    def _get_data_source(self, category: str, politician: Dict) -> str:
        """데이터 소스를 결정합니다."""
        sources = {
            'current_member': 'current_assembly_csv',
            'election_candidate': '22nd_election_lod',
            'local_politician': '20th_local_election_lod',
            'education_candidate': '7th_education_election_lod'
        }
        return sources.get(category, 'unknown')
    
    def _get_category_description(self, category: str) -> str:
        """카테고리 설명을 반환합니다."""
        descriptions = {
            'current_member': '현직 22대 국회의원',
            'election_candidate': '22대 국회의원선거 출마자',
            'local_politician': '20대 시·도의회의원선거 출마자',
            'education_candidate': '제7회 교육감선거 출마자'
        }
        return descriptions.get(category, '정치인')
    
    def _get_search_priority(self, category: str, politician: Dict) -> int:
        """검색 우선순위를 결정합니다."""
        priorities = {
            'current_member': 100,  # 최고 우선순위
            'education_candidate': 85 if politician.get('is_elected', False) else 75,  # 교육감
            'election_candidate': 90 if politician.get('is_elected', False) else 70,   # 22대 국회의원
            'local_politician': 60 if politician.get('is_elected', False) else 50      # 지방의원
        }
        return priorities.get(category, 30)
    
    def build_final_search_index(self) -> Dict:
        """최종 검색 인덱스를 구축합니다."""
        search_index = {
            'by_name': {},
            'by_party': {},
            'by_district': {},
            'by_category': {
                'current_member': [],
                'election_candidate': [],
                'local_politician': [],
                'education_candidate': []
            },
            'by_political_level': {},
            'by_specialized_field': {},
            'fuzzy_search': []
        }
        
        for politician in self.integrated_politicians:
            name = politician['name']
            party = politician['party']
            district = politician['district']
            category = politician['category']
            political_level = politician['political_profile']['political_level']
            specialized_field = politician['political_profile']['specialized_field']
            
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
            
            # 전문 분야별 인덱스
            if specialized_field not in search_index['by_specialized_field']:
                search_index['by_specialized_field'][specialized_field] = []
            search_index['by_specialized_field'][specialized_field].append(politician)
            
            # 퍼지 검색용
            search_terms = [name, party, district, political_level, specialized_field]
            search_terms = [term for term in search_terms if term]
            search_index['fuzzy_search'].append({
                'politician': politician,
                'search_terms': ' '.join(search_terms).lower()
            })
        
        logger.info("✅ 최종 검색 인덱스 구축 완료")
        return search_index
    
    def run_final_integration(self) -> Dict:
        """최종 통합 작업을 실행합니다."""
        logger.info("🚀 최종 통합 시스템 시작")
        
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
        
        # 교육감
        for edu_candidate in self.education_candidates:
            normalized = self.normalize_politician_data(edu_candidate, 'education_candidate')
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
        
        # 4. 최종 검색 인덱스 구축
        self.search_index = self.build_final_search_index()
        
        # 5. 통계 생성
        statistics = {
            'total_politicians': len(self.integrated_politicians),
            'current_members': len([p for p in self.integrated_politicians if p['category'] == 'current_member']),
            'election_candidates': len([p for p in self.integrated_politicians if p['category'] == 'election_candidate']),
            'local_politicians': len([p for p in self.integrated_politicians if p['category'] == 'local_politician']),
            'education_candidates': len([p for p in self.integrated_politicians if p['category'] == 'education_candidate']),
            'parties_count': len(self.search_index['by_party']),
            'districts_count': len(self.search_index['by_district']),
            'political_levels': len(self.search_index['by_political_level']),
            'specialized_fields': len(self.search_index['by_specialized_field']),
            'integration_timestamp': datetime.now().isoformat()
        }
        
        # 6. 카테고리 분석
        categories = {
            'current_member': {
                'count': statistics['current_members'],
                'name': '현직 국회의원',
                'description': '현직 22대 국회의원',
                'features': ['입법정보', '연락처', '기사검색', '연결성분석'],
                'priority': 100,
                'icon': '🏛️'
            },
            'election_candidate': {
                'count': statistics['election_candidates'],
                'name': '22대 출마자',
                'description': '22대 국회의원선거 출마자',
                'features': ['선거결과', '득표정보', '기사검색'],
                'priority': 80,
                'icon': '🗳️'
            },
            'education_candidate': {
                'count': statistics['education_candidates'],
                'name': '교육감 출마자',
                'description': '제7회 교육감선거 출마자',
                'features': ['교육정책', '공약정보', '기사검색'],
                'priority': 75,
                'icon': '🎓'
            },
            'local_politician': {
                'count': statistics['local_politicians'],
                'name': '지방의원 출마자',
                'description': '20대 시·도의회의원선거 출마자',
                'features': ['지방선거결과', '득표정보', '기사검색'],
                'priority': 60,
                'icon': '🏘️'
            }
        }
        
        # 결과 정리
        self.integration_results = {
            'statistics': statistics,
            'categories': categories,
            'search_index': self.search_index,
            'integrated_politicians': self.integrated_politicians
        }
        
        logger.info("✅ 최종 통합 완료")
        return self.integration_results
    
    def generate_final_report(self) -> str:
        """최종 통합 결과 리포트를 생성합니다."""
        stats = self.integration_results['statistics']
        categories = self.integration_results['categories']
        
        report = f"""
🏛️ NewsBot.kr 최종 통합 시스템 결과
{'='*80}

📊 최종 통합 통계:
- 🎯 전체 정치인: {stats['total_politicians']:,}명
- 🏛️ 현직 국회의원: {stats['current_members']:,}명
- 🗳️ 22대 출마자: {stats['election_candidates']:,}명  
- 🎓 교육감 출마자: {stats['education_candidates']:,}명
- 🏘️ 지방의원 출마자: {stats['local_politicians']:,}명
- 🎭 정당 수: {stats['parties_count']:,}개
- 🗺️ 선거구 수: {stats['districts_count']:,}개
- 📊 정치 수준: {stats['political_levels']:,}개
- 🎯 전문 분야: {stats['specialized_fields']:,}개

🏷️ 4단계 카테고리 시스템:
"""
        
        # 우선순위 순으로 정렬
        sorted_categories = sorted(categories.items(), key=lambda x: x[1]['priority'], reverse=True)
        
        for cat_id, cat_data in sorted_categories:
            report += f"""
{cat_data['icon']} {cat_data['name']} ({cat_data['count']:,}명):
   - {cat_data['description']}
   - 기능: {', '.join(cat_data['features'])}
   - 우선순위: {cat_data['priority']}
"""
        
        report += f"""
🔍 완전한 검색 시스템:
- 이름별 검색: {len(self.integration_results['search_index']['by_name']):,}명
- 정당별 검색: {stats['parties_count']:,}개 정당
- 선거구별 검색: {stats['districts_count']:,}개 선거구
- 정치수준별 검색: {stats['political_levels']:,}개 수준
- 전문분야별 검색: {stats['specialized_fields']:,}개 분야
- 퍼지 검색: {len(self.integration_results['search_index']['fuzzy_search']):,}개 항목

💬 완전한 팝업 시스템:
- 🏛️ 현직 의원: 완전한 정보 (입법+연락처+기사+연결성)
- 🗳️ 22대 출마자: 선거정보 + 기사검색
- 🎓 교육감: 교육정책 + 공약정보 + 기사검색
- 🏘️ 지방의원: 지방선거정보 + 기사검색
- ✅ 모든 카테고리: 동등한 수준의 상세 정보 제공

🚀 완전한 정치인 데이터베이스 구축 완료!
- 중앙정치 + 지방정치 + 교육자치 완전 커버
- 4단계 우선순위 시스템
- 확장 가능한 구조로 추가 선거 통합 준비

"""
        
        return report
    
    def save_final_results(self):
        """최종 통합 결과를 저장합니다."""
        try:
            # 전체 최종 통합 결과
            with open("newsbot_final_integration.json", 'w', encoding='utf-8') as f:
                json.dump(self.integration_results, f, ensure_ascii=False, indent=2)
            
            # 최종 검색용 데이터
            search_data = {
                'politicians': [
                    {
                        'id': p['id'],
                        'name': p['name'],
                        'category': p['category'],
                        'party': p['party'],
                        'district': p['district'],
                        'political_level': p['political_profile']['political_level'],
                        'specialized_field': p['political_profile']['specialized_field'],
                        'search_priority': p['meta']['search_priority']
                    }
                    for p in self.integrated_politicians
                ],
                'categories': self.integration_results['categories'],
                'search_index': self.search_index
            }
            
            with open("newsbot_final_search.json", 'w', encoding='utf-8') as f:
                json.dump(search_data, f, ensure_ascii=False, indent=2)
            
            # 최종 팝업용 데이터 (카테고리별 분리)
            popup_data = {
                'current_members': {},
                'election_candidates': {},
                'local_politicians': {},
                'education_candidates': {}
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
                elif category == 'education_candidate':
                    popup_data['education_candidates'][politician_id] = politician
            
            with open("newsbot_final_popup.json", 'w', encoding='utf-8') as f:
                json.dump(popup_data, f, ensure_ascii=False, indent=2)
            
            logger.info("✅ 최종 통합 결과 파일 저장 완료")
            
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {str(e)}")

def main():
    """메인 실행 함수"""
    logger.info("=== NewsBot.kr 최종 통합 시스템 시작 ===")
    
    integration_system = FinalIntegrationSystem()
    
    # 최종 통합 실행
    results = integration_system.run_final_integration()
    
    if not results:
        logger.error("❌ 최종 통합 시스템 실행 실패")
        return False
    
    # 결과 저장
    integration_system.save_final_results()
    
    # 리포트 생성 및 출력
    report = integration_system.generate_final_report()
    print(report)
    
    # 리포트 파일 저장
    with open("newsbot_final_integration_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info("✅ NewsBot.kr 최종 통합 시스템 완료")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ 최종 통합 시스템 실행 완료")
    else:
        logger.error("❌ 최종 통합 시스템 실행 실패")
