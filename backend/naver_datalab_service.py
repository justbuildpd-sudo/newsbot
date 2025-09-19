#!/usr/bin/env python3
"""
네이버 데이터랩 검색어 트렌드 API 서비스
정치인별 검색량 트렌드 분석
"""

import requests
import json
import time
from datetime import datetime, timedelta
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NaverDatalabService:
    def __init__(self):
        # 네이버 개발자 API 정보 (뉴스 API와 동일)
        self.client_id = "kXwlSsFmb055ku9rWyx1"
        self.client_secret = "JZqw_LTiq_"
        self.base_url = "https://openapi.naver.com/v1/datalab/search"
        
        # 요청 헤더
        self.headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "Content-Type": "application/json"
        }
        
        # 정치인 목록 로드
        self.load_politicians()
        
    def load_politicians(self):
        """22대 국회의원 목록 로드"""
        try:
            with open('22nd_assembly_members_300.json', 'r', encoding='utf-8') as f:
                members = json.load(f)
            self.politicians = [member.get('naas_nm', '') for member in members if member.get('naas_nm')]
            logger.info(f"정치인 목록 로드 완료: {len(self.politicians)}명")
        except FileNotFoundError:
            try:
                with open('../22nd_assembly_members_300.json', 'r', encoding='utf-8') as f:
                    members = json.load(f)
                self.politicians = [member.get('naas_nm', '') for member in members if member.get('naas_nm')]
                logger.info(f"정치인 목록 로드 완료: {len(self.politicians)}명")
            except FileNotFoundError:
                self.politicians = ["이재명", "한동훈", "조국", "정청래", "김기현"]
                logger.warning("정치인 데이터 파일을 찾을 수 없어 기본 목록 사용")
    
    def get_search_trend(self, keywords, start_date, end_date, time_unit="date", device="", gender="", age=""):
        """검색어 트렌드 조회"""
        try:
            # 요청 데이터 구성
            request_body = {
                "startDate": start_date,
                "endDate": end_date,
                "timeUnit": time_unit,  # date, week, month
                "keywordGroups": [
                    {
                        "groupName": keyword,
                        "keywords": [keyword]
                    } for keyword in keywords
                ]
            }
            
            # 옵션 파라미터 추가
            if device:
                request_body["device"] = device  # pc, mo
            if gender:
                request_body["gender"] = gender  # m, f
            if age:
                request_body["age"] = age  # 1~11 (10세 단위)
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=json.dumps(request_body, ensure_ascii=False).encode('utf-8'),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"트렌드 조회 성공: {len(keywords)}개 키워드")
                return data
            else:
                logger.error(f"데이터랩 API 오류: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"트렌드 조회 오류: {e}")
            return None
    
    def get_politician_trend(self, politician_name, days=30):
        """특정 정치인 검색 트렌드"""
        try:
            # 날짜 범위 설정
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # 정치인과 관련 키워드들
            keywords = [
                politician_name,
                f"{politician_name} 의원",
                f"{politician_name} 국회의원"
            ]
            
            trend_data = self.get_search_trend(
                keywords, 
                start_date_str, 
                end_date_str, 
                time_unit="date"
            )
            
            if trend_data:
                return self.process_trend_data(trend_data, politician_name)
            else:
                return None
                
        except Exception as e:
            logger.error(f"{politician_name} 트렌드 조회 오류: {e}")
            return None
    
    def get_politicians_comparison_trend(self, politicians, days=30):
        """여러 정치인 검색량 비교"""
        try:
            # 날짜 범위 설정
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # 최대 5명까지 비교 (API 제한)
            compare_politicians = politicians[:5]
            
            trend_data = self.get_search_trend(
                compare_politicians,
                start_date_str,
                end_date_str,
                time_unit="date"
            )
            
            if trend_data:
                return self.process_comparison_data(trend_data, compare_politicians)
            else:
                return None
                
        except Exception as e:
            logger.error(f"정치인 비교 트렌드 조회 오류: {e}")
            return None
    
    def process_trend_data(self, trend_data, politician_name):
        """트렌드 데이터 가공"""
        try:
            results = trend_data.get('results', [])
            if not results:
                return None
            
            processed_data = {
                'politician': politician_name,
                'period': {
                    'start': trend_data.get('startDate'),
                    'end': trend_data.get('endDate')
                },
                'trends': [],
                'statistics': {}
            }
            
            # 각 키워드별 트렌드 데이터 처리
            for result in results:
                keyword_data = {
                    'keyword': result.get('title'),
                    'data': result.get('data', [])
                }
                processed_data['trends'].append(keyword_data)
            
            # 통계 계산
            if processed_data['trends']:
                main_trend = processed_data['trends'][0]['data']
                if main_trend:
                    values = [point.get('ratio', 0) for point in main_trend]
                    processed_data['statistics'] = {
                        'average': sum(values) / len(values) if values else 0,
                        'max': max(values) if values else 0,
                        'min': min(values) if values else 0,
                        'total_points': len(values)
                    }
            
            return processed_data
            
        except Exception as e:
            logger.error(f"트렌드 데이터 처리 오류: {e}")
            return None
    
    def process_comparison_data(self, trend_data, politicians):
        """비교 트렌드 데이터 가공"""
        try:
            results = trend_data.get('results', [])
            if not results:
                return None
            
            processed_data = {
                'politicians': politicians,
                'period': {
                    'start': trend_data.get('startDate'),
                    'end': trend_data.get('endDate')
                },
                'comparison': [],
                'ranking': []
            }
            
            # 각 정치인별 트렌드 데이터
            for result in results:
                politician_trend = {
                    'politician': result.get('title'),
                    'data': result.get('data', []),
                    'average': 0
                }
                
                # 평균 검색량 계산
                data_points = result.get('data', [])
                if data_points:
                    values = [point.get('ratio', 0) for point in data_points]
                    politician_trend['average'] = sum(values) / len(values)
                
                processed_data['comparison'].append(politician_trend)
            
            # 평균 검색량 기준 랭킹
            processed_data['ranking'] = sorted(
                processed_data['comparison'],
                key=lambda x: x['average'],
                reverse=True
            )
            
            return processed_data
            
        except Exception as e:
            logger.error(f"비교 데이터 처리 오류: {e}")
            return None
    
    def get_weekly_trend(self, politicians, weeks=4):
        """주간 트렌드 조회"""
        days = weeks * 7
        return self.get_politicians_comparison_trend(politicians, days)
    
    def get_monthly_trend(self, politicians, months=3):
        """월간 트렌드 조회"""
        days = months * 30
        return self.get_politicians_comparison_trend(politicians, days)
    
    def save_trend_data(self, trend_data, filename=None):
        """트렌드 데이터 저장"""
        if filename is None:
            filename = f"trend_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(trend_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"트렌드 데이터 저장 완료: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"트렌드 데이터 저장 오류: {e}")
            return None

