"""
newsbot.kr Backend API Server
FastAPI 기반 뉴스 분석 플랫폼 백엔드
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="newsbot.kr API",
    description="정치 뉴스 분석 플랫폼 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "newsbot.kr API Server",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "newsbot-kr-api"
    }

@app.get("/api/news")
async def get_news():
    """뉴스 목록 조회 API"""
    # TODO: 실제 뉴스 데이터 조회 로직 구현
    return {
        "message": "뉴스 목록 조회 기능은 구현 예정입니다.",
        "data": []
    }

@app.get("/api/search")
async def search_news(query: str = ""):
    """뉴스 검색 API"""
    # TODO: 실제 검색 로직 구현
    return {
        "message": f"'{query}' 검색 기능은 구현 예정입니다.",
        "query": query,
        "results": []
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
