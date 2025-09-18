#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOD 데이터 진실성 검증 시스템
기존 298명 현직 국회의원 데이터와 LOD에서 수집한 데이터를 교차검증합니다.
"""

import json
import logging
from typing import Dict, List, Tuple, Set
from datetime import datetime
import difflib

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataVerificationSystem:
    """데이터 진실성 검증 클래스"""
    
    def __init__(self):
        self.existing_members = []
        self.lod_candidates = []
        self.verification_results = {
            'matched_members': [],
            'missing_members': [],
            'extra_candidates': [],
            'data_conflicts': [],
            'statistics': {}
        }
    
    def load_existing_members(self, file_path: str) -> bool:
        """기존 298명 현직 국회의원 데이터를 로드합니다."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 다양한 데이터 형식 지원
            if isinstance(data, list):
                self.existing_members = data
            elif isinstance(data, dict):
                if 'candidates' in data:
                    self.existing_members = data['candidates']
                elif 'members' in data:
                    self.existing_members = data['members']
                else:
                    # 첫 번째 리스트 타입 값을 찾기
                    for value in data.values():
                        if isinstance(value, list):
                            self.existing_members = value
                            break
            
            logger.info(f"✅ 기존 의원 데이터 로드 완료: {len(self.existing_members)}명")
            return True
            
        except Exception as e:
            logger.error(f"❌ 기존 의원 데이터 로드 실패: {str(e)}")
            return False
    
    def load_lod_candidates(self, file_path: str) -> bool:
        """LOD에서 수집한 후보자 데이터를 로드합니다."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'candidates' in data:
                self.lod_candidates = data['candidates']
            else:
                self.lod_candidates = data
                
            logger.info(f"✅ LOD 후보자 데이터 로드 완료: {len(self.lod_candidates)}명")
            return True
            
        except Exception as e:
            logger.error(f"❌ LOD 후보자 데이터 로드 실패: {str(e)}")
            return False
    
    def normalize_name(self, name: str) -> str:
        """이름을 정규화합니다."""
        if not name:
            return ""
        
        # 한자명을 한글로 변환하는 간단한 매핑 (확장 가능)
        hanja_to_hangul = {
            '權性東': '권성동',
            '鄭東泳': '정동영',
            '張耿態': '장경태',
            '韓政旼': '한정민',
            '李壽珍': '이수진',
            '朴洙瑩': '박수영',
            '朱晋佑': '주진우',
            '金福德': '김복덕'
        }
        
        # 한자명이면 한글로 변환
        if name in hanja_to_hangul:
            return hanja_to_hangul[name]
        
        # 공백 제거 및 소문자 변환
        return name.strip().lower()
    
    def find_best_match(self, target_name: str, candidate_list: List[Dict]) -> Tuple[Dict, float]:
        """가장 유사한 이름을 찾습니다."""
        best_match = None
        best_score = 0.0
        
        target_normalized = self.normalize_name(target_name)
        
        for candidate in candidate_list:
            candidate_name = candidate.get('name', '')
            candidate_normalized = self.normalize_name(candidate_name)
            
            # 정확히 일치하는 경우
            if target_normalized == candidate_normalized:
                return candidate, 1.0
            
            # 유사도 계산
            similarity = difflib.SequenceMatcher(None, target_normalized, candidate_normalized).ratio()
            
            if similarity > best_score:
                best_score = similarity
                best_match = candidate
        
        return best_match, best_score
    
    def verify_member_data(self, existing_member: Dict, lod_candidate: Dict) -> Dict:
        """개별 의원 데이터를 검증합니다."""
        conflicts = []
        
        # 정당 비교
        existing_party = existing_member.get('party', '').strip()
        lod_party = lod_candidate.get('party', '').strip()
        
        if existing_party and lod_party and existing_party != lod_party:
            conflicts.append({
                'field': 'party',
                'existing': existing_party,
                'lod': lod_party
            })
        
        # 선거구 비교
        existing_district = existing_member.get('district', '').strip()
        lod_district = lod_candidate.get('district', '').strip()
        
        if existing_district and lod_district and existing_district != lod_district:
            conflicts.append({
                'field': 'district',
                'existing': existing_district,
                'lod': lod_district
            })
        
        return {
            'name': existing_member.get('name', ''),
            'conflicts': conflicts,
            'lod_data': {
                'vote_count': lod_candidate.get('vote_count'),
                'vote_rate': lod_candidate.get('vote_rate'),
                'is_elected': lod_candidate.get('is_elected', False)
            }
        }
    
    def run_verification(self) -> Dict:
        """전체 데이터 검증을 실행합니다."""
        logger.info("🔍 데이터 진실성 검증 시작")
        
        # LOD에서 당선자만 필터링
        lod_winners = [c for c in self.lod_candidates if c.get('is_elected', False)]
        logger.info(f"📊 LOD 당선자: {len(lod_winners)}명")
        
        matched_count = 0
        missing_members = []
        data_conflicts = []
        
        # 기존 298명과 LOD 당선자 매칭
        for existing_member in self.existing_members:
            existing_name = existing_member.get('name', '')
            
            # LOD에서 가장 유사한 후보 찾기
            best_match, similarity = self.find_best_match(existing_name, lod_winners)
            
            if similarity >= 0.8:  # 80% 이상 유사도
                matched_count += 1
                
                # 데이터 검증
                verification_result = self.verify_member_data(existing_member, best_match)
                
                if verification_result['conflicts']:
                    data_conflicts.append(verification_result)
                
                self.verification_results['matched_members'].append({
                    'existing': existing_member,
                    'lod': best_match,
                    'similarity': similarity,
                    'verification': verification_result
                })
            else:
                missing_members.append({
                    'name': existing_name,
                    'data': existing_member,
                    'best_match': best_match,
                    'similarity': similarity
                })
        
        # LOD에만 있는 당선자 찾기
        existing_names = {self.normalize_name(m.get('name', '')) for m in self.existing_members}
        extra_candidates = []
        
        for lod_winner in lod_winners:
            lod_name_normalized = self.normalize_name(lod_winner.get('name', ''))
            
            if lod_name_normalized not in existing_names:
                # 유사한 이름이 있는지 확인
                _, similarity = self.find_best_match(lod_winner.get('name', ''), self.existing_members)
                
                if similarity < 0.8:  # 유사도가 낮으면 추가 후보로 분류
                    extra_candidates.append(lod_winner)
        
        # 결과 정리
        self.verification_results.update({
            'missing_members': missing_members,
            'extra_candidates': extra_candidates,
            'data_conflicts': data_conflicts,
            'statistics': {
                'existing_members_count': len(self.existing_members),
                'lod_winners_count': len(lod_winners),
                'lod_total_candidates': len(self.lod_candidates),
                'matched_count': matched_count,
                'missing_count': len(missing_members),
                'extra_count': len(extra_candidates),
                'conflicts_count': len(data_conflicts),
                'match_rate': (matched_count / len(self.existing_members)) * 100 if self.existing_members else 0,
                'verification_timestamp': datetime.now().isoformat()
            }
        })
        
        logger.info("✅ 데이터 진실성 검증 완료")
        return self.verification_results
    
    def generate_report(self) -> str:
        """검증 결과 리포트를 생성합니다."""
        stats = self.verification_results['statistics']
        
        report = f"""
