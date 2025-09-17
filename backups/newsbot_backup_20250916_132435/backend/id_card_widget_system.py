#!/usr/bin/env python3
"""
신분증 형태 카드 위젯 시스템
차근차근 모든 경우를 상정하고 분석하여 안정적인 시스템 구축
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IDCardWidgetSystem:
    """신분증 형태 카드 위젯 시스템"""
    
    def __init__(self, output_dir: str = "id_card_widgets"):
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
                "position": "국회의원",
                "term": "22대",
                "connectivity_score": 78.2,
                "photo_url": "https://via.placeholder.com/120x150/e74c3c/ffffff?text=김주영",
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
                "position": "국회의원",
                "term": "22대",
                "connectivity_score": 72.8,
                "photo_url": "https://via.placeholder.com/120x150/2ecc71/ffffff?text=신장식",
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
        os.makedirs(f"{self.output_dir}/cards", exist_ok=True)
        os.makedirs(f"{self.output_dir}/pages", exist_ok=True)
        os.makedirs(f"{self.output_dir}/images", exist_ok=True)
    
    def create_id_card_widget(self, politician_name: str) -> str:
        """신분증 형태 카드 위젯 생성"""
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
    <title>{politician['name']} 신분증 카드</title>
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
        
        .connection-item.입법_연결 {{ border-left-color: #FF6B6B; }}
        .connection-item.위원회_연결 {{ border-left-color: #4ECDC4; }}
        .connection-item.정치적_연결 {{ border-left-color: #45B7D1; }}
        .connection-item.지역_연결 {{ border-left-color: #96CEB4; }}
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
        
        @media (max-width: 480px) {{
            .id-card-container {{
                margin: 10px;
                padding: 20px;
            }}
            
            .card-header {{
                flex-direction: column;
                text-align: center;
            }}
            
            .photo-container {{
                margin-right: 0;
                margin-bottom: 15px;
            }}
            
            .connections-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="id-card-container">
        <div class="id-card">
            <div class="card-header">
                <div class="photo-container">
                    <img src="{politician['photo_url']}" alt="{politician['name']}" class="photo" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    <div class="photo-placeholder" style="display: none;">
                        {politician['name'][0]}
                    </div>
                </div>
                <div class="basic-info">
                    <div class="name">{politician['name']}</div>
                    <div class="position">{politician['position']}</div>
                    <div class="term">{politician['term']}</div>
                </div>
            </div>
            
            <div class="card-body">
                <div class="info-row">
                    <div class="info-label">정당</div>
                    <div class="info-value">{politician['party']}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">지역구</div>
                    <div class="info-value">{politician['district']}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">위원회</div>
                    <div class="info-value">{politician['committee']}</div>
                </div>
            </div>
            
            <div class="score-section">
                <div class="score-label">연결성 점수</div>
                <div class="score-value">{politician['connectivity_score']}</div>
                <div class="score-description">네트워크 영향력</div>
            </div>
            
            <div class="connections-section">
                <div class="connections-title">주요 연결</div>
                <div class="connections-grid">
"""
            
            # 연결된 정치인 카드들 추가 (최대 6개)
            for i, conn in enumerate(politician["connections"][:6]):
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
                <div class="card-id">ID: {politician['name'].replace(' ', '').upper()}{politician['connectivity_score']:.0f}</div>
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
            
            # HTML 파일로 저장
            filename = f"card_{politician['name']}.html"
            filepath = f"{self.output_dir}/cards/{filename}"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"신분증 카드 위젯 생성 완료: {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"신분증 카드 위젯 생성 실패: {e}")
            return None
    
    def create_politician_page(self, politician_name: str) -> str:
        """개별 정치인 페이지 생성 (카드 중심)"""
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
    <title>{politician['name']} 정치인 카드</title>
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
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 3em;
            margin-bottom: 15px;
            font-weight: 600;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .card-section {{
            display: flex;
            justify-content: center;
            margin-bottom: 40px;
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
        
        .card-iframe {{
            width: 400px;
            height: 600px;
            border: none;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }}
        
        @media (max-width: 480px) {{
            .card-iframe {{
                width: 100%;
                height: 500px;
            }}
        }}
    </style>
</head>
<body>
    <button class="back-button" onclick="history.back()">← 뒤로가기</button>
    
    <div class="container">
        <div class="header">
            <h1>🏛️ {politician['name']} 정치인 카드</h1>
            <p>신분증 형태의 정치인 정보 카드</p>
        </div>
        
        <div class="card-section">
            <iframe src="cards/card_{politician['name']}.html" class="card-iframe"></iframe>
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
        """모든 정치인 카드 위젯 생성"""
        results = {}
        
        for politician_name in self.politicians.keys():
            logger.info(f"정치인 카드 생성 중: {politician_name}")
            
            # 신분증 카드 위젯 생성
            card_file = self.create_id_card_widget(politician_name)
            
            # 개인 페이지 생성
            page_file = self.create_politician_page(politician_name)
            
            if card_file and page_file:
                results[politician_name] = {
                    "card": card_file,
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
    <title>정치인 신분증 카드 시스템</title>
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
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
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
            text-align: center;
        }
        
        .politician-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }
        
        .card-preview {
            width: 200px;
            height: 300px;
            margin: 0 auto 20px;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .card-preview iframe {
            width: 100%;
            height: 100%;
            border: none;
            transform: scale(0.5);
            transform-origin: top left;
        }
        
        .politician-name {
            font-size: 1.8em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
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
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            margin-bottom: 20px;
            font-size: 14px;
        }
        
        .view-button {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-family: 'SF Pro Display', -apple-system, sans-serif;
            font-size: 1em;
            font-weight: 500;
            cursor: pointer;
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
            <h1>🏛️ 정치인 신분증 카드</h1>
            <p>신분증 형태의 직관적인 정치인 정보 시스템</p>
        </div>
        
        <div class="politicians-grid">
"""
            
            # 각 정치인 카드 추가
            for politician_name, politician_data in self.politicians.items():
                html_content += f"""
            <div class="politician-card" onclick="location.href='pages/page_{politician_name}.html'">
                <div class="card-preview">
                    <iframe src="cards/card_{politician_name}.html"></iframe>
                </div>
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
                    카드 보기
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
        # 신분증 카드 위젯 시스템 초기화
        system = IDCardWidgetSystem()
        
        # 모든 정치인 카드 생성
        logger.info("신분증 카드 위젯 시스템 생성 시작...")
        results = system.create_all_widgets()
        
        # 인덱스 페이지 생성
        logger.info("인덱스 페이지 생성 중...")
        index_file = system.create_index_page()
        
        # 결과 출력
        print("\n🏛️ 신분증 카드 위젯 시스템 완성!")
        print(f"📁 출력 디렉토리: {system.output_dir}")
        print(f"📄 인덱스 페이지: {index_file}")
        print("\n📊 생성된 카드:")
        
        for politician, result in results.items():
            print(f"  - {politician}:")
            print(f"    * 신분증 카드: {result['card']}")
            print(f"    * 개인 페이지: {result['page']}")
        
        print(f"\n🌐 웹에서 보기: {system.output_dir}/index.html")
        
    except Exception as e:
        logger.error(f"카드 시스템 생성 실패: {e}")

if __name__ == "__main__":
    main()
