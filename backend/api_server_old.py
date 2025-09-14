from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from news_service import NewsService
from politician_service import politician_service
from politician_analyzer import politician_analyzer
from rate_limiter import rate_limiter
from monitoring import system_monitor
from database import db
import json
import time
from datetime import datetime

app = FastAPI(title="NewsBot API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 뉴스 서비스 인스턴스
news_service = NewsService()

# Rate Limiting 및 모니터링 미들웨어
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    start_time = time.time()
    
    # 클라이언트 IP 추출
    client_ip = request.client.host
    if request.headers.get("x-forwarded-for"):
        client_ip = request.headers.get("x-forwarded-for").split(",")[0].strip()
    
    # Rate Limiting 확인
    is_allowed, message = rate_limiter.is_allowed(client_ip)
    
    if not is_allowed:
        # 보안 이벤트 로깅
        system_monitor.log_security_event("rate_limit_exceeded", {
            "ip": client_ip,
            "path": request.url.path,
            "user_agent": request.headers.get("user-agent", "")
        })
        
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": "Rate limit exceeded",
                "message": message,
                "retry_after": 60
            }
        )
    
    # 요청 처리
    response = await call_next(request)
    
    # 응답 시간 기록
    response_time = time.time() - start_time
    system_monitor.record_request(response_time, response.status_code)
    
    return response

@app.get("/")
async def root():
    return {"message": "NewsBot API Server", "status": "running"}

