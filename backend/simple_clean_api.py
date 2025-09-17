#!/usr/bin/env python3
"""
NewsBot 완전 새로운 API 서버 - 정공법 해결
"""

import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NewsBot Clean API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 데이터
politicians_data = []

def load_clean_data():
    """깨끗한 데이터 로드"""
    global politicians_data
    politicians_data = []  # 초기화
    
    # 우선순위 파일들
    files_to_try = [
        'final_298_current_assembly.json',
        'updated_298_current_assembly.json',
        'verified_22nd_assembly_from_csv.json'
    ]
    
    for filename in files_to_try:
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 데이터 검증
                if data and len(data) > 0:
                    first_member = data[0]
                    name = first_member.get('name', '').strip()
                    party = first_member.get('party', '').strip()
                    
                    if name and party:
                        politicians_data = data
                        logger.info(f"✅ 데이터 로드 성공: {filename} - {len(data)}명")
                        logger.info(f"검증 샘플: {name} ({party})")
                        return True
                    else:
                        logger.warning(f"❌ 데이터 품질 문제: {filename}")
                        continue
        except Exception as e:
            logger.error(f"파일 로드 실패: {filename} - {e}")
            continue
    
    # 모든 파일 로드 실패 시 최소 실제 데이터
    logger.warning("모든 파일 로드 실패, 최소 실제 데이터 사용")
    politicians_data = [
        {"name": "강경숙", "party": "조국혁신당", "district": "비례대표", "committee": "교육위원회"},
        {"name": "강대식", "party": "국민의힘", "district": "대구 동구군위군을", "committee": "국방위원회"},
        {"name": "강득구", "party": "더불어민주당", "district": "경기 안양시만안구", "committee": "환경노동위원회"},
        {"name": "강명구", "party": "국민의힘", "district": "경북 구미시을", "committee": "농림축산식품해양수산위원회"},
        {"name": "강민국", "party": "국민의힘", "district": "경남 진주시을", "committee": "정무위원회"},
        {"name": "이재명", "party": "더불어민주당", "district": "경기 성남시분당구을", "committee": "기획재정위원회"},
        {"name": "김기현", "party": "국민의힘", "district": "울산 북구", "committee": "정무위원회"},
        {"name": "정청래", "party": "더불어민주당", "district": "서울 마포구을", "committee": "기획재정위원회"}
    ]
    return False

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 데이터 로드"""
    logger.info("🚀 NewsBot Clean API 서버 시작")
    success = load_clean_data()
    if success:
        logger.info(f"✅ 서버 준비 완료: {len(politicians_data)}명 의원 데이터")
    else:
        logger.warning("⚠️ 파일 로드 실패, 최소 데이터로 서버 시작")

@app.get("/")
async def root():
    """API 서버 상태"""
    return {
        "message": "NewsBot Clean API Server",
        "status": "running",
        "politicians_count": len(politicians_data),
        "sample_member": politicians_data[0] if politicians_data else None
    }

@app.get("/api/assembly/members")
async def get_assembly_members():
    """국회의원 목록 조회"""
    try:
        if not politicians_data:
            return {
                "success": False,
                "error": "의원 데이터가 로드되지 않았습니다"
            }
        
        # 명시적으로 필드 검증
        clean_members = []
        for member in politicians_data:
            clean_member = {
                "name": str(member.get('name', '')).strip(),
                "party": str(member.get('party', '')).strip(),
                "district": str(member.get('district', '')).strip(),
                "committee": str(member.get('committee', '')).strip(),
                "photo_url": str(member.get('photo_url', '')).strip()
            }
            # 이름이 있는 의원만 포함
            if clean_member["name"]:
                clean_members.append(clean_member)
        
        return {
            "success": True,
            "data": clean_members,
            "total_count": len(clean_members),
            "source": "NewsBot Clean API",
            "debug_info": {
                "raw_count": len(politicians_data),
                "clean_count": len(clean_members),
                "first_raw": politicians_data[0] if politicians_data else None,
                "first_clean": clean_members[0] if clean_members else None
            }
        }
    except Exception as e:
        logger.error(f"국회의원 목록 조회 오류: {e}")
        return {
            "success": False,
            "error": f"조회 실패: {str(e)}"
        }

@app.get("/api/assembly/members/{member_name}")
async def get_assembly_member(member_name: str):
    """특정 국회의원 조회"""
    try:
        for member in politicians_data:
            if member.get('name') == member_name:
                return {
                    "success": True,
                    "data": member
                }
        
        return {
            "success": False,
            "error": f"의원 '{member_name}'을 찾을 수 없습니다"
        }
    except Exception as e:
        logger.error(f"의원 조회 오류: {e}")
        return {
            "success": False,
            "error": f"조회 실패: {str(e)}"
        }

@app.post("/api/reload")
async def reload_data():
    """데이터 강제 재로드"""
    try:
        success = load_clean_data()
        return {
            "success": True,
            "message": "데이터 재로드 완료",
            "politicians_count": len(politicians_data),
            "file_load_success": success,
            "sample": politicians_data[0] if politicians_data else None
        }
    except Exception as e:
        logger.error(f"데이터 재로드 오류: {e}")
        return {
            "success": False,
            "error": f"재로드 실패: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
# 강제 배포 트리거
