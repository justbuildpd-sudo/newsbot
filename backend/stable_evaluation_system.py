#!/usr/bin/env python3
"""
안정적인 정치인 평가 시스템
API 없이도 작동하는 완전한 평가 지표 제공
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import statistics
from collections import defaultdict, Counter

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class StableEvaluationSystem:
    def __init__(self, db_path: str = "data/legislative_data_standalone.db"):
        self.db_path = db_path
        self.init_database()
        self.load_politician_data()
    
    def init_database(self):
        """안정적인 평가를 위한 데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 통합 평가 결과 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stable_politician_evaluation (
                politician_name TEXT PRIMARY KEY,
                total_bills INTEGER DEFAULT 0,
                policy_bills INTEGER DEFAULT 0,
                administrative_bills INTEGER DEFAULT 0,
                technical_bills INTEGER DEFAULT 0,
                bill_cleanup_bills INTEGER DEFAULT 0,
                substantial_bills INTEGER DEFAULT 0,
                passage_rate REAL DEFAULT 0.0,
                avg_policy_impact REAL DEFAULT 0.0,
                avg_legislative_quality REAL DEFAULT 0.0,
                avg_public_interest REAL DEFAULT 0.0,
                avg_innovation REAL DEFAULT 0.0,
                political_intent_score REAL DEFAULT 0.0,
                policy_intent_score REAL DEFAULT 0.0,
                legislative_strategy_score REAL DEFAULT 0.0,
                timing_intent_score REAL DEFAULT 0.0,
                intent_consistency_score REAL DEFAULT 0.0,
                political_agenda_score REAL DEFAULT 0.0,
                bill_diversity_score REAL DEFAULT 0.0,
                committee_activity_score REAL DEFAULT 0.0,
                collaboration_score REAL DEFAULT 0.0,
                total_evaluation_score REAL DEFAULT 0.0,
                ranking INTEGER DEFAULT 0,
                evaluation_category TEXT,
                strengths TEXT,
                weaknesses TEXT,
                recommendations TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 의원 기본 정보 테이블 (API 없이 사용)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS politician_profiles (
                politician_name TEXT PRIMARY KEY,
                party TEXT,
                district TEXT,
                committee TEXT,
                profile_image_url TEXT,
                birth_year INTEGER,
                education TEXT,
                career TEXT,
                major_achievements TEXT,
                political_orientation TEXT,
                constituency_characteristics TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 법안별 상세 평가 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bill_detailed_evaluation (
                bill_id TEXT PRIMARY KEY,
                bill_no TEXT,
                bill_name TEXT,
                proposer_name TEXT,
                proposal_date TEXT,
                committee_name TEXT,
                bill_status TEXT,
                bill_category TEXT,
                policy_impact_score REAL DEFAULT 0.0,
                legislative_quality_score REAL DEFAULT 0.0,
                public_interest_score REAL DEFAULT 0.0,
                innovation_score REAL DEFAULT 0.0,
                political_intent_score REAL DEFAULT 0.0,
                policy_intent_score REAL DEFAULT 0.0,
                legislative_strategy_score REAL DEFAULT 0.0,
                timing_intent_score REAL DEFAULT 0.0,
                overall_bill_score REAL DEFAULT 0.0,
                bill_analysis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bill_id) REFERENCES real_assembly_bills_22nd (bill_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("안정적인 평가 시스템 데이터베이스 초기화 완료")
    
    def load_politician_data(self):
        """의원 기본 정보 로드 (API 없이 사용)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 기존 의원 프로필 데이터 확인
            cursor.execute('SELECT COUNT(*) FROM politician_profiles')
            existing_count = cursor.fetchone()[0]
            
            if existing_count == 0:
                # 기본 의원 프로필 데이터 생성
                self.create_basic_politician_profiles(cursor)
                conn.commit()
                logger.info("기본 의원 프로필 데이터 생성 완료")
            else:
                logger.info(f"기존 의원 프로필 데이터 사용: {existing_count}명")
                
        except Exception as e:
            logger.error(f"의원 데이터 로드 실패: {e}")
        finally:
            conn.close()
    
    def create_basic_politician_profiles(self, cursor):
        """기본 의원 프로필 데이터 생성"""
        # 실제 발의자 목록에서 의원 프로필 생성
        cursor.execute('''
            SELECT DISTINCT proposer_name, committee_name
            FROM real_assembly_bills_22nd
            WHERE proposer_name IS NOT NULL AND proposer_name != ''
            ORDER BY proposer_name
        ''')
        
        proposers = cursor.fetchall()
        
        for proposer_name, committee_name in proposers:
            # 간단한 프로필 정보 생성
            profile_data = self.generate_politician_profile(proposer_name, committee_name)
            
            cursor.execute('''
                INSERT OR REPLACE INTO politician_profiles (
                    politician_name, party, district, committee,
                    profile_image_url, birth_year, education, career,
                    major_achievements, political_orientation, constituency_characteristics
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                proposer_name,
                profile_data['party'],
                profile_data['district'],
                committee_name or '미분류',
                profile_data['profile_image_url'],
                profile_data['birth_year'],
                profile_data['education'],
                profile_data['career'],
                profile_data['major_achievements'],
                profile_data['political_orientation'],
                profile_data['constituency_characteristics']
            ))
    
    def generate_politician_profile(self, name: str, committee: str) -> Dict:
        """의원 프로필 정보 생성"""
        # 이름에서 성별 추정
        gender = "남성" if any(char in name for char in ['수', '영', '희', '정', '미', '숙']) else "남성"
        
        # 위원회에서 정치적 성향 추정
        political_orientation = "중도"
        if committee:
            if any(keyword in committee for keyword in ["환경", "복지", "교육", "보건"]):
                political_orientation = "진보"
            elif any(keyword in committee for keyword in ["국방", "행정", "기획"]):
                political_orientation = "보수"
        
        return {
            'party': "정당미분류",
            'district': "지역미분류",
            'profile_image_url': f"/static/images/politicians/{name.replace(' ', '_')}.jpg",
            'birth_year': 1960 + (hash(name) % 30),  # 1960-1990년 사이
            'education': "대학교 졸업",
            'career': f"{committee} 위원회 활동",
            'major_achievements': f"{name}의 주요 성과",
            'political_orientation': political_orientation,
            'constituency_characteristics': "지역 특성 분석 필요"
        }
    
    def calculate_comprehensive_evaluation(self):
        """종합적인 정치인 평가 계산"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 평가 결과 삭제
        cursor.execute('DELETE FROM stable_politician_evaluation')
        
        # 모든 발의자별 평가 계산
        cursor.execute('''
            SELECT DISTINCT proposer_name
            FROM real_assembly_bills_22nd
            WHERE proposer_name IS NOT NULL AND proposer_name != ''
        ''')
        
        proposers = cursor.fetchall()
        logger.info(f"총 {len(proposers)}명 발의자 평가 시작")
        
        evaluation_results = []
        
        for proposer in proposers:
            politician_name = proposer[0]
            
            try:
                # 기본 입법 성과 계산
                basic_scores = self.calculate_basic_legislative_scores(politician_name, cursor)
                
                # 의도 분석 점수 계산
                intent_scores = self.calculate_intent_scores(politician_name, cursor)
                
                # 고급 평가 지표 계산
                advanced_scores = self.calculate_advanced_scores(politician_name, cursor)
                
                # 종합 점수 계산
                total_score = self.calculate_total_score(basic_scores, intent_scores, advanced_scores)
                
                # 평가 카테고리 결정
                evaluation_category = self.determine_evaluation_category(total_score)
                
                # 강점/약점 분석
                strengths, weaknesses = self.analyze_strengths_weaknesses(
                    basic_scores, intent_scores, advanced_scores
                )
                
                # 개선 권고사항
                recommendations = self.generate_recommendations(
                    basic_scores, intent_scores, advanced_scores
                )
                
                # 결과 저장
                cursor.execute('''
                    INSERT INTO stable_politician_evaluation (
                        politician_name, total_bills, policy_bills, administrative_bills,
                        technical_bills, bill_cleanup_bills, substantial_bills, passage_rate,
                        avg_policy_impact, avg_legislative_quality, avg_public_interest,
                        avg_innovation, political_intent_score, policy_intent_score,
                        legislative_strategy_score, timing_intent_score, intent_consistency_score,
                        political_agenda_score, bill_diversity_score, committee_activity_score,
                        collaboration_score, total_evaluation_score, evaluation_category,
                        strengths, weaknesses, recommendations
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    politician_name,
                    basic_scores['total_bills'],
                    basic_scores['policy_bills'],
                    basic_scores['administrative_bills'],
                    basic_scores['technical_bills'],
                    basic_scores['bill_cleanup_bills'],
                    basic_scores['substantial_bills'],
                    basic_scores['passage_rate'],
                    basic_scores['avg_policy_impact'],
                    basic_scores['avg_legislative_quality'],
                    basic_scores['avg_public_interest'],
                    basic_scores['avg_innovation'],
                    intent_scores['political_intent'],
                    intent_scores['policy_intent'],
                    intent_scores['legislative_strategy'],
                    intent_scores['timing_intent'],
                    intent_scores['consistency'],
                    intent_scores['political_agenda'],
                    advanced_scores['bill_diversity'],
                    advanced_scores['committee_activity'],
                    advanced_scores['collaboration'],
                    total_score,
                    evaluation_category,
                    json.dumps(strengths, ensure_ascii=False),
                    json.dumps(weaknesses, ensure_ascii=False),
                    json.dumps(recommendations, ensure_ascii=False)
                ))
                
                evaluation_results.append({
                    'name': politician_name,
                    'total_score': total_score,
                    'category': evaluation_category
                })
                
            except Exception as e:
                logger.error(f"의원 평가 실패 ({politician_name}): {e}")
                continue
        
        # 랭킹 업데이트
        evaluation_results.sort(key=lambda x: x['total_score'], reverse=True)
        for i, result in enumerate(evaluation_results):
            cursor.execute('''
                UPDATE stable_politician_evaluation
                SET ranking = ?
                WHERE politician_name = ?
            ''', (i + 1, result['name']))
        
        conn.commit()
        conn.close()
        logger.info(f"종합 평가 완료: {len(evaluation_results)}명")
    
    def calculate_basic_legislative_scores(self, politician_name: str, cursor) -> Dict:
        """기본 입법 성과 점수 계산"""
        # 법안 수 및 통과율
        cursor.execute('''
            SELECT 
                COUNT(*) as total_bills,
                SUM(CASE WHEN bill_status IN ('원안가결', '가결', '공포') THEN 1 ELSE 0 END) as passed_bills,
                AVG(a.policy_impact_score) as avg_policy_impact,
                AVG(a.legislative_quality_score) as avg_legislative_quality,
                AVG(a.public_interest_score) as avg_public_interest,
                AVG(a.innovation_score) as avg_innovation
            FROM real_assembly_bills_22nd b
            LEFT JOIN real_bill_analysis_22nd a ON b.bill_id = a.bill_id
            WHERE b.proposer_name = ?
        ''', (politician_name,))
        
        result = cursor.fetchone()
        total_bills = result[0] or 0
        passed_bills = result[1] or 0
        passage_rate = (passed_bills / total_bills * 100) if total_bills > 0 else 0
        
        # 법안 카테고리별 분류
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN a.bill_category = '정책법안' THEN 1 ELSE 0 END) as policy_bills,
                SUM(CASE WHEN a.bill_category = '의안정리' THEN 1 ELSE 0 END) as bill_cleanup_bills,
                SUM(CASE WHEN a.bill_category = '기술수정' THEN 1 ELSE 0 END) as technical_bills,
                SUM(CASE WHEN a.bill_category = '실질입법' THEN 1 ELSE 0 END) as substantial_bills
            FROM real_assembly_bills_22nd b
            LEFT JOIN real_bill_analysis_22nd a ON b.bill_id = a.bill_id
            WHERE b.proposer_name = ?
        ''', (politician_name,))
        
        category_result = cursor.fetchone()
        
        return {
            'total_bills': total_bills,
            'policy_bills': category_result[0] or 0,
            'administrative_bills': 0,  # 기본값
            'technical_bills': category_result[2] or 0,
            'bill_cleanup_bills': category_result[1] or 0,
            'substantial_bills': category_result[3] or 0,
            'passage_rate': round(passage_rate, 2),
            'avg_policy_impact': round(result[2] or 0, 2),
            'avg_legislative_quality': round(result[3] or 0, 2),
            'avg_public_interest': round(result[4] or 0, 2),
            'avg_innovation': round(result[5] or 0, 2)
        }
    
    def calculate_intent_scores(self, politician_name: str, cursor) -> Dict:
        """의도 분석 점수 계산"""
        cursor.execute('''
            SELECT 
                AVG(i.political_intent_score) as avg_political_intent,
                AVG(i.policy_intent_score) as avg_policy_intent,
                AVG(i.legislative_strategy_score) as avg_legislative_strategy,
                AVG(i.timing_intent_score) as avg_timing_intent,
                AVG(i.overall_intent_score) as avg_overall_intent
            FROM real_assembly_bills_22nd b
            LEFT JOIN bill_intent_analysis i ON b.bill_id = i.bill_id
            WHERE b.proposer_name = ?
        ''', (politician_name,))
        
        result = cursor.fetchone()
        
        # 의도 일관성 점수
        cursor.execute('''
            SELECT intent_category, COUNT(*) as count
            FROM real_assembly_bills_22nd b
            LEFT JOIN bill_intent_analysis i ON b.bill_id = i.bill_id
            WHERE b.proposer_name = ? AND i.intent_category IS NOT NULL
            GROUP BY intent_category
            ORDER BY count DESC
        ''', (politician_name,))
        
        categories = cursor.fetchall()
        consistency_score = 0
        if categories:
            total_intent_bills = sum(cat[1] for cat in categories)
            max_category_count = max(cat[1] for cat in categories)
            consistency_score = (max_category_count / total_intent_bills * 100) if total_intent_bills > 0 else 0
        
        # 정치적 아젠다 점수
        political_agenda = ((result[0] or 0) * 0.4 + (result[3] or 0) * 0.3 + 
                           (result[2] or 0) * 0.2 + (result[1] or 0) * 0.1)
        
        return {
            'political_intent': round(result[0] or 0, 2),
            'policy_intent': round(result[1] or 0, 2),
            'legislative_strategy': round(result[2] or 0, 2),
            'timing_intent': round(result[3] or 0, 2),
            'consistency': round(consistency_score, 2),
            'political_agenda': round(political_agenda, 2)
        }
    
    def calculate_advanced_scores(self, politician_name: str, cursor) -> Dict:
        """고급 평가 지표 계산"""
        # 법안 다양성 점수 (다양한 위원회에서 발의)
        cursor.execute('''
            SELECT COUNT(DISTINCT committee_name) as committee_count
            FROM real_assembly_bills_22nd
            WHERE proposer_name = ? AND committee_name IS NOT NULL
        ''', (politician_name,))
        
        committee_count = cursor.fetchone()[0] or 0
        bill_diversity = min(committee_count * 10, 100)  # 최대 100점
        
        # 위원회 활동 점수
        cursor.execute('''
            SELECT committee_name, COUNT(*) as bill_count
            FROM real_assembly_bills_22nd
            WHERE proposer_name = ? AND committee_name IS NOT NULL
            GROUP BY committee_name
            ORDER BY bill_count DESC
        ''', (politician_name,))
        
        committee_activity = 0
        if committee_count > 0:
            # 가장 활발한 위원회에서의 활동 비율
            committee_activity = min(committee_count * 15, 100)
        
        # 협력 점수 (공동발의 참여)
        cursor.execute('''
            SELECT COUNT(*) as collaboration_count
            FROM real_assembly_bills_22nd
            WHERE proposer_name = ? AND co_proposers IS NOT NULL AND co_proposers != ''
        ''', (politician_name,))
        
        collaboration_count = cursor.fetchone()[0] or 0
        collaboration_score = min(collaboration_count * 5, 100)  # 최대 100점
        
        return {
            'bill_diversity': round(bill_diversity, 2),
            'committee_activity': round(committee_activity, 2),
            'collaboration': round(collaboration_score, 2)
        }
    
    def calculate_total_score(self, basic_scores: Dict, intent_scores: Dict, advanced_scores: Dict) -> float:
        """종합 점수 계산"""
        # 가중치 적용
        total_score = (
            basic_scores['total_bills'] * 0.15 +  # 법안 수
            basic_scores['passage_rate'] * 0.20 +  # 통과율
            basic_scores['avg_policy_impact'] * 0.15 +  # 정책 영향도
            basic_scores['avg_legislative_quality'] * 0.10 +  # 입법 품질
            intent_scores['political_agenda'] * 0.15 +  # 정치적 아젠다
            intent_scores['consistency'] * 0.10 +  # 의도 일관성
            advanced_scores['bill_diversity'] * 0.05 +  # 법안 다양성
            advanced_scores['collaboration'] * 0.05 +  # 협력
            advanced_scores['committee_activity'] * 0.05  # 위원회 활동
        )
        
        return round(total_score, 2)
    
    def determine_evaluation_category(self, total_score: float) -> str:
        """평가 카테고리 결정"""
        if total_score >= 80:
            return "우수"
        elif total_score >= 60:
            return "양호"
        elif total_score >= 40:
            return "보통"
        elif total_score >= 20:
            return "미흡"
        else:
            return "부족"
    
    def analyze_strengths_weaknesses(self, basic_scores: Dict, intent_scores: Dict, advanced_scores: Dict) -> Tuple[List, List]:
        """강점/약점 분석"""
        strengths = []
        weaknesses = []
        
        # 강점 분석
        if basic_scores['total_bills'] >= 5:
            strengths.append("활발한 입법 활동")
        if basic_scores['passage_rate'] >= 70:
            strengths.append("높은 법안 통과율")
        if basic_scores['avg_policy_impact'] >= 50:
            strengths.append("높은 정책 영향도")
        if intent_scores['consistency'] >= 70:
            strengths.append("일관된 입법 철학")
        if advanced_scores['collaboration'] >= 50:
            strengths.append("협력적 입법 활동")
        
        # 약점 분석
        if basic_scores['total_bills'] < 2:
            weaknesses.append("입법 활동 부족")
        if basic_scores['passage_rate'] < 30:
            weaknesses.append("낮은 법안 통과율")
        if basic_scores['avg_policy_impact'] < 30:
            weaknesses.append("낮은 정책 영향도")
        if intent_scores['consistency'] < 40:
            weaknesses.append("일관성 부족")
        if advanced_scores['bill_diversity'] < 30:
            weaknesses.append("법안 다양성 부족")
        
        return strengths, weaknesses
    
    def generate_recommendations(self, basic_scores: Dict, intent_scores: Dict, advanced_scores: Dict) -> List:
        """개선 권고사항 생성"""
        recommendations = []
        
        if basic_scores['total_bills'] < 3:
            recommendations.append("더 많은 법안 발의를 통한 입법 활동 증대")
        if basic_scores['passage_rate'] < 50:
            recommendations.append("법안 품질 향상 및 통과율 개선")
        if basic_scores['avg_policy_impact'] < 40:
            recommendations.append("정책 영향도가 높은 법안 발의")
        if intent_scores['consistency'] < 50:
            recommendations.append("일관된 입법 철학 정립")
        if advanced_scores['collaboration'] < 40:
            recommendations.append("다른 의원과의 협력 강화")
        if advanced_scores['bill_diversity'] < 40:
            recommendations.append("다양한 분야의 법안 발의")
        
        return recommendations
    
    def generate_evaluation_report(self) -> Dict:
        """평가 보고서 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 전체 통계
            cursor.execute('SELECT COUNT(*) FROM stable_politician_evaluation')
            total_evaluated = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(total_evaluation_score) FROM stable_politician_evaluation')
            avg_score = cursor.fetchone()[0] or 0
            
            # 카테고리별 분포
            cursor.execute('''
                SELECT evaluation_category, COUNT(*) as count
                FROM stable_politician_evaluation
                GROUP BY evaluation_category
                ORDER BY count DESC
            ''')
            category_distribution = {row[0]: row[1] for row in cursor.fetchall()}
            
            # 상위 10명
            cursor.execute('''
                SELECT politician_name, total_evaluation_score, evaluation_category
                FROM stable_politician_evaluation
                ORDER BY total_evaluation_score DESC
                LIMIT 10
            ''')
            top_10 = [{"name": row[0], "score": row[1], "category": row[2]} for row in cursor.fetchall()]
            
            # 하위 10명
            cursor.execute('''
                SELECT politician_name, total_evaluation_score, evaluation_category
                FROM stable_politician_evaluation
                ORDER BY total_evaluation_score ASC
                LIMIT 10
            ''')
            bottom_10 = [{"name": row[0], "score": row[1], "category": row[2]} for row in cursor.fetchall()]
            
            report = {
                "evaluation_date": datetime.now().isoformat(),
                "total_evaluated_politicians": total_evaluated,
                "average_score": round(avg_score, 2),
                "category_distribution": category_distribution,
                "top_10_politicians": top_10,
                "bottom_10_politicians": bottom_10,
                "evaluation_criteria": {
                    "legislative_activity": "입법 활동량 (15%)",
                    "passage_rate": "법안 통과율 (20%)",
                    "policy_impact": "정책 영향도 (15%)",
                    "legislative_quality": "입법 품질 (10%)",
                    "political_agenda": "정치적 아젠다 (15%)",
                    "intent_consistency": "의도 일관성 (10%)",
                    "bill_diversity": "법안 다양성 (5%)",
                    "collaboration": "협력 활동 (5%)",
                    "committee_activity": "위원회 활동 (5%)"
                }
            }
            
            # 보고서 저장
            with open("data/stable_evaluation_report.json", 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info("안정적인 평가 보고서 생성 완료")
            return report
            
        except Exception as e:
            logger.error(f"평가 보고서 생성 실패: {e}")
            return {}
        finally:
            conn.close()
    
    def run_stable_evaluation(self):
        """안정적인 평가 시스템 실행"""
        logger.info("안정적인 정치인 평가 시스템 시작")
        
        # 1. 종합적인 평가 계산
        logger.info("1단계: 종합적인 평가 계산")
        self.calculate_comprehensive_evaluation()
        
        # 2. 평가 보고서 생성
        logger.info("2단계: 평가 보고서 생성")
        report = self.generate_evaluation_report()
        
        logger.info("안정적인 정치인 평가 시스템 완료")
        return report

if __name__ == "__main__":
    evaluator = StableEvaluationSystem()
    report = evaluator.run_stable_evaluation()
    
    if report:
        print("✅ 안정적인 정치인 평가 시스템이 성공적으로 완료되었습니다.")
        print(f"📊 평가된 의원 수: {report.get('total_evaluated_politicians', 0)}명")
        print(f"📈 평균 점수: {report.get('average_score', 0)}점")
    else:
        print("❌ 평가 시스템 실행 중 오류가 발생했습니다.")

