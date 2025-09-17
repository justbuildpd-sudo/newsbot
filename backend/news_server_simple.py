#!/usr/bin/env python3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import requests
import time

app = FastAPI(title="NewsBot Simple API", version="1.0.0")

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

def load_politicians():
    global politicians_data
    try:
        with open('politicians_data_with_party.json', 'r', encoding='utf-8') as f:
            politicians_data = json.load(f)
        print(f"✅ 정치인 데이터 로드: {len(politicians_data)}명")
    except Exception as e:
        print(f"❌ 데이터 로드 실패: {e}")
        politicians_data = []

def get_news_from_naver(query, display=20):
    headers = {
        'X-Naver-Client-Id': "kXwlSsFmb055ku9rWyx1",
        'X-Naver-Client-Secret': "JZqw_LTiq_"
    }
    params = {'query': query, 'display': display, 'sort': 'sim'}
    
    try:
        response = requests.get("https://openapi.naver.com/v1/search/news.json", 
                              headers=headers, params=params)
        response.raise_for_status()
        return response.json().get('items', [])
    except Exception as e:
        print(f"뉴스 API 오류: {e}")
        return []

def analyze_mentions(news_items):
    if not politicians_data:
        return []
    
    mentioned_news = []
    for news in news_items:
        title = news.get('title', '').replace('<b>', '').replace('</b>', '')
        description = news.get('description', '').replace('<b>', '').replace('</b>', '')
        content = f"{title} {description}"
        
        mentioned_politicians = []
        for politician in politicians_data:
            name = politician.get('name', '')
            if name and name in content:
                mentioned_politicians.append({
                    'name': name,
                    'party': politician.get('party', '정당정보없음')
                })
        
        if mentioned_politicians:
            news['mentioned_politicians'] = mentioned_politicians
            mentioned_news.append(news)
    
    return mentioned_news

@app.get("/")
def root():
    return {"message": "NewsBot Simple API", "status": "running"}

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "politician_count": len(politicians_data) if politicians_data else 0,
        "news_cache_size": len(news_cache)
    }

@app.get("/api/assembly/members")
def get_members():
    return {
        "success": True,
        "data": politicians_data,
        "count": len(politicians_data) if politicians_data else 0
    }

@app.get("/api/news/with-politicians")
def get_news():
    global last_news_fetch, news_cache
    
    current_time = time.time()
    
    if not last_news_fetch or (current_time - last_news_fetch) > 1800:  # 30분
        print("🔄 새 뉴스 수집 중...")
        
        queries = ["국회 의원", "정치 뉴스", "정부 정책"]
        all_news = []
        
        for query in queries:
            news_items = get_news_from_naver(query, 15)
            all_news.extend(news_items)
        
        # 중복 제거
        seen_titles = set()
        unique_news = []
        for news in all_news:
            title = news.get('title', '')
            if title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(news)
        
        mentioned_news = analyze_mentions(unique_news)
        
        news_cache = {
            'news': mentioned_news,
            'total_news': len(unique_news),
            'mentioned_news': len(mentioned_news),
            'fetch_time': time.time()
        }
        
        last_news_fetch = current_time
        print(f"✅ 뉴스 수집 완료: {len(unique_news)}개 중 {len(mentioned_news)}개에 정치인 언급")
    
    return {
        "success": True,
        "data": news_cache.get('news', []),
        "total_news": news_cache.get('total_news', 0),
        "mentioned_news": news_cache.get('mentioned_news', 0)
    }

if __name__ == "__main__":
    print("🚀 NewsBot Simple Server 시작 중...")
    load_politicians()
    uvicorn.run(app, host="0.0.0.0", port=8001)
