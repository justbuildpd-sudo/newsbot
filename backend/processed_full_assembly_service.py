#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
전체 국회의원 데이터 서비스
309명의 22대 국회의원 데이터를 제공하는 서비스
"""

import json
import os
from typing import List, Dict, Optional

class ProcessedFullAssemblyService:
    def __init__(self):
        self.members = []
        self.stats = {}
        self.load_data()
    
    def load_data(self):
        """데이터 로드"""
        try:
            # 의원 데이터 로드
            members_file = os.path.join(os.path.dirname(__file__), 'processed_full_assembly_members.json')
            if os.path.exists(members_file):
                with open(members_file, 'r', encoding='utf-8') as f:
                    self.members = json.load(f)
            
            # 통계 데이터 로드
            stats_file = os.path.join(os.path.dirname(__file__), 'processed_full_assembly_stats.json')
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
            
            print(f"전체 국회의원 데이터 로드 완료: {len(self.members)}명")
            
        except Exception as e:
            print(f"데이터 로드 오류: {e}")
            self.members = []
            self.stats = {}
    
    def get_all_members(self) -> List[Dict]:
        """전체 의원 목록 반환"""
        return self.members
    
    def get_member_by_id(self, member_id: str) -> Optional[Dict]:
        """ID로 의원 정보 조회"""
        for member in self.members:
            if member.get('id') == member_id:
                return member
        return None
    
    def get_members_by_party(self, party: str) -> List[Dict]:
        """정당별 의원 목록 반환"""
        return [member for member in self.members if member.get('party') == party]
    
    def get_members_by_committee(self, committee: str) -> List[Dict]:
        """위원회별 의원 목록 반환"""
        return [member for member in self.members if member.get('committee') == committee]
    
    def get_members_by_orientation(self, orientation: str) -> List[Dict]:
        """정치성향별 의원 목록 반환"""
        return [member for member in self.members if member.get('orientation') == orientation]
    
    def search_members(self, query: str) -> List[Dict]:
        """의원 검색 (이름, 정당, 위원회, 지역)"""
        query = query.lower()
        results = []
        
        for member in self.members:
            # 이름 검색
            if query in member.get('name', '').lower():
                results.append(member)
                continue
            
            # 정당 검색
            if query in member.get('party', '').lower():
                results.append(member)
                continue
            
            # 위원회 검색
            if query in member.get('committee', '').lower():
                results.append(member)
                continue
            
            # 지역 검색
            if query in member.get('district', '').lower():
                results.append(member)
                continue
        
        return results
    
    def get_top_members(self, limit: int = 20) -> List[Dict]:
        """상위 의원 목록 반환 (정당별 대표)"""
        # 정당별로 대표 의원 선택
        party_representatives = {}
        
        for member in self.members:
            party = member.get('party', '정당 정보 없음')
            if party not in party_representatives:
                party_representatives[party] = member
        
        # 정당별 대표 의원들을 리스트로 변환
        representatives = list(party_representatives.values())
        
        # 추가 의원들로 채우기
        remaining_slots = limit - len(representatives)
        if remaining_slots > 0:
            # 이미 선택된 의원들 제외
            selected_ids = {member.get('id') for member in representatives}
            additional_members = [
                member for member in self.members 
                if member.get('id') not in selected_ids
            ][:remaining_slots]
            representatives.extend(additional_members)
        
        return representatives[:limit]
    
    def get_statistics(self) -> Dict:
        """통계 정보 반환"""
        return self.stats
    
    def get_party_list(self) -> List[str]:
        """정당 목록 반환"""
        parties = set()
        for member in self.members:
            party = member.get('party')
            if party:
                parties.add(party)
        return sorted(list(parties))
    
    def get_committee_list(self) -> List[str]:
        """위원회 목록 반환"""
        committees = set()
        for member in self.members:
            committee = member.get('committee')
            if committee:
                committees.add(committee)
        return sorted(list(committees))
    
    def get_orientation_list(self) -> List[str]:
        """정치성향 목록 반환"""
        orientations = set()
        for member in self.members:
            orientation = member.get('orientation')
            if orientation:
                orientations.add(orientation)
        return sorted(list(orientations))

# 전역 인스턴스
processed_full_assembly_service = ProcessedFullAssemblyService()
