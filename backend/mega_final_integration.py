#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메가 최종 통합 시스템
8개 카테고리 8,724명 규모의 메가 정치인 데이터베이스를 구축합니다.
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os
import gc
import hashlib
from collections import defaultdict

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MegaFinalIntegrationSystem:
    """메가 최종 통합 시스템 클래스"""
    
    def __init__(self):
        self.data_sources = {}
        self.integrated_politicians = []
        self.partitioned_data = {}
        self.search_index = {}
        self.system_config = {
            'max_batch_size': 2000,
            'partition_size': 3000,  # 더 큰 파티션으로 조정
            'memory_cleanup_interval': 1000,
            'max_search_results': 100
        }
    
    def register_all_data_sources(self):
        """모든 데이터 소스를 등록합니다."""
        self.register_data_source("현직_국회의원", "enhanced_298_members_with_contact.json", "current_member", 100)
        self.register_data_source("22대_출마자", "politician_classification_results.json", "22nd_candidate", 90)
        self.register_data_source("21대_출마자", "21st_assembly_election.json", "21st_candidate", 85)
        self.register_data_source("교육감", "education_superintendent_election.json", "education_candidate", 80)
        self.register_data_source("시도의원", "metro_council_election_full.json", "metro_council_candidate", 70)
        self.register_data_source("지방의원", "20th_local_election_full.json", "local_politician", 65)
        self.register_data_source("기초의원", "basic_council_election_full.json", "basic_council_candidate", 60)
        self.register_data_source("보궐선거", "2019_byelection.json", "byelection_candidate", 55)
    
    def register_data_source(self, source_name: str, file_path: str, category: str, priority: int):
        """데이터 소스를 등록합니다."""
        self.data_sources[source_name] = {
            'file_path': file_path,
            'category': category,
            'priority': priority,
            'loaded': False,
            'count': 0
        }
        logger.info(f"📋 데이터 소스 등록: {source_name} ({category}, 우선순위: {priority})")
    
    def load_data_source(self, source_name: str) -> List[Dict]:
        """개별 데이터 소스를 로드합니다."""
        source_info = self.data_sources.get(source_name)
        if not source_info:
            logger.error(f"❌ 알 수 없는 데이터 소스: {source_name}")
            return []
        
        try:
            file_path = source_info['file_path']
            
            if not os.path.exists(file_path):
                logger.warning(f"⚠️ 파일 없음: {file_path}")
                return []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 다양한 데이터 형식 지원
            candidates = []
            if isinstance(data, list):
                candidates = data
            elif isinstance(data, dict):
                # 계층적 LOD 결과 처리
                if 'all_candidates' in data:
                    candidates = data['all_candidates']
                elif 'candidates' in data:
                    candidates = data['candidates']
                elif 'members' in data:
                    candidates = data['members']
                # 22대 출마자 특별 처리
                elif 'current_assembly_members' in data and 'former_politicians' in data:
                    winners = data.get('current_assembly_members', [])
                    losers = data.get('former_politicians', [])
                    candidates = winners + losers
                else:
                    # 첫 번째 리스트 타입 값 찾기
                    for value in data.values():
                        if isinstance(value, list):
                            candidates = value
                            break
            
            source_info['loaded'] = True
            source_info['count'] = len(candidates)
            
            logger.info(f"✅ {source_name} 로드 완료: {len(candidates):,}명")
            return candidates
            
        except Exception as e:
            logger.error(f"❌ {source_name} 로드 실패: {str(e)}")
            return []
    
    def normalize_politician_mega(self, politician: Dict, category: str, priority: int) -> Dict:
        """정치인 데이터를 메가 데이터베이스용으로 표준화합니다."""
        name = politician.get('name', 'unknown').strip()
        district = (politician.get('district') or 'unknown').strip()
        
        # 해시 기반 고유 ID (메모리 효율성)
        unique_string = f"{category}_{name}_{district}"
        politician_id = hashlib.md5(unique_string.encode()).hexdigest()[:12]
        
        # 메가 DB를 위한 핵심 정보만 포함
        normalized = {
            'id': politician_id,
            'name': name,
            'category': category,
            'party': (politician.get('party') or '').strip() or None,
            'district': district,
            'is_elected': politician.get('is_elected', False),
            'search_priority': priority,
            'political_level': self._get_political_level(category, politician),
            'specialized_field': self._get_specialized_field(category),
            'vote_count': politician.get('vote_count'),
            'vote_rate': politician.get('vote_rate'),
            'age': politician.get('age'),
            'gender': politician.get('sexDistinction') or politician.get('gender'),
            'occupation': politician.get('occupationDetail') or politician.get('occupation'),
            'election_info': self._get_election_info(politician, category)
        }
        
        return normalized
    
    def _get_political_level(self, category: str, politician: Dict) -> str:
        """정치 수준을 결정합니다."""
        levels = {
            'current_member': '현직 국회의원',
            '22nd_candidate': '22대 국회의원 출마자',
            '21st_candidate': '21대 국회의원 출마자',
            'education_candidate': '교육감 출마자',
            'metro_council_candidate': '시·도의원 출마자',
            'local_politician': '지방의원 출마자',
            'basic_council_candidate': '기초의원 출마자',
            'byelection_candidate': '보궐선거 출마자'
        }
        return levels.get(category, '정치인')
    
    def _get_specialized_field(self, category: str) -> str:
        """전문 분야를 결정합니다."""
        fields = {
            'current_member': '중앙정치',
            '22nd_candidate': '중앙정치',
            '21st_candidate': '중앙정치',
            'education_candidate': '교육정책',
            'metro_council_candidate': '광역자치',
            'local_politician': '지방정치',
            'basic_council_candidate': '기초자치',
            'byelection_candidate': '보궐정치'
        }
        return fields.get(category, '일반정치')
    
    def _get_election_info(self, politician: Dict, category: str) -> Dict:
        """선거 정보를 추출합니다."""
        election_info = politician.get('election_info', {})
        
        if isinstance(election_info, dict):
            return {
                'election_name': election_info.get('parent_election_name') or election_info.get('election_name'),
                'election_day': election_info.get('parent_election_day') or election_info.get('election_day'),
                'election_type': election_info.get('election_type')
            }
        
        return {}
    
    def run_mega_final_integration(self) -> Dict:
        """메가 최종 통합 작업을 실행합니다."""
        logger.info("🚀 메가 최종 통합 시스템 시작")
        
        # 1. 모든 데이터 소스 등록
        self.register_all_data_sources()
        
        # 2. 모든 데이터 소스 로드 및 통합
        total_processed = 0
        
        for source_name, source_info in self.data_sources.items():
            logger.info(f"🔄 {source_name} 처리 중...")
            
            candidates = self.load_data_source(source_name)
            
            if len(candidates) == 0:
                continue
            
            # 배치 처리로 메모리 효율성 확보
            batch_size = min(self.system_config['max_batch_size'], len(candidates))
            if batch_size == 0:
                batch_size = 1
            
            for i in range(0, len(candidates), batch_size):
                batch = candidates[i:i + batch_size]
                
                for politician in batch:
                    normalized = self.normalize_politician_mega(
                        politician, 
                        source_info['category'], 
                        source_info['priority']
                    )
                    self.integrated_politicians.append(normalized)
                
                total_processed += len(batch)
                
                # 메모리 정리
                if total_processed % self.system_config['memory_cleanup_interval'] == 0:
                    gc.collect()
                    logger.info(f"   메모리 정리 완료: {total_processed:,}명 처리")
            
            logger.info(f"✅ {source_name} 처리 완료: {len(candidates):,}명")
        
        # 3. 중복 제거 (효율적 알고리즘)
        logger.info("🔄 메가 규모 중복 제거...")
        unique_dict = {}
        duplicate_count = 0
        
        for politician in self.integrated_politicians:
            name = politician['name']
            district = politician['district']
            key = f"{name}_{district}"
            
            if key not in unique_dict:
                unique_dict[key] = politician
            else:
                # 우선순위 비교
                if politician['search_priority'] > unique_dict[key]['search_priority']:
                    unique_dict[key] = politician
                duplicate_count += 1
        
        self.integrated_politicians = list(unique_dict.values())
        logger.info(f"✅ 중복 제거 완료: {duplicate_count:,}명 제거, {len(self.integrated_politicians):,}명 최종")
        
        # 4. 데이터 파티셔닝
        self.partition_mega_data()
        
        # 5. 통계 생성
        statistics = {
            'total_politicians': len(self.integrated_politicians),
            'duplicates_removed': duplicate_count,
            'partitions_count': len(self.partitioned_data),
            'categories': {},
            'integration_timestamp': datetime.now().isoformat()
        }
        
        # 카테고리별 통계
        for politician in self.integrated_politicians:
            category = politician['category']
            if category not in statistics['categories']:
                statistics['categories'][category] = 0
            statistics['categories'][category] += 1
        
        # 6. 카테고리 정의
        categories = {
            'current_member': {
                'name': '현직 국회의원',
                'description': '현직 22대 국회의원',
                'priority': 100,
                'icon': '🏛️'
            },
            '22nd_candidate': {
                'name': '22대 출마자',
                'description': '22대 국회의원선거 출마자',
                'priority': 90,
                'icon': '🗳️'
            },
            '21st_candidate': {
                'name': '21대 출마자',
                'description': '21대 국회의원선거 출마자',
                'priority': 85,
                'icon': '🗳️'
            },
            'education_candidate': {
                'name': '교육감',
                'description': '제7회 교육감선거 출마자',
                'priority': 80,
                'icon': '🎓'
            },
            'metro_council_candidate': {
                'name': '시·도의원',
                'description': '제7회 시·도의회의원선거 출마자',
                'priority': 70,
                'icon': '🏢'
            },
            'local_politician': {
                'name': '지방의원',
                'description': '20대 시·도의회의원선거 출마자',
                'priority': 65,
                'icon': '🏘️'
            },
            'basic_council_candidate': {
                'name': '기초의원',
                'description': '제7회 기초의회의원선거 출마자',
                'priority': 60,
                'icon': '🏪'
            },
            'byelection_candidate': {
                'name': '보궐선거',
                'description': '2019년 보궐선거 출마자',
                'priority': 55,
                'icon': '🔄'
            }
        }
        
        results = {
            'statistics': statistics,
            'categories': categories,
            'partitioned_data': self.partitioned_data,
            'system_config': self.system_config
        }
        
        logger.info("✅ 메가 최종 통합 완료")
        return results
    
    def partition_mega_data(self) -> Dict:
        """메가 데이터를 파티션으로 분할합니다."""
        logger.info("🔄 메가 데이터 파티셔닝 시작...")
        
        partitions = defaultdict(list)
        partition_size = self.system_config['partition_size']
        
        # 카테고리별 파티셔닝
        for politician in self.integrated_politicians:
            category = politician['category']
            partition_index = len(partitions[category]) // partition_size
            partition_key = f"{category}_{partition_index}"
            partitions[partition_key].append(politician)
        
        self.partitioned_data = dict(partitions)
        
        logger.info(f"✅ 메가 데이터 파티셔닝 완료: {len(self.partitioned_data)}개 파티션")
        return self.partitioned_data
    
    def generate_mega_report(self, results: Dict) -> str:
        """메가 통합 결과 리포트를 생성합니다."""
        stats = results['statistics']
        categories = results['categories']
        
        report = f"""
🏛️ NewsBot.kr 메가 최종 통합 시스템 결과
{'='*120}

📊 메가 통합 통계:
- 🎯 전체 정치인: {stats['total_politicians']:,}명
- 🔄 중복 제거: {stats['duplicates_removed']:,}명
- 📦 파티션 수: {stats['partitions_count']:,}개

📋 8개 카테고리별 분포:
"""
        
        # 우선순위 순으로 정렬
        sorted_categories = sorted(categories.items(), key=lambda x: x[1]['priority'], reverse=True)
        
        for cat_id, cat_data in sorted_categories:
            count = stats['categories'].get(cat_id, 0)
            percentage = (count / stats['total_politicians']) * 100 if stats['total_politicians'] > 0 else 0
            report += f"""
{cat_data['icon']} {cat_data['name']}: {count:,}명 ({percentage:.1f}%)
   - {cat_data['description']}
   - 우선순위: {cat_data['priority']}
"""
        
        report += f"""
🚀 메가 정치인 생태계 완성!
- 현직 + 22대 + 21대 + 교육감 + 광역 + 지방 + 기초 + 보궐
- 한국 정치사의 완전한 아카이브
- {stats['total_politicians']:,}명 규모의 세계 최대급 정치인 데이터베이스

💡 활용 가능성:
- 정치인 경력 추적 (21대 → 22대 당선/낙선 분석)
- 정치인 이동 패턴 (중앙 ↔ 지방 ↔ 기초)
- 정당별 세력 변화 추이 분석
- 지역별 정치 생태계 완전 분석
- 교육감 → 정치인 진출 패턴 분석

🔧 시스템 성능:
- 파티션 크기: {self.system_config['partition_size']:,}명/파티션
- 배치 처리: {self.system_config['max_batch_size']:,}명/배치
- 메모리 정리: {self.system_config['memory_cleanup_interval']:,}명마다

"""
        
        return report
    
    def save_mega_results(self, results: Dict):
        """메가 통합 결과를 저장합니다."""
        try:
            logger.info("🔄 메가 결과 파일 저장 시작...")
            
            # 메타데이터만 저장
            metadata = {
                'statistics': results['statistics'],
                'categories': results['categories'],
                'system_config': results['system_config'],
                'timestamp': datetime.now().isoformat()
            }
            
            with open("newsbot_mega_metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 파티션별 저장 (메모리 효율성)
            for partition_name, partition_data in results['partitioned_data'].items():
                if len(partition_data) > 0:  # 빈 파티션 제외
                    filename = f"newsbot_mega_{partition_name}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(partition_data, f, ensure_ascii=False, indent=1)
                    
                    file_size = os.path.getsize(filename) / (1024 * 1024)
                    logger.info(f"✅ 메가 파티션 저장: {partition_name} - {len(partition_data):,}명 ({file_size:.1f}MB)")
            
            # 카테고리별 요약 저장
            category_summary = {}
            for politician in self.integrated_politicians:
                category = politician['category']
                if category not in category_summary:
                    category_summary[category] = []
                
                # 요약 정보만 저장 (검색용)
                summary_info = {
                    'id': politician['id'],
                    'name': politician['name'],
                    'party': politician['party'],
                    'district': politician['district'],
                    'is_elected': politician['is_elected'],
                    'search_priority': politician['search_priority']
                }
                category_summary[category].append(summary_info)
            
            with open("newsbot_mega_summary.json", 'w', encoding='utf-8') as f:
                json.dump(category_summary, f, ensure_ascii=False, indent=1)
            
            logger.info("✅ 메가 통합 결과 파일 저장 완료")
            
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {str(e)}")

def main():
    """메인 실행 함수"""
    logger.info("=== NewsBot.kr 메가 최종 통합 시스템 시작 ===")
    
    system = MegaFinalIntegrationSystem()
    
    # 메가 최종 통합 실행
    results = system.run_mega_final_integration()
    
    if not results:
        logger.error("❌ 메가 최종 통합 시스템 실행 실패")
        return False
    
    # 결과 저장
    system.save_mega_results(results)
    
    # 리포트 생성 및 출력
    report = system.generate_mega_report(results)
    print(report)
    
    # 리포트 파일 저장
    with open("newsbot_mega_final_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info("✅ NewsBot.kr 메가 최종 통합 시스템 완료")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ 메가 최종 통합 시스템 실행 완료")
    else:
        logger.error("❌ 메가 최종 통합 시스템 실행 실패")
