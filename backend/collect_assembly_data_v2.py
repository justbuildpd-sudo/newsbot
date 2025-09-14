#!/usr/bin/env python3
"""
국회의원 API 데이터 수집 스크립트 v2
- getMemberCurrStateList 엔드포인트 사용 (200 응답 확인됨)
- 국회의원 현황 정보 수집
"""

import requests
import json
import time
import random
from datetime import datetime
import xml.etree.ElementTree as ET
import os

class AssemblyDataCollectorV2:
    def __init__(self):
        self.api_key = "RoSdWk52fty0NNpB6SxxmgXiC2vEXOpOSw1bHPcRxuBEmcXi91fT52waWOMDo67trsxJcm59pVGNYExnLOa8A=="
        self.base_url = "https://apis.data.go.kr/9710000/NationalAssemblyInfoService"
        self.collected_data = []
        self.failed_requests = []
        self.total_requests = 0
        self.max_requests = 3000
        
    def call_assembly_api(self, endpoint, params):
        """국회 API 호출"""
        try:
            url = f"{self.base_url}/{endpoint}"
            params['serviceKey'] = self.api_key
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.text
        except Exception as e:
            print(f"API 호출 오류: {e}")
            return None
    
    def parse_xml_response(self, xml_content):
        """XML 응답 파싱"""
        try:
            root = ET.fromstring(xml_content)
            items = root.findall('.//item')
            
            parsed_data = []
            for item in items:
                data = {}
                for child in item:
                    data[child.tag] = child.text
                parsed_data.append(data)
            
            return parsed_data
        except Exception as e:
            print(f"XML 파싱 오류: {e}")
            return []
    
    def get_member_curr_state_list(self, page_no=1, num_of_rows=100):
        """국회의원 현황 조회 (작동하는 엔드포인트)"""
        print(f"국회의원 현황 조회 중... (페이지: {page_no})")
        
        params = {
            'numOfRows': num_of_rows,
            'pageNo': page_no
        }
        
        xml_content = self.call_assembly_api('getMemberCurrStateList', params)
        if xml_content:
            members = self.parse_xml_response(xml_content)
            print(f"페이지 {page_no}: {len(members)}명 조회 완료")
            return members
        return []
    
    def collect_all_data(self):
        """전체 데이터 수집"""
        print("=== 국회의원 데이터 수집 시작 (v2) ===")
        print(f"목표: {self.max_requests}번 API 호출")
        print("사용 엔드포인트: getMemberCurrStateList")
        
        page_no = 1
        num_of_rows = 100  # 페이지당 100명씩
        
        while self.total_requests < self.max_requests:
            # API 호출
            members = self.get_member_curr_state_list(page_no, num_of_rows)
            self.total_requests += 1
            
            if not members:
                print(f"페이지 {page_no}에서 더 이상 데이터가 없습니다.")
                break
            
            # 데이터 처리
            for member in members:
                member['collected_at'] = datetime.now().isoformat()
                member['request_number'] = self.total_requests
                member['page_number'] = page_no
                
                self.collected_data.append(member)
            
            print(f"  ✅ 페이지 {page_no} 성공: {len(members)}명")
            print(f"  📊 누적 수집: {len(self.collected_data)}명")
            
            page_no += 1
            
            # API 호출 간격 조절 (1-3초 랜덤)
            delay = random.uniform(1, 3)
            time.sleep(delay)
            
            # 진행 상황 출력
            if page_no % 10 == 0:
                print(f"\n=== 진행 상황 ===")
                print(f"완료 페이지: {page_no - 1}")
                print(f"총 수집: {len(self.collected_data)}명")
                print(f"총 API 호출: {self.total_requests}")
                print("================\n")
        
        print(f"\n=== 데이터 수집 완료 ===")
        print(f"총 API 호출: {self.total_requests}")
        print(f"총 수집: {len(self.collected_data)}명")
        print(f"실패: {len(self.failed_requests)}")
        print("=====================")
    
    def save_data(self):
        """수집된 데이터 저장"""
        # 성공한 데이터 저장
        success_file = 'collected_assembly_members_v2.json'
        with open(success_file, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
        print(f"성공 데이터 저장: {success_file} ({len(self.collected_data)}명)")
        
        # 실패한 요청 저장
        if self.failed_requests:
            failed_file = 'failed_assembly_requests_v2.json'
            with open(failed_file, 'w', encoding='utf-8') as f:
                json.dump(self.failed_requests, f, ensure_ascii=False, indent=2)
            print(f"실패 데이터 저장: {failed_file} ({len(self.failed_requests)}건)")
        
        # 수집 통계 저장
        stats = {
            'collection_date': datetime.now().isoformat(),
            'total_requests': self.total_requests,
            'successful_collections': len(self.collected_data),
            'failed_requests': len(self.failed_requests),
            'success_rate': f"{(len(self.collected_data) / self.total_requests * 100):.2f}%" if self.total_requests > 0 else "0%",
            'endpoint_used': 'getMemberCurrStateList'
        }
        
        stats_file = 'collection_stats_v2.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"수집 통계 저장: {stats_file}")
        
        # 샘플 데이터 출력
        if self.collected_data:
            print(f"\n=== 샘플 데이터 (첫 번째 항목) ===")
            sample = self.collected_data[0]
            for key, value in sample.items():
                print(f"{key}: {value}")
            print("================================")

def main():
    collector = AssemblyDataCollectorV2()
    
    try:
        collector.collect_all_data()
        collector.save_data()
        
        print("\n🎉 데이터 수집이 완료되었습니다!")
        print(f"수집된 국회의원 수: {len(collector.collected_data)}")
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
        collector.save_data()
    except Exception as e:
        print(f"오류 발생: {e}")
        collector.save_data()

if __name__ == "__main__":
    main()
