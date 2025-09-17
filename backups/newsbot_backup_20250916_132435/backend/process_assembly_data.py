#!/usr/bin/env python3
"""
수집된 국회의원 데이터 가공 스크립트
- 상세 정보를 기본 정보에 통합
- newsbot.kr에서 사용할 수 있는 형태로 변환
"""

import json
from datetime import datetime
from typing import List, Dict

class AssemblyDataProcessor:
    def __init__(self):
        self.processed_data = []
        
    def load_collected_data(self, filename: str) -> List[Dict]:
        """수집된 데이터 로드"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"수집된 데이터 로드 완료: {len(data)}건")
            return data
        except Exception as e:
            print(f"데이터 로드 오류: {e}")
            return []
    
    def process_member_data(self, member: Dict) -> Dict:
        """개별 의원 데이터 가공"""
        # 기본 정보
        processed = {
            'id': member.get('id', ''),
            'name': member.get('name', ''),
            'name_hanja': member.get('name_hanja', ''),
            'name_english': member.get('name_english', ''),
            'district': member.get('district', ''),
            'terms': member.get('terms', ''),
            'image_url': member.get('image_url', ''),
            'member_number': member.get('member_number', ''),
            'mention_count': member.get('mention_count', 0),
            'influence_score': member.get('influence_score', 0.0)
        }
        
        # 상세 정보에서 추가 데이터 추출
        detailed_info = member.get('detailed_info', {})
        if detailed_info and detailed_info.get('items'):
            detail = detailed_info['items'][0]  # 첫 번째 상세 정보 사용
            
            # 정당 정보 (상세 정보에서 가져오기)
            processed['party'] = detail.get('polyNm', member.get('party', ''))
            
            # 위원회 정보 (상세 정보에서 가져오기)
            processed['committee'] = detail.get('shrtNm', member.get('committee', ''))
            
            # 생년월일
            bth_date = detail.get('bthDate', '')
            if bth_date and len(bth_date) == 8:
                processed['birth_date'] = f"{bth_date[:4]}-{bth_date[4:6]}-{bth_date[6:8]}"
            
            # 선거구 정보
            processed['election_district'] = detail.get('origNm', member.get('district', ''))
            
            # 비서진 정보
            secretary = detail.get('secretary', '')
            if secretary:
                processed['secretary'] = [s.strip() for s in secretary.split(',') if s.strip()]
            
            # 보좌진 정보
            staff = detail.get('staff', '')
            if staff:
                processed['staff'] = [s.strip() for s in staff.split(',') if s.strip()]
            
            # 홈페이지
            processed['homepage'] = detail.get('assemHomep', member.get('website', ''))
            
            # 재선 정보
            processed['reelection_info'] = detail.get('reeleGbnNm', member.get('terms', ''))
        
        # 정치 성향 재계산
        processed['political_orientation'] = self._get_political_orientation(processed.get('party', ''))
        
        # 주요 이슈 재계산
        processed['key_issues'] = self._get_key_issues(processed.get('committee', ''))
        
        # 설명 업데이트
        party = processed.get('party', '')
        district = processed.get('district', '')
        committee = processed.get('committee', '')
        
        if party and district:
            processed['description'] = f"{district} 지역구 {party} 소속"
        elif party:
            processed['description'] = f"{party} 소속"
        elif district:
            processed['description'] = f"{district} 지역구"
        else:
            processed['description'] = "국회의원"
        
        if committee:
            processed['description'] += f" ({committee})"
        
        # 연락처 정보 (기본값 설정)
        processed['phone'] = member.get('phone', '')
        processed['email'] = member.get('email', '')
        
        # 수집 정보
        processed['collected_at'] = member.get('collected_at', '')
        processed['data_source'] = '국회 공식 API'
        
        return processed
    
    def _get_political_orientation(self, party: str) -> str:
        """정당에 따른 정치 성향 판단"""
        if not party:
            return "중도성향"
            
        progressive_parties = ["더불어민주당", "정의당", "진보당", "조국혁신당", "개혁신당"]
        conservative_parties = ["국민의힘", "새누리당", "자유한국당", "새로운미래", "개혁신당"]
        
        if party in progressive_parties:
            return "진보성향"
        elif party in conservative_parties:
            return "보수성향"
        else:
            return "중도성향"
    
    def _get_key_issues(self, committee: str) -> List[str]:
        """위원회에 따른 주요 이슈 추출"""
        if not committee:
            return ["정치", "국정", "의정"]
            
        issue_mapping = {
            "환경노동위원회": ["환경보호", "노동권익", "기후변화", "에너지정책"],
            "기획재정위원회": ["경제정책", "예산", "재정", "세금정책"],
            "과학기술정보방송통신위원회": ["과학기술", "정보통신", "방송", "디지털정책"],
            "교육위원회": ["교육정책", "학교", "학생", "교육개혁"],
            "문화체육관광위원회": ["문화", "체육", "관광", "콘텐츠정책"],
            "보건복지위원회": ["보건", "복지", "의료", "사회보장"],
            "법제사법위원회": ["법제", "사법", "인권", "법치주의"],
            "행정안전위원회": ["행정", "안전", "지방자치", "공공기관"],
            "국방위원회": ["국방", "안보", "군사", "방위산업"],
            "외교통일위원회": ["외교", "통일", "국제관계", "북한정책"],
            "정보위원회": ["정보", "보안", "정보통신", "사이버보안"],
            "여성가족위원회": ["여성", "가족", "성평등", "아동정책"]
        }
        
        for key, issues in issue_mapping.items():
            if key in committee:
                return issues
        
        return ["정치", "국정", "의정"]
    
    def process_all_data(self, input_filename: str, output_filename: str):
        """전체 데이터 가공"""
        print("=== 국회의원 데이터 가공 시작 ===")
        
        # 데이터 로드
        raw_data = self.load_collected_data(input_filename)
        if not raw_data:
            print("가공할 데이터가 없습니다.")
            return
        
        # 중복 제거 (같은 ID의 의원은 마지막 데이터만 사용)
        unique_members = {}
        for member in raw_data:
            member_id = member.get('id', '')
            if member_id:
                unique_members[member_id] = member
        
        print(f"중복 제거 후: {len(unique_members)}명")
        
        # 각 의원 데이터 가공
        for member_id, member in unique_members.items():
            processed = self.process_member_data(member)
            self.processed_data.append(processed)
        
        # 정당별로 그룹화
        party_groups = {}
        for member in self.processed_data:
            party = member.get('party', '미분류')
            if party not in party_groups:
                party_groups[party] = []
            party_groups[party].append(member)
        
        print(f"\n=== 정당별 분포 ===")
        for party, members in sorted(party_groups.items()):
            print(f"{party}: {len(members)}명")
        
        # 가공된 데이터 저장
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(self.processed_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n가공된 데이터 저장: {output_filename}")
        print(f"총 {len(self.processed_data)}명의 국회의원 데이터 가공 완료")
        
        # 통계 정보 저장
        stats = {
            'processed_date': datetime.now().isoformat(),
            'total_members': len(self.processed_data),
            'party_distribution': {party: len(members) for party, members in party_groups.items()},
            'data_source': '국회 공식 API',
            'processing_version': '1.0'
        }
        
        stats_filename = 'processed_assembly_stats.json'
        with open(stats_filename, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"통계 정보 저장: {stats_filename}")
        
        # 샘플 데이터 출력
        if self.processed_data:
            print(f"\n=== 샘플 데이터 (첫 번째 의원) ===")
            sample = self.processed_data[0]
            for key, value in sample.items():
                if isinstance(value, list):
                    print(f"{key}: {value}")
                else:
                    print(f"{key}: {value}")
            print("================================")

def main():
    processor = AssemblyDataProcessor()
    processor.process_all_data(
        'collected_detailed_assembly_members.json',
        'processed_assembly_members.json'
    )

if __name__ == "__main__":
    main()
