"""
네이버 뉴스 API를 통한 뉴스 수집 스크립트
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class NaverNewsCollector:
    """네이버 뉴스 수집기"""
    
    def __init__(self):
        self.client_id = os.getenv("NAVER_CLIENT_ID")
        self.client_secret = os.getenv("NAVER_CLIENT_SECRET")
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        self.headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
    
    def search_news(self, query: str, display: int = 10, start: int = 1, sort: str = "sim") -> Dict[str, Any]:
        """
        네이버 뉴스 검색
        
        Args:
            query: 검색 키워드
            display: 검색 결과 출력 건수 (1-100)
            start: 검색 시작 위치 (1-1000)
            sort: 정렬 옵션 (sim: 정확도, date: 날짜)
        
        Returns:
            검색 결과 딕셔너리
        """
        params = {
            "query": query,
            "display": display,
            "start": start,
            "sort": sort
        }
        
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"뉴스 검색 중 오류 발생: {e}")
            return {}
    
    def collect_political_news(self, keywords: List[str], days: int = 7) -> List[Dict[str, Any]]:
        """
        정치 관련 뉴스 수집
        
        Args:
            keywords: 검색할 키워드 목록
            days: 수집할 일수
        
        Returns:
            수집된 뉴스 목록
        """
        all_news = []
        
        for keyword in keywords:
            print(f"'{keyword}' 키워드로 뉴스 수집 중...")
            
            # 최근 N일간의 뉴스 수집
            for i in range(days):
                date = datetime.now() - timedelta(days=i)
                date_str = date.strftime("%Y%m%d")
                
                # 날짜별 검색
                query = f"{keyword} {date_str}"
                result = self.search_news(query, display=100, sort="date")
                
                if "items" in result:
                    for item in result["items"]:
                        # 중복 제거를 위한 ID 생성
                        news_id = f"{item['title']}_{item['pubDate']}"
                        
                        news_item = {
                            "id": news_id,
                            "title": item["title"],
                            "description": item["description"],
                            "link": item["link"],
                            "pubDate": item["pubDate"],
                            "keyword": keyword,
                            "collected_at": datetime.now().isoformat()
                        }
                        
                        all_news.append(news_item)
                
                # API 호출 제한을 위한 대기
                time.sleep(0.1)
        
        # 중복 제거
        unique_news = []
        seen_ids = set()
        
        for news in all_news:
            if news["id"] not in seen_ids:
                unique_news.append(news)
                seen_ids.add(news["id"])
        
        print(f"총 {len(unique_news)}개의 뉴스를 수집했습니다.")
        return unique_news
    
    def save_to_json(self, news_list: List[Dict[str, Any]], filename: str = None):
        """뉴스 데이터를 JSON 파일로 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"news_data_{timestamp}.json"
        
        filepath = os.path.join("..", "database", "raw_data", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        
        print(f"뉴스 데이터가 {filepath}에 저장되었습니다.")

def main():
    """메인 실행 함수"""
    collector = NaverNewsCollector()
    
    # 정치 관련 키워드
    political_keywords = [
        "국회",
        "정치",
        "정부",
        "대통령",
        "국무총리",
        "정당",
        "선거",
        "정책",
        "법안",
        "예산"
    ]
    
    # 뉴스 수집
    news_data = collector.collect_political_news(political_keywords, days=7)
    
    # JSON 파일로 저장
    collector.save_to_json(news_data)
    
    print("뉴스 수집이 완료되었습니다!")

if __name__ == "__main__":
    main()
