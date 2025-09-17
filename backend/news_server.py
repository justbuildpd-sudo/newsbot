#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴스 기능이 포함된 간단한 서버
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import requests
from datetime import datetime, timedelta
import time

app = FastAPI(
    title="NewsBot API - News Integration",
    version="2.2.0",
    description="뉴스 기능이 포함된 국회의원 정보 API"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
politicians_data = None
news_cache = {}
last_news_fetch = None
news_fetch_interval = 1800  # 30분

# 네이버 뉴스 API 설정
NAVER_CLIENT_ID = "kXwlSsFmb055ku9rWyx1"
NAVER_CLIENT_SECRET = "JZqw_LTiq_"
NAVER_BASE_URL = "https://openapi.naver.com/v1/search/news.json"

def load_politicians():
    """국회의원 데이터 로드"""
    global politicians_data
    try:
        with open('politicians_data_with_party.json', 'r', encoding='utf-8') as f:
            politicians_data = json.load(f)
        print(f"✅ 국회의원 데이터 로드 완료: {len(politicians_data)}명")
    except Exception as e:
        print(f"❌ 국회의원 데이터 로드 실패: {e}")
        politicians_data = []

def get_news_from_naver(query: str, display: int = 50):
    """네이버 뉴스 API에서 뉴스 가져오기"""
    headers = {
        'X-Naver-Client-Id': NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
    }
    
    params = {
        'query': query,
        'display': display,
        'sort': 'sim'
    }
    
    try:
        response = requests.get(NAVER_BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('items', [])
    except Exception as e:
        print(f"네이버 API 오류: {e}")
        return []

def analyze_politician_mentions(news_items):
    """뉴스에서 정치인 언급 분석"""
    if not politicians_data:
        return []
    
    mentioned_news = []
    
    for news in news_items:
        title = news.get('title', '').replace('<b>', '').replace('</b>', '')
        description = news.get('description', '').replace('<b>', '').replace('</b>', '')
        content = f"{title} {description}"
        
        mentioned_politicians = []
        
        # 정치인 이름 매칭
        for politician in politicians_data:
            name = politician.get('name', '')
            if name and name in content:
                mentioned_politicians.append({
                    'name': name,
                    'party': politician.get('party', '정당정보없음'),
                    'district': politician.get('district', '지역구정보없음')
                })
        
        if mentioned_politicians:
            news['mentioned_politicians'] = mentioned_politicians
            mentioned_news.append(news)
    
    return mentioned_news

@app.get("/")
async def root():
    return {"message": "NewsBot API - 뉴스 기능 포함", "version": "2.2.0"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "data_loaded": politicians_data is not None,
        "politician_count": len(politicians_data) if politicians_data else 0,
        "news_cache_size": len(news_cache),
        "last_news_fetch": last_news_fetch
    }

@app.get("/api/assembly/members")
async def get_assembly_members():
    """국회의원 목록"""
    if not politicians_data:
        load_politicians()
    
    return {
        "success": True,
        "data": politicians_data,
        "count": len(politicians_data)
    }

@app.get("/api/news/with-politicians")
async def get_news_with_politicians():
    """정치인 언급이 포함된 뉴스"""
    global last_news_fetch, news_cache
    
    current_time = time.time()
    
    # 30분마다 새 뉴스 수집
    if not last_news_fetch or (current_time - last_news_fetch) > news_fetch_interval:
        print("🔄 새 뉴스 수집 중...")
        
        # 정치 관련 뉴스 검색
        political_queries = [
            "국회 의원",
            "정치 뉴스",
            "정부 정책",
            "여당 야당"
        ]
        
        all_news = []
        for query in political_queries:
            news_items = get_news_from_naver(query, 20)
            all_news.extend(news_items)
        
        # 중복 제거
        seen_titles = set()
        unique_news = []
        for news in all_news:
            title = news.get('title', '')
            if title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(news)
        
        # 정치인 언급 분석
        mentioned_news = analyze_politician_mentions(unique_news)
        
        news_cache = {
            'news': mentioned_news,
            'total_news': len(unique_news),
            'mentioned_news': len(mentioned_news),
            'fetch_time': datetime.now().isoformat()
        }
        
        last_news_fetch = current_time
        print(f"✅ 뉴스 수집 완료: {len(unique_news)}개 중 {len(mentioned_news)}개에 정치인 언급")
    
    return {
        "success": True,
        "data": news_cache.get('news', []),
        "total_news": news_cache.get('total_news', 0),
        "mentioned_news": news_cache.get('mentioned_news', 0),
        "fetch_time": news_cache.get('fetch_time'),
        "cache_status": "fresh" if last_news_fetch and (current_time - last_news_fetch) < news_fetch_interval else "stale"
    }

@app.get("/api/news/search")
async def search_news(query: str, limit: int = 20):
    """뉴스 검색"""
    news_items = get_news_from_naver(query, limit)
    mentioned_news = analyze_politician_mentions(news_items)
    
    return {
        "success": True,
        "data": mentioned_news,
        "query": query,
        "total": len(mentioned_news)
    }

@app.get("/api/news/politician-mentions")
async def get_politician_mentions():
    """정치인별 언급 통계"""
    if not news_cache.get('news'):
        # 뉴스가 없으면 새로 수집
        await get_news_with_politicians()
    
    mention_counts = {}
    for news in news_cache.get('news', []):
        for politician in news.get('mentioned_politicians', []):
            name = politician['name']
            mention_counts[name] = mention_counts.get(name, 0) + 1
    
    # 언급 횟수 순으로 정렬
    sorted_mentions = sorted(mention_counts.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "success": True,
        "data": dict(sorted_mentions),
        "total_mentions": sum(mention_counts.values())
    }

if __name__ == "__main__":
    print("🚀 뉴스 서버 시작 중...")
    load_politicians()
    uvicorn.run(app, host="0.0.0.0", port=8001)
