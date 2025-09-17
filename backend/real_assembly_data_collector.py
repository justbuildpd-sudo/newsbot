#!/usr/bin/env python3
"""
22대 국회 실제 입법 데이터 수집 시스템
국회 API를 통해 실제 법안 데이터를 수집하고 정교하게 분석
"""

import sqlite3
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re
import time
import xml.etree.ElementTree as ET

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class RealAssemblyDataCollector:
    def __init__(self, db_path: str = "newsbot_stable.db"):
        self.db_path = db_path
        self.assembly_api_key = "57a5b206dc5341889b4ee3fbbb8757be"
        self.base_url = "https://open.assembly.go.kr/portal/openapi"
        self.init_database()
    
    def init_database(self):
        """실제 22대 국회 입법 데이터를 위한 데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 22대 국회 법안 테이블 (실제 데이터)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS real_assembly_bills_22nd (
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
                era_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 법안 세분화 분석 테이블 (실제 데이터 기반)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS real_bill_analysis_22nd (
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
                FOREIGN KEY (bill_id) REFERENCES real_assembly_bills_22nd (bill_id)
            )
        ''')
        
        # 의원별 입법성과 통계 테이블 (실제 데이터 기반)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS real_politician_legislative_stats_22nd (
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
        logger.info("실제 22대 국회 입법 데이터베이스 초기화 완료")
    
    def fetch_bills_from_assembly_api(self, page_size: int = 100) -> List[Dict]:
        """국회 API에서 22대 법안 데이터 수집 (XML 형식)"""
        bills = []
        
        try:
            # 22대 국회 법안 번호 범위 추정 (2200001부터 시작)
            start_bill_no = 2200001
            end_bill_no = 2299999
            
            logger.info(f"22대 법안 데이터 수집 중... (법안번호: {start_bill_no}~{end_bill_no})")
            
            # 법안 번호별로 순차적으로 조회
            for bill_no in range(start_bill_no, end_bill_no + 1):
                url = f"{self.base_url}/ALLBILL"
                params = {
                    'KEY': self.assembly_api_key,
                    'Type': 'xml',
                    'pIndex': 1,
                    'pSize': 1,
                    'BILL_NO': str(bill_no)
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
                
                try:
                    response = requests.get(url, params=params, headers=headers, timeout=10)
                    
                    if response.status_code != 200:
                        continue
                    
                    # XML 파싱
                    root = ET.fromstring(response.text)
                    
                    # 에러 메시지 확인
                    error_code = root.find('.//CODE')
                    if error_code is not None and error_code.text != 'INFO-000':
                        continue
                    
                    # 데이터가 없으면 다음 번호로
                    rows = root.findall('.//row')
                    if len(rows) == 0:
                        continue
                    
                    # 각 row 요소 파싱
                    for row in rows:
                        bill_data = {}
                        for child in row:
                            bill_data[child.tag] = child.text if child.text else ''
                        
                        # 22대 국회 데이터만 필터링
                        era_code = bill_data.get('ERACO', '')
                        if era_code == '제22대':
                            bills.append(bill_data)
                            logger.info(f"22대 법안 발견: {bill_data.get('BILL_NM', '')} (번호: {bill_data.get('BILL_NO', '')})")
                    
                except ET.ParseError:
                    continue
                except Exception as e:
                    logger.debug(f"법안번호 {bill_no} 조회 실패: {e}")
                    continue
                
                # API 호출 제한 고려
                time.sleep(0.1)
                
                # 진행 상황 출력
                if len(bills) % 10 == 0 and len(bills) > 0:
                    logger.info(f"현재까지 수집된 22대 법안: {len(bills)}개")
                
                # 최대 1000개로 제한
                if len(bills) >= 1000:
                    break
            
            logger.info(f"22대 법안 데이터 수집 완료: 총 {len(bills)}개")
            return bills
            
        except Exception as e:
            logger.error(f"국회 API 데이터 수집 실패: {e}")
            return []
    
    def analyze_bill_content_advanced(self, bill_name: str, bill_type: str = "", committee: str = "") -> Dict[str, any]:
        """법안 내용을 고도화된 기준으로 분석"""
        
        # 고급 키워드 분류 시스템
        policy_impact_keywords = {
            "국민안전": 25, "복지": 20, "환경": 20, "교육": 18, "의료": 18,
            "경제": 15, "고용": 15, "주거": 15, "디지털": 12, "혁신": 12,
            "보호": 10, "지원": 10, "육성": 10, "촉진": 8, "개선": 8
        }
        
        cleanup_keywords = {
            "일부개정": 15, "전부개정": 10, "폐지": 8, "정리": 5, "정비": 5,
            "시행령": 3, "시행규칙": 3, "위임": 2, "세부사항": 1
        }
        
        technical_keywords = {
            "기술적": 8, "문구": 3, "표현": 3, "용어": 2, "정의": 2,
            "절차": 5, "방법": 5, "시기": 3, "기한": 3, "조건": 3
        }
        
        substantial_keywords = {
            "신설": 20, "신규": 15, "추가": 10, "확대": 8, "강화": 8,
            "도입": 12, "시행": 10, "실시": 8, "처벌": 15, "과태료": 10
        }
        
        innovation_keywords = {
            "디지털": 15, "스마트": 12, "AI": 20, "빅데이터": 18, "블록체인": 15,
            "친환경": 10, "지속가능": 12, "4차산업": 15, "플랫폼": 10
        }
        
        urgency_keywords = {
            "긴급": 25, "시급": 20, "즉시": 15, "조속": 10, "신속": 8,
            "응급": 20, "비상": 15, "특별": 10, "임시": 5
        }
        
        combined_text = (bill_name + " " + bill_type + " " + committee).lower()
        
        # 정책 영향도 점수 계산
        policy_impact_score = 0
        for keyword, weight in policy_impact_keywords.items():
            if keyword in combined_text:
                policy_impact_score += weight
        
        # 카테고리 분류 (가중치 기반)
        cleanup_score = sum(weight for keyword, weight in cleanup_keywords.items() if keyword in combined_text)
        technical_score = sum(weight for keyword, weight in technical_keywords.items() if keyword in combined_text)
        substantial_score = sum(weight for keyword, weight in substantial_keywords.items() if keyword in combined_text)
        
        if cleanup_score > max(technical_score, substantial_score, 10):
            category = "의안정리"
        elif substantial_score > max(technical_score, 15):
            category = "실질입법"
        elif technical_score > 10:
            category = "기술수정"
        elif policy_impact_score > 20:
            category = "정책법안"
        else:
            category = "기타"
        
        # 세부 점수 계산
        legislative_quality_score = min(100, 40 + len(bill_name) * 0.8 + len(committee) * 2)
        public_interest_score = min(100, policy_impact_score * 0.8)
        innovation_score = min(100, sum(weight for keyword, weight in innovation_keywords.items() if keyword in combined_text))
        complexity_score = min(100, len(bill_name) * 1.5 + len(committee) * 3)
        urgency_score = min(100, sum(weight for keyword, weight in urgency_keywords.items() if keyword in combined_text))
        
        # 총 분석 점수 (가중평균)
        total_score = (
            policy_impact_score * 0.35 +
            legislative_quality_score * 0.25 +
            public_interest_score * 0.20 +
            innovation_score * 0.10 +
            complexity_score * 0.05 +
            urgency_score * 0.05
        )
        
        return {
            "category": category,
            "policy_impact_score": round(min(100, policy_impact_score), 2),
            "legislative_quality_score": round(legislative_quality_score, 2),
            "public_interest_score": round(public_interest_score, 2),
            "innovation_score": round(innovation_score, 2),
            "complexity_score": round(complexity_score, 2),
            "urgency_score": round(urgency_score, 2),
            "total_analysis_score": round(min(100, total_score), 2)
        }
    
    def process_and_store_real_bills(self, bills: List[Dict]):
        """실제 수집된 법안 데이터를 처리하고 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 데이터 삭제
        cursor.execute('DELETE FROM real_assembly_bills_22nd')
        cursor.execute('DELETE FROM real_bill_analysis_22nd')
        
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
                era_code = bill.get('ERACO', '')
                
                # 공동발의자 정보 (간단히 처리)
                co_proposers = ""
                
                cursor.execute('''
                    INSERT OR REPLACE INTO real_assembly_bills_22nd (
                        bill_id, bill_no, bill_name, bill_type, proposal_date,
                        proposer_name, proposer_type, committee_name, proposal_session,
                        co_proposers, bill_status, passage_date, promulgation_date, 
                        bill_content, era_code
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    bill_id, bill_no, bill_name, bill_type, proposal_date,
                    proposer_name, proposer_type, committee_name, proposal_session,
                    co_proposers, bill_status, passage_date, promulgation_date, 
                    bill_name, era_code
                ))
                
                # 고도화된 법안 분석 수행
                analysis = self.analyze_bill_content_advanced(bill_name, bill_type, committee_name)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO real_bill_analysis_22nd (
                        bill_id, bill_category, policy_impact_score, legislative_quality_score,
                        public_interest_score, innovation_score, complexity_score, urgency_score,
                        total_analysis_score, analysis_notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    bill_id, analysis["category"], analysis["policy_impact_score"],
                    analysis["legislative_quality_score"], analysis["public_interest_score"],
                    analysis["innovation_score"], analysis["complexity_score"],
                    analysis["urgency_score"], analysis["total_analysis_score"],
                    f"실제데이터분석: {analysis['category']} 카테고리, {bill_type} 유형"
                ))
                
                processed_count += 1
                
                if processed_count % 50 == 0:
                    logger.info(f"실제 데이터 처리 완료: {processed_count}개 법안")
                
            except Exception as e:
                logger.error(f"법안 처리 실패: {e}")
                continue
        
        conn.commit()
        conn.close()
        logger.info(f"실제 22대 법안 데이터 처리 완료: {processed_count}개")
    
    def calculate_real_politician_legislative_stats(self):
        """실제 의원별 입법성과 통계 계산"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 통계 삭제
        cursor.execute('DELETE FROM real_politician_legislative_stats_22nd')
        
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
            FROM real_assembly_bills_22nd b
            JOIN real_bill_analysis_22nd a ON b.bill_id = a.bill_id
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
                INSERT INTO real_politician_legislative_stats_22nd (
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
        logger.info(f"실제 의원별 입법성과 통계 계산 완료: {len(stats)}명")
    
    def run_real_analysis(self):
        """실제 22대 국회 입법 데이터 분석 실행"""
        logger.info("실제 22대 국회 입법 데이터 수집 및 분석 시작")
        
        # 1. 국회 API에서 실제 법안 데이터 수집
        bills = self.fetch_bills_from_assembly_api()
        
        if not bills:
            logger.error("실제 법안 데이터 수집 실패")
            return False
        
        # 2. 실제 법안 데이터 처리 및 저장
        self.process_and_store_real_bills(bills)
        
        # 3. 실제 의원별 입법성과 통계 계산
        self.calculate_real_politician_legislative_stats()
        
        logger.info("실제 22대 국회 입법 데이터 분석 완료")
        return True

if __name__ == "__main__":
    collector = RealAssemblyDataCollector()
    success = collector.run_real_analysis()
    
    if success:
        # 결과 요약 출력
        conn = sqlite3.connect(collector.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM real_assembly_bills_22nd')
        total_bills = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM real_politician_legislative_stats_22nd')
        total_politicians = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT politician_name, total_bills, total_performance_score, ranking
            FROM real_politician_legislative_stats_22nd
            ORDER BY total_performance_score DESC
            LIMIT 10
        ''')
        
        top_performers = cursor.fetchall()
        
        print(f"\n📊 실제 22대 국회 입법성과 분석 결과:")
        print(f"총 법안 수: {total_bills}개")
        print(f"분석 대상 의원: {total_politicians}명")
        print(f"\n🏆 입법성과 상위 10명:")
        
        for politician in top_performers:
            print(f"{politician[3]}. {politician[0]} - {politician[1]}개 법안, {politician[2]:.2f}점")
        
        conn.close()
    else:
        print("❌ 실제 데이터 수집 실패")
