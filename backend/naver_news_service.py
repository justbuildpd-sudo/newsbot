#!/usr/bin/env python3
"""
네이버 뉴스 API 서비스
정치인별 뉴스 수집 및 분석
"""

import requests
import json
import time
from datetime import datetime, timedelta
from urllib.parse import quote
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NaverNewsService:
    def __init__(self):
        # 네이버 개발자 API 정보
        self.client_id = "kXwlSsFmb055ku9rWyx1"
        self.client_secret = "JZqw_LTiq_"
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        
        # 요청 헤더
        self.headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "User-Agent": "NewsBot/1.0"
        }
        
        # API 호출 제한 (하루 25,000회)
        self.request_delay = 0.1  # 100ms 간격
        self.daily_limit = 25000
        self.request_count = 0
        
        # 정치인 목록 로드
        self.load_politicians()
        
    def load_politicians(self):
        """22대 국회의원 목록 로드"""
        try:
            with open('22nd_assembly_members_300.json', 'r', encoding='utf-8') as f:
                members = json.load(f)
            self.politicians = [member.get('naas_nm', '') for member in members if member.get('naas_nm')]
            logger.info(f"정치인 목록 로드 완료: {len(self.politicians)}명")
        except FileNotFoundError:
            try:
                with open('../22nd_assembly_members_300.json', 'r', encoding='utf-8') as f:
                    members = json.load(f)
                self.politicians = [member.get('naas_nm', '') for member in members if member.get('naas_nm')]
                logger.info(f"정치인 목록 로드 완료: {len(self.politicians)}명")
            except FileNotFoundError:
                self.politicians = ["이재명", "한동훈", "조국", "정청래", "김기현"]
                logger.warning("정치인 데이터 파일을 찾을 수 없어 기본 목록 사용")
    
    def search_news(self, query, display=10, start=1, sort="sim"):
        """네이버 뉴스 검색"""
        if self.request_count >= self.daily_limit:
            logger.warning("일일 API 호출 한도 초과")
            return None
            
        try:
            # URL 인코딩
            encoded_query = quote(query)
            
            params = {
                "query": encoded_query,
                "display": display,  # 최대 100
                "start": start,      # 시작 위치
                "sort": sort         # sim(정확도), date(날짜)
            }
            
            response = requests.get(
                self.base_url, 
                headers=self.headers, 
                params=params,
                timeout=10
            )
            
            self.request_count += 1
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"뉴스 검색 성공: '{query}' - {len(data.get('items', []))}건")
                return data
            else:
                logger.error(f"API 호출 실패: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"뉴스 검색 오류: {e}")
            return None
        
        finally:
            time.sleep(self.request_delay)
    
    def search_politician_news(self, politician_name, days=30, max_results=20):
        """특정 정치인 관련 뉴스 검색"""
        try:
            # 검색 쿼리 생성 (정치 뉴스에 특화)
            queries = [
                f'{politician_name} 의원',
                f'{politician_name} 국회의원',
                f'{politician_name} 국회',
                f'{politician_name} 정당',
                f'{politician_name} 법안'
            ]
            
            all_news = []
            seen_titles = set()
            
            for query in queries:
                if len(all_news) >= max_results:
                    break
                    
                news_data = self.search_news(query, display=min(20, max_results), sort="sim")
                if not news_data:
                    continue
                
                for item in news_data.get('items', []):
                    # 중복 제거
                    title = self.clean_html(item.get('title', ''))
                    if title in seen_titles:
                        logger.debug(f"중복 제목 건너뛰기: {title}")
                        continue
                    
                    # 정치 관련 뉴스 필터링
                    description = item.get('description', '')
                    if not self.is_political_news(title, description):
                        logger.debug(f"정치 관련 없음: {title}")
                        continue
                    
                    seen_titles.add(title)
                    
                    # 날짜 필터링 (최근 N일) - 더 관대하게
                    pub_date = self.parse_date(item.get('pubDate', ''))
                    if pub_date:
                        # timezone-aware datetime으로 변환
                        now = datetime.now(pub_date.tzinfo) if pub_date.tzinfo else datetime.now()
                        days_diff = (now - pub_date).days
                        logger.debug(f"날짜 체크: {title} - {days_diff}일 전")
                        # 30일 이내 뉴스만 수집 (기본값보다 관대)
                        if days_diff > days:
                            logger.debug(f"날짜 초과로 제외: {days_diff}일 > {days}일")
                            continue
                    else:
                        logger.debug(f"날짜 파싱 실패: {item.get('pubDate', '')}")
                        # 날짜를 파싱할 수 없어도 수집 (최신 뉴스일 가능성)
                    
                    # 뉴스 데이터 정리
                    news_item = {
                        'title': title,
                        'description': self.clean_html(description),
                        'link': item.get('link', ''),
                        'pub_date': pub_date.isoformat() if pub_date else item.get('pubDate', ''),
                        'politician': politician_name,
                        'sentiment': self.analyze_sentiment(title + ' ' + description),
                        'collected_at': datetime.now().isoformat()
                    }
                    
                    all_news.append(news_item)
                    logger.info(f"뉴스 수집: {title}")
                    
                    if len(all_news) >= max_results:
                        break
            
            logger.info(f"{politician_name} 관련 뉴스 수집: {len(all_news)}건")
            return all_news
            
        except Exception as e:
            logger.error(f"{politician_name} 뉴스 검색 오류: {e}")
            return []
    
    def collect_all_politicians_news(self, days=7, max_per_politician=10):
        """모든 정치인 뉴스 수집"""
        all_news = {}
        total_collected = 0
        
        logger.info(f"전체 정치인 뉴스 수집 시작: {len(self.politicians)}명")
        
        for i, politician in enumerate(self.politicians):
            if self.request_count >= self.daily_limit * 0.9:  # 90% 사용 시 중단
                logger.warning("API 호출 한도 근접으로 수집 중단")
                break
            
            logger.info(f"진행률: {i+1}/{len(self.politicians)} - {politician}")
            
            news = self.search_politician_news(politician, days, max_per_politician)
            if news:
                all_news[politician] = news
                total_collected += len(news)
            
            # 요청 간격 조절
            time.sleep(0.2)
        
        logger.info(f"뉴스 수집 완료: 총 {total_collected}건")
        return all_news
    
    def is_political_news(self, title, description):
        """정치 관련 뉴스인지 판단 (개선된 버전)"""
        political_keywords = [
            '의원', '국회', '정치', '정부', '국정', '법안', '발의', '위원회',
            '정당', '선거', '공약', '정책', '국정감사', '국정조사', '본회의',
            '민주당', '국민의힘', '조국혁신당', '개혁신당', '진보당', '기본소득당',
            '발언', '비판', '지지', '반대', '찬성', '의정', '국회의원', '대통령',
            '총리', '장관', '청와대', '국무회의', '내각', '여당', '야당', '원내대표'
        ]
        
        # 제외할 키워드 (영화, 드라마, 연예 등) - 더 엄격하게
        exclude_keywords = [
            '영화', '드라마', '예능', '연예', '배우', '가수', '아이돌',
            '방송', 'TV', '시청률', '출연', '캐스팅', '촬영', '공연', '콘서트'
        ]
        
        text = title + ' ' + description
        
        # 강한 제외 키워드가 있으면 정치 뉴스가 아님
        strong_exclude = ['영화', '드라마', '예능', '배우', '가수']
        if any(keyword in text for keyword in strong_exclude):
            return False
        
        # 정치 키워드가 하나라도 있으면 정치 뉴스로 판단
        return any(keyword in text for keyword in political_keywords)
    
    def analyze_sentiment(self, text):
        """간단한 감정 분석 (키워드 기반)"""
        positive_words = [
            '성공', '발전', '개선', '긍정', '좋은', '훌륭', '성과', '발표', 
            '지지', '찬성', '협력', '합의', '통과', '승인', '추진'
        ]
        
        negative_words = [
            '실패', '문제', '비판', '반대', '갈등', '논란', '우려', '위기',
            '부정', '거부', '반발', '충돌', '폐기', '중단', '취소'
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
        import re
        # HTML 태그 제거
        clean = re.sub('<.*?>', '', text)
        # HTML 엔티티 변환
        clean = clean.replace('&lt;', '<').replace('&gt;', '>')
        clean = clean.replace('&amp;', '&').replace('&quot;', '"')
        clean = clean.replace('&#39;', "'").replace('&nbsp;', ' ')
        return clean.strip()
    
    def parse_date(self, date_string):
        """날짜 문자열 파싱"""
        try:
            # RFC 2822 형식: "Mon, 16 Sep 2024 10:30:00 +0900"
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_string)
        except:
            try:
                # ISO 형식 시도
                return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            except:
                return None
    
    def save_news_data(self, news_data, filename=None):
        """뉴스 데이터 저장"""
        if filename is None:
            filename = f"news_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(news_data, f, ensure_ascii=False, indent=2)
            
            total_news = sum(len(news) for news in news_data.values())
            logger.info(f"뉴스 데이터 저장 완료: {filename} ({total_news}건)")
            return filename
            
        except Exception as e:
            logger.error(f"뉴스 데이터 저장 오류: {e}")
            return None
    
    def get_trending_politicians(self, news_data, limit=10):
        """뉴스 언급량 기준 트렌딩 정치인"""
        trending = []
        
        for politician, news_list in news_data.items():
            if news_list:
                sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
                for news in news_list:
                    sentiment_counts[news.get('sentiment', 'neutral')] += 1
                
                trending.append({
                    'politician': politician,
                    'news_count': len(news_list),
                    'positive': sentiment_counts['positive'],
                    'negative': sentiment_counts['negative'],
                    'neutral': sentiment_counts['neutral'],
                    'sentiment_ratio': sentiment_counts['positive'] / len(news_list) if news_list else 0
                })
        
        # 뉴스 수 기준 정렬
        trending.sort(key=lambda x: x['news_count'], reverse=True)
        return trending[:limit]
    
    def get_api_status(self):
        """API 사용 현황"""
        return {
            'request_count': self.request_count,
            'daily_limit': self.daily_limit,
            'remaining': self.daily_limit - self.request_count,
            'usage_percentage': (self.request_count / self.daily_limit) * 100
        }

def main():
    """메인 실행 함수"""
    service = NaverNewsService()
    
    print("🌐 네이버 뉴스 API 서비스 시작")
    print(f"📊 정치인 수: {len(service.politicians)}명")
    
    # 주요 정치인 뉴스 수집 테스트
    test_politicians = ["이재명", "한동훈", "조국"]
    
    for politician in test_politicians:
        print(f"\n🔍 {politician} 뉴스 검색 중...")
        news = service.search_politician_news(politician, days=3, max_results=5)
        
        if news:
            print(f"✅ {len(news)}건 수집")
            for i, item in enumerate(news[:3]):
                print(f"  {i+1}. {item['title']} ({item['sentiment']})")
        else:
            print("❌ 뉴스 없음")
    
    print(f"\n📊 API 사용량: {service.get_api_status()}")

if __name__ == "__main__":
    main()
