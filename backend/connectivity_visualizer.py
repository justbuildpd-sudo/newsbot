#!/usr/bin/env python3
"""
연결성 시각화 시스템
3단계(위젯)와 5단계(보고서) 연결성 시각화
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import networkx as nx
import numpy as np
from collections import defaultdict

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class ConnectivityVisualizer:
    def __init__(self, db_path: str = "data/legislative_data_standalone.db"):
        self.db_path = db_path
        
        # 연결성 유형별 색상 정의
        self.connection_colors = {
            "입법_연결": "#FF6B6B",      # 빨간색 - 공동발의
            "위원회_연결": "#4ECDC4",    # 청록색 - 같은 위원회
            "정치적_연결": "#45B7D1",    # 파란색 - 같은 정당
            "지역_연결": "#96CEB4",      # 연두색 - 같은 지역구
            "정책_연결": "#FFEAA7",      # 노란색 - 유사 정책
            "시간_연결": "#DDA0DD",      # 보라색 - 동시기 활동
            "기타_연결": "#A0A0A0"       # 회색 - 기타
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
    
    def get_connection_color(self, connection_type: str) -> str:
        """연결 유형에 따른 색상 반환"""
        return self.connection_colors.get(connection_type, "#A0A0A0")
    
    def get_connection_style(self, target_type: str) -> str:
        """연결 대상에 따른 선 스타일 반환"""
        return self.connection_styles.get(target_type, "-")
    
    def create_widget_visualization(self, politician_name: str, max_levels: int = 3) -> Dict:
        """위젯용 3단계 연결성 시각화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 해당 정치인의 기본 연결성 데이터 조회
            cursor.execute('''
                SELECT main_connections, connectivity_score
                FROM basic_connectivity_analysis
                WHERE politician_name = ?
            ''', (politician_name,))
            
            result = cursor.fetchone()
            if not result:
                return {"error": "정치인을 찾을 수 없습니다"}
            
            main_connections = json.loads(result[0]) if result[0] else []
            connectivity_score = result[1] or 0
            
            # 네트워크 데이터 생성
            network_data = self.build_network_data(politician_name, main_connections, max_levels)
            
            # 시각화 생성
            visualization_data = self.generate_visualization_data(network_data, max_levels)
            
            return {
                "politician_name": politician_name,
                "connectivity_score": connectivity_score,
                "max_levels": max_levels,
                "network_data": network_data,
                "visualization": visualization_data
            }
            
        except Exception as e:
            logger.error(f"위젯 시각화 생성 실패 ({politician_name}): {e}")
            return {"error": f"시각화 생성 실패: {e}"}
        finally:
            conn.close()
    
    def create_report_visualization(self, politician_name: str, max_levels: int = 5) -> Dict:
        """보고서용 5단계 연결성 시각화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 해당 정치인의 기본 연결성 데이터 조회
            cursor.execute('''
                SELECT main_connections, connectivity_score, total_connections,
                       legislative_connections, committee_connections, political_connections
                FROM basic_connectivity_analysis
                WHERE politician_name = ?
            ''', (politician_name,))
            
            result = cursor.fetchone()
            if not result:
                return {"error": "정치인을 찾을 수 없습니다"}
            
            main_connections = json.loads(result[0]) if result[0] else []
            connectivity_score = result[1] or 0
            total_connections = result[2] or 0
            legislative_connections = result[3] or 0
            committee_connections = result[4] or 0
            political_connections = result[5] or 0
            
            # 확장된 네트워크 데이터 생성
            expanded_network = self.build_expanded_network(politician_name, main_connections, max_levels, cursor)
            
            # 상세 시각화 생성
            detailed_visualization = self.generate_detailed_visualization(
                expanded_network, max_levels, {
                    "connectivity_score": connectivity_score,
                    "total_connections": total_connections,
                    "legislative_connections": legislative_connections,
                    "committee_connections": committee_connections,
                    "political_connections": political_connections
                }
            )
            
            return {
                "politician_name": politician_name,
                "max_levels": max_levels,
                "statistics": {
                    "connectivity_score": connectivity_score,
                    "total_connections": total_connections,
                    "legislative_connections": legislative_connections,
                    "committee_connections": committee_connections,
                    "political_connections": political_connections
                },
                "network_data": expanded_network,
                "visualization": detailed_visualization
            }
            
        except Exception as e:
            logger.error(f"보고서 시각화 생성 실패 ({politician_name}): {e}")
            return {"error": f"시각화 생성 실패: {e}"}
        finally:
            conn.close()
    
    def build_network_data(self, politician_name: str, main_connections: List[Dict], max_levels: int) -> Dict:
        """네트워크 데이터 구축"""
        network_data = {
            "nodes": [],
            "edges": [],
            "levels": {}
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
        
        # 레벨별 노드와 엣지 추가
        for level in range(1, max_levels + 1):
            network_data["levels"][f"level_{level}"] = []
        
        # 1단계 연결 (직접 연결)
        for i, conn in enumerate(main_connections[:10]):  # 상위 10개만
            node_id = conn["connected_to"]
            
            # 노드 추가
            network_data["nodes"].append({
                "id": node_id,
                "name": node_id,
                "type": "connection",
                "level": 1,
                "size": 15,
                "color": self.get_connection_color(conn["connection_type"])
            })
            
            # 엣지 추가
            network_data["edges"].append({
                "source": politician_name,
                "target": node_id,
                "type": conn["connection_type"],
                "strength": conn["strength"],
                "meaning": conn["connection_meaning"],
                "width": self.get_connection_width(conn["strength"]),
                "style": self.get_connection_style("정치인"),
                "color": self.get_connection_color(conn["connection_type"])
            })
            
            network_data["levels"]["level_1"].append({
                "node": node_id,
                "connection": conn
            })
        
        return network_data
    
    def build_expanded_network(self, politician_name: str, main_connections: List[Dict], 
                             max_levels: int, cursor) -> Dict:
        """확장된 네트워크 데이터 구축 (5단계)"""
        network_data = {
            "nodes": [],
            "edges": [],
            "levels": {}
        }
        
        # 중심 노드
        network_data["nodes"].append({
            "id": politician_name,
            "name": politician_name,
            "type": "center",
            "level": 0,
            "size": 25,
            "color": "#FFD700"
        })
        
        # 레벨별 초기화
        for level in range(1, max_levels + 1):
            network_data["levels"][f"level_{level}"] = []
        
        # 1단계 연결 (직접 연결)
        for conn in main_connections[:15]:  # 상위 15개
            node_id = conn["connected_to"]
            
            network_data["nodes"].append({
                "id": node_id,
                "name": node_id,
                "type": "connection",
                "level": 1,
                "size": 18,
                "color": self.get_connection_color(conn["connection_type"])
            })
            
            network_data["edges"].append({
                "source": politician_name,
                "target": node_id,
                "type": conn["connection_type"],
                "strength": conn["strength"],
                "meaning": conn["connection_meaning"],
                "width": self.get_connection_width(conn["strength"]),
                "style": self.get_connection_style("정치인"),
                "color": self.get_connection_color(conn["connection_type"])
            })
            
            network_data["levels"]["level_1"].append({
                "node": node_id,
                "connection": conn
            })
        
        # 2-5단계 연결 (간접 연결)
        for level in range(2, max_levels + 1):
            self.add_indirect_connections(network_data, level, cursor)
        
        return network_data
    
    def add_indirect_connections(self, network_data: Dict, level: int, cursor):
        """간접 연결 추가 (2-5단계)"""
        # 이전 레벨의 노드들에서 새로운 연결 찾기
        previous_level_nodes = network_data["levels"][f"level_{level-1}"]
        
        for node_info in previous_level_nodes[:5]:  # 각 레벨당 최대 5개 노드
            node_name = node_info["node"]
            
            # 해당 노드의 연결 찾기
            cursor.execute('''
                SELECT main_connections
                FROM basic_connectivity_analysis
                WHERE politician_name = ?
            ''', (node_name,))
            
            result = cursor.fetchone()
            if not result or not result[0]:
                continue
            
            connections = json.loads(result[0])
            
            for conn in connections[:3]:  # 각 노드당 최대 3개 연결
                target_node = conn["connected_to"]
                
                # 이미 존재하는 노드인지 확인
                if any(node["id"] == target_node for node in network_data["nodes"]):
                    continue
                
                # 노드 추가
                network_data["nodes"].append({
                    "id": target_node,
                    "name": target_node,
                    "type": "indirect_connection",
                    "level": level,
                    "size": max(15 - level * 2, 8),
                    "color": self.get_connection_color(conn["connection_type"])
                })
                
                # 엣지 추가
                network_data["edges"].append({
                    "source": node_name,
                    "target": target_node,
                    "type": conn["connection_type"],
                    "strength": conn["strength"] * (0.8 ** (level - 1)),  # 레벨에 따라 강도 감소
                    "meaning": f"{level}단계 연결: {conn['connection_meaning']}",
                    "width": self.get_connection_width(conn["strength"] * (0.8 ** (level - 1))),
                    "style": self.get_connection_style("정치인"),
                    "color": self.get_connection_color(conn["connection_type"])
                })
                
                network_data["levels"][f"level_{level}"].append({
                    "node": target_node,
                    "connection": conn
                })
    
    def generate_visualization_data(self, network_data: Dict, max_levels: int) -> Dict:
        """시각화 데이터 생성"""
        return {
            "node_count": len(network_data["nodes"]),
            "edge_count": len(network_data["edges"]),
            "level_distribution": {
                f"level_{i}": len(network_data["levels"].get(f"level_{i}", []))
                for i in range(1, max_levels + 1)
            },
            "connection_type_distribution": self.calculate_connection_type_distribution(network_data),
            "strength_distribution": self.calculate_strength_distribution(network_data),
            "legend": self.generate_legend()
        }
    
    def generate_detailed_visualization(self, network_data: Dict, max_levels: int, 
                                      statistics: Dict) -> Dict:
        """상세 시각화 데이터 생성"""
        return {
            "node_count": len(network_data["nodes"]),
            "edge_count": len(network_data["edges"]),
            "level_distribution": {
                f"level_{i}": len(network_data["levels"].get(f"level_{i}", []))
                for i in range(1, max_levels + 1)
            },
            "connection_type_distribution": self.calculate_connection_type_distribution(network_data),
            "strength_distribution": self.calculate_strength_distribution(network_data),
            "statistics": statistics,
            "legend": self.generate_legend(),
            "insights": self.generate_insights(network_data, statistics)
        }
    
    def calculate_connection_type_distribution(self, network_data: Dict) -> Dict:
        """연결 유형별 분포 계산"""
        type_counts = defaultdict(int)
        
        for edge in network_data["edges"]:
            conn_type = edge["type"]
            type_counts[conn_type] += 1
        
        return dict(type_counts)
    
    def calculate_strength_distribution(self, network_data: Dict) -> Dict:
        """연결 강도별 분포 계산"""
        strength_ranges = {
            "매우강함": 0,
            "강함": 0,
            "보통": 0,
            "약함": 0,
            "매우약함": 0
        }
        
        for edge in network_data["edges"]:
            strength = edge["strength"]
            if strength >= 0.8:
                strength_ranges["매우강함"] += 1
            elif strength >= 0.6:
                strength_ranges["강함"] += 1
            elif strength >= 0.4:
                strength_ranges["보통"] += 1
            elif strength >= 0.2:
                strength_ranges["약함"] += 1
            else:
                strength_ranges["매우약함"] += 1
        
        return strength_ranges
    
    def generate_legend(self) -> Dict:
        """범례 생성"""
        return {
            "connection_types": [
                {"type": "입법_연결", "color": self.connection_colors["입법_연결"], "meaning": "공동발의"},
                {"type": "위원회_연결", "color": self.connection_colors["위원회_연결"], "meaning": "같은 위원회"},
                {"type": "정치적_연결", "color": self.connection_colors["정치적_연결"], "meaning": "같은 정당"},
                {"type": "지역_연결", "color": self.connection_colors["지역_연결"], "meaning": "같은 지역구"},
                {"type": "정책_연결", "color": self.connection_colors["정책_연결"], "meaning": "유사 정책"},
                {"type": "시간_연결", "color": self.connection_colors["시간_연결"], "meaning": "동시기 활동"}
            ],
            "connection_strengths": [
                {"strength": "매우강함", "width": self.connection_widths["매우강함"], "range": "0.8-1.0"},
                {"strength": "강함", "width": self.connection_widths["강함"], "range": "0.6-0.8"},
                {"strength": "보통", "width": self.connection_widths["보통"], "range": "0.4-0.6"},
                {"strength": "약함", "width": self.connection_widths["약함"], "range": "0.2-0.4"},
                {"strength": "매우약함", "width": self.connection_widths["매우약함"], "range": "0.0-0.2"}
            ],
            "connection_styles": [
                {"style": "정치인", "line_style": self.connection_styles["정치인"], "meaning": "정치인 간 연결"},
                {"style": "정당", "line_style": self.connection_styles["정당"], "meaning": "정당 간 연결"},
                {"style": "위원회", "line_style": self.connection_styles["위원회"], "meaning": "위원회 간 연결"}
            ]
        }
    
    def generate_insights(self, network_data: Dict, statistics: Dict) -> List[str]:
        """연결성 인사이트 생성"""
        insights = []
        
        # 연결성 점수 기반 인사이트
        connectivity_score = statistics.get("connectivity_score", 0)
        if connectivity_score >= 80:
            insights.append("매우 높은 연결성을 보이는 정치인입니다.")
        elif connectivity_score >= 60:
            insights.append("높은 연결성을 보이는 정치인입니다.")
        elif connectivity_score >= 40:
            insights.append("보통 수준의 연결성을 보이는 정치인입니다.")
        else:
            insights.append("연결성이 상대적으로 낮은 정치인입니다.")
        
        # 연결 유형 기반 인사이트
        type_dist = self.calculate_connection_type_distribution(network_data)
        if type_dist.get("입법_연결", 0) > 5:
            insights.append("공동발의를 통한 입법적 협력이 활발합니다.")
        if type_dist.get("위원회_연결", 0) > 3:
            insights.append("위원회 활동을 통한 네트워크가 잘 형성되어 있습니다.")
        if type_dist.get("정치적_연결", 0) > 5:
            insights.append("정당 내 네트워크가 강합니다.")
        
        # 연결 강도 기반 인사이트
        strength_dist = self.calculate_strength_distribution(network_data)
        strong_connections = strength_dist.get("매우강함", 0) + strength_dist.get("강함", 0)
        if strong_connections > 3:
            insights.append("강력한 연결 관계를 다수 보유하고 있습니다.")
        
        return insights

if __name__ == "__main__":
    visualizer = ConnectivityVisualizer()
    
    # 테스트용 시각화 생성
    test_politician = "김원이 의원 등 17인"
    
    print("위젯용 3단계 연결성 시각화 생성 중...")
    widget_result = visualizer.create_widget_visualization(test_politician, 3)
    print(f"위젯 시각화 완료: {widget_result.get('node_count', 0)}개 노드, {widget_result.get('edge_count', 0)}개 연결")
    
    print("보고서용 5단계 연결성 시각화 생성 중...")
    report_result = visualizer.create_report_visualization(test_politician, 5)
    print(f"보고서 시각화 완료: {report_result.get('node_count', 0)}개 노드, {report_result.get('edge_count', 0)}개 연결")

