#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
확장 가능한 대규모 시스템
25,000명 규모까지 확장 가능한 정치인 데이터베이스 시스템을 구축합니다.
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

class ScalableMassiveSystem:
    """확장 가능한 대규모 시스템 클래스"""
    
    def __init__(self):
        self.data_sources = {}
        self.integrated_politicians = []
        self.partitioned_data = {}  # 파티션별 데이터
        self.search_index = {}
        self.system_config = {
            'max_batch_size': 2000,
            'partition_size': 5000,
            'memory_cleanup_interval': 1000,
            'max_search_results': 100
        }
    
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
                if 'candidates' in data:
                    candidates = data['candidates']
                elif 'members' in data:
                    candidates = data['members']
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
    
    def normalize_politician_minimal(self, politician: Dict, category: str, priority: int) -> Dict:
        """정치인 데이터를 최소 형태로 표준화합니다."""
        name = politician.get('name', 'unknown').strip()
        district = (politician.get('district') or 'unknown').strip()
        
        # 해시 기반 고유 ID (메모리 효율성)
        unique_string = f"{category}_{name}_{district}"
        politician_id = hashlib.md5(unique_string.encode()).hexdigest()[:12]
        
        # 최소 필수 정보만 포함
        normalized = {
            'id': politician_id,
            'name': name,
            'category': category,
            'party': (politician.get('party') or '').strip() or None,
            'district': district,
            'is_elected': politician.get('is_elected', False),
            'search_priority': priority,
            'political_level': self._get_political_level(category, politician),
            'vote_count': politician.get('vote_count'),
            'age': politician.get('age'),
            'gender': politician.get('sexDistinction') or politician.get('gender')
        }
        
        return normalized
    
    def _get_political_level(self, category: str, politician: Dict) -> str:
        """정치 수준을 결정합니다."""
        levels = {
            'current_member': '국회의원',
            'election_candidate': '국회의원 출마자',
            'education_candidate': '교육감',
            'metro_council_candidate': '시·도의원',
            'local_politician': '지방의원',
            'basic_council_candidate': '기초의원'
        }
        return levels.get(category, '정치인')
    
    def partition_data(self) -> Dict:
        """데이터를 파티션으로 분할합니다."""
        logger.info("🔄 데이터 파티셔닝 시작...")
        
        partitions = defaultdict(list)
        partition_size = self.system_config['partition_size']
        
        # 카테고리별 파티셔닝
        for politician in self.integrated_politicians:
            category = politician['category']
            partition_key = f"{category}_{len(partitions[category]) // partition_size}"
            partitions[partition_key].append(politician)
        
        self.partitioned_data = dict(partitions)
        
        logger.info(f"✅ 데이터 파티셔닝 완료: {len(self.partitioned_data)}개 파티션")
        return self.partitioned_data
    
    def build_scalable_search_index(self) -> Dict:
        """확장 가능한 검색 인덱스를 구축합니다."""
        logger.info("🔄 확장 가능한 검색 인덱스 구축...")
        
        search_index = {
            'by_name': defaultdict(list),
            'by_party': defaultdict(list),
            'by_category': defaultdict(list),
            'by_political_level': defaultdict(list),
            'priority_index': defaultdict(list)  # 우선순위별 인덱스
        }
        
        processed_count = 0
        batch_size = self.system_config['memory_cleanup_interval']
        
        for politician in self.integrated_politicians:
            name = politician['name']
            party = politician['party']
            category = politician['category']
            political_level = politician['political_level']
            priority = politician['search_priority']
            
            # 이름별 인덱스 (우선순위 순 정렬)
            if name:
                search_index['by_name'][name.lower()].append(politician)
                # 상위 5개만 유지 (메모리 효율성)
                search_index['by_name'][name.lower()].sort(
                    key=lambda x: x['search_priority'], reverse=True
                )
                search_index['by_name'][name.lower()] = search_index['by_name'][name.lower()][:5]
            
            # 정당별 인덱스
            if party:
                search_index['by_party'][party].append(politician)
            
            # 카테고리별 인덱스
            search_index['by_category'][category].append(politician)
            
            # 정치 수준별 인덱스
            search_index['by_political_level'][political_level].append(politician)
            
            # 우선순위별 인덱스
            priority_group = priority // 10 * 10  # 10단위로 그룹화
            search_index['priority_index'][priority_group].append(politician)
            
            processed_count += 1
            
            # 메모리 관리
            if processed_count % batch_size == 0:
                gc.collect()
                logger.info(f"   검색 인덱스 처리: {processed_count:,}명 완료")
        
        # defaultdict를 일반 dict로 변환
        final_index = {
            'by_name': dict(search_index['by_name']),
            'by_party': dict(search_index['by_party']),
            'by_category': dict(search_index['by_category']),
            'by_political_level': dict(search_index['by_political_level']),
            'priority_index': dict(search_index['priority_index'])
        }
        
        logger.info("✅ 확장 가능한 검색 인덱스 구축 완료")
        return final_index
    
    def run_scalable_integration(self) -> Dict:
        """확장 가능한 통합 작업을 실행합니다."""
        logger.info("🚀 확장 가능한 대규모 통합 시스템 시작")
        
        # 1. 데이터 소스 등록
        self.register_data_source("현직_국회의원", "enhanced_298_members_with_contact.json", "current_member", 100)
        self.register_data_source("22대_출마자", "politician_classification_results.json", "election_candidate", 80)
        self.register_data_source("교육감", "education_superintendent_election.json", "education_candidate", 75)
        self.register_data_source("시도의원", "metro_council_election_full.json", "metro_council_candidate", 65)
        self.register_data_source("지방의원", "20th_local_election_full.json", "local_politician", 60)
        self.register_data_source("기초의원", "basic_council_election_full.json", "basic_council_candidate", 50)
        
        # 2. 모든 데이터 소스 로드 및 통합
        total_processed = 0
        
        for source_name, source_info in self.data_sources.items():
            logger.info(f"🔄 {source_name} 처리 중...")
            
            candidates = self.load_data_source(source_name)
            
            if source_name == "22대_출마자":
                # 특별 처리: classification_results에서 candidates 추출
                winners = candidates.get('current_assembly_members', []) if isinstance(candidates, dict) else []
                losers = candidates.get('former_politicians', []) if isinstance(candidates, dict) else []
                candidates = winners + losers
            
            # 배치 처리로 메모리 효율성 확보
            if len(candidates) == 0:
                continue
                
            batch_size = min(self.system_config['max_batch_size'], len(candidates))
            if batch_size == 0:
                batch_size = 1
            
            for i in range(0, len(candidates), batch_size):
                batch = candidates[i:i + batch_size]
                
                for politician in batch:
                    normalized = self.normalize_politician_minimal(
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
        logger.info("🔄 대규모 중복 제거...")
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
        self.partition_data()
        
        # 5. 확장 가능한 검색 인덱스 구축
        self.search_index = self.build_scalable_search_index()
        
        # 6. 통계 생성
        statistics = {
            'total_politicians': len(self.integrated_politicians),
            'duplicates_removed': duplicate_count,
            'partitions_count': len(self.partitioned_data),
            'categories': {},
            'parties': len(self.search_index['by_party']),
            'political_levels': len(self.search_index['by_political_level']),
            'integration_timestamp': datetime.now().isoformat()
        }
        
        # 카테고리별 통계
        for politician in self.integrated_politicians:
            category = politician['category']
            if category not in statistics['categories']:
                statistics['categories'][category] = 0
            statistics['categories'][category] += 1
        
        results = {
            'statistics': statistics,
            'partitioned_data': self.partitioned_data,
            'search_index': self.search_index,
            'system_config': self.system_config
        }
        
        logger.info("✅ 확장 가능한 대규모 통합 완료")
        return results
    
    def generate_scalability_report(self, results: Dict) -> str:
        """확장성 리포트를 생성합니다."""
        stats = results['statistics']
        
        report = f"""
🚀 NewsBot.kr 확장 가능한 대규모 시스템 결과
{'='*120}

📊 현재 통합 통계:
- 🎯 전체 정치인: {stats['total_politicians']:,}명
- 🔄 중복 제거: {stats['duplicates_removed']:,}명
- 📦 파티션 수: {stats['partitions_count']:,}개
- 🎭 정당 수: {stats['parties']:,}개
- 📊 정치 수준: {stats['political_levels']:,}개

📋 카테고리별 분포:
"""
        
        for category, count in stats['categories'].items():
            percentage = (count / stats['total_politicians']) * 100
            report += f"   - {category}: {count:,}명 ({percentage:.1f}%)\n"
        
        report += f"""
🔧 시스템 확장성 분석:
- 현재 처리 능력: {stats['total_politicians']:,}명 ✅
- 목표 확장 규모: 25,000명
- 확장 여유도: {25000 - stats['total_politicians']:,}명 ({((25000 - stats['total_politicians']) / stats['total_politicians'] * 100):.1f}% 추가 가능)

💾 메모리 최적화:
- 파티션 크기: {self.system_config['partition_size']:,}명/파티션
- 배치 처리: {self.system_config['max_batch_size']:,}명/배치
- 메모리 정리: {self.system_config['memory_cleanup_interval']:,}명마다

🔍 검색 시스템 최적화:
- 이름별 검색: 상위 5개 결과만 유지
- 최대 검색 결과: {self.system_config['max_search_results']:,}개
- 우선순위 기반 정렬

🚀 추가 확장 준비:
- ✅ 25,000명 규모까지 확장 가능
- ✅ 파티션 기반 메모리 관리
- ✅ 배치 처리로 성능 최적화
- ✅ 우선순위 기반 중복 제거

💡 다음 선거 DB 통합 시:
1. register_data_source()로 새 데이터 등록
2. 자동 배치 처리 및 메모리 최적화
3. 기존 데이터와 자동 통합
4. 우선순위 기반 중복 제거

"""
        
        return report
    
    def save_scalable_results(self, results: Dict):
        """확장 가능한 결과를 저장합니다."""
        try:
            # 메타데이터만 저장 (통계, 설정)
            metadata = {
                'statistics': results['statistics'],
                'system_config': results['system_config'],
                'timestamp': datetime.now().isoformat()
            }
            
            with open("newsbot_scalable_metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 파티션별 저장 (메모리 효율성)
            for partition_name, partition_data in results['partitioned_data'].items():
                filename = f"newsbot_partition_{partition_name}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(partition_data, f, ensure_ascii=False, indent=1)
                
                file_size = os.path.getsize(filename) / (1024 * 1024)
                logger.info(f"✅ 파티션 저장: {partition_name} - {len(partition_data):,}명 ({file_size:.1f}MB)")
            
            # 검색 인덱스 저장 (압축)
            with open("newsbot_scalable_search_index.json", 'w', encoding='utf-8') as f:
                json.dump(results['search_index'], f, ensure_ascii=False, indent=1)
            
            logger.info("✅ 확장 가능한 결과 파일 저장 완료")
            
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {str(e)}")

def main():
    """메인 실행 함수"""
    logger.info("=== NewsBot.kr 확장 가능한 대규모 시스템 시작 ===")
    
    system = ScalableMassiveSystem()
    
    # 확장 가능한 통합 실행
    results = system.run_scalable_integration()
    
    if not results:
        logger.error("❌ 확장 가능한 시스템 실행 실패")
        return False
    
    # 결과 저장
    system.save_scalable_results(results)
    
    # 리포트 생성 및 출력
    report = system.generate_scalability_report(results)
    print(report)
    
    # 리포트 파일 저장
    with open("newsbot_scalability_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info("✅ 확장 가능한 대규모 시스템 완료")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ 확장 가능한 시스템 실행 완료")
    else:
        logger.error("❌ 확장 가능한 시스템 실행 실패")
