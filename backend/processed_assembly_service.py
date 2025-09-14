#!/usr/bin/env python3
"""
가공된 국회의원 데이터 서비스
- processed_assembly_members.json 파일을 사용
- newsbot.kr에서 사용할 수 있는 API 제공
"""

import json
import os
from typing import List, Dict, Optional

class ProcessedAssemblyService:
    def __init__(self):
        self.data_file = 'processed_assembly_members.json'
        self.members = []
        self.load_data()
    
    def load_data(self):
        """가공된 데이터 로드"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.members = json.load(f)
                print(f"✅ 가공된 국회의원 데이터 로드 완료: {len(self.members)}명")
            else:
                print(f"❌ 데이터 파일을 찾을 수 없습니다: {self.data_file}")
                self.members = []
        except Exception as e:
            print(f"❌ 데이터 로드 오류: {e}")
            self.members = []
    
    def get_all_members(self) -> List[Dict]:
        """모든 국회의원 목록 반환"""
        return self.members
    
    def get_members_by_party(self, party_name: str) -> List[Dict]:
        """정당별 국회의원 목록 반환"""
        return [member for member in self.members if member.get('party', '') == party_name]
    
    def get_member_by_id(self, member_id: str) -> Optional[Dict]:
        """ID로 특정 국회의원 조회"""
        for member in self.members:
            if member.get('id') == member_id:
                return member
        return None
    
    def search_members(self, query: str) -> List[Dict]:
        """이름으로 국회의원 검색"""
        query = query.lower()
        results = []
        
        for member in self.members:
            name = member.get('name', '').lower()
            name_hanja = member.get('name_hanja', '').lower()
            name_english = member.get('name_english', '').lower()
            district = member.get('district', '').lower()
            party = member.get('party', '').lower()
            
            if (query in name or 
                query in name_hanja or 
                query in name_english or 
                query in district or 
                query in party):
                results.append(member)
        
        return results
    
    def get_top_influential_members(self, limit: int = 20) -> List[Dict]:
        """영향력 높은 국회의원 조회 (언급 횟수 기준)"""
        sorted_members = sorted(
            self.members, 
            key=lambda x: x.get('mention_count', 0), 
            reverse=True
        )
        return sorted_members[:limit]
    
    def get_members_by_committee(self, committee: str) -> List[Dict]:
        """위원회별 국회의원 목록 반환"""
        return [member for member in self.members if committee in member.get('committee', '')]
    
    def get_members_by_orientation(self, orientation: str) -> List[Dict]:
        """정치 성향별 국회의원 목록 반환"""
        return [member for member in self.members if member.get('political_orientation', '') == orientation]
    
    def get_statistics(self) -> Dict:
        """통계 정보 반환"""
        total_members = len(self.members)
        
        # 정당별 분포
        party_distribution = {}
        for member in self.members:
            party = member.get('party', '미분류')
            party_distribution[party] = party_distribution.get(party, 0) + 1
        
        # 위원회별 분포
        committee_distribution = {}
        for member in self.members:
            committee = member.get('committee', '미분류')
            committee_distribution[committee] = committee_distribution.get(committee, 0) + 1
        
        # 정치 성향별 분포
        orientation_distribution = {}
        for member in self.members:
            orientation = member.get('political_orientation', '미분류')
            orientation_distribution[orientation] = orientation_distribution.get(orientation, 0) + 1
        
        return {
            'total_members': total_members,
            'party_distribution': party_distribution,
            'committee_distribution': committee_distribution,
            'orientation_distribution': orientation_distribution
        }
    
    def update_mention_count(self, member_id: str, mention_count: int):
        """특정 의원의 언급 횟수 업데이트"""
        for member in self.members:
            if member.get('id') == member_id:
                member['mention_count'] = mention_count
                # 영향력 점수 재계산 (언급 횟수 기반)
                member['influence_score'] = min(mention_count * 0.1, 10.0)
                break
    
    def refresh_data(self):
        """데이터 새로고침"""
        self.load_data()

# 전역 인스턴스
processed_assembly_service = ProcessedAssemblyService()
