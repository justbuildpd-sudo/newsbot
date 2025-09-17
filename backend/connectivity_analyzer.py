#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
정치인 연결성 분석기
정당별, 위원회별 연결성을 분석하여 패밀리트리 구축
"""

import json
import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from typing import Dict, List, Tuple, Set
import logging
from datetime import datetime
import os

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectivityAnalyzer:
    def __init__(self, politicians_json_path: str = "data/politicians.json"):
        self.politicians_json_path = politicians_json_path
        self.db_path = "connectivity_network.db"
        self.graph = nx.Graph()
        self.politicians_data = []
        self.init_database()
        self.load_politicians_data()
    
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 정치인 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS politicians (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                party_name TEXT,
                district TEXT,
                committee TEXT,
                terms TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 연결성 네트워크 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS connectivity_network (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                politician_a TEXT,
                politician_b TEXT,
                connection_strength INTEGER DEFAULT 1,
                connection_type TEXT,  -- 'party', 'committee', 'district'
                connection_value TEXT,  -- 정당명, 위원회명, 지역구명
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("데이터베이스 초기화 완료")
    
    def load_politicians_data(self):
        """정치인 데이터 로드"""
        try:
            with open(self.politicians_json_path, 'r', encoding='utf-8') as f:
                self.politicians_data = json.load(f)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 기존 데이터 삭제
            cursor.execute('DELETE FROM politicians')
            
            for politician in self.politicians_data:
                cursor.execute('''
                    INSERT INTO politicians (name, party_name, district, committee, terms)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    politician.get('name', ''),
                    politician.get('party', ''),
                    politician.get('district', ''),
                    politician.get('committee', ''),
                    politician.get('terms', '')
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"{len(self.politicians_data)}명 정치인 데이터 로드 완료")
            
        except Exception as e:
            logger.error(f"정치인 데이터 로드 실패: {e}")
    
    def analyze_party_connectivity(self):
        """정당별 연결성 분석"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 정당 연결성 삭제
        cursor.execute('DELETE FROM connectivity_network WHERE connection_type = "party"')
        
        # 정당별 정치인 그룹화
        party_groups = {}
        cursor.execute('SELECT name, party_name FROM politicians WHERE party_name IS NOT NULL AND party_name != ""')
        
        for name, party in cursor.fetchall():
            if party not in party_groups:
                party_groups[party] = []
            party_groups[party].append(name)
        
        # 정당 내 연결성 구축
        connections = 0
        for party, members in party_groups.items():
            if len(members) > 1:
                for i, member_a in enumerate(members):
                    for j, member_b in enumerate(members):
                        if i < j:  # 중복 방지
                            cursor.execute('''
                                INSERT INTO connectivity_network 
                                (politician_a, politician_b, connection_strength, connection_type, connection_value)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (member_a, member_b, 1, 'party', party))
                            connections += 1
        
        conn.commit()
        conn.close()
        logger.info(f"정당별 연결성 분석 완료: {connections}개 연결")
        return connections
    
    def analyze_committee_connectivity(self):
        """위원회별 연결성 분석"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 위원회 연결성 삭제
        cursor.execute('DELETE FROM connectivity_network WHERE connection_type = "committee"')
        
        # 위원회별 정치인 그룹화
        committee_groups = {}
        cursor.execute('SELECT name, committee FROM politicians WHERE committee IS NOT NULL AND committee != ""')
        
        for name, committee in cursor.fetchall():
            if committee not in committee_groups:
                committee_groups[committee] = []
            committee_groups[committee].append(name)
        
        # 위원회 내 연결성 구축
        connections = 0
        for committee, members in committee_groups.items():
            if len(members) > 1:
                for i, member_a in enumerate(members):
                    for j, member_b in enumerate(members):
                        if i < j:  # 중복 방지
                            cursor.execute('''
                                INSERT INTO connectivity_network 
                                (politician_a, politician_b, connection_strength, connection_type, connection_value)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (member_a, member_b, 2, 'committee', committee))
                            connections += 1
        
        conn.commit()
        conn.close()
        logger.info(f"위원회별 연결성 분석 완료: {connections}개 연결")
        return connections
    
    def analyze_district_connectivity(self):
        """지역구별 연결성 분석"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 지역구 연결성 삭제
        cursor.execute('DELETE FROM connectivity_network WHERE connection_type = "district"')
        
        # 지역구별 정치인 그룹화
        district_groups = {}
        cursor.execute('SELECT name, district FROM politicians WHERE district IS NOT NULL AND district != ""')
        
        for name, district in cursor.fetchall():
            if district not in district_groups:
                district_groups[district] = []
            district_groups[district].append(name)
        
        # 지역구 내 연결성 구축
        connections = 0
        for district, members in district_groups.items():
            if len(members) > 1:
                for i, member_a in enumerate(members):
                    for j, member_b in enumerate(members):
                        if i < j:  # 중복 방지
                            cursor.execute('''
                                INSERT INTO connectivity_network 
                                (politician_a, politician_b, connection_strength, connection_type, connection_value)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (member_a, member_b, 1, 'district', district))
                            connections += 1
        
        conn.commit()
        conn.close()
        logger.info(f"지역구별 연결성 분석 완료: {connections}개 연결")
        return connections
    
    def build_network_graph(self):
        """네트워크 그래프 구축"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 연결성 데이터 로드
        cursor.execute('''
            SELECT politician_a, politician_b, connection_strength, connection_type, connection_value
            FROM connectivity_network
        ''')
        
        connections = cursor.fetchall()
        conn.close()
        
        # NetworkX 그래프 구축
        self.graph.clear()
        
        # 노드 추가 (정치인)
        for politician in self.politicians_data:
            self.graph.add_node(
                politician['name'],
                party=politician.get('party', ''),
                district=politician.get('district', ''),
                committee=politician.get('committee', ''),
                terms=politician.get('terms', '')
            )
        
        # 엣지 추가 (연결성)
        for politician_a, politician_b, strength, conn_type, conn_value in connections:
            self.graph.add_edge(
                politician_a, politician_b,
                weight=strength,
                connection_type=conn_type,
                connection_value=conn_value
            )
        
        logger.info(f"네트워크 그래프 구축 완료: {self.graph.number_of_nodes()}개 노드, {self.graph.number_of_edges()}개 엣지")
        return self.graph
    
    def get_connectivity_stats(self):
        """연결성 통계 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 전체 통계
        cursor.execute('SELECT COUNT(*) FROM politicians')
        total_politicians = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM connectivity_network')
        total_connections = cursor.fetchone()[0]
        
        # 연결 타입별 통계
        cursor.execute('''
            SELECT connection_type, COUNT(*) as count
            FROM connectivity_network
            GROUP BY connection_type
        ''')
        connection_types = cursor.fetchall()
        
        # 가장 연결성이 높은 정치인
        cursor.execute('''
            SELECT politician_a, COUNT(*) as connection_count
            FROM connectivity_network
            GROUP BY politician_a
            ORDER BY connection_count DESC
            LIMIT 10
        ''')
        top_connected = cursor.fetchall()
        
        # 정당별 연결성
        cursor.execute('''
            SELECT p.party_name, COUNT(cn.id) as connection_count
            FROM politicians p
            LEFT JOIN connectivity_network cn ON p.name = cn.politician_a OR p.name = cn.politician_b
            GROUP BY p.party_name
            ORDER BY connection_count DESC
        ''')
        party_connections = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_politicians': total_politicians,
            'total_connections': total_connections,
            'connection_types': connection_types,
            'top_connected': top_connected,
            'party_connections': party_connections
        }
    
    def create_family_tree_visualization(self, output_path: str = "family_tree.png"):
        """패밀리트리 시각화 생성"""
        if not self.graph.nodes():
            logger.error("그래프가 비어있습니다.")
            return
        
        # 그래프 레이아웃 계산
        pos = nx.spring_layout(self.graph, k=3, iterations=50)
        
        # 정당별 색상 매핑
        party_colors = {
            '국민의힘': '#E53E3E',
            '더불어민주당': '#3182CE',
            '정의당': '#38A169',
            '개혁신당': '#805AD5',
            '정당정보없음': '#718096'
        }
        
        # 노드 색상 설정
        node_colors = []
        for node in self.graph.nodes():
            party = self.graph.nodes[node].get('party', '정당정보없음')
            node_colors.append(party_colors.get(party, '#718096'))
        
        # 그래프 그리기
        plt.figure(figsize=(20, 16))
        
        # 엣지 그리기
        nx.draw_networkx_edges(
            self.graph, pos,
            alpha=0.3,
            width=0.5,
            edge_color='gray'
        )
        
        # 노드 그리기
        nx.draw_networkx_nodes(
            self.graph, pos,
            node_color=node_colors,
            node_size=100,
            alpha=0.8
        )
        
        # 라벨 그리기 (중요한 노드만)
        important_nodes = [node for node in self.graph.nodes() 
                          if self.graph.degree(node) > 5]
        labels = {node: node for node in important_nodes}
        nx.draw_networkx_labels(
            self.graph, pos, labels,
            font_size=8,
            font_weight='bold'
        )
        
        # 범례 추가
        legend_elements = []
        for party, color in party_colors.items():
            if any(self.graph.nodes[node].get('party') == party for node in self.graph.nodes()):
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                                markerfacecolor=color, markersize=10, label=party))
        
        plt.legend(handles=legend_elements, loc='upper right')
        plt.title('국회의원 연결성 네트워크 (패밀리트리)', fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        
        # 이미지 저장
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"패밀리트리 시각화 저장 완료: {output_path}")
    
    def run_full_analysis(self):
        """전체 분석 실행"""
        logger.info("연결성 분석 시작...")
        
        # 각 연결성 분석
        party_connections = self.analyze_party_connectivity()
        committee_connections = self.analyze_committee_connectivity()
        district_connections = self.analyze_district_connectivity()
        
        # 네트워크 그래프 구축
        self.build_network_graph()
        
        # 통계 생성
        stats = self.get_connectivity_stats()
        
        # 패밀리트리 시각화
        self.create_family_tree_visualization()
        
        return {
            'party_connections': party_connections,
            'committee_connections': committee_connections,
            'district_connections': district_connections,
            'total_connections': party_connections + committee_connections + district_connections,
            'stats': stats
        }

if __name__ == "__main__":
    analyzer = ConnectivityAnalyzer()
    result = analyzer.run_full_analysis()
    print(f"분석 완료: {result}")