@app.get("/api/news")
async def get_news():
    """정치 관련 뉴스 가져오기"""
    try:
        news = news_service.get_cached_news()
        return {
            "success": True,
            "data": news,
            "count": len(news),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 가져오기 실패: {str(e)}")

@app.get("/api/news/refresh")
async def refresh_news():
    """뉴스 새로고침"""
    try:
        # 캐시 초기화하고 새로운 뉴스 가져오기
        news_service.news_cache = {}
        news = news_service.get_political_news()
        
        # 캐시에 저장
        for article in news:
            news_id = hashlib.md5(article['title'].encode()).hexdigest()
            news_service.news_cache[news_id] = article
        
        return {
            "success": True,
            "data": news,
            "count": len(news),
            "message": "뉴스가 새로고침되었습니다",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 새로고침 실패: {str(e)}")

@app.get("/api/news/stats")
async def get_news_stats():
    """뉴스 통계 정보"""
    try:
        news = news_service.get_cached_news()
        
        # 키워드별 통계
        keyword_stats = {}
        for article in news:
            for keyword in news_service.political_keywords:
                if keyword in article['title'].lower():
                    keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1
        
        return {
            "success": True,
            "stats": {
                "total_news": len(news),
                "keyword_stats": keyword_stats,
                "last_cleanup": news_service.last_cleanup.isoformat(),
                "next_cleanup": (news_service.last_cleanup + news_service.cleanup_interval).isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 가져오기 실패: {str(e)}")

@app.get("/api/news/content")
async def get_news_content(url: str):
    """뉴스 기사 전문 가져오기"""
    try:
        content = news_service.get_news_content(url)
        return {
            "success": True,
            "data": content,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 내용 가져오기 실패: {str(e)}")

@app.get("/api/health")
async def health_check():
    """서버 상태 확인"""
    stats = system_monitor.get_system_stats()
    alerts = system_monitor.check_alerts()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "news_cache_size": len(news_service.news_cache),
        "system_stats": stats,
        "alerts": alerts
    }

@app.get("/api/monitoring/stats")
async def get_monitoring_stats():
    """모니터링 통계 확인"""
    stats = system_monitor.get_system_stats()
    alerts = system_monitor.check_alerts()
    recent_errors = system_monitor.get_recent_errors()
    
    return {
        "success": True,
        "data": {
            "system_stats": stats,
            "alerts": alerts,
            "recent_errors": recent_errors
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/rate-limit/stats")
async def get_rate_limit_stats():
    """Rate Limiting 통계 확인"""
    stats = rate_limiter.get_stats()
    return {
        "success": True,
        "data": stats,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/rate-limit/reset")
async def reset_rate_limits():
    """Rate Limiting 초기화 (관리자용)"""
    # 실제 운영에서는 인증이 필요
    rate_limiter.blocked_ips.clear()
    rate_limiter.ip_requests.clear()
    return {
        "success": True,
        "message": "Rate limits have been reset",
        "timestamp": datetime.now().isoformat()
    }

# 정치인 관련 API 엔드포인트
@app.get("/api/politicians")
async def get_politicians():
    """모든 정치인 목록을 반환합니다."""
    try:
        politicians = politician_service.get_all_politicians()
        return {
            "success": True,
            "data": politicians,
            "total_count": len(politicians)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 목록 조회 오류: {str(e)}")

@app.get("/api/politicians/featured")
async def get_featured_politicians(limit: int = 6):
    """주요 정치인 목록을 반환합니다."""
    try:
        politicians = politician_service.get_featured_politicians(limit)
        return {
            "success": True,
            "data": politicians,
            "count": len(politicians)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"주요 정치인 조회 오류: {str(e)}")

@app.get("/api/politicians/{politician_id}")
async def get_politician_by_id(politician_id: int):
    """특정 정치인 정보를 반환합니다."""
    try:
        politician = politician_service.get_politician_by_id(politician_id)
        if not politician:
            raise HTTPException(status_code=404, detail="정치인을 찾을 수 없습니다")
        
        return {
            "success": True,
            "data": politician
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 조회 오류: {str(e)}")

@app.get("/api/politicians/search")
async def search_politicians(q: str):
    """정치인을 검색합니다."""
    try:
        if not q or len(q.strip()) < 2:
            raise HTTPException(status_code=400, detail="검색어는 2글자 이상이어야 합니다")
        
        politicians = politician_service.search_politicians(q.strip())
        return {
            "success": True,
            "data": politicians,
            "query": q,
            "count": len(politicians)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 검색 오류: {str(e)}")

@app.get("/api/politicians/party/{party}")
async def get_politicians_by_party(party: str):
    """정당별 정치인 목록을 반환합니다."""
    try:
        politicians = politician_service.get_politicians_by_party(party)
        return {
            "success": True,
            "data": politicians,
            "party": party,
            "count": len(politicians)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정당별 정치인 조회 오류: {str(e)}")

@app.get("/api/politicians/stats")
async def get_politician_stats():
    """정치인 통계 정보를 반환합니다."""
    try:
        stats = politician_service.get_politician_summary()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 통계 조회 오류: {str(e)}")

# 정치인 랭킹 관련 API 엔드포인트
@app.get("/api/politicians/ranking")
async def get_politician_ranking(limit: int = 8):
    """뉴스 언급 수 기준 정치인 랭킹을 반환합니다."""
    try:
        # 최신 뉴스 데이터 가져오기
        news_data = news_service.get_news()
        
        # 정치인 언급 분석
        top_politicians = politician_analyzer.get_top_politicians(news_data, limit)
        
        return {
            "success": True,
            "data": top_politicians,
            "count": len(top_politicians),
            "analysis_time": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 랭킹 조회 오류: {str(e)}")

@app.get("/api/politicians/ranking/refresh")
async def refresh_politician_ranking(limit: int = 8):
    """정치인 랭킹을 새로고침합니다."""
    try:
        # 뉴스 데이터 새로고침
        await news_service.refresh_news()
        news_data = news_service.get_news()
        
        # 정치인 언급 분석
        top_politicians = politician_analyzer.get_top_politicians(news_data, limit)
        
        return {
            "success": True,
            "data": top_politicians,
            "count": len(top_politicians),
            "message": "정치인 랭킹이 새로고침되었습니다",
            "analysis_time": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 랭킹 새로고침 오류: {str(e)}")

@app.get("/api/politicians/ranking/stats")
async def get_ranking_stats():
    """정치인 랭킹 분석 통계를 반환합니다."""
    try:
        stats = politician_analyzer.get_politician_ranking_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"랭킹 통계 조회 오류: {str(e)}")

@app.post("/api/politicians/init")
async def initialize_politicians():
    """정치인 데이터 초기화"""
    try:
        # 정치인 서비스 재초기화
        politician_service.load_politicians()
        return {"success": True, "message": "정치인 데이터 초기화 완료"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"정치인 데이터 초기화 실패: {str(e)}")

if __name__ == "__main__":
    import hashlib  # news_service에서 사용
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