def main():
    """메인 실행 함수"""
    service = NaverDatalabService()
    
    print("📈 네이버 데이터랩 검색어 트렌드 API 테스트")
    print(f"📊 정치인 수: {len(service.politicians)}명")
    
    # 주요 정치인 트렌드 비교 (최근 30일)
    major_politicians = ["이재명", "한동훈", "조국", "정청래", "김기현"]
    
    print(f"\n🔍 주요 정치인 트렌드 비교 (최근 30일)")
    comparison_data = service.get_politicians_comparison_trend(major_politicians, days=30)
    
    if comparison_data:
        print("✅ 트렌드 비교 데이터 수집 성공")
        
        # 랭킹 출력
        print("\n📊 검색량 랭킹:")
        for i, politician_data in enumerate(comparison_data['ranking']):
            politician = politician_data['politician']
            average = politician_data['average']
            print(f"  {i+1}. {politician}: 평균 검색량 {average:.2f}")
        
        # 데이터 저장
        filename = service.save_trend_data(comparison_data, 'politicians_trend_comparison.json')
        if filename:
            print(f"\n💾 트렌드 데이터 저장: {filename}")
    else:
        print("❌ 트렌드 데이터 수집 실패")
    
    # 개별 정치인 상세 트렌드 (이재명)
    print(f"\n🔍 이재명 상세 트렌드 (최근 30일)")
    individual_trend = service.get_politician_trend("이재명", days=30)
    
    if individual_trend:
        print("✅ 개별 트렌드 데이터 수집 성공")
        stats = individual_trend.get('statistics', {})
        print(f"📊 통계: 평균 {stats.get('average', 0):.2f}, 최대 {stats.get('max', 0)}, 최소 {stats.get('min', 0)}")
        
        # 데이터 저장
        filename = service.save_trend_data(individual_trend, 'lee_jaemyung_trend.json')
        if filename:
            print(f"💾 개별 트렌드 저장: {filename}")
    else:
        print("❌ 개별 트렌드 데이터 수집 실패")

if __name__ == "__main__":
    main()

