#!/usr/bin/env python3
"""
네이버 뉴스 필터링 로직 디버깅
"""

import requests
import json
import re
from datetime import datetime
from email.utils import parsedate_to_datetime

def debug_filtering():
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
    
    def is_political_news(title, description):
        political_keywords = [
            '의원', '국회', '정치', '정부', '국정', '법안', '발의', '위원회',
            '정당', '선거', '공약', '정책', '국정감사', '국정조사', '본회의',
            '민주당', '국민의힘', '조국혁신당', '개혁신당', '진보당', '기본소득당',
            '발언', '비판', '지지', '반대', '찬성', '의정', '국회의원', '대통령',
            '총리', '장관', '청와대', '국무회의', '내각', '여당', '야당', '원내대표'
        ]
        
        strong_exclude = ['영화', '드라마', '예능', '배우', '가수']
        text = title + ' ' + description
        
        if any(keyword in text for keyword in strong_exclude):
            return False
        
        return any(keyword in text for keyword in political_keywords)
    
    def parse_date(date_string):
        try:
            return parsedate_to_datetime(date_string)
        except:
            return None
    
    # 이재명 뉴스 상세 디버깅
    politician = "이재명"
    query = f'{politician} 정치'
    
    print(f"🔍 '{query}' 검색 결과 필터링 과정 분석")
    print("=" * 60)
    
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
            
            print(f"📊 API 응답: {len(items)}건")
            
            for i, item in enumerate(items):
                title = clean_html(item.get('title', ''))
                description = clean_html(item.get('description', ''))
                pub_date_str = item.get('pubDate', '')
                
                print(f"\n--- 뉴스 {i+1} 필터링 과정 ---")
                print(f"제목: {title}")
                print(f"설명: {description[:100]}...")
                print(f"발행일: {pub_date_str}")
                
                # 1. 정치 관련성 체크
                is_political = is_political_news(title, description)
                print(f"1️⃣ 정치 관련성: {'✅' if is_political else '❌'}")
                
                if not is_political:
                    print("   → 정치 관련 없음으로 필터링됨")
                    continue
                
                # 2. 날짜 체크
                pub_date = parse_date(pub_date_str)
                if pub_date:
                    now = datetime.now(pub_date.tzinfo) if pub_date.tzinfo else datetime.now()
                    days_diff = (now - pub_date).days
                    print(f"2️⃣ 날짜 필터링: {days_diff}일 전 ({'✅' if days_diff <= 30 else '❌'})")
                    
                    if days_diff > 30:
                        print("   → 30일 초과로 필터링됨")
                        continue
                else:
                    print(f"2️⃣ 날짜 파싱 실패: {pub_date_str}")
                    continue
                
                print("✅ 최종 통과: 수집 대상")
        
        else:
            print(f"❌ API 오류: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    debug_filtering()

