#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NewsBot-KR 웹 서비스 (localhost:5000)
기존 newsbot.kr 서버 작업과 연결된 Flask 웹 애플리케이션
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
import requests
import json
import os
import sqlite3
from datetime import datetime
import sys

# 프로젝트 루트 디렉토리 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'newsbot-kr-web-service-2025'

# 기존 서버 연결 설정
BACKEND_API_URL = "http://localhost:8001/api"  # 기존 API 서버
UNIFIED_API_URL = "http://localhost:8000/api"  # 통합 서버
BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')

class NewsBot5000Service:
    """NewsBot localhost:5000 서비스"""
    
    def __init__(self):
        self.backend_api_url = BACKEND_API_URL
        self.unified_api_url = UNIFIED_API_URL
        self.session = requests.Session()
        self.session.timeout = 10
    
    def get_health_status(self):
        """서버 상태 확인"""
        status = {
            "api_server_8001": False,
            "unified_server_8000": False,
            "web_service_5000": True
        }
        
        try:
            response = self.session.get(f"{self.backend_api_url}/health")
            if response.status_code == 200:
                status["api_server_8001"] = True
        except:
            pass
        
        try:
            response = self.session.get(f"{self.unified_api_url}/health")
            if response.status_code == 200:
                status["unified_server_8000"] = True
        except:
            pass
        
        return status
    
    def get_politicians_data(self, limit=50):
        """국회의원 데이터 조회 (기존 API 연동)"""
        try:
            # 먼저 기존 API 서버에서 조회
            response = self.session.get(f"{self.backend_api_url}/politicians/featured", 
                                      params={"limit": limit})
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", [])
        except:
            pass
        
        try:
            # 백업으로 통합 서버에서 조회
            response = self.session.get(f"{self.unified_api_url}/politicians", 
                                      params={"limit": limit})
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", [])
        except:
            pass
        
        return []
    
    def get_news_data(self, limit=20):
        """뉴스 데이터 조회 (기존 API 연동)"""
        try:
            response = self.session.get(f"{self.backend_api_url}/news/with-politicians")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    news_list = data.get("data", [])
                    return news_list[:limit]
        except:
            pass
        
        return []
    
    def get_assembly_stats(self):
        """국회의원 통계 조회"""
        try:
            response = self.session.get(f"{self.backend_api_url}/assembly/statistics")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", {})
        except:
            pass
        
        return {}
    
    def get_politician_rankings(self, limit=10):
        """정치인 랭킹 조회 (통합 서버)"""
        try:
            response = self.session.get(f"{self.unified_api_url}/evaluation/ranking", 
                                      params={"limit": limit})
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", {}).get("politicians", [])
        except:
            pass
        
        return []
    
    def search_politicians(self, query):
        """정치인 검색"""
        try:
            response = self.session.get(f"{self.backend_api_url}/assembly/search", 
                                      params={"query": query})
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", [])
        except:
            pass
        
        return []
    
    def get_politician_detail(self, name):
        """정치인 상세 정보 조회"""
        try:
            # 기존 API에서 정치인 정보 조회
            response = self.session.get(f"{self.backend_api_url}/politicians")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    politicians = data.get("data", [])
                    for politician in politicians:
                        if (politician.get("name") == name or 
                            politician.get("naas_nm") == name):
                            return politician
        except:
            pass
        
        # 기본 정보 반환
        return {
            "name": name,
            "party": "정당정보없음",
            "district": "지역구 정보 없음",
            "committee": "위원회 정보 없음"
        }

# 서비스 인스턴스 생성
service = NewsBot5000Service()

@app.route('/')
def index():
    """메인 페이지"""
    # 서버 상태 확인
    health_status = service.get_health_status()
    
    # 주요 정치인 데이터
    politicians = service.get_politicians_data(limit=6)
    
    # 뉴스 데이터
    news = service.get_news_data(limit=5)
    
    # 통계 데이터
    stats = service.get_assembly_stats()
    
    return render_template('index.html',
                         health_status=health_status,
                         politicians=politicians,
                         news=news,
                         stats=stats,
                         current_time=datetime.now())

