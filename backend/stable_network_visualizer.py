#!/usr/bin/env python3
"""
안정적인 네트워크 시각화 생성기
HTML/CSS/JavaScript로 직접 구현하여 안정성 확보
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StableNetworkVisualizer:
    """안정적인 네트워크 시각화 클래스"""
    
    def __init__(self, output_dir: str = "stable_network_widgets"):
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
    
    def create_network_widget(self, politician_name: str) -> str:
        """안정적인 네트워크 위젯 생성 (HTML/CSS/JS 직접 구현)"""
        try:
            if politician_name not in self.politicians:
                logger.error(f"정치인 데이터를 찾을 수 없습니다: {politician_name}")
                return None
            
            politician = self.politicians[politician_name]
            
            # HTML 콘텐츠 생성
            html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{politician['name']} 연결성 네트워크</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
            padding: 20px;
            overflow-x: auto;
        }}
        
        .network-container {{
            width: 100%;
            height: 600px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }}
        
        .network-svg {{
            width: 100%;
            height: 100%;
        }}
        
        .node {{
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .node:hover {{
            transform: scale(1.1);
        }}
        
        .node-center {{
            fill: #FFD700;
            stroke: #3498db;
            stroke-width: 3;
        }}
        
        .node-level1 {{
            fill: #ecf0f1;
            stroke: #bdc3c7;
            stroke-width: 2;
        }}
        
        .node-level2 {{
            fill: #f8f9fa;
            stroke: #95a5a6;
            stroke-width: 1.5;
        }}
        
        .node-level3 {{
            fill: #ffffff;
            stroke: #7f8c8d;
            stroke-width: 1;
        }}
        
        .node-text {{
            font-family: 'SF Pro Display', -apple-system, sans-serif;
            font-size: 12px;
            font-weight: 500;
            text-anchor: middle;
            dominant-baseline: central;
            pointer-events: none;
        }}
        
        .node-center .node-text {{
            font-size: 14px;
            font-weight: 600;
            fill: #2c3e50;
        }}
        
        .node-level1 .node-text {{
            font-size: 12px;
            fill: #2c3e50;
        }}
        
        .node-level2 .node-text {{
            font-size: 11px;
            fill: #7f8c8d;
        }}
        
        .node-level3 .node-text {{
            font-size: 10px;
            fill: #95a5a6;
        }}
        
        .edge {{
            stroke: #bdc3c7;
            stroke-width: 2;
            fill: none;
            opacity: 0.7;
        }}
        
        .edge:hover {{
            opacity: 1;
            stroke-width: 3;
        }}
        
        .tooltip {{
            position: absolute;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-size: 12px;
            pointer-events: none;
            z-index: 1000;
            max-width: 200px;
            font-family: 'SF Pro Display', -apple-system, sans-serif;
        }}
        
        .legend {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            font-size: 11px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }}
        
        .legend-color {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
    </style>
</head>
<body>
    <div class="network-container">
        <svg class="network-svg" id="networkSvg">
            <!-- 네트워크 노드와 엣지가 여기에 동적으로 생성됩니다 -->
        </svg>
        
        <div class="tooltip" id="tooltip" style="display: none;"></div>
        
        <div class="legend">
            <h4 style="margin-bottom: 10px; color: #2c3e50;">연결 유형</h4>
            <div class="legend-item">
                <div class="legend-color" style="background: #FF6B6B;"></div>
                <span>입법 연결</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #4ECDC4;"></div>
                <span>위원회 연결</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #45B7D1;"></div>
                <span>정치적 연결</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #96CEB4;"></div>
                <span>지역 연결</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FFEAA7;"></div>
                <span>정책 연결</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #DDA0DD;"></div>
                <span>시간 연결</span>
            </div>
        </div>
    </div>
    
    <script>
        // 정치인 데이터
        const politicianData = {json.dumps(politician, ensure_ascii=False, indent=2)};
        
        // 네트워크 생성
        function createNetwork() {{
            const svg = document.getElementById('networkSvg');
            const tooltip = document.getElementById('tooltip');
            
            // SVG 크기 설정
            const container = document.querySelector('.network-container');
            const width = container.clientWidth;
            const height = container.clientHeight;
            
            svg.setAttribute('width', width);
            svg.setAttribute('height', height);
            
            // 중심 노드 위치
            const centerX = width / 2;
            const centerY = height / 2;
            
            // 노드와 엣지 생성
            const nodes = [];
            const edges = [];
            
            // 중심 노드 추가
            nodes.push({{
                id: politicianData.name,
                x: centerX,
                y: centerY,
                level: 0,
                type: 'center',
                data: politicianData
            }});
            
            // 1단계 연결 노드들 (원형 배치)
            const level1Connections = politicianData.connections.filter(conn => conn.level === 1);
            const level1Radius = 150;
            
            level1Connections.forEach((conn, index) => {{
                const angle = (2 * Math.PI * index) / level1Connections.length;
                const x = centerX + level1Radius * Math.cos(angle);
                const y = centerY + level1Radius * Math.sin(angle);
                
                nodes.push({{
                    id: conn.name,
                    x: x,
                    y: y,
                    level: 1,
                    type: conn.type,
                    data: conn
                }});
                
                // 중심 노드와 연결
                edges.push({{
                    from: politicianData.name,
                    to: conn.name,
                    type: conn.type,
                    strength: conn.strength
                }});
            }});
            
            // 2단계 연결 노드들
            const level2Connections = politicianData.connections.filter(conn => conn.level === 2);
            level2Connections.forEach((conn, index) => {{
                const parentNode = nodes.find(node => node.id === conn.parent);
                if (parentNode) {{
                    const angle = Math.random() * 2 * Math.PI;
                    const distance = 100;
                    const x = parentNode.x + distance * Math.cos(angle);
                    const y = parentNode.y + distance * Math.sin(angle);
                    
                    nodes.push({{
                        id: conn.name,
                        x: x,
                        y: y,
                        level: 2,
                        type: conn.type,
                        data: conn
                    }});
                    
                    // 부모 노드와 연결
                    edges.push({{
                        from: conn.parent,
                        to: conn.name,
                        type: conn.type,
                        strength: conn.strength
                    }});
                }}
            }});
            
            // 3단계 연결 노드들
            const level3Connections = politicianData.connections.filter(conn => conn.level === 3);
            level3Connections.forEach((conn, index) => {{
                const parentNode = nodes.find(node => node.id === conn.parent);
                if (parentNode) {{
                    const angle = Math.random() * 2 * Math.PI;
                    const distance = 80;
                    const x = parentNode.x + distance * Math.cos(angle);
                    const y = parentNode.y + distance * Math.sin(angle);
                    
                    nodes.push({{
                        id: conn.name,
                        x: x,
                        y: y,
                        level: 3,
                        type: conn.type,
                        data: conn
                    }});
                    
                    // 부모 노드와 연결
                    edges.push({{
                        from: conn.parent,
                        to: conn.name,
                        type: conn.type,
                        strength: conn.strength
                    }});
                }}
            }});
            
            // SVG에 노드와 엣지 그리기
            drawNetwork(svg, nodes, edges, tooltip);
        }}
        
        function drawNetwork(svg, nodes, edges, tooltip) {{
            // 기존 내용 지우기
            svg.innerHTML = '';
            
            // 엣지 그리기
            edges.forEach(edge => {{
                const fromNode = nodes.find(n => n.id === edge.from);
                const toNode = nodes.find(n => n.id === edge.to);
                
                if (fromNode && toNode) {{
                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', fromNode.x);
                    line.setAttribute('y1', fromNode.y);
                    line.setAttribute('x2', toNode.x);
                    line.setAttribute('y2', toNode.y);
                    line.setAttribute('class', 'edge');
                    line.setAttribute('stroke', getConnectionColor(edge.type));
                    line.setAttribute('stroke-width', Math.max(1, edge.strength * 4));
                    
                    svg.appendChild(line);
                }}
            }});
            
            // 노드 그리기
            nodes.forEach(node => {{
                const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
                group.setAttribute('class', 'node');
                group.setAttribute('transform', `translate(${{node.x}}, ${{node.y}})`);
                
                // 노드 원 그리기
                const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                circle.setAttribute('r', getNodeRadius(node.level));
                circle.setAttribute('class', `node-level${{node.level}}`);
                
                if (node.level === 0) {{
                    circle.setAttribute('fill', '#FFD700');
                    circle.setAttribute('stroke', '#3498db');
                    circle.setAttribute('stroke-width', '3');
                }} else {{
                    circle.setAttribute('fill', '#ecf0f1');
                    circle.setAttribute('stroke', getConnectionColor(node.type));
                    circle.setAttribute('stroke-width', '2');
                }}
                
                // 노드 텍스트
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('class', 'node-text');
                text.textContent = node.id;
                
                // 이벤트 리스너
                group.addEventListener('mouseenter', (e) => {{
                    showTooltip(e, node, tooltip);
                }});
                
                group.addEventListener('mouseleave', () => {{
                    hideTooltip(tooltip);
                }});
                
                group.appendChild(circle);
                group.appendChild(text);
                svg.appendChild(group);
            }});
        }}
        
        function getNodeRadius(level) {{
            switch(level) {{
                case 0: return 25;
                case 1: return 20;
                case 2: return 15;
                case 3: return 12;
                default: return 10;
            }}
        }}
        
        function getConnectionColor(type) {{
            const colors = {{
                '입법_연결': '#FF6B6B',
                '위원회_연결': '#4ECDC4',
                '정치적_연결': '#45B7D1',
                '지역_연결': '#96CEB4',
                '정책_연결': '#FFEAA7',
                '시간_연결': '#DDA0DD'
            }};
            return colors[type] || '#bdc3c7';
        }}
        
        function showTooltip(event, node, tooltip) {{
            const data = node.data;
            let content = '';
            
            if (node.level === 0) {{
                content = `
                    <div style="font-weight: 600; margin-bottom: 5px;">${{data.name}}</div>
                    <div>${{data.party}}</div>
                    <div>${{data.district}}</div>
                    <div>${{data.committee}}</div>
                    <div style="color: #e74c3c; font-weight: 600; margin-top: 5px;">
                        연결성 점수: ${{data.connectivity_score}}점
                    </div>
                `;
            }} else {{
                content = `
                    <div style="font-weight: 600; margin-bottom: 5px;">${{data.name}}</div>
                    <div>연결 유형: ${{data.type}}</div>
                    <div>설명: ${{data.description}}</div>
                    <div style="color: ${{getConnectionColor(data.type)}}; font-weight: 600; margin-top: 5px;">
                        연결 강도: ${{data.strength.toFixed(1)}}
                    </div>
                `;
            }}
            
            tooltip.innerHTML = content;
            tooltip.style.display = 'block';
            tooltip.style.left = event.pageX + 10 + 'px';
            tooltip.style.top = event.pageY - 10 + 'px';
        }}
        
        function hideTooltip(tooltip) {{
            tooltip.style.display = 'none';
        }}
        
        // 페이지 로드 시 네트워크 생성
        window.addEventListener('load', createNetwork);
        window.addEventListener('resize', createNetwork);
    </script>
</body>
</html>
"""
            
            # HTML 파일로 저장
            filename = f"network_{politician['name']}.html"
            filepath = f"{self.output_dir}/widgets/{filename}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"안정적인 네트워크 위젯 생성 완료: {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"네트워크 위젯 생성 실패: {e}")
            return None
    
    def create_politician_page(self, politician_name: str) -> str:
        """개별 정치인 페이지 생성"""
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
    <title>{politician['name']} 연결성 분석</title>
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
                <h2>🌐 연결성 네트워크 시각화</h2>
                <div class="widget-container">
                    <iframe src="widgets/network_{politician['name']}.html"></iframe>
                </div>
            </div>
        </div>
    </div>
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
            
            # 네트워크 위젯 생성
            widget_file = self.create_network_widget(politician_name)
            
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
        """전체 정치인 목록 인덱스 페이지 생성"""
        try:
            html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>정치인 연결성 분석 - 안정적인 네트워크 시각화</title>
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
            <h1>🌐 정치인 연결성 분석</h1>
            <p>안정적인 네트워크 시각화 시스템</p>
        </div>
        
        <div class="politicians-grid">
