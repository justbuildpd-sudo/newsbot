#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로컬 저장된 국회의원 데이터 기반 서비스
샘플 데이터 절대 노출 방지
"""

import json
import os
from typing import List, Dict, Optional
from pathlib import Path

class LocalPoliticianService:
    def __init__(self, data_file: str = "politicians_data_with_party.json"):
        self.data_file = data_file
        self.politicians_data = []
        self._load_data()
    
    def _load_data(self):
        """로컬 데이터 로드"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.politicians_data = json.load(f)
                print(f"✅ 로컬 데이터 로드 완료: {len(self.politicians_data)}명")
            else:
                print(f"❌ 데이터 파일을 찾을 수 없습니다: {self.data_file}")
                self.politicians_data = []
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            self.politicians_data = []
    
    def get_all_politicians(self) -> List[Dict]:
        """모든 국회의원 정보 반환"""
        return self.politicians_data
    
    def get_politician_by_id(self, member_id: str) -> Optional[Dict]:
        """ID로 특정 국회의원 정보 조회"""
        for politician in self.politicians_data:
            if politician.get('id') == member_id or politician.get('member_number') == member_id:
                return politician
        return None
    
    def get_politicians_by_party(self, party_name: str) -> List[Dict]:
        """정당별 국회의원 조회"""
        results = []
        for politician in self.politicians_data:
            if politician.get('party', '').lower() == party_name.lower():
                results.append(politician)
        return results
    
    def search_politicians(self, query: str) -> List[Dict]:
        """이름으로 국회의원 검색"""
        results = []
        query_lower = query.lower()
        
        for politician in self.politicians_data:
            name = politician.get('name', '').lower()
            name_hanja = politician.get('name_hanja', '').lower()
            name_english = politician.get('name_english', '').lower()
            
            if (query_lower in name or 
                query_lower in name_hanja or 
                query_lower in name_english):
                results.append(politician)
        
        return results
    
    def get_politician_image_path(self, member_id: str) -> Optional[str]:
        """국회의원 이미지 경로 반환 (이미지 없으므로 None)"""
        return None
    
    def get_politician_display_text(self, member_id: str) -> str:
        """국회의원 표시 텍스트 반환 (정당명)"""
        politician = self.get_politician_by_id(member_id)
        if politician:
            return politician.get('display_text', politician.get('party', '정보없음'))
        return '정보없음'
    
    def get_politician_stats(self) -> Dict:
        """국회의원 통계 정보"""
        total_count = len(self.politicians_data)
        
        # 정당별 통계
        party_stats = {}
        for politician in self.politicians_data:
            party = politician.get('party', '정당정보없음')
            party_stats[party] = party_stats.get(party, 0) + 1
        
        return {
            'total_politicians': total_count,
            'party_distribution': party_stats,
            'data_source': 'local_with_party_info'
        }
    
    def refresh_data(self):
        """데이터 새로고침"""
        self._load_data()
    
    def is_data_loaded(self) -> bool:
        """데이터가 로드되었는지 확인"""
        return len(self.politicians_data) > 0

if __name__ == "__main__":
    service = LocalPoliticianService()
    stats = service.get_politician_stats()
    print(f"📊 국회의원 통계: {stats}")
