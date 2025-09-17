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
    
    # 여러 경로에서 데이터 파일 찾기 (사진 URL 포함 데이터 우선)
    possible_paths = [
        '../22nd_assembly_members_300.json',
        '22nd_assembly_members_300.json',
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
    
    # 데이터 파일이 없으면 샘플 데이터 생성 (사진 URL 포함)
    politicians_data = [
        {
            "name": "정청래",
            "party": "더불어민주당", 
            "district": "서울 마포구을",
            "committee": "기획재정위원회",
            "id": "sample1",
            "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/sample1.jpg"
        },
        {
            "name": "김영배", 
            "party": "더불어민주당",
            "district": "서울 강남구갑",
            "committee": "기획재정위원회", 
            "id": "sample2",
            "photo_url": "https://www.assembly.go.kr/static/portal/img/openassm/new/sample2.jpg"
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

@app.get("/api/bills/scores")
async def get_bill_scores():
    """발의안 점수 (샘플 데이터)"""
    try:
        # 정치인별 발의안 점수 생성
        bill_scores = {}
        for politician in politicians_data:
            name = politician.get('name') or politician.get('naas_nm', '')
            if name:
                # 해시 기반 가상 점수 생성
                hash_val = hash(name) % 100
                bill_scores[name] = {
                    "main_proposals": (hash_val % 20) + 1,
                    "co_proposals": (hash_val % 30) + 5, 
                    "total_bills": (hash_val % 50) + 6,
                    "success_rate": round((hash_val % 80 + 20) / 100, 2)
                }
        
        return {
            "success": True,
            "data": bill_scores,
            "count": len(bill_scores),
            "source": "NewsBot 경량 API (샘플 데이터)"
        }
    except Exception as e:
        logger.error(f"발의안 점수 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="발의안 점수 조회 실패")

@app.get("/api/bills/politician/{politician_name}")
async def get_politician_bills(politician_name: str):
    """특정 정치인의 발의안 목록"""
    try:
        # 해당 정치인 찾기
        politician = next((p for p in politicians_data 
                         if p.get('name') == politician_name or p.get('naas_nm') == politician_name), None)
        
        if not politician:
            raise HTTPException(status_code=404, detail="정치인을 찾을 수 없습니다")
        
        # 샘플 발의안 데이터 생성
        hash_val = hash(politician_name)
        bills = []
        for i in range((hash_val % 5) + 1):
            bills.append({
                "bill_id": f"22{hash_val % 9999:04d}{i+1:02d}",
                "title": f"{politician_name} 의원 대표발의 법안 {i+1}",
                "status": ["발의", "심사중", "통과", "폐기"][i % 4],
                "date": "2024-09-01",
                "type": "주발의" if i == 0 else "공동발의"
            })
        
        return {
            "success": True,
            "data": {
                "politician": politician_name,
                "bills": bills,
                "total_count": len(bills)
            },
            "source": "NewsBot 경량 API (샘플 데이터)"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"정치인 발의안 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="발의안 조회 실패")

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
