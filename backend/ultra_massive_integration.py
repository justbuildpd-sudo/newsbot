#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
초대형 통합 시스템
현직 국회의원 + 22대 출마자 + 지방의회의원 + 교육감 + 기초의회의원 + 시·도의회의원
총 8,301명을 통합하여 초대형 정치인 데이터베이스를 구축합니다.
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os
import gc  # 메모리 관리

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UltraMassiveIntegrationSystem:
    """초대형 통합 시스템 클래스"""
    
    def __init__(self):
        self.current_assembly_members = []  # 현직 국회의원 (298명)
        self.election_candidates = []       # 22대 출마자 (693명)
        self.local_politicians = []         # 지방의회의원 (48명)
        self.education_candidates = []      # 교육감 (59명)
        self.basic_council_candidates = []  # 기초의회의원 (5,318명)
        self.metro_council_candidates = []  # 시·도의회의원 (1,886명)
        self.integrated_politicians = []    # 통합된 정치인 데이터
        self.search_index = {}              # 검색 인덱스
        self.integration_results = {}
    
    def load_all_data(self) -> bool:
        """모든 데이터를 로드합니다."""
        logger.info("🔄 초대형 데이터 로드 시작")
        
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
        
        # 4. 교육감 데이터
        try:
            with open("education_superintendent_election.json", 'r', encoding='utf-8') as f:
                education_data = json.load(f)
            
            self.education_candidates = education_data.get('candidates', [])
            logger.info(f"✅ 교육감 후보자: {len(self.education_candidates)}명")
        except Exception as e:
            logger.warning(f"교육감 데이터 로드 실패: {str(e)}")
        
        # 5. 기초의회의원 데이터 (대용량)
        try:
            logger.info("🔄 기초의회의원 대용량 데이터 로드 중...")
            with open("basic_council_election_full.json", 'r', encoding='utf-8') as f:
                basic_council_data = json.load(f)
            
            self.basic_council_candidates = basic_council_data.get('candidates', [])
            logger.info(f"✅ 기초의회의원: {len(self.basic_council_candidates)}명")
        except Exception as e:
            logger.warning(f"기초의회의원 데이터 로드 실패: {str(e)}")
        
        # 6. 시·도의회의원 데이터 (신규 대용량)
        try:
            logger.info("🔄 시·도의회의원 대용량 데이터 로드 중...")
            with open("metro_council_election_full.json", 'r', encoding='utf-8') as f:
                metro_council_data = json.load(f)
            
            self.metro_council_candidates = metro_council_data.get('candidates', [])
            logger.info(f"✅ 시·도의회의원: {len(self.metro_council_candidates)}명")
        except Exception as e:
            logger.warning(f"시·도의회의원 데이터 로드 실패: {str(e)}")
        
        total_loaded = (len(self.current_assembly_members) + 
                       len(self.election_candidates) + 
                       len(self.local_politicians) + 
                       len(self.education_candidates) +
                       len(self.basic_council_candidates) +
                       len(self.metro_council_candidates))
        logger.info(f"📊 초대형 데이터 로드 완료: {total_loaded:,}명")
        
        return total_loaded > 0
    
    def normalize_politician_data(self, politician: Dict, category: str) -> Dict:
        """정치인 데이터를 표준화합니다."""
        # 메모리 효율성을 위한 핵심 정보만 추출
        name = politician.get('name', 'unknown').strip()
        district = politician.get('district', 'unknown').strip()
        
        category_prefixes = {
            'current_member': 'assembly',
            'election_candidate': '22nd',
            'local_politician': 'local',
            'education_candidate': 'education',
            'basic_council_candidate': 'basic',
            'metro_council_candidate': 'metro'
        }
        
        politician_id = f"{category_prefixes.get(category, 'unknown')}_{name}_{district}"
        
        # 초대형 DB를 위한 최소 필수 정보만 포함
        normalized = {
            # 핵심 정보
            'id': politician_id,
            'name': name,
            'category': category,
            'party': (politician.get('party') or '').strip() or None,
            'district': district or None,
            
            # 기본 정보 (최소화)
            'age': politician.get('age'),
            'gender': politician.get('sexDistinction') or politician.get('gender'),
            'occupation': politician.get('occupationDetail') or politician.get('occupation'),
            
            # 선거 정보 (핵심만)
            'election_data': {
                'vote_count': politician.get('vote_count'),
                'vote_rate': politician.get('vote_rate'),
                'is_elected': politician.get('is_elected', False),
                'election_type': politician.get('election_info', {}).get('election_type')
            },
            
            # 정치 프로필 (간소화)
            'political_profile': {
                'political_level': self._determine_political_level(category, politician),
                'specialized_field': self._determine_specialized_field(category),
                'search_priority': self._get_search_priority(category, politician)
            },
            
            # 검색 키워드 (최소화)
            'search_keywords': [name, politician.get('party', ''), category][:3],  # 최대 3개만
            
            # 메타 정보 (최소화)
            'meta': {
                'category_description': self._get_category_description(category),
                'data_source': self._get_data_source(category)
            }
        }
        
        return normalized
    
    def _determine_political_level(self, category: str, politician: Dict) -> str:
        """정치인의 정치 수준을 결정합니다."""
        levels = {
            'current_member': '국회의원',
            'election_candidate': '국회의원 당선자' if politician.get('is_elected', False) else '국회의원 출마자',
            'local_politician': '지방의회의원',
            'education_candidate': '교육감',
            'basic_council_candidate': '기초의회의원 당선자' if politician.get('is_elected', False) else '기초의회의원 출마자',
            'metro_council_candidate': '시·도의회의원 당선자' if politician.get('is_elected', False) else '시·도의회의원 출마자'
        }
        return levels.get(category, '정치인')
    
    def _determine_specialized_field(self, category: str) -> str:
        """정치인의 전문 분야를 결정합니다."""
        fields = {
            'current_member': '중앙정치',
            'election_candidate': '중앙정치',
            'local_politician': '지방정치',
            'education_candidate': '교육정책',
            'basic_council_candidate': '기초자치',
            'metro_council_candidate': '광역자치'
        }
        return fields.get(category, '일반정치')
    
    def _get_search_priority(self, category: str, politician: Dict) -> int:
        """검색 우선순위를 결정합니다."""
        priorities = {
            'current_member': 100,  # 최고 우선순위
            'education_candidate': 85 if politician.get('is_elected', False) else 75,
            'election_candidate': 90 if politician.get('is_elected', False) else 70,
            'metro_council_candidate': 65 if politician.get('is_elected', False) else 55,  # 새로 추가
            'local_politician': 60 if politician.get('is_elected', False) else 50,
            'basic_council_candidate': 55 if politician.get('is_elected', False) else 40
        }
        return priorities.get(category, 30)
    
    def _get_data_source(self, category: str) -> str:
        """데이터 소스를 결정합니다."""
        sources = {
            'current_member': 'current_assembly_csv',
            'election_candidate': '22nd_election_lod',
            'local_politician': '20th_local_election_lod',
            'education_candidate': '7th_education_election_lod',
            'basic_council_candidate': '7th_basic_council_election_lod',
            'metro_council_candidate': '7th_metro_council_election_lod'
        }
        return sources.get(category, 'unknown')
    
    def _get_category_description(self, category: str) -> str:
        """카테고리 설명을 반환합니다."""
        descriptions = {
            'current_member': '현직 22대 국회의원',
            'election_candidate': '22대 국회의원선거 출마자',
            'local_politician': '20대 시·도의회의원선거 출마자',
            'education_candidate': '제7회 교육감선거 출마자',
            'basic_council_candidate': '제7회 기초의회의원선거 출마자',
            'metro_council_candidate': '제7회 시·도의회의원선거 출마자'
        }
        return descriptions.get(category, '정치인')
    
    def run_ultra_massive_integration(self) -> Dict:
        """초대형 통합 작업을 실행합니다."""
        logger.info("🚀 초대형 통합 시스템 시작")
        
        # 1. 모든 데이터 로드
        if not self.load_all_data():
            logger.error("❌ 데이터 로드 실패")
            return None
        
        # 2. 데이터 표준화 및 통합 (대용량 배치 처리)
        logger.info("🔄 초대형 데이터 표준화 및 통합")
        
        batch_size = 1000
        
        # 현직 국회의원
        for member in self.current_assembly_members:
            normalized = self.normalize_politician_data(member, 'current_member')
            self.integrated_politicians.append(normalized)
        logger.info(f"✅ 현직 국회의원 처리 완료: {len(self.current_assembly_members)}명")
        
        # 22대 출마자
        for i, candidate in enumerate(self.election_candidates):
            normalized = self.normalize_politician_data(candidate, 'election_candidate')
            self.integrated_politicians.append(normalized)
            
            if (i + 1) % batch_size == 0:
                gc.collect()
        logger.info(f"✅ 22대 출마자 처리 완료: {len(self.election_candidates)}명")
        
        # 교육감
        for edu_candidate in self.education_candidates:
            normalized = self.normalize_politician_data(edu_candidate, 'education_candidate')
            self.integrated_politicians.append(normalized)
        logger.info(f"✅ 교육감 처리 완료: {len(self.education_candidates)}명")
        
        # 지방의회의원
        for local_pol in self.local_politicians:
            normalized = self.normalize_politician_data(local_pol, 'local_politician')
            self.integrated_politicians.append(normalized)
        logger.info(f"✅ 지방의회의원 처리 완료: {len(self.local_politicians)}명")
        
        # 시·도의회의원 (대용량 배치 처리)
        logger.info("🔄 시·도의회의원 대용량 처리 시작...")
        for i, metro_candidate in enumerate(self.metro_council_candidates):
            normalized = self.normalize_politician_data(metro_candidate, 'metro_council_candidate')
            self.integrated_politicians.append(normalized)
            
            if (i + 1) % batch_size == 0:
                gc.collect()
                logger.info(f"   시·도의회의원 처리: {i + 1:,}/{len(self.metro_council_candidates):,}명 완료")
        logger.info(f"✅ 시·도의회의원 처리 완료: {len(self.metro_council_candidates):,}명")
        
        # 기초의회의원 (초대용량 배치 처리)
        logger.info("🔄 기초의회의원 초대용량 처리 시작...")
        for i, basic_candidate in enumerate(self.basic_council_candidates):
            normalized = self.normalize_politician_data(basic_candidate, 'basic_council_candidate')
            self.integrated_politicians.append(normalized)
            
            if (i + 1) % batch_size == 0:
                gc.collect()
                logger.info(f"   기초의회의원 처리: {i + 1:,}/{len(self.basic_council_candidates):,}명 완료")
        logger.info(f"✅ 기초의회의원 처리 완료: {len(self.basic_council_candidates):,}명")
        
        # 3. 중복 제거 (이름+선거구 기준, 우선순위 고려)
        logger.info("🔄 초대형 중복 제거 처리...")
        unique_politicians = {}
        duplicate_count = 0
        
        for politician in self.integrated_politicians:
            name = politician['name']
            district = politician['district']
            key = f"{name}_{district}"
            
            if key not in unique_politicians:
                unique_politicians[key] = politician
            else:
                # 우선순위가 높은 것으로 교체
                existing_priority = unique_politicians[key]['political_profile']['search_priority']
                new_priority = politician['political_profile']['search_priority']
                
                if new_priority > existing_priority:
                    unique_politicians[key] = politician
                duplicate_count += 1
        
        self.integrated_politicians = list(unique_politicians.values())
        logger.info(f"✅ 중복 제거 완료: {duplicate_count:,}명 중복 제거, {len(self.integrated_politicians):,}명 최종")
        
        # 4. 통계 생성
        statistics = {
            'total_politicians': len(self.integrated_politicians),
            'current_members': len([p for p in self.integrated_politicians if p['category'] == 'current_member']),
            'election_candidates': len([p for p in self.integrated_politicians if p['category'] == 'election_candidate']),
            'local_politicians': len([p for p in self.integrated_politicians if p['category'] == 'local_politician']),
            'education_candidates': len([p for p in self.integrated_politicians if p['category'] == 'education_candidate']),
            'basic_council_candidates': len([p for p in self.integrated_politicians if p['category'] == 'basic_council_candidate']),
            'metro_council_candidates': len([p for p in self.integrated_politicians if p['category'] == 'metro_council_candidate']),
            'duplicates_removed': duplicate_count,
            'integration_timestamp': datetime.now().isoformat()
        }
        
        # 5. 카테고리 분석
        categories = {
            'current_member': {
                'count': statistics['current_members'],
                'name': '현직 국회의원',
                'description': '현직 22대 국회의원',
                'priority': 100,
                'icon': '🏛️'
            },
            'election_candidate': {
                'count': statistics['election_candidates'],
                'name': '22대 출마자',
                'description': '22대 국회의원선거 출마자',
                'priority': 80,
                'icon': '🗳️'
            },
            'education_candidate': {
                'count': statistics['education_candidates'],
                'name': '교육감',
                'description': '제7회 교육감선거 출마자',
                'priority': 75,
                'icon': '🎓'
            },
            'metro_council_candidate': {
                'count': statistics['metro_council_candidates'],
                'name': '시·도의원',
                'description': '제7회 시·도의회의원선거 출마자',
                'priority': 65,
                'icon': '🏢'
            },
            'local_politician': {
                'count': statistics['local_politicians'],
                'name': '지방의원',
                'description': '20대 시·도의회의원선거 출마자',
                'priority': 60,
                'icon': '🏘️'
            },
            'basic_council_candidate': {
                'count': statistics['basic_council_candidates'],
                'name': '기초의원',
                'description': '제7회 기초의회의원선거 출마자',
                'priority': 50,
                'icon': '🏪'
            }
        }
        
        # 결과 정리
        self.integration_results = {
            'statistics': statistics,
            'categories': categories,
            'integrated_politicians': self.integrated_politicians
        }
        
        logger.info("✅ 초대형 통합 완료")
        return self.integration_results
    
    def generate_ultra_massive_report(self) -> str:
        """초대형 통합 결과 리포트를 생성합니다."""
        stats = self.integration_results['statistics']
        categories = self.integration_results['categories']
        
        report = f"""
🏛️ NewsBot.kr 초대형 통합 시스템 결과
{'='*100}

📊 초대형 통합 통계:
- 🎯 전체 정치인: {stats['total_politicians']:,}명
- 🏛️ 현직 국회의원: {stats['current_members']:,}명
- 🗳️ 22대 출마자: {stats['election_candidates']:,}명  
- 🎓 교육감: {stats['education_candidates']:,}명
- 🏢 시·도의원: {stats['metro_council_candidates']:,}명
- 🏪 기초의원: {stats['basic_council_candidates']:,}명
- 🏘️ 지방의원: {stats['local_politicians']:,}명
- 🔄 중복 제거: {stats['duplicates_removed']:,}명

🏷️ 6단계 카테고리 시스템:
"""
        
        # 우선순위 순으로 정렬
        sorted_categories = sorted(categories.items(), key=lambda x: x[1]['priority'], reverse=True)
        
        for cat_id, cat_data in sorted_categories:
            report += f"""
{cat_data['icon']} {cat_data['name']} ({cat_data['count']:,}명):
   - {cat_data['description']}
   - 우선순위: {cat_data['priority']}
"""
        
        report += f"""
🚀 초대형 정치인 생태계 완성!
- 중앙정치 + 광역자치 + 기초자치 + 교육자치 완전 커버
- 한국 정치의 모든 영역과 수준을 포함
- {stats['total_politicians']:,}명 규모의 세계 최대급 정치인 데이터베이스

💡 활용 가능성:
- 정치인 관계 네트워크 분석
- 정당별/지역별 정치 생태계 분석  
- 중앙-지방-기초 정치 연결고리 분석
- 정치인 경력 추적 및 이동 패턴 분석

"""
        
        return report
    
    def save_ultra_massive_results(self):
        """초대형 통합 결과를 저장합니다."""
        try:
            logger.info("🔄 초대형 결과 파일 저장 시작...")
            
            # 통계 및 카테고리 정보만 저장 (메타데이터)
            metadata = {
                'statistics': self.integration_results['statistics'],
                'categories': self.integration_results['categories'],
                'integration_timestamp': datetime.now().isoformat()
            }
            
            with open("newsbot_ultra_massive_metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=1)
            
            # 카테고리별 개별 저장 (메모리 효율성)
            categories = ['current_member', 'election_candidate', 'education_candidate', 
                         'metro_council_candidate', 'local_politician', 'basic_council_candidate']
            
            for category in categories:
                category_data = [p for p in self.integrated_politicians if p['category'] == category]
                
                if category_data:
                    filename = f"newsbot_ultra_{category}_data.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(category_data, f, ensure_ascii=False, indent=1)
                    
                    file_size = os.path.getsize(filename) / (1024 * 1024)
                    logger.info(f"✅ {category} 데이터 저장 완료: {len(category_data):,}명 ({file_size:.1f}MB)")
            
            logger.info("✅ 초대형 통합 결과 파일 저장 완료")
            
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {str(e)}")

def main():
    """메인 실행 함수"""
    logger.info("=== NewsBot.kr 초대형 통합 시스템 시작 ===")
    
    integration_system = UltraMassiveIntegrationSystem()
    
    # 초대형 통합 실행
    results = integration_system.run_ultra_massive_integration()
    
    if not results:
        logger.error("❌ 초대형 통합 시스템 실행 실패")
        return False
    
    # 결과 저장
    integration_system.save_ultra_massive_results()
    
    # 리포트 생성 및 출력
    report = integration_system.generate_ultra_massive_report()
    print(report)
    
    # 리포트 파일 저장
    with open("newsbot_ultra_massive_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info("✅ NewsBot.kr 초대형 통합 시스템 완료")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ 초대형 통합 시스템 실행 완료")
    else:
        logger.error("❌ 초대형 통합 시스템 실행 실패")

