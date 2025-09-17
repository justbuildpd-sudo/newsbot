#!/usr/bin/env python3
"""
고급 네트워크 시각화 시스템
Pyvis, Plotly, Dash를 활용한 세련된 연결성 시각화
"""

import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from pyvis.network import Network
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import networkx as nx
import pandas as pd

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedNetworkVisualizer:
    """고급 네트워크 시각화 클래스"""
    
    def __init__(self, db_path: str = "basic_connectivity.db"):
        self.db_path = db_path
        self.connection_colors = {
            "입법_연결": "#FF6B6B",  # 공동발의 (빨간색)
            "위원회_연결": "#4ECDC4", # 같은 위원회 (청록색)
            "정치적_연결": "#45B7D1", # 같은 정당 (파란색)
            "지역_연결": "#96CEB4",  # 같은 지역구 (연두색)
            "정책_연결": "#FFEAA7",  # 유사 정책 (노란색)
            "시간_연결": "#DDA0DD",  # 동시기 활동 (보라색)
        }
        
        # 한글 폰트 설정
        self.korean_fonts = [
            "Noto Sans KR", "Malgun Gothic", "AppleGothic", 
            "NanumGothic", "NanumBarunGothic", "맑은 고딕", 
            "나눔고딕", "나눔바른고딕", "Arial Unicode MS"
        ]
        
    def get_korean_font(self) -> str:
        """사용 가능한 한글 폰트 반환"""
        import matplotlib.font_manager as fm
        
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        
        for font in self.korean_fonts:
            if font in available_fonts:
                logger.info(f"한글 폰트 사용: {font}")
                return font
        
        logger.warning("한글 폰트를 찾을 수 없습니다. 기본 폰트 사용")
        return "Arial"
    
    def create_pyvis_network(self, politician_name: str, max_levels: int = 3) -> str:
        """Pyvis를 사용한 대화형 네트워크 시각화"""
        try:
            # 데이터베이스에서 연결성 데이터 로드
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 정치인 기본 정보 조회
            cursor.execute('''
                SELECT politician_name, connectivity_score, total_connections,
                       legislative_connections, committee_connections, political_connections
                FROM politician_connectivity 
                WHERE politician_name = ?
            ''', (politician_name,))
            
            politician_data = cursor.fetchone()
            if not politician_data:
                logger.error(f"정치인 데이터를 찾을 수 없습니다: {politician_name}")
                return None
            
            # 네트워크 객체 생성
            net = Network(
                height="600px", 
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
                        "springLength": 200,
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
                        "size": 14,
                        "face": "Noto Sans KR"
                    },
                    "scaling": {
                        "min": 10,
                        "max": 50
                    }
                },
                "edges": {
                    "width": 2,
                    "smooth": {
                        "type": "continuous"
                    }
                }
            }
            """)
            
            # 중심 노드 추가
            net.add_node(
                politician_name,
                label=politician_name,
                size=30,
                color="#FFD700",
                title=f"""
                <div style="font-family: 'Noto Sans KR', sans-serif; font-size: 14px;">
                    <h3>{politician_name}</h3>
                    <p><strong>연결성 점수:</strong> {politician_data[1]:.1f}점</p>
                    <p><strong>총 연결 수:</strong> {politician_data[2]}개</p>
                    <p><strong>입법 연결:</strong> {politician_data[3]}개</p>
                    <p><strong>위원회 연결:</strong> {politician_data[4]}개</p>
                    <p><strong>정치적 연결:</strong> {politician_data[5]}개</p>
                </div>
                """,
                shape="star"
            )
            
            # 연결된 정치인들 추가 (샘플 데이터)
            sample_connections = [
                ("권영세의원 등 10인", "위원회_연결", 0.9, 25),
                ("한병도의원 등 10인", "정치적_연결", 0.8, 22),
                ("김선교의원 등 10인", "정치적_연결", 0.8, 22),
                ("김승수의원 등 11인", "정치적_연결", 0.8, 22),
                ("박수현의원 등 8인", "지역_연결", 0.7, 20),
                ("이재정의원 등 9인", "정책_연결", 0.6, 18),
                ("정부수의원 등 7인", "시간_연결", 0.5, 16),
                ("최민호의원 등 6인", "입법_연결", 0.4, 14),
                ("서지영의원 등 5인", "위원회_연결", 0.3, 12),
                ("김영배의원 등 4인", "정치적_연결", 0.2, 10)
            ]
            
            for name, conn_type, strength, size in sample_connections:
                color = self.connection_colors.get(conn_type, "#CCCCCC")
                
                net.add_node(
                    name,
                    label=name,
                    size=size,
                    color=color,
                    title=f"""
                    <div style="font-family: 'Noto Sans KR', sans-serif; font-size: 12px;">
                        <h4>{name}</h4>
                        <p><strong>연결 유형:</strong> {conn_type}</p>
                        <p><strong>연결 강도:</strong> {strength:.1f}</p>
                    </div>
                    """,
                    shape="dot"
                )
                
                # 연결선 추가
                edge_width = max(1, int(strength * 8))
                net.add_edge(
                    politician_name,
                    name,
                    width=edge_width,
                    color=color,
                    title=f"연결 강도: {strength:.1f}"
                )
            
            # HTML 파일로 저장
            output_file = f"network_{politician_name.replace(' ', '_')}.html"
            net.save_graph(output_file)
            
            conn.close()
            logger.info(f"Pyvis 네트워크 시각화 완료: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Pyvis 네트워크 시각화 실패: {e}")
            return None
    
    def create_plotly_network(self, politician_name: str) -> go.Figure:
        """Plotly를 사용한 3D 네트워크 시각화"""
        try:
            # 샘플 데이터 생성
            nodes = [
                {"name": politician_name, "x": 0, "y": 0, "z": 0, "size": 30, "color": "#FFD700", "type": "center"},
                {"name": "권영세의원 등 10인", "x": 2, "y": 0, "z": 0, "size": 25, "color": "#4ECDC4", "type": "위원회"},
                {"name": "한병도의원 등 10인", "x": -2, "y": 0, "z": 0, "size": 25, "color": "#45B7D1", "type": "정치적"},
                {"name": "김선교의원 등 10인", "x": 0, "y": 2, "z": 0, "size": 25, "color": "#45B7D1", "type": "정치적"},
                {"name": "김승수의원 등 11인", "x": 0, "y": -2, "z": 0, "size": 25, "color": "#45B7D1", "type": "정치적"},
                {"name": "박수현의원 등 8인", "x": 1.5, "y": 1.5, "z": 1, "size": 20, "color": "#96CEB4", "type": "지역"},
                {"name": "이재정의원 등 9인", "x": -1.5, "y": 1.5, "z": 1, "size": 20, "color": "#FFEAA7", "type": "정책"},
                {"name": "정부수의원 등 7인", "x": 1.5, "y": -1.5, "z": 1, "size": 18, "color": "#DDA0DD", "type": "시간"},
                {"name": "최민호의원 등 6인", "x": -1.5, "y": -1.5, "z": 1, "size": 16, "color": "#FF6B6B", "type": "입법"},
                {"name": "서지영의원 등 5인", "x": 3, "y": 0, "z": 2, "size": 14, "color": "#4ECDC4", "type": "위원회"},
                {"name": "김영배의원 등 4인", "x": -3, "y": 0, "z": 2, "size": 12, "color": "#45B7D1", "type": "정치적"}
            ]
            
            # 노드 데이터 추출
            node_x = [node["x"] for node in nodes]
            node_y = [node["y"] for node in nodes]
            node_z = [node["z"] for node in nodes]
            node_sizes = [node["size"] for node in nodes]
            node_colors = [node["color"] for node in nodes]
            node_names = [node["name"] for node in nodes]
            node_types = [node["type"] for node in nodes]
            
            # 3D 산점도 생성
            fig = go.Figure(data=go.Scatter3d(
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
                        width=3
                    ),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # 레이아웃 설정
            fig.update_layout(
                title=dict(
                    text=f"🔗 {politician_name} 연결성 네트워크 (3D)",
                    font=dict(size=20, family="Noto Sans KR"),
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
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02
                ),
                margin=dict(l=0, r=0, t=50, b=0)
            )
            
            # 범례 추가
            legend_traces = []
            for conn_type, color in self.connection_colors.items():
                legend_traces.append(go.Scatter3d(
                    x=[None], y=[None], z=[None],
                    mode='markers',
                    marker=dict(size=10, color=color),
                    name=conn_type,
                    showlegend=True
                ))
            
            for trace in legend_traces:
                fig.add_trace(trace)
            
            logger.info(f"Plotly 3D 네트워크 시각화 완료: {politician_name}")
            return fig
            
        except Exception as e:
            logger.error(f"Plotly 네트워크 시각화 실패: {e}")
            return None
    
    def create_dash_app(self) -> dash.Dash:
        """Dash를 사용한 대화형 웹 애플리케이션"""
        app = dash.Dash(__name__)
        
        # 레이아웃 설정
        app.layout = html.Div([
            html.H1("🔗 정치인 연결성 분석 시스템", 
                   style={'textAlign': 'center', 'fontFamily': 'Noto Sans KR', 'marginBottom': '30px'}),
            
            html.Div([
                html.Label("정치인 선택:", style={'fontFamily': 'Noto Sans KR', 'fontSize': '16px'}),
                dcc.Dropdown(
                    id='politician-dropdown',
                    options=[
                        {'label': '강대식의원 등 12인', 'value': '강대식의원 등 12인'},
                        {'label': '권영세의원 등 10인', 'value': '권영세의원 등 10인'},
                        {'label': '한병도의원 등 10인', 'value': '한병도의원 등 10인'},
                        {'label': '김선교의원 등 10인', 'value': '김선교의원 등 10인'},
                        {'label': '김승수의원 등 11인', 'value': '김승수의원 등 11인'}
                    ],
                    value='강대식의원 등 12인',
                    style={'fontFamily': 'Noto Sans KR', 'marginBottom': '20px'}
                )
            ], style={'width': '30%', 'margin': '0 auto', 'marginBottom': '30px'}),
            
            html.Div([
                dcc.Tabs(id="tabs", value="network-tab", children=[
                    dcc.Tab(label="네트워크 시각화", value="network-tab", 
                           style={'fontFamily': 'Noto Sans KR'}),
                    dcc.Tab(label="3D 시각화", value="3d-tab", 
                           style={'fontFamily': 'Noto Sans KR'}),
                    dcc.Tab(label="통계 분석", value="stats-tab", 
                           style={'fontFamily': 'Noto Sans KR'})
                ])
            ]),
            
            html.Div(id="tab-content", style={'marginTop': '20px'})
        ])
        
        @app.callback(Output("tab-content", "children"), Input("tabs", "value"), Input("politician-dropdown", "value"))
        def render_tab_content(active_tab, selected_politician):
            if active_tab == "network-tab":
                # Pyvis 네트워크 시각화
                html_file = self.create_pyvis_network(selected_politician)
                if html_file:
                    return html.Iframe(
                        src=f"../{html_file}",
                        style={"width": "100%", "height": "600px", "border": "none"}
                    )
                else:
                    return html.Div("네트워크 시각화를 생성할 수 없습니다.", 
                                  style={'textAlign': 'center', 'fontFamily': 'Noto Sans KR'})
            
            elif active_tab == "3d-tab":
                # Plotly 3D 시각화
                fig = self.create_plotly_network(selected_politician)
                if fig:
                    return dcc.Graph(figure=fig, style={"height": "600px"})
                else:
                    return html.Div("3D 시각화를 생성할 수 없습니다.", 
                                  style={'textAlign': 'center', 'fontFamily': 'Noto Sans KR'})
            
            elif active_tab == "stats-tab":
                # 통계 분석
                return self.create_stats_dashboard(selected_politician)
        
        return app
    
    def create_stats_dashboard(self, politician_name: str) -> html.Div:
        """통계 분석 대시보드"""
        # 샘플 통계 데이터
        stats_data = {
            "연결성 점수": 85.5,
            "총 연결 수": 15,
            "입법 연결": 3,
            "위원회 연결": 5,
            "정치적 연결": 4,
            "지역 연결": 2,
            "정책 연결": 1
        }
        
        # 연결 유형별 차트
        conn_types = list(self.connection_colors.keys())
        conn_counts = [3, 5, 4, 2, 1, 0]  # 샘플 데이터
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=conn_types,
            values=conn_counts,
            marker_colors=list(self.connection_colors.values()),
            textinfo='label+percent',
            textfont=dict(family="Noto Sans KR", size=12)
        )])
        
        fig_pie.update_layout(
            title="연결 유형별 분포",
            font=dict(family="Noto Sans KR"),
            showlegend=True
        )
        
        return html.Div([
            html.H3(f"{politician_name} 연결성 통계", 
                   style={'textAlign': 'center', 'fontFamily': 'Noto Sans KR'}),
            
            html.Div([
                html.Div([
                    html.H4("주요 지표", style={'fontFamily': 'Noto Sans KR'}),
                    html.Ul([
                        html.Li(f"{key}: {value}", style={'fontFamily': 'Noto Sans KR', 'margin': '10px 0'})
                        for key, value in stats_data.items()
                    ])
                ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                
                html.Div([
                    dcc.Graph(figure=fig_pie, style={"height": "400px"})
                ], style={'width': '50%', 'display': 'inline-block'})
            ])
        ])
    
    def run_visualization_demo(self):
        """시각화 데모 실행"""
        try:
            # Pyvis 네트워크 생성
            logger.info("Pyvis 네트워크 시각화 생성 중...")
            html_file = self.create_pyvis_network("강대식의원 등 12인")
            if html_file:
                logger.info(f"Pyvis 네트워크 저장 완료: {html_file}")
            
            # Plotly 3D 네트워크 생성
            logger.info("Plotly 3D 네트워크 시각화 생성 중...")
            fig = self.create_plotly_network("강대식의원 등 12인")
            if fig:
                fig.write_html("network_3d.html")
                logger.info("Plotly 3D 네트워크 저장 완료: network_3d.html")
            
            # Dash 앱 실행
            logger.info("Dash 앱 시작 중...")
            app = self.create_dash_app()
            app.run_server(debug=True, port=8050)
            
        except Exception as e:
            logger.error(f"시각화 데모 실행 실패: {e}")

def main():
    """메인 함수"""
    visualizer = AdvancedNetworkVisualizer()
    visualizer.run_visualization_demo()

if __name__ == "__main__":
    main()
