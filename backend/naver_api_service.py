#!/usr/bin/env python3
"""
3. 네이버 뉴스/트렌드 API - 뉴스 및 트렌드 전용 서비스
- 네이버 뉴스 API
- 네이버 데이터랩 (트렌드)
- 실시간 뉴스
- 검색량 트렌드
"""
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NaverAPIService:
    """네이버 뉴스/트렌드 API 클래스"""
    
    def __init__(self):
        self.news_data = {}
        self.trend_data = {}
        self.load_news_data()
        self.load_trend_data()
    
    def load_news_data(self):
        """뉴스 데이터 로드"""
        # 네이버 뉴스 데이터 파일들
        news_files = [
            'naver_integrated_data.json',  # 통합 데이터
            'naver_news_collected.json',   # 수집된 뉴스
        ]
        
        for filename in news_files:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 데이터 구조에 따라 처리
                if isinstance(data, dict) and 'politicians' in data:
                    # 통합 데이터 형식
                    self.news_data = data.get('politicians', {})
                elif isinstance(data, dict):
                    # 직접 정치인별 뉴스 형식
                    self.news_data = data
                
                logger.info(f"뉴스 데이터 로드 성공: {filename} ({len(self.news_data)}명)")
                break
            except FileNotFoundError:
                continue
        
        if not self.news_data:
            logger.warning("뉴스 데이터 파일을 찾을 수 없음")
    
    def load_trend_data(self):
        """트렌드 데이터 로드"""
        # 트렌드 데이터 파일들
        trend_files = [
            'extended_trend_data.json',    # 확장된 트렌드
            'naver_integrated_data.json',  # 통합 데이터
            'trend_analysis_result.json'   # 분석 결과
        ]
        
        for filename in trend_files:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.trend_data = json.load(f)
                logger.info(f"트렌드 데이터 로드 성공: {filename}")
                break
            except FileNotFoundError:
                continue
        
        if not self.trend_data:
            logger.warning("트렌드 데이터 파일을 찾을 수 없음")
    
    def get_trending_news(self, limit: int = 20) -> List[Dict]:
        """트렌딩 뉴스 조회"""
        all_news = []
        
        for politician_name, politician_data in self.news_data.items():
            # 데이터 구조에 따라 뉴스 추출
            news_list = []
            if isinstance(politician_data, dict):
                news_list = politician_data.get('news', [])
            elif isinstance(politician_data, list):
                news_list = politician_data
            
            for news in news_list:
                news_copy = news.copy()
                news_copy['politician'] = politician_name
                all_news.append(news_copy)
        
        # 최신순 정렬
        all_news.sort(key=lambda x: x.get('pub_date', ''), reverse=True)
        return all_news[:limit]
    
    def get_politician_news(self, politician_name: str) -> Dict:
        """정치인별 뉴스 조회"""
        politician_data = self.news_data.get(politician_name, {})
        
        if not politician_data:
            return {
                'success': False,
                'error': f'{politician_name} 의원의 뉴스를 찾을 수 없습니다'
            }
        
        # 데이터 구조에 따라 뉴스 추출
        news_list = []
        if isinstance(politician_data, dict):
            news_list = politician_data.get('news', [])
        elif isinstance(politician_data, list):
            news_list = politician_data
        
        return {
            'success': True,
            'politician': politician_name,
            'news': news_list,
            'count': len(news_list),
            'source': '네이버 뉴스 API'
        }
    
    def get_trend_chart(self) -> Dict:
        """트렌드 차트 데이터"""
        chart_data = self.trend_data.get('chart_data', {})
        
        if not chart_data:
            return {
                'success': False,
                'error': '트렌드 차트 데이터가 없습니다'
            }
        
        return {
            'success': True,
            'data': chart_data,
            'source': '네이버 데이터랩 API'
        }
    
    def get_trend_ranking(self) -> Dict:
        """트렌드 랭킹"""
        ranking = self.trend_data.get('ranking', [])
        summary = self.trend_data.get('summary', {})
        
        return {
            'success': True,
            'data': {
                'ranking': ranking,
                'summary': summary,
                'generated_at': self.trend_data.get('generated_at', '')
            },
            'source': '네이버 데이터랩 API'
        }
    
    def get_politician_trend(self, politician_name: str) -> Dict:
        """정치인별 트렌드"""
        # 트렌드 데이터에서 해당 정치인 찾기
        ranking = self.trend_data.get('ranking', [])
        
        for item in ranking:
            if item.get('politician') == politician_name:
                return {
                    'success': True,
                    'data': item,
                    'source': '네이버 데이터랩 API'
                }
        
        return {
            'success': False,
            'error': f'{politician_name} 의원의 트렌드 데이터가 없습니다'
        }
    
    def get_statistics(self) -> Dict:
        """뉴스/트렌드 통계"""
        news_stats = {
            'politicians_with_news': len(self.news_data),
            'total_news': 0
        }
        
        for politician_data in self.news_data.values():
            if isinstance(politician_data, dict):
                news_list = politician_data.get('news', [])
            elif isinstance(politician_data, list):
                news_list = politician_data
            else:
                news_list = []
            
            news_stats['total_news'] += len(news_list)
        
        trend_stats = {
            'trend_politicians': len(self.trend_data.get('ranking', [])),
            'trend_period': self.trend_data.get('period', {})
        }
        
        return {
            'news': news_stats,
            'trends': trend_stats
        }

# 전역 인스턴스
naver_api = NaverAPIService()

if __name__ == "__main__":
    # 테스트
    stats = naver_api.get_statistics()
    print("네이버 뉴스/트렌드 API 통계:")
    print(f"뉴스 보유 정치인: {stats['news']['politicians_with_news']}명")
    print(f"총 뉴스: {stats['news']['total_news']}건")
    print(f"트렌드 분석 정치인: {stats['trends']['trend_politicians']}명")
    
    # 트렌드 차트 테스트
    chart = naver_api.get_trend_chart()
    if chart['success']:
        chart_data = chart['data']
        print(f"\\n트렌드 차트: {len(chart_data.get('labels', []))}일, {len(chart_data.get('datasets', []))}명")

