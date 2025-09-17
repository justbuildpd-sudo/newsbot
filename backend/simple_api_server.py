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
from datetime import datetime, timedelta

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
bills_data = {}

def load_bills_data():
    """발의안 데이터 로드"""
    global bills_data
    
    # 발의안 데이터 파일 찾기 (개선된 데이터 우선)
    possible_paths = [
        'enhanced_bills_data_22nd.json',
        'bills_data_22nd.json',
        '../enhanced_bills_data_22nd.json',
        '../bills_data_22nd.json',
        './backend/enhanced_bills_data_22nd.json',
        './backend/bills_data_22nd.json'
    ]
    
    for path in possible_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                bills_data = json.load(f)
            logger.info(f"발의안 데이터 로드 성공: {len(bills_data)}명 ({path})")
            return
        except FileNotFoundError:
            continue
    
    logger.warning("발의안 데이터 파일을 찾을 수 없음")

def load_politicians_data():
    """정치인 데이터 로드"""
    global politicians_data
    
    # 여러 경로에서 데이터 파일 찾기 (사진 URL 포함 데이터 우선)
    possible_paths = [
        '22nd_assembly_members_300.json',  # 백엔드 폴더 내
        '../22nd_assembly_members_300.json',  # 상위 폴더
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
load_bills_data()

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
    """발의안 점수 (개선된 실제 데이터 기반)"""
    try:
        # 개선된 발의안 데이터에서 점수 계산
        bill_scores = {}
        for name, bills in bills_data.items():
            if bills:
                # 주발의자인 경우 (공동발의자가 있는 경우)
                main_proposals = sum(1 for bill in bills if len(bill.get('co_proposers', [])) > 0)
                # 공동발의 (주발의가 아닌 경우)
                co_proposals = len(bills) - main_proposals
                total_bills = len(bills)
                
                # 통과율 계산 (본회의 통과, 정부이송 포함)
                passed_bills = sum(1 for bill in bills 
                                 if bill.get('status') in ['본회의 통과', '정부이송', '공포'])
                success_rate = round(passed_bills / total_bills, 2) if total_bills > 0 else 0
                
                # 최근 활동 점수 (최근 3개월 내 발의안)
                recent_bills = sum(1 for bill in bills 
                                 if is_recent_bill(bill.get('propose_date', '')))
                
                bill_scores[name] = {
                    "main_proposals": main_proposals,
                    "co_proposals": co_proposals,
                    "total_bills": total_bills,
                    "success_rate": success_rate,
                    "recent_activity": recent_bills
                }
        
        return {
            "success": True,
            "data": bill_scores,
            "count": len(bill_scores),
            "source": "NewsBot 경량 API (개선된 발의안 데이터)",
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"발의안 점수 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="발의안 점수 조회 실패")

def is_recent_bill(propose_date):
    """최근 3개월 내 발의안인지 확인"""
    try:
        if not propose_date:
            return False
        bill_date = datetime.strptime(propose_date, '%Y-%m-%d')
        three_months_ago = datetime.now() - timedelta(days=90)
        return bill_date >= three_months_ago
    except:
        return False

@app.get("/api/bills/politician/{politician_name}")
async def get_politician_bills(politician_name: str):
    """특정 정치인의 발의안 목록 (개선된 데이터)"""
    try:
        # 발의안 데이터에서 해당 정치인 찾기
        if politician_name not in bills_data:
            raise HTTPException(status_code=404, detail="해당 정치인의 발의안을 찾을 수 없습니다")
        
        bills = bills_data[politician_name]
        
        # 발의안을 최신순으로 정렬
        sorted_bills = sorted(bills, key=lambda x: x.get('propose_date', ''), reverse=True)
        
        # 통계 계산
        stats = {
            "total_bills": len(bills),
            "main_proposals": sum(1 for bill in bills if len(bill.get('co_proposers', [])) > 0),
            "recent_bills": sum(1 for bill in bills if is_recent_bill(bill.get('propose_date', ''))),
            "passed_bills": sum(1 for bill in bills 
                              if bill.get('status') in ['본회의 통과', '정부이송', '공포']),
            "committees": list(set(bill.get('committee', '') for bill in bills if bill.get('committee')))
        }
        
        return {
            "success": True,
            "data": {
                "politician": politician_name,
                "bills": sorted_bills,
                "statistics": stats,
                "total_count": len(bills)
            },
            "source": "NewsBot 경량 API (개선된 발의안 데이터)",
            "last_updated": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"정치인 발의안 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="발의안 조회 실패")

@app.get("/api/bills/recent")
async def get_recent_bills(limit: int = 20):
    """최근 발의안 목록"""
    try:
        all_bills = []
        
        # 모든 의원의 발의안 수집
        for politician_name, bills in bills_data.items():
            for bill in bills:
                bill_copy = bill.copy()
                bill_copy['politician'] = politician_name
                all_bills.append(bill_copy)
        
        # 최신순으로 정렬
        sorted_bills = sorted(all_bills, 
                            key=lambda x: x.get('propose_date', ''), 
                            reverse=True)[:limit]
        
        return {
            "success": True,
            "data": sorted_bills,
            "total_count": len(sorted_bills),
            "source": "NewsBot 경량 API (개선된 발의안 데이터)"
        }
    except Exception as e:
        logger.error(f"최근 발의안 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="최근 발의안 조회 실패")

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
