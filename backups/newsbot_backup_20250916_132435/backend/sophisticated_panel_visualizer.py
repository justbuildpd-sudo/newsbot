#!/usr/bin/env python3
"""
세련된 패널 기반 시각화 시스템
사각형 패널에 기본정보를 담고, 클릭 시 해당 인물의 연결정보로 확장
"""

import json
import os
import math
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SophisticatedPanelVisualizer:
    """세련된 패널 기반 시각화 시스템"""
    
    def __init__(self, output_dir: str = "sophisticated_panels"):
        self.output_dir = output_dir
        self.connection_colors = {
            "입법_연결": "#FF6B6B",  # 공동발의 (빨간색)
            "위원회_연결": "#4ECDC4", # 같은 위원회 (청록색)
            "정치적_연결": "#45B7D1", # 같은 정당 (파란색)
            "지역_연결": "#96CEB4",  # 같은 지역구 (연두색)
            "정책_연결": "#FFEAA7",  # 유사 정책 (노란색)
            "시간_연결": "#DDA0DD",  # 동시기 활동 (보라색)
        }
        
        # 확장된 정치인 데이터
        self.politicians = {
            "정청래": {
                "name": "정청래",
                "party": "더불어민주당",
                "district": "서울 마포구을",
                "committee": "기획재정위원회",
                "position": "국회의원",
                "term": "22대",
                "connectivity_score": 85.5,
                "photo_url": "https://via.placeholder.com/120x150/3498db/ffffff?text=정청래",
                "connections": [
                    {"name": "김영배", "type": "정치적_연결", "strength": 0.9, "description": "같은 정당", "level": 1, "party": "더불어민주당", "district": "서울 강남구갑", "committee": "기획재정위원회"},
                    {"name": "박수현", "type": "위원회_연결", "strength": 0.8, "description": "같은 위원회", "level": 1, "party": "더불어민주당", "district": "경기 성남시분당구갑", "committee": "기획재정위원회"},
                    {"name": "이재정", "type": "입법_연결", "strength": 0.7, "description": "공동발의", "level": 1, "party": "더불어민주당", "district": "서울 마포구갑", "committee": "환경노동위원회"},
                    {"name": "최민호", "type": "지역_연결", "strength": 0.6, "description": "같은 지역구", "level": 1, "party": "더불어민주당", "district": "서울 마포구을", "committee": "과학기술정보방송통신위원회"},
                    {"name": "서지영", "type": "정책_연결", "strength": 0.5, "description": "유사 정책", "level": 1, "party": "더불어민주당", "district": "서울 강동구갑", "committee": "기획재정위원회"},
                    {"name": "권영세", "type": "시간_연결", "strength": 0.4, "description": "동시기 활동", "level": 1, "party": "더불어민주당", "district": "서울 송파구갑", "committee": "법제사법위원회"},
                    # 2단계 연결
                    {"name": "김태호", "type": "정치적_연결", "strength": 0.3, "description": "김영배와 연결", "level": 2, "parent": "김영배", "party": "더불어민주당", "district": "서울 강남구을", "committee": "기획재정위원회"},
                    {"name": "박민수", "type": "위원회_연결", "strength": 0.3, "description": "박수현과 연결", "level": 2, "parent": "박수현", "party": "더불어민주당", "district": "경기 성남시분당구을", "committee": "기획재정위원회"},
                    {"name": "이수진", "type": "입법_연결", "strength": 0.2, "description": "이재정과 연결", "level": 2, "parent": "이재정", "party": "더불어민주당", "district": "서울 마포구갑", "committee": "환경노동위원회"},
                    {"name": "최영희", "type": "지역_연결", "strength": 0.2, "description": "최민호와 연결", "level": 2, "parent": "최민호", "party": "더불어민주당", "district": "서울 마포구을", "committee": "과학기술정보방송통신위원회"},
                    {"name": "서민수", "type": "정책_연결", "strength": 0.2, "description": "서지영과 연결", "level": 2, "parent": "서지영", "party": "더불어민주당", "district": "서울 강동구을", "committee": "기획재정위원회"},
                    {"name": "권지영", "type": "시간_연결", "strength": 0.2, "description": "권영세와 연결", "level": 2, "parent": "권영세", "party": "더불어민주당", "district": "서울 송파구을", "committee": "법제사법위원회"},
                    # 3단계 연결
                    {"name": "김수진", "type": "정치적_연결", "strength": 0.1, "description": "김태호와 연결", "level": 3, "parent": "김태호", "party": "더불어민주당", "district": "서울 강남구갑", "committee": "기획재정위원회"},
                    {"name": "박영희", "type": "위원회_연결", "strength": 0.1, "description": "박민수와 연결", "level": 3, "parent": "박민수", "party": "더불어민주당", "district": "경기 성남시분당구갑", "committee": "기획재정위원회"},
                    {"name": "이민수", "type": "입법_연결", "strength": 0.1, "description": "이수진과 연결", "level": 3, "parent": "이수진", "party": "더불어민주당", "district": "서울 마포구갑", "committee": "환경노동위원회"},
                    {"name": "최지영", "type": "지역_연결", "strength": 0.1, "description": "최영희와 연결", "level": 3, "parent": "최영희", "party": "더불어민주당", "district": "서울 마포구을", "committee": "과학기술정보방송통신위원회"},
                    {"name": "서수진", "type": "정책_연결", "strength": 0.1, "description": "서민수와 연결", "level": 3, "parent": "서민수", "party": "더불어민주당", "district": "서울 강동구갑", "committee": "기획재정위원회"},
                    {"name": "권영희", "type": "시간_연결", "strength": 0.1, "description": "권지영과 연결", "level": 3, "parent": "권지영", "party": "더불어민주당", "district": "서울 송파구갑", "committee": "법제사법위원회"}
                ]
            },
            "김영배": {
                "name": "김영배",
                "party": "더불어민주당",
                "district": "서울 강남구갑",
                "committee": "기획재정위원회",
                "position": "국회의원",
                "term": "22대",
                "connectivity_score": 78.2,
                "photo_url": "https://via.placeholder.com/120x150/e74c3c/ffffff?text=김영배",
                "connections": [
                    {"name": "정청래", "type": "정치적_연결", "strength": 0.9, "description": "같은 정당", "level": 1, "party": "더불어민주당", "district": "서울 마포구을", "committee": "기획재정위원회"},
                    {"name": "박수현", "type": "위원회_연결", "strength": 0.8, "description": "같은 위원회", "level": 1, "party": "더불어민주당", "district": "경기 성남시분당구갑", "committee": "기획재정위원회"},
                    {"name": "이재정", "type": "입법_연결", "strength": 0.7, "description": "공동발의", "level": 1, "party": "더불어민주당", "district": "서울 마포구갑", "committee": "환경노동위원회"},
                    {"name": "최민호", "type": "지역_연결", "strength": 0.6, "description": "같은 지역구", "level": 1, "party": "더불어민주당", "district": "서울 강남구을", "committee": "과학기술정보방송통신위원회"},
                    {"name": "서지영", "type": "정책_연결", "strength": 0.5, "description": "유사 정책", "level": 1, "party": "더불어민주당", "district": "서울 강동구갑", "committee": "기획재정위원회"},
                    {"name": "권영세", "type": "시간_연결", "strength": 0.4, "description": "동시기 활동", "level": 1, "party": "더불어민주당", "district": "서울 송파구갑", "committee": "법제사법위원회"}
                ]
            }
        }
        
        # 출력 디렉토리 생성
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/widgets", exist_ok=True)
        os.makedirs(f"{self.output_dir}/pages", exist_ok=True)
    
    def calculate_panel_positions(self, connections: List[Dict], center_x: float = 400, center_y: float = 300) -> List[Dict]:
        """패널 위치 계산 (방사형 배치)"""
        positions = []
        
        # 중심 패널 (정청래)
        positions.append({
            "name": "정청래",
            "x": center_x,
            "y": center_y,
            "level": 0,
            "is_center": True,
            "width": 200,
            "height": 120
        })
        
        # 1단계 연결 (중심에서 반지름 180px)
        level1_connections = [conn for conn in connections if conn["level"] == 1]
        level1_radius = 180
        level1_angle_step = 2 * math.pi / len(level1_connections) if level1_connections else 0
        
        for i, conn in enumerate(level1_connections):
            angle = i * level1_angle_step
            x = center_x + level1_radius * math.cos(angle) - 80  # 패널 중심으로 조정
            y = center_y + level1_radius * math.sin(angle) - 40
            positions.append({
                "name": conn["name"],
                "x": x,
                "y": y,
                "level": 1,
                "parent": "정청래",
                "connection_type": conn["type"],
                "strength": conn["strength"],
                "width": 160,
                "height": 80
            })
        
        # 2단계 연결 (1단계에서 반지름 120px)
        level2_connections = [conn for conn in connections if conn["level"] == 2]
        level2_radius = 120
        
        for conn in level2_connections:
            parent_pos = next((pos for pos in positions if pos["name"] == conn["parent"]), None)
            if parent_pos:
                siblings = [c for c in level2_connections if c["parent"] == conn["parent"]]
                sibling_index = siblings.index(conn)
                sibling_count = len(siblings)
                
                if sibling_count == 1:
                    parent_angle = math.atan2(parent_pos["y"] - center_y, parent_pos["x"] - center_x)
                    angle = parent_angle + math.pi
                else:
                    parent_angle = math.atan2(parent_pos["y"] - center_y, parent_pos["x"] - center_x)
                    angle_offset = (sibling_index - (sibling_count - 1) / 2) * 0.8
                    angle = parent_angle + angle_offset
                
                x = parent_pos["x"] + level2_radius * math.cos(angle) - 60
                y = parent_pos["y"] + level2_radius * math.sin(angle) - 30
                positions.append({
                    "name": conn["name"],
                    "x": x,
                    "y": y,
                    "level": 2,
                    "parent": conn["parent"],
                    "connection_type": conn["type"],
                    "strength": conn["strength"],
                    "width": 120,
                    "height": 60
                })
        
        # 3단계 연결 (2단계에서 반지름 80px)
        level3_connections = [conn for conn in connections if conn["level"] == 3]
        level3_radius = 80
        
        for conn in level3_connections:
            parent_pos = next((pos for pos in positions if pos["name"] == conn["parent"]), None)
            if parent_pos:
                parent_angle = math.atan2(parent_pos["y"] - center_y, parent_pos["x"] - center_x)
                angle = parent_angle + math.pi
                
                x = parent_pos["x"] + level3_radius * math.cos(angle) - 40
                y = parent_pos["y"] + level3_radius * math.sin(angle) - 20
                positions.append({
                    "name": conn["name"],
                    "x": x,
                    "y": y,
                    "level": 3,
                    "parent": conn["parent"],
                    "connection_type": conn["type"],
                    "strength": conn["strength"],
                    "width": 80,
                    "height": 40
                })
        
        return positions
    
    def create_sophisticated_panel_widget(self, politician_name: str) -> str:
        """세련된 패널 기반 위젯 생성"""
        try:
            if politician_name not in self.politicians:
                logger.error(f"정치인 데이터를 찾을 수 없습니다: {politician_name}")
                return None
            
            politician = self.politicians[politician_name]
            positions = self.calculate_panel_positions(politician["connections"])
            
            # HTML 콘텐츠 생성
            html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{politician['name']} 세련된 패널 네트워크</title>
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
            overflow: hidden;
        }}
        
        .network-container {{
            width: 100%;
            height: 100vh;
            position: relative;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .network-svg {{
            width: 100%;
            height: 100%;
        }}
        
        .panel {{
            cursor: pointer;
            transition: all 0.3s ease;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
        }}
        
        .panel:hover {{
            transform: scale(1.05);
            filter: drop-shadow(0 8px 16px rgba(0,0,0,0.2));
        }}
        
        .panel-center {{
            fill: #FFD700;
            stroke: #2c3e50;
            stroke-width: 3;
            rx: 15;
            ry: 15;
        }}
        
        .panel-level1 {{
            fill: #3498db;
            stroke: #2980b9;
            stroke-width: 2;
            rx: 12;
            ry: 12;
        }}
        
        .panel-level2 {{
            fill: #2ecc71;
            stroke: #27ae60;
            stroke-width: 2;
            rx: 10;
            ry: 10;
        }}
        
        .panel-level3 {{
            fill: #e74c3c;
            stroke: #c0392b;
            stroke-width: 2;
            rx: 8;
            ry: 8;
        }}
        
        .panel-text {{
            font-family: 'SF Pro Display', -apple-system, sans-serif;
            font-size: 12px;
            font-weight: 600;
            fill: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }}
        
        .panel-name {{
            font-size: 14px;
            font-weight: 700;
            text-anchor: middle;
            dominant-baseline: middle;
        }}
        
        .panel-info {{
            font-size: 10px;
            font-weight: 500;
            text-anchor: middle;
            dominant-baseline: middle;
        }}
        
        .connection-line {{
            stroke-width: 2;
            fill: none;
            opacity: 0.6;
            transition: all 0.3s ease;
        }}
        
        .connection-line:hover {{
            stroke-width: 4;
            opacity: 1;
        }}
        
        .connection-line.입법_연결 {{ stroke: #FF6B6B; }}
        .connection-line.위원회_연결 {{ stroke: #4ECDC4; }}
        .connection-line.정치적_연결 {{ stroke: #45B7D1; }}
        .connection-line.지역_연결 {{ stroke: #96CEB4; }}
        .connection-line.정책_연결 {{ stroke: #FFEAA7; }}
        .connection-line.시간_연결 {{ stroke: #DDA0DD; }}
        
        .legend {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            min-width: 200px;
        }}
        
        .legend-title {{
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
            text-align: center;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            font-size: 12px;
        }}
        
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 4px;
            margin-right: 10px;
        }}
        
        .info-panel {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(255,255,255,0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            max-width: 350px;
        }}
        
        .info-title {{
            font-size: 20px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        
        .info-detail {{
            font-size: 13px;
            color: #7f8c8d;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
        }}
        
        .info-label {{
            font-weight: 500;
        }}
        
        .info-value {{
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .score-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #3498db, #2ecc71);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            margin-top: 15px;
            text-align: center;
            width: 100%;
        }}
        
        .controls {{
            position: absolute;
            top: 20px;
            left: 20px;
            display: flex;
            gap: 10px;
        }}
        
        .control-btn {{
            background: rgba(255,255,255,0.9);
            border: none;
            padding: 12px 18px;
            border-radius: 25px;
            font-family: 'SF Pro Display', -apple-system, sans-serif;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        
        .control-btn:hover {{
            background: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .control-btn.active {{
            background: #3498db;
            color: white;
        }}
        
        .detail-modal {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }}
        
        .modal-content {{
            background: white;
            padding: 30px;
            border-radius: 20px;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }}
        
        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        
        .modal-title {{
            font-size: 24px;
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .close-btn {{
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #7f8c8d;
        }}
        
        .modal-body {{
            font-size: 14px;
            line-height: 1.6;
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    <div class="network-container">
        <div class="controls">
            <button class="control-btn" onclick="resetView()">초기화</button>
            <button class="control-btn" onclick="toggleLevels()">레벨 토글</button>
            <button class="control-btn" onclick="showAllPanels()">전체 보기</button>
        </div>
        
        <div class="legend">
            <div class="legend-title">연결 유형</div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FF6B6B;"></div>
                <span>공동발의</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #4ECDC4;"></div>
                <span>같은 위원회</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #45B7D1;"></div>
                <span>같은 정당</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #96CEB4;"></div>
                <span>같은 지역구</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FFEAA7;"></div>
                <span>유사 정책</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #DDA0DD;"></div>
                <span>동시기 활동</span>
            </div>
        </div>
        
        <div class="info-panel">
            <div class="info-title">{politician['name']}</div>
            <div class="info-detail">
                <span class="info-label">정당:</span>
                <span class="info-value">{politician['party']}</span>
            </div>
            <div class="info-detail">
                <span class="info-label">지역구:</span>
                <span class="info-value">{politician['district']}</span>
            </div>
            <div class="info-detail">
                <span class="info-label">위원회:</span>
                <span class="info-value">{politician['committee']}</span>
            </div>
            <div class="score-badge">연결성 점수: {politician['connectivity_score']}</div>
        </div>
        
        <svg class="network-svg" viewBox="0 0 800 600">
"""
            
            # 연결선 그리기
            for pos in positions:
                if pos["name"] != "정청래" and "parent" in pos:
                    parent_pos = next((p for p in positions if p["name"] == pos["parent"]), None)
                    if parent_pos:
                        connection_type = pos.get("connection_type", "정치적_연결")
                        # 패널 중심점으로 연결선 그리기
                        parent_center_x = parent_pos["x"] + parent_pos["width"] / 2
                        parent_center_y = parent_pos["y"] + parent_pos["height"] / 2
                        child_center_x = pos["x"] + pos["width"] / 2
                        child_center_y = pos["y"] + pos["height"] / 2
                        
                        html_content += f'''
            <line class="connection-line {connection_type}" 
                  x1="{parent_center_x}" y1="{parent_center_y}" 
                  x2="{child_center_x}" y2="{child_center_y}">
                <title>{pos['parent']} → {pos['name']} ({connection_type})</title>
            </line>
'''
            
            # 패널 그리기
            for pos in positions:
                if pos["name"] == "정청래":
                    # 중심 패널
                    html_content += f'''
            <rect class="panel panel-center" 
                  x="{pos['x']}" y="{pos['y']}" 
                  width="{pos['width']}" height="{pos['height']}">
                <title>{pos['name']} (중심)</title>
            </rect>
            <text class="panel-text panel-name" x="{pos['x'] + pos['width']/2}" y="{pos['y'] + 30}">{pos['name']}</text>
            <text class="panel-text panel-info" x="{pos['x'] + pos['width']/2}" y="{pos['y'] + 50}">{politician['party']}</text>
            <text class="panel-text panel-info" x="{pos['x'] + pos['width']/2}" y="{pos['y'] + 70}">{politician['district']}</text>
            <text class="panel-text panel-info" x="{pos['x'] + pos['width']/2}" y="{pos['y'] + 90}">점수: {politician['connectivity_score']}</text>
'''
                else:
                    # 주변 패널
                    level = pos["level"]
                    panel_class = f"panel-level{level}"
                    
                    # 연결된 정치인 정보 찾기
                    conn_info = next((conn for conn in politician["connections"] if conn["name"] == pos["name"]), {})
                    
                    html_content += f'''
            <rect class="panel {panel_class}" 
                  x="{pos['x']}" y="{pos['y']}" 
                  width="{pos['width']}" height="{pos['height']}">
                <title>{pos['name']} (레벨 {level})</title>
            </rect>
            <text class="panel-text panel-name" x="{pos['x'] + pos['width']/2}" y="{pos['y'] + 20}">{pos['name']}</text>
            <text class="panel-text panel-info" x="{pos['x'] + pos['width']/2}" y="{pos['y'] + 35}">{conn_info.get('party', '')}</text>
            <text class="panel-text panel-info" x="{pos['x'] + pos['width']/2}" y="{pos['y'] + 50}">{conn_info.get('district', '')}</text>
'''
            
            html_content += """
        </svg>
    </div>
    
    <!-- 상세 정보 모달 -->
    <div class="detail-modal" id="detailModal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title" id="modalTitle">상세 정보</div>
                <button class="close-btn" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body" id="modalBody">
                <!-- 상세 정보가 여기에 표시됩니다 -->
            </div>
        </div>
    </div>
    
    <script>
        let showAllLevels = true;
        let currentPolitician = '정청래';
        
        function resetView() {
            const svg = document.querySelector('.network-svg');
            svg.style.transform = 'scale(1) translate(0, 0)';
        }
        
        function toggleLevels() {
            showAllLevels = !showAllLevels;
            const panels = document.querySelectorAll('.panel');
            const lines = document.querySelectorAll('.connection-line');
            
            panels.forEach(panel => {
                const level = panel.classList.contains('panel-center') ? 0 : 
                             panel.classList.contains('panel-level1') ? 1 :
                             panel.classList.contains('panel-level2') ? 2 : 3;
                
                if (level > 2 && !showAllLevels) {
                    panel.style.display = 'none';
                } else {
                    panel.style.display = 'block';
                }
            });
            
            lines.forEach(line => {
                if (!showAllLevels) {
                    line.style.display = 'none';
                } else {
                    line.style.display = 'block';
                }
            });
        }
        
        function showAllPanels() {
            const panels = document.querySelectorAll('.panel');
            const lines = document.querySelectorAll('.connection-line');
            
            panels.forEach(panel => {
                panel.style.display = 'block';
            });
            
            lines.forEach(line => {
                line.style.display = 'block';
            });
        }
        
        function showPoliticianDetail(politicianName) {
            // 해당 정치인의 상세 정보 표시
            const modal = document.getElementById('detailModal');
            const title = document.getElementById('modalTitle');
            const body = document.getElementById('modalBody');
            
            title.textContent = politicianName + ' 상세 정보';
            body.innerHTML = `
                <h3>기본 정보</h3>
                <p><strong>정당:</strong> ${politicianName}의 정당</p>
                <p><strong>지역구:</strong> ${politicianName}의 지역구</p>
                <p><strong>위원회:</strong> ${politicianName}의 위원회</p>
                <p><strong>연결성 점수:</strong> 85.5</p>
                
                <h3>주요 연결</h3>
                <ul>
                    <li>김영배 - 같은 정당 (강도: 0.9)</li>
                    <li>박수현 - 같은 위원회 (강도: 0.8)</li>
                    <li>이재정 - 공동발의 (강도: 0.7)</li>
                </ul>
                
                <h3>입법 활동</h3>
                <p>총 발의 법안: 15건</p>
                <p>통과 법안: 8건</p>
                <p>통과율: 53.3%</p>
            `;
            
            modal.style.display = 'flex';
        }
        
        function closeModal() {
            const modal = document.getElementById('detailModal');
            modal.style.display = 'none';
        }
        
        // 드래그 앤 줌 기능
        let isDragging = false;
        let startX, startY, translateX = 0, translateY = 0, scale = 1;
        
        const svg = document.querySelector('.network-svg');
        
        svg.addEventListener('mousedown', (e) => {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
        });
        
        svg.addEventListener('mousemove', (e) => {
            if (isDragging) {
                const deltaX = e.clientX - startX;
                const deltaY = e.clientY - startY;
                translateX += deltaX;
                translateY += deltaY;
                svg.style.transform = `scale(${scale}) translate(${translateX}px, ${translateY}px)`;
                startX = e.clientX;
                startY = e.clientY;
            }
        });
        
        svg.addEventListener('mouseup', () => {
            isDragging = false;
        });
        
        svg.addEventListener('wheel', (e) => {
            e.preventDefault();
            const delta = e.deltaY > 0 ? 0.9 : 1.1;
            scale *= delta;
            scale = Math.max(0.5, Math.min(3, scale));
            svg.style.transform = `scale(${scale}) translate(${translateX}px, ${translateY}px)`;
        });
        
        // 패널 클릭 이벤트
        document.querySelectorAll('.panel').forEach(panel => {
            panel.addEventListener('click', (e) => {
                const name = e.target.getAttribute('title').split(' ')[0];
                console.log('선택된 패널:', name);
                showPoliticianDetail(name);
            });
        });
        
        // 모달 외부 클릭 시 닫기
        document.getElementById('detailModal').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                closeModal();
            }
        });
    </script>
</body>
</html>
"""
            
            # HTML 파일로 저장
            filename = f"sophisticated_panel_{politician_name}.html"
            filepath = f"{self.output_dir}/widgets/{filename}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"세련된 패널 위젯 생성 완료: {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"세련된 패널 위젯 생성 실패: {e}")
            return None
    
    def create_all_widgets(self) -> Dict[str, Any]:
        """모든 정치인 세련된 패널 위젯 생성"""
        results = {}
        
        for politician_name in self.politicians.keys():
            logger.info(f"세련된 패널 위젯 생성 중: {politician_name}")
            
            widget_file = self.create_sophisticated_panel_widget(politician_name)
            
            if widget_file:
                results[politician_name] = {
                    "widget": widget_file,
                    "status": "success"
                }
        
        return results

def main():
    """메인 함수"""
    try:
        # 세련된 패널 시각화 시스템 초기화
        visualizer = SophisticatedPanelVisualizer()
        
        # 모든 정치인 위젯 생성
        logger.info("세련된 패널 시각화 시스템 생성 시작...")
        results = visualizer.create_all_widgets()
        
        # 결과 출력
        print("\n🎨 세련된 패널 시각화 시스템 완성!")
        print(f"📁 출력 디렉토리: {visualizer.output_dir}")
        print("\n📊 생성된 위젯:")
        
        for politician, result in results.items():
            print(f"  - {politician}: {result['widget']}")
        
        print(f"\n🌐 웹에서 보기: {visualizer.output_dir}/widgets/sophisticated_panel_정청래.html")
        
    except Exception as e:
        logger.error(f"세련된 패널 시각화 생성 실패: {e}")

if __name__ == "__main__":
    main()