@app.route('/politicians')
def politicians():
    """국회의원 목록 페이지"""
    page = request.args.get('page', 1, type=int)
    limit = 20
    
    politicians_data = service.get_politicians_data(limit=limit * page)
    
    # 페이지네이션 계산
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_politicians = politicians_data[start_idx:end_idx]
    
    total_pages = max(1, (len(politicians_data) + limit - 1) // limit)
    
    return render_template('politicians.html',
                         politicians=paginated_politicians,
                         page=page,
                         total_pages=total_pages,
                         total_count=len(politicians_data))

@app.route('/rankings')
def rankings():
    """정치인 랭킹 페이지"""
    rankings_data = service.get_politician_rankings(limit=20)
    
    return render_template('rankings.html',
                         rankings=rankings_data)

@app.route('/news')
def news():
    """뉴스 페이지"""
    news_data = service.get_news_data(limit=30)
    
    return render_template('news.html',
                         news=news_data)

@app.route('/search')
def search():
    """검색 페이지"""
    query = request.args.get('q', '')
    results = []
    
    if query and len(query.strip()) >= 2:
        results = service.search_politicians(query.strip())
    
    return render_template('search.html',
                         query=query,
                         results=results)

@app.route('/politician/<politician_name>')
def politician_detail(politician_name):
    """정치인 상세 분석 페이지"""
    # 정치인 기본 정보 조회
    politician_data = service.get_politician_detail(politician_name)
    
    return render_template('politician_detail.html',
                         politician_name=politician_name,
                         politician_data=politician_data)

@app.route('/widgets/id-card/<politician_name>')
def widget_id_card(politician_name):
    """신분증 카드 위젯"""
    return redirect(f'/static/id_card_widgets/cards/card_{politician_name}.html')

@app.route('/widgets/family-tree/<politician_name>')
def widget_family_tree(politician_name):
    """맥패밀리트리 위젯"""
    return redirect(f'/static/mac_family_tree_widgets/widgets/radial_network_{politician_name}.html')

@app.route('/widgets/panel/<politician_name>')
def widget_panel(politician_name):
    """세련된 패널 위젯"""
    return redirect(f'/static/sophisticated_panels/widgets/sophisticated_panel_{politician_name}.html')

@app.route('/status')
def status():
    """시스템 상태 페이지"""
    health_status = service.get_health_status()
    stats = service.get_assembly_stats()
    
    return render_template('status.html',
                         health_status=health_status,
                         stats=stats,
                         current_time=datetime.now())

# API 엔드포인트들 (기존 서버 프록시)
@app.route('/api/health')
def api_health():
    """서버 상태 확인 API"""
    health_status = service.get_health_status()
    
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'NewsBot-KR Web Service (Port 5000)',
        'connected_services': health_status,
        'version': '1.0.0'
    })

@app.route('/api/politicians')
def api_politicians():
    """국회의원 API (프록시)"""
    limit = request.args.get('limit', 50, type=int)
    politicians_data = service.get_politicians_data(limit=limit)
    
    return jsonify({
        'success': True,
        'data': politicians_data,
        'count': len(politicians_data),
        'source': 'NewsBot Web Service (Port 5000)'
    })

@app.route('/api/news')
def api_news():
    """뉴스 API (프록시)"""
    limit = request.args.get('limit', 20, type=int)
    news_data = service.get_news_data(limit=limit)
    
    return jsonify({
        'success': True,
        'data': news_data,
        'count': len(news_data),
        'source': 'NewsBot Web Service (Port 5000)'
    })

@app.route('/api/rankings')
def api_rankings():
    """랭킹 API (프록시)"""
    limit = request.args.get('limit', 10, type=int)
    rankings_data = service.get_politician_rankings(limit=limit)
    
    return jsonify({
        'success': True,
        'data': rankings_data,
        'count': len(rankings_data),
        'source': 'NewsBot Web Service (Port 5000)'
    })

@app.route('/api/search')
def api_search():
    """검색 API (프록시)"""
    query = request.args.get('q', '')
    
    if not query or len(query.strip()) < 2:
        return jsonify({
            'success': False,
            'error': '검색어는 2글자 이상이어야 합니다',
            'data': []
        })
    
    results = service.search_politicians(query.strip())
    
    return jsonify({
        'success': True,
        'data': results,
        'count': len(results),
        'query': query,
        'source': 'NewsBot Web Service (Port 5000)'
    })

@app.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 에러 핸들러"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    print("🚀 NewsBot-KR 웹 서비스 시작 (Port 5000)")
    print("🔗 기존 서버 연결:")
    print(f"   - API 서버 (8001): {BACKEND_API_URL}")
    print(f"   - 통합 서버 (8000): {UNIFIED_API_URL}")
    print("📍 웹 서비스 URL: http://localhost:5000")
    
    # 서버 상태 확인
    health_status = service.get_health_status()
    print("🏥 서버 상태:")
    for server, status in health_status.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {server}: {'연결됨' if status else '연결 안됨'}")
    
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)