#!/usr/bin/env python3
"""
개인 정치인 중심 위젯 기반 연결성 시각화
각 정치인별로 개별 위젯과 웹 페이지 생성
"""

import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from pyvis.network import Network
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import pandas as pd
import os
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndividualPoliticianWidgets:
    """개인 정치인 중심 위젯 생성 클래스"""
    
    def __init__(self, output_dir: str = "politician_widgets"):
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
                    {"name": "김영배", "type": "정치적_연결", "strength": 0.9, "description": "같은 정당"},
                    {"name": "박수현", "type": "위원회_연결", "strength": 0.8, "description": "같은 위원회"},
                    {"name": "이재정", "type": "입법_연결", "strength": 0.7, "description": "공동발의"},
                    {"name": "최민호", "type": "지역_연결", "strength": 0.6, "description": "같은 지역구"},
                    {"name": "서지영", "type": "정책_연결", "strength": 0.5, "description": "유사 정책"},
                    {"name": "권영세", "type": "시간_연결", "strength": 0.4, "description": "동시기 활동"}
                ]
            },
            "김주영": {
                "name": "김주영",
                "party": "국민의힘",
                "district": "경기 김포시갑",
                "committee": "과학기술정보방송통신위원회",
                "connectivity_score": 78.2,
                "connections": [
                    {"name": "한병도", "type": "정치적_연결", "strength": 0.9, "description": "같은 정당"},
                    {"name": "김선교", "type": "위원회_연결", "strength": 0.8, "description": "같은 위원회"},
                    {"name": "김승수", "type": "입법_연결", "strength": 0.7, "description": "공동발의"},
                    {"name": "정부수", "type": "지역_연결", "strength": 0.6, "description": "같은 지역구"},
                    {"name": "강대식", "type": "정책_연결", "strength": 0.5, "description": "유사 정책"}
                ]
            },
            "신장식": {
                "name": "신장식",
                "party": "더불어민주당",
                "district": "비례대표",
                "committee": "환경노동위원회",
                "connectivity_score": 72.8,
                "connections": [
                    {"name": "이수진", "type": "정치적_연결", "strength": 0.9, "description": "같은 정당"},
                    {"name": "박민수", "type": "위원회_연결", "strength": 0.8, "description": "같은 위원회"},
                    {"name": "최영희", "type": "입법_연결", "strength": 0.7, "description": "공동발의"},
                    {"name": "김태호", "type": "정책_연결", "strength": 0.6, "description": "유사 정책"},
                    {"name": "정수진", "type": "시간_연결", "strength": 0.5, "description": "동시기 활동"}
                ]
            }
        }
        
        # 출력 디렉토리 생성
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/widgets", exist_ok=True)
        os.makedirs(f"{self.output_dir}/pages", exist_ok=True)
    
    def create_politician_widget(self, politician_name: str) -> Dict[str, str]:
        """개별 정치인 위젯 생성"""
        try:
            if politician_name not in self.politicians:
                logger.error(f"정치인 데이터를 찾을 수 없습니다: {politician_name}")
                return None
            
            politician = self.politicians[politician_name]
            
            # 1. Pyvis 대화형 위젯 생성
            pyvis_file = self._create_pyvis_widget(politician)
            
            # 2. Plotly 3D 위젯 생성
            plotly_file = self._create_plotly_widget(politician)
            
            # 3. 개인 페이지 생성
            page_file = self._create_politician_page(politician)
            
            return {
                "politician": politician_name,
                "pyvis_widget": pyvis_file,
                "plotly_widget": plotly_file,
                "individual_page": page_file,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"정치인 위젯 생성 실패 ({politician_name}): {e}")
            return None
    
    def _create_pyvis_widget(self, politician: Dict) -> str:
        """Pyvis 대화형 위젯 생성"""
        try:
            net = Network(
                height="500px", 
                width="100%", 
                bgcolor="#ffffff",
                font_color="#333333",
                directed=False
            )
            
            # 네트워크 옵션 설정
            net.set_options("""
            {
                "physics": {
                    "enabled": true,
                    "stabilization": {"iterations": 100},
                    "barnesHut": {
                        "gravitationalConstant": -2000,
                        "centralGravity": 0.1,
                        "springLength": 150,
                        "springConstant": 0.05,
                        "damping": 0.09
                    }
                },
                "interaction": {
                    "hover": true,
                    "tooltipDelay": 200,
                    "hideEdgesOnDrag": false
                },
                "nodes": {
                    "font": {
                        "size": 16,
                        "face": "Noto Sans KR, sans-serif"
                    },
                    "scaling": {
                        "min": 15,
                        "max": 40
                    }
                },
                "edges": {
                    "width": 3,
                    "smooth": {
                        "type": "continuous"
                    }
                }
            }
            """)
            
            # 중심 노드 (개인 정치인)
            net.add_node(
                politician["name"],
                label=politician["name"],
                size=35,
                color="#FFD700",
                title=f"""
                <div style="font-family: 'Noto Sans KR', sans-serif; font-size: 14px; text-align: center;">
                    <h2 style="margin: 0; color: #333;">{politician["name"]}</h2>
                    <p style="margin: 5px 0; color: #666;">{politician["party"]}</p>
                    <p style="margin: 5px 0; color: #666;">{politician["district"]}</p>
                    <p style="margin: 5px 0; color: #666;">{politician["committee"]}</p>
                    <hr style="margin: 10px 0; border: 1px solid #eee;">
                    <p style="margin: 5px 0; font-weight: bold; color: #FF6B6B;">
                        연결성 점수: {politician["connectivity_score"]}점
                    </p>
                </div>
                """,
                shape="star"
            )
            
            # 연결된 정치인들 추가
            for i, conn in enumerate(politician["connections"]):
                color = self.connection_colors.get(conn["type"], "#CCCCCC")
                size = max(20, int(conn["strength"] * 30))
                
                net.add_node(
                    conn["name"],
                    label=conn["name"],
                    size=size,
                    color=color,
                    title=f"""
                    <div style="font-family: 'Noto Sans KR', sans-serif; font-size: 12px;">
                        <h4 style="margin: 0; color: #333;">{conn["name"]}</h4>
                        <p style="margin: 5px 0; color: #666;">{conn["description"]}</p>
                        <p style="margin: 5px 0; font-weight: bold; color: {color};">
                            연결 강도: {conn["strength"]:.1f}
                        </p>
                    </div>
                    """,
                    shape="dot"
                )
                
                # 연결선 추가
                edge_width = max(2, int(conn["strength"] * 8))
                net.add_edge(
                    politician["name"],
                    conn["name"],
                    width=edge_width,
                    color=color,
                    title=f"{conn['description']} (강도: {conn['strength']:.1f})"
                )
            
            # HTML 파일로 저장
            filename = f"widget_{politician['name']}_pyvis.html"
            filepath = f"{self.output_dir}/widgets/{filename}"
            net.save_graph(filepath)
            
            logger.info(f"Pyvis 위젯 생성 완료: {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"Pyvis 위젯 생성 실패: {e}")
            return None
    
    def _create_plotly_widget(self, politician: Dict) -> str:
        """Plotly 3D 위젯 생성"""
        try:
            # 노드 데이터 생성
            nodes = []
            
            # 중심 노드
            nodes.append({
                "name": politician["name"],
                "x": 0, "y": 0, "z": 0,
                "size": 30, "color": "#FFD700",
                "type": "center"
            })
            
            # 연결된 노드들 (원형 배치)
            import math
            for i, conn in enumerate(politician["connections"]):
                angle = (2 * math.pi * i) / len(politician["connections"])
                radius = 2.0
                
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                z = 0.5 * math.sin(angle * 2)  # 3D 효과
                
                color = self.connection_colors.get(conn["type"], "#CCCCCC")
                size = max(15, int(conn["strength"] * 25))
                
                nodes.append({
                    "name": conn["name"],
                    "x": x, "y": y, "z": z,
                    "size": size, "color": color,
                    "type": conn["type"],
                    "strength": conn["strength"]
                })
            
            # 3D 산점도 생성
            fig = go.Figure()
            
            # 노드 그리기
            node_x = [node["x"] for node in nodes]
            node_y = [node["y"] for node in nodes]
            node_z = [node["z"] for node in nodes]
            node_sizes = [node["size"] for node in nodes]
            node_colors = [node["color"] for node in nodes]
            node_names = [node["name"] for node in nodes]
            
            fig.add_trace(go.Scatter3d(
                x=node_x,
                y=node_y,
                z=node_z,
                mode='markers+text',
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    opacity=0.8,
                    line=dict(width=2, color='white')
                ),
                text=node_names,
                textposition="top center",
                hovertemplate="<b>%{text}</b><br>" +
                            "위치: (%{x:.1f}, %{y:.1f}, %{z:.1f})<br>" +
                            "크기: %{marker.size}<extra></extra>",
                name="정치인"
            ))
            
            # 연결선 추가
            center_node = nodes[0]
            for node in nodes[1:]:
                fig.add_trace(go.Scatter3d(
                    x=[center_node["x"], node["x"]],
                    y=[center_node["y"], node["y"]],
                    z=[center_node["z"], node["z"]],
                    mode='lines',
                    line=dict(
                        color=node["color"],
                        width=max(2, int(node["strength"] * 6))
                    ),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # 레이아웃 설정
            fig.update_layout(
                title=dict(
                    text=f"🔗 {politician['name']} 연결성 네트워크 (3D)",
                    font=dict(size=18, family="Noto Sans KR"),
                    x=0.5
                ),
                scene=dict(
                    xaxis=dict(showbackground=False, showticklabels=False, title=""),
                    yaxis=dict(showbackground=False, showticklabels=False, title=""),
                    zaxis=dict(showbackground=False, showticklabels=False, title=""),
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                font=dict(family="Noto Sans KR", size=12),
                showlegend=False,
                margin=dict(l=0, r=0, t=50, b=0),
                height=500
            )
            
            # HTML 파일로 저장
            filename = f"widget_{politician['name']}_plotly.html"
            filepath = f"{self.output_dir}/widgets/{filename}"
            fig.write_html(filepath)
            
            logger.info(f"Plotly 위젯 생성 완료: {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"Plotly 위젯 생성 실패: {e}")
            return None
    
    def _create_politician_page(self, politician: Dict) -> str:
        """개별 정치인 페이지 생성"""
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{politician['name']} 연결성 분석</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
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
            background: linear-gradient(135deg, #FF6B6B, #4ECDC4);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header .info {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .score-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 25px;
            margin-top: 15px;
            font-size: 1.1em;
            font-weight: bold;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .widget-section {{
            margin-bottom: 40px;
        }}
        
        .widget-section h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #4ECDC4;
            padding-bottom: 10px;
        }}
        
        .widget-container {{
            border: 2px solid #f0f0f0;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .widget-container iframe {{
            width: 100%;
            height: 500px;
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
            transition: transform 0.3s ease;
        }}
        
        .connection-card:hover {{
            transform: translateY(-5px);
        }}
        
        .connection-card.입법_연결 {{ border-left-color: #FF6B6B; }}
        .connection-card.위원회_연결 {{ border-left-color: #4ECDC4; }}
        .connection-card.정치적_연결 {{ border-left-color: #45B7D1; }}
        .connection-card.지역_연결 {{ border-left-color: #96CEB4; }}
        .connection-card.정책_연결 {{ border-left-color: #FFEAA7; }}
        .connection-card.시간_연결 {{ border-left-color: #DDA0DD; }}
        
        .connection-name {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .connection-type {{
            color: #666;
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
            background: #f0f0f0;
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .strength-fill {{
            height: 100%;
            background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
            border-radius: 4px;
            transition: width 0.3s ease;
        }}
        
        .strength-value {{
            font-weight: bold;
            color: #333;
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
            font-family: 'Noto Sans KR', sans-serif;
            font-size: 1em;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }}
        
        .back-button:hover {{
            background: white;
            transform: translateY(-2px);
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
                <h2>🌐 대화형 네트워크 시각화</h2>
                <div class="widget-container">
                    <iframe src="widgets/widget_{politician['name']}_pyvis.html"></iframe>
                </div>
            </div>
            
            <div class="widget-section">
                <h2>🎯 3D 네트워크 시각화</h2>
                <div class="widget-container">
                    <iframe src="widgets/widget_{politician['name']}_plotly.html"></iframe>
                </div>
            </div>
            
            <div class="widget-section">
                <h2>🔗 연결된 정치인 상세</h2>
                <div class="connections-grid">
"""
            
            # 연결된 정치인 카드들 추가
            for conn in politician["connections"]:
                strength_percent = int(conn["strength"] * 100)
                html_content += f"""
                    <div class="connection-card {conn['type']}">
                        <div class="connection-name">{conn['name']}</div>
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
    
    def create_all_politician_widgets(self) -> Dict[str, Any]:
        """모든 정치인 위젯 생성"""
        results = {}
        
        for politician_name in self.politicians.keys():
            logger.info(f"정치인 위젯 생성 중: {politician_name}")
            result = self.create_politician_widget(politician_name)
            if result:
                results[politician_name] = result
        
        return results
    
    def create_index_page(self) -> str:
        """전체 정치인 목록 인덱스 페이지 생성"""
        try:
            html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>정치인 연결성 분석 시스템</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
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
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
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
        }
        
        .politician-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }
        
        .politician-name {
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
        }
        
        .politician-info {
            color: #666;
            margin-bottom: 20px;
        }
        
        .politician-info p {
            margin-bottom: 5px;
        }
        
        .score-badge {
            display: inline-block;
            background: linear-gradient(135deg, #FF6B6B, #4ECDC4);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        
        .connections-preview {
            margin-top: 20px;
        }
        
        .connections-preview h4 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .connection-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .connection-tag {
            background: #f0f0f0;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.9em;
            color: #666;
        }
        
        .view-button {
            background: linear-gradient(135deg, #4ECDC4, #45B7D1);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            font-family: 'Noto Sans KR', sans-serif;
            font-size: 1em;
            cursor: pointer;
            margin-top: 20px;
            width: 100%;
            transition: all 0.3s ease;
        }
        
        .view-button:hover {
            background: linear-gradient(135deg, #45B7D1, #4ECDC4);
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔗 정치인 연결성 분석 시스템</h1>
            <p>개인 정치인 중심의 고급 네트워크 시각화</p>
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
                    상세 분석 보기
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
        # 위젯 생성기 초기화
        widget_generator = IndividualPoliticianWidgets()
        
        # 모든 정치인 위젯 생성
        logger.info("모든 정치인 위젯 생성 시작...")
        results = widget_generator.create_all_politician_widgets()
        
        # 인덱스 페이지 생성
        logger.info("인덱스 페이지 생성 중...")
        index_file = widget_generator.create_index_page()
        
        # 결과 출력
        print("\n🎯 개인 정치인 중심 위젯 생성 완료!")
        print(f"📁 출력 디렉토리: {widget_generator.output_dir}")
        print(f"📄 인덱스 페이지: {index_file}")
        print("\n📊 생성된 위젯:")
        
        for politician, result in results.items():
            print(f"  - {politician}:")
            print(f"    * Pyvis 위젯: {result['pyvis_widget']}")
            print(f"    * Plotly 위젯: {result['plotly_widget']}")
            print(f"    * 개인 페이지: {result['individual_page']}")
        
        print(f"\n🌐 웹에서 보기: {widget_generator.output_dir}/index.html")
        
    except Exception as e:
        logger.error(f"위젯 생성 실패: {e}")

if __name__ == "__main__":
    main()
