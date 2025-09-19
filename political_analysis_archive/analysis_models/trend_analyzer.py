#!/usr/bin/env python3
"""
뉴스 데이터 기반 트렌드 분석 시스템
네이버 뉴스 API 데이터로 정치인 트렌드 차트 생성
"""

import json
import re
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    def __init__(self):
        self.load_news_data()
        self.load_politicians_data()
    
    def load_news_data(self):
        """수집된 뉴스 데이터 로드"""
        try:
            with open('naver_news_collected.json', 'r', encoding='utf-8') as f:
                self.news_data = json.load(f)
            total_news = sum(len(news) for news in self.news_data.values())
            logger.info(f"뉴스 데이터 로드: {len(self.news_data)}명, {total_news}건")
        except FileNotFoundError:
            self.news_data = {}
            logger.warning("뉴스 데이터 파일을 찾을 수 없음")
    
    def load_politicians_data(self):
        """정치인 데이터 로드"""
        try:
            with open('22nd_assembly_members_300.json', 'r', encoding='utf-8') as f:
                members = json.load(f)
            self.politicians_info = {member.get('naas_nm', ''): member for member in members if member.get('naas_nm')}
            logger.info(f"정치인 정보 로드: {len(self.politicians_info)}명")
        except FileNotFoundError:
            self.politicians_info = {}
            logger.warning("정치인 데이터 파일을 찾을 수 없음")
    
    def analyze_mention_trends(self):
        """뉴스 언급량 기반 트렌드 분석"""
        trends = {}
        
        for politician, news_list in self.news_data.items():
            if not news_list:
                continue
            
            # 일별 언급량 계산
            daily_mentions = defaultdict(int)
            sentiment_by_date = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
            
            for news in news_list:
                # 날짜 추출 (RFC 2822 형식)
                pub_date_str = news.get('pub_date', '')
                try:
                    from email.utils import parsedate_to_datetime
                    pub_date = parsedate_to_datetime(pub_date_str)
                    date_key = pub_date.strftime('%Y-%m-%d')
                    
                    daily_mentions[date_key] += 1
                    sentiment = news.get('sentiment', 'neutral')
                    sentiment_by_date[date_key][sentiment] += 1
                    
                except:
                    # 날짜 파싱 실패 시 오늘 날짜로 처리
                    today = datetime.now().strftime('%Y-%m-%d')
                    daily_mentions[today] += 1
                    sentiment = news.get('sentiment', 'neutral')
                    sentiment_by_date[today][sentiment] += 1
            
            # 트렌드 데이터 구성
            trend_points = []
            for date, count in sorted(daily_mentions.items()):
                sentiments = sentiment_by_date[date]
                trend_points.append({
                    'date': date,
                    'mentions': count,
                    'positive': sentiments['positive'],
                    'negative': sentiments['negative'], 
                    'neutral': sentiments['neutral'],
                    'sentiment_ratio': sentiments['positive'] / count if count > 0 else 0
                })
            
            # 통계 계산
            total_mentions = sum(point['mentions'] for point in trend_points)
            avg_mentions = total_mentions / len(trend_points) if trend_points else 0
            
            trends[politician] = {
                'politician': politician,
                'party': self.politicians_info.get(politician, {}).get('party_name', '무소속'),
                'total_mentions': total_mentions,
                'average_mentions': round(avg_mentions, 2),
                'trend_points': trend_points,
                'peak_date': max(trend_points, key=lambda x: x['mentions'])['date'] if trend_points else None,
                'sentiment_summary': {
                    'positive': sum(point['positive'] for point in trend_points),
                    'negative': sum(point['negative'] for point in trend_points),
                    'neutral': sum(point['neutral'] for point in trend_points)
                }
            }
        
        return trends
    
    def create_trending_ranking(self, trends):
        """트렌딩 랭킹 생성"""
        ranking = []
        
        for politician, trend_data in trends.items():
            ranking.append({
                'rank': 0,  # 나중에 설정
                'politician': politician,
                'party': trend_data['party'],
                'total_mentions': trend_data['total_mentions'],
                'average_mentions': trend_data['average_mentions'],
                'sentiment_ratio': trend_data['sentiment_summary']['positive'] / trend_data['total_mentions'] if trend_data['total_mentions'] > 0 else 0,
                'peak_date': trend_data['peak_date']
            })
        
        # 총 언급량 기준 정렬
        ranking.sort(key=lambda x: x['total_mentions'], reverse=True)
        
        # 순위 부여
        for i, item in enumerate(ranking):
            item['rank'] = i + 1
        
        return ranking
    
    def generate_chart_data(self, trends, chart_type="mentions"):
        """차트 데이터 생성"""
        chart_data = {
            'type': chart_type,
            'labels': [],
            'datasets': []
        }
        
        if not trends:
            return chart_data
        
        # 모든 날짜 수집
        all_dates = set()
        for trend_data in trends.values():
            for point in trend_data['trend_points']:
                all_dates.add(point['date'])
        
        # 날짜 정렬
        sorted_dates = sorted(all_dates)
        chart_data['labels'] = sorted_dates
        
        # 각 정치인별 데이터셋 생성
        colors = ['#3B82F6', '#EF4444', '#8B5CF6', '#10B981', '#F59E0B']
        
        for i, (politician, trend_data) in enumerate(trends.items()):
            # 날짜별 데이터 매핑
            date_values = {}
            for point in trend_data['trend_points']:
                if chart_type == "mentions":
                    date_values[point['date']] = point['mentions']
                elif chart_type == "sentiment":
                    date_values[point['date']] = point['sentiment_ratio']
            
            # 모든 날짜에 대한 값 생성 (없는 날짜는 0)
            values = [date_values.get(date, 0) for date in sorted_dates]
            
            dataset = {
                'label': politician,
                'data': values,
                'borderColor': colors[i % len(colors)],
                'backgroundColor': colors[i % len(colors)] + '20',  # 투명도 추가
                'tension': 0.4
            }
            
            chart_data['datasets'].append(dataset)
        
        return chart_data
    
    def save_trend_analysis(self, trends, ranking, chart_data):
        """트렌드 분석 결과 저장"""
        analysis_result = {
            'generated_at': datetime.now().isoformat(),
            'trends': trends,
            'ranking': ranking,
            'chart_data': chart_data,
            'summary': {
                'total_politicians': len(trends),
                'total_mentions': sum(t['total_mentions'] for t in trends.values()),
                'top_politician': ranking[0]['politician'] if ranking else None,
                'analysis_period': f"최근 {len(chart_data.get('labels', []))}일"
            }
        }
        
        filename = 'trend_analysis_result.json'
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"트렌드 분석 결과 저장: {filename}")
            return filename
        except Exception as e:
            logger.error(f"분석 결과 저장 오류: {e}")
            return None

