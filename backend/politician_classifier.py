#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
정치인 분류 시스템
LOD에서 수집한 693명의 후보자를 당선자/낙선자, 현직/전직으로 분류합니다.
"""

import json
import logging
from typing import Dict, List, Set
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PoliticianClassifier:
    """정치인 분류 클래스"""
    
    def __init__(self):
        self.lod_candidates = []
        self.classification_results = {
            'current_assembly_members': [],    # 현직 국회의원 (당선자)
            'former_politicians': [],          # 전직/예비 정치인 (낙선자)
            'statistics': {},
            'party_analysis': {},
            'district_analysis': {}
        }
    
    def load_lod_data(self, file_path: str) -> bool:
        """LOD 후보자 데이터를 로드합니다."""
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
    
    def classify_by_election_result(self) -> Dict:
        """선거 결과에 따라 당선자/낙선자를 분류합니다."""
        winners = []
        losers = []
        unknown = []
        
        for candidate in self.lod_candidates:
            is_elected = candidate.get('is_elected', False)
            candidate_type = candidate.get('candidate_type', '')
            
            # WinCandidate 클래스이거나 is_elected가 True인 경우
            if is_elected or candidate_type == 'WinCandidate':
                winners.append(candidate)
            elif candidate_type == 'Candidate':
                losers.append(candidate)
            else:
                unknown.append(candidate)
        
        logger.info(f"📊 선거 결과 분류 - 당선: {len(winners)}명, 낙선: {len(losers)}명, 미확인: {len(unknown)}명")
        
        return {
            'winners': winners,
            'losers': losers,
            'unknown': unknown
        }
    
    def analyze_parties(self, candidates: List[Dict]) -> Dict:
        """정당별 분석을 수행합니다."""
        party_stats = {}
        
        for candidate in candidates:
            party = candidate.get('party', '미상').strip()
            if not party:
                party = '미상'
            
            if party not in party_stats:
                party_stats[party] = {
                    'count': 0,
                    'total_votes': 0,
                    'candidates': []
                }
            
            party_stats[party]['count'] += 1
            party_stats[party]['total_votes'] += candidate.get('vote_count', 0) or 0
            party_stats[party]['candidates'].append({
                'name': candidate.get('name'),
                'district': candidate.get('district'),
                'vote_count': candidate.get('vote_count'),
                'vote_rate': candidate.get('vote_rate')
            })
        
        # 정당별 정렬 (후보자 수 기준)
        sorted_parties = sorted(party_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        
        return dict(sorted_parties)
    
    def analyze_districts(self, candidates: List[Dict]) -> Dict:
        """선거구별 분석을 수행합니다."""
        district_stats = {}
        
        for candidate in candidates:
            district = candidate.get('district', '미상').strip()
            if not district:
                district = '미상'
            
            if district not in district_stats:
                district_stats[district] = {
                    'candidates': [],
                    'total_candidates': 0,
                    'winner': None
                }
            
            district_stats[district]['candidates'].append(candidate)
            district_stats[district]['total_candidates'] += 1
            
            # 당선자 찾기
            if candidate.get('is_elected', False):
                district_stats[district]['winner'] = candidate
        
        return district_stats
    
    def enrich_candidate_data(self, candidate: Dict) -> Dict:
        """후보자 데이터를 보강합니다."""
        enriched = candidate.copy()
        
        # 정치인 경력 분석
        career = candidate.get('career', '')
        occupation = candidate.get('occupationDetail', '')
        
        # 현직/전직 여부 판단
        is_incumbent = False
        political_experience = []
        
        if career:
            career_lower = career.lower()
            if '국회의원' in career or '의원' in career:
                political_experience.append('국회의원')
            if '장관' in career or 'minister' in career_lower:
                political_experience.append('장관')
            if '시장' in career or '도지사' in career or '군수' in career:
                political_experience.append('지방자치단체장')
            if '대통령' in career or 'president' in career_lower:
                political_experience.append('대통령')
        
        if occupation:
            if '국회의원' in occupation:
                is_incumbent = True
        
        # 연령대 분류
        age = candidate.get('age')
        age_group = '미상'
        if age:
            try:
                age_num = int(age)
                if age_num < 40:
                    age_group = '30대 이하'
                elif age_num < 50:
                    age_group = '40대'
                elif age_num < 60:
                    age_group = '50대'
                elif age_num < 70:
                    age_group = '60대'
                else:
                    age_group = '70대 이상'
            except:
                pass
        
        # 득표율 등급
        vote_rate = candidate.get('vote_rate', 0) or 0
        if vote_rate >= 70:
            vote_grade = '압승'
        elif vote_rate >= 60:
            vote_grade = '승리'
        elif vote_rate >= 50:
            vote_grade = '근소승'
        elif vote_rate >= 40:
            vote_grade = '근소패'
        elif vote_rate > 0:
            vote_grade = '패배'
        else:
            vote_grade = '미상'
        
        enriched.update({
            'is_incumbent': is_incumbent,
            'political_experience': political_experience,
            'age_group': age_group,
            'vote_grade': vote_grade,
            'classification_timestamp': datetime.now().isoformat()
        })
        
        return enriched
    
    def run_classification(self) -> Dict:
        """전체 분류 작업을 실행합니다."""
        logger.info("🔄 정치인 분류 시작")
        
        # 1. 당선자/낙선자 분류
        election_results = self.classify_by_election_result()
        
        # 2. 데이터 보강
        enriched_winners = [self.enrich_candidate_data(c) for c in election_results['winners']]
        enriched_losers = [self.enrich_candidate_data(c) for c in election_results['losers']]
        
        # 3. 정당별 분석
        winner_party_analysis = self.analyze_parties(enriched_winners)
        loser_party_analysis = self.analyze_parties(enriched_losers)
        
        # 4. 선거구별 분석
        district_analysis = self.analyze_districts(self.lod_candidates)
        
        # 5. 통계 생성
        statistics = {
            'total_candidates': len(self.lod_candidates),
            'winners_count': len(enriched_winners),
            'losers_count': len(enriched_losers),
            'unknown_count': len(election_results['unknown']),
            'parties_count': len(set(c.get('party', '') for c in self.lod_candidates if c.get('party'))),
            'districts_count': len(set(c.get('district', '') for c in self.lod_candidates if c.get('district'))),
            'average_vote_rate_winners': sum(c.get('vote_rate', 0) or 0 for c in enriched_winners) / len(enriched_winners) if enriched_winners else 0,
            'average_vote_rate_losers': sum(c.get('vote_rate', 0) or 0 for c in enriched_losers) / len(enriched_losers) if enriched_losers else 0,
            'classification_timestamp': datetime.now().isoformat()
        }
        
        # 결과 저장
        self.classification_results = {
            'current_assembly_members': enriched_winners,
            'former_politicians': enriched_losers,
            'unknown_candidates': election_results['unknown'],
            'statistics': statistics,
            'party_analysis': {
                'winners': winner_party_analysis,
                'losers': loser_party_analysis
            },
            'district_analysis': district_analysis
        }
        
        logger.info("✅ 정치인 분류 완료")
        return self.classification_results
    
    def generate_classification_report(self) -> str:
        """분류 결과 리포트를 생성합니다."""
        stats = self.classification_results['statistics']
        
        report = f"""
