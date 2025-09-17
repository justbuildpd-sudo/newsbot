#!/usr/bin/env python3
"""
2. 국회의안정보API - 의안 정보 전용 서비스 (4개 서비스)
- 의안 정보
- 의안 검증  
- 발의안 데이터
- 입법 활동 분석
"""
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BillsInfoAPI:
    """국회의안정보API 클래스"""
    
    def __init__(self):
        self.bills_data = {}
        self.load_bills_data()
    
    def load_bills_data(self):
        """발의안 데이터 로드"""
        # 발의안 데이터 파일들 우선순위
        data_files = [
            'enhanced_bills_data_22nd.json',  # 가장 완전한 발의안 데이터
            'bills_data_22nd.json',
            'member_bill_matches_22nd_300.json'
        ]
        
        for filename in data_files:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.bills_data = json.load(f)
                logger.info(f"발의안 데이터 로드 성공: {filename} ({len(self.bills_data)}명)")
                break
            except FileNotFoundError:
                continue
        
        if not self.bills_data:
            logger.error("발의안 데이터 파일을 찾을 수 없음")
    
    def get_politician_bills(self, politician_name: str) -> Dict:
        """정치인별 발의안 조회"""
        bills = self.bills_data.get(politician_name, [])
        
        if not bills:
            return {
                'success': False,
                'error': f'{politician_name} 의원의 발의안을 찾을 수 없습니다'
            }
        
        # 최신순 정렬
        sorted_bills = sorted(bills, 
                            key=lambda x: x.get('propose_date', ''), 
                            reverse=True)
        
        return {
            'success': True,
            'politician': politician_name,
            'bills': sorted_bills,
            'total_count': len(bills),
            'source': '국회의안정보API'
        }
    
    def get_bill_scores(self, politician_name: str) -> Dict:
        """발의안 점수 계산"""
        bills = self.bills_data.get(politician_name, [])
        
        if not bills:
            return {
                'main_proposals': 0,
                'co_proposals': 0,
                'total_bills': 0,
                'success_rate': 0,
                'recent_activity': 0
            }
        
        # 통계 계산
        main_proposals = sum(1 for bill in bills if bill.get('role') == 'main_proposer')
        co_proposals = sum(1 for bill in bills if bill.get('role') == 'co_proposer')
        total_bills = len(bills)
        
        # 성공률 계산 (본회의 통과 기준)
        passed_bills = sum(1 for bill in bills if '통과' in bill.get('status', ''))
        success_rate = (passed_bills / total_bills * 100) if total_bills > 0 else 0
        
        # 최근 활동 (30일 내)
        recent_activity = sum(1 for bill in bills if self.is_recent_bill(bill))
        
        return {
            'main_proposals': main_proposals,
            'co_proposals': co_proposals,
            'total_bills': total_bills,
            'success_rate': round(success_rate, 1),
            'recent_activity': recent_activity
        }
    
    def get_recent_bills(self, limit: int = 20) -> List[Dict]:
        """최근 발의안 목록"""
        all_bills = []
        
        for politician_name, bills in self.bills_data.items():
            for bill in bills:
                bill_copy = bill.copy()
                bill_copy['politician'] = politician_name
                all_bills.append(bill_copy)
        
        # 최신순 정렬
        sorted_bills = sorted(all_bills, 
                            key=lambda x: x.get('propose_date', ''), 
                            reverse=True)
        
        return sorted_bills[:limit]
    
    def verify_bill_info(self, bill_id: str) -> Dict:
        """의안 정보 검증"""
        # 모든 발의안에서 해당 ID 검색
        for politician_name, bills in self.bills_data.items():
            for bill in bills:
                if bill.get('bill_id') == bill_id:
                    return {
                        'verified': True,
                        'bill': bill,
                        'politician': politician_name,
                        'verification_date': datetime.now().isoformat()
                    }
        
        return {
            'verified': False,
            'error': f'의안 ID {bill_id}를 찾을 수 없습니다'
        }
    
    def is_recent_bill(self, bill: Dict) -> bool:
        """최근 발의안 여부 확인 (30일 기준)"""
        try:
            propose_date = bill.get('propose_date', '')
            if not propose_date:
                return False
            
            # 날짜 파싱 (YYYY-MM-DD 형식 가정)
            bill_date = datetime.strptime(propose_date, '%Y-%m-%d')
            cutoff_date = datetime.now() - timedelta(days=30)
            
            return bill_date >= cutoff_date
        except:
            return False
    
    def get_statistics(self) -> Dict:
        """발의안 통계 정보"""
        total_bills = 0
        total_politicians = len(self.bills_data)
        
        status_stats = {}
        committee_stats = {}
        
        for politician_name, bills in self.bills_data.items():
            total_bills += len(bills)
            
            for bill in bills:
                status = bill.get('status', '알 수 없음')
                status_stats[status] = status_stats.get(status, 0) + 1
                
                committee = bill.get('committee', '')
                if committee:
                    committee_stats[committee] = committee_stats.get(committee, 0) + 1
        
        return {
            'total_politicians': total_politicians,
            'total_bills': total_bills,
            'average_bills_per_politician': round(total_bills / total_politicians, 1) if total_politicians > 0 else 0,
            'status_distribution': status_stats,
            'committee_distribution': committee_stats
        }

# 전역 인스턴스
bills_api = BillsInfoAPI()

if __name__ == "__main__":
    # 테스트
    stats = bills_api.get_statistics()
    print("국회의안정보API 통계:")
    print(f"총 정치인: {stats['total_politicians']}명")
    print(f"총 발의안: {stats['total_bills']}건")
    print(f"평균 발의안: {stats['average_bills_per_politician']}건/인")
    
    # 샘플 의원 발의안 확인
    sample_politician = list(bills_api.bills_data.keys())[0] if bills_api.bills_data else None
    if sample_politician:
        scores = bills_api.get_bill_scores(sample_politician)
        print(f"\\n샘플 ({sample_politician}):")
        print(f"  대표발의: {scores['main_proposals']}건")
        print(f"  공동발의: {scores['co_proposals']}건")
        print(f"  성공률: {scores['success_rate']}%")
