#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
종합 정치인 평가 시스템
기사 카운팅 + 의안발의 + 의안결과 + 연결성 분석을 통한 종합 평가
"""

import sqlite3
import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import numpy as np
from dataclasses import dataclass

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PoliticianScore:
    """정치인 종합 점수"""
    name: str
    party: str
    district: str
    committee: str
    
    # 기본 정보 점수
    basic_score: float = 0.0
    
    # 뉴스 언급 점수
    news_mention_score: float = 0.0
    news_sentiment_score: float = 0.0
    news_trend_score: float = 0.0
    
    # 의안발의 점수
    bill_sponsor_score: float = 0.0
    bill_co_sponsor_score: float = 0.0
    bill_success_rate: float = 0.0
    
    # 의안결과 점수
    bill_pass_rate: float = 0.0
    bill_impact_score: float = 0.0
    bill_quality_score: float = 0.0
    
    # 연결성 점수
    connectivity_score: float = 0.0
    influence_score: float = 0.0
    collaboration_score: float = 0.0
    
    # 종합 점수
    total_score: float = 0.0
    rank: int = 0

class ComprehensiveEvaluationSystem:
    def __init__(self):
        self.politicians_db = "data/politicians.json"
        self.connectivity_db = "connectivity_network.db"
        self.bills_db = "bills_connectivity.db"
        self.news_api_key = "57a5b206dc5341889b4ee3fbbb8757be"
        self.bill_api_key = "57a5b206dc5341889b4ee3fbbb8757be"
        
        # 가중치 설정
        self.weights = {
            'news_mention': 0.25,      # 뉴스 언급 가중치
            'news_sentiment': 0.15,    # 뉴스 감정 가중치
            'bill_sponsor': 0.20,      # 의안발의 가중치
            'bill_success': 0.15,      # 의안 성공률 가중치
            'bill_impact': 0.10,       # 의안 영향력 가중치
            'connectivity': 0.10,      # 연결성 가중치
            'influence': 0.05          # 영향력 가중치
        }
        
        self.politicians_data = []
        self.evaluation_results = []
        
    def load_politicians_data(self):
        """정치인 기본 데이터 로드"""
        try:
            with open(self.politicians_db, 'r', encoding='utf-8') as f:
                self.politicians_data = json.load(f)
            logger.info(f"{len(self.politicians_data)}명 정치인 데이터 로드 완료")
        except Exception as e:
            logger.error(f"정치인 데이터 로드 실패: {e}")
    
    def analyze_news_mentions(self, politician_name: str, days: int = 30) -> Dict:
        """뉴스 언급 분석"""
        try:
            # 네이버 뉴스 API 호출
            url = "https://openapi.naver.com/v1/search/news.json"
            headers = {
                "X-Naver-Client-Id": "your_client_id",
                "X-Naver-Client-Secret": "your_client_secret"
            }
            params = {
                "query": politician_name,
                "display": 100,
                "sort": "sim"
            }
            
            # 실제 API 호출 대신 시뮬레이션 데이터 사용
            # 실제 구현 시에는 위의 API를 사용
            mention_count = np.random.randint(0, 50)
            positive_mentions = int(mention_count * 0.6)
            negative_mentions = int(mention_count * 0.2)
            neutral_mentions = mention_count - positive_mentions - negative_mentions
            
            return {
                "mention_count": mention_count,
                "positive_mentions": positive_mentions,
                "negative_mentions": negative_mentions,
                "neutral_mentions": neutral_mentions,
                "sentiment_score": (positive_mentions - negative_mentions) / max(mention_count, 1),
                "trend_score": np.random.uniform(0, 10)
            }
        except Exception as e:
            logger.error(f"뉴스 분석 실패 ({politician_name}): {e}")
            return {
                "mention_count": 0,
                "positive_mentions": 0,
                "negative_mentions": 0,
                "neutral_mentions": 0,
                "sentiment_score": 0,
                "trend_score": 0
            }
    
    def analyze_bill_sponsorship(self, politician_name: str) -> Dict:
        """의안발의 분석"""
        try:
            conn = sqlite3.connect(self.bills_db)
            cursor = conn.cursor()
            
            # 대표발의 의안 수
            cursor.execute('''
                SELECT COUNT(*) FROM bills 
                WHERE ppsr_nm LIKE ? AND ppsr_knd = '의원'
            ''', (f'%{politician_name}%',))
            main_sponsor_count = cursor.fetchone()[0]
            
            # 공동발의 의안 수
            cursor.execute('''
                SELECT COUNT(*) FROM bills 
                WHERE ppsr_nm LIKE ? AND ppsr_knd = '공동발의'
            ''', (f'%{politician_name}%',))
            co_sponsor_count = cursor.fetchone()[0]
            
            # 의안 성공률 (가결된 의안)
            cursor.execute('''
                SELECT COUNT(*) FROM bills 
                WHERE ppsr_nm LIKE ? AND rgs_conf_rslt LIKE '%가결%'
            ''', (f'%{politician_name}%',))
            passed_bills = cursor.fetchone()[0]
            
            total_bills = main_sponsor_count + co_sponsor_count
            success_rate = passed_bills / max(total_bills, 1)
            
            conn.close()
            
            return {
                "main_sponsor_count": main_sponsor_count,
                "co_sponsor_count": co_sponsor_count,
                "total_bills": total_bills,
                "passed_bills": passed_bills,
                "success_rate": success_rate
            }
        except Exception as e:
            logger.error(f"의안발의 분석 실패 ({politician_name}): {e}")
            return {
                "main_sponsor_count": 0,
                "co_sponsor_count": 0,
                "total_bills": 0,
                "passed_bills": 0,
                "success_rate": 0
            }
    
    def analyze_bill_impact(self, politician_name: str) -> Dict:
        """의안 영향력 분석"""
        try:
            conn = sqlite3.connect(self.bills_db)
            cursor = conn.cursor()
            
            # 중요 의안 발의 (법률안, 예산안 등)
            cursor.execute('''
                SELECT COUNT(*) FROM bills 
                WHERE ppsr_nm LIKE ? AND bill_knd IN ('법률안', '예산안', '결산안')
            ''', (f'%{politician_name}%',))
            important_bills = cursor.fetchone()[0]
            
            # 공포된 의안 수
            cursor.execute('''
                SELECT COUNT(*) FROM bills 
                WHERE ppsr_nm LIKE ? AND prom_dt IS NOT NULL AND prom_dt != ''
            ''', (f'%{politician_name}%',))
            enacted_bills = cursor.fetchone()[0]
            
            # 소관 위원회 다양성
            cursor.execute('''
                SELECT COUNT(DISTINCT jrcmit_nm) FROM bills 
                WHERE ppsr_nm LIKE ? AND jrcmit_nm IS NOT NULL
            ''', (f'%{politician_name}%',))
            committee_diversity = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "important_bills": important_bills,
                "enacted_bills": enacted_bills,
                "committee_diversity": committee_diversity,
                "impact_score": (important_bills * 2 + enacted_bills * 3 + committee_diversity) / 10
            }
        except Exception as e:
            logger.error(f"의안 영향력 분석 실패 ({politician_name}): {e}")
            return {
                "important_bills": 0,
                "enacted_bills": 0,
                "committee_diversity": 0,
                "impact_score": 0
            }
    
    def analyze_connectivity(self, politician_name: str) -> Dict:
        """연결성 분석"""
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
                "party_connections": party_connections,
                "connectivity_score": total_connections * 0.5 + avg_strength * 0.3 + party_connections * 0.2
            }
        except Exception as e:
            logger.error(f"연결성 분석 실패 ({politician_name}): {e}")
            return {
                "total_connections": 0,
                "avg_strength": 0,
                "party_connections": 0,
                "connectivity_score": 0
            }
    
    def calculate_comprehensive_score(self, politician_data: Dict) -> PoliticianScore:
        """종합 점수 계산"""
        name = politician_data['name']
        
        # 뉴스 분석
        news_data = self.analyze_news_mentions(name)
        
        # 의안발의 분석
        bill_data = self.analyze_bill_sponsorship(name)
        
        # 의안 영향력 분석
        impact_data = self.analyze_bill_impact(name)
        
        # 연결성 분석
        connectivity_data = self.analyze_connectivity(name)
        
        # 점수 계산
        news_mention_score = min(news_data['mention_count'] / 10, 10)  # 0-10점
        news_sentiment_score = (news_data['sentiment_score'] + 1) * 5  # 0-10점
        news_trend_score = news_data['trend_score']  # 0-10점
        
        bill_sponsor_score = min(bill_data['main_sponsor_count'] / 5, 10)  # 0-10점
        bill_co_sponsor_score = min(bill_data['co_sponsor_count'] / 10, 10)  # 0-10점
        bill_success_rate = bill_data['success_rate'] * 10  # 0-10점
        
        bill_pass_rate = min(impact_data['enacted_bills'] / 3, 10)  # 0-10점
        bill_impact_score = min(impact_data['impact_score'], 10)  # 0-10점
        bill_quality_score = min(impact_data['important_bills'] / 2, 10)  # 0-10점
        
        connectivity_score = min(connectivity_data['connectivity_score'], 10)  # 0-10점
        influence_score = min(connectivity_data['total_connections'] / 20, 10)  # 0-10점
        collaboration_score = min(connectivity_data['party_connections'] / 10, 10)  # 0-10점
        
        # 가중 평균으로 종합 점수 계산
        total_score = (
            news_mention_score * self.weights['news_mention'] +
            news_sentiment_score * self.weights['news_sentiment'] +
            bill_sponsor_score * self.weights['bill_sponsor'] +
            bill_success_rate * self.weights['bill_success'] +
            bill_impact_score * self.weights['bill_impact'] +
            connectivity_score * self.weights['connectivity'] +
            influence_score * self.weights['influence']
        )
        
        return PoliticianScore(
            name=name,
            party=politician_data.get('party', ''),
            district=politician_data.get('district', ''),
            committee=politician_data.get('committee', ''),
            news_mention_score=news_mention_score,
            news_sentiment_score=news_sentiment_score,
            news_trend_score=news_trend_score,
            bill_sponsor_score=bill_sponsor_score,
            bill_co_sponsor_score=bill_co_sponsor_score,
            bill_success_rate=bill_success_rate,
            bill_pass_rate=bill_pass_rate,
            bill_impact_score=bill_impact_score,
            bill_quality_score=bill_quality_score,
            connectivity_score=connectivity_score,
            influence_score=influence_score,
            collaboration_score=collaboration_score,
            total_score=total_score
        )
    
    def run_comprehensive_evaluation(self) -> List[PoliticianScore]:
        """종합 평가 실행"""
        logger.info("종합 정치인 평가 시작...")
        
        self.load_politicians_data()
        self.evaluation_results = []
        
        for politician in self.politicians_data:
            try:
                score = self.calculate_comprehensive_score(politician)
                self.evaluation_results.append(score)
            except Exception as e:
                logger.error(f"정치인 평가 실패 ({politician.get('name', 'Unknown')}): {e}")
        
        # 점수순으로 정렬
        self.evaluation_results.sort(key=lambda x: x.total_score, reverse=True)
        
        # 순위 설정
        for i, result in enumerate(self.evaluation_results):
            result.rank = i + 1
        
        logger.info(f"종합 평가 완료: {len(self.evaluation_results)}명")
        return self.evaluation_results
    
    def get_top_politicians(self, limit: int = 20) -> List[PoliticianScore]:
        """상위 정치인 조회"""
        return self.evaluation_results[:limit]
    
    def get_party_ranking(self) -> Dict[str, List[PoliticianScore]]:
        """정당별 순위"""
        party_ranking = {}
        for result in self.evaluation_results:
            party = result.party or '정당정보없음'
            if party not in party_ranking:
                party_ranking[party] = []
            party_ranking[party].append(result)
        return party_ranking
    
    def get_committee_ranking(self) -> Dict[str, List[PoliticianScore]]:
        """위원회별 순위"""
        committee_ranking = {}
        for result in self.evaluation_results:
            committee = result.committee or '위원회정보없음'
            if committee not in committee_ranking:
                committee_ranking[committee] = []
            committee_ranking[committee].append(result)
        return committee_ranking
    
    def save_evaluation_results(self, filename: str = "evaluation_results.json"):
        """평가 결과 저장"""
        results_data = []
        for result in self.evaluation_results:
            results_data.append({
                "name": result.name,
                "party": result.party,
                "district": result.district,
                "committee": result.committee,
                "rank": result.rank,
                "total_score": round(result.total_score, 2),
                "scores": {
                    "news_mention": round(result.news_mention_score, 2),
                    "news_sentiment": round(result.news_sentiment_score, 2),
                    "news_trend": round(result.news_trend_score, 2),
                    "bill_sponsor": round(result.bill_sponsor_score, 2),
                    "bill_co_sponsor": round(result.bill_co_sponsor_score, 2),
                    "bill_success_rate": round(result.bill_success_rate, 2),
                    "bill_pass_rate": round(result.bill_pass_rate, 2),
                    "bill_impact": round(result.bill_impact_score, 2),
                    "bill_quality": round(result.bill_quality_score, 2),
                    "connectivity": round(result.connectivity_score, 2),
                    "influence": round(result.influence_score, 2),
                    "collaboration": round(result.collaboration_score, 2)
                }
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"평가 결과 저장 완료: {filename}")

if __name__ == "__main__":
    evaluator = ComprehensiveEvaluationSystem()
    results = evaluator.run_comprehensive_evaluation()
    
    # 상위 10명 출력
    print("\n=== 상위 10명 정치인 ===")
    for i, result in enumerate(results[:10]):
        print(f"{i+1:2d}. {result.name:10s} ({result.party:10s}) - {result.total_score:.2f}점")
    
    # 정당별 상위 3명
    print("\n=== 정당별 상위 3명 ===")
    party_ranking = evaluator.get_party_ranking()
    for party, politicians in party_ranking.items():
        print(f"\n{party}:")
        for i, pol in enumerate(politicians[:3]):
            print(f"  {i+1}. {pol.name} - {pol.total_score:.2f}점")
    
    # 결과 저장
    evaluator.save_evaluation_results()
