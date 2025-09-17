#!/usr/bin/env python3
"""
고급 연결성 시각화 API
Pyvis, Plotly, Dash를 활용한 세련된 네트워크 시각화 서비스
"""

import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from advanced_network_visualizer import AdvancedNetworkVisualizer
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="고급 연결성 시각화 API",
    description="Pyvis, Plotly, Dash를 활용한 세련된 정치인 네트워크 시각화",
    version="1.0.0"
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="../"), name="static")

# 시각화 도구 초기화
visualizer = AdvancedNetworkVisualizer()

@app.get("/")
async def root():
    """메인 페이지"""
    return FileResponse("../index.html")

@app.get("/api/enhanced-connectivity/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy", 
        "message": "고급 연결성 시각화 API가 정상 작동 중입니다",
        "tools": ["Pyvis", "Plotly", "Dash"],
        "features": ["대화형 네트워크", "3D 시각화", "한글 폰트 지원"]
    }

@app.get("/api/enhanced-connectivity/pyvis/{politician_name}")
async def get_pyvis_network(politician_name: str):
    """Pyvis 대화형 네트워크 시각화"""
    try:
        html_file = visualizer.create_pyvis_network(politician_name)
        if not html_file:
            raise HTTPException(status_code=404, detail="네트워크 시각화 생성 실패")
        
        return {
            "status": "success",
            "message": f"{politician_name}의 Pyvis 네트워크 시각화가 생성되었습니다",
            "html_file": html_file,
            "view_url": f"/static/{html_file}"
        }
    except Exception as e:
        logger.error(f"Pyvis 네트워크 생성 실패 ({politician_name}): {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/api/enhanced-connectivity/plotly/{politician_name}")
async def get_plotly_network(politician_name: str):
    """Plotly 3D 네트워크 시각화"""
    try:
        fig = visualizer.create_plotly_network(politician_name)
        if not fig:
            raise HTTPException(status_code=404, detail="3D 네트워크 시각화 생성 실패")
        
        # HTML 파일로 저장
        html_file = f"network_3d_{politician_name.replace(' ', '_')}.html"
        fig.write_html(html_file)
        
        return {
            "status": "success",
            "message": f"{politician_name}의 Plotly 3D 네트워크 시각화가 생성되었습니다",
            "html_file": html_file,
            "view_url": f"/static/{html_file}"
        }
    except Exception as e:
        logger.error(f"Plotly 3D 네트워크 생성 실패 ({politician_name}): {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/api/enhanced-connectivity/dash")
async def get_dash_app():
    """Dash 대화형 웹 애플리케이션"""
    try:
        app = visualizer.create_dash_app()
        return {
            "status": "success",
            "message": "Dash 대화형 웹 애플리케이션이 준비되었습니다",
            "dash_url": "http://localhost:8050"
        }
    except Exception as e:
        logger.error(f"Dash 앱 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/api/enhanced-connectivity/visualization/{politician_name}")
async def get_comprehensive_visualization(politician_name: str):
    """종합 시각화 (Pyvis + Plotly)"""
    try:
        # Pyvis 네트워크 생성
        pyvis_file = visualizer.create_pyvis_network(politician_name)
        
        # Plotly 3D 네트워크 생성
        plotly_fig = visualizer.create_plotly_network(politician_name)
        plotly_file = f"network_3d_{politician_name.replace(' ', '_')}.html"
        if plotly_fig:
            plotly_fig.write_html(plotly_file)
        
        return {
            "status": "success",
            "message": f"{politician_name}의 종합 시각화가 생성되었습니다",
            "visualizations": {
                "pyvis_network": {
                    "file": pyvis_file,
                    "view_url": f"/static/{pyvis_file}" if pyvis_file else None,
                    "description": "대화형 네트워크 시각화"
                },
                "plotly_3d": {
                    "file": plotly_file,
                    "view_url": f"/static/{plotly_file}" if plotly_fig else None,
                    "description": "3D 네트워크 시각화"
                }
            },
            "features": {
                "interactive": True,
                "korean_font_support": True,
                "responsive_design": True,
                "multi_level_network": True
            }
        }
    except Exception as e:
        logger.error(f"종합 시각화 생성 실패 ({politician_name}): {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/api/enhanced-connectivity/sample")
async def get_sample_visualization():
    """샘플 시각화 생성"""
    try:
        # 샘플 정치인으로 시각화 생성
        sample_politician = "강대식의원 등 12인"
        
        # Pyvis 네트워크
        pyvis_file = visualizer.create_pyvis_network(sample_politician)
        
        # Plotly 3D 네트워크
        plotly_fig = visualizer.create_plotly_network(sample_politician)
        plotly_file = "network_3d_sample.html"
        if plotly_fig:
            plotly_fig.write_html(plotly_file)
        
        return {
            "status": "success",
            "message": "샘플 시각화가 생성되었습니다",
            "sample_politician": sample_politician,
            "files": {
                "pyvis": pyvis_file,
                "plotly_3d": plotly_file
            },
            "view_urls": {
                "pyvis": f"/static/{pyvis_file}" if pyvis_file else None,
                "plotly_3d": f"/static/{plotly_file}" if plotly_fig else None
            }
        }
    except Exception as e:
        logger.error(f"샘플 시각화 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/api/enhanced-connectivity/features")
async def get_features():
    """지원 기능 목록"""
    return {
        "visualization_tools": {
            "pyvis": {
                "name": "Pyvis",
                "description": "대화형 네트워크 시각화",
                "features": ["드래그 앤 드롭", "줌/팬", "호버 효과", "툴팁"],
                "output": "HTML 파일"
            },
            "plotly": {
                "name": "Plotly",
                "description": "3D 네트워크 시각화",
                "features": ["3D 회전", "인터랙티브", "애니메이션", "반응형"],
                "output": "HTML 파일"
            },
            "dash": {
                "name": "Dash",
                "description": "대화형 웹 애플리케이션",
                "features": ["실시간 업데이트", "다중 탭", "필터링", "통계 대시보드"],
                "output": "웹 앱"
            }
        },
        "korean_support": {
            "fonts": ["Noto Sans KR", "Malgun Gothic", "AppleGothic", "NanumGothic"],
            "encoding": "UTF-8",
            "rendering": "완벽 지원"
        },
        "network_features": {
            "levels": "3단계 (위젯) / 5단계 (보고서)",
            "connection_types": 6,
            "visual_attributes": ["색상", "굵기", "선 스타일"],
            "interactivity": "완전 대화형"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
