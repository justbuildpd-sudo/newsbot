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
        """뉴스 기사 전문 가져오기 (단순화된 버전)"""
        try:
            # 간단한 응답만 반환
            return {
                'title': '뉴스 제목',
                'content': '뉴스 내용을 가져오는 중입니다...',
                'images': [],
                'pub_date': '',
                'url': news_url
            }
            
        except Exception as e:
            print(f"뉴스 내용 가져오기 오류: {e}")
            return {
                'title': '',
                'content': '',
                'images': [],
                'pub_date': '',
                'url': news_url
            }
    
    def clean_html(self, text: str) -> str:
        """HTML 태그 제거"""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    def filter_news(self, news_list: List[Dict]) -> List[Dict]:
        """뉴스 필터링 (중복 제거, 시간 필터링, 정치 키워드 필터링)"""
        filtered_news = []
        seen_titles = set()
        
        for news in news_list:
            title = news.get('title', '')
            description = news.get('description', '')
            pub_date = news.get('pubDate', '')
            
            # 제목 중복 체크 (60% 이상 유사도)
            is_duplicate = False
            for seen_title in seen_titles:
                similarity = SequenceMatcher(None, title, seen_title).ratio()
                if similarity > 0.6:
                    is_duplicate = True
                    break
            
            if is_duplicate:
                continue
            
            # 시간 필터링 (4시간 이내)
            try:
                news_time = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                if datetime.now(news_time.tzinfo) - news_time > timedelta(hours=4):
                    continue
            except:
                pass
            
            # 정치 키워드 필터링
            text_to_check = f"{title} {description}".lower()
            has_political_keyword = any(keyword in text_to_check for keyword in self.political_keywords)
            
            if has_political_keyword:
                filtered_news.append(news)
                seen_titles.add(title)
        
        return filtered_news
    
    def cleanup_old_news(self):
        """오래된 뉴스 캐시 정리"""
        current_time = datetime.now()
        if current_time - self.last_cleanup > self.cleanup_interval:
            # 4시간 15분 이상 된 뉴스 제거
            cutoff_time = current_time - timedelta(hours=4, minutes=15)
            self.news_cache = {
                key: news for key, news in self.news_cache.items()
                if news.get('cached_at', current_time) > cutoff_time
            }
            self.last_cleanup = current_time
    
    def get_news(self) -> List[Dict]:
        """필터링된 뉴스 가져오기"""
        all_news = []
        
        for keyword in self.search_keywords:
            news_list = self.get_news_from_naver(keyword)
            all_news.extend(news_list)
        
        # 필터링 적용
        filtered_news = self.filter_news(all_news)
        
        # 캐시에 저장
        for news in filtered_news:
            cache_key = hashlib.md5(news.get('link', '').encode()).hexdigest()
            news['cached_at'] = datetime.now()
            self.news_cache[cache_key] = news
        
        # 오래된 뉴스 정리
        self.cleanup_old_news()
        
        return list(self.news_cache.values())
