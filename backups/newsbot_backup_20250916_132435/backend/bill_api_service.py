#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
의안정보 통합 API 서비스
국회의원들의 발의 활동을 분석하여 연결성 네트워크 구축
"""

import requests
import json
import time
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BillAPIService:
    def __init__(self, api_key: str = "57a5b206dc5341889b4ee3fbbb8757be"):
        self.api_key = api_key
        self.base_url = "https://open.assembly.go.kr/portal/openapi/ALLBILL"
        self.db_path = "bills_connectivity.db"
        self.init_database()
        
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 정치인 테이블 (기존 데이터 연동)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS politicians (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                party_name TEXT,
                district TEXT,
                committee TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
                sponsor_type TEXT,  -- '대표발의' 또는 '공동발의'
                sponsor_order INTEGER,  -- 발의 순서
                FOREIGN KEY (bill_id) REFERENCES bills (bill_id)
            )
        ''')
        
        # 연결성 네트워크 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS connectivity_network (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                politician_a TEXT,
                politician_b TEXT,
                connection_strength INTEGER DEFAULT 1,
                connection_type TEXT,  -- 'co_sponsor', 'committee', 'party', 'meeting'
                bill_count INTEGER DEFAULT 0,
                meeting_count INTEGER DEFAULT 0,
                last_collaboration TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("데이터베이스 초기화 완료")
    
    def fetch_bills(self, page_size: int = 100, max_pages: int = 50) -> List[Dict]:
        """의안 데이터 수집"""
        all_bills = []
        
        for page in range(1, max_pages + 1):
            try:
                params = {
                    'KEY': self.api_key,
                    'Type': 'json',
                    'pIndex': page,
                    'pSize': page_size
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
                
                # API 제한 고려하여 잠시 대기
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
                saved_count += 1
                
            except Exception as e:
                logger.error(f"의안 저장 실패: {e}")
                continue
        
        conn.commit()
        conn.close()
        logger.info(f"{saved_count}개 의안 저장 완료")
    
    def analyze_sponsorship_relationships(self):
        """발의자 관계 분석"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 의안별 발의자 정보 추출
        cursor.execute('''
            SELECT bill_id, ppsr_nm, ppsr_knd, ppsl_dt
            FROM bills 
            WHERE ppsr_nm IS NOT NULL AND ppsr_nm != ''
            ORDER BY ppsl_dt DESC
        ''')
        
        bills_data = cursor.fetchall()
        
        # 발의자 관계 분석
        relationships = {}
        
        for bill_id, ppsr_nm, ppsr_knd, ppsl_dt in bills_data:
            if not ppsr_nm or ppsr_nm == '':
                continue
                
            # 발의자 이름 파싱 (여러 명일 수 있음)
            sponsors = self._parse_sponsors(ppsr_nm)
            
            if len(sponsors) > 1:
                # 공동발의 관계 구축
                for i, sponsor_a in enumerate(sponsors):
                    for j, sponsor_b in enumerate(sponsors):
                        if i != j:
                            key = tuple(sorted([sponsor_a, sponsor_b]))
                            if key not in relationships:
                                relationships[key] = {
                                    'count': 0,
                                    'last_date': ppsl_dt,
                                    'bills': []
                                }
                            relationships[key]['count'] += 1
                            relationships[key]['last_date'] = max(
                                relationships[key]['last_date'], ppsl_dt
                            )
                            relationships[key]['bills'].append(bill_id)
        
        # 연결성 네트워크 테이블에 저장
        cursor.execute('DELETE FROM connectivity_network WHERE connection_type = "co_sponsor"')
        
        for (politician_a, politician_b), data in relationships.items():
            cursor.execute('''
                INSERT INTO connectivity_network (
                    politician_a, politician_b, connection_strength, 
                    connection_type, bill_count, last_collaboration
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                politician_a, politician_b, data['count'],
                'co_sponsor', data['count'], data['last_date']
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"{len(relationships)}개 발의자 관계 분석 완료")
        return relationships
    
    def _parse_sponsors(self, ppsr_nm: str) -> List[str]:
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
    
    def get_connectivity_stats(self) -> Dict:
        """연결성 통계 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 전체 통계
        cursor.execute('SELECT COUNT(*) FROM bills')
        total_bills = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM connectivity_network')
        total_connections = cursor.fetchone()[0]
        
        # 가장 활발한 연결
        cursor.execute('''
            SELECT politician_a, politician_b, connection_strength, bill_count
            FROM connectivity_network 
            ORDER BY connection_strength DESC 
            LIMIT 10
        ''')
        top_connections = cursor.fetchall()
        
        # 정당별 연결성
        cursor.execute('''
            SELECT cn.politician_a, cn.politician_b, cn.connection_strength,
                   p1.party_name as party_a, p2.party_name as party_b
            FROM connectivity_network cn
            LEFT JOIN politicians p1 ON cn.politician_a = p1.name
            LEFT JOIN politicians p2 ON cn.politician_b = p2.name
            ORDER BY cn.connection_strength DESC
            LIMIT 20
        ''')
        party_connections = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_bills': total_bills,
            'total_connections': total_connections,
            'top_connections': top_connections,
            'party_connections': party_connections
        }
    
    def load_politicians_from_json(self, json_path: str = "data/politicians.json"):
        """기존 정치인 데이터 로드"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                politicians_data = json.load(f)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for politician in politicians_data:
                cursor.execute('''
                    INSERT OR REPLACE INTO politicians (name, party_name, district, committee)
                    VALUES (?, ?, ?, ?)
                ''', (
                    politician.get('name', ''),
                    politician.get('party', ''),
                    politician.get('district', ''),
                    politician.get('committee', '')
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"{len(politicians_data)}명 정치인 데이터 로드 완료")
            return len(politicians_data)
            
        except Exception as e:
            logger.error(f"정치인 데이터 로드 실패: {e}")
            return 0
    
    def analyze_meeting_connectivity(self, meeting_db_path: str = "meeting_records_simple.db"):
        """회의록 기반 연결성 분석"""
        try:
            # 회의록 데이터베이스 연결
            meeting_conn = sqlite3.connect(meeting_db_path)
            meeting_cursor = meeting_conn.cursor()
            
            # 연결성 데이터베이스 연결
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 기존 회의록 연결성 삭제
            cursor.execute('DELETE FROM connectivity_network WHERE connection_type = "meeting"')
            
            # 위원회별 정치인 그룹 분석
            meeting_cursor.execute('''
                SELECT DISTINCT committee_name, speaker_name 
                FROM meetings m
                JOIN speakers s ON m.id = s.meeting_id
                WHERE committee_name IS NOT NULL AND speaker_name IS NOT NULL
            ''')
            
            committee_members = {}
            for committee, speaker in meeting_cursor.fetchall():
                if committee not in committee_members:
                    committee_members[committee] = set()
                committee_members[committee].add(speaker)
            
            # 위원회 내 연결성 구축
            for committee, members in committee_members.items():
                members_list = list(members)
                for i, member_a in enumerate(members_list):
                    for j, member_b in enumerate(members_list):
                        if i < j:  # 중복 방지
                            # 같은 위원회에서 함께 활동한 횟수 계산
                            meeting_cursor.execute('''
                                SELECT COUNT(DISTINCT m.id)
                                FROM meetings m
                                JOIN speakers s1 ON m.id = s1.meeting_id
                                JOIN speakers s2 ON m.id = s2.meeting_id
                                WHERE m.committee_name = ? 
                                AND s1.speaker_name = ? 
                                AND s2.speaker_name = ?
                            ''', (committee, member_a, member_b))
                            
                            meeting_count = meeting_cursor.fetchone()[0]
                            
                            if meeting_count > 0:
                                cursor.execute('''
                                    INSERT INTO connectivity_network (
                                        politician_a, politician_b, connection_strength,
                                        connection_type, meeting_count, last_collaboration
                                    ) VALUES (?, ?, ?, ?, ?, ?)
                                ''', (
                                    member_a, member_b, meeting_count,
                                    'meeting', meeting_count, datetime.now().strftime('%Y-%m-%d')
                                ))
            
            conn.commit()
            meeting_conn.close()
            conn.close()
            
            logger.info(f"{len(committee_members)}개 위원회 연결성 분석 완료")
            return len(committee_members)
            
        except Exception as e:
            logger.error(f"회의록 연결성 분석 실패: {e}")
            return 0
    
    def run_full_analysis(self):
        """전체 분석 실행"""
        logger.info("정치인 데이터 로드 시작...")
        politicians_count = self.load_politicians_from_json()
        
        logger.info("회의록 기반 연결성 분석 시작...")
        committee_count = self.analyze_meeting_connectivity()
        
        logger.info("연결성 통계 생성 중...")
        stats = self.get_connectivity_stats()
        
        return {
            'politicians_count': politicians_count,
            'committee_count': committee_count,
            'stats': stats
        }

if __name__ == "__main__":
    service = BillAPIService()
    result = service.run_full_analysis()
    print(f"분석 완료: {result}")
