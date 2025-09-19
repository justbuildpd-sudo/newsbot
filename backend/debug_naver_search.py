#!/usr/bin/env python3
"""
네이버 뉴스 API 검색 조건 상세 분석
"""

import requests
import json
from urllib.parse import quote

class NaverNewsDebugger:
    def __init__(self):
        self.client_id = "kXwlSsFmb055ku9rWyx1"
        self.client_secret = "JZqw_LTiq_"
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        
        self.headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "User-Agent": "NewsBot/1.0"
        }
    
    def test_search_conditions(self):
        """다양한 검색 조건 테스트"""
        
        # 테스트할 검색어들
        test_queries = [
            "이재명",
            '"이재명"',
            "이재명 의원",
            "이재명 국회의원", 
            "이재명 정치",
            "이재명 AND 의원",
            "이재명 AND 정치",
            "이재명 -영화",
            "이재명 -드라마",
            "더불어민주당 이재명",
            "국회 이재명"
        ]
        
        # 정렬 옵션 테스트
        sort_options = ["sim", "date"]
        
        print("🔍 네이버 뉴스 API 검색 조건 분석")
        print("=" * 60)
        
        for sort_type in sort_options:
            print(f"\n📊 정렬 방식: {sort_type} ({'정확도' if sort_type == 'sim' else '날짜'})")
            print("-" * 40)
            
            for query in test_queries:
                print(f"\n검색어: '{query}'")
                result = self.search_with_details(query, sort=sort_type)
                
                if result and result.get('items'):
                    items = result['items']
                    print(f"  결과 수: {len(items)}건")
                    
                    # 첫 번째 결과 상세 분석
                    if items:
                        first_item = items[0]
                        print(f"  첫 번째 결과:")
                        print(f"    제목: {self.clean_html(first_item.get('title', ''))}")
                        print(f"    발행일: {first_item.get('pubDate', '')}")
                        print(f"    설명: {self.clean_html(first_item.get('description', ''))[:100]}...")
                        
                        # 정치 관련성 체크
                        is_political = self.check_political_relevance(
                            first_item.get('title', ''),
                            first_item.get('description', '')
                        )
                        print(f"    정치 관련: {'✅' if is_political else '❌'}")
                else:
                    print(f"  결과 수: 0건")
    
    def search_with_details(self, query, display=10, sort="date"):
        """상세한 검색 실행"""
        try:
            params = {
                "query": query,
                "display": display,
                "start": 1,
                "sort": sort
            }
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"    API 오류: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"    검색 오류: {e}")
            return None
    
    def check_political_relevance(self, title, description):
        """정치 관련성 체크"""
        political_keywords = [
            '의원', '국회', '정치', '정부', '국정', '법안', '발의', '위원회',
            '정당', '선거', '공약', '정책', '국정감사', '본회의', '민주당',
            '국민의힘', '조국혁신당'
        ]
        
        text = (title + ' ' + description).lower()
        return any(keyword in text for keyword in political_keywords)
    
    def clean_html(self, text):
        """HTML 태그 제거"""
        import re
        clean = re.sub('<.*?>', '', text)
        clean = clean.replace('&lt;', '<').replace('&gt;', '>')
        clean = clean.replace('&amp;', '&').replace('&quot;', '"')
        clean = clean.replace('&#39;', "'").replace('&nbsp;', ' ')
        return clean.strip()
    
    def analyze_api_limits(self):
        """API 제한사항 분석"""
        print("\n📋 네이버 뉴스 API 제한사항")
        print("=" * 40)
        print("• 일일 호출 한도: 25,000회")
        print("• 검색 결과: 최대 1,000건 (start 1~1000)")
        print("• display: 1~100 (한 번에 가져올 수 있는 결과 수)")
        print("• sort: sim(정확도), date(날짜)")
        print("• 검색 범위: 네이버에 등록된 뉴스 사이트")
        print("• 검색 기간: 최근 뉴스 위주 (정확한 기간 제한 불명)")
    
    def test_recent_political_news(self):
        """최근 정치 뉴스 검색 테스트"""
        print("\n🗞️ 최근 정치 뉴스 검색 테스트")
        print("=" * 40)
        
        # 일반적인 정치 키워드로 검색
        general_queries = [
            "국회",
            "정치",
            "의원",
            "국정감사",
            "법안",
            "더불어민주당",
            "국민의힘"
        ]
        
        for query in general_queries:
            print(f"\n검색어: '{query}'")
            result = self.search_with_details(query, display=5, sort="date")
            
            if result and result.get('items'):
                items = result['items']
                print(f"  최신 뉴스 {len(items)}건:")
                
                for i, item in enumerate(items[:3]):
                    title = self.clean_html(item.get('title', ''))
                    pub_date = item.get('pubDate', '')
                    print(f"    {i+1}. {title}")
                    print(f"       발행: {pub_date}")
            else:
                print("  검색 결과 없음")

if __name__ == "__main__":
    debugger = NaverNewsDebugger()
    
    # 1. 검색 조건 분석
    debugger.test_search_conditions()
    
    # 2. API 제한사항 분석
    debugger.analyze_api_limits()
    
    # 3. 최근 정치 뉴스 테스트
    debugger.test_recent_political_news()

