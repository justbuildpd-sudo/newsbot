#!/usr/bin/env python3
"""
네이버 뉴스 API 응답 내용 상세 분석
"""

import requests
import json
import re

def analyze_news_content():
    client_id = "kXwlSsFmb055ku9rWyx1"
    client_secret = "JZqw_LTiq_"
    base_url = "https://openapi.naver.com/v1/search/news.json"
    
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "User-Agent": "NewsBot/1.0"
    }
    
    def clean_html(text):
        clean = re.sub('<.*?>', '', text)
        clean = clean.replace('&lt;', '<').replace('&gt;', '>')
        clean = clean.replace('&amp;', '&').replace('&quot;', '"')
        clean = clean.replace('&#39;', "'").replace('&nbsp;', ' ')
        return clean.strip()
    
    # 정치인별 뉴스 상세 분석
    politicians = ['이재명', '한동훈', '조국']
    
    for politician in politicians:
        print(f"\n🔍 {politician} 뉴스 상세 분석")
        print("=" * 50)
        
        # 가장 효과적인 검색어 찾기
        queries = [
            f'{politician} 정치',
            f'{politician} 의원', 
            f'{politician} 국회'
        ]
        
        for query in queries:
            print(f"\n검색어: '{query}'")
            
            try:
                params = {
                    "query": query,
                    "display": 5,
                    "start": 1,
                    "sort": "date"
                }
                
                response = requests.get(base_url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    
                    print(f"  📊 검색 결과: {len(items)}건")
                    
                    for i, item in enumerate(items[:3]):
                        title = clean_html(item.get('title', ''))
                        description = clean_html(item.get('description', ''))
                        pub_date = item.get('pubDate', '')
                        
                        print(f"\n  뉴스 {i+1}:")
                        print(f"    제목: {title}")
                        print(f"    설명: {description[:150]}...")
                        print(f"    발행일: {pub_date}")
                        
                        # 정치 키워드 체크
                        political_keywords = ['의원', '국회', '정치', '정부', '정당', '법안', '발의']
                        found_keywords = [kw for kw in political_keywords if kw in (title + description)]
                        print(f"    정치 키워드: {found_keywords}")
                        
                        # 제외 키워드 체크
                        exclude_keywords = ['영화', '드라마', '예능', '배우']
                        found_exclude = [kw for kw in exclude_keywords if kw in (title + description)]
                        print(f"    제외 키워드: {found_exclude}")
                        
                        # 최종 판단
                        is_political = len(found_keywords) > 0 and len(found_exclude) == 0
                        print(f"    정치 관련성: {'✅' if is_political else '❌'}")
                
                else:
                    print(f"  API 오류: {response.status_code}")
                    
            except Exception as e:
                print(f"  검색 오류: {e}")

if __name__ == "__main__":
    analyze_news_content()
