#!/usr/bin/env python3
"""
표심 분석 시스템
정치인의 표심, 언론 노출, 입법 성과, 소통 활동, 정치적 일관성을 종합 분석
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import math

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class VotingSentimentAnalyzer:
    def __init__(self, db_path: str = "newsbot_stable.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """표심 분석을 위한 데이터베이스 테이블 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 표심 지수 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voting_sentiment_scores (
                politician_name TEXT PRIMARY KEY,
                voting_sentiment_index REAL DEFAULT 0.0,
                media_exposure_index REAL DEFAULT 0.0,
                legislative_performance_index REAL DEFAULT 0.0,
                communication_activity_index REAL DEFAULT 0.0,
                political_consistency_index REAL DEFAULT 0.0,
                total_voting_score REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (politician_name) REFERENCES politicians (name)
            )
        ''')
        
        # 여론조사 데이터 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS opinion_polls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                politician_name TEXT,
                poll_date TEXT,
                support_rate REAL,
                poll_agency TEXT,
                poll_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (politician_name) REFERENCES politicians (name)
            )
        ''')
        
        # 언론 노출 데이터 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS media_exposure (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                politician_name TEXT,
                news_date TEXT,
                news_count INTEGER DEFAULT 0,
                tv_appearance_count INTEGER DEFAULT 0,
                media_tone_score REAL DEFAULT 0.0,
                keywords TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (politician_name) REFERENCES politicians (name)
            )
        ''')
        
        # 입법 활동 데이터 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS legislative_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                politician_name TEXT,
                bill_title TEXT,
                bill_type TEXT,
                proposal_date TEXT,
                co_sponsors TEXT,
                passage_status TEXT,
                policy_impact_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (politician_name) REFERENCES politicians (name)
            )
        ''')
        
        # 소통 활동 데이터 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS communication_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                politician_name TEXT,
                activity_date TEXT,
                sns_posts INTEGER DEFAULT 0,
                sns_engagement REAL DEFAULT 0.0,
                local_event_participation INTEGER DEFAULT 0,
                citizen_consultation_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (politician_name) REFERENCES politicians (name)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("표심 분석 데이터베이스 초기화 완료")
    
    def calculate_voting_sentiment_index(self, politician_name: str) -> float:
        """표심 지수 계산"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 여론조사 지지율 (가상 데이터)
        cursor.execute('''
            SELECT AVG(support_rate) FROM opinion_polls 
            WHERE politician_name = ? AND poll_date >= '2024-01-01'
        ''', (politician_name,))
        
        poll_result = cursor.fetchone()
        poll_support_rate = poll_result[0] if poll_result[0] else 50.0  # 기본값 50%
        
        # 지역 만족도 (가상 데이터)
        regional_satisfaction = min(100.0, 60.0 + (hash(politician_name) % 30))
        
        # 정치 신뢰도 (가상 데이터)
        political_trust = min(100.0, 55.0 + (hash(politician_name + "trust") % 25))
        
        # 표심 지수 계산
        voting_sentiment = (poll_support_rate * 0.4) + (regional_satisfaction * 0.3) + (political_trust * 0.3)
        
        conn.close()
        return round(voting_sentiment, 2)
    
    def calculate_media_exposure_index(self, politician_name: str) -> float:
        """언론 노출 지수 계산"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 뉴스 언급 횟수 (가상 데이터)
        news_mentions = min(1000, 50 + (hash(politician_name) % 200))
        
        # TV 출연 횟수 (가상 데이터)
        tv_appearances = min(100, 10 + (hash(politician_name + "tv") % 30))
        
        # 언론 톤 점수 (가상 데이터)
        media_tone = min(100.0, 60.0 + (hash(politician_name + "tone") % 30))
        
        # 언론 노출 지수 계산
        media_exposure = (min(100, news_mentions / 10) * 0.3) + (tv_appearances * 0.4) + (media_tone * 0.3)
        
        conn.close()
        return round(media_exposure, 2)
    
    def calculate_legislative_performance_index(self, politician_name: str) -> float:
        """입법 성과 지수 계산"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 법안 발의 수 (가상 데이터)
        bill_proposals = min(50, 5 + (hash(politician_name + "bills") % 20))
        
        # 법안 통과율 (가상 데이터)
        passage_rate = min(100.0, 30.0 + (hash(politician_name + "passage") % 40))
        
        # 정책 영향도 (가상 데이터)
        policy_impact = min(100.0, 40.0 + (hash(politician_name + "impact") % 35))
        
        # 입법 성과 지수 계산
        legislative_performance = (min(100, bill_proposals * 2) * 0.2) + (passage_rate * 0.4) + (policy_impact * 0.4)
        
        conn.close()
        return round(legislative_performance, 2)
    
    def calculate_communication_activity_index(self, politician_name: str) -> float:
        """소통 활동 지수 계산"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # SNS 활동도 (가상 데이터)
        sns_activity = min(100.0, 40.0 + (hash(politician_name + "sns") % 40))
        
        # 지역 행사 참여 (가상 데이터)
        local_events = min(100, 20 + (hash(politician_name + "events") % 30))
        
        # 시민 상담 처리 (가상 데이터)
        citizen_consultation = min(100.0, 50.0 + (hash(politician_name + "consultation") % 30))
        
        # 소통 활동 지수 계산
        communication_activity = (sns_activity * 0.3) + (local_events * 0.4) + (citizen_consultation * 0.3)
        
        conn.close()
        return round(communication_activity, 2)
    
    def calculate_political_consistency_index(self, politician_name: str) -> float:
        """정치적 일관성 지수 계산"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 입장 변화도 (낮을수록 좋음, 가상 데이터)
        position_change = max(0.0, 100.0 - (30.0 + (hash(politician_name + "position") % 40)))
        
        # 정치 철학 일치도 (가상 데이터)
        philosophy_consistency = min(100.0, 60.0 + (hash(politician_name + "philosophy") % 30))
        
        # 정치적 일관성 지수 계산
        political_consistency = (position_change * 0.6) + (philosophy_consistency * 0.4)
        
        conn.close()
        return round(political_consistency, 2)
    
    def calculate_total_voting_score(self, politician_name: str) -> Dict[str, float]:
        """전체 표심 점수 계산"""
        voting_sentiment = self.calculate_voting_sentiment_index(politician_name)
        media_exposure = self.calculate_media_exposure_index(politician_name)
        legislative_performance = self.calculate_legislative_performance_index(politician_name)
        communication_activity = self.calculate_communication_activity_index(politician_name)
        political_consistency = self.calculate_political_consistency_index(politician_name)
        
        # 가중 평균으로 총점 계산
        total_score = (
            voting_sentiment * 0.3 +      # 표심 지수 30%
            media_exposure * 0.25 +       # 언론 노출 25%
            legislative_performance * 0.25 +  # 입법 성과 25%
            communication_activity * 0.1 +   # 소통 활동 10%
            political_consistency * 0.1      # 정치적 일관성 10%
        )
        
        return {
            "voting_sentiment_index": voting_sentiment,
            "media_exposure_index": media_exposure,
            "legislative_performance_index": legislative_performance,
            "communication_activity_index": communication_activity,
            "political_consistency_index": political_consistency,
            "total_voting_score": round(total_score, 2)
        }
    
    def update_politician_scores(self, politician_name: str):
        """정치인 점수 업데이트"""
        scores = self.calculate_total_voting_score(politician_name)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO voting_sentiment_scores (
                politician_name, voting_sentiment_index, media_exposure_index,
                legislative_performance_index, communication_activity_index,
                political_consistency_index, total_voting_score, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            politician_name,
            scores["voting_sentiment_index"],
            scores["media_exposure_index"],
            scores["legislative_performance_index"],
            scores["communication_activity_index"],
            scores["political_consistency_index"],
            scores["total_voting_score"]
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ {politician_name} 표심 점수 업데이트 완료: {scores['total_voting_score']}점")
        return scores
    
    def get_politician_ranking(self, limit: int = 20) -> List[Dict]:
        """정치인 표심 점수 랭킹"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                p.name, p.party_name, p.district,
                v.voting_sentiment_index, v.media_exposure_index,
                v.legislative_performance_index, v.communication_activity_index,
                v.political_consistency_index, v.total_voting_score
            FROM voting_sentiment_scores v
            JOIN politicians p ON v.politician_name = p.name
            ORDER BY v.total_voting_score DESC
            LIMIT ?
        ''', (limit,))
        
        ranking = []
        for i, row in enumerate(cursor.fetchall()):
            ranking.append({
                "rank": i + 1,
                "name": row[0],
                "party": row[1] if row[1] else "정당정보없음",
                "district": row[2] if row[2] else "정보없음",
                "scores": {
                    "voting_sentiment": round(row[3], 2),
                    "media_exposure": round(row[4], 2),
                    "legislative_performance": round(row[5], 2),
                    "communication_activity": round(row[6], 2),
                    "political_consistency": round(row[7], 2),
                    "total": round(row[8], 2)
                }
            })
        
        conn.close()
        return ranking
    
    def run_analysis(self):
        """전체 정치인 표심 분석 실행"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name FROM politicians')
        politicians = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        logger.info(f"표심 분석 시작: {len(politicians)}명")
        
        for politician in politicians:
            try:
                self.update_politician_scores(politician)
            except Exception as e:
                logger.error(f"❌ {politician} 분석 실패: {e}")
        
        logger.info("✅ 표심 분석 완료")

if __name__ == "__main__":
    analyzer = VotingSentimentAnalyzer()
    analyzer.run_analysis()
    
    # 상위 10명 랭킹 출력
    ranking = analyzer.get_politician_ranking(10)
    print("\n🏆 표심 점수 상위 10명:")
    for politician in ranking:
        print(f"{politician['rank']}. {politician['name']} ({politician['party']}) - {politician['scores']['total']}점")

