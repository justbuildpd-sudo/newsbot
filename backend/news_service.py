import requests
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Set
import re
from difflib import SequenceMatcher

class NewsService:
    def __init__(self):
        self.client_id = "kXwlSsFmb055ku9rWyx1"
        self.client_secret = "JZqw_LTiq_"
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        self.news_cache = {}  # 뉴스 캐시
        self.last_cleanup = datetime.now()
        self.cleanup_interval = timedelta(hours=4, minutes=15)  # 4시간 15분
        
        # 정치 관련 키워드
        self.political_keywords = [
            "대통령", "국회", "의원", "민주당", "국민의힘", 
            "트럼프", "총리", "정치", "정부", "여당", "야당"
        ]
        
        # 검색 키워드 (단독, 속보)
        self.search_keywords = ["단독", "속보"]
    
    def get_news_from_naver(self, query: str, display: int = 100) -> List[Dict]:
        """네이버 뉴스 API에서 뉴스 가져오기"""
        headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }
        
        params = {
            'query': query,
            'display': display,
            'sort': 'sim'  # 정확도순
        }
        
        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('items', [])
        except Exception as e:
            print(f"네이버 API 오류: {e}")
            return []
    
    def get_news_content(self, news_url: str) -> Dict:
    """뉴스 기사 전문 가져오기 (간단한 버전)"""
    try:
        import time
        
        # 요청 간격 조절
        time.sleep(1)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(news_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 간단한 텍스트 추출 (BeautifulSoup 없이)
        text = response.text
        
        # 제목 추출 (간단한 방법)
        title = ""
        if '<title>' in text:
            start = text.find('<title>') + 7
            end = text.find('</title>', start)
            if start < end:
                title = text[start:end].strip()
        
        # 본문 추출 (간단한 방법)
        content = ""
        if 'newsct_article' in text:
            content = "뉴스 내용을 가져오는 중입니다..."
        
        return {
            'title': title,
            'content': content,
            'images': [],
            'pub_date': ''
        }
        
    except Exception as e:
        print(f"뉴스 내용 가져오기 오류: {e}")
        return {
            'title': '',
            'content': '',
            'images': [],
            'pub_date': ''
        }
    
    def clean_html(self, text: str) -> str:
        """HTML 태그 제거"""
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    def calculate_similarity(self, title1: str, title2: str) -> float:
        """제목 유사도 계산 (0-1)"""
        return SequenceMatcher(None, title1, title2).ratio()
    
    def is_duplicate_news(self, new_title: str, existing_news: List[Dict], threshold: float = 0.6) -> bool:
        """중복 뉴스 확인 (60% 이상 유사도)"""
        for news in existing_news:
            if self.calculate_similarity(new_title, news['title']) >= threshold:
                return True
        return False
    
    def is_recent_news(self, pub_date: str, hours: int = 4) -> bool:
        """최근 뉴스인지 확인 (4시간 이내)"""
        try:
            # 네이버 API 날짜 형식: "Mon, 14 Sep 2025 12:00:00 +0900"
            news_time = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
            cutoff_time = datetime.now(news_time.tzinfo) - timedelta(hours=hours)
            return news_time > cutoff_time
        except:
            return False
    
    def contains_political_keywords(self, title: str, description: str = "") -> bool:
        """정치 관련 키워드 포함 여부 확인"""
        text = f"{title} {description}".lower()
        for keyword in self.political_keywords:
            if keyword in text:
                return True
        return False
    
    def filter_news(self, news_list: List[Dict]) -> List[Dict]:
        """뉴스 필터링 (중복 제거, 시간 필터링, 정치 키워드 필터링)"""
        filtered_news = []
        
        for news in news_list:
            # HTML 태그 제거
            title = self.clean_html(news.get('title', ''))
            description = self.clean_html(news.get('description', ''))
            pub_date = news.get('pubDate', '')
            
            # 1. 최근 뉴스인지 확인 (4시간 이내)
            if not self.is_recent_news(pub_date):
                continue
            
            # 2. 정치 관련 키워드 포함 여부 확인
            if not self.contains_political_keywords(title, description):
                continue
            
            # 3. 중복 뉴스 확인 (60% 이상 유사도)
            if self.is_duplicate_news(title, filtered_news):
                continue
            
            # 필터링 통과한 뉴스 추가
            filtered_news.append({
                'title': title,
                'description': description,
                'link': news.get('link', ''),
                'pubDate': pub_date,
                'source': news.get('originallink', ''),
                'timestamp': datetime.now().isoformat()
            })
        
        return filtered_news
    
    def get_political_news(self) -> List[Dict]:
        """정치 관련 뉴스 가져오기"""
        all_news = []
        
        # 단독, 속보 키워드로 검색
        for keyword in self.search_keywords:
            news_list = self.get_news_from_naver(keyword, display=50)
            all_news.extend(news_list)
        
        # 필터링 적용
        filtered_news = self.filter_news(all_news)
        
        # 최신순으로 정렬
        filtered_news.sort(key=lambda x: x['pubDate'], reverse=True)
        
        return filtered_news[:20]  # 상위 20개만 반환
    
    def cleanup_old_news(self):
        """오래된 뉴스 정리 (4시간 15분 주기)"""
        current_time = datetime.now()
        if current_time - self.last_cleanup >= self.cleanup_interval:
            # 캐시된 뉴스 중 오래된 것들 제거
            cutoff_time = current_time - timedelta(hours=4, minutes=15)
            
            # 타임스탬프 기준으로 오래된 뉴스 제거
            self.news_cache = {
                k: v for k, v in self.news_cache.items()
                if datetime.fromisoformat(v['timestamp']) > cutoff_time
            }
            
            self.last_cleanup = current_time
            print(f"뉴스 정리 완료: {len(self.news_cache)}개 뉴스 남음")
    
    def get_cached_news(self) -> List[Dict]:
        """캐시된 뉴스 반환"""
        self.cleanup_old_news()
        
        if not self.news_cache:
            # 캐시가 비어있으면 새로운 뉴스 가져오기
            new_news = self.get_political_news()
            for news in new_news:
                news_id = hashlib.md5(news['title'].encode()).hexdigest()
                self.news_cache[news_id] = news
        
        return list(self.news_cache.values())[:10]  # 상위 10개만 반환

# 테스트용
if __name__ == "__main__":
    news_service = NewsService()
    news = news_service.get_political_news()
    
    print(f"가져온 뉴스 수: {len(news)}")
    for i, article in enumerate(news[:5], 1):
        print(f"{i}. {article['title']}")
        print(f"   출처: {article['source']}")
        print(f"   시간: {article['pubDate']}")
        print()
