#!/usr/bin/env python3
"""
국회의원 API 데이터 수집 스크립트
- 국회의원 상세정보조회 API를 3000번 호출
- 수집된 데이터를 JSON 파일로 저장
"""

import requests
import json
import time
import random
from datetime import datetime
import xml.etree.ElementTree as ET
import os

class AssemblyDataCollector:
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
    
    def get_member_list(self):
        """국회의원 목록 조회"""
        print("국회의원 목록 조회 중...")
        
        params = {
            'numOfRows': 1000,  # 최대 1000명
            'pageNo': 1
        }
        
        xml_content = self.call_assembly_api('getMemberList', params)
        if xml_content:
            members = self.parse_xml_response(xml_content)
            print(f"총 {len(members)}명의 국회의원 목록 조회 완료")
            return members
        return []
    
    def get_member_detail(self, member_id):
        """국회의원 상세 정보 조회"""
        params = {
            'dept_cd': member_id
        }
        
        xml_content = self.call_assembly_api('getMemberDetailInfo', params)
        if xml_content:
            details = self.parse_xml_response(xml_content)
            return details[0] if details else None
        return None
    
    def collect_all_data(self):
        """전체 데이터 수집"""
        print("=== 국회의원 데이터 수집 시작 ===")
        print(f"목표: {self.max_requests}번 API 호출")
        
        # 1단계: 국회의원 목록 조회
        members = self.get_member_list()
        if not members:
            print("국회의원 목록 조회 실패")
            return
        
        print(f"수집할 국회의원 수: {len(members)}")
        
        # 2단계: 각 의원의 상세 정보 조회
        for i, member in enumerate(members):
            if self.total_requests >= self.max_requests:
                print(f"최대 요청 수({self.max_requests})에 도달했습니다.")
                break
                
            member_id = member.get('dept_cd', '')
            if not member_id:
                continue
                
            print(f"[{i+1}/{len(members)}] {member.get('empNm', 'Unknown')} 상세 정보 조회 중...")
            
            # 상세 정보 조회
            detail = self.get_member_detail(member_id)
            self.total_requests += 1
            
            if detail:
                # 기본 정보와 상세 정보 결합
                combined_data = {**member, **detail}
                combined_data['collected_at'] = datetime.now().isoformat()
                combined_data['request_number'] = self.total_requests
                
                self.collected_data.append(combined_data)
                print(f"  ✅ 성공: {member.get('empNm', 'Unknown')}")
            else:
                self.failed_requests.append({
                    'member_id': member_id,
                    'member_name': member.get('empNm', 'Unknown'),
                    'request_number': self.total_requests
                })
                print(f"  ❌ 실패: {member.get('empNm', 'Unknown')}")
            
            # API 호출 간격 조절 (1-3초 랜덤)
            delay = random.uniform(1, 3)
            time.sleep(delay)
            
            # 진행 상황 출력
            if (i + 1) % 50 == 0:
                print(f"\n=== 진행 상황 ===")
                print(f"완료: {i + 1}/{len(members)}")
                print(f"성공: {len(self.collected_data)}")
                print(f"실패: {len(self.failed_requests)}")
                print(f"총 API 호출: {self.total_requests}")
                print("================\n")
        
        print(f"\n=== 데이터 수집 완료 ===")
        print(f"총 API 호출: {self.total_requests}")
        print(f"성공: {len(self.collected_data)}")
        print(f"실패: {len(self.failed_requests)}")
        print("=====================")
    
    def save_data(self):
        """수집된 데이터 저장"""
        # 성공한 데이터 저장
        success_file = 'collected_assembly_members.json'
        with open(success_file, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
        print(f"성공 데이터 저장: {success_file} ({len(self.collected_data)}명)")
        
        # 실패한 요청 저장
        if self.failed_requests:
            failed_file = 'failed_assembly_requests.json'
            with open(failed_file, 'w', encoding='utf-8') as f:
                json.dump(self.failed_requests, f, ensure_ascii=False, indent=2)
            print(f"실패 데이터 저장: {failed_file} ({len(self.failed_requests)}건)")
        
        # 수집 통계 저장
        stats = {
            'collection_date': datetime.now().isoformat(),
            'total_requests': self.total_requests,
            'successful_collections': len(self.collected_data),
            'failed_requests': len(self.failed_requests),
            'success_rate': f"{(len(self.collected_data) / self.total_requests * 100):.2f}%" if self.total_requests > 0 else "0%"
        }
        
        stats_file = 'collection_stats.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"수집 통계 저장: {stats_file}")

def main():
    collector = AssemblyDataCollector()
    
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
