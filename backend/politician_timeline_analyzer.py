"""
시간축 기반 정치인 분석 시스템
- 뉴스: 현재 시점의 새로운 사건
- 발화록: 과거의 행보 기록
- 의원: 현재 상태
"""
import pandas as pd
import os
import json
import re
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
from collections import defaultdict

class PoliticianTimelineAnalyzer:
    def __init__(self, meeting_data_path: str, batch_size: int = 20):
        self.meeting_data_path = meeting_data_path
        self.batch_size = batch_size
        
        # 시간축별 데이터 저장
        self.current_news = {}  # 현재 뉴스 (실시간)
        self.historical_speeches = {}  # 과거 발화록
        self.current_politicians = {}  # 현재 의원 정보
        self.timeline_data = {}  # 통합 타임라인 데이터
        
        # 분석 결과
        self.politician_profiles = {}
        self.trend_analysis = {}
        self.prediction_indicators = {}
        
    def load_historical_speeches_batch(self, start_index: int = 0) -> Dict:
        """과거 발화록 배치 로드 (과거 행보 분석용)"""
        print(f"📚 과거 발화록 배치 로드 중... (시작: {start_index})")
        
        # 발언자 파일 찾기
        speaker_files = [f for f in os.listdir(self.meeting_data_path) 
                        if '발언자목록' in f and f.endswith('.xlsx')]
        
        end_index = min(start_index + self.batch_size, len(speaker_files))
        batch_files = speaker_files[start_index:end_index]
        
        processed_count = 0
        for file in batch_files:
            try:
                file_path = os.path.join(self.meeting_data_path, file)
                df = pd.read_excel(file_path)
                
                if len(df) >= 2 and df.iloc[1, 0] == '순번':
                    df = df.iloc[1:].reset_index(drop=True)
                    df.columns = ['순번', '발언자명', '대수', '발언자구분', '의원ID', '소속정당', '지역']
                    df = df.dropna(subset=['발언자명'])
                    
                    if not df.empty:
                        member_name = self._extract_member_name_from_filename(file)
                        
                        # 발화록 데이터를 시간순으로 정렬
                        speeches = df.to_dict('records')
                        speeches.sort(key=lambda x: x.get('순번', 0))
                        
                        self.historical_speeches[member_name] = {
                            'file_name': file,
                            'speeches': speeches,
                            'total_speeches': len(speeches),
                            'date_range': self._extract_date_range(speeches),
                            'last_updated': datetime.now().isoformat()
                        }
                        
                        print(f"✅ {member_name}: {len(speeches)}개 과거 발언 기록")
                        processed_count += 1
                        
            except Exception as e:
                print(f"❌ {file} 처리 오류: {e}")
            
            time.sleep(0.05)  # CPU 부하 방지
        
        print(f"📊 과거 발화록 배치 처리 완료: {processed_count}개 파일")
        return {
            'processed_count': processed_count,
            'total_speeches': len(self.historical_speeches),
            'has_more': end_index < len(speaker_files),
            'next_start': end_index
        }
    
    def load_current_politicians(self, politician_list: List[Dict]) -> Dict:
        """현재 의원 정보 로드 (현재 상태)"""
        print("👥 현재 의원 정보 로드 중...")
        
        for politician in politician_list:
            name = politician.get('name', '')
            if name:
                self.current_politicians[name] = {
                    'id': politician.get('id', ''),
                    'name': name,
                    'party': politician.get('party', ''),
                    'district': politician.get('district', ''),
                    'committee': politician.get('committee', ''),
                    'political_orientation': politician.get('political_orientation', ''),
                    'key_issues': politician.get('key_issues', []),
                    'current_status': 'active',
                    'last_updated': datetime.now().isoformat()
                }
        
        print(f"📊 현재 의원 정보 로드 완료: {len(self.current_politicians)}명")
        return {'total_politicians': len(self.current_politicians)}
    
    def update_current_news(self, news_data: List[Dict]) -> Dict:
        """현재 뉴스 업데이트 (실시간 사건)"""
        print("📰 현재 뉴스 업데이트 중...")
        
        current_time = datetime.now()
        for news in news_data:
            news_id = news.get('id', hashlib.md5(news.get('title', '').encode()).hexdigest())
            
            self.current_news[news_id] = {
                'id': news_id,
                'title': news.get('title', ''),
                'description': news.get('description', ''),
                'content': news.get('content', ''),
                'published_at': news.get('published_at', current_time.isoformat()),
                'source': news.get('source', ''),
                'mentioned_politicians': news.get('mentioned_politicians', []),
                'politician_count': news.get('politician_count', 0),
                'news_type': 'current_event',
                'last_updated': current_time.isoformat()
            }
        
        print(f"📊 현재 뉴스 업데이트 완료: {len(self.current_news)}개")
        return {'total_news': len(self.current_news)}
    
    def create_politician_timeline(self, politician_name: str) -> Dict:
        """개별 정치인 타임라인 생성"""
        timeline = {
            'politician_name': politician_name,
            'current_info': self.current_politicians.get(politician_name, {}),
            'historical_speeches': self.historical_speeches.get(politician_name, {}),
            'recent_news_mentions': [],
            'timeline_analysis': {},
            'created_at': datetime.now().isoformat()
        }
        
        # 최근 뉴스에서 언급된 내용 찾기
        for news_id, news in self.current_news.items():
            for mentioned in news.get('mentioned_politicians', []):
                if mentioned.get('name') == politician_name:
                    timeline['recent_news_mentions'].append({
                        'news_id': news_id,
                        'title': news.get('title', ''),
                        'published_at': news.get('published_at', ''),
                        'mention_type': mentioned.get('mention_type', ''),
                        'context': mentioned.get('context', '')
                    })
        
        # 타임라인 분석
        timeline['timeline_analysis'] = self._analyze_politician_timeline(timeline)
        
        return timeline
    
    def _analyze_politician_timeline(self, timeline: Dict) -> Dict:
        """정치인 타임라인 분석"""
        analysis = {
            'activity_level': 'low',
            'issue_focus': [],
            'trend_direction': 'stable',
            'prediction_indicators': [],
            'key_insights': []
        }
        
        # 활동 수준 분석
        speech_count = timeline.get('historical_speeches', {}).get('total_speeches', 0)
        news_mentions = len(timeline.get('recent_news_mentions', []))
        
        if speech_count > 50 and news_mentions > 5:
            analysis['activity_level'] = 'high'
        elif speech_count > 20 or news_mentions > 2:
            analysis['activity_level'] = 'medium'
        
        # 이슈 포커스 분석
        current_info = timeline.get('current_info', {})
        analysis['issue_focus'] = current_info.get('key_issues', [])
        
        # 트렌드 방향 분석
        if news_mentions > speech_count / 10:
            analysis['trend_direction'] = 'rising'
        elif news_mentions < speech_count / 20:
            analysis['trend_direction'] = 'declining'
        
        # 예측 지표
        if analysis['activity_level'] == 'high' and analysis['trend_direction'] == 'rising':
            analysis['prediction_indicators'].append('활발한 활동과 상승 트렌드')
        
        if len(timeline.get('recent_news_mentions', [])) > 0:
            analysis['prediction_indicators'].append('최근 언론 주목도 증가')
        
        # 핵심 인사이트
        if speech_count > 0:
            analysis['key_insights'].append(f"과거 {speech_count}회 발언 기록 보유")
        
        if news_mentions > 0:
            analysis['key_insights'].append(f"최근 {news_mentions}건 뉴스 언급")
        
        return analysis
    
    def _extract_member_name_from_filename(self, filename: str) -> str:
        """파일명에서 의원명 추출"""
        pattern = r'통합검색_국회회의록_발언자목록_(.+?)\+\(.+?\)_\d{4}-\d{2}-\d{2}\.xlsx'
        match = re.search(pattern, filename)
        if match:
            return match.group(1)
        return filename
    
    def _extract_date_range(self, speeches: List[Dict]) -> Dict:
        """발언 날짜 범위 추출"""
        if not speeches:
            return {'start': None, 'end': None}
        
        first_speech = speeches[0]
        last_speech = speeches[-1]
        
        return {
            'start': first_speech.get('순번', ''),
            'end': last_speech.get('순번', ''),
            'total_speeches': len(speeches)
        }
    
    def get_analysis_summary(self) -> Dict:
        """분석 요약 생성"""
        return {
            'total_politicians': len(self.current_politicians),
            'total_historical_speeches': len(self.historical_speeches),
            'total_current_news': len(self.current_news),
            'last_updated': datetime.now().isoformat()
        }

