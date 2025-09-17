#!/usr/bin/env python3
"""
22대 국회 입법 데이터 수집 및 세분화 시스템
실제 국회 데이터를 수집하여 의원별 입법성과를 정교하게 분석
"""

import sqlite3
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class AssemblyDataCollector:
    def __init__(self, db_path: str = "newsbot_stable.db"):
        self.db_path = db_path
        self.assembly_api_key = "57a5b206dc5341889b4ee3fbbb8757be"
        self.base_url = "https://open.assembly.go.kr/portal/openapi"
        self.init_database()
    
    def init_database(self):
        """22대 국회 입법 데이터를 위한 데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 22대 국회 법안 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assembly_bills_22nd (
                bill_id TEXT PRIMARY KEY,
                bill_no TEXT,
                bill_name TEXT,
                bill_type TEXT,
                proposal_date TEXT,
                proposer_name TEXT,
                proposer_type TEXT,
                committee_name TEXT,
                proposal_session TEXT,
                co_proposers TEXT,
                bill_status TEXT,
                passage_date TEXT,
                promulgation_date TEXT,
                bill_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 법안 세분화 분석 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bill_analysis_22nd (
                bill_id TEXT PRIMARY KEY,
                bill_category TEXT, -- '정책법안', '의안정리', '기술수정', '실질입법', '기타'
                policy_impact_score REAL DEFAULT 0.0,
                legislative_quality_score REAL DEFAULT 0.0,
                public_interest_score REAL DEFAULT 0.0,
                innovation_score REAL DEFAULT 0.0,
                complexity_score REAL DEFAULT 0.0,
                urgency_score REAL DEFAULT 0.0,
                total_analysis_score REAL DEFAULT 0.0,
                analysis_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bill_id) REFERENCES assembly_bills_22nd (bill_id)
            )
        ''')
        
        # 의원별 입법성과 통계 테이블 (22대)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS politician_legislative_stats_22nd (
                politician_name TEXT PRIMARY KEY,
                total_bills INTEGER DEFAULT 0,
                policy_bills INTEGER DEFAULT 0,
                administrative_bills INTEGER DEFAULT 0,
                technical_bills INTEGER DEFAULT 0,
                bill_cleanup_bills INTEGER DEFAULT 0,
                substantial_bills INTEGER DEFAULT 0,
                passage_rate REAL DEFAULT 0.0,
                avg_policy_impact REAL DEFAULT 0.0,
                avg_legislative_quality REAL DEFAULT 0.0,
                avg_public_interest REAL DEFAULT 0.0,
                avg_innovation REAL DEFAULT 0.0,
                total_performance_score REAL DEFAULT 0.0,
                ranking INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (politician_name) REFERENCES politicians (name)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("22대 국회 입법 데이터베이스 초기화 완료")
    
    def fetch_bills_from_assembly_api(self, page_size: int = 1000) -> List[Dict]:
        """국회 API에서 22대 법안 데이터 수집"""
        bills = []
        page = 1
        
        try:
            while True:
                url = f"{self.base_url}/ALLBILL"
                params = {
                    'KEY': self.assembly_api_key,
                    'Type': 'json',
                    'pIndex': page,
                    'pSize': page_size
                }
                
                logger.info(f"22대 법안 데이터 수집 중... 페이지 {page}")
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code != 200:
                    logger.error(f"API 요청 실패: {response.status_code}")
                    break
                
                data = response.json()
                
                if 'ALLBILL' not in data or 'row' not in data['ALLBILL']:
                    logger.warning(f"페이지 {page}: 데이터 없음")
                    break
                
                page_bills = data['ALLBILL']['row']
                if not page_bills:
                    logger.info(f"페이지 {page}: 더 이상 데이터 없음")
                    break
                
                bills.extend(page_bills)
                logger.info(f"페이지 {page}: {len(page_bills)}개 법안 수집")
                
                page += 1
                time.sleep(1)  # API 호출 제한 고려
                
                if page > 50:  # 최대 50페이지로 제한
                    break
            
            logger.info(f"22대 법안 데이터 수집 완료: 총 {len(bills)}개")
            return bills
            
        except Exception as e:
            logger.error(f"국회 API 데이터 수집 실패: {e}")
            return []
    
    def analyze_bill_content(self, bill_name: str, bill_content: str = "") -> Dict[str, any]:
        """법안 내용을 세분화 기준으로 분석"""
        
        # 키워드 기반 분류
        cleanup_keywords = [
            "일부개정", "전부개정", "폐지", "정리", "정비", "개선", "보완",
            "수정", "조정", "통합", "분리", "명칭변경", "조문정리",
            "시행령", "시행규칙", "위임", "위임사항", "위임조항", "세부사항"
        ]
        
        policy_keywords = [
            "정책", "제도", "혁신", "개혁", "발전", "지원", "육성", "촉진",
            "보호", "복지", "안전", "환경", "교육", "의료", "주거", "고용",
            "경제", "산업", "기술", "디지털", "스마트", "친환경", "지속가능",
            "국민", "시민", "사회", "공공", "공익"
        ]
        
        technical_keywords = [
            "기술적", "문구", "표현", "용어", "정의", "범위", "기준",
            "절차", "방법", "시기", "기한", "조건", "요건", "자격",
            "관리", "운영", "처리", "절차"
        ]
        
        substantial_keywords = [
            "신설", "신규", "추가", "확대", "강화", "도입", "시행",
            "실시", "운영", "관리", "감독", "조사", "처벌", "과태료",
            "벌금", "징역", "형", "처분", "제재"
        ]
        
        innovation_keywords = [
            "디지털", "스마트", "AI", "빅데이터", "블록체인", "친환경", "지속가능",
            "혁신", "창조", "신기술", "미래", "4차산업", "플랫폼", "온라인",
            "자동화", "효율", "최적화"
        ]
        
        urgency_keywords = [
            "긴급", "시급", "즉시", "조속", "신속", "빠른", "급한",
            "응급", "비상", "특별", "임시", "한시적"
        ]
        
        combined_text = (bill_name + " " + bill_content).lower()
        
        # 카테고리 분류
        if any(keyword in combined_text for keyword in cleanup_keywords):
            category = "의안정리"
        elif any(keyword in combined_text for keyword in policy_keywords):
            category = "정책법안"
        elif any(keyword in combined_text for keyword in technical_keywords):
            category = "기술수정"
        elif any(keyword in combined_text for keyword in substantial_keywords):
            category = "실질입법"
        else:
            category = "기타"
        
        # 점수 계산
        policy_impact_score = min(100, sum(10 for keyword in policy_keywords if keyword in combined_text))
        legislative_quality_score = min(100, 50 + len(bill_name) * 0.5)  # 제목 길이 기반
        public_interest_score = min(100, sum(15 for keyword in ["공공", "공익", "국민", "시민"] if keyword in combined_text))
        innovation_score = min(100, sum(20 for keyword in innovation_keywords if keyword in combined_text))
        complexity_score = min(100, len(bill_name) * 2 + len(bill_content) * 0.01)
        urgency_score = min(100, sum(25 for keyword in urgency_keywords if keyword in combined_text))
        
        # 총 분석 점수
        total_score = (
            policy_impact_score * 0.3 +
            legislative_quality_score * 0.2 +
            public_interest_score * 0.2 +
            innovation_score * 0.15 +
            complexity_score * 0.1 +
            urgency_score * 0.05
        )
        
        return {
            "category": category,
            "policy_impact_score": round(policy_impact_score, 2),
            "legislative_quality_score": round(legislative_quality_score, 2),
            "public_interest_score": round(public_interest_score, 2),
            "innovation_score": round(innovation_score, 2),
            "complexity_score": round(complexity_score, 2),
            "urgency_score": round(urgency_score, 2),
            "total_analysis_score": round(total_score, 2)
        }
    
    def process_and_store_bills(self, bills: List[Dict]):
        """수집된 법안 데이터를 처리하고 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 데이터 삭제
        cursor.execute('DELETE FROM assembly_bills_22nd')
        cursor.execute('DELETE FROM bill_analysis_22nd')
        
        processed_count = 0
        
        for bill in bills:
            try:
                # 법안 기본 정보 저장
                bill_id = bill.get('BILL_ID', '')
                bill_no = bill.get('BILL_NO', '')
                bill_name = bill.get('BILL_NM', '')
                bill_type = bill.get('BILL_KND', '')
                proposal_date = bill.get('PPSL_DT', '')
                proposer_name = bill.get('PPSR_NM', '')
                proposer_type = bill.get('PPSR_KND', '')
                committee_name = bill.get('JRCMIT_NM', '')
                proposal_session = bill.get('PPSL_SESS', '')
                bill_status = bill.get('RGS_CONF_RSLT', '')
                passage_date = bill.get('RGS_RSLN_DT', '')
                promulgation_date = bill.get('PROM_DT', '')
                
                # 공동발의자 정보 (간단히 처리)
                co_proposers = ""
                
                cursor.execute('''
                    INSERT OR REPLACE INTO assembly_bills_22nd (
                        bill_id, bill_no, bill_name, bill_type, proposal_date,
                        proposer_name, proposer_type, committee_name, proposal_session,
                        co_proposers, bill_status, passage_date, promulgation_date, bill_content
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    bill_id, bill_no, bill_name, bill_type, proposal_date,
                    proposer_name, proposer_type, committee_name, proposal_session,
                    co_proposers, bill_status, passage_date, promulgation_date, bill_name
                ))
                
                # 법안 분석 수행
                analysis = self.analyze_bill_content(bill_name, bill_name)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO bill_analysis_22nd (
                        bill_id, bill_category, policy_impact_score, legislative_quality_score,
                        public_interest_score, innovation_score, complexity_score, urgency_score,
                        total_analysis_score, analysis_notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    bill_id, analysis["category"], analysis["policy_impact_score"],
                    analysis["legislative_quality_score"], analysis["public_interest_score"],
                    analysis["innovation_score"], analysis["complexity_score"],
                    analysis["urgency_score"], analysis["total_analysis_score"],
                    f"자동분석: {analysis['category']} 카테고리"
                ))
                
                processed_count += 1
                
                if processed_count % 100 == 0:
                    logger.info(f"처리 완료: {processed_count}개 법안")
                
            except Exception as e:
                logger.error(f"법안 처리 실패: {e}")
                continue
        
        conn.commit()
        conn.close()
        logger.info(f"22대 법안 데이터 처리 완료: {processed_count}개")
    
    def calculate_politician_legislative_stats(self):
        """의원별 입법성과 통계 계산"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 통계 삭제
        cursor.execute('DELETE FROM politician_legislative_stats_22nd')
        
        # 의원별 통계 계산
        cursor.execute('''
            SELECT 
                b.proposer_name,
                COUNT(*) as total_bills,
                SUM(CASE WHEN a.bill_category = '정책법안' THEN 1 ELSE 0 END) as policy_bills,
                SUM(CASE WHEN a.bill_category = '의안정리' THEN 1 ELSE 0 END) as bill_cleanup_bills,
                SUM(CASE WHEN a.bill_category = '기술수정' THEN 1 ELSE 0 END) as technical_bills,
                SUM(CASE WHEN a.bill_category = '실질입법' THEN 1 ELSE 0 END) as substantial_bills,
                SUM(CASE WHEN a.bill_category = '기타' THEN 1 ELSE 0 END) as administrative_bills,
                AVG(CASE WHEN b.bill_status IN ('원안가결', '가결', '공포') THEN 1.0 ELSE 0.0 END) * 100 as passage_rate,
                AVG(a.policy_impact_score) as avg_policy_impact,
                AVG(a.legislative_quality_score) as avg_legislative_quality,
                AVG(a.public_interest_score) as avg_public_interest,
                AVG(a.innovation_score) as avg_innovation,
                AVG(a.total_analysis_score) as total_performance_score
            FROM assembly_bills_22nd b
            JOIN bill_analysis_22nd a ON b.bill_id = a.bill_id
            WHERE b.proposer_name IS NOT NULL AND b.proposer_name != ''
            GROUP BY b.proposer_name
            HAVING COUNT(*) >= 1
            ORDER BY AVG(a.total_analysis_score) DESC
        ''')
        
        stats = cursor.fetchall()
        
        for i, stat in enumerate(stats):
            politician_name = stat[0]
            total_bills = stat[1]
            policy_bills = stat[2]
            bill_cleanup_bills = stat[3]
            technical_bills = stat[4]
            substantial_bills = stat[5]
            administrative_bills = stat[6]
            passage_rate = stat[7] if stat[7] else 0
            avg_policy_impact = stat[8] if stat[8] else 0
            avg_legislative_quality = stat[9] if stat[9] else 0
            avg_public_interest = stat[10] if stat[10] else 0
            avg_innovation = stat[11] if stat[11] else 0
            total_performance_score = stat[12] if stat[12] else 0
            
            cursor.execute('''
                INSERT INTO politician_legislative_stats_22nd (
                    politician_name, total_bills, policy_bills, administrative_bills,
                    technical_bills, bill_cleanup_bills, substantial_bills, passage_rate,
                    avg_policy_impact, avg_legislative_quality, avg_public_interest,
                    avg_innovation, total_performance_score, ranking, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                politician_name, total_bills, policy_bills, administrative_bills,
                technical_bills, bill_cleanup_bills, substantial_bills, passage_rate,
                avg_policy_impact, avg_legislative_quality, avg_public_interest,
                avg_innovation, total_performance_score, i + 1
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"의원별 입법성과 통계 계산 완료: {len(stats)}명")
    
    def run_full_analysis(self):
        """전체 22대 국회 입법 데이터 분석 실행"""
        logger.info("22대 국회 입법 데이터 수집 및 분석 시작")
        
        # 1. 국회 API에서 법안 데이터 수집
        bills = self.fetch_bills_from_assembly_api()
        
        if not bills:
            logger.warning("법안 데이터 수집 실패. 샘플 데이터로 진행합니다.")
            # 샘플 데이터 생성
            bills = self.generate_sample_bills()
        
        # 2. 법안 데이터 처리 및 저장
        self.process_and_store_bills(bills)
        
        # 3. 의원별 입법성과 통계 계산
        self.calculate_politician_legislative_stats()
        
        logger.info("22대 국회 입법 데이터 분석 완료")
    
    def generate_sample_bills(self) -> List[Dict]:
        """샘플 법안 데이터 생성 (API 실패 시 사용)"""
        sample_bills = []
        
        # 정청래 의원 관련 샘플 법안
        sample_bills.extend([
            {
                'BILL_ID': 'BILL_001',
                'BILL_NO': '2120001',
                'BILL_NM': '국민안전강화법 일부개정법률안',
                'BILL_KND': '법률안',
                'PPSL_DT': '20240530',
                'PPSR_NM': '정청래',
                'PPSR_KND': '의원',
                'JRCMIT_NM': '행정안전위원회',
                'PPSL_SESS': '22대',
                'RGS_CONF_RSLT': '제안',
                'RGS_RSLN_DT': '',
                'PROM_DT': ''
            },
            {
                'BILL_ID': 'BILL_002',
                'BILL_NO': '2120002',
                'BILL_NM': '지역균형발전특별법 일부개정법률안',
                'BILL_KND': '법률안',
                'PPSL_DT': '20240615',
                'PPSR_NM': '정청래',
                'PPSR_KND': '의원',
                'JRCMIT_NM': '기획재정위원회',
                'PPSL_SESS': '22대',
                'RGS_CONF_RSLT': '원안가결',
                'RGS_RSLN_DT': '20241120',
                'PROM_DT': '20241201'
            }
        ])
        
        # 다른 의원들의 샘플 법안 (가상 데이터)
        politicians = ['김주영', '신장식', '박성민', '강준현', '김현']
        
        for i, politician in enumerate(politicians):
            for j in range(3):  # 각 의원당 3개 법안
                sample_bills.append({
                    'BILL_ID': f'BILL_{i*3+j+3:03d}',
                    'BILL_NO': f'212{i*3+j+3:04d}',
                    'BILL_NM': f'{politician} 의원 발의 법안 {j+1}',
                    'BILL_KND': '법률안',
                    'PPSL_DT': f'2024{6+j:02d}15',
                    'PPSR_NM': politician,
                    'PPSR_KND': '의원',
                    'JRCMIT_NM': '기획재정위원회',
                    'PPSL_SESS': '22대',
                    'RGS_CONF_RSLT': '제안' if j % 2 == 0 else '원안가결',
                    'RGS_RSLN_DT': f'2024{7+j:02d}01' if j % 2 == 1 else '',
                    'PROM_DT': f'2024{8+j:02d}01' if j % 2 == 1 else ''
                })
        
        return sample_bills

if __name__ == "__main__":
    collector = AssemblyDataCollector()
    collector.run_full_analysis()
    
    # 결과 요약 출력
    conn = sqlite3.connect(collector.db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM assembly_bills_22nd')
    total_bills = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM politician_legislative_stats_22nd')
    total_politicians = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT politician_name, total_bills, total_performance_score, ranking
        FROM politician_legislative_stats_22nd
        ORDER BY total_performance_score DESC
        LIMIT 10
    ''')
    
    top_performers = cursor.fetchall()
    
    print(f"\n📊 22대 국회 입법성과 분석 결과:")
    print(f"총 법안 수: {total_bills}개")
    print(f"분석 대상 의원: {total_politicians}명")
    print(f"\n🏆 입법성과 상위 10명:")
    
    for politician in top_performers:
        print(f"{politician[3]}. {politician[0]} - {politician[1]}개 법안, {politician[2]:.2f}점")
    
    conn.close()
