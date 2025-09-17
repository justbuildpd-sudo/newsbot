#!/usr/bin/env python3
"""
NewsBot 경량 API 서버 - Render 배포 전용
국회의원 데이터와 기본 평가만 제공하는 최소한의 서버
"""

import os
import json
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="NewsBot 경량 API",
    description="국회의원 데이터 및 기본 평가 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 데이터 저장
politicians_data = []

def load_politicians_data():
    """정치인 데이터 로드"""
    global politicians_data
    
    # 여러 경로에서 데이터 파일 찾기
    possible_paths = [
        'politicians_data_with_party.json',
        'data/politicians.json',
        '../politicians_data_with_party.json'
    ]
    
    for path in possible_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                politicians_data = json.load(f)
            logger.info(f"정치인 데이터 로드 성공: {len(politicians_data)}명 ({path})")
            return
        except FileNotFoundError:
            continue
    
    # 데이터 파일이 없으면 샘플 데이터 생성
    politicians_data = [
        {
            "name": "정청래",
            "party": "더불어민주당", 
            "district": "서울 마포구을",
            "committee": "기획재정위원회",
            "id": "sample1"
        },
        {
            "name": "김영배",
            "party": "더불어민주당",
            "district": "서울 강남구갑", 
            "committee": "기획재정위원회",
            "id": "sample2"
        }
    ]
    logger.warning("데이터 파일을 찾을 수 없어 샘플 데이터 사용")

# 서버 시작 시 데이터 로드
load_politicians_data()

@app.get("/")
async def root():
    """루트 페이지"""
    return {
        "message": "NewsBot 경량 API 서버",
        "status": "running",
        "politicians_count": len(politicians_data),
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "politicians_count": len(politicians_data),
        "data_loaded": len(politicians_data) > 0,
        "version": "1.0.0"
    }

@app.get("/api/assembly/members")
async def get_assembly_members():
    """국회의원 목록 조회"""
    try:
        return {
            "success": True,
            "data": politicians_data,
            "total_count": len(politicians_data),
            "source": "NewsBot 경량 API"
        }
    except Exception as e:
        logger.error(f"국회의원 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="국회의원 데이터 조회 실패")

@app.get("/api/assembly/members/{member_id}")
async def get_assembly_member(member_id: str):
    """특정 국회의원 조회"""
    try:
        member = next((p for p in politicians_data if p.get('id') == member_id or p.get('name') == member_id), None)
        
        if member:
            return {
                "success": True,
                "data": member,
                "source": "NewsBot 경량 API"
            }
        else:
            raise HTTPException(status_code=404, detail="국회의원을 찾을 수 없습니다")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"국회의원 상세 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="국회의원 상세 조회 실패")

@app.get("/api/assembly/stats")
async def get_assembly_stats():
    """국회의원 통계"""
    try:
        # 정당별 분포 계산
        party_stats = {}
        for politician in politicians_data:
            party = politician.get('party', '정당정보없음')
            party_stats[party] = party_stats.get(party, 0) + 1
        
        return {
            "success": True,
            "data": {
                "total_politicians": len(politicians_data),
                "party_distribution": party_stats
            },
            "source": "NewsBot 경량 API"
        }
    except Exception as e:
        logger.error(f"통계 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="통계 조회 실패")

@app.get("/api/politicians")
async def get_politicians():
    """정치인 목록 (호환성)"""
    return await get_assembly_members()

@app.get("/api/politicians/featured")
async def get_featured_politicians():
    """주요 정치인 목록"""
    try:
        # 상위 6명만 반환
        featured = politicians_data[:6]
        return {
            "success": True,
            "data": featured,
            "count": len(featured),
            "source": "NewsBot 경량 API"
        }
    except Exception as e:
        logger.error(f"주요 정치인 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="주요 정치인 조회 실패")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 NewsBot 경량 API 서버 시작")
    print(f"📊 정치인 데이터: {len(politicians_data)}명")
    print(f"🌐 서버 주소: http://0.0.0.0:{port}")
    print(f"📖 API 문서: http://0.0.0.0:{port}/docs")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