def main():
    """메인 실행 함수"""
    meeting_data_path = "/Users/hopidaay/InsightForge/qa_service/data/processed_meetings"
    
    analyzer = PoliticianTimelineAnalyzer(meeting_data_path, batch_size=10)
    
    print("🚀 시간축 기반 정치인 분석 시스템 시작")
    print("=" * 60)
    
    # 1단계: 현재 의원 정보 로드
    print("\n�� 1단계: 현재 의원 정보 로드")
    from assembly_api_service import AssemblyAPIService
    assembly_api = AssemblyAPIService()
    politician_list = assembly_api.get_member_list()
    current_result = analyzer.load_current_politicians(politician_list)
    print(f"처리 결과: {current_result}")
    
    # 2단계: 과거 발화록 배치 로드
    print("\n📚 2단계: 과거 발화록 배치 로드")
    speech_result = analyzer.load_historical_speeches_batch(0)
    print(f"처리 결과: {speech_result}")
    
    # 최종 요약
    summary = analyzer.get_analysis_summary()
    print(f"\n🎉 시간축 기반 정치인 분석 완료!")
    print(f"📊 최종 요약:")
    print(f"   - 현재 의원: {summary['total_politicians']}명")
    print(f"   - 과거 발화록: {summary['total_historical_speeches']}명")
    print(f"   - 현재 뉴스: {summary['total_current_news']}건")

if __name__ == "__main__":
    main()
