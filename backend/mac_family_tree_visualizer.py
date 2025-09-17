#!/usr/bin/env python3
"""
맥 패밀리트리 스타일 네트워크 시각화
단일 테마, 직관적인 트리 구조, 개인 정치인 중심
"""

import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from pyvis.network import Network
import os
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MacFamilyTreeVisualizer:
    """맥 패밀리트리 스타일 네트워크 시각화 클래스"""
    
    def __init__(self, output_dir: str = "family_tree_widgets"):
        self.output_dir = output_dir
        self.connection_colors = {
            "입법_연결": "#FF6B6B",  # 공동발의 (빨간색)
            "위원회_연결": "#4ECDC4", # 같은 위원회 (청록색)
            "정치적_연결": "#45B7D1", # 같은 정당 (파란색)
            "지역_연결": "#96CEB4",  # 같은 지역구 (연두색)
            "정책_연결": "#FFEAA7",  # 유사 정책 (노란색)
            "시간_연결": "#DDA0DD",  # 동시기 활동 (보라색)
        }
        
        # 개인 정치인 데이터 (샘플)
        self.politicians = {
            "정청래": {
                "name": "정청래",
                "party": "더불어민주당",
                "district": "서울 마포구을",
                "committee": "기획재정위원회",
                "connectivity_score": 85.5,
                "connections": [
                    {"name": "김영배", "type": "정치적_연결", "strength": 0.9, "description": "같은 정당", "level": 1},
                    {"name": "박수현", "type": "위원회_연결", "strength": 0.8, "description": "같은 위원회", "level": 1},
                    {"name": "이재정", "type": "입법_연결", "strength": 0.7, "description": "공동발의", "level": 1},
                    {"name": "최민호", "type": "지역_연결", "strength": 0.6, "description": "같은 지역구", "level": 1},
                    {"name": "서지영", "type": "정책_연결", "strength": 0.5, "description": "유사 정책", "level": 1},
                    {"name": "권영세", "type": "시간_연결", "strength": 0.4, "description": "동시기 활동", "level": 1},
                    # 2단계 연결
                    {"name": "김태호", "type": "정치적_연결", "strength": 0.3, "description": "김영배와 연결", "level": 2, "parent": "김영배"},
                    {"name": "박민수", "type": "위원회_연결", "strength": 0.3, "description": "박수현과 연결", "level": 2, "parent": "박수현"},
                    {"name": "이수진", "type": "입법_연결", "strength": 0.2, "description": "이재정과 연결", "level": 2, "parent": "이재정"},
                    # 3단계 연결
                    {"name": "최영희", "type": "정치적_연결", "strength": 0.1, "description": "김태호와 연결", "level": 3, "parent": "김태호"},
                    {"name": "정수진", "type": "위원회_연결", "strength": 0.1, "description": "박민수와 연결", "level": 3, "parent": "박민수"}
                ]
            },
            "김주영": {
                "name": "김주영",
                "party": "국민의힘",
                "district": "경기 김포시갑",
                "committee": "과학기술정보방송통신위원회",
                "connectivity_score": 78.2,
                "connections": [
                    {"name": "한병도", "type": "정치적_연결", "strength": 0.9, "description": "같은 정당", "level": 1},
                    {"name": "김선교", "type": "위원회_연결", "strength": 0.8, "description": "같은 위원회", "level": 1},
                    {"name": "김승수", "type": "입법_연결", "strength": 0.7, "description": "공동발의", "level": 1},
                    {"name": "정부수", "type": "지역_연결", "strength": 0.6, "description": "같은 지역구", "level": 1},
                    {"name": "강대식", "type": "정책_연결", "strength": 0.5, "description": "유사 정책", "level": 1},
                    # 2단계 연결
                    {"name": "이민호", "type": "정치적_연결", "strength": 0.3, "description": "한병도와 연결", "level": 2, "parent": "한병도"},
                    {"name": "박지영", "type": "위원회_연결", "strength": 0.3, "description": "김선교와 연결", "level": 2, "parent": "김선교"},
                    # 3단계 연결
                    {"name": "최수진", "type": "정치적_연결", "strength": 0.1, "description": "이민호와 연결", "level": 3, "parent": "이민호"}
                ]
            },
            "신장식": {
                "name": "신장식",
                "party": "더불어민주당",
                "district": "비례대표",
                "committee": "환경노동위원회",
                "connectivity_score": 72.8,
                "connections": [
                    {"name": "이수진", "type": "정치적_연결", "strength": 0.9, "description": "같은 정당", "level": 1},
                    {"name": "박민수", "type": "위원회_연결", "strength": 0.8, "description": "같은 위원회", "level": 1},
                    {"name": "최영희", "type": "입법_연결", "strength": 0.7, "description": "공동발의", "level": 1},
                    {"name": "김태호", "type": "정책_연결", "strength": 0.6, "description": "유사 정책", "level": 1},
                    {"name": "정수진", "type": "시간_연결", "strength": 0.5, "description": "동시기 활동", "level": 1},
                    # 2단계 연결
                    {"name": "박지영", "type": "정치적_연결", "strength": 0.3, "description": "이수진과 연결", "level": 2, "parent": "이수진"},
                    {"name": "이민호", "type": "위원회_연결", "strength": 0.3, "description": "박민수와 연결", "level": 2, "parent": "박민수"},
                    # 3단계 연결
                    {"name": "최수진", "type": "정치적_연결", "strength": 0.1, "description": "박지영과 연결", "level": 3, "parent": "박지영"}
                ]
            }
        }
        
        # 출력 디렉토리 생성
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/widgets", exist_ok=True)
        os.makedirs(f"{self.output_dir}/pages", exist_ok=True)
    
    def create_family_tree_widget(self, politician_name: str) -> str:
        """맥 패밀리트리 스타일 위젯 생성"""
        try:
            if politician_name not in self.politicians:
                logger.error(f"정치인 데이터를 찾을 수 없습니다: {politician_name}")
                return None
            
            politician = self.politicians[politician_name]
            
            # Pyvis 네트워크 생성
            net = Network(
                height="600px", 
                width="100%", 
                bgcolor="#f8f9fa",
                font_color="#2c3e50",
                directed=False
            )
            
            # 맥 패밀리트리 스타일 옵션 설정
            net.set_options("""
            {
                "physics": {
                    "enabled": true,
                    "stabilization": {"iterations": 200},
                    "hierarchicalRepulsion": {
                        "centralGravity": 0.0,
                        "springLength": 200,
                        "springConstant": 0.01,
                        "nodeDistance": 300,
                        "damping": 0.09
                    }
                },
                "interaction": {
                    "hover": true,
                    "tooltipDelay": 300,
                    "hideEdgesOnDrag": false,
                    "dragNodes": true,
                    "dragView": true,
                    "zoomView": true
                },
                "nodes": {
                    "font": {
                        "size": 14,
                        "face": "SF Pro Display, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                        "color": "#2c3e50"
                    },
                    "scaling": {
                        "min": 20,
                        "max": 50
                    },
                    "borderWidth": 2,
                    "borderWidthSelected": 4
                },
                "edges": {
                    "width": 3,
                    "smooth": {
                        "type": "continuous",
                        "roundness": 0.5
                    },
                    "color": {
                        "color": "#bdc3c7",
                        "highlight": "#3498db",
                        "hover": "#2980b9"
                    }
                },
                "layout": {
                    "hierarchical": {
                        "enabled": true,
                        "levelSeparation": 200,
                        "nodeSpacing": 150,
                        "treeSpacing": 200,
                        "blockShifting": true,
                        "edgeMinimization": true,
                        "parentCentralization": true,
                        "direction": "UD",
                        "sortMethod": "directed"
                    }
                }
            }
            """)
            
            # 중심 노드 (개인 정치인) - 맥 스타일
            net.add_node(
                politician["name"],
                label=f"""
                <div style="text-align: center; font-family: 'SF Pro Display', -apple-system, sans-serif;">
                    <div style="font-size: 18px; font-weight: 600; color: #2c3e50; margin-bottom: 5px;">
                        {politician["name"]}
                    </div>
                    <div style="font-size: 12px; color: #7f8c8d; margin-bottom: 3px;">
                        {politician["party"]}
                    </div>
                    <div style="font-size: 11px; color: #95a5a6;">
                        {politician["district"]}
                    </div>
                    <div style="font-size: 11px; color: #95a5a6;">
                        {politician["committee"]}
                    </div>
                    <div style="font-size: 13px; font-weight: 600; color: #e74c3c; margin-top: 5px;">
                        {politician["connectivity_score"]}점
                    </div>
                </div>
                """,
                size=40,
                color="#ecf0f1",
                border="#3498db",
                title=f"""
                <div style="font-family: 'SF Pro Display', -apple-system, sans-serif; font-size: 13px; line-height: 1.4;">
                    <div style="font-weight: 600; color: #2c3e50; margin-bottom: 8px; font-size: 16px;">
                        {politician["name"]}
                    </div>
                    <div style="color: #7f8c8d; margin-bottom: 4px;">
                        <strong>정당:</strong> {politician["party"]}
                    </div>
                    <div style="color: #7f8c8d; margin-bottom: 4px;">
                        <strong>지역구:</strong> {politician["district"]}
                    </div>
                    <div style="color: #7f8c8d; margin-bottom: 4px;">
                        <strong>위원회:</strong> {politician["committee"]}
                    </div>
                    <div style="color: #e74c3c; font-weight: 600; margin-top: 8px; font-size: 14px;">
                        연결성 점수: {politician["connectivity_score"]}점
                    </div>
                </div>
                """,
                shape="box",
                margin=10
            )
            
            # 연결된 노드들 추가 (레벨별로)
            level_1_nodes = [conn for conn in politician["connections"] if conn["level"] == 1]
            level_2_nodes = [conn for conn in politician["connections"] if conn["level"] == 2]
            level_3_nodes = [conn for conn in politician["connections"] if conn["level"] == 3]
            
            # 1단계 연결 노드들
            for conn in level_1_nodes:
                color = self.connection_colors.get(conn["type"], "#bdc3c7")
                size = max(25, int(conn["strength"] * 35))
                
                net.add_node(
                    conn["name"],
                    label=f"""
                    <div style="text-align: center; font-family: 'SF Pro Display', -apple-system, sans-serif;">
                        <div style="font-size: 14px; font-weight: 500; color: #2c3e50; margin-bottom: 3px;">
                            {conn["name"]}
                        </div>
                        <div style="font-size: 10px; color: #7f8c8d;">
                            {conn["description"]}
                        </div>
                        <div style="font-size: 11px; font-weight: 500; color: {color}; margin-top: 2px;">
                            {conn["strength"]:.1f}
                        </div>
                    </div>
                    """,
                    size=size,
                    color="#ffffff",
                    border=color,
                    title=f"""
                    <div style="font-family: 'SF Pro Display', -apple-system, sans-serif; font-size: 12px; line-height: 1.3;">
                        <div style="font-weight: 600; color: #2c3e50; margin-bottom: 6px;">
                            {conn["name"]}
                        </div>
                        <div style="color: #7f8c8d; margin-bottom: 3px;">
                            <strong>연결 유형:</strong> {conn["type"]}
                        </div>
                        <div style="color: #7f8c8d; margin-bottom: 3px;">
                            <strong>설명:</strong> {conn["description"]}
                        </div>
                        <div style="color: {color}; font-weight: 600; margin-top: 6px;">
                            연결 강도: {conn["strength"]:.1f}
                        </div>
                    </div>
                    """,
                    shape="box",
                    margin=8
                )
                
                # 중심 노드와 연결
                edge_width = max(2, int(conn["strength"] * 6))
                net.add_edge(
                    politician["name"],
                    conn["name"],
                    width=edge_width,
                    color=color,
                    title=f"{conn['description']} (강도: {conn['strength']:.1f})"
                )
            
            # 2단계 연결 노드들
            for conn in level_2_nodes:
                color = self.connection_colors.get(conn["type"], "#bdc3c7")
                size = max(20, int(conn["strength"] * 30))
                
                net.add_node(
                    conn["name"],
                    label=f"""
                    <div style="text-align: center; font-family: 'SF Pro Display', -apple-system, sans-serif;">
                        <div style="font-size: 12px; font-weight: 500; color: #2c3e50; margin-bottom: 2px;">
                            {conn["name"]}
                        </div>
                        <div style="font-size: 9px; color: #7f8c8d;">
                            {conn["description"]}
                        </div>
                        <div style="font-size: 10px; font-weight: 500; color: {color}; margin-top: 1px;">
                            {conn["strength"]:.1f}
                        </div>
                    </div>
                    """,
                    size=size,
                    color="#f8f9fa",
                    border=color,
                    title=f"""
                    <div style="font-family: 'SF Pro Display', -apple-system, sans-serif; font-size: 11px; line-height: 1.3;">
                        <div style="font-weight: 600; color: #2c3e50; margin-bottom: 4px;">
                            {conn["name"]}
                        </div>
                        <div style="color: #7f8c8d; margin-bottom: 2px;">
                            <strong>연결 유형:</strong> {conn["type"]}
                        </div>
                        <div style="color: #7f8c8d; margin-bottom: 2px;">
                            <strong>설명:</strong> {conn["description"]}
                        </div>
                        <div style="color: {color}; font-weight: 600; margin-top: 4px;">
                            연결 강도: {conn["strength"]:.1f}
                        </div>
                    </div>
                    """,
                    shape="box",
                    margin=6
                )
                
                # 부모 노드와 연결
                edge_width = max(1, int(conn["strength"] * 4))
                net.add_edge(
                    conn["parent"],
                    conn["name"],
                    width=edge_width,
                    color=color,
                    title=f"{conn['description']} (강도: {conn['strength']:.1f})"
                )
            
            # 3단계 연결 노드들
            for conn in level_3_nodes:
                color = self.connection_colors.get(conn["type"], "#bdc3c7")
                size = max(15, int(conn["strength"] * 25))
                
                net.add_node(
                    conn["name"],
                    label=f"""
                    <div style="text-align: center; font-family: 'SF Pro Display', -apple-system, sans-serif;">
                        <div style="font-size: 11px; font-weight: 500; color: #2c3e50; margin-bottom: 1px;">
                            {conn["name"]}
                        </div>
                        <div style="font-size: 8px; color: #7f8c8d;">
                            {conn["description"]}
                        </div>
                        <div style="font-size: 9px; font-weight: 500; color: {color}; margin-top: 1px;">
                            {conn["strength"]:.1f}
                        </div>
                    </div>
                    """,
                    size=size,
                    color="#f8f9fa",
                    border=color,
                    title=f"""
                    <div style="font-family: 'SF Pro Display', -apple-system, sans-serif; font-size: 10px; line-height: 1.3;">
                        <div style="font-weight: 600; color: #2c3e50; margin-bottom: 3px;">
                            {conn["name"]}
                        </div>
                        <div style="color: #7f8c8d; margin-bottom: 2px;">
                            <strong>연결 유형:</strong> {conn["type"]}
                        </div>
                        <div style="color: #7f8c8d; margin-bottom: 2px;">
                            <strong>설명:</strong> {conn["description"]}
                        </div>
                        <div style="color: {color}; font-weight: 600; margin-top: 3px;">
                            연결 강도: {conn["strength"]:.1f}
                        </div>
                    </div>
                    """,
                    shape="box",
                    margin=4
                )
                
                # 부모 노드와 연결
                edge_width = max(1, int(conn["strength"] * 3))
                net.add_edge(
                    conn["parent"],
                    conn["name"],
                    width=edge_width,
                    color=color,
                    title=f"{conn['description']} (강도: {conn['strength']:.1f})"
                )
            
            # HTML 파일로 저장
            filename = f"family_tree_{politician['name']}.html"
            filepath = f"{self.output_dir}/widgets/{filename}"
            net.save_graph(filepath)
            
            logger.info(f"맥 패밀리트리 위젯 생성 완료: {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"맥 패밀리트리 위젯 생성 실패: {e}")
            return None
    
    def create_politician_page(self, politician_name: str) -> str:
        """개별 정치인 페이지 생성 (맥 스타일)"""
        try:
            if politician_name not in self.politicians:
                logger.error(f"정치인 데이터를 찾을 수 없습니다: {politician_name}")
                return None
            
            politician = self.politicians[politician_name]
            
            html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{politician['name']} 연결성 분석 - 맥 패밀리트리 스타일</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 15px;
            font-weight: 600;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header .info {{
            font-size: 1.1em;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        
        .score-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 12px 24px;
            border-radius: 25px;
            margin-top: 15px;
            font-size: 1.1em;
            font-weight: 600;
            backdrop-filter: blur(10px);
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .widget-section {{
            margin-bottom: 40px;
        }}
        
        .widget-section h2 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.8em;
            font-weight: 600;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        
        .widget-container {{
            border: 2px solid #ecf0f1;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            background: #f8f9fa;
        }}
        
        .widget-container iframe {{
            width: 100%;
            height: 600px;
            border: none;
        }}
        
        .connections-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .connection-card {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border-left: 5px solid;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .connection-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }}
        
        .connection-card.입법_연결 {{ border-left-color: #FF6B6B; }}
        .connection-card.위원회_연결 {{ border-left-color: #4ECDC4; }}
        .connection-card.정치적_연결 {{ border-left-color: #45B7D1; }}
        .connection-card.지역_연결 {{ border-left-color: #96CEB4; }}
        .connection-card.정책_연결 {{ border-left-color: #FFEAA7; }}
        .connection-card.시간_연결 {{ border-left-color: #DDA0DD; }}
        
        .connection-name {{
            font-size: 1.3em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .connection-type {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        
        .connection-strength {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .strength-bar {{
            flex: 1;
            height: 8px;
            background: #ecf0f1;
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .strength-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            border-radius: 4px;
            transition: width 0.3s ease;
        }}
        
        .strength-value {{
            font-weight: 600;
            color: #2c3e50;
            min-width: 40px;
        }}
        
        .back-button {{
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(255,255,255,0.9);
            border: none;
            padding: 15px 25px;
            border-radius: 25px;
            font-family: 'SF Pro Display', -apple-system, sans-serif;
            font-size: 1em;
            font-weight: 500;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }}
        
        .back-button:hover {{
            background: white;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.25);
        }}
        
        .level-indicator {{
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
            margin-left: 8px;
        }}
    </style>
</head>
<body>
    <button class="back-button" onclick="history.back()">← 뒤로가기</button>
    
    <div class="container">
        <div class="header">
            <h1>{politician['name']}</h1>
            <div class="info">
                <p>{politician['party']} | {politician['district']}</p>
                <p>{politician['committee']}</p>
            </div>
            <div class="score-badge">
                연결성 점수: {politician['connectivity_score']}점
            </div>
        </div>
        
        <div class="content">
            <div class="widget-section">
                <h2>🌳 맥 패밀리트리 스타일 연결성 시각화</h2>
                <div class="widget-container">
                    <iframe src="widgets/family_tree_{politician['name']}.html"></iframe>
                </div>
            </div>
            
            <div class="widget-section">
                <h2>🔗 연결된 정치인 상세</h2>
                <div class="connections-grid">
"""
            
            # 연결된 정치인 카드들 추가 (레벨별로)
            for conn in politician["connections"]:
                strength_percent = int(conn["strength"] * 100)
                level_text = f"L{conn['level']}" if conn['level'] > 1 else ""
                
                html_content += f"""
                    <div class="connection-card {conn['type']}">
                        <div class="connection-name">
                            {conn['name']}
                            <span class="level-indicator">{level_text}</span>
                        </div>
                        <div class="connection-type">{conn['description']}</div>
                        <div class="connection-strength">
                            <div class="strength-bar">
                                <div class="strength-fill" style="width: {strength_percent}%"></div>
                            </div>
                            <div class="strength-value">{conn['strength']:.1f}</div>
                        </div>
                    </div>
                """
            
            html_content += """
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // 연결 강도 바 애니메이션
        document.addEventListener('DOMContentLoaded', function() {
            const strengthBars = document.querySelectorAll('.strength-fill');
            strengthBars.forEach(bar => {
                const width = bar.style.width;
                bar.style.width = '0%';
                setTimeout(() => {
                    bar.style.width = width;
                }, 500);
            });
        });
    </script>
</body>
</html>
"""
            
            # HTML 파일로 저장
            filename = f"page_{politician['name']}.html"
            filepath = f"{self.output_dir}/pages/{filename}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"정치인 페이지 생성 완료: {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"정치인 페이지 생성 실패: {e}")
            return None
    
    def create_all_widgets(self) -> Dict[str, Any]:
        """모든 정치인 위젯 생성"""
        results = {}
        
        for politician_name in self.politicians.keys():
            logger.info(f"정치인 위젯 생성 중: {politician_name}")
            
            # 패밀리트리 위젯 생성
            widget_file = self.create_family_tree_widget(politician_name)
            
            # 개인 페이지 생성
            page_file = self.create_politician_page(politician_name)
            
            if widget_file and page_file:
                results[politician_name] = {
                    "widget": widget_file,
                    "page": page_file,
                    "status": "success"
                }
        
        return results
    
    def create_index_page(self) -> str:
        """전체 정치인 목록 인덱스 페이지 생성 (맥 스타일)"""
        try:
            html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>정치인 연결성 분석 - 맥 패밀리트리 스타일</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 50px;
        }
        
        .header h1 {
            font-size: 3.5em;
            margin-bottom: 20px;
            font-weight: 600;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.3em;
            opacity: 0.9;
            font-weight: 300;
        }
        
        .politicians-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
        }
        
        .politician-card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
            border: 1px solid #ecf0f1;
        }
        
        .politician-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }
        
        .politician-name {
            font-size: 1.8em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .politician-info {
            color: #7f8c8d;
            margin-bottom: 20px;
            line-height: 1.5;
        }
        
        .politician-info p {
            margin-bottom: 5px;
        }
        
        .score-badge {
            display: inline-block;
            background: linear-gradient(135deg, #3498db, #2ecc71);
            color: white;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: 600;
            margin-bottom: 20px;
        }
        
        .connections-preview {
            margin-top: 20px;
        }
        
        .connections-preview h4 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-weight: 600;
        }
        
        .connection-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .connection-tag {
            background: #ecf0f1;
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 0.9em;
            color: #7f8c8d;
            font-weight: 500;
        }
        
        .view-button {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-family: 'SF Pro Display', -apple-system, sans-serif;
            font-size: 1em;
            font-weight: 500;
            cursor: pointer;
            margin-top: 20px;
            width: 100%;
            transition: all 0.3s ease;
        }
        
        .view-button:hover {
            background: linear-gradient(135deg, #2980b9, #3498db);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌳 정치인 연결성 분석</h1>
            <p>맥 패밀리트리 스타일의 직관적인 네트워크 시각화</p>
        </div>
        
        <div class="politicians-grid">
"""
            
            # 각 정치인 카드 추가
            for politician_name, politician_data in self.politicians.items():
                connection_types = list(set([conn["type"] for conn in politician_data["connections"]]))
                
                html_content += f"""
            <div class="politician-card" onclick="location.href='pages/page_{politician_name}.html'">
                <div class="politician-name">{politician_name}</div>
                <div class="politician-info">
                    <p><strong>정당:</strong> {politician_data['party']}</p>
                    <p><strong>지역구:</strong> {politician_data['district']}</p>
                    <p><strong>위원회:</strong> {politician_data['committee']}</p>
                </div>
                <div class="score-badge">
                    연결성 점수: {politician_data['connectivity_score']}점
                </div>
                <div class="connections-preview">
                    <h4>연결 유형:</h4>
                    <div class="connection-tags">
"""
                
                for conn_type in connection_types:
                    html_content += f'                        <span class="connection-tag">{conn_type}</span>\n'
                
                html_content += f"""
                    </div>
                </div>
                <button class="view-button" onclick="event.stopPropagation(); location.href='pages/page_{politician_name}.html'">
                    패밀리트리 보기
                </button>
            </div>
"""
            
            html_content += """
        </div>
    </div>
</body>
</html>
"""
            
            # HTML 파일로 저장
            filepath = f"{self.output_dir}/index.html"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"인덱스 페이지 생성 완료: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"인덱스 페이지 생성 실패: {e}")
            return None

def main():
    """메인 함수"""
    try:
        # 맥 패밀리트리 시각화 생성기 초기화
        visualizer = MacFamilyTreeVisualizer()
        
        # 모든 정치인 위젯 생성
        logger.info("맥 패밀리트리 스타일 위젯 생성 시작...")
        results = visualizer.create_all_widgets()
        
        # 인덱스 페이지 생성
        logger.info("인덱스 페이지 생성 중...")
        index_file = visualizer.create_index_page()
        
        # 결과 출력
        print("\n🌳 맥 패밀리트리 스타일 연결성 시각화 완성!")
        print(f"📁 출력 디렉토리: {visualizer.output_dir}")
        print(f"📄 인덱스 페이지: {index_file}")
        print("\n📊 생성된 위젯:")
        
        for politician, result in results.items():
            print(f"  - {politician}:")
            print(f"    * 패밀리트리 위젯: {result['widget']}")
            print(f"    * 개인 페이지: {result['page']}")
        
        print(f"\n🌐 웹에서 보기: {visualizer.output_dir}/index.html")
        
    except Exception as e:
        logger.error(f"위젯 생성 실패: {e}")

if __name__ == "__main__":
    main()