def main():
    analyzer = TrendAnalyzer()
    
    print("📈 뉴스 기반 트렌드 분석 시작")
    
    # 1. 언급량 트렌드 분석
    trends = analyzer.analyze_mention_trends()
    if trends:
        print(f"✅ 트렌드 분석 완료: {len(trends)}명")
        
        # 2. 랭킹 생성
        ranking = analyzer.create_trending_ranking(trends)
        print(f"✅ 랭킹 생성 완료: {len(ranking)}명")
        
        print("\n📊 트렌딩 랭킹:")
        for item in ranking:
            print(f"  {item['rank']}. {item['politician']} ({item['party']})")
            print(f"     총 언급: {item['total_mentions']}건, 평균: {item['average_mentions']:.1f}건")
            print(f"     감정비율: {item['sentiment_ratio']:.2f}, 피크: {item['peak_date']}")
        
        # 3. 차트 데이터 생성
        chart_data = analyzer.generate_chart_data(trends, "mentions")
        print(f"✅ 차트 데이터 생성: {len(chart_data['datasets'])}개 데이터셋")
        
        # 4. 결과 저장
        result_file = analyzer.save_trend_analysis(trends, ranking, chart_data)
        if result_file:
            print(f"💾 최종 결과 저장: {result_file}")
    else:
        print("❌ 트렌드 분석 실패")

if __name__ == "__main__":
    main()