"""
            
            # 각 정치인 카드 추가
            for politician_name, politician_data in self.politicians.items():
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
                <button class="view-button" onclick="event.stopPropagation(); location.href='pages/page_{politician_name}.html'">
                    네트워크 보기
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
        # 안정적인 네트워크 시각화 생성기 초기화
        visualizer = StableNetworkVisualizer()
        
        # 모든 정치인 위젯 생성
        logger.info("안정적인 네트워크 시각화 생성 시작...")
        results = visualizer.create_all_widgets()
        
        # 인덱스 페이지 생성
        logger.info("인덱스 페이지 생성 중...")
        index_file = visualizer.create_index_page()
        
        # 결과 출력
        print("\n🌐 안정적인 네트워크 시각화 완성!")
        print(f"📁 출력 디렉토리: {visualizer.output_dir}")
        print(f"📄 인덱스 페이지: {index_file}")
        print("\n📊 생성된 위젯:")
        
        for politician, result in results.items():
            print(f"  - {politician}:")
            print(f"    * 네트워크 위젯: {result['widget']}")
            print(f"    * 개인 페이지: {result['page']}")
        
        print(f"\n🌐 웹에서 보기: {visualizer.output_dir}/index.html")
        
    except Exception as e:
        logger.error(f"위젯 생성 실패: {e}")

if __name__ == "__main__":
    main()

