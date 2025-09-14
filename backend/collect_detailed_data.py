#!/usr/bin/env python3
"""
국회의원 상세 정보 3000번 호출 수집 스크립트
- 기존 API 서비스 사용
- 298명의 의원에 대해 상세 정보 수집
"""

import json
import time
import random
from datetime import datetime
from assembly_api_service import assembly_api

class DetailedDataCollector:
    def __init__(self):
        self.collected_data = []
        self.failed_requests = []
        self.total_requests = 0
        self.max_requests = 3000
        self.member_list = []
        
    def load_member_list(self):
        """국회의원 목록 로드"""
        print("국회의원 목록 로드 중...")
        self.member_list = assembly_api.get_member_list()
        print(f"총 {len(self.member_list)}명의 국회의원 목록 로드 완료")
        
        # ID가 있는 의원들만 필터링
        valid_members = [m for m in self.member_list if m.get('id')]
        print(f"유효한 ID를 가진 의원: {len(valid_members)}명")
        
        return valid_members
    
    def collect_detailed_data(self):
        """상세 정보 수집"""
        print("=== 국회의원 상세 정보 수집 시작 ===")
        print(f"목표: {self.max_requests}번 API 호출")
        
        # 의원 목록 로드
        valid_members = self.load_member_list()
        
        if not valid_members:
            print("수집할 의원이 없습니다.")
            return
        
        # 각 의원에 대해 상세 정보 수집 (여러 번 반복)
        iteration = 0
        while self.total_requests < self.max_requests and valid_members:
            iteration += 1
            print(f"\n=== 반복 {iteration} 시작 ===")
            
            for i, member in enumerate(valid_members):
                if self.total_requests >= self.max_requests:
                    print(f"최대 요청 수({self.max_requests})에 도달했습니다.")
                    break
                
                member_id = member.get('id')
                if not member_id:
                    continue
                
                print(f"[{self.total_requests + 1}/{self.max_requests}] {member.get('name', 'Unknown')} 상세 정보 조회 중...")
                
                # 상세 정보 조회
                detail = assembly_api.get_member_detail(member_id)
                self.total_requests += 1
                
                if detail and detail.get('items'):
                    # 기본 정보와 상세 정보 결합
                    combined_data = {
                        **member,
                        'detailed_info': detail,
                        'collected_at': datetime.now().isoformat(),
                        'request_number': self.total_requests,
                        'iteration': iteration
                    }
                    
                    self.collected_data.append(combined_data)
                    print(f"  ✅ 성공: {member.get('name', 'Unknown')}")
                else:
                    self.failed_requests.append({
                        'member_id': member_id,
                        'member_name': member.get('name', 'Unknown'),
                        'request_number': self.total_requests,
                        'iteration': iteration
                    })
                    print(f"  ❌ 실패: {member.get('name', 'Unknown')}")
                
                # API 호출 간격 조절 (1-3초 랜덤)
                delay = random.uniform(1, 3)
                time.sleep(delay)
                
                # 진행 상황 출력
                if (self.total_requests) % 50 == 0:
                    print(f"\n=== 진행 상황 ===")
                    print(f"완료 요청: {self.total_requests}/{self.max_requests}")
                    print(f"성공: {len(self.collected_data)}")
                    print(f"실패: {len(self.failed_requests)}")
                    print(f"현재 반복: {iteration}")
                    print("================\n")
            
            # 모든 의원을 한 번씩 처리했으면 다시 처음부터
            if self.total_requests < self.max_requests:
                print(f"반복 {iteration} 완료. 다음 반복 시작...")
        
        print(f"\n=== 데이터 수집 완료 ===")
        print(f"총 API 호출: {self.total_requests}")
        print(f"성공: {len(self.collected_data)}")
        print(f"실패: {len(self.failed_requests)}")
        print(f"총 반복: {iteration}")
        print("=====================")
    
    def save_data(self):
        """수집된 데이터 저장"""
        # 성공한 데이터 저장
        success_file = 'collected_detailed_assembly_members.json'
        with open(success_file, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
        print(f"성공 데이터 저장: {success_file} ({len(self.collected_data)}건)")
        
        # 실패한 요청 저장
        if self.failed_requests:
            failed_file = 'failed_detailed_requests.json'
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
            'unique_members': len(set(item['id'] for item in self.collected_data if item.get('id'))),
            'total_members_available': len(self.member_list)
        }
        
        stats_file = 'detailed_collection_stats.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"수집 통계 저장: {stats_file}")
        
        # 샘플 데이터 출력
        if self.collected_data:
            print(f"\n=== 샘플 데이터 (첫 번째 항목) ===")
            sample = self.collected_data[0]
            print(f"이름: {sample.get('name', 'N/A')}")
            print(f"정당: {sample.get('party', 'N/A')}")
            print(f"지역구: {sample.get('district', 'N/A')}")
            print(f"상세 정보 키: {list(sample.get('detailed_info', {}).keys())}")
            print(f"수집 시간: {sample.get('collected_at', 'N/A')}")
            print("================================")

def main():
    collector = DetailedDataCollector()
    
    try:
        collector.collect_detailed_data()
        collector.save_data()
        
        print("\n🎉 상세 정보 수집이 완료되었습니다!")
        print(f"수집된 상세 정보: {len(collector.collected_data)}건")
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
        collector.save_data()
    except Exception as e:
        print(f"오류 발생: {e}")
        collector.save_data()

if __name__ == "__main__":
    main()
