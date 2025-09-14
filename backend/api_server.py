from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict
import hashlib
from difflib import SequenceMatcher

app = FastAPI(title="NewsBot API Simple", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
news_cache = {}
politician_data = []

# 정치인 데이터 (하드코딩)
def load_politician_data():
    global politician_data
    politician_data = [
        {
            "id": 1,
            "name": "강득구",
            "party": "더불어민주당",
            "district": "경기 안양시만안구",
            "committee": "환경노동위원회",
            "mention_count": 0,
            "influence_score": 0
        },
        {
            "id": 2,
            "name": "김영주",
            "party": "더불어민주당", 
            "district": "경기 수원시정",
            "committee": "기획재정위원회",
            "mention_count": 0,
            "influence_score": 0
        },
        {
            "id": 3,
            "name": "박정훈",
            "party": "국민의힘",
            "district": "서울 강남구갑",
            "committee": "과학기술정보방송통신위원회",
            "mention_count": 0,
            "influence_score": 0
        }
    ]

# 뉴스 서비스 (단순화)
class SimpleNewsService:
    def __init__(self):
        self.client_id = "kXwlSsFmb055ku9rWyx1"
        self.client_secret = "JZqw_LTiq_"
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        
    def get_news_from_naver(self, query: str, display: int = 10) -> List[Dict]:
        """네이버 뉴스 API에서 뉴스 가져오기"""
        headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }
        
        params = {
            'query': query,
            'display': display,
            'sort': 'sim'
        }
        
        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('items', [])
        except Exception as e:
            print(f"네이버 API 오류: {e}")
            return []
    
    def get_news(self) -> List[Dict]:
        """뉴스 가져오기 (단순화)"""
        global news_cache
        
        # 캐시된 뉴스가 있으면 반환
        if news_cache:
            return list(news_cache.values())
        
        # 새 뉴스 가져오기
        all_news = []
        for keyword in ["단독", "속보"]:
            news_list = self.get_news_from_naver(keyword, 5)
            all_news.extend(news_list)
        
        # 간단한 필터링
        filtered_news = []
        for news in all_news:
            title = news.get('title', '')
            description = news.get('description', '')
            
            # 정치 키워드 체크
            political_keywords = ["대통령", "국회", "의원", "민주당", "국민의힘", "정치"]
            text = f"{title} {description}".lower()
            
            if any(keyword in text for keyword in political_keywords):
                news['id'] = hashlib.md5(news.get('link', '').encode()).hexdigest()[:8]
                news['cached_at'] = datetime.now().isoformat()
                filtered_news.append(news)
                news_cache[news['id']] = news
        
        return filtered_news

# 뉴스 서비스 인스턴스
news_service = SimpleNewsService()

# 앱 시작 시 정치인 데이터 로드
load_politician_data()

# API 엔드포인트
@app.get("/")
async def root():
    return {"message": "NewsBot API Server", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "news_cache_size": len(news_cache),
        "politician_count": len(politician_data)
    }

@app.get("/api/news")
async def get_news():
    """뉴스 목록 조회"""
    try:
        news = news_service.get_news()
        return {
            "success": True,
            "data": news,
            "total_count": len(news)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 가져오기 실패: {str(e)}")

@app.get("/api/news/refresh")
async def refresh_news():
    """뉴스 새로고침"""
    try:
        global news_cache
        news_cache.clear()
        news = news_service.get_news()
        return {
            "success": True,
            "message": "뉴스 새로고침 완료",
            "data": news,
            "total_count": len(news)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 새로고침 실패: {str(e)}")

@app.get("/api/politicians")
async def get_politicians():
    """정치인 목록 조회"""
    try:
        return {
            "success": True,
            "data": politician_data,
            "total_count": len(politician_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 조회 실패: {str(e)}")

@app.get("/api/politicians/ranking")
async def get_politician_ranking():
    """정치인 랭킹 조회"""
    try:
        # 간단한 랭킹 (언급 횟수 기준)
        ranked_politicians = sorted(
            politician_data, 
            key=lambda x: x.get('mention_count', 0), 
            reverse=True
        )[:8]
        
        return {
            "success": True,
            "data": ranked_politicians,
            "total_count": len(ranked_politicians)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 랭킹 조회 실패: {str(e)}")

@app.get("/api/news/content")
async def get_news_content(url: str):
    """뉴스 상세 내용 조회 (단순화)"""
    try:
        return {
            "title": "뉴스 제목",
            "content": "뉴스 내용을 가져오는 중입니다...",
            "images": [],
            "pub_date": "",
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 내용 조회 실패: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
