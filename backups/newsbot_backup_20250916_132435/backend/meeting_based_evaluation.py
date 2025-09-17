#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
회의록 기반 정치인 평가 시스템
실제 회의록 데이터를 활용한 정확한 정치인 활동 평가
"""

import sqlite3
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from collections import Counter
import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MeetingBasedEvaluation:
    def __init__(self):
        self.meeting_db_path = "meeting_records_simple.db"
        self.politicians_db = "data/politicians.json"
        self.connectivity_db = "connectivity_network.db"
        self.evaluation_db = "meeting_evaluation.db"
        
        self.politicians_data = []
        self.evaluation_results = []
        
        self.init_database()
        self.load_politicians_data()
    
    def init_database(self):
        """평가 결과 데이터베이스 초기화"""
        conn = sqlite3.connect(self.evaluation_db)
        cursor = conn.cursor()
        
        # 정치인 활동 평가 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS politician_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                politician_name TEXT UNIQUE,
                total_meetings INTEGER DEFAULT 0,
                total_speeches INTEGER DEFAULT 0,
                committee_meetings INTEGER DEFAULT 0,
                committee_diversity INTEGER DEFAULT 0,
                speech_frequency REAL DEFAULT 0.0,
                participation_rate REAL DEFAULT 0.0,
                influence_score REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 위원회별 활동 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS committee_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                politician_name TEXT,
                committee_name TEXT,
                meeting_count INTEGER DEFAULT 0,
                speech_count INTEGER DEFAULT 0,
                avg_speeches_per_meeting REAL DEFAULT 0.0,
                FOREIGN KEY (politician_name) REFERENCES politician_activity (politician_name)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("회의록 기반 평가 데이터베이스 초기화 완료")
    
    def load_politicians_data(self):
        """정치인 기본 데이터 로드"""
        try:
            with open(self.politicians_db, 'r', encoding='utf-8') as f:
                self.politicians_data = json.load(f)
            logger.info(f"{len(self.politicians_data)}명 정치인 데이터 로드 완료")
        except Exception as e:
            logger.error(f"정치인 데이터 로드 실패: {e}")
    
    def analyze_meeting_participation(self, politician_name: str) -> Dict:
        """회의록 참여도 분석"""
        try:
            conn = sqlite3.connect(self.meeting_db_path)
            cursor = conn.cursor()
            
            # 전체 회의 참여 수
            cursor.execute('''
                SELECT COUNT(DISTINCT m.id) FROM meetings m
                JOIN speakers s ON m.id = s.meeting_id
                WHERE s.speaker_name = ?
            ''', (politician_name,))
            total_meetings = cursor.fetchone()[0]
            
            # 전체 발언 수
            cursor.execute('''
                SELECT COUNT(*) FROM speakers
                WHERE speaker_name = ?
            ''', (politician_name,))
            total_speeches = cursor.fetchone()[0]
            
            # 위원회별 참여 분석
            cursor.execute('''
                SELECT m.committee_name, COUNT(DISTINCT m.id) as meeting_count,
                       COUNT(s.id) as speech_count
                FROM meetings m
                JOIN speakers s ON m.id = s.meeting_id
                WHERE s.speaker_name = ?
                GROUP BY m.committee_name
            ''', (politician_name,))
            committee_data = cursor.fetchall()
            
            # 위원회 다양성
            committee_diversity = len(committee_data)
            
            # 평균 발언 빈도
            speech_frequency = total_speeches / max(total_meetings, 1)
            
            # 참여율 (전체 회의 대비)
            cursor.execute('SELECT COUNT(DISTINCT id) FROM meetings')
            total_meetings_in_db = cursor.fetchone()[0]
            participation_rate = total_meetings / max(total_meetings_in_db, 1)
            
            conn.close()
            
            return {
                "politician_name": politician_name,
                "total_meetings": total_meetings,
                "total_speeches": total_speeches,
                "committee_diversity": committee_diversity,
                "speech_frequency": speech_frequency,
                "participation_rate": participation_rate,
                "committee_data": committee_data
            }
            
        except Exception as e:
            logger.error(f"회의록 분석 실패 ({politician_name}): {e}")
            return {
                "politician_name": politician_name,
                "total_meetings": 0,
                "total_speeches": 0,
                "committee_diversity": 0,
                "speech_frequency": 0,
                "participation_rate": 0,
                "committee_data": []
            }
    
    def analyze_speech_content(self, politician_name: str) -> Dict:
        """발언 내용 분석"""
        try:
            conn = sqlite3.connect(self.meeting_db_path)
            cursor = conn.cursor()
            
            # 발언 내용 가져오기
            cursor.execute('''
                SELECT speech_content FROM speakers
                WHERE speaker_name = ? AND speech_content IS NOT NULL
            ''', (politician_name,))
            speeches = cursor.fetchall()
            
            if not speeches:
                conn.close()
                return {
                    "avg_speech_length": 0,
                    "keyword_diversity": 0,
                    "policy_keywords": 0,
                    "content_quality_score": 0
                }
            
            # 평균 발언 길이
            speech_lengths = [len(speech[0]) for speech in speeches if speech[0]]
            avg_speech_length = np.mean(speech_lengths) if speech_lengths else 0
            
            # 키워드 분석
            all_text = ' '.join([speech[0] for speech in speeches if speech[0]])
            
            # 정책 관련 키워드
            policy_keywords = [
                '정책', '법안', '예산', '제도', '개선', '발전', '지원', '투자',
                '교육', '복지', '경제', '환경', '안전', '보건', '문화', '체육',
                '농업', '산업', '교통', '통신', '에너지', '과학', '기술'
            ]
            
            keyword_count = sum(1 for keyword in policy_keywords if keyword in all_text)
            keyword_diversity = len(set([word for word in all_text.split() if len(word) > 2]))
            
            # 내용 품질 점수
            content_quality_score = min(
                (avg_speech_length / 100) * 0.3 +  # 발언 길이
                (keyword_count / 10) * 0.4 +       # 정책 키워드
                (keyword_diversity / 100) * 0.3,   # 키워드 다양성
                10
            )
            
            conn.close()
            
            return {
                "avg_speech_length": avg_speech_length,
                "keyword_diversity": keyword_diversity,
                "policy_keywords": keyword_count,
                "content_quality_score": content_quality_score
            }
            
        except Exception as e:
            logger.error(f"발언 내용 분석 실패 ({politician_name}): {e}")
            return {
                "avg_speech_length": 0,
                "keyword_diversity": 0,
                "policy_keywords": 0,
                "content_quality_score": 0
            }
    
    def calculate_influence_score(self, politician_name: str) -> float:
        """영향력 점수 계산"""
        try:
            conn = sqlite3.connect(self.connectivity_db)
            cursor = conn.cursor()
            
            # 연결성 점수
            cursor.execute('''
                SELECT COUNT(*) FROM connectivity_network
                WHERE politician_a = ? OR politician_b = ?
            ''', (politician_name, politician_name))
            connectivity_count = cursor.fetchone()[0]
            
            # 평균 연결 강도
            cursor.execute('''
                SELECT AVG(connection_strength) FROM connectivity_network
                WHERE politician_a = ? OR politician_b = ?
            ''', (politician_name, politician_name))
            avg_connection_strength = cursor.fetchone()[0] or 0
            
            conn.close()
            
            # 영향력 점수 계산 (0-10점)
            influence_score = min(
                (connectivity_count / 50) * 5 +  # 연결 수 기반
                (avg_connection_strength / 5) * 5,  # 연결 강도 기반
                10
            )
            
            return influence_score
            
        except Exception as e:
            logger.error(f"영향력 점수 계산 실패 ({politician_name}): {e}")
            return 0.0
    
    def evaluate_politician(self, politician_name: str) -> Dict:
        """개별 정치인 종합 평가"""
        # 회의록 참여도 분석
        meeting_data = self.analyze_meeting_participation(politician_name)
        
        # 발언 내용 분석
        speech_data = self.analyze_speech_content(politician_name)
        
        # 영향력 점수
        influence_score = self.calculate_influence_score(politician_name)
        
        # 종합 점수 계산
        participation_score = min(meeting_data['participation_rate'] * 10, 10)
        activity_score = min(meeting_data['speech_frequency'] * 2, 10)
        diversity_score = min(meeting_data['committee_diversity'] * 2, 10)
        content_score = speech_data['content_quality_score']
        
        # 가중 평균으로 종합 점수 계산
        total_score = (
            participation_score * 0.25 +    # 참여도 25%
            activity_score * 0.25 +         # 활동도 25%
            diversity_score * 0.20 +        # 다양성 20%
            content_score * 0.15 +          # 내용 품질 15%
            influence_score * 0.15          # 영향력 15%
        )
        
        return {
            "politician_name": politician_name,
            "total_score": round(total_score, 2),
            "participation_score": round(participation_score, 2),
            "activity_score": round(activity_score, 2),
            "diversity_score": round(diversity_score, 2),
            "content_score": round(content_score, 2),
            "influence_score": round(influence_score, 2),
            "meeting_data": meeting_data,
            "speech_data": speech_data
        }
    
    def run_comprehensive_evaluation(self):
        """종합 평가 실행"""
        logger.info("회의록 기반 정치인 평가 시작...")
        
        self.evaluation_results = []
        
        for politician in self.politicians_data:
            name = politician.get('name', '')
            if name:
                try:
                    result = self.evaluate_politician(name)
                    self.evaluation_results.append(result)
                except Exception as e:
                    logger.error(f"정치인 평가 실패 ({name}): {e}")
        
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
        cursor.execute('DELETE FROM politician_activity')
        cursor.execute('DELETE FROM committee_activity')
        
        for result in self.evaluation_results:
            # 기본 활동 정보 저장
            cursor.execute('''
                INSERT INTO politician_activity (
                    politician_name, total_meetings, total_speeches,
                    committee_meetings, committee_diversity, speech_frequency,
                    participation_rate, influence_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result['politician_name'],
                result['meeting_data']['total_meetings'],
                result['meeting_data']['total_speeches'],
                result['meeting_data']['total_meetings'],  # committee_meetings
                result['meeting_data']['committee_diversity'],
                result['meeting_data']['speech_frequency'],
                result['meeting_data']['participation_rate'],
                result['influence_score']
            ))
            
            # 위원회별 활동 정보 저장
            for committee, meeting_count, speech_count in result['meeting_data']['committee_data']:
                avg_speeches = speech_count / max(meeting_count, 1)
                cursor.execute('''
                    INSERT INTO committee_activity (
                        politician_name, committee_name, meeting_count,
                        speech_count, avg_speeches_per_meeting
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    result['politician_name'], committee, meeting_count,
                    speech_count, avg_speeches
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
            # 정치인 정보에서 정당 찾기
            politician_info = next(
                (p for p in self.politicians_data if p.get('name') == result['politician_name']), 
                {}
            )
            party = politician_info.get('party', '정당정보없음')
            
            if party not in party_ranking:
                party_ranking[party] = []
            party_ranking[party].append(result)
        
        return party_ranking
    
    def get_committee_ranking(self) -> Dict[str, List[Dict]]:
        """위원회별 순위"""
        committee_ranking = {}
        for result in self.evaluation_results:
            # 정치인 정보에서 위원회 찾기
            politician_info = next(
                (p for p in self.politicians_data if p.get('name') == result['politician_name']), 
                {}
            )
            committee = politician_info.get('committee', '위원회정보없음')
            
            if committee not in committee_ranking:
                committee_ranking[committee] = []
            committee_ranking[committee].append(result)
        
        return committee_ranking
    
    def print_evaluation_summary(self):
        """평가 결과 요약 출력"""
        print("\n=== 회의록 기반 정치인 평가 결과 ===")
        print(f"총 평가 대상: {len(self.evaluation_results)}명")
        
        # 상위 10명
        print("\n=== 상위 10명 ===")
        for i, result in enumerate(self.evaluation_results[:10]):
            print(f"{i+1:2d}. {result['politician_name']:10s} - "
                  f"총점:{result['total_score']:5.2f} "
                  f"참여:{result['participation_score']:4.1f} "
                  f"활동:{result['activity_score']:4.1f} "
                  f"다양성:{result['diversity_score']:4.1f} "
                  f"영향력:{result['influence_score']:4.1f}")
        
        # 정당별 상위 3명
        print("\n=== 정당별 상위 3명 ===")
        party_ranking = self.get_party_ranking()
        for party, politicians in party_ranking.items():
            print(f"\n{party}:")
            for i, pol in enumerate(politicians[:3]):
                print(f"  {i+1}. {pol['politician_name']} - {pol['total_score']:.2f}점")

if __name__ == "__main__":
    evaluator = MeetingBasedEvaluation()
    results = evaluator.run_comprehensive_evaluation()
    evaluator.print_evaluation_summary()
