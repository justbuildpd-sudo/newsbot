#!/usr/bin/env python3
"""
실제 데이터 기반 향상된 위젯 생성기
수집한 실제 데이터를 활용하여 동적으로 위젯 생성
"""

import os
import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedWidgetGenerator:
    """실제 데이터 기반 향상된 위젯 생성기"""
    
    def __init__(self, db_path: str = "real_politician_data.db", output_dir: str = "enhanced_widgets"):
        self.db_path = db_path
        self.output_dir = output_dir
        
        # 출력 디렉토리 생성
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/cards", exist_ok=True)
        os.makedirs(f"{self.output_dir}/networks", exist_ok=True)
        os.makedirs(f"{self.output_dir}/pages", exist_ok=True)
        
        # 연결성 색상 정의
        self.connection_colors = {
            "정치적_연결": "#45B7D1",  # 파란색
            "위원회_연결": "#4ECDC4",  # 청록색
            "지역_연결": "#96CEB4",   # 연두색
            "입법_연결": "#FF6B6B",   # 빨간색
            "정책_연결": "#FFEAA7",   # 노란색
            "시간_연결": "#DDA0DD"    # 보라색
        }
    
    def load_politician_data(self, politician_name: str) -> Optional[Dict]:
        """데이터베이스에서 정치인 데이터 로드"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 기본 정보 조회
            cursor.execute('''
                SELECT name, party, district, committee, position, term, photo_url
                FROM politicians 
                WHERE name = ?
            ''', (politician_name,))
            
            politician = cursor.fetchone()
            if not politician:
                return None
            
            # 평가 점수 조회
            cursor.execute('''
                SELECT legislative_score, connectivity_score, news_score, total_score
                FROM evaluation_scores 
                WHERE politician_name = ?
            ''', (politician_name,))
            
            scores = cursor.fetchone()
            
            # 연결 정보 조회
            cursor.execute('''
                SELECT politician2, connection_type, strength, description
                FROM connections 
                WHERE politician1 = ?
                ORDER BY strength DESC
                LIMIT 20
            ''', (politician_name,))
            
            connections = cursor.fetchall()
            
            # 입법 활동 조회
            cursor.execute('''
                SELECT COUNT(*) as total_bills,
                       SUM(CASE WHEN status = '가결' THEN 1 ELSE 0 END) as passed_bills
                FROM bills 
                WHERE proposer_name = ?
            ''', (politician_name,))
            
            legislative_stats = cursor.fetchone()
            
            return {
                'name': politician[0],
                'party': politician[1],
                'district': politician[2],
                'committee': politician[3],
                'position': politician[4],
                'term': politician[5],
                'photo_url': politician[6],
                'legislative_score': scores[0] if scores else 0,
                'connectivity_score': scores[1] if scores else 0,
                'news_score': scores[2] if scores else 0,
                'total_score': scores[3] if scores else 0,
                'connections': [
                    {
                        'name': conn[0],
                        'type': conn[1],
                        'strength': conn[2],
                        'description': conn[3],
                        'level': 1
                    } for conn in connections
                ],
                'legislative_stats': {
                    'total_bills': legislative_stats[0] if legislative_stats else 0,
                    'passed_bills': legislative_stats[1] if legislative_stats else 0,
                    'pass_rate': (legislative_stats[1] / legislative_stats[0] * 100) if legislative_stats and legislative_stats[0] > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"정치인 데이터 로드 실패: {e}")
            return None
        finally:
            conn.close()
    
    def generate_id_card(self, politician_data: Dict) -> str:
        """신분증 형태 카드 생성"""
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{politician_data['name']} 신분증 카드</title>
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
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .id-card-container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 30px;
            max-width: 400px;
            width: 100%;
        }}
        
        .id-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 15px;
            padding: 25px;
            border: 2px solid #dee2e6;
            position: relative;
            overflow: hidden;
        }}
        
        .id-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #3498db, #2ecc71, #e74c3c, #f39c12);
        }}
        
        .card-header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }}
        
        .photo-container {{
            width: 80px;
            height: 100px;
            border-radius: 10px;
            overflow: hidden;
            margin-right: 20px;
            border: 3px solid #3498db;
            background: #ecf0f1;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .photo {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .photo-placeholder {{
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #3498db, #2980b9);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            font-weight: 600;
        }}
        
        .basic-info {{
            flex: 1;
        }}
        
        .name {{
            font-size: 24px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .position {{
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 3px;
        }}
        
        .term {{
            font-size: 12px;
            color: #95a5a6;
            background: #ecf0f1;
            padding: 2px 8px;
            border-radius: 10px;
            display: inline-block;
        }}
        
        .card-body {{
            margin-bottom: 20px;
        }}
        
        .info-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #ecf0f1;
        }}
        
        .info-row:last-child {{
            border-bottom: none;
        }}
        
        .info-label {{
            font-size: 12px;
            color: #7f8c8d;
            font-weight: 500;
            min-width: 60px;
        }}
        
        .info-value {{
            font-size: 13px;
            color: #2c3e50;
            font-weight: 600;
            text-align: right;
            flex: 1;
        }}
        
        .score-section {{
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }}
        
        .score-label {{
            font-size: 12px;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        
        .score-value {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .score-description {{
            font-size: 11px;
            opacity: 0.8;
        }}
        
        .legislative-stats {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        
        .stats-title {{
            font-size: 14px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
            text-align: center;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 18px;
            font-weight: 700;
            color: #3498db;
        }}
        
        .stat-label {{
            font-size: 11px;
            color: #7f8c8d;
        }}
        
        .connections-section {{
            margin-top: 20px;
        }}
        
        .connections-title {{
            font-size: 14px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
            text-align: center;
        }}
        
        .connections-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
        }}
        
        .connection-item {{
            background: white;
            border-radius: 8px;
            padding: 8px;
            border-left: 3px solid;
            font-size: 11px;
            transition: transform 0.2s ease;
        }}
        
        .connection-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        .connection-item.정치적_연결 {{ border-left-color: #45B7D1; }}
        .connection-item.위원회_연결 {{ border-left-color: #4ECDC4; }}
        .connection-item.지역_연결 {{ border-left-color: #96CEB4; }}
        .connection-item.입법_연결 {{ border-left-color: #FF6B6B; }}
        .connection-item.정책_연결 {{ border-left-color: #FFEAA7; }}
        .connection-item.시간_연결 {{ border-left-color: #DDA0DD; }}
        
        .connection-name {{
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 2px;
        }}
        
        .connection-type {{
            color: #7f8c8d;
            font-size: 10px;
        }}
        
        .card-footer {{
            text-align: center;
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #ecf0f1;
        }}
        
        .qr-code {{
            width: 60px;
            height: 60px;
            background: #2c3e50;
            border-radius: 8px;
            margin: 0 auto 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 10px;
            font-weight: 600;
        }}
        
        .card-id {{
            font-size: 10px;
            color: #95a5a6;
            font-family: 'Courier New', monospace;
        }}
    </style>
</head>
<body>
    <div class="id-card-container">
        <div class="id-card">
            <div class="card-header">
                <div class="photo-container">
                    <img src="{politician_data['photo_url']}" alt="{politician_data['name']}" class="photo" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    <div class="photo-placeholder" style="display: none;">
                        {politician_data['name'][0]}
                    </div>
                </div>
                <div class="basic-info">
                    <div class="name">{politician_data['name']}</div>
                    <div class="position">{politician_data['position']}</div>
                    <div class="term">{politician_data['term']}</div>
                </div>
            </div>
            
            <div class="card-body">
                <div class="info-row">
                    <div class="info-label">정당</div>
                    <div class="info-value">{politician_data['party']}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">지역구</div>
                    <div class="info-value">{politician_data['district']}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">위원회</div>
                    <div class="info-value">{politician_data['committee']}</div>
                </div>
            </div>
            
            <div class="score-section">
                <div class="score-label">종합 점수</div>
                <div class="score-value">{politician_data['total_score']:.1f}</div>
                <div class="score-description">입법·연결성·뉴스 종합</div>
            </div>
            
            <div class="legislative-stats">
                <div class="stats-title">입법 활동</div>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value">{politician_data['legislative_stats']['total_bills']}</div>
                        <div class="stat-label">발의 법안</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{politician_data['legislative_stats']['passed_bills']}</div>
                        <div class="stat-label">통과 법안</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{politician_data['legislative_stats']['pass_rate']:.1f}%</div>
                        <div class="stat-label">통과율</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{len(politician_data['connections'])}</div>
                        <div class="stat-label">연결 수</div>
                    </div>
                </div>
            </div>
            
            <div class="connections-section">
                <div class="connections-title">주요 연결</div>
                <div class="connections-grid">
"""
            
            # 연결된 정치인 카드들 추가 (최대 6개)
            for i, conn in enumerate(politician_data["connections"][:6]):
                html_content += f"""
                    <div class="connection-item {conn['type']}">
                        <div class="connection-name">{conn['name']}</div>
                        <div class="connection-type">{conn['description']}</div>
                    </div>
                """
            
            html_content += f"""
                </div>
            </div>
            
            <div class="card-footer">
                <div class="qr-code">
                    QR
                </div>
                <div class="card-id">ID: {politician_data['name'].replace(' ', '').upper()}{politician_data['total_score']:.0f}</div>
            </div>
        </div>
    </div>
    
    <script>
        // 카드 애니메이션
        document.addEventListener('DOMContentLoaded', function() {{
            const card = document.querySelector('.id-card');
            
            // 카드 등장 애니메이션
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {{
                card.style.transition = 'all 0.6s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }}, 100);
            
            // 연결 항목 호버 효과
            const connectionItems = document.querySelectorAll('.connection-item');
            connectionItems.forEach(item => {{
                item.addEventListener('mouseenter', function() {{
                    this.style.transform = 'translateY(-2px) scale(1.02)';
                }});
                
                item.addEventListener('mouseleave', function() {{
                    this.style.transform = 'translateY(0) scale(1)';
                }});
            }});
        }});
    </script>
</body>
</html>
"""
            
            return html_content
            
        except Exception as e:
            logger.error(f"신분증 카드 생성 실패: {e}")
            return None
    
    def generate_network_visualization(self, politician_data: Dict) -> str:
        """네트워크 시각화 생성"""
        try:
            # 연결된 정치인들의 위치 계산 (방사형 배치)
            connections = politician_data["connections"][:12]  # 최대 12개
            positions = self._calculate_network_positions(connections, politician_data["name"])
            
            html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{politician_data['name']} 네트워크 시각화</title>
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
        
        .node-connection {{
            fill: #3498db;
            stroke: #2980b9;
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
        
        .connection-line.정치적_연결 {{ stroke: #45B7D1; }}
        .connection-line.위원회_연결 {{ stroke: #4ECDC4; }}
        .connection-line.지역_연결 {{ stroke: #96CEB4; }}
        .connection-line.입법_연결 {{ stroke: #FF6B6B; }}
        .connection-line.정책_연결 {{ stroke: #FFEAA7; }}
        .connection-line.시간_연결 {{ stroke: #DDA0DD; }}
        
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
    </style>
</head>
<body>
    <div class="network-container">
        <div class="info-panel">
            <div class="info-title">{politician_data['name']}</div>
            <div class="info-detail">
                <span class="info-label">정당:</span>
                <span class="info-value">{politician_data['party']}</span>
            </div>
            <div class="info-detail">
                <span class="info-label">지역구:</span>
                <span class="info-value">{politician_data['district']}</span>
            </div>
            <div class="info-detail">
                <span class="info-label">위원회:</span>
                <span class="info-value">{politician_data['committee']}</span>
            </div>
            <div class="score-badge">종합 점수: {politician_data['total_score']:.1f}</div>
        </div>
        
        <svg class="network-svg" viewBox="0 0 800 600">
"""
            
            # 연결선 그리기
            for pos in positions:
                if pos["name"] != politician_data["name"]:
                    connection_type = pos.get("connection_type", "정치적_연결")
                    html_content += f'''
            <line class="connection-line {connection_type}" 
                  x1="400" y1="300" 
                  x2="{pos['x']}" y2="{pos['y']}">
                <title>{politician_data['name']} → {pos['name']} ({connection_type})</title>
            </line>
'''
            
            # 노드 그리기
            for pos in positions:
                if pos["name"] == politician_data["name"]:
                    # 중심 노드
                    html_content += f'''
            <circle class="node node-center" 
                    cx="400" cy="300" r="25">
                <title>{pos['name']} (중심)</title>
            </circle>
            <text class="node-text" x="400" y="300">{pos['name'][0]}</text>
'''
                else:
                    # 연결 노드
                    html_content += f'''
            <circle class="node node-connection" 
                    cx="{pos['x']}" cy="{pos['y']}" r="15">
                <title>{pos['name']}</title>
            </circle>
            <text class="node-text" x="{pos['x']}" y="{pos['y']}">{pos['name'][0]}</text>
'''
            
            html_content += """
        </svg>
    </div>
    
    <script>
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
    </script>
</body>
</html>
"""
            
            return html_content
            
        except Exception as e:
            logger.error(f"네트워크 시각화 생성 실패: {e}")
            return None
    
    def _calculate_network_positions(self, connections: List[Dict], center_name: str) -> List[Dict]:
        """네트워크 노드 위치 계산"""
        import math
        
        positions = []
        
        # 중심 노드
        positions.append({
            "name": center_name,
            "x": 400,
            "y": 300,
            "is_center": True
        })
        
        # 연결 노드들을 원형으로 배치
        radius = 150
        angle_step = 2 * math.pi / len(connections) if connections else 0
        
        for i, conn in enumerate(connections):
            angle = i * angle_step
            x = 400 + radius * math.cos(angle)
            y = 300 + radius * math.sin(angle)
            positions.append({
                "name": conn["name"],
                "x": x,
                "y": y,
                "connection_type": conn["type"],
                "strength": conn["strength"]
            })
        
        return positions
    
    def generate_all_widgets(self):
        """모든 정치인에 대한 위젯 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 정치인 목록 조회
            cursor.execute('SELECT name FROM politicians ORDER BY name')
            politicians = cursor.fetchall()
            
            logger.info(f"위젯 생성 시작: {len(politicians)}명")
            
            for politician in politicians:
                name = politician[0]
                logger.info(f"위젯 생성 중: {name}")
                
                # 정치인 데이터 로드
                politician_data = self.load_politician_data(name)
                if not politician_data:
                    continue
                
                # 신분증 카드 생성
                card_html = self.generate_id_card(politician_data)
                if card_html:
                    card_file = f"{self.output_dir}/cards/card_{name}.html"
                    with open(card_file, 'w', encoding='utf-8') as f:
                        f.write(card_html)
                    logger.info(f"신분증 카드 생성 완료: {card_file}")
                
                # 네트워크 시각화 생성
                network_html = self.generate_network_visualization(politician_data)
                if network_html:
                    network_file = f"{self.output_dir}/networks/network_{name}.html"
                    with open(network_file, 'w', encoding='utf-8') as f:
                        f.write(network_html)
                    logger.info(f"네트워크 시각화 생성 완료: {network_file}")
            
            logger.info("모든 위젯 생성 완료")
            
        except Exception as e:
            logger.error(f"위젯 생성 실패: {e}")
        finally:
            conn.close()

def main():
    """메인 함수"""
    try:
        # 향상된 위젯 생성기 초기화
        generator = EnhancedWidgetGenerator()
        
        # 모든 위젯 생성
        generator.generate_all_widgets()
        
        print("\n🎨 향상된 위젯 생성 완료!")
        print(f"📁 출력 디렉토리: {generator.output_dir}")
        print("📊 생성된 위젯:")
        print("  - 신분증 카드: cards/")
        print("  - 네트워크 시각화: networks/")
        
    except Exception as e:
        logger.error(f"향상된 위젯 생성 실패: {e}")

if __name__ == "__main__":
    main()

