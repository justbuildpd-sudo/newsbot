#!/usr/bin/env python3
"""
네이버 뉴스 API + 데이터랩 검색어 트렌드 API 통합 서비스
"""

import requests
import json
import time
import re
from datetime import datetime, timedelta
from urllib.parse import quote
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedNaverService:
    def __init__(self):
        # 네이버 개발자 API 정보
        self.client_id = "kXwlSsFmb055ku9rWyx1"
        self.client_secret = "JZqw_LTiq_"
        
        # API 엔드포인트
        self.news_api_url = "https://openapi.naver.com/v1/search/news.json"
        self.datalab_api_url = "https://openapi.naver.com/v1/datalab/search"
        
        # 공통 헤더
        self.common_headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "User-Agent": "NewsBot/1.0"
        }
        
        # 데이터랩 전용 헤더
        self.datalab_headers = {
            **self.common_headers,
            "Content-Type": "application/json"
        }
        
        # 정치인 목록 로드
        self.load_politicians()
        
        # API 사용량 추적
        self.news_requests = 0
        self.datalab_requests = 0
        
    def load_politicians(self):
        """22대 국회의원 목록 로드"""
        try:
            with open('22nd_assembly_members_300.json', 'r', encoding='utf-8') as f:
                members = json.load(f)
            self.politicians = [member.get('naas_nm', '') for member in members if member.get('naas_nm')]
            self.politicians_info = {member.get('naas_nm', ''): member for member in members if member.get('naas_nm')}
            logger.info(f"정치인 목록 로드 완료: {len(self.politicians)}명")
        except FileNotFoundError:
            try:
                with open('../22nd_assembly_members_300.json', 'r', encoding='utf-8') as f:
                    members = json.load(f)
                self.politicians = [member.get('naas_nm', '') for member in members if member.get('naas_nm')]
                self.politicians_info = {member.get('naas_nm', ''): member for member in members if member.get('naas_nm')}
                logger.info(f"정치인 목록 로드 완료: {len(self.politicians)}명")
            except FileNotFoundError:
                self.politicians = ["이재명", "한동훈", "조국", "정청래", "김기현"]
                self.politicians_info = {}
                logger.warning("정치인 데이터 파일을 찾을 수 없어 기본 목록 사용")
    
    def search_news(self, query, display=10, sort="sim"):
        """네이버 뉴스 검색"""
        try:
            params = {
                "query": query,
                "display": display,
                "start": 1,
                "sort": sort
            }
            
            response = requests.get(
                self.news_api_url,
                headers=self.common_headers,
                params=params,
                timeout=10
            )
            
            self.news_requests += 1
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"뉴스 검색 성공: '{query}' - {len(data.get('items', []))}건")
                return data
            else:
                logger.error(f"뉴스 API 오류: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"뉴스 검색 오류: {e}")
            return None
        
        finally:
            time.sleep(0.1)  # API 호출 간격
    
    def get_search_trend(self, keywords, start_date, end_date, time_unit="date"):
        """
        네이버 데이터랩 검색어 트렌드 조회
        
        POST /v1/datalab/search
        HOST: openapi.naver.com
        Content-Type: application/json
        X-Naver-Client-Id: kXwlSsFmb055ku9rWyx1
        X-Naver-Client-Secret: JZqw_LTiq_
        """
        try:
            # 요청 바디 구성 (정확한 API 스펙에 따라)
            request_body = {
                "startDate": start_date,
                "endDate": end_date,
                "timeUnit": time_unit,  # date, week, month
                "keywordGroups": []
            }
            
            # 키워드 그룹 생성 (최대 5개까지)
            for keyword in keywords[:5]:
                request_body["keywordGroups"].append({
                    "groupName": keyword,
                    "keywords": [keyword]
                })
            
            logger.info(f"데이터랩 API 요청: {len(keywords)}개 키워드, {start_date}~{end_date}")
            
            response = requests.post(
                self.datalab_api_url,
                headers=self.datalab_headers,
                data=json.dumps(request_body, ensure_ascii=False).encode('utf-8'),
                timeout=15
            )
            
            self.datalab_requests += 1
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"데이터랩 API 성공: {len(data.get('results', []))}개 결과")
                return data
            else:
                logger.error(f"데이터랩 API 오류: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"데이터랩 API 요청 오류: {e}")
            return None
        
        finally:
            time.sleep(0.2)  # API 호출 간격
    
    def collect_politician_data(self, politician_name, days=30, max_news=10):
        """정치인별 뉴스 + 트렌드 통합 수집"""
        try:
            logger.info(f"🔍 {politician_name} 통합 데이터 수집 시작")
            
            # 1. 뉴스 데이터 수집
            news_data = self.collect_politician_news(politician_name, max_news)
            
            # 2. 검색 트렌드 데이터 수집
            trend_data = self.collect_politician_trend(politician_name, days)
            
            # 3. 통합 데이터 구성
            integrated_data = {
                'politician': politician_name,
                'party': self.politicians_info.get(politician_name, {}).get('party_name', '무소속'),
                'collected_at': datetime.now().isoformat(),
                'news': news_data,
                'trend': trend_data,
                'summary': self.create_summary(news_data, trend_data)
            }
            
            logger.info(f"✅ {politician_name} 통합 데이터 수집 완료")
            return integrated_data
            
        except Exception as e:
            logger.error(f"{politician_name} 통합 데이터 수집 오류: {e}")
            return None
    
    def collect_politician_news(self, politician_name, max_results=10):
        """정치인 뉴스 수집"""
        try:
            # 최적화된 검색어들
            queries = [
                f'{politician_name} 의원',
                f'{politician_name} 국회',
                f'{politician_name} 정치'
            ]
            
            all_news = []
            seen_titles = set()
            
            for query in queries:
                if len(all_news) >= max_results:
                    break
                
                news_result = self.search_news(query, display=min(10, max_results))
                if not news_result:
                    continue
                
                for item in news_result.get('items', []):
                    title = self.clean_html(item.get('title', ''))
                    
                    # 중복 제거
                    if title in seen_titles:
                        continue
                    
                    # 정치 관련성 체크
                    if not self.is_political_news(title, item.get('description', '')):
                        continue
                    
                    seen_titles.add(title)
                    
                    news_item = {
                        'title': title,
                        'description': self.clean_html(item.get('description', '')),
                        'link': item.get('link', ''),
                        'pub_date': item.get('pubDate', ''),
                        'sentiment': self.analyze_sentiment(title + ' ' + item.get('description', ''))
                    }
                    
                    all_news.append(news_item)
                    
                    if len(all_news) >= max_results:
                        break
            
            logger.info(f"{politician_name} 뉴스 수집: {len(all_news)}건")
            return all_news
            
        except Exception as e:
            logger.error(f"{politician_name} 뉴스 수집 오류: {e}")
            return []
    
    def collect_politician_trend(self, politician_name, days=30):
        """정치인 검색 트렌드 수집"""
        try:
            # 날짜 범위 설정
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # 검색어 트렌드 조회
            trend_result = self.get_search_trend(
                [politician_name],
                start_date_str,
                end_date_str,
                time_unit="date"
            )
            
            if trend_result and trend_result.get('results'):
                result = trend_result['results'][0]
                trend_points = result.get('data', [])
                
                # 통계 계산
                if trend_points:
                    values = [point.get('ratio', 0) for point in trend_points]
                    stats = {
                        'average': sum(values) / len(values),
                        'max': max(values),
                        'min': min(values),
                        'total_points': len(values),
                        'trend_direction': self.calculate_trend_direction(values)
                    }
                else:
                    stats = {'average': 0, 'max': 0, 'min': 0, 'total_points': 0, 'trend_direction': 'stable'}
                
                trend_data = {
                    'period': {'start': start_date_str, 'end': end_date_str},
                    'data_points': trend_points,
                    'statistics': stats
                }
                
                logger.info(f"{politician_name} 트렌드 수집: {len(trend_points)}일, 평균 {stats['average']:.2f}")
                return trend_data
            else:
                logger.warning(f"{politician_name} 트렌드 데이터 없음")
                return None
                
        except Exception as e:
            logger.error(f"{politician_name} 트렌드 수집 오류: {e}")
            return None
    
    def collect_multiple_politicians_comparison(self, politicians, days=30):
        """여러 정치인 검색량 비교"""
        try:
            # 최대 5명까지 비교 (API 제한)
            compare_list = politicians[:5]
            
            # 날짜 범위 설정
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # 비교 트렌드 조회
            comparison_result = self.get_search_trend(
                compare_list,
                start_date_str,
                end_date_str,
                time_unit="date"
            )
            
            if comparison_result and comparison_result.get('results'):
                processed_comparison = {
                    'period': {'start': start_date_str, 'end': end_date_str},
                    'politicians': [],
                    'chart_data': self.create_chart_data(comparison_result),
                    'ranking': []
                }
                
                # 각 정치인별 데이터 처리
                for result in comparison_result['results']:
                    politician = result.get('title')
                    trend_points = result.get('data', [])
                    
                    if trend_points:
                        values = [point.get('ratio', 0) for point in trend_points]
                        avg_search = sum(values) / len(values)
                        
                        politician_data = {
                            'politician': politician,
                            'party': self.politicians_info.get(politician, {}).get('party_name', '무소속'),
                            'average_search': round(avg_search, 2),
                            'max_search': max(values),
                            'trend_direction': self.calculate_trend_direction(values),
                            'data_points': trend_points
                        }
                        
                        processed_comparison['politicians'].append(politician_data)
                
                # 검색량 기준 랭킹
                processed_comparison['ranking'] = sorted(
                    processed_comparison['politicians'],
                    key=lambda x: x['average_search'],
                    reverse=True
                )
                
                # 순위 부여
                for i, item in enumerate(processed_comparison['ranking']):
                    item['rank'] = i + 1
                
                logger.info(f"정치인 비교 트렌드 수집: {len(compare_list)}명")
                return processed_comparison
            else:
                logger.warning("비교 트렌드 데이터 없음")
                return None
                
        except Exception as e:
            logger.error(f"정치인 비교 트렌드 오류: {e}")
            return None
    
    def calculate_trend_direction(self, values):
        """트렌드 방향 계산"""
        if len(values) < 2:
            return 'stable'
        
        # 최근 3일과 이전 3일 비교
        recent_avg = sum(values[-3:]) / min(3, len(values[-3:]))
        previous_avg = sum(values[-6:-3]) / min(3, len(values[-6:-3])) if len(values) >= 6 else recent_avg
        
        if recent_avg > previous_avg * 1.2:
            return 'rising'
        elif recent_avg < previous_avg * 0.8:
            return 'falling'
        else:
            return 'stable'
    
    def create_chart_data(self, datalab_result):
        """차트 데이터 생성 (Chart.js 형식)"""
        try:
            results = datalab_result.get('results', [])
            if not results:
                return None
            
            # 날짜 라벨 생성 (첫 번째 결과의 날짜 사용)
            first_result = results[0]
            dates = [point.get('period') for point in first_result.get('data', [])]
            
            # 데이터셋 생성
            datasets = []
            colors = ['#3B82F6', '#EF4444', '#8B5CF6', '#10B981', '#F59E0B']
            
            for i, result in enumerate(results):
                politician = result.get('title')
                values = [point.get('ratio', 0) for point in result.get('data', [])]
                
                dataset = {
                    'label': politician,
                    'data': values,
                    'borderColor': colors[i % len(colors)],
                    'backgroundColor': colors[i % len(colors)] + '20',
                    'tension': 0.4,
                    'fill': False
                }
                
                datasets.append(dataset)
            
            chart_data = {
                'labels': dates,
                'datasets': datasets
            }
            
            return chart_data
            
        except Exception as e:
            logger.error(f"차트 데이터 생성 오류: {e}")
            return None
    
    def create_summary(self, news_data, trend_data):
        """뉴스 + 트렌드 통합 요약"""
        summary = {
            'news_count': len(news_data) if news_data else 0,
            'trend_available': trend_data is not None,
            'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0}
        }
        
        # 뉴스 감정 분석
        if news_data:
            for news in news_data:
                sentiment = news.get('sentiment', 'neutral')
                summary['sentiment_distribution'][sentiment] += 1
        
        # 트렌드 정보
        if trend_data and trend_data.get('statistics'):
            stats = trend_data['statistics']
            summary.update({
                'average_search': stats.get('average', 0),
                'search_trend': stats.get('trend_direction', 'stable'),
                'peak_search': stats.get('max', 0)
            })
        
        return summary
    
    def is_political_news(self, title, description):
        """정치 관련 뉴스 판단"""
        political_keywords = [
            '의원', '국회', '정치', '정부', '정당', '법안', '발의', '위원회',
            '선거', '정책', '국정감사', '본회의', '민주당', '국민의힘', '조국혁신당',
            '대통령', '총리', '장관', '여당', '야당', '원내대표'
        ]
        
        # 강한 제외 키워드
        exclude_keywords = ['영화', '드라마', '예능', '배우', '가수', '연예인']
        
        text = title + ' ' + description
        
        # 제외 키워드 체크
        if any(keyword in text for keyword in exclude_keywords):
            return False
        
        # 정치 키워드 체크
        return any(keyword in text for keyword in political_keywords)
    
    def analyze_sentiment(self, text):
        """감정 분석"""
        positive_words = [
            '성공', '발전', '개선', '긍정', '좋은', '훌륭', '성과', 
            '지지', '찬성', '협력', '합의', '통과', '승인', '추진'
        ]
        
        negative_words = [
            '실패', '문제', '비판', '반대', '갈등', '논란', '우려', '위기',
            '부정', '거부', '반발', '충돌', '폐기', '중단', '취소', '구속'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def clean_html(self, text):
        """HTML 태그 제거"""
        clean = re.sub('<.*?>', '', text)
        clean = clean.replace('&lt;', '<').replace('&gt;', '>')
        clean = clean.replace('&amp;', '&').replace('&quot;', '"')
        clean = clean.replace('&#39;', "'").replace('&nbsp;', ' ')
        return clean.strip()
    
    def get_api_usage(self):
        """API 사용량 현황"""
        return {
            'news_requests': self.news_requests,
            'datalab_requests': self.datalab_requests,
            'total_requests': self.news_requests + self.datalab_requests,
            'news_limit': 25000,  # 일일 한도
            'datalab_limit': 1000   # 일일 한도 (추정)
        }
    
    def save_integrated_data(self, data, filename=None):
        """통합 데이터 저장"""
        if filename is None:
            filename = f"integrated_naver_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"통합 데이터 저장 완료: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"통합 데이터 저장 오류: {e}")
            return None

def main():
    """메인 실행 함수"""
    service = IntegratedNaverService()
    
    print("🌐 네이버 뉴스 + 데이터랩 통합 서비스 테스트")
    print(f"📊 정치인 수: {len(service.politicians)}명")
    
    # 주요 정치인 통합 데이터 수집
    major_politicians = ["이재명", "한동훈", "조국"]
    all_integrated_data = {}
    
    for politician in major_politicians:
        print(f"\n{'='*50}")
        print(f"🔍 {politician} 통합 데이터 수집")
        print('='*50)
        
        integrated_data = service.collect_politician_data(politician, days=30, max_news=5)
        
        if integrated_data:
            all_integrated_data[politician] = integrated_data
            
            # 결과 출력
            summary = integrated_data['summary']
            print(f"✅ 뉴스: {summary['news_count']}건")
            print(f"✅ 트렌드: {'있음' if summary['trend_available'] else '없음'}")
            
            if summary['trend_available']:
                print(f"📈 평균 검색량: {summary.get('average_search', 0):.2f}")
                print(f"📊 트렌드: {summary.get('search_trend', 'stable')}")
            
            print(f"😊 감정 분석: 긍정 {summary['sentiment_distribution']['positive']}건, "
                  f"부정 {summary['sentiment_distribution']['negative']}건, "
                  f"중립 {summary['sentiment_distribution']['neutral']}건")
        else:
            print(f"❌ {politician} 데이터 수집 실패")
    
    # 정치인 비교 트렌드
    print(f"\n{'='*50}")
    print("📊 정치인 검색량 비교 트렌드")
    print('='*50)
    
    comparison_data = service.collect_multiple_politicians_comparison(major_politicians, days=30)
    if comparison_data:
        print("✅ 비교 트렌드 수집 성공")
        
        print("\n🏆 검색량 랭킹:")
        for item in comparison_data['ranking']:
            print(f"  {item['rank']}. {item['politician']} ({item['party']})")
            print(f"     평균 검색량: {item['average_search']:.2f}")
            print(f"     트렌드: {item['trend_direction']}")
        
        all_integrated_data['comparison'] = comparison_data
    else:
        print("❌ 비교 트렌드 수집 실패")
    
    # 최종 데이터 저장
    if all_integrated_data:
        filename = service.save_integrated_data(all_integrated_data, 'naver_integrated_data.json')
        if filename:
            print(f"\n💾 통합 데이터 저장 완료: {filename}")
    
    # API 사용량 출력
    usage = service.get_api_usage()
    print(f"\n📊 API 사용량:")
    print(f"  뉴스 API: {usage['news_requests']}회")
    print(f"  데이터랩 API: {usage['datalab_requests']}회")
    print(f"  총 요청: {usage['total_requests']}회")

if __name__ == "__main__":
    main()

