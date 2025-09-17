#!/usr/bin/env python3
"""
고도화된 연결성 분석 시스템
개별 인물별 강력한 연결점 중심의 다단계 연결성 분석
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
import statistics
from collections import defaultdict, Counter
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class AdvancedConnectivityAnalyzer:
    def __init__(self, db_path: str = "data/legislative_data_standalone.db"):
        self.db_path = db_path
        self.init_database()
        
        # 연결성 유형별 색상 정의
        self.connection_colors = {
            "정치적_연결": "#FF6B6B",      # 빨간색 - 정당, 정치적 동맹
            "입법_연결": "#4ECDC4",        # 청록색 - 공동발의, 입법협력
            "위원회_연결": "#45B7D1",      # 파란색 - 같은 위원회 활동
            "지역_연결": "#96CEB4",        # 연두색 - 같은 지역구
            "정책_연결": "#FFEAA7",        # 노란색 - 유사 정책 관심사
            "시간_연결": "#DDA0DD",        # 보라색 - 동시기 활동
            "기타_연결": "#A0A0A0"         # 회색 - 기타 연결
        }
        
        # 연결 강도별 굵기 정의
        self.connection_widths = {
            "매우강함": 8.0,
            "강함": 6.0,
            "보통": 4.0,
            "약함": 2.0,
            "매우약함": 1.0
        }
        
        # 연결 대상별 선 스타일 정의
        self.connection_styles = {
            "정치인": "-",           # 실선
            "정당": "--",            # 점선
            "위원회": ":",           # 점선
            "지역": "-.",            # 점쇄선
            "정책": "-",             # 실선
            "기타": "-"              # 실선
        }
    
    def init_database(self):
        """고도화된 연결성 분석을 위한 데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 연결성 분석 결과 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS advanced_connectivity_analysis (
                politician_name TEXT PRIMARY KEY,
                total_connections INTEGER DEFAULT 0,
                political_connections INTEGER DEFAULT 0,
                legislative_connections INTEGER DEFAULT 0,
                committee_connections INTEGER DEFAULT 0,
                regional_connections INTEGER DEFAULT 0,
                policy_connections INTEGER DEFAULT 0,
                temporal_connections INTEGER DEFAULT 0,
                connectivity_score REAL DEFAULT 0.0,
                influence_score REAL DEFAULT 0.0,
                centrality_score REAL DEFAULT 0.0,
                main_connection_points TEXT,
                connection_network_data TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 개별 연결 관계 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS individual_connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                politician_name TEXT,
                connected_to TEXT,
                connection_type TEXT,
                connection_strength REAL,
                connection_meaning TEXT,
                connection_details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (politician_name) REFERENCES advanced_connectivity_analysis (politician_name)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("고도화된 연결성 분석 데이터베이스 초기화 완료")
    
    def analyze_politician_connectivity(self, politician_name: str) -> Dict:
        """개별 정치인의 연결성 분석"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 1. 기본 입법 활동 데이터 수집
            cursor.execute('''
                SELECT 
                    b.bill_id, b.bill_name, b.proposal_date, b.committee_name,
                    b.co_proposers, a.bill_category, a.policy_impact_score
                FROM real_assembly_bills_22nd b
                LEFT JOIN real_bill_analysis_22nd a ON b.bill_id = a.bill_id
                WHERE b.proposer_name = ?
                ORDER BY b.proposal_date DESC
            ''', (politician_name,))
            
            bills = cursor.fetchall()
            
            # 2. 의원 프로필 정보 수집
            cursor.execute('''
                SELECT party, district, committee, political_orientation
                FROM politician_profiles
                WHERE politician_name = ?
            ''', (politician_name,))
            
            profile = cursor.fetchone()
            
            # 3. 연결성 분석 수행
            connections = self.find_connections(politician_name, bills, profile, cursor)
            
            # 4. 연결성 점수 계산
            connectivity_scores = self.calculate_connectivity_scores(connections)
            
            # 5. 주요 연결점 식별
            main_connection_points = self.identify_main_connection_points(connections)
            
            # 6. 네트워크 데이터 생성
            network_data = self.generate_network_data(politician_name, connections)
            
            return {
                "politician_name": politician_name,
                "profile": {
                    "party": profile[0] if profile else "미분류",
                    "district": profile[1] if profile else "미분류",
                    "committee": profile[2] if profile else "미분류",
                    "political_orientation": profile[3] if profile else "미분류"
                },
                "connections": connections,
                "scores": connectivity_scores,
                "main_connection_points": main_connection_points,
                "network_data": network_data
            }
            
        except Exception as e:
            logger.error(f"연결성 분석 실패 ({politician_name}): {e}")
            return {}
        finally:
            conn.close()
    
    def find_connections(self, politician_name: str, bills: List, profile: Tuple, cursor) -> List[Dict]:
        """연결 관계 찾기"""
        connections = []
        
        # 1. 공동발의자 연결 (입법 연결)
        legislative_connections = self.find_legislative_connections(politician_name, bills, cursor)
        connections.extend(legislative_connections)
        
        # 2. 같은 위원회 연결 (위원회 연결)
        committee_connections = self.find_committee_connections(politician_name, profile, cursor)
        connections.extend(committee_connections)
        
        # 3. 같은 정당 연결 (정치적 연결)
        political_connections = self.find_political_connections(politician_name, profile, cursor)
        connections.extend(political_connections)
        
        # 4. 같은 지역구 연결 (지역 연결)
        regional_connections = self.find_regional_connections(politician_name, profile, cursor)
        connections.extend(regional_connections)
        
        # 5. 유사 정책 관심사 연결 (정책 연결)
        policy_connections = self.find_policy_connections(politician_name, bills, cursor)
        connections.extend(policy_connections)
        
        # 6. 동시기 활동 연결 (시간 연결)
        temporal_connections = self.find_temporal_connections(politician_name, bills, cursor)
        connections.extend(temporal_connections)
        
        return connections
    
    def find_legislative_connections(self, politician_name: str, bills: List, cursor) -> List[Dict]:
        """입법 연결 찾기 (공동발의자)"""
        connections = []
        
        for bill in bills:
            bill_id, bill_name, proposal_date, committee_name, co_proposers, bill_category, policy_impact = bill
            
            if co_proposers and co_proposers.strip():
                # 공동발의자 파싱 (간단한 형태로 가정)
                co_proposer_list = [name.strip() for name in co_proposers.split(',') if name.strip()]
                
                for co_proposer in co_proposer_list:
                    if co_proposer != politician_name:
                        # 연결 강도 계산
                        strength = self.calculate_connection_strength(
                            "입법", bill_category, policy_impact, 1
                        )
                        
                        connections.append({
                            "connected_to": co_proposer,
                            "connection_type": "입법_연결",
                            "connection_strength": strength,
                            "connection_meaning": f"공동발의: {bill_name[:30]}...",
                            "connection_details": {
                                "bill_name": bill_name,
                                "bill_category": bill_category,
                                "proposal_date": proposal_date,
                                "committee": committee_name,
                                "policy_impact": policy_impact or 0
                            },
                            "target_type": "정치인"
                        })
        
        return connections
    
    def find_committee_connections(self, politician_name: str, profile: Tuple, cursor) -> List[Dict]:
        """위원회 연결 찾기"""
        connections = []
        
        if not profile or not profile[2]:
            return connections
        
        committee = profile[2]
        
        # 같은 위원회 의원들 찾기
        cursor.execute('''
            SELECT DISTINCT proposer_name, COUNT(*) as bill_count
            FROM real_assembly_bills_22nd
            WHERE committee_name = ? AND proposer_name != ?
            GROUP BY proposer_name
            ORDER BY bill_count DESC
            LIMIT 10
        ''', (committee, politician_name))
        
        committee_members = cursor.fetchall()
        
        for member, bill_count in committee_members:
            strength = min(bill_count * 0.1, 1.0)  # 최대 1.0
            
            connections.append({
                "connected_to": member,
                "connection_type": "위원회_연결",
                "connection_strength": strength,
                "connection_meaning": f"같은 위원회: {committee}",
                "connection_details": {
                    "committee": committee,
                    "bill_count": bill_count,
                    "connection_level": "위원회"
                },
                "target_type": "정치인"
            })
        
        return connections
    
    def find_political_connections(self, politician_name: str, profile: Tuple, cursor) -> List[Dict]:
        """정치적 연결 찾기 (같은 정당)"""
        connections = []
        
        if not profile or not profile[0]:
            return connections
        
        party = profile[0]
        
        # 같은 정당 의원들 찾기
        cursor.execute('''
            SELECT DISTINCT proposer_name, COUNT(*) as bill_count
            FROM real_assembly_bills_22nd b
            JOIN politician_profiles p ON b.proposer_name = p.politician_name
            WHERE p.party = ? AND b.proposer_name != ?
            GROUP BY proposer_name
            ORDER BY bill_count DESC
            LIMIT 10
        ''', (party, politician_name))
        
        party_members = cursor.fetchall()
        
        for member, bill_count in party_members:
            strength = min(bill_count * 0.05, 1.0)  # 최대 1.0
            
            connections.append({
                "connected_to": member,
                "connection_type": "정치적_연결",
                "connection_strength": strength,
                "connection_meaning": f"같은 정당: {party}",
                "connection_details": {
                    "party": party,
                    "bill_count": bill_count,
                    "connection_level": "정당"
                },
                "target_type": "정치인"
            })
        
        return connections
    
    def find_regional_connections(self, politician_name: str, profile: Tuple, cursor) -> List[Dict]:
        """지역 연결 찾기 (같은 지역구)"""
        connections = []
        
        if not profile or not profile[1]:
            return connections
        
        district = profile[1]
        
        # 같은 지역구 의원들 찾기 (간단한 지역명 매칭)
        cursor.execute('''
            SELECT DISTINCT proposer_name, COUNT(*) as bill_count
            FROM real_assembly_bills_22nd b
            JOIN politician_profiles p ON b.proposer_name = p.politician_name
            WHERE p.district LIKE ? AND b.proposer_name != ?
            GROUP BY proposer_name
            ORDER BY bill_count DESC
            LIMIT 5
        ''', (f"%{district}%", politician_name))
        
        regional_members = cursor.fetchall()
        
        for member, bill_count in regional_members:
            strength = min(bill_count * 0.08, 1.0)  # 최대 1.0
            
            connections.append({
                "connected_to": member,
                "connection_type": "지역_연결",
                "connection_strength": strength,
                "connection_meaning": f"같은 지역: {district}",
                "connection_details": {
                    "district": district,
                    "bill_count": bill_count,
                    "connection_level": "지역"
                },
                "target_type": "정치인"
            })
        
        return connections
    
    def find_policy_connections(self, politician_name: str, bills: List, cursor) -> List[Dict]:
        """정책 연결 찾기 (유사 정책 관심사)"""
        connections = []
        
        # 해당 의원의 정책 관심사 키워드 추출
        policy_keywords = self.extract_policy_keywords(bills)
        
        if not policy_keywords:
            return connections
        
        # 유사한 정책 관심사를 가진 의원들 찾기
        for keyword in policy_keywords[:5]:  # 상위 5개 키워드만
            cursor.execute('''
                SELECT DISTINCT proposer_name, COUNT(*) as bill_count
                FROM real_assembly_bills_22nd
                WHERE bill_name LIKE ? AND proposer_name != ?
                GROUP BY proposer_name
                ORDER BY bill_count DESC
                LIMIT 3
            ''', (f"%{keyword}%", politician_name))
            
            similar_politicians = cursor.fetchall()
            
            for member, bill_count in similar_politicians:
                strength = min(bill_count * 0.1, 1.0)  # 최대 1.0
                
                connections.append({
                    "connected_to": member,
                    "connection_type": "정책_연결",
                    "connection_strength": strength,
                    "connection_meaning": f"유사 정책: {keyword}",
                    "connection_details": {
                        "policy_keyword": keyword,
                        "bill_count": bill_count,
                        "connection_level": "정책"
                    },
                    "target_type": "정치인"
                })
        
        return connections
    
    def find_temporal_connections(self, politician_name: str, bills: List, cursor) -> List[Dict]:
        """시간 연결 찾기 (동시기 활동)"""
        connections = []
        
        if not bills:
            return connections
        
        # 해당 의원의 활동 기간 추출
        proposal_dates = [bill[2] for bill in bills if bill[2]]
        if not proposal_dates:
            return connections
        
        # 동시기 활동 의원들 찾기
        for date in proposal_dates[:5]:  # 최근 5개 날짜만
            cursor.execute('''
                SELECT DISTINCT proposer_name, COUNT(*) as bill_count
                FROM real_assembly_bills_22nd
                WHERE proposal_date = ? AND proposer_name != ?
                GROUP BY proposer_name
                ORDER BY bill_count DESC
                LIMIT 3
            ''', (date, politician_name))
            
            temporal_members = cursor.fetchall()
            
            for member, bill_count in temporal_members:
                strength = min(bill_count * 0.2, 1.0)  # 최대 1.0
                
                connections.append({
                    "connected_to": member,
                    "connection_type": "시간_연결",
                    "connection_strength": strength,
                    "connection_meaning": f"동시기 활동: {date}",
                    "connection_details": {
                        "activity_date": date,
                        "bill_count": bill_count,
                        "connection_level": "시간"
                    },
                    "target_type": "정치인"
                })
        
        return connections
    
    def extract_policy_keywords(self, bills: List) -> List[str]:
        """정책 키워드 추출"""
        keywords = []
        
        for bill in bills:
            bill_name = bill[1] if bill[1] else ""
            bill_category = bill[5] if bill[5] else ""
            
            # 간단한 키워드 추출 (실제로는 더 정교한 NLP 필요)
            if "환경" in bill_name:
                keywords.append("환경")
            if "복지" in bill_name:
                keywords.append("복지")
            if "교육" in bill_name:
                keywords.append("교육")
            if "경제" in bill_name:
                keywords.append("경제")
            if "안전" in bill_name:
                keywords.append("안전")
            if "보건" in bill_name:
                keywords.append("보건")
        
        # 키워드 빈도 계산
        keyword_counts = Counter(keywords)
        return [keyword for keyword, count in keyword_counts.most_common(10)]
    
    def calculate_connection_strength(self, connection_type: str, bill_category: str, 
                                    policy_impact: float, base_strength: float) -> float:
        """연결 강도 계산"""
        strength = base_strength
        
        # 정책 영향도 반영
        if policy_impact:
            strength *= (1 + policy_impact / 100)
        
        # 법안 카테고리별 가중치
        category_weights = {
            "정책법안": 1.5,
            "실질입법": 1.3,
            "의안정리": 1.0,
            "기술수정": 0.8
        }
        
        if bill_category in category_weights:
            strength *= category_weights[bill_category]
        
        return min(strength, 1.0)  # 최대 1.0
    
    def calculate_connectivity_scores(self, connections: List[Dict]) -> Dict:
        """연결성 점수 계산"""
        if not connections:
            return {
                "total_connections": 0,
                "political_connections": 0,
                "legislative_connections": 0,
                "committee_connections": 0,
                "regional_connections": 0,
                "policy_connections": 0,
                "temporal_connections": 0,
                "connectivity_score": 0.0,
                "influence_score": 0.0,
                "centrality_score": 0.0
            }
        
        # 연결 유형별 개수 계산
        connection_counts = defaultdict(int)
        total_strength = 0
        
        for conn in connections:
            conn_type = conn["connection_type"]
            connection_counts[conn_type] += 1
            total_strength += conn["connection_strength"]
        
        # 연결성 점수 계산
        connectivity_score = min(total_strength * 10, 100)  # 최대 100점
        
        # 영향력 점수 (연결된 사람들의 평균 영향력)
        influence_score = min(len(connections) * 5, 100)  # 최대 100점
        
        # 중심성 점수 (다양한 유형의 연결)
        centrality_score = min(len(set(conn["connection_type"] for conn in connections)) * 20, 100)
        
        return {
            "total_connections": len(connections),
            "political_connections": connection_counts["정치적_연결"],
            "legislative_connections": connection_counts["입법_연결"],
            "committee_connections": connection_counts["위원회_연결"],
            "regional_connections": connection_counts["지역_연결"],
            "policy_connections": connection_counts["정책_연결"],
            "temporal_connections": connection_counts["시간_연결"],
            "connectivity_score": round(connectivity_score, 2),
            "influence_score": round(influence_score, 2),
            "centrality_score": round(centrality_score, 2)
        }
    
    def identify_main_connection_points(self, connections: List[Dict]) -> List[Dict]:
        """주요 연결점 식별"""
        if not connections:
            return []
        
        # 연결 강도별 정렬
        sorted_connections = sorted(connections, key=lambda x: x["connection_strength"], reverse=True)
        
        # 상위 5개 연결점 선택
        main_points = []
        for conn in sorted_connections[:5]:
            main_points.append({
                "connected_to": conn["connected_to"],
                "connection_type": conn["connection_type"],
                "connection_strength": conn["connection_strength"],
                "connection_meaning": conn["connection_meaning"],
                "target_type": conn["target_type"]
            })
        
        return main_points
    
    def generate_network_data(self, politician_name: str, connections: List[Dict]) -> Dict:
        """네트워크 데이터 생성"""
        network_data = {
            "nodes": [],
            "edges": [],
            "levels": {
                "level_1": [],  # 직접 연결
                "level_2": [],  # 2단계 연결
                "level_3": [],  # 3단계 연결
                "level_4": [],  # 4단계 연결
                "level_5": []   # 5단계 연결
            }
        }
        
        # 중심 노드 (분석 대상)
        network_data["nodes"].append({
            "id": politician_name,
            "name": politician_name,
            "type": "center",
            "level": 0,
            "size": 20,
            "color": "#FFD700"  # 금색
        })
        
        # 1단계 연결 (직접 연결)
        for conn in connections:
            node_id = conn["connected_to"]
            
            # 노드 추가
            network_data["nodes"].append({
                "id": node_id,
                "name": node_id,
                "type": conn["target_type"],
                "level": 1,
                "size": 15,
                "color": self.connection_colors.get(conn["connection_type"], "#A0A0A0")
            })
            
            # 엣지 추가
            network_data["edges"].append({
                "source": politician_name,
                "target": node_id,
                "type": conn["connection_type"],
                "strength": conn["connection_strength"],
                "meaning": conn["connection_meaning"],
                "width": self.get_connection_width(conn["connection_strength"]),
                "style": self.connection_styles.get(conn["target_type"], "-"),
                "color": self.connection_colors.get(conn["connection_type"], "#A0A0A0")
            })
            
            network_data["levels"]["level_1"].append({
                "node": node_id,
                "connection": conn
            })
        
        return network_data
    
    def get_connection_width(self, strength: float) -> float:
        """연결 강도에 따른 선 굵기 반환"""
        if strength >= 0.8:
            return self.connection_widths["매우강함"]
        elif strength >= 0.6:
            return self.connection_widths["강함"]
        elif strength >= 0.4:
            return self.connection_widths["보통"]
        elif strength >= 0.2:
            return self.connection_widths["약함"]
        else:
            return self.connection_widths["매우약함"]
    
    def run_comprehensive_analysis(self):
        """종합적인 연결성 분석 실행"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 분석 결과 삭제
        cursor.execute('DELETE FROM advanced_connectivity_analysis')
        cursor.execute('DELETE FROM individual_connections')
        
        # 모든 발의자 목록 조회
        cursor.execute('''
            SELECT DISTINCT proposer_name
            FROM real_assembly_bills_22nd
            WHERE proposer_name IS NOT NULL AND proposer_name != ''
            ORDER BY proposer_name
        ''')
        
        politicians = cursor.fetchall()
        logger.info(f"총 {len(politicians)}명 정치인의 연결성 분석 시작")
        
        analyzed_count = 0
        
        for politician in politicians:
            politician_name = politician[0]
            
            try:
                # 개별 연결성 분석
                analysis_result = self.analyze_politician_connectivity(politician_name)
                
                if analysis_result:
                    # 결과 저장
                    cursor.execute('''
                        INSERT INTO advanced_connectivity_analysis (
                            politician_name, total_connections, political_connections,
                            legislative_connections, committee_connections, regional_connections,
                            policy_connections, temporal_connections, connectivity_score,
                            influence_score, centrality_score, main_connection_points,
                            connection_network_data
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        politician_name,
                        analysis_result["scores"]["total_connections"],
                        analysis_result["scores"]["political_connections"],
                        analysis_result["scores"]["legislative_connections"],
                        analysis_result["scores"]["committee_connections"],
                        analysis_result["scores"]["regional_connections"],
                        analysis_result["scores"]["policy_connections"],
                        analysis_result["scores"]["temporal_connections"],
                        analysis_result["scores"]["connectivity_score"],
                        analysis_result["scores"]["influence_score"],
                        analysis_result["scores"]["centrality_score"],
                        json.dumps(analysis_result["main_connection_points"], ensure_ascii=False),
                        json.dumps(analysis_result["network_data"], ensure_ascii=False)
                    ))
                    
                    # 개별 연결 관계 저장
                    for conn in analysis_result["connections"]:
                        cursor.execute('''
                            INSERT INTO individual_connections (
                                politician_name, connected_to, connection_type,
                                connection_strength, connection_meaning, connection_details
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            politician_name,
                            conn["connected_to"],
                            conn["connection_type"],
                            conn["connection_strength"],
                            conn["connection_meaning"],
                            json.dumps(conn["connection_details"], ensure_ascii=False)
                        ))
                    
                    analyzed_count += 1
                    
                    if analyzed_count % 50 == 0:
                        logger.info(f"연결성 분석 완료: {analyzed_count}명")
                
            except Exception as e:
                logger.error(f"연결성 분석 실패 ({politician_name}): {e}")
                continue
        
        conn.commit()
        conn.close()
        logger.info(f"종합 연결성 분석 완료: {analyzed_count}명")
    
    def generate_connectivity_report(self) -> Dict:
        """연결성 분석 보고서 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 전체 통계
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_analyzed,
                    AVG(connectivity_score) as avg_connectivity,
                    AVG(influence_score) as avg_influence,
                    AVG(centrality_score) as avg_centrality,
                    MAX(connectivity_score) as max_connectivity,
                    MIN(connectivity_score) as min_connectivity
                FROM advanced_connectivity_analysis
            ''')
            
            stats = cursor.fetchone()
            
            # 상위 연결성 의원들
            cursor.execute('''
                SELECT politician_name, connectivity_score, influence_score, centrality_score
                FROM advanced_connectivity_analysis
                ORDER BY connectivity_score DESC
                LIMIT 10
            ''')
            
            top_connected = [{"name": row[0], "connectivity": row[1], "influence": row[2], "centrality": row[3]} for row in cursor.fetchall()]
            
            # 연결 유형별 통계
            cursor.execute('''
                SELECT 
                    AVG(political_connections) as avg_political,
                    AVG(legislative_connections) as avg_legislative,
                    AVG(committee_connections) as avg_committee,
                    AVG(regional_connections) as avg_regional,
                    AVG(policy_connections) as avg_policy,
                    AVG(temporal_connections) as avg_temporal
                FROM advanced_connectivity_analysis
            ''')
            
            connection_type_stats = cursor.fetchone()
            
            report = {
                "analysis_date": datetime.now().isoformat(),
                "total_analyzed_politicians": stats[0],
                "average_scores": {
                    "connectivity": round(stats[1], 2),
                    "influence": round(stats[2], 2),
                    "centrality": round(stats[3], 2)
                },
                "score_range": {
                    "max_connectivity": round(stats[4], 2),
                    "min_connectivity": round(stats[5], 2)
                },
                "top_connected_politicians": top_connected,
                "connection_type_averages": {
                    "political": round(connection_type_stats[0], 2),
                    "legislative": round(connection_type_stats[1], 2),
                    "committee": round(connection_type_stats[2], 2),
                    "regional": round(connection_type_stats[3], 2),
                    "policy": round(connection_type_stats[4], 2),
                    "temporal": round(connection_type_stats[5], 2)
                }
            }
            
            # 보고서 저장
            with open("data/advanced_connectivity_report.json", 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info("고도화된 연결성 분석 보고서 생성 완료")
            return report
            
        except Exception as e:
            logger.error(f"연결성 보고서 생성 실패: {e}")
            return {}
        finally:
            conn.close()

if __name__ == "__main__":
    analyzer = AdvancedConnectivityAnalyzer()
    analyzer.run_comprehensive_analysis()
    report = analyzer.generate_connectivity_report()
    
    if report:
        print("✅ 고도화된 연결성 분석이 성공적으로 완료되었습니다.")
        print(f"📊 분석된 정치인 수: {report.get('total_analyzed_politicians', 0)}명")
        print(f"📈 평균 연결성 점수: {report.get('average_scores', {}).get('connectivity', 0)}점")
    else:
        print("❌ 연결성 분석 중 오류가 발생했습니다.")

