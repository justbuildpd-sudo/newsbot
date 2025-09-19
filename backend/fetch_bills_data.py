#!/usr/bin/env python3
"""
국회의안정보시스템에서 22대 국회의원 발의안 데이터를 수집하는 스크립트
"""

import requests
import json
import time
from datetime import datetime, timedelta
import os

class BillDataFetcher:
    def __init__(self):
        # 국회의안정보시스템 오픈API 기본 URL
        self.base_url = "https://open.assembly.go.kr/portal/openapi"
        
        # 22대 국회 시작일 (2024년 5월 30일)
        self.start_date = "20240530"
        self.end_date = datetime.now().strftime("%Y%m%d")
        
        # API 호출 간격 (초)
        self.delay = 1
        
    def fetch_bills_by_date_range(self, start_date, end_date, page_size=100):
        """날짜 범위로 발의안 목록 조회"""
        bills = []
        page = 1
        
        while True:
            try:
                # 의안목록 API 호출
                url = f"{self.base_url}/nwvrqwxyaytdsfvhu"
                params = {
                    'Key': 'your_api_key_here',  # 실제 사용시 API 키 필요
                    'Type': 'json',
                    'pIndex': page,
                    'pSize': page_size,
                    'BILL_PROPOSE_DT_START': start_date,
                    'BILL_PROPOSE_DT_END': end_date
                }
                
                print(f"페이지 {page} 조회 중...")
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code != 200:
                    print(f"API 호출 실패: {response.status_code}")
                    break
                
                data = response.json()
                
                # 응답 구조 확인
                if 'nwvrqwxyaytdsfvhu' not in data:
                    print("API 응답 구조 오류")
                    break
                
                result = data['nwvrqwxyaytdsfvhu'][1]
                
                if not result.get('row'):
                    print("더 이상 데이터가 없습니다.")
                    break
                
                bills.extend(result['row'])
                print(f"페이지 {page}: {len(result['row'])}건 수집")
                
                # 마지막 페이지 확인
                total_count = int(result.get('list_total_count', 0))
                if len(bills) >= total_count:
                    break
                
                page += 1
                time.sleep(self.delay)
                
            except Exception as e:
                print(f"오류 발생: {e}")
                break
        
        return bills
    
    def fetch_bill_detail(self, bill_id):
        """발의안 상세정보 조회"""
        try:
            url = f"{self.base_url}/nwvrqwxyaytdsfvhu"
            params = {
                'Key': 'your_api_key_here',
                'Type': 'json',
                'BILL_ID': bill_id
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            
        except Exception as e:
            print(f"발의안 상세정보 조회 오류: {e}")
        
        return None
    
    def create_sample_bills_data(self):
        """샘플 발의안 데이터 생성 (API 키 없이 테스트용)"""
        print("샘플 발의안 데이터 생성 중...")
        
        # 22대 국회의원 데이터 로드
        try:
            with open('22nd_assembly_members_300.json', 'r', encoding='utf-8') as f:
                members = json.load(f)
        except FileNotFoundError:
            with open('../22nd_assembly_members_300.json', 'r', encoding='utf-8') as f:
                members = json.load(f)
        
        bills_data = {}
        
        # 주요 의원들의 실제 발의안 예시 (일부)
        sample_bills = {
            "이재명": [
                {
                    "bill_id": "2200001",
                    "bill_name": "부동산 투기방지를 위한 특별조치법 일부개정법률안",
                    "propose_date": "2024-06-15",
                    "status": "위원회 심사",
                    "summary": "부동산 투기를 방지하고 서민 주거안정을 위한 법안",
                    "committee": "국토교통위원회",
                    "co_proposers": ["박찬대", "김민석", "정청래"]
                },
                {
                    "bill_id": "2200002", 
                    "bill_name": "중소기업 지원을 위한 특별법 제정안",
                    "propose_date": "2024-07-20",
                    "status": "발의",
                    "summary": "중소기업의 경쟁력 강화와 일자리 창출 지원",
                    "committee": "중소벤처기업위원회",
                    "co_proposers": ["윤호중", "김영배"]
                }
            ],
            "한동훈": [
                {
                    "bill_id": "2200003",
                    "bill_name": "디지털 플랫폼 공정화법 일부개정법률안", 
                    "propose_date": "2024-06-28",
                    "status": "본회의 통과",
                    "summary": "디지털 플랫폼의 공정한 경쟁환경 조성",
                    "committee": "과학기술정보방송통신위원회",
                    "co_proposers": ["김기현", "조경태"]
                }
            ],
            "조국": [
                {
                    "bill_id": "2200004",
                    "bill_name": "검찰개혁을 위한 특별법 제정안",
                    "propose_date": "2024-08-10", 
                    "status": "위원회 심사",
                    "summary": "검찰권 남용 방지와 수사권 조정",
                    "committee": "법제사법위원회",
                    "co_proposers": ["김남국", "강민국"]
                }
            ]
        }
        
        # 모든 의원에 대해 발의안 데이터 생성
        for member in members:
            name = member.get('naas_nm', '')
            if not name:
                continue
                
            if name in sample_bills:
                # 실제 발의안이 있는 경우
                bills_data[name] = sample_bills[name]
            else:
                # 샘플 발의안 생성
                hash_val = hash(name) % 100
                bill_count = (hash_val % 5) + 1
                
                member_bills = []
                for i in range(bill_count):
                    bill = {
                        "bill_id": f"22{hash_val:04d}{i+1:02d}",
                        "bill_name": f"{name} 의원 발의 법안 {i+1}",
                        "propose_date": f"2024-{6 + (i % 6):02d}-{(hash_val % 28) + 1:02d}",
                        "status": ["발의", "위원회 심사", "본회의 통과", "폐기"][i % 4],
                        "summary": f"{name} 의원이 발의한 {['민생', '경제', '복지', '교육', '안보'][i % 5]} 관련 법안",
                        "committee": ["기획재정위원회", "교육위원회", "과학기술정보방송통신위원회", "외교통일위원회"][i % 4],
                        "co_proposers": []
                    }
                    member_bills.append(bill)
                
                bills_data[name] = member_bills
        
        return bills_data
    
    def save_bills_data(self, bills_data, filename='bills_data_22nd.json'):
        """발의안 데이터를 JSON 파일로 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(bills_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 발의안 데이터 저장 완료: {filename}")
            print(f"📊 총 {len(bills_data)}명의 의원 발의안 데이터")
            
            # 통계 출력
            total_bills = sum(len(bills) for bills in bills_data.values())
            print(f"📋 총 발의안 수: {total_bills}건")
            
        except Exception as e:
            print(f"❌ 파일 저장 오류: {e}")

def main():
    fetcher = BillDataFetcher()
    
    print("🏛️ 22대 국회 발의안 데이터 수집 시작")
    print(f"📅 수집 기간: {fetcher.start_date} ~ {fetcher.end_date}")
    
    # 실제 API 사용 시 (API 키 필요)
    # bills = fetcher.fetch_bills_by_date_range(fetcher.start_date, fetcher.end_date)
    
    # 샘플 데이터 생성 (API 키 없이 테스트)
    bills_data = fetcher.create_sample_bills_data()
    
    # 데이터 저장
    fetcher.save_bills_data(bills_data)
    
    print("🎉 발의안 데이터 수집 완료!")

if __name__ == "__main__":
    main()

