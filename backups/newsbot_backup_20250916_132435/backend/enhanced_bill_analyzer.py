#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
강화된 의안 분석 시스템
실제 의안정보 API를 활용한 정확한 의안 결과 분석
"""

import requests
import json
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import re

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedBillAnalyzer:
    def __init__(self, api_key: str = "57a5b206dc5341889b4ee3fbbb8757be"):
        self.api_key = api_key
        self.base_url = "https://open.assembly.go.kr/portal/openapi/ALLBILL"
        self.db_path = "enhanced_bills_analysis.db"
        self.politicians_db = "data/politicians.json"
        self.init_database()
        
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 의안 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id TEXT UNIQUE,
                bill_no TEXT,
                bill_knd TEXT,
                bill_nm TEXT,
                ppsr_knd TEXT,
                ppsr_nm TEXT,
                ppsl_sess TEXT,
                ppsl_dt TEXT,
                jrcmit_nm TEXT,
                jrcmit_cmmt_dt TEXT,
                jrcmit_prsnt_dt TEXT,
                jrcmit_proc_dt TEXT,
                jrcmit_proc_rslt TEXT,
                law_cmmt_dt TEXT,
                law_prsnt_dt TEXT,
                law_proc_dt TEXT,
                law_proc_rslt TEXT,
                rgs_prsnt_dt TEXT,
                rgs_rsln_dt TEXT,
                rgs_conf_nm TEXT,
                rgs_conf_rslt TEXT,
                gvrn_trsf_dt TEXT,
                prom_law_nm TEXT,
                prom_dt TEXT,
                prom_no TEXT,
                link_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 발의자 관계 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bill_sponsors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id TEXT,
                sponsor_name TEXT,
                sponsor_type TEXT,
                sponsor_order INTEGER,
                FOREIGN KEY (bill_id) REFERENCES bills (bill_id)
            )
        ''')
        
        # 의안 결과 분석 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bill_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                politician_name TEXT,
                total_bills INTEGER DEFAULT 0,
                main_sponsor_bills INTEGER DEFAULT 0,
                co_sponsor_bills INTEGER DEFAULT 0,
                passed_bills INTEGER DEFAULT 0,
                enacted_bills INTEGER DEFAULT 0,
                important_bills INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                enactment_rate REAL DEFAULT 0.0,
                impact_score REAL DEFAULT 0.0,
                committee_diversity INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("강화된 의안 분석 데이터베이스 초기화 완료")
    
    def fetch_bills_from_api(self, max_pages: int = 50) -> List[Dict]:
        """API에서 의안 데이터 수집"""
        all_bills = []
        
        for page in range(1, max_pages + 1):
            try:
                params = {
                    'KEY': self.api_key,
                    'Type': 'json',
                    'pIndex': page,
                    'pSize': 100
                }
                
                response = requests.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                if 'ALLBILL' not in data or 'row' not in data['ALLBILL']:
                    logger.warning(f"페이지 {page}: 데이터 없음")
                    break
                
                bills = data['ALLBILL']['row']
                if not bills:
                    logger.info(f"페이지 {page}: 더 이상 데이터 없음")
                    break
                
                all_bills.extend(bills)
                logger.info(f"페이지 {page}: {len(bills)}개 의안 수집")
                
                # API 제한 고려
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"페이지 {page} 수집 실패: {e}")
                break
        
        logger.info(f"총 {len(all_bills)}개 의안 수집 완료")
        return all_bills
    
    def save_bills_to_db(self, bills: List[Dict]):
        """의안 데이터를 데이터베이스에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        for bill in bills:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO bills (
                        bill_id, bill_no, bill_knd, bill_nm, ppsr_knd, ppsr_nm,
                        ppsl_sess, ppsl_dt, jrcmit_nm, jrcmit_cmmt_dt, jrcmit_prsnt_dt,
                        jrcmit_proc_dt, jrcmit_proc_rslt, law_cmmt_dt, law_prsnt_dt,
                        law_proc_dt, law_proc_rslt, rgs_prsnt_dt, rgs_rsln_dt,
                        rgs_conf_nm, rgs_conf_rslt, gvrn_trsf_dt, prom_law_nm,
                        prom_dt, prom_no, link_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    bill.get('BILL_ID', ''),
                    bill.get('BILL_NO', ''),
                    bill.get('BILL_KND', ''),
                    bill.get('BILL_NM', ''),
                    bill.get('PPSR_KND', ''),
                    bill.get('PPSR_NM', ''),
                    bill.get('PPSL_SESS', ''),
                    bill.get('PPSL_DT', ''),
                    bill.get('JRCMIT_NM', ''),
                    bill.get('JRCMIT_CMMT_DT', ''),
                    bill.get('JRCMIT_PRSNT_DT', ''),
                    bill.get('JRCMIT_PROC_DT', ''),
                    bill.get('JRCMIT_PROC_RSLT', ''),
                    bill.get('LAW_CMMT_DT', ''),
                    bill.get('LAW_PRSNT_DT', ''),
                    bill.get('LAW_PROC_DT', ''),
                    bill.get('LAW_PROC_RSLT', ''),
                    bill.get('RGS_PRSNT_DT', ''),
                    bill.get('RGS_RSLN_DT', ''),
                    bill.get('RGS_CONF_NM', ''),
                    bill.get('RGS_CONF_RSLT', ''),
                    bill.get('GVRN_TRSF_DT', ''),
                    bill.get('PROM_LAW_NM', ''),
                    bill.get('PROM_DT', ''),
                    bill.get('PROM_NO', ''),
                    bill.get('LINK_URL', '')
                ))
                
                # 발의자 정보 파싱 및 저장
                self._parse_and_save_sponsors(cursor, bill.get('BILL_ID', ''), bill.get('PPSR_NM', ''))
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"의안 저장 실패: {e}")
                continue
        
        conn.commit()
        conn.close()
        logger.info(f"{saved_count}개 의안 저장 완료")
    
    def _parse_and_save_sponsors(self, cursor, bill_id: str, ppsr_nm: str):
        """발의자 정보 파싱 및 저장"""
        if not ppsr_nm or not bill_id:
            return
        
        # 발의자 이름 파싱
        sponsors = self._parse_sponsor_names(ppsr_nm)
        
        for i, sponsor in enumerate(sponsors):
            sponsor_type = '대표발의' if i == 0 else '공동발의'
            cursor.execute('''
                INSERT OR REPLACE INTO bill_sponsors 
                (bill_id, sponsor_name, sponsor_type, sponsor_order)
                VALUES (?, ?, ?, ?)
            ''', (bill_id, sponsor, sponsor_type, i + 1))
    
    def _parse_sponsor_names(self, ppsr_nm: str) -> List[str]:
        """발의자 이름 파싱"""
        if not ppsr_nm:
            return []
        
        # 쉼표, 세미콜론, 공백으로 구분
        sponsors = []
        for delimiter in [',', ';', ' ']:
            if delimiter in ppsr_nm:
                sponsors = [s.strip() for s in ppsr_nm.split(delimiter) if s.strip()]
                break
        
        if not sponsors:
            sponsors = [ppsr_nm.strip()]
        
        return sponsors
    
    def analyze_politician_bill_performance(self, politician_name: str) -> Dict:
        """정치인별 의안 성과 분석"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기본 통계
        cursor.execute('''
            SELECT COUNT(*) FROM bill_sponsors 
            WHERE sponsor_name = ?
        ''', (politician_name,))
        total_bills = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM bill_sponsors 
            WHERE sponsor_name = ? AND sponsor_type = '대표발의'
        ''', (politician_name,))
        main_sponsor_bills = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM bill_sponsors 
            WHERE sponsor_name = ? AND sponsor_type = '공동발의'
        ''', (politician_name,))
        co_sponsor_bills = cursor.fetchone()[0]
        
        # 의안 결과 분석
        cursor.execute('''
            SELECT COUNT(*) FROM bill_sponsors bs
            JOIN bills b ON bs.bill_id = b.bill_id
            WHERE bs.sponsor_name = ? 
            AND (b.rgs_conf_rslt LIKE '%가결%' OR b.rgs_conf_rslt LIKE '%통과%')
        ''', (politician_name,))
        passed_bills = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM bill_sponsors bs
            JOIN bills b ON bs.bill_id = b.bill_id
            WHERE bs.sponsor_name = ? 
            AND b.prom_dt IS NOT NULL AND b.prom_dt != ''
        ''', (politician_name,))
        enacted_bills = cursor.fetchone()[0]
        
        # 중요 의안 분석
        cursor.execute('''
            SELECT COUNT(*) FROM bill_sponsors bs
            JOIN bills b ON bs.bill_id = b.bill_id
            WHERE bs.sponsor_name = ? 
            AND b.bill_knd IN ('법률안', '예산안', '결산안', '조약안')
        ''', (politician_name,))
        important_bills = cursor.fetchone()[0]
        
        # 위원회 다양성
        cursor.execute('''
            SELECT COUNT(DISTINCT b.jrcmit_nm) FROM bill_sponsors bs
            JOIN bills b ON bs.bill_id = b.bill_id
            WHERE bs.sponsor_name = ? AND b.jrcmit_nm IS NOT NULL
        ''', (politician_name,))
        committee_diversity = cursor.fetchone()[0]
        
        # 성공률 계산
        success_rate = passed_bills / max(total_bills, 1)
        enactment_rate = enacted_bills / max(total_bills, 1)
        
        # 영향력 점수 계산
        impact_score = (
            important_bills * 3 +  # 중요 의안 가중치
            enacted_bills * 2 +   # 공포 의안 가중치
            committee_diversity * 1  # 위원회 다양성 가중치
        ) / 10
        
        conn.close()
        
        return {
            "politician_name": politician_name,
            "total_bills": total_bills,
            "main_sponsor_bills": main_sponsor_bills,
            "co_sponsor_bills": co_sponsor_bills,
            "passed_bills": passed_bills,
            "enacted_bills": enacted_bills,
            "important_bills": important_bills,
            "success_rate": success_rate,
            "enactment_rate": enactment_rate,
            "impact_score": impact_score,
            "committee_diversity": committee_diversity
        }
    
    def run_comprehensive_bill_analysis(self):
        """종합 의안 분석 실행"""
        logger.info("의안 데이터 수집 시작...")
        
        # API에서 의안 데이터 수집 (테스트용으로 10페이지만)
        bills = self.fetch_bills_from_api(max_pages=10)
        
        if bills:
            logger.info("의안 데이터 저장 중...")
            self.save_bills_to_db(bills)
        
        # 정치인별 의안 성과 분석
        logger.info("정치인별 의안 성과 분석 시작...")
        
        with open(self.politicians_db, 'r', encoding='utf-8') as f:
            politicians_data = json.load(f)
        
        analysis_results = []
        for politician in politicians_data:
            name = politician.get('name', '')
            if name:
                result = self.analyze_politician_bill_performance(name)
                analysis_results.append(result)
        
        # 결과를 데이터베이스에 저장
        self.save_analysis_results(analysis_results)
        
        # 상위 성과자 출력
        sorted_results = sorted(analysis_results, key=lambda x: x['impact_score'], reverse=True)
        
        print("\n=== 의안 성과 상위 10명 ===")
        for i, result in enumerate(sorted_results[:10]):
            print(f"{i+1:2d}. {result['politician_name']:10s} - "
                  f"총의안:{result['total_bills']:3d} "
                  f"가결:{result['passed_bills']:3d} "
                  f"공포:{result['enacted_bills']:3d} "
                  f"영향력:{result['impact_score']:.2f}")
        
        return analysis_results
    
    def save_analysis_results(self, results: List[Dict]):
        """분석 결과를 데이터베이스에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 데이터 삭제
        cursor.execute('DELETE FROM bill_analysis')
        
        for result in results:
            cursor.execute('''
                INSERT INTO bill_analysis (
                    politician_name, total_bills, main_sponsor_bills, co_sponsor_bills,
                    passed_bills, enacted_bills, important_bills, success_rate,
                    enactment_rate, impact_score, committee_diversity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result['politician_name'], result['total_bills'], result['main_sponsor_bills'],
                result['co_sponsor_bills'], result['passed_bills'], result['enacted_bills'],
                result['important_bills'], result['success_rate'], result['enactment_rate'],
                result['impact_score'], result['committee_diversity']
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"{len(results)}명의 의안 성과 분석 결과 저장 완료")
    
    def get_bill_statistics(self) -> Dict:
        """의안 통계 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 전체 의안 수
        cursor.execute('SELECT COUNT(*) FROM bills')
        total_bills = cursor.fetchone()[0]
        
        # 의안 종류별 통계
        cursor.execute('''
            SELECT bill_knd, COUNT(*) as count
            FROM bills
            GROUP BY bill_knd
            ORDER BY count DESC
        ''')
        bill_types = cursor.fetchall()
        
        # 처리 결과별 통계
        cursor.execute('''
            SELECT rgs_conf_rslt, COUNT(*) as count
            FROM bills
            WHERE rgs_conf_rslt IS NOT NULL AND rgs_conf_rslt != ''
            GROUP BY rgs_conf_rslt
            ORDER BY count DESC
        ''')
        bill_results = cursor.fetchall()
        
        # 공포된 의안 수
        cursor.execute('''
            SELECT COUNT(*) FROM bills
            WHERE prom_dt IS NOT NULL AND prom_dt != ''
        ''')
        enacted_bills = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_bills": total_bills,
            "enacted_bills": enacted_bills,
            "enactment_rate": enacted_bills / max(total_bills, 1),
            "bill_types": [{"type": t[0], "count": t[1]} for t in bill_types],
            "bill_results": [{"result": r[0], "count": r[1]} for r in bill_results]
        }

if __name__ == "__main__":
    analyzer = EnhancedBillAnalyzer()
    results = analyzer.run_comprehensive_bill_analysis()
    
    # 통계 출력
    stats = analyzer.get_bill_statistics()
    print(f"\n=== 의안 통계 ===")
    print(f"총 의안 수: {stats['total_bills']}")
    print(f"공포된 의안: {stats['enacted_bills']}")
    print(f"공포율: {stats['enactment_rate']:.2%}")
