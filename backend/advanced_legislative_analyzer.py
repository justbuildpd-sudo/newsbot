#!/usr/bin/env python3
"""
고도화된 입법 의도 분석 시스템
모든 법안을 세밀하게 관측하여 발의의원의 의도를 파악
"""

import sqlite3
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics
from collections import Counter, defaultdict
import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class AdvancedLegislativeAnalyzer:
    def __init__(self, db_path: str = "data/legislative_data_standalone.db"):
        self.db_path = db_path
        self.init_database()
        
        # 의도 분석을 위한 키워드 사전
        self.intent_keywords = {
            "정치적_의도": {
                "선거_관련": ["선거", "투표", "정당", "후보", "공천", "지지", "표심"],
                "정치_공학": ["여론", "지지율", "인기", "이슈", "화제", "관심"],
                "정치_적대": ["반대", "비판", "공격", "문제", "잘못", "실패"],
                "정치_연합": ["협력", "연대", "공동", "합의", "협상", "지지"]
            },
            "정책_의도": {
                "복지_확대": ["복지", "지원", "보조금", "수당", "혜택", "혜택"],
                "경제_성장": ["경제", "성장", "발전", "투자", "창업", "일자리"],
                "환경_보호": ["환경", "친환경", "탄소", "기후", "녹색", "재생"],
                "교육_개선": ["교육", "학교", "학생", "교사", "학습", "육성"],
                "안전_강화": ["안전", "보안", "방어", "보호", "예방", "대응"]
            },
            "입법_전략": {
                "점진적_개혁": ["일부개정", "단계적", "점진", "점진적", "단계"],
                "전면_개혁": ["전부개정", "전면", "대폭", "근본", "혁신"],
                "기술적_수정": ["기술적", "문구", "표현", "용어", "정의"],
                "실질_입법": ["신설", "신규", "추가", "확대", "강화", "도입"]
            },
            "정치적_타이밍": {
                "선거_전": ["선거", "투표", "후보", "공천", "지지"],
                "정부_정책_지지": ["정부", "정책", "지원", "추진", "실시"],
                "야당_비판": ["비판", "문제", "잘못", "실패", "책임"],
                "여론_대응": ["여론", "지지율", "인기", "이슈", "관심"]
            }
        }
        
        # 법안 유형별 의도 패턴
        self.bill_type_patterns = {
            "법률안": {
                "정책_법안": ["신설", "신규", "추가", "확대", "강화", "도입"],
                "의안_정리": ["일부개정", "전부개정", "폐지", "정리", "정비"],
                "기술_수정": ["기술적", "문구", "표현", "용어", "정의", "절차"]
            }
        }
    
    def init_database(self):
        """고도화된 분석을 위한 데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 의도 분석 결과 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bill_intent_analysis (
                bill_id TEXT PRIMARY KEY,
                political_intent_score REAL DEFAULT 0.0,
                policy_intent_score REAL DEFAULT 0.0,
                legislative_strategy_score REAL DEFAULT 0.0,
                timing_intent_score REAL DEFAULT 0.0,
                overall_intent_score REAL DEFAULT 0.0,
                intent_category TEXT,
                intent_keywords TEXT,
                intent_analysis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bill_id) REFERENCES real_assembly_bills_22nd (bill_id)
            )
        ''')
        
        # 의원별 의도 패턴 분석 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS politician_intent_patterns (
                politician_name TEXT PRIMARY KEY,
                total_bills INTEGER DEFAULT 0,
                political_intent_avg REAL DEFAULT 0.0,
                policy_intent_avg REAL DEFAULT 0.0,
                legislative_strategy_avg REAL DEFAULT 0.0,
                timing_intent_avg REAL DEFAULT 0.0,
                overall_intent_avg REAL DEFAULT 0.0,
                dominant_intent_category TEXT,
                intent_consistency_score REAL DEFAULT 0.0,
                political_agenda_score REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 법안 간 연관성 분석 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bill_relationships (
                bill_id_1 TEXT,
                bill_id_2 TEXT,
                similarity_score REAL DEFAULT 0.0,
                relationship_type TEXT,
                common_keywords TEXT,
                proposer_overlap INTEGER DEFAULT 0,
                committee_overlap INTEGER DEFAULT 0,
                timing_proximity INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (bill_id_1, bill_id_2),
                FOREIGN KEY (bill_id_1) REFERENCES real_assembly_bills_22nd (bill_id),
                FOREIGN KEY (bill_id_2) REFERENCES real_assembly_bills_22nd (bill_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("고도화된 분석 데이터베이스 초기화 완료")
    
    def analyze_bill_intent(self, bill_name: str, bill_type: str, committee: str, 
                           proposer_name: str, proposal_date: str) -> Dict:
        """개별 법안의 의도 분석"""
        
        combined_text = f"{bill_name} {bill_type} {committee} {proposer_name}".lower()
        
        # 1. 정치적 의도 분석
        political_intent_score = 0
        political_keywords = []
        
        for category, keywords in self.intent_keywords["정치적_의도"].items():
            for keyword in keywords:
                if keyword in combined_text:
                    political_intent_score += 1
                    political_keywords.append(keyword)
        
        # 2. 정책 의도 분석
        policy_intent_score = 0
        policy_keywords = []
        
        for category, keywords in self.intent_keywords["정책_의도"].items():
            for keyword in keywords:
                if keyword in combined_text:
                    policy_intent_score += 1
                    policy_keywords.append(keyword)
        
        # 3. 입법 전략 분석
        legislative_strategy_score = 0
        strategy_keywords = []
        
        for category, keywords in self.intent_keywords["입법_전략"].items():
            for keyword in keywords:
                if keyword in combined_text:
                    legislative_strategy_score += 1
                    strategy_keywords.append(keyword)
        
        # 4. 정치적 타이밍 분석
        timing_intent_score = 0
        timing_keywords = []
        
        for category, keywords in self.intent_keywords["정치적_타이밍"].items():
            for keyword in keywords:
                if keyword in combined_text:
                    timing_intent_score += 1
                    timing_keywords.append(keyword)
        
        # 5. 의도 카테고리 결정
        intent_scores = {
            "정치적_의도": political_intent_score,
            "정책_의도": policy_intent_score,
            "입법_전략": legislative_strategy_score,
            "정치적_타이밍": timing_intent_score
        }
        
        dominant_intent = max(intent_scores, key=intent_scores.get)
        overall_intent_score = sum(intent_scores.values())
        
        # 6. 의도 분석 텍스트 생성
        intent_analysis = self.generate_intent_analysis(
            bill_name, proposer_name, intent_scores, 
            political_keywords, policy_keywords, 
            strategy_keywords, timing_keywords
        )
        
        return {
            "political_intent_score": political_intent_score,
            "policy_intent_score": policy_intent_score,
            "legislative_strategy_score": legislative_strategy_score,
            "timing_intent_score": timing_intent_score,
            "overall_intent_score": overall_intent_score,
            "intent_category": dominant_intent,
            "intent_keywords": {
                "political": political_keywords,
                "policy": policy_keywords,
                "strategy": strategy_keywords,
                "timing": timing_keywords
            },
            "intent_analysis": intent_analysis
        }
    
    def generate_intent_analysis(self, bill_name: str, proposer_name: str, 
                               intent_scores: Dict, political_keywords: List,
                               policy_keywords: List, strategy_keywords: List,
                               timing_keywords: List) -> str:
        """의도 분석 텍스트 생성"""
        
        analysis_parts = []
        
        # 기본 정보
        analysis_parts.append(f"법안명: {bill_name}")
        analysis_parts.append(f"발의자: {proposer_name}")
        
        # 의도 점수 분석
        if intent_scores["정치적_의도"] > 0:
            analysis_parts.append(f"정치적 의도: {intent_scores['정치적_의도']}점 - {', '.join(political_keywords[:3])}")
        
        if intent_scores["정책_의도"] > 0:
            analysis_parts.append(f"정책 의도: {intent_scores['정책_의도']}점 - {', '.join(policy_keywords[:3])}")
        
        if intent_scores["입법_전략"] > 0:
            analysis_parts.append(f"입법 전략: {intent_scores['입법_전략']}점 - {', '.join(strategy_keywords[:3])}")
        
        if intent_scores["정치적_타이밍"] > 0:
            analysis_parts.append(f"정치적 타이밍: {intent_scores['정치적_타이밍']}점 - {', '.join(timing_keywords[:3])}")
        
        # 종합 의도 판단
        dominant_intent = max(intent_scores, key=intent_scores.get)
        if intent_scores[dominant_intent] > 0:
            analysis_parts.append(f"주요 의도: {dominant_intent} (점수: {intent_scores[dominant_intent]})")
        
        return " | ".join(analysis_parts)
    
    def analyze_all_bills_intent(self):
        """모든 법안의 의도 분석 실행"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 분석 결과 삭제
        cursor.execute('DELETE FROM bill_intent_analysis')
        
        # 모든 법안 조회
        cursor.execute('''
            SELECT bill_id, bill_name, bill_type, committee_name, 
                   proposer_name, proposal_date
            FROM real_assembly_bills_22nd
            ORDER BY proposal_date DESC
        ''')
        
        bills = cursor.fetchall()
        logger.info(f"총 {len(bills)}개 법안의 의도 분석 시작")
        
        analyzed_count = 0
        
        for bill in bills:
            bill_id, bill_name, bill_type, committee_name, proposer_name, proposal_date = bill
            
            try:
                # 의도 분석 수행
                intent_analysis = self.analyze_bill_intent(
                    bill_name, bill_type, committee_name, proposer_name, proposal_date
                )
                
                # 결과 저장
                cursor.execute('''
                    INSERT INTO bill_intent_analysis (
                        bill_id, political_intent_score, policy_intent_score,
                        legislative_strategy_score, timing_intent_score,
                        overall_intent_score, intent_category, intent_keywords,
                        intent_analysis
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    bill_id,
                    intent_analysis["political_intent_score"],
                    intent_analysis["policy_intent_score"],
                    intent_analysis["legislative_strategy_score"],
                    intent_analysis["timing_intent_score"],
                    intent_analysis["overall_intent_score"],
                    intent_analysis["intent_category"],
                    json.dumps(intent_analysis["intent_keywords"], ensure_ascii=False),
                    intent_analysis["intent_analysis"]
                ))
                
                analyzed_count += 1
                
                if analyzed_count % 100 == 0:
                    logger.info(f"의도 분석 완료: {analyzed_count}개 법안")
                
            except Exception as e:
                logger.error(f"법안 의도 분석 실패 ({bill_id}): {e}")
                continue
        
        conn.commit()
        conn.close()
        logger.info(f"모든 법안 의도 분석 완료: {analyzed_count}개")
    
    def analyze_politician_intent_patterns(self):
        """의원별 의도 패턴 분석"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 분석 결과 삭제
        cursor.execute('DELETE FROM politician_intent_patterns')
        
        # 의원별 의도 패턴 분석
        cursor.execute('''
            SELECT 
                b.proposer_name,
                COUNT(*) as total_bills,
                AVG(i.political_intent_score) as avg_political_intent,
                AVG(i.policy_intent_score) as avg_policy_intent,
                AVG(i.legislative_strategy_score) as avg_legislative_strategy,
                AVG(i.timing_intent_score) as avg_timing_intent,
                AVG(i.overall_intent_score) as avg_overall_intent
            FROM real_assembly_bills_22nd b
            JOIN bill_intent_analysis i ON b.bill_id = i.bill_id
            WHERE b.proposer_name IS NOT NULL AND b.proposer_name != ''
            GROUP BY b.proposer_name
            HAVING COUNT(*) >= 1
        ''')
        
        politicians = cursor.fetchall()
        logger.info(f"총 {len(politicians)}명 의원의 의도 패턴 분석 시작")
        
        for politician in politicians:
            politician_name = politician[0]
            total_bills = politician[1]
            avg_political_intent = politician[2] or 0
            avg_policy_intent = politician[3] or 0
            avg_legislative_strategy = politician[4] or 0
            avg_timing_intent = politician[5] or 0
            avg_overall_intent = politician[6] or 0
            
            # 가장 빈번한 의도 카테고리 찾기
            dominant_intent_category = self.find_dominant_intent_category(politician_name, conn)
            
            # 의도 일관성 점수 계산
            intent_consistency_score = self.calculate_intent_consistency(
                politician_name, conn
            )
            
            # 정치적 아젠다 점수 계산
            political_agenda_score = self.calculate_political_agenda_score(
                avg_political_intent, avg_policy_intent, 
                avg_legislative_strategy, avg_timing_intent
            )
            
            # 결과 저장
            cursor.execute('''
                INSERT INTO politician_intent_patterns (
                    politician_name, total_bills, political_intent_avg,
                    policy_intent_avg, legislative_strategy_avg,
                    timing_intent_avg, overall_intent_avg,
                    dominant_intent_category, intent_consistency_score,
                    political_agenda_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                politician_name, total_bills, avg_political_intent,
                avg_policy_intent, avg_legislative_strategy,
                avg_timing_intent, avg_overall_intent,
                dominant_intent_category, intent_consistency_score,
                political_agenda_score
            ))
        
        conn.commit()
        conn.close()
        logger.info("의원별 의도 패턴 분석 완료")
    
    def find_dominant_intent_category(self, politician_name: str, conn) -> str:
        """가장 빈번한 의도 카테고리 찾기"""
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT intent_category, COUNT(*) as count
            FROM bill_intent_analysis i
            JOIN real_assembly_bills_22nd b ON i.bill_id = b.bill_id
            WHERE b.proposer_name = ?
            GROUP BY intent_category
            ORDER BY count DESC
            LIMIT 1
        ''', (politician_name,))
        
        result = cursor.fetchone()
        return result[0] if result else "기타"
    
    def calculate_intent_consistency(self, politician_name: str, conn) -> float:
        """의도 일관성 점수 계산"""
        cursor = conn.cursor()
        
        # 해당 의원의 의도 카테고리 분포 조회
        cursor.execute('''
            SELECT intent_category, COUNT(*) as count
            FROM bill_intent_analysis i
            JOIN real_assembly_bills_22nd b ON i.bill_id = b.bill_id
            WHERE b.proposer_name = ?
            GROUP BY intent_category
        ''', (politician_name,))
        
        categories = cursor.fetchall()
        if not categories:
            return 0.0
        
        # 가장 많은 의도 카테고리의 비율 계산
        total_bills = sum(cat[1] for cat in categories)
        max_category_count = max(cat[1] for cat in categories)
        
        consistency_score = (max_category_count / total_bills) * 100
        return round(consistency_score, 2)
    
    def calculate_political_agenda_score(self, political_intent: float, 
                                       policy_intent: float, 
                                       legislative_strategy: float, 
                                       timing_intent: float) -> float:
        """정치적 아젠다 점수 계산"""
        # 정치적 의도와 타이밍 의도의 가중평균
        political_agenda = (political_intent * 0.4 + timing_intent * 0.3 + 
                           legislative_strategy * 0.2 + policy_intent * 0.1)
        return round(political_agenda, 2)
    
    def analyze_bill_relationships(self):
        """법안 간 연관성 분석"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 연관성 분석 결과 삭제
        cursor.execute('DELETE FROM bill_relationships')
        
        # 모든 법안 조회
        cursor.execute('''
            SELECT b1.bill_id, b1.bill_name, b1.proposer_name, b1.committee_name, b1.proposal_date,
                   b2.bill_id, b2.bill_name, b2.proposer_name, b2.committee_name, b2.proposal_date
            FROM real_assembly_bills_22nd b1
            CROSS JOIN real_assembly_bills_22nd b2
            WHERE b1.bill_id < b2.bill_id
        ''')
        
        bill_pairs = cursor.fetchall()
        logger.info(f"총 {len(bill_pairs)}개 법안 쌍의 연관성 분석 시작")
        
        analyzed_count = 0
        
        for pair in bill_pairs:
            bill1_id, bill1_name, bill1_proposer, bill1_committee, bill1_date = pair[:5]
            bill2_id, bill2_name, bill2_proposer, bill2_committee, bill2_date = pair[5:]
            
            try:
                # 유사도 점수 계산
                similarity_score = self.calculate_bill_similarity(
                    bill1_name, bill2_name, bill1_proposer, bill2_proposer,
                    bill1_committee, bill2_committee, bill1_date, bill2_date
                )
                
                if similarity_score > 0.3:  # 유사도가 30% 이상인 경우만 저장
                    # 연관성 유형 결정
                    relationship_type = self.determine_relationship_type(
                        bill1_proposer, bill2_proposer, bill1_committee, bill2_committee
                    )
                    
                    # 공통 키워드 추출
                    common_keywords = self.extract_common_keywords(bill1_name, bill2_name)
                    
                    # 발의자 중복 여부
                    proposer_overlap = 1 if bill1_proposer == bill2_proposer else 0
                    
                    # 위원회 중복 여부
                    committee_overlap = 1 if bill1_committee == bill2_committee else 0
                    
                    # 시간적 근접성 계산
                    timing_proximity = self.calculate_timing_proximity(bill1_date, bill2_date)
                    
                    # 결과 저장
                    cursor.execute('''
                        INSERT INTO bill_relationships (
                            bill_id_1, bill_id_2, similarity_score, relationship_type,
                            common_keywords, proposer_overlap, committee_overlap,
                            timing_proximity
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        bill1_id, bill2_id, similarity_score, relationship_type,
                        json.dumps(common_keywords, ensure_ascii=False),
                        proposer_overlap, committee_overlap, timing_proximity
                    ))
                
                analyzed_count += 1
                
                if analyzed_count % 10000 == 0:
                    logger.info(f"연관성 분석 완료: {analyzed_count}개 쌍")
                
            except Exception as e:
                logger.error(f"법안 연관성 분석 실패 ({bill1_id}, {bill2_id}): {e}")
                continue
        
        conn.commit()
        conn.close()
        logger.info(f"법안 간 연관성 분석 완료: {analyzed_count}개 쌍")
    
    def calculate_bill_similarity(self, name1: str, name2: str, 
                                proposer1: str, proposer2: str,
                                committee1: str, committee2: str,
                                date1: str, date2: str) -> float:
        """법안 간 유사도 계산"""
        similarity_score = 0.0
        
        # 1. 법안명 유사도 (40%)
        name_similarity = self.calculate_text_similarity(name1, name2)
        similarity_score += name_similarity * 0.4
        
        # 2. 발의자 동일성 (20%)
        if proposer1 == proposer2:
            similarity_score += 0.2
        
        # 3. 위원회 동일성 (20%)
        if committee1 == committee2:
            similarity_score += 0.2
        
        # 4. 시간적 근접성 (20%)
        timing_similarity = self.calculate_timing_similarity(date1, date2)
        similarity_score += timing_similarity * 0.2
        
        return round(similarity_score, 3)
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """텍스트 유사도 계산 (간단한 Jaccard 유사도)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def calculate_timing_similarity(self, date1: str, date2: str) -> float:
        """시간적 유사도 계산"""
        try:
            d1 = datetime.strptime(date1, "%Y-%m-%d")
            d2 = datetime.strptime(date2, "%Y-%m-%d")
            
            days_diff = abs((d1 - d2).days)
            
            # 30일 이내면 1.0, 90일 이내면 0.5, 그 외는 0.0
            if days_diff <= 30:
                return 1.0
            elif days_diff <= 90:
                return 0.5
            else:
                return 0.0
        except:
            return 0.0
    
    def determine_relationship_type(self, proposer1: str, proposer2: str,
                                  committee1: str, committee2: str) -> str:
        """연관성 유형 결정"""
        if proposer1 == proposer2:
            return "동일_발의자"
        elif committee1 == committee2:
            return "동일_위원회"
        else:
            return "일반_연관"
    
    def extract_common_keywords(self, name1: str, name2: str) -> List[str]:
        """공통 키워드 추출"""
        words1 = set(name1.lower().split())
        words2 = set(name2.lower().split())
        
        common = words1.intersection(words2)
        return list(common)[:5]  # 최대 5개 키워드
    
    def calculate_timing_proximity(self, date1: str, date2: str) -> int:
        """시간적 근접성 계산 (일 단위)"""
        try:
            d1 = datetime.strptime(date1, "%Y-%m-%d")
            d2 = datetime.strptime(date2, "%Y-%m-%d")
            return abs((d1 - d2).days)
        except:
            return 999999
    
    def run_comprehensive_analysis(self):
        """종합적인 의도 분석 실행"""
        logger.info("고도화된 입법 의도 분석 시작")
        
        # 1. 모든 법안의 의도 분석
        logger.info("1단계: 모든 법안의 의도 분석")
        self.analyze_all_bills_intent()
        
        # 2. 의원별 의도 패턴 분석
        logger.info("2단계: 의원별 의도 패턴 분석")
        self.analyze_politician_intent_patterns()
        
        # 3. 법안 간 연관성 분석
        logger.info("3단계: 법안 간 연관성 분석")
        self.analyze_bill_relationships()
        
        logger.info("고도화된 입법 의도 분석 완료")
        
        # 4. 분석 결과 요약
        self.generate_analysis_summary()
    
    def generate_analysis_summary(self):
        """분석 결과 요약 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 전체 통계
            cursor.execute('SELECT COUNT(*) FROM bill_intent_analysis')
            total_analyzed_bills = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM politician_intent_patterns')
            total_analyzed_politicians = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM bill_relationships')
            total_relationships = cursor.fetchone()[0]
            
            # 의도 카테고리 분포
            cursor.execute('''
                SELECT intent_category, COUNT(*) as count
                FROM bill_intent_analysis
                GROUP BY intent_category
                ORDER BY count DESC
            ''')
            intent_distribution = {row[0]: row[1] for row in cursor.fetchall()}
            
            # 상위 정치적 아젠다 의원들
            cursor.execute('''
                SELECT politician_name, political_agenda_score, total_bills
                FROM politician_intent_patterns
                ORDER BY political_agenda_score DESC
                LIMIT 10
            ''')
            top_political_agenda = cursor.fetchall()
            
            # 상위 의도 일관성 의원들
            cursor.execute('''
                SELECT politician_name, intent_consistency_score, total_bills
                FROM politician_intent_patterns
                ORDER BY intent_consistency_score DESC
                LIMIT 10
            ''')
            top_consistency = cursor.fetchall()
            
            summary = {
                "analysis_date": datetime.now().isoformat(),
                "total_analyzed_bills": total_analyzed_bills,
                "total_analyzed_politicians": total_analyzed_politicians,
                "total_relationships": total_relationships,
                "intent_distribution": intent_distribution,
                "top_political_agenda_politicians": [
                    {"name": row[0], "score": row[1], "bills": row[2]} 
                    for row in top_political_agenda
                ],
                "top_consistency_politicians": [
                    {"name": row[0], "score": row[1], "bills": row[2]} 
                    for row in top_consistency
                ]
            }
            
            # 요약 파일 저장
            with open("data/intent_analysis_summary.json", 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            logger.info("분석 결과 요약 생성 완료")
            logger.info(f"분석된 법안: {total_analyzed_bills}개")
            logger.info(f"분석된 의원: {total_analyzed_politicians}명")
            logger.info(f"발견된 연관성: {total_relationships}개")
            
        except Exception as e:
            logger.error(f"분석 결과 요약 생성 실패: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    analyzer = AdvancedLegislativeAnalyzer()
    analyzer.run_comprehensive_analysis()
