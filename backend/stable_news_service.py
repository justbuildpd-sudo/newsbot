#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
안정적인 뉴스 서비스
Render와 Vercel 환경에서 안정적으로 작동하도록 개선
"""

import requests
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from difflib import SequenceMatcher
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StableNewsService:
    def __init__(self):
        self.client_id = "kXwlSsFmb055ku9rWyx1"
        self.client_secret = "JZqw_LTiq_"
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        self.news_cache = {}
        self.last_cleanup = datetime.now()
        self.cleanup_interval = timedelta(hours=4, minutes=15)
        
        # 정치 관련 키워드 (확장)
        self.political_keywords = [
            "대통령", "국회", "의원", "민주당", "국민의힘", 
            "트럼프", "총리", "정치", "정부", "여당", "야당",
            "조국혁신당", "개혁신당", "새로운미래", "정의당",
            "국무총리", "장관", "차관", "청와대", "여의도",
            "국정감사", "예산안", "법안", "정책", "입법",
            "선거", "투표", "당대표", "원내대표", "정치권"
        ]
        
        # 검색 키워드 (단독, 속보)
        self.search_keywords = ["단독", "속보"]
        
        # 요청 헤더 (안정성 향상)
        self.headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        # 요청 세션 (연결 재사용)
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_news_from_naver(self, query: str, display: int = 100) -> List[Dict]:
        """네이버 뉴스 API에서 뉴스 가져오기 (안정성 향상)"""
        params = {
            'query': query,
            'display': min(display, 100),  # 최대 100개로 제한
            'sort': 'sim'  # 정확도순
        }
        
        try:
            # 요청 간격 조절 (API 제한 준수)
            time.sleep(0.5)
            
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('items', [])
            
            logger.info(f"네이버 API 호출 성공: {query} - {len(items)}개 뉴스")
            return items
            
        except requests.exceptions.Timeout:
            logger.error(f"네이버 API 타임아웃: {query}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"네이버 API 요청 오류: {query} - {e}")
            return []
        except Exception as e:
            logger.error(f"네이버 API 예상치 못한 오류: {query} - {e}")
            return []
    
    def get_news_content_safe(self, news_url: str) -> Dict:
        """뉴스 기사 전문 가져오기 (안전한 버전)"""
        try:
            # 네이버 뉴스 URL 확인
            if 'news.naver.com' not in news_url:
                return {
                    'title': '',
                    'content': '네이버 뉴스가 아닙니다.',
                    'images': [],
                    'pub_date': '',
                    'url': news_url
                }
            
            # 요청 간격 조절
            time.sleep(1)
            
            # 안전한 헤더 설정
            safe_headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = self.session.get(news_url, headers=safe_headers, timeout=15)
            response.raise_for_status()
            
            # 간단한 텍스트 추출 (BeautifulSoup 없이)
            content = response.text
            
            # 제목 추출 (정규식 사용)
            title = self.extract_title_regex(content)
            
            # 본문 추출 (정규식 사용)
            article_content = self.extract_content_regex(content)
            
            # 이미지 추출 (정규식 사용)
            images = self.extract_images_regex(content)
            
            return {
                'title': title,
                'content': article_content,
                'images': images,
                'pub_date': datetime.now().isoformat(),
                'url': news_url
            }
            
        except Exception as e:
            logger.error(f"뉴스 내용 추출 오류: {news_url} - {e}")
            return {
                'title': '',
                'content': '기사 내용을 가져올 수 없습니다.',
                'images': [],
                'pub_date': '',
                'url': news_url
            }
    
    def extract_title_regex(self, html_content: str) -> str:
        """정규식으로 제목 추출"""
        title_patterns = [
            r'<title[^>]*>(.*?)</title>',
            r'<h1[^>]*>(.*?)</h1>',
            r'class="media_end_head_headline"[^>]*>(.*?)</',
            r'class="go_article"[^>]*>.*?<h1[^>]*>(.*?)</h1>',
            r'class="article_info"[^>]*>.*?<h3[^>]*>(.*?)</h3>'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # HTML 태그 제거
                title = re.sub(r'<[^>]+>', '', title)
                # 특수 문자 정리
                title = re.sub(r'&[^;]+;', '', title)
                if len(title) > 10:  # 충분한 길이의 제목인지 확인
                    return title
        
        return "제목을 찾을 수 없습니다."
    
    def extract_content_regex(self, html_content: str) -> str:
        """정규식으로 본문 추출"""
        content_patterns = [
            r'id="newsct_article"[^>]*>(.*?)</div>',
            r'class="go_article"[^>]*>(.*?)</div>',
            r'class="article_body"[^>]*>(.*?)</div>',
            r'class="news_body"[^>]*>(.*?)</div>',
            r'class="article_view"[^>]*>(.*?)</div>',
            r'class="article_content"[^>]*>(.*?)</div>'
        ]
        
        for pattern in content_patterns:
            match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1)
                # 스크립트, 스타일 태그 제거
                content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
                content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
                content = re.sub(r'<[^>]+>', '', content)  # 모든 HTML 태그 제거
                content = re.sub(r'&[^;]+;', '', content)  # HTML 엔티티 제거
                content = re.sub(r'\s+', ' ', content)  # 공백 정리
                content = content.strip()
                
                if len(content) > 100:  # 충분한 길이의 내용인지 확인
                    return content
        
        return "본문을 찾을 수 없습니다."
    
    def extract_images_regex(self, html_content: str) -> List[str]:
        """정규식으로 이미지 URL 추출"""
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        matches = re.findall(img_pattern, html_content, re.IGNORECASE)
        
        images = []
        for img_url in matches:
            # 상대 URL을 절대 URL로 변환
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = 'https://news.naver.com' + img_url
            
            # 유효한 이미지 URL인지 확인
            if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                images.append(img_url)
        
        return images[:5]  # 최대 5개 이미지만
    
    def clean_html(self, text: str) -> str:
        """HTML 태그 제거"""
        if not text:
            return ""
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    def calculate_similarity(self, title1: str, title2: str) -> float:
        """제목 유사도 계산 (0-1)"""
        if not title1 or not title2:
            return 0.0
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
        except Exception as e:
            logger.warning(f"날짜 파싱 오류: {pub_date} - {e}")
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
            try:
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
                
            except Exception as e:
                logger.warning(f"뉴스 필터링 중 오류: {e}")
                continue
        
        return filtered_news
    
    def get_political_news(self) -> List[Dict]:
        """정치 관련 뉴스 가져오기 (안정성 향상)"""
        all_news = []
        
        try:
            # 단독, 속보 키워드로 검색
            for keyword in self.search_keywords:
                news_list = self.get_news_from_naver(keyword, display=50)
                all_news.extend(news_list)
                
                # API 제한을 위한 대기
                time.sleep(1)
            
            # 필터링 적용
            filtered_news = self.filter_news(all_news)
            
            # 최신순으로 정렬
            filtered_news.sort(key=lambda x: x['pubDate'], reverse=True)
            
            logger.info(f"정치 뉴스 필터링 완료: {len(filtered_news)}개")
            return filtered_news[:20]  # 상위 20개만 반환
            
        except Exception as e:
            logger.error(f"정치 뉴스 가져오기 오류: {e}")
            return []
    
    def cleanup_old_news(self):
        """오래된 뉴스 정리 (4시간 15분 주기)"""
        current_time = datetime.now()
        if current_time - self.last_cleanup >= self.cleanup_interval:
            # 캐시된 뉴스 중 오래된 것들 제거
            cutoff_time = current_time - timedelta(hours=4, minutes=15)
            
            # 캐시 정리
            keys_to_remove = []
            for key, news_data in self.news_cache.items():
                if news_data.get('timestamp', '') < cutoff_time.isoformat():
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.news_cache[key]
            
            self.last_cleanup = current_time
            logger.info(f"뉴스 캐시 정리 완료: {len(keys_to_remove)}개 제거")
    
    def get_cached_news(self) -> List[Dict]:
        """캐시된 뉴스 반환"""
        self.cleanup_old_news()
        
        # 캐시가 비어있으면 새로 가져오기
        if not self.news_cache:
            fresh_news = self.get_political_news()
            for news in fresh_news:
                cache_key = hashlib.md5(news['link'].encode()).hexdigest()
                self.news_cache[cache_key] = news
            return fresh_news
        
        # 캐시된 뉴스 반환
        return list(self.news_cache.values())
    
    def get_news_with_content(self) -> List[Dict]:
        """뉴스와 상세 내용을 함께 반환"""
        news_list = self.get_cached_news()
        enhanced_news = []
        
        for news in news_list[:10]:  # 상위 10개만 상세 내용 가져오기
            try:
                content_data = self.get_news_content_safe(news['link'])
                enhanced_news.append({
                    **news,
                    'full_content': content_data['content'],
                    'images': content_data['images'],
                    'full_title': content_data['title']
                })
                
                # 요청 간격 조절
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f"뉴스 상세 내용 가져오기 오류: {e}")
                enhanced_news.append(news)
        
        return enhanced_news

# 전역 인스턴스
stable_news_service = StableNewsService()
