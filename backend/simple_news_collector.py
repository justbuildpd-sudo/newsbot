#!/usr/bin/env python3
"""
간단하고 확실한 네이버 뉴스 수집기
"""

import requests
import json
import re
from datetime import datetime

class SimpleNewsCollector:
    def __init__(self):
        self.client_id = "kXwlSsFmb055ku9rWyx1"
        self.client_secret = "JZqw_LTiq_"
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        
        self.headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
    
    def clean_html(self, text):
        """HTML 태그 제거"""
        clean = re.sub('<.*?>', '', text)
        clean = clean.replace('&lt;', '<').replace('&gt;', '>')
        clean = clean.replace('&amp;', '&').replace('&quot;', '"')
        clean = clean.replace('&#39;', "'").replace('&nbsp;', ' ')
        return clean.strip()
    
    def collect_political_news(self, politician_name, max_results=10):
        """정치인 뉴스 수집 (간단 버전)"""
        try:
            # 가장 효과적인 검색어 사용
            query = f"{politician_name} 의원"
            
            params = {
                "query": query,
                "display": max_results,
                "start": 1,
                "sort": "sim"  # 정확도 정렬
            }
            
            print(f"🔍 검색어: '{query}'")
            response = requests.get(self.base_url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                print(f"📊 검색 결과: {len(items)}건")
                
                collected_news = []
                for i, item in enumerate(items):
                    title = self.clean_html(item.get('title', ''))
                    description = self.clean_html(item.get('description', ''))
                    
                    # 기본적인 정치 관련성 체크
                    if self.is_relevant_news(title, description, politician_name):
                        news_item = {
                            'title': title,
                            'description': description,
                            'link': item.get('link', ''),
                            'pub_date': item.get('pubDate', ''),
                            'politician': politician_name,
                            'sentiment': self.simple_sentiment(title + ' ' + description),
                            'collected_at': datetime.now().isoformat()
                        }
                        collected_news.append(news_item)
                        print(f"  ✅ 수집: {title}")
                    else:
                        print(f"  ❌ 제외: {title}")
                
                return collected_news
            else:
                print(f"❌ API 오류: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 수집 오류: {e}")
            return []
    
    def is_relevant_news(self, title, description, politician_name):
        """관련성 체크 (매우 관대한 조건)"""
        text = (title + ' ' + description).lower()
        
        # 강한 제외 조건만 적용
        exclude_keywords = ['영화', '드라마', '예능', '배우', '가수', '연예인']
        if any(keyword in text for keyword in exclude_keywords):
            return False
        
        # 정치인 이름이 포함되어 있고, 기본적인 정치 키워드가 하나라도 있으면 수집
        basic_political = ['의원', '국회', '정치', '정부', '정당', '법안']
        has_political_keyword = any(keyword in text for keyword in basic_political)
        
        return politician_name in (title + description) and has_political_keyword
    
    def simple_sentiment(self, text):
        """간단한 감정 분석"""
        positive = ['성공', '발전', '개선', '좋은', '지지', '찬성', '통과', '승인']
        negative = ['실패', '문제', '비판', '반대', '갈등', '논란', '우려', '거부']
        
        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        else:
            return 'neutral'

def main():
    collector = SimpleNewsCollector()
    
    # 주요 정치인 뉴스 수집
    politicians = ['이재명', '한동훈', '조국']
    all_news = {}
    
    for politician in politicians:
        print(f"\n{'='*50}")
        print(f"🔍 {politician} 뉴스 수집")
        print('='*50)
        
        news = collector.collect_political_news(politician, max_results=5)
        
        if news:
            all_news[politician] = news
            print(f"\n🎉 {politician}: {len(news)}건 수집 완료")
        else:
            print(f"\n❌ {politician}: 수집된 뉴스 없음")
    
    # 전체 결과 저장
    if all_news:
        with open('naver_news_collected.json', 'w', encoding='utf-8') as f:
            json.dump(all_news, f, ensure_ascii=False, indent=2)
        
        total_count = sum(len(news) for news in all_news.values())
        print(f"\n💾 뉴스 데이터 저장 완료: naver_news_collected.json")
        print(f"📊 총 수집량: {len(all_news)}명 정치인, {total_count}건 뉴스")
    
    print(f"\n🎉 네이버 뉴스 수집 완료!")

if __name__ == "__main__":
    main()