🏛️ 정치인 분류 결과 리포트
{'='*50}

📊 전체 통계:
- 전체 후보자: {stats['total_candidates']}명
- 당선자 (현직 국회의원): {stats['winners_count']}명
- 낙선자 (전직/예비 정치인): {stats['losers_count']}명
- 미분류: {stats['unknown_count']}명
- 참여 정당 수: {stats['parties_count']}개
- 선거구 수: {stats['districts_count']}개

📈 득표율 분석:
- 당선자 평균 득표율: {stats['average_vote_rate_winners']:.1f}%
- 낙선자 평균 득표율: {stats['average_vote_rate_losers']:.1f}%

"""
        
        # 주요 정당 분석 (당선자)
        winner_parties = self.classification_results['party_analysis']['winners']
        if winner_parties:
            report += "\n🏆 주요 정당 (당선자):\n"
            for party, data in list(winner_parties.items())[:10]:
                avg_votes = data['total_votes'] / data['count'] if data['count'] > 0 else 0
                report += f"   - {party}: {data['count']}명 (평균 {avg_votes:,.0f}표)\n"
        
        # 주요 정당 분석 (낙선자)
        loser_parties = self.classification_results['party_analysis']['losers']
        if loser_parties:
            report += "\n📉 주요 정당 (낙선자):\n"
            for party, data in list(loser_parties.items())[:10]:
                avg_votes = data['total_votes'] / data['count'] if data['count'] > 0 else 0
                report += f"   - {party}: {data['count']}명 (평균 {avg_votes:,.0f}표)\n"
        
        return report
    
    def save_results(self, filename: str):
        """분류 결과를 파일로 저장합니다."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.classification_results, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 분류 결과 저장 완료: {filename}")
        except Exception as e:
            logger.error(f"❌ 분류 결과 저장 실패: {str(e)}")

def main():
    """메인 실행 함수"""
    logger.info("=== 정치인 분류 시스템 시작 ===")
    
    classifier = PoliticianClassifier()
    
    # LOD 데이터 로드 대기
    lod_file = "candidate_details_full.json"
    
    import os
    import time
    
    # LOD 데이터 수집 완료 대기
    while not os.path.exists(lod_file):
        logger.info("⏳ LOD 데이터 수집 완료 대기 중...")
        time.sleep(10)
    
    # 파일이 완전히 생성될 때까지 대기
    time.sleep(5)
    
    if not classifier.load_lod_data(lod_file):
        logger.error("❌ LOD 데이터를 로드할 수 없습니다")
        return False
    
    # 분류 실행
    results = classifier.run_classification()
    
    # 결과 저장
    classifier.save_results("politician_classification_results.json")
    
    # 리포트 생성 및 출력
    report = classifier.generate_classification_report()
    print(report)
    
    # 리포트 파일 저장
    with open("politician_classification_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info("✅ 정치인 분류 완료")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ 분류 시스템 실행 완료")
    else:
        logger.error("❌ 분류 시스템 실행 실패")

