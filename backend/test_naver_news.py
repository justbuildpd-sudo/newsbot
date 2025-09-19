#!/usr/bin/env python3
"""
네이버 뉴스 API 디버깅 테스트
"""

from naver_news_service import NaverNewsService
import json

def test_single_politician():
    service = NaverNewsService()
    
    # 단일 정치인 뉴스 검색 (디버깅 모드)
    politician = "이재명"
    print(f"🔍 {politician} 뉴스 검색 (디버깅)")
    
    # 원시 API 응답 확인
    raw_data = service.search_news(f'"{politician}"', display=5)
    if raw_data:
        print(f"📊 원시 데이터: {len(raw_data.get('items', []))}건")
        
        for i, item in enumerate(raw_data.get('items', [])[:3]):
            print(f"\n뉴스 {i+1}:")
            print(f"  제목: {service.clean_html(item.get('title', ''))}")
            print(f"  발행일: {item.get('pubDate', '')}")
            print(f"  링크: {item.get('link', '')}")
            
            # 날짜 파싱 테스트
            pub_date = service.parse_date(item.get('pubDate', ''))
            if pub_date:
                from datetime import datetime
                now = datetime.now(pub_date.tzinfo) if pub_date.tzinfo else datetime.now()
                days_ago = (now - pub_date).days
                print(f"  파싱된 날짜: {pub_date}")
                print(f"  {days_ago}일 전")
            else:
                print(f"  날짜 파싱 실패")
    
    # 처리된 뉴스 확인
    print(f"\n🔄 처리된 뉴스:")
    processed_news = service.search_politician_news(politician, days=30, max_results=5)
    if processed_news:
        print(f"✅ {len(processed_news)}건 수집")
        for news in processed_news:
            print(f"  - {news['title']} ({news['sentiment']})")
    else:
        print("❌ 처리된 뉴스 없음")

if __name__ == "__main__":
    test_single_politician()