🔍 데이터 진실성 검증 리포트
{'='*50}

📊 기본 통계:
- 기존 현직 의원: {stats['existing_members_count']}명
- LOD 전체 후보자: {stats['lod_total_candidates']}명
- LOD 당선자: {stats['lod_winners_count']}명

🎯 매칭 결과:
- 매칭 성공: {stats['matched_count']}명 ({stats['match_rate']:.1f}%)
- 매칭 실패: {stats['missing_count']}명
- LOD 추가 당선자: {stats['extra_count']}명
- 데이터 충돌: {stats['conflicts_count']}명

"""
        
        if self.verification_results['missing_members']:
            report += "\n❌ 매칭되지 않은 현직 의원:\n"
            for missing in self.verification_results['missing_members'][:10]:  # 상위 10명만 표시
                report += f"   - {missing['name']} (유사도: {missing['similarity']:.2f})\n"
        
        if self.verification_results['extra_candidates']:
            report += "\n➕ LOD 추가 당선자:\n"
            for extra in self.verification_results['extra_candidates'][:10]:  # 상위 10명만 표시
                report += f"   - {extra.get('name')} ({extra.get('party')}, {extra.get('district')})\n"
        
        if self.verification_results['data_conflicts']:
            report += "\n⚠️ 데이터 충돌:\n"
            for conflict in self.verification_results['data_conflicts'][:5]:  # 상위 5명만 표시
                report += f"   - {conflict['name']}:\n"
                for c in conflict['conflicts']:
                    report += f"     * {c['field']}: '{c['existing']}' vs '{c['lod']}'\n"
        
        return report
    
    def save_results(self, filename: str):
        """검증 결과를 파일로 저장합니다."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.verification_results, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 검증 결과 저장 완료: {filename}")
        except Exception as e:
            logger.error(f"❌ 검증 결과 저장 실패: {str(e)}")

def main():
    """메인 실행 함수"""
    logger.info("=== LOD 데이터 진실성 검증 시작 ===")
    
    verifier = DataVerificationSystem()
    
    # 기존 298명 현직 의원 데이터 로드
    existing_files = [
        "final_298_current_assembly.json",
        "updated_298_current_assembly.json", 
        "enhanced_298_members_with_contact.json",
        "../politicians_data_with_party.json"
    ]
    
    loaded = False
    for file_path in existing_files:
        if verifier.load_existing_members(file_path):
            loaded = True
            break
    
    if not loaded:
        logger.error("❌ 기존 의원 데이터를 로드할 수 없습니다")
        return False
    
    # LOD 후보자 데이터 로드 대기
    lod_file = "candidate_details_full.json"
    
    import os
    import time
    
    # LOD 데이터 수집 완료 대기
    while not os.path.exists(lod_file):
        logger.info("⏳ LOD 데이터 수집 완료 대기 중...")
        time.sleep(10)
    
    # 파일이 완전히 생성될 때까지 대기
    time.sleep(5)
    
    if not verifier.load_lod_candidates(lod_file):
        logger.error("❌ LOD 후보자 데이터를 로드할 수 없습니다")
        return False
    
    # 검증 실행
    results = verifier.run_verification()
    
    # 결과 저장
    verifier.save_results("data_verification_results.json")
    
    # 리포트 생성 및 출력
    report = verifier.generate_report()
    print(report)
    
    # 리포트 파일 저장
    with open("data_verification_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info("✅ 데이터 진실성 검증 완료")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ 검증 시스템 실행 완료")
    else:
        logger.error("❌ 검증 시스템 실행 실패")
