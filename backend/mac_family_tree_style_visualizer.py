#!/usr/bin/env python3
"""
맥패밀리트리 스타일 방사형 시각화 시스템
중심 정치인을 중심으로 주변 인물들을 원형으로 배치하는 방사형 레이아웃
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

class MacFamilyTreeStyleVisualizer:
    """맥패밀리트리 스타일 방사형 시각화 시스템"""
    
    def __init__(self, output_dir: str = "mac_family_tree_widgets"):
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
                "position": "국회의원",
                "term": "22대",
                "connectivity_score": 85.5,
                "photo_url": "https://via.placeholder.com/120x150/3498db/ffffff?text=정청래",
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
                    {"name": "최영희", "type": "지역_연결", "strength": 0.2, "description": "최민호와 연결", "level": 2, "parent": "최민호"},
                    {"name": "서민수", "type": "정책_연결", "strength": 0.2, "description": "서지영과 연결", "level": 2, "parent": "서지영"},
                    {"name": "권지영", "type": "시간_연결", "strength": 0.2, "description": "권영세와 연결", "level": 2, "parent": "권영세"},
                    # 3단계 연결
                    {"name": "김수진", "type": "정치적_연결", "strength": 0.1, "description": "김태호와 연결", "level": 3, "parent": "김태호"},
                    {"name": "박영희", "type": "위원회_연결", "strength": 0.1, "description": "박민수와 연결", "level": 3, "parent": "박민수"},
                    {"name": "이민수", "type": "입법_연결", "strength": 0.1, "description": "이수진과 연결", "level": 3, "parent": "이수진"},
                    {"name": "최지영", "type": "지역_연결", "strength": 0.1, "description": "최영희와 연결", "level": 3, "parent": "최영희"},
                    {"name": "서수진", "type": "정책_연결", "strength": 0.1, "description": "서민수와 연결", "level": 3, "parent": "서민수"},
                    {"name": "권영희", "type": "시간_연결", "strength": 0.1, "description": "권지영과 연결", "level": 3, "parent": "권지영"}
                ]
            }
        }
        
        # 출력 디렉토리 생성
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/widgets", exist_ok=True)
        os.makedirs(f"{self.output_dir}/pages", exist_ok=True)
    
    def calculate_radial_positions(self, connections: List[Dict], center_x: float = 400, center_y: float = 300) -> List[Dict]:
        """방사형 위치 계산 (맥패밀리트리 스타일)"""
        positions = []
        
        # 중심 노드 (정청래)
        positions.append({
            "name": "정청래",
            "x": center_x,
            "y": center_y,
            "level": 0,
            "is_center": True
        })
        
        # 1단계 연결 (중심에서 반지름 120px)
        level1_connections = [conn for conn in connections if conn["level"] == 1]
        level1_radius = 120
        level1_angle_step = 2 * math.pi / len(level1_connections) if level1_connections else 0
        
        for i, conn in enumerate(level1_connections):
            angle = i * level1_angle_step
            x = center_x + level1_radius * math.cos(angle)
            y = center_y + level1_radius * math.sin(angle)
            positions.append({
                "name": conn["name"],
                "x": x,
                "y": y,
                "level": 1,
                "parent": "정청래",
                "connection_type": conn["type"],
                "strength": conn["strength"]
            })
        
        # 2단계 연결 (1단계에서 반지름 80px)
        level2_connections = [conn for conn in connections if conn["level"] == 2]
        level2_radius = 80
        
        for conn in level2_connections:
            # 부모 노드의 위치 찾기
            parent_pos = next((pos for pos in positions if pos["name"] == conn["parent"]), None)
            if parent_pos:
                # 부모 노드 주변에 배치 (각 부모당 2-3개씩)
                siblings = [c for c in level2_connections if c["parent"] == conn["parent"]]
                sibling_index = siblings.index(conn)
                sibling_count = len(siblings)
                
                if sibling_count == 1:
                    # 부모 노드 반대편에 배치
                    parent_angle = math.atan2(parent_pos["y"] - center_y, parent_pos["x"] - center_x)
                    angle = parent_angle + math.pi
                else:
                    # 부모 노드 주변에 분산 배치
                    parent_angle = math.atan2(parent_pos["y"] - center_y, parent_pos["x"] - center_x)
                    angle_offset = (sibling_index - (sibling_count - 1) / 2) * 0.5
                    angle = parent_angle + angle_offset
                
                x = parent_pos["x"] + level2_radius * math.cos(angle)
                y = parent_pos["y"] + level2_radius * math.sin(angle)
                positions.append({
                    "name": conn["name"],
                    "x": x,
                    "y": y,
                    "level": 2,
                    "parent": conn["parent"],
                    "connection_type": conn["type"],
                    "strength": conn["strength"]
                })
        
        # 3단계 연결 (2단계에서 반지름 60px)
        level3_connections = [conn for conn in connections if conn["level"] == 3]
        level3_radius = 60
        
        for conn in level3_connections:
            # 부모 노드의 위치 찾기
            parent_pos = next((pos for pos in positions if pos["name"] == conn["parent"]), None)
            if parent_pos:
                # 부모 노드 반대편에 배치
                parent_angle = math.atan2(parent_pos["y"] - center_y, parent_pos["x"] - center_x)
                angle = parent_angle + math.pi
                
                x = parent_pos["x"] + level3_radius * math.cos(angle)
                y = parent_pos["y"] + level3_radius * math.sin(angle)
                positions.append({
                    "name": conn["name"],
                    "x": x,
                    "y": y,
                    "level": 3,
                    "parent": conn["parent"],
                    "connection_type": conn["type"],
                    "strength": conn["strength"]
                })
        
        return positions
    
    def create_radial_network_widget(self, politician_name: str) -> str:
        """맥패밀리트리 스타일 방사형 네트워크 위젯 생성"""
        try:
            if politician_name not in self.politicians:
                logger.error(f"정치인 데이터를 찾을 수 없습니다: {politician_name}")
                return None
            
            politician = self.politicians[politician_name]
            positions = self.calculate_radial_positions(politician["connections"])
            
            # HTML 콘텐츠 생성
            html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{politician['name']} 맥패밀리트리 스타일 네트워크</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
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
        
        .node {{
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .node:hover {{
            transform: scale(1.1);
        }}
        
        .node-center {{
            fill: #FFD700;
            stroke: #2c3e50;
            stroke-width: 3;
        }}
        
        .node-level1 {{
            fill: #3498db;
            stroke: #2980b9;
            stroke-width: 2;
        }}
        
        .node-level2 {{
            fill: #2ecc71;
            stroke: #27ae60;
            stroke-width: 2;
        }}
        
        .node-level3 {{
            fill: #e74c3c;
            stroke: #c0392b;
            stroke-width: 2;
        }}
        
        .node-text {{
            font-family: 'SF Pro Display', -apple-system, sans-serif;
            font-size: 12px;
            font-weight: 600;
            text-anchor: middle;
            dominant-baseline: middle;
            fill: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
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
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }}
        
        .legend-title {{
            font-size: 14px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 5px;
            font-size: 12px;
        }}
        
        .legend-color {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        
        .info-panel {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            max-width: 300px;
        }}
        
        .info-title {{
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .info-detail {{
            font-size: 12px;
            color: #7f8c8d;
            margin-bottom: 5px;
        }}
        
        .score-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #3498db, #2ecc71);
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 10px;
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
            padding: 10px 15px;
            border-radius: 20px;
            font-family: 'SF Pro Display', -apple-system, sans-serif;
            font-size: 12px;
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
    </style>
</head>
<body>
    <div class="network-container">
        <div class="controls">
            <button class="control-btn" onclick="resetView()">초기화</button>
            <button class="control-btn" onclick="toggleLevels()">레벨 토글</button>
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
            <div class="info-detail">정당: {politician['party']}</div>
            <div class="info-detail">지역구: {politician['district']}</div>
            <div class="info-detail">위원회: {politician['committee']}</div>
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
                        html_content += f'''
            <line class="connection-line {connection_type}" 
                  x1="{parent_pos['x']}" y1="{parent_pos['y']}" 
                  x2="{pos['x']}" y2="{pos['y']}">
                <title>{pos['parent']} → {pos['name']} ({connection_type})</title>
            </line>
'''
            
            # 노드 그리기
            for pos in positions:
                if pos["name"] == "정청래":
                    # 중심 노드
                    html_content += f'''
            <circle class="node node-center" 
                    cx="{pos['x']}" cy="{pos['y']}" r="25">
                <title>{pos['name']} (중심)</title>
            </circle>
            <text class="node-text" x="{pos['x']}" y="{pos['y']}">{pos['name'][0]}</text>
'''
                else:
                    # 주변 노드
                    level = pos["level"]
                    radius = 20 if level == 1 else 15 if level == 2 else 12
                    node_class = f"node-level{level}"
                    
                    html_content += f'''
            <circle class="node {node_class}" 
                    cx="{pos['x']}" cy="{pos['y']}" r="{radius}">
                <title>{pos['name']} (레벨 {level})</title>
            </circle>
            <text class="node-text" x="{pos['x']}" y="{pos['y']}">{pos['name'][0]}</text>
'''
            
            html_content += """
        </svg>
    </div>
    
    <script>
        let showAllLevels = true;
        
        function resetView() {
            const svg = document.querySelector('.network-svg');
            svg.style.transform = 'scale(1) translate(0, 0)';
        }
        
        function toggleLevels() {
            showAllLevels = !showAllLevels;
            const nodes = document.querySelectorAll('.node');
            const lines = document.querySelectorAll('.connection-line');
            
            nodes.forEach(node => {
                const level = node.classList.contains('node-center') ? 0 : 
                             node.classList.contains('node-level1') ? 1 :
                             node.classList.contains('node-level2') ? 2 : 3;
                
                if (level > 2 && !showAllLevels) {
                    node.style.display = 'none';
                } else {
                    node.style.display = 'block';
                }
            });
            
            lines.forEach(line => {
                const startNode = line.getAttribute('x1');
                const endNode = line.getAttribute('x2');
                // 간단한 레벨 체크 (실제로는 더 정교한 로직 필요)
                if (!showAllLevels) {
                    line.style.display = 'none';
                } else {
                    line.style.display = 'block';
                }
            });
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
        
        // 노드 클릭 이벤트
        document.querySelectorAll('.node').forEach(node => {
            node.addEventListener('click', (e) => {
                const name = e.target.getAttribute('title').split(' ')[0];
                console.log('선택된 노드:', name);
                // 여기에 노드 선택 시 상세 정보 표시 로직 추가
            });
        });
    </script>
</body>
</html>
"""
            
            # HTML 파일로 저장
            filename = f"radial_network_{politician_name}.html"
            filepath = f"{self.output_dir}/widgets/{filename}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"맥패밀리트리 스타일 위젯 생성 완료: {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"맥패밀리트리 스타일 위젯 생성 실패: {e}")
            return None
    
    def create_all_widgets(self) -> Dict[str, Any]:
        """모든 정치인 맥패밀리트리 스타일 위젯 생성"""
        results = {}
        
        for politician_name in self.politicians.keys():
            logger.info(f"맥패밀리트리 스타일 위젯 생성 중: {politician_name}")
            
            widget_file = self.create_radial_network_widget(politician_name)
            
            if widget_file:
                results[politician_name] = {
                    "widget": widget_file,
                    "status": "success"
                }
        
        return results

def main():
    """메인 함수"""
    try:
        # 맥패밀리트리 스타일 시각화 시스템 초기화
        visualizer = MacFamilyTreeStyleVisualizer()
        
        # 모든 정치인 위젯 생성
        logger.info("맥패밀리트리 스타일 시각화 시스템 생성 시작...")
        results = visualizer.create_all_widgets()
        
        # 결과 출력
        print("\n🌳 맥패밀리트리 스타일 시각화 시스템 완성!")
        print(f"📁 출력 디렉토리: {visualizer.output_dir}")
        print("\n📊 생성된 위젯:")
        
        for politician, result in results.items():
            print(f"  - {politician}: {result['widget']}")
        
        print(f"\n🌐 웹에서 보기: {visualizer.output_dir}/widgets/radial_network_정청래.html")
        
    except Exception as e:
        logger.error(f"맥패밀리트리 스타일 시각화 생성 실패: {e}")

if __name__ == "__main__":
    main()

