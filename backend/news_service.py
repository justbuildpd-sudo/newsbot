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
        self.last_news_fetch = None  # 마지막 뉴스 수집 시간
        self.news_fetch_interval = timedelta(minutes=30)  # 30분마다 새로 수집
        
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
        """뉴스 기사 전문 가져오기 (웹 스크래핑)"""
        try:
            import requests
            # BeautifulSoup 제거됨
            import re
            import time
            
            # 네이버 뉴스 URL 확인
            if 'news.naver.com' not in news_url:
                return {
                    'title': '',
                    'content': '네이버 뉴스가 아닙니다.',
                    'images': [],
                    'pub_date': '',
                    'url': news_url
                }
            
            # User-Agent 설정 (네이버 봇 차단 우회)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            # 요청 간격 조절 (DDoS 방지)
            time.sleep(1)
            
            response = requests.get(news_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # BeautifulSoup 제거됨 - 간단한 텍스트 추출
            
            # 네이버 뉴스 특화 셀렉터
            title = ""
            title_selectors = [
                '.media_end_head_headline',  # 네이버 뉴스 제목
                'h1', 
                '.article_info h3', 
                '.news_title', 
                '.headline', 
                'title'
            ]
            
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text().strip()
                    # HTML 태그 제거
                    title = re.sub(r'<[^>]+>', '', title)
                    break
            
            # 본문 추출 (네이버 뉴스 특화)
            content = ""
            content_selectors = [
                '#newsct_article',  # 네이버 뉴스 본문
                '.go_article',      # 네이버 뉴스 본문
                '.article_body', 
                '.news_body', 
                '.article_view', 
                '.article_content', 
                '.news_content', 
                '.content',
                '[id*="article"]', 
                '[class*="article"]', 
                '[class*="content"]'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # 스크립트, 스타일, 광고 태그 제거
                    for unwanted in content_elem(["script", "style", ".ad", ".advertisement", ".banner"]):
                        unwanted.decompose()
                    
                    # 텍스트 추출
                    content = content_elem.get_text().strip()
                    
                    # HTML 태그 제거
                    content = re.sub(r'<[^>]+>', '', content)
                    
                    # 불필요한 공백 정리
                    content = re.sub(r'\s+', ' ', content)
                    
                    if len(content) > 100:  # 충분한 길이의 내용이 있는지 확인
                        break
            
            # 이미지 추출 (네이버 뉴스 특화)
            images = []
            img_selectors = [
                '#newsct_article img',  # 네이버 뉴스 본문 이미지
                '.go_article img',      # 네이버 뉴스 본문 이미지
                'img[src*="http"]', 
                '.article_body img', 
                '.news_body img',
                '.article_view img', 
                '.content img'
            ]
            
            for selector in img_selectors:
                img_elements = soup.select(selector)
                for img in img_elements:
                    src = img.get('src') or img.get('data-src') or img.get('data-original')
                    if src and src.startswith('http'):
                        # 네이버 이미지 URL 정리
                        if 'news.naver.com' in src:
                            # 네이버 이미지 크기 조정 (더 큰 이미지)
                            src = src.replace('type=f120_80', 'type=f640_480')
                        
                        alt = img.get('alt', '')
                        # 빈 alt 텍스트 처리
                        if not alt:
                            alt = '뉴스 이미지'
                        
                        images.append({
                            'src': src,
                            'alt': alt
                        })
            
            # 발행일 추출
            pub_date = ""
            date_selectors = [
                '.article_info .t11', '.news_date', '.article_date',
                '.publish_date', '[class*="date"]', '[class*="time"]'
            ]
            
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    pub_date = date_elem.get_text().strip()
                    break
            
            return {
                'title': title,
                'content': content,
                'images': images[:5],  # 최대 5개 이미지
                'pub_date': pub_date,
                'url': news_url
            }
            
        except Exception as e:
            print(f"뉴스 내용 가져오기 오류: {e}")
            return {
                'title': '',
                'content': '기사 내용을 가져올 수 없습니다.',
                'images': [],
                'pub_date': '',
                'url': news_url
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
        """캐시된 뉴스 반환 (타이밍 조절)"""
        self.cleanup_old_news()
        
        current_time = datetime.now()
        
        # 캐시가 비어있거나 지정된 시간이 지났으면 새로 수집
        if not self.news_cache or (self.last_news_fetch is None or 
                                 current_time - self.last_news_fetch > self.news_fetch_interval):
            print(f"📰 뉴스 새로 수집 중... (마지막 수집: {self.last_news_fetch})")
            new_news = self.get_political_news()
            self.news_cache = {}
            for news in new_news:
                news_id = hashlib.md5(news['title'].encode()).hexdigest()
                self.news_cache[news_id] = news
            self.last_news_fetch = current_time
            print(f"✅ 뉴스 {len(new_news)}개 수집 완료")
        else:
            print(f"📋 캐시된 뉴스 사용 중... (남은 시간: {self.news_fetch_interval - (current_time - self.last_news_fetch)})")
        
        return list(self.news_cache.values())
    
    def get_news_stats(self) -> Dict:
        """뉴스 통계 정보"""
        return {
            'total_cached': len(self.news_cache),
            'last_cleanup': self.last_cleanup.isoformat(),
            'cache_size': len(self.news_cache)
        }
    

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
