#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실용적 정치인 평가 시스템
기존 데이터를 활용한 종합적인 정치인 평가 및 랭킹 시스템
"""

import sqlite3
import json
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from collections import Counter

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PracticalEvaluationSystem:
    def __init__(self):
        self.politicians_db = "data/politicians.json"
        self.connectivity_db = "connectivity_network.db"
        self.evaluation_db = "practical_evaluation.db"
        
        self.politicians_data = []
        self.evaluation_results = []
        
        self.init_database()
        self.load_politicians_data()
    
    def init_database(self):
        """평가 결과 데이터베이스 초기화"""
        conn = sqlite3.connect(self.evaluation_db)
        cursor = conn.cursor()
        
        # 정치인 종합 평가 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS politician_evaluation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                politician_name TEXT UNIQUE,
                party TEXT,
                district TEXT,
                committee TEXT,
                
                -- 뉴스 언급 점수
                news_mention_score REAL DEFAULT 0.0,
                news_sentiment_score REAL DEFAULT 0.0,
                news_trend_score REAL DEFAULT 0.0,
                
                -- 의안발의 점수
                bill_sponsor_score REAL DEFAULT 0.0,
                bill_co_sponsor_score REAL DEFAULT 0.0,
                bill_success_rate REAL DEFAULT 0.0,
                
                -- 의안결과 점수
                bill_pass_rate REAL DEFAULT 0.0,
                bill_impact_score REAL DEFAULT 0.0,
                bill_quality_score REAL DEFAULT 0.0,
                
                -- 연결성 점수
                connectivity_score REAL DEFAULT 0.0,
                influence_score REAL DEFAULT 0.0,
                collaboration_score REAL DEFAULT 0.0,
                
                -- 종합 점수
                total_score REAL DEFAULT 0.0,
                rank INTEGER DEFAULT 0,
                
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("실용적 평가 데이터베이스 초기화 완료")
    
    def load_politicians_data(self):
        """정치인 기본 데이터 로드"""
        try:
            with open(self.politicians_db, 'r', encoding='utf-8') as f:
                self.politicians_data = json.load(f)
            logger.info(f"{len(self.politicians_data)}명 정치인 데이터 로드 완료")
        except Exception as e:
            logger.error(f"정치인 데이터 로드 실패: {e}")
    
    def simulate_news_analysis(self, politician_name: str) -> Dict:
        """뉴스 언급 분석 시뮬레이션"""
        # 실제 구현 시에는 네이버 뉴스 API를 사용
        # 현재는 정치인별로 다른 패턴의 시뮬레이션 데이터 생성
        
        # 이름 기반 시드 생성
        name_seed = sum(ord(c) for c in politician_name) % 1000
        np.random.seed(name_seed)
        
        # 언급 횟수 (0-100)
        mention_count = np.random.poisson(20)
        
        # 감정 분석 (긍정/부정/중립)
        sentiment_ratio = np.random.dirichlet([3, 1, 2])  # 긍정, 부정, 중립
        positive_mentions = int(mention_count * sentiment_ratio[0])
        negative_mentions = int(mention_count * sentiment_ratio[1])
        neutral_mentions = mention_count - positive_mentions - negative_mentions
        
        # 트렌드 점수 (최근 언급 증가/감소)
        trend_score = np.random.uniform(0, 10)
        
        return {
            "mention_count": mention_count,
            "positive_mentions": positive_mentions,
            "negative_mentions": negative_mentions,
            "neutral_mentions": neutral_mentions,
            "sentiment_score": (positive_mentions - negative_mentions) / max(mention_count, 1),
            "trend_score": trend_score
        }
    
    def simulate_bill_analysis(self, politician_name: str) -> Dict:
        """의안발의 분석 시뮬레이션"""
        # 이름 기반 시드 생성
        name_seed = sum(ord(c) for c in politician_name) % 1000
        np.random.seed(name_seed)
        
        # 대표발의 의안 수 (0-20)
        main_sponsor_count = np.random.poisson(5)
        
        # 공동발의 의안 수 (0-50)
        co_sponsor_count = np.random.poisson(15)
        
        # 성공률 (0-1)
        success_rate = np.random.beta(2, 3)  # 평균 0.4 정도
        
        # 가결된 의안 수
        passed_bills = int((main_sponsor_count + co_sponsor_count) * success_rate)
        
        # 공포된 의안 수 (가결된 것의 일부)
        enacted_bills = int(passed_bills * np.random.beta(2, 3))
        
        # 중요 의안 수 (법률안, 예산안 등)
        important_bills = int(main_sponsor_count * np.random.beta(1, 4))
        
        return {
            "main_sponsor_count": main_sponsor_count,
            "co_sponsor_count": co_sponsor_count,
            "total_bills": main_sponsor_count + co_sponsor_count,
            "passed_bills": passed_bills,
            "enacted_bills": enacted_bills,
            "important_bills": important_bills,
            "success_rate": success_rate,
            "enactment_rate": enacted_bills / max(main_sponsor_count + co_sponsor_count, 1)
        }
    
    def get_connectivity_data(self, politician_name: str) -> Dict:
        """연결성 데이터 조회"""
        try:
            conn = sqlite3.connect(self.connectivity_db)
            cursor = conn.cursor()
            
            # 총 연결 수
            cursor.execute('''
                SELECT COUNT(*) FROM connectivity_network
                WHERE politician_a = ? OR politician_b = ?
            ''', (politician_name, politician_name))
            total_connections = cursor.fetchone()[0]
            
            # 평균 연결 강도
            cursor.execute('''
                SELECT AVG(connection_strength) FROM connectivity_network
                WHERE politician_a = ? OR politician_b = ?
            ''', (politician_name, politician_name))
            avg_strength = cursor.fetchone()[0] or 0
            
            # 정당 내 연결성
            cursor.execute('''
                SELECT COUNT(*) FROM connectivity_network cn
                JOIN politicians p1 ON cn.politician_a = p1.name
                JOIN politicians p2 ON cn.politician_b = p2.name
                WHERE (cn.politician_a = ? OR cn.politician_b = ?)
                AND p1.party_name = p2.party_name
            ''', (politician_name, politician_name))
            party_connections = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_connections": total_connections,
                "avg_strength": avg_strength,
                "party_connections": party_connections
            }
            
        except Exception as e:
            logger.error(f"연결성 데이터 조회 실패 ({politician_name}): {e}")
            return {
                "total_connections": 0,
                "avg_strength": 0,
                "party_connections": 0
            }
    
    def calculate_comprehensive_score(self, politician: Dict) -> Dict:
        """종합 점수 계산"""
        name = politician['name']
        party = politician.get('party', '')
        district = politician.get('district', '')
        committee = politician.get('committee', '')
        
        # 뉴스 분석
        news_data = self.simulate_news_analysis(name)
        
        # 의안 분석
        bill_data = self.simulate_bill_analysis(name)
        
        # 연결성 분석
        connectivity_data = self.get_connectivity_data(name)
        
        # 점수 계산 (0-10점 스케일)
        
        # 1. 뉴스 언급 점수 (25% 가중치)
        news_mention_score = min(news_data['mention_count'] / 10, 10)
        news_sentiment_score = (news_data['sentiment_score'] + 1) * 5  # -1~1을 0~10으로 변환
        news_trend_score = news_data['trend_score']
        
        # 2. 의안발의 점수 (30% 가중치)
        bill_sponsor_score = min(bill_data['main_sponsor_count'] / 2, 10)
        bill_co_sponsor_score = min(bill_data['co_sponsor_count'] / 5, 10)
        bill_success_rate = bill_data['success_rate'] * 10
        
        # 3. 의안결과 점수 (25% 가중치)
        bill_pass_rate = min(bill_data['enacted_bills'] / 3, 10)
        bill_impact_score = min(bill_data['important_bills'] / 2, 10)
        bill_quality_score = min(bill_data['enactment_rate'] * 10, 10)
        
        # 4. 연결성 점수 (20% 가중치)
        connectivity_score = min(connectivity_data['total_connections'] / 20, 10)
        influence_score = min(connectivity_data['avg_strength'] * 2, 10)
        collaboration_score = min(connectivity_data['party_connections'] / 10, 10)
        
        # 가중 평균으로 종합 점수 계산
        total_score = (
            # 뉴스 점수 (25%)
            (news_mention_score * 0.4 + news_sentiment_score * 0.3 + news_trend_score * 0.3) * 0.25 +
            
            # 의안발의 점수 (30%)
            (bill_sponsor_score * 0.4 + bill_co_sponsor_score * 0.3 + bill_success_rate * 0.3) * 0.30 +
            
            # 의안결과 점수 (25%)
            (bill_pass_rate * 0.4 + bill_impact_score * 0.3 + bill_quality_score * 0.3) * 0.25 +
            
            # 연결성 점수 (20%)
            (connectivity_score * 0.4 + influence_score * 0.3 + collaboration_score * 0.3) * 0.20
        )
        
        return {
            "politician_name": name,
            "party": party,
            "district": district,
            "committee": committee,
            
            # 뉴스 점수
            "news_mention_score": round(news_mention_score, 2),
            "news_sentiment_score": round(news_sentiment_score, 2),
            "news_trend_score": round(news_trend_score, 2),
            
            # 의안발의 점수
            "bill_sponsor_score": round(bill_sponsor_score, 2),
            "bill_co_sponsor_score": round(bill_co_sponsor_score, 2),
            "bill_success_rate": round(bill_success_rate, 2),
            
            # 의안결과 점수
            "bill_pass_rate": round(bill_pass_rate, 2),
            "bill_impact_score": round(bill_impact_score, 2),
            "bill_quality_score": round(bill_quality_score, 2),
            
            # 연결성 점수
            "connectivity_score": round(connectivity_score, 2),
            "influence_score": round(influence_score, 2),
            "collaboration_score": round(collaboration_score, 2),
            
            # 종합 점수
            "total_score": round(total_score, 2),
            
            # 상세 데이터
            "news_data": news_data,
            "bill_data": bill_data,
            "connectivity_data": connectivity_data
        }
    
    def run_comprehensive_evaluation(self):
        """종합 평가 실행"""
        logger.info("실용적 정치인 평가 시작...")
        
        self.evaluation_results = []
        
        for politician in self.politicians_data:
            try:
                result = self.calculate_comprehensive_score(politician)
                self.evaluation_results.append(result)
            except Exception as e:
                logger.error(f"정치인 평가 실패 ({politician.get('name', 'Unknown')}): {e}")
        
        # 점수순으로 정렬
        self.evaluation_results.sort(key=lambda x: x['total_score'], reverse=True)
        
        # 순위 설정
        for i, result in enumerate(self.evaluation_results):
            result['rank'] = i + 1
        
        # 결과 저장
        self.save_evaluation_results()
        
        logger.info(f"종합 평가 완료: {len(self.evaluation_results)}명")
        return self.evaluation_results
    
    def save_evaluation_results(self):
        """평가 결과를 데이터베이스에 저장"""
        conn = sqlite3.connect(self.evaluation_db)
        cursor = conn.cursor()
        
        # 기존 데이터 삭제
        cursor.execute('DELETE FROM politician_evaluation')
        
        for result in self.evaluation_results:
            cursor.execute('''
                INSERT INTO politician_evaluation (
                    politician_name, party, district, committee,
                    news_mention_score, news_sentiment_score, news_trend_score,
                    bill_sponsor_score, bill_co_sponsor_score, bill_success_rate,
                    bill_pass_rate, bill_impact_score, bill_quality_score,
                    connectivity_score, influence_score, collaboration_score,
                    total_score, rank
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result['politician_name'], result['party'], result['district'], result['committee'],
                result['news_mention_score'], result['news_sentiment_score'], result['news_trend_score'],
                result['bill_sponsor_score'], result['bill_co_sponsor_score'], result['bill_success_rate'],
                result['bill_pass_rate'], result['bill_impact_score'], result['bill_quality_score'],
                result['connectivity_score'], result['influence_score'], result['collaboration_score'],
                result['total_score'], result['rank']
            ))
        
        conn.commit()
        conn.close()
        logger.info("평가 결과 저장 완료")
    
    def get_top_performers(self, limit: int = 20) -> List[Dict]:
        """상위 성과자 조회"""
        return self.evaluation_results[:limit]
    
    def get_party_ranking(self) -> Dict[str, List[Dict]]:
        """정당별 순위"""
        party_ranking = {}
        for result in self.evaluation_results:
            party = result['party'] or '정당정보없음'
            if party not in party_ranking:
                party_ranking[party] = []
            party_ranking[party].append(result)
        return party_ranking
    
    def get_committee_ranking(self) -> Dict[str, List[Dict]]:
        """위원회별 순위"""
        committee_ranking = {}
        for result in self.evaluation_results:
            committee = result['committee'] or '위원회정보없음'
            if committee not in committee_ranking:
                committee_ranking[committee] = []
            committee_ranking[committee].append(result)
        return committee_ranking
    
    def print_evaluation_summary(self):
        """평가 결과 요약 출력"""
        print("\n=== 실용적 정치인 평가 결과 ===")
        print(f"총 평가 대상: {len(self.evaluation_results)}명")
        
        # 상위 15명
        print("\n=== 상위 15명 ===")
        for i, result in enumerate(self.evaluation_results[:15]):
            print(f"{i+1:2d}. {result['politician_name']:10s} ({result['party']:10s}) - "
                  f"총점:{result['total_score']:5.2f} "
                  f"뉴스:{result['news_mention_score']:4.1f} "
                  f"의안:{result['bill_sponsor_score']:4.1f} "
                  f"결과:{result['bill_pass_rate']:4.1f} "
                  f"연결:{result['connectivity_score']:4.1f}")
        
        # 정당별 상위 3명
        print("\n=== 정당별 상위 3명 ===")
        party_ranking = self.get_party_ranking()
        for party, politicians in party_ranking.items():
            print(f"\n{party}:")
            for i, pol in enumerate(politicians[:3]):
                print(f"  {i+1}. {pol['politician_name']} - {pol['total_score']:.2f}점")
        
        # 위원회별 상위 3명
        print("\n=== 위원회별 상위 3명 ===")
        committee_ranking = self.get_committee_ranking()
        for committee, politicians in committee_ranking.items():
            if len(politicians) > 0:
                print(f"\n{committee}:")
                for i, pol in enumerate(politicians[:3]):
                    print(f"  {i+1}. {pol['politician_name']} - {pol['total_score']:.2f}점")

if __name__ == "__main__":
    evaluator = PracticalEvaluationSystem()
    results = evaluator.run_comprehensive_evaluation()
    evaluator.print_evaluation_summary()

