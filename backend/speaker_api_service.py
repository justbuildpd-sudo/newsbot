#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
의원 발화 API 서비스
의원 위젯 클릭 시 발화 정보 제공
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import re

class SpeakerAPIService:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.speaker_records_dir = os.path.join(data_dir, "speaker_records")
        self.politicians_data = self._load_politicians_data()
        self.speeches_data = self._load_speeches_data()
    
    def _load_politicians_data(self) -> List[Dict]:
        """의원 데이터 로드"""
        try:
            with open('backend/processed_assembly_members.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"의원 데이터 로드 실패: {e}")
            return []
    
    def _load_speeches_data(self) -> Dict:
        """발화 데이터 로드 (시뮬레이션)"""
        # 실제로는 데이터베이스나 파일에서 로드
        # 여기서는 시뮬레이션 데이터 생성
        return self._generate_simulation_speeches()
    
    def _generate_simulation_speeches(self) -> Dict:
        """발화 데이터 시뮬레이션"""
        import random
        from datetime import datetime, timedelta
        
        committees = [
            '법제사법위원회', '기획재정위원회', '과학기술정보방송통신위원회',
            '행정안전위원회', '문화체육관광위원회', '환경노동위원회',
            '보건복지위원회', '교육위원회', '국방위원회', '외교통일위원회'
        ]
        
        meeting_types = ['상임위원회', '특별위원회', '본회의', '국정감사']
        
        speeches_data = {}
        
        for politician in self.politicians_data[:20]:  # 처음 20명만
            politician_id = politician.get('id', '')
            politician_name = politician.get('name', '')
            
            # 3-8개의 발화 데이터 생성
            num_speeches = random.randint(3, 8)
            speeches = []
            
            for i in range(num_speeches):
                days_ago = random.randint(1, 365)
                speech_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                
                committee = random.choice(committees)
                meeting_type = random.choice(meeting_types)
                session_num = random.randint(400, 450)
                meeting_num = random.randint(1, 20)
                
                meeting_title = f'제22대 국회 제{session_num}차 {committee}'
                
                speech_contents = [
                    f'{politician_name} 의원입니다. {committee}에서 중요한 정책에 대해 발언하겠습니다.',
                    f'안녕하세요. {politician_name}입니다. 오늘 회의에서 {random.choice(["예산안", "법안", "정책"])}에 대해 말씀드리겠습니다.',
                    f'{politician_name} 의원으로서 국민의 소리에 귀 기울이며 정책을 제안하겠습니다.',
                    f'정당한 의견을 제시하고자 합니다. {politician_name}입니다.',
                    f'국정감사에서 중요한 사안에 대해 질의하겠습니다. {politician_name} 의원입니다.',
                    f'{politician_name}입니다. {committee}에서 {random.choice(["예산", "법안", "정책"])} 심사에 대해 발언하겠습니다.'
                ]
                
                speech = {
                    'id': f'{politician_id}_{i+1}',
                    'meeting_title': meeting_title,
                    'date': speech_date,
                    'committee': committee,
                    'meeting_type': meeting_type,
                    'session_num': session_num,
                    'meeting_num': meeting_num,
                    'content': random.choice(speech_contents),
                    'politician_id': politician_id,
                    'politician_name': politician_name
                }
                
                speeches.append(speech)
            
            speeches_data[politician_id] = speeches
        
        return speeches_data
    
    def get_politician_speeches(self, politician_id: str) -> Dict:
        """특정 의원의 발화 정보 조회"""
        politician = self._get_politician_by_id(politician_id)
        if not politician:
            return {"error": "의원을 찾을 수 없습니다."}
        
        speeches = self.speeches_data.get(politician_id, [])
        
        # 발화 통계 계산
        total_speeches = len(speeches)
        active_committees = self._get_active_committees(speeches)
        recent_speech_date = self._get_recent_speech_date(speeches)
        
        # 시계열 리스트 생성
        timeline = self._create_timeline(speeches)
        
        return {
            "politician": politician,
            "speeches": speeches,
            "statistics": {
                "total_speeches": total_speeches,
                "active_committees": active_committees,
                "recent_speech_date": recent_speech_date
            },
            "timeline": timeline
        }
    
    def _get_politician_by_id(self, politician_id: str) -> Optional[Dict]:
        """ID로 의원 조회"""
        for politician in self.politicians_data:
            if politician.get('id') == politician_id:
                return politician
        return None
    
    def _get_active_committees(self, speeches: List[Dict]) -> List[Dict]:
        """활발한 위원회 목록"""
        if not speeches:
            return []
        
        committee_counts = {}
        for speech in speeches:
            committee = speech.get('committee', '')
            if committee:
                committee_counts[committee] = committee_counts.get(committee, 0) + 1
        
        # 상위 5개 위원회 반환
        sorted_committees = sorted(committee_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"name": name, "count": count} for name, count in sorted_committees[:5]]
    
    def _get_recent_speech_date(self, speeches: List[Dict]) -> str:
        """최근 발화 날짜"""
        if not speeches:
            return "없음"
        
        dates = [speech.get('date', '') for speech in speeches if speech.get('date')]
        if dates:
            return max(dates)
        return "없음"
    
    def _create_timeline(self, speeches: List[Dict]) -> List[Dict]:
        """시계열 리스트 생성"""
        if not speeches:
            return []
        
        # 날짜별로 정렬 (최신순)
        sorted_speeches = sorted(speeches, key=lambda x: x.get('date', ''), reverse=True)
        
        timeline = []
        for speech in sorted_speeches:
            timeline_item = {
                "date": speech.get('date', ''),
                "meeting_title": speech.get('meeting_title', ''),
                "committee": speech.get('committee', ''),
                "meeting_type": speech.get('meeting_type', ''),
                "speech_id": speech.get('id', ''),
                "content_preview": speech.get('content', '')[:100] + '...' if len(speech.get('content', '')) > 100 else speech.get('content', '')
            }
            timeline.append(timeline_item)
        
        return timeline
    
    def get_speech_detail(self, speech_id: str) -> Dict:
        """특정 발화 상세 정보 조회"""
        for politician_id, speeches in self.speeches_data.items():
            for speech in speeches:
                if speech.get('id') == speech_id:
                    return speech
        
        return {"error": "발화를 찾을 수 없습니다."}
    
    def search_speeches(self, query: str, politician_id: str = None) -> List[Dict]:
        """발화 검색"""
        results = []
        
        for pid, speeches in self.speeches_data.items():
            if politician_id and pid != politician_id:
                continue
            
            for speech in speeches:
                content = speech.get('content', '').lower()
                meeting_title = speech.get('meeting_title', '').lower()
                committee = speech.get('committee', '').lower()
                
                if query.lower() in content or query.lower() in meeting_title or query.lower() in committee:
                    results.append(speech)
        
        return results

def main():
    """테스트 실행"""
    service = SpeakerAPIService()
    
    # 첫 번째 의원의 발화 정보 조회
    if service.politicians_data:
        first_politician = service.politicians_data[0]
        politician_id = first_politician.get('id')
        
        print(f"=== {first_politician.get('name')} 의원 발화 정보 ===")
        speeches_info = service.get_politician_speeches(politician_id)
        
        print(f"총 발화 수: {speeches_info['statistics']['total_speeches']}회")
        print(f"활발한 위원회: {[c['name'] for c in speeches_info['statistics']['active_committees']]}")
        print(f"최근 발화: {speeches_info['statistics']['recent_speech_date']}")
        
        print("\\n=== 시계열 리스트 ===")
        for item in speeches_info['timeline'][:3]:
            print(f"- {item['date']}: {item['meeting_title']} ({item['committee']})")

if __name__ == "__main__":
    main()


