#!/usr/bin/env python3
"""
NewsBot 성능 최적화 시스템
데이터 로딩 속도 개선 및 캐싱 구현
"""

import json
import time
import asyncio
from datetime import datetime, timedelta
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = {}  # Time To Live
        self.default_ttl = 300  # 5분
        
        # 데이터 사전 로드
        self.preload_data()
    
    def preload_data(self):
        """서버 시작 시 모든 데이터 사전 로드"""
        start_time = time.time()
        
        try:
            # 1. 정치인 데이터 로드
            self.politicians_data = self.load_json_file([
                '22nd_assembly_members_300.json',
                '../22nd_assembly_members_300.json'
            ])
            
            # 2. 발의안 데이터 로드
            self.bills_data = self.load_json_file([
                'enhanced_bills_data_22nd.json',
                'bills_data_22nd.json',
                '../enhanced_bills_data_22nd.json'
            ])
            
            # 3. 뉴스 데이터 로드
            self.news_data = self.load_json_file([
                'naver_news_collected.json',
                '../naver_news_collected.json'
            ])
            
            # 4. 트렌드 데이터 로드
            self.trend_data = self.load_json_file([
                'naver_integrated_data.json',
                '../naver_integrated_data.json'
            ])
            
            load_time = time.time() - start_time
            logger.info(f"데이터 사전 로드 완료: {load_time:.2f}초")
            
            # 5. 캐시 데이터 생성
            self.generate_cache()
            
        except Exception as e:
            logger.error(f"데이터 사전 로드 오류: {e}")
    
    def load_json_file(self, possible_paths):
        """JSON 파일 로드 (여러 경로 시도)"""
        for path in possible_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"파일 로드 성공: {path}")
                return data
            except FileNotFoundError:
                continue
        
        logger.warning(f"파일을 찾을 수 없음: {possible_paths}")
        return {} if isinstance(possible_paths[0], str) and 'json' in possible_paths[0] else []
    
    def generate_cache(self):
        """자주 사용되는 데이터 캐시 생성"""
        try:
            # 1. 정치인 목록 캐시 (경량화)
            if self.politicians_data:
                lightweight_politicians = []
                for politician in self.politicians_data:
                    lightweight_politicians.append({
                        'name': politician.get('naas_nm', ''),
                        'party': politician.get('party_name', '무소속'),
                        'district': politician.get('district', ''),
                        'photo_url': politician.get('photo_url', ''),
                        'committee': politician.get('committee', '')
                    })
                
                self.set_cache('politicians_lightweight', lightweight_politicians, ttl=3600)  # 1시간
            
            # 2. 발의안 점수 캐시 (미리 계산)
            if self.bills_data:
                bill_scores = self.calculate_all_bill_scores()
                self.set_cache('bill_scores_calculated', bill_scores, ttl=1800)  # 30분
            
            # 3. 뉴스 요약 캐시
            if self.news_data:
                news_summary = self.create_news_summary()
                self.set_cache('news_summary', news_summary, ttl=900)  # 15분
            
            # 4. 트렌드 차트 캐시
            if self.trend_data:
                chart_data = self.prepare_chart_data()
                self.set_cache('trend_chart_data', chart_data, ttl=1800)  # 30분
            
            logger.info(f"캐시 생성 완료: {len(self.cache)}개 항목")
            
        except Exception as e:
            logger.error(f"캐시 생성 오류: {e}")
    
    def calculate_all_bill_scores(self):
        """모든 정치인 발의안 점수 미리 계산"""
        bill_scores = {}
        
        for name, bills in self.bills_data.items():
            if bills:
                main_proposals = sum(1 for bill in bills if len(bill.get('co_proposers', [])) > 0)
                co_proposals = len(bills) - main_proposals
                total_bills = len(bills)
                
                passed_bills = sum(1 for bill in bills 
                                 if bill.get('status') in ['본회의 통과', '정부이송', '공포'])
                success_rate = round(passed_bills / total_bills, 2) if total_bills > 0 else 0
                
                bill_scores[name] = {
                    "main_proposals": main_proposals,
                    "co_proposals": co_proposals,
                    "total_bills": total_bills,
                    "success_rate": success_rate
                }
        
        return bill_scores
    
    def create_news_summary(self):
        """뉴스 데이터 요약 생성"""
        summary = {
            'total_politicians': len(self.news_data),
            'total_news': sum(len(news) for news in self.news_data.values()),
            'sentiment_stats': {'positive': 0, 'negative': 0, 'neutral': 0},
            'latest_news': [],
            'trending_politicians': []
        }
        
        all_news = []
        for politician, news_list in self.news_data.items():
            for news in news_list:
                news_copy = news.copy()
                news_copy['politician'] = politician
                all_news.append(news_copy)
                
                # 감정 통계
                sentiment = news.get('sentiment', 'neutral')
                summary['sentiment_stats'][sentiment] += 1
        
        # 최신 뉴스 5건
        all_news.sort(key=lambda x: x.get('pub_date', ''), reverse=True)
        summary['latest_news'] = all_news[:5]
        
        # 트렌딩 정치인 (뉴스 수 기준)
        politician_news_count = {}
        for politician, news_list in self.news_data.items():
            politician_news_count[politician] = len(news_list)
        
        trending = sorted(politician_news_count.items(), key=lambda x: x[1], reverse=True)
        summary['trending_politicians'] = [{'politician': p, 'news_count': c} for p, c in trending[:5]]
        
        return summary
    
    def prepare_chart_data(self):
        """차트 데이터 미리 준비"""
        if not self.trend_data or 'comparison' not in self.trend_data:
            return None
        
        comparison = self.trend_data['comparison']
        chart_data = comparison.get('chart_data', {})
        
        # Chart.js 형식으로 최적화
        optimized_chart = {
            'type': 'line',
            'labels': chart_data.get('labels', []),
            'datasets': chart_data.get('datasets', []),
            'options': {
                'responsive': True,
                'plugins': {
                    'legend': {'position': 'top'},
                    'title': {'display': True, 'text': '정치인 검색량 트렌드'}
                },
                'scales': {
                    'y': {'beginAtZero': True, 'title': {'display': True, 'text': '검색량 지수'}},
                    'x': {'title': {'display': True, 'text': '날짜'}}
                }
            }
        }
        
        return optimized_chart
    
    def set_cache(self, key, value, ttl=None):
        """캐시 설정"""
        if ttl is None:
            ttl = self.default_ttl
        
        self.cache[key] = value
        self.cache_ttl[key] = datetime.now() + timedelta(seconds=ttl)
    
    def get_cache(self, key):
        """캐시 조회"""
        if key not in self.cache:
            return None
        
        # TTL 확인
        if datetime.now() > self.cache_ttl.get(key, datetime.now()):
            # 만료된 캐시 삭제
            del self.cache[key]
            if key in self.cache_ttl:
                del self.cache_ttl[key]
            return None
        
        return self.cache[key]
    
    def clear_expired_cache(self):
        """만료된 캐시 정리"""
        now = datetime.now()
        expired_keys = [key for key, expire_time in self.cache_ttl.items() if now > expire_time]
        
        for key in expired_keys:
            if key in self.cache:
                del self.cache[key]
            del self.cache_ttl[key]
        
        if expired_keys:
            logger.info(f"만료된 캐시 정리: {len(expired_keys)}개")
    
    def get_politicians_fast(self):
        """빠른 정치인 목록 조회"""
        cached = self.get_cache('politicians_lightweight')
        if cached:
            return cached
        
        # 캐시 미스 시 다시 생성
        if self.politicians_data:
            lightweight = []
            for politician in self.politicians_data:
                lightweight.append({
                    'name': politician.get('naas_nm', ''),
                    'party': politician.get('party_name', '무소속'),
                    'district': politician.get('district', ''),
                    'photo_url': politician.get('photo_url', '')
                })
            
            self.set_cache('politicians_lightweight', lightweight, ttl=3600)
            return lightweight
        
        return []
    
    def get_bill_scores_fast(self):
        """빠른 발의안 점수 조회"""
        cached = self.get_cache('bill_scores_calculated')
        if cached:
            return cached
        
        # 캐시 미스 시 다시 계산
        if self.bills_data:
            scores = self.calculate_all_bill_scores()
            self.set_cache('bill_scores_calculated', scores, ttl=1800)
            return scores
        
        return {}
    
    def get_news_summary_fast(self):
        """빠른 뉴스 요약 조회"""
        cached = self.get_cache('news_summary')
        if cached:
            return cached
        
        # 캐시 미스 시 다시 생성
        if self.news_data:
            summary = self.create_news_summary()
            self.set_cache('news_summary', summary, ttl=900)
            return summary
        
        return {}
    
    def get_trend_chart_fast(self):
        """빠른 트렌드 차트 조회"""
        cached = self.get_cache('trend_chart_data')
        if cached:
            return cached
        
        # 캐시 미스 시 다시 준비
        if self.trend_data:
            chart = self.prepare_chart_data()
            self.set_cache('trend_chart_data', chart, ttl=1800)
            return chart
        
        return None
    
    def get_performance_stats(self):
        """성능 통계"""
        return {
            'cache_items': len(self.cache),
            'cache_keys': list(self.cache.keys()),
            'data_sizes': {
                'politicians': len(self.politicians_data) if self.politicians_data else 0,
                'bills': len(self.bills_data) if self.bills_data else 0,
                'news': len(self.news_data) if self.news_data else 0,
                'trends': len(self.trend_data) if self.trend_data else 0
            }
        }

def main():
    """성능 최적화 테스트"""
    optimizer = PerformanceOptimizer()
    
    print("⚡ NewsBot 성능 최적화 테스트")
    
    # 성능 측정
    tests = [
        ('정치인 목록 (최적화)', optimizer.get_politicians_fast),
        ('발의안 점수 (최적화)', optimizer.get_bill_scores_fast),
        ('뉴스 요약 (최적화)', optimizer.get_news_summary_fast),
        ('트렌드 차트 (최적화)', optimizer.get_trend_chart_fast)
    ]
    
    for test_name, test_func in tests:
        start_time = time.time()
        result = test_func()
        end_time = time.time()
        
        if isinstance(result, list):
            data_size = len(result)
        elif isinstance(result, dict):
            data_size = len(result)
        else:
            data_size = 1 if result else 0
        
        print(f"✅ {test_name}: {end_time - start_time:.3f}초 ({data_size}개 항목)")
    
    # 성능 통계
    stats = optimizer.get_performance_stats()
    print(f"\n📊 성능 통계:")
    print(f"캐시 항목: {stats['cache_items']}개")
    print(f"데이터 크기: {stats['data_sizes']}")

if __name__ == "__main__":
    main()

