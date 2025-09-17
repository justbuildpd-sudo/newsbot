#!/usr/bin/env python3
"""
실제 데이터 연동 시스템
국회 API를 통한 22대 국회 데이터 수집 및 통합
"""

import os
import json
import sqlite3
import requests
import xml.etree.ElementTree as ET
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealDataIntegration:
    """실제 데이터 연동 시스템"""
    
    def __init__(self, db_path: str = "real_politician_data.db"):
        self.db_path = db_path
        self.assembly_api_key = "YOUR_ASSEMBLY_API_KEY"  # 실제 API 키로 교체 필요
        self.base_url = "http://apis.data.go.kr/9710000/NationalAssemblyInfoService"
        
        # 데이터베이스 초기화
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 정치인 정보 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS politicians (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                party TEXT,
                district TEXT,
                committee TEXT,
                position TEXT,
                term TEXT,
                photo_url TEXT,
                connectivity_score REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 법안 정보 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id TEXT UNIQUE,
                bill_name TEXT,
                proposer_name TEXT,
                proposer_party TEXT,
                committee TEXT,
                status TEXT,
                proposal_date TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 연결성 정보 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                politician1 TEXT,
                politician2 TEXT,
                connection_type TEXT,
                strength REAL,
                description TEXT,
                level INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 평가 점수 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluation_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                politician_name TEXT,
                legislative_score REAL,
                connectivity_score REAL,
                news_score REAL,
                total_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("데이터베이스 초기화 완료")
    
    def fetch_assembly_members(self) -> List[Dict]:
        """국회 API에서 22대 국회의원 정보 수집"""
        members = []
        
        try:
            url = f"{self.base_url}/getMemberCurrStateList"
            params = {
                'KEY': self.assembly_api_key,
                'Type': 'xml',
                'pIndex': 1,
                'pSize': 300
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            logger.info("22대 국회의원 정보 수집 시작...")
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"API 호출 실패: {response.status_code}")
                return members
            
            # XML 파싱
            root = ET.fromstring(response.text)
            
            # 에러 체크
            result_code = root.find('.//RESULT/CODE')
            if result_code is not None and result_code.text != 'INFO-000':
                logger.error(f"API 에러: {result_code.text}")
                return members
            
            # 의원 정보 추출
            rows = root.findall('.//row')
            logger.info(f"수집된 의원 수: {len(rows)}")
            
            for row in rows:
                member_data = {}
                for child in row:
                    member_data[child.tag] = child.text if child.text else ''
                
                # 22대 국회 데이터만 필터링
                if member_data.get('ERACO', '') == '제22대':
                    members.append({
                        'name': member_data.get('HG_NM', ''),
                        'party': member_data.get('POLY_NM', ''),
                        'district': member_data.get('ORIG_NM', ''),
                        'committee': member_data.get('CMIT_NM', ''),
                        'position': '국회의원',
                        'term': '22대',
                        'photo_url': f"https://via.placeholder.com/120x150/3498db/ffffff?text={member_data.get('HG_NM', '')[:2]}"
                    })
            
            logger.info(f"22대 국회의원 정보 수집 완료: {len(members)}명")
            return members
            
        except Exception as e:
            logger.error(f"의원 정보 수집 실패: {e}")
            return members
    
    def fetch_assembly_bills(self, limit: int = 1000) -> List[Dict]:
        """국회 API에서 22대 법안 정보 수집"""
        bills = []
        
        try:
            logger.info("22대 법안 정보 수집 시작...")
            
            # 22대 국회 법안 번호 범위 (2200001 ~ 2299999)
            start_bill_no = 2200001
            end_bill_no = min(2200001 + limit, 2299999)
            
            for bill_no in range(start_bill_no, end_bill_no + 1):
                url = f"{self.base_url}/getBillInfoList"
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
                    
                    # 에러 체크
                    result_code = root.find('.//RESULT/CODE')
                    if result_code is not None and result_code.text != 'INFO-000':
                        continue
                    
                    # 법안 정보 추출
                    rows = root.findall('.//row')
                    if len(rows) == 0:
                        continue
                    
                    for row in rows:
                        bill_data = {}
                        for child in row:
                            bill_data[child.tag] = child.text if child.text else ''
                        
                        # 22대 국회 데이터만 필터링
                        if bill_data.get('ERACO', '') == '제22대':
                            bills.append({
                                'bill_id': bill_data.get('BILL_ID', ''),
                                'bill_name': bill_data.get('BILL_NM', ''),
                                'proposer_name': bill_data.get('PROPOSER', ''),
                                'proposer_party': bill_data.get('PROPOSER_PARTY', ''),
                                'committee': bill_data.get('COMMITTEE', ''),
                                'status': bill_data.get('STATUS', ''),
                                'proposal_date': bill_data.get('PROPOSAL_DATE', ''),
                                'content': bill_data.get('CONTENT', '')
                            })
                            logger.info(f"법안 수집: {bill_data.get('BILL_NM', '')} (번호: {bill_data.get('BILL_ID', '')})")
                
                except ET.ParseError:
                    continue
                except Exception as e:
                    logger.debug(f"법안번호 {bill_no} 조회 실패: {e}")
                    continue
                
                # API 호출 제한 고려
                time.sleep(0.1)
                
                # 진행 상황 출력
                if (bill_no - start_bill_no + 1) % 100 == 0:
                    logger.info(f"법안 수집 진행: {bill_no - start_bill_no + 1}/{limit}")
            
            logger.info(f"22대 법안 정보 수집 완료: {len(bills)}건")
            return bills
            
        except Exception as e:
            logger.error(f"법안 정보 수집 실패: {e}")
            return bills
    
    def save_politicians(self, politicians: List[Dict]):
        """정치인 정보 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for politician in politicians:
                cursor.execute('''
                    INSERT OR REPLACE INTO politicians 
                    (name, party, district, committee, position, term, photo_url, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    politician['name'],
                    politician['party'],
                    politician['district'],
                    politician['committee'],
                    politician['position'],
                    politician['term'],
                    politician['photo_url']
                ))
            
            conn.commit()
            logger.info(f"정치인 정보 저장 완료: {len(politicians)}명")
            
        except Exception as e:
            logger.error(f"정치인 정보 저장 실패: {e}")
        finally:
            conn.close()
    
    def save_bills(self, bills: List[Dict]):
        """법안 정보 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for bill in bills:
                cursor.execute('''
                    INSERT OR REPLACE INTO bills 
                    (bill_id, bill_name, proposer_name, proposer_party, committee, status, proposal_date, content)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    bill['bill_id'],
                    bill['bill_name'],
                    bill['proposer_name'],
                    bill['proposer_party'],
                    bill['committee'],
                    bill['status'],
                    bill['proposal_date'],
                    bill['content']
                ))
            
            conn.commit()
            logger.info(f"법안 정보 저장 완료: {len(bills)}건")
            
        except Exception as e:
            logger.error(f"법안 정보 저장 실패: {e}")
        finally:
            conn.close()
    
    def analyze_connections(self):
        """연결성 분석"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 기존 연결성 데이터 삭제
            cursor.execute('DELETE FROM connections')
            
            # 정치인 목록 조회
            cursor.execute('SELECT name, party, district, committee FROM politicians')
            politicians = cursor.fetchall()
            
            logger.info(f"연결성 분석 시작: {len(politicians)}명")
            
            for i, p1 in enumerate(politicians):
                p1_name, p1_party, p1_district, p1_committee = p1
                
                for j, p2 in enumerate(politicians):
                    if i >= j:  # 중복 방지
                        continue
                    
                    p2_name, p2_party, p2_district, p2_committee = p2
                    
                    connections = []
                    
                    # 같은 정당 연결
                    if p1_party and p2_party and p1_party == p2_party:
                        connections.append({
                            'type': '정치적_연결',
                            'strength': 0.9,
                            'description': '같은 정당'
                        })
                    
                    # 같은 위원회 연결
                    if p1_committee and p2_committee and p1_committee == p2_committee:
                        connections.append({
                            'type': '위원회_연결',
                            'strength': 0.8,
                            'description': '같은 위원회'
                        })
                    
                    # 같은 지역구 연결 (간단한 지역명 비교)
                    if p1_district and p2_district:
                        p1_region = p1_district.split()[0] if ' ' in p1_district else p1_district
                        p2_region = p2_district.split()[0] if ' ' in p2_district else p2_district
                        if p1_region == p2_region:
                            connections.append({
                                'type': '지역_연결',
                                'strength': 0.7,
                                'description': '같은 지역'
                            })
                    
                    # 연결 정보 저장
                    for conn in connections:
                        cursor.execute('''
                            INSERT INTO connections 
                            (politician1, politician2, connection_type, strength, description, level)
                            VALUES (?, ?, ?, ?, ?, 1)
                        ''', (p1_name, p2_name, conn['type'], conn['strength'], conn['description']))
            
            conn.commit()
            logger.info("연결성 분석 완료")
            
        except Exception as e:
            logger.error(f"연결성 분석 실패: {e}")
        finally:
            conn.close()
    
    def calculate_evaluation_scores(self):
        """평가 점수 계산"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 기존 평가 점수 삭제
            cursor.execute('DELETE FROM evaluation_scores')
            
            # 정치인별 평가 점수 계산
            cursor.execute('SELECT name FROM politicians')
            politicians = cursor.fetchall()
            
            for politician in politicians:
                name = politician[0]
                
                # 입법 성과 점수 (발의 법안 수 기반)
                cursor.execute('''
                    SELECT COUNT(*) FROM bills 
                    WHERE proposer_name = ?
                ''', (name,))
                bill_count = cursor.fetchone()[0] or 0
                legislative_score = min(bill_count * 2, 100)  # 최대 100점
                
                # 연결성 점수 (연결 수 기반)
                cursor.execute('''
                    SELECT COUNT(*) FROM connections 
                    WHERE politician1 = ? OR politician2 = ?
                ''', (name, name))
                connection_count = cursor.fetchone()[0] or 0
                connectivity_score = min(connection_count * 5, 100)  # 최대 100점
                
                # 뉴스 점수 (현재는 기본값)
                news_score = 50.0
                
                # 총점 계산
                total_score = (legislative_score * 0.4 + connectivity_score * 0.4 + news_score * 0.2)
                
                # 평가 점수 저장
                cursor.execute('''
                    INSERT INTO evaluation_scores 
                    (politician_name, legislative_score, connectivity_score, news_score, total_score)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, legislative_score, connectivity_score, news_score, total_score))
            
            conn.commit()
            logger.info("평가 점수 계산 완료")
            
        except Exception as e:
            logger.error(f"평가 점수 계산 실패: {e}")
        finally:
            conn.close()
    
    def run_full_integration(self):
        """전체 데이터 연동 실행"""
        try:
            logger.info("실제 데이터 연동 시작...")
            
            # 1. 의원 정보 수집
            politicians = self.fetch_assembly_members()
            if politicians:
                self.save_politicians(politicians)
            
            # 2. 법안 정보 수집 (제한적으로)
            bills = self.fetch_assembly_bills(limit=100)  # 테스트용으로 100개만
            if bills:
                self.save_bills(bills)
            
            # 3. 연결성 분석
            self.analyze_connections()
            
            # 4. 평가 점수 계산
            self.calculate_evaluation_scores()
            
            logger.info("실제 데이터 연동 완료")
            
            # 결과 요약
            self.print_summary()
            
        except Exception as e:
            logger.error(f"데이터 연동 실패: {e}")
    
    def print_summary(self):
        """결과 요약 출력"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 정치인 수
            cursor.execute('SELECT COUNT(*) FROM politicians')
            politician_count = cursor.fetchone()[0]
            
            # 법안 수
            cursor.execute('SELECT COUNT(*) FROM bills')
            bill_count = cursor.fetchone()[0]
            
            # 연결 수
            cursor.execute('SELECT COUNT(*) FROM connections')
            connection_count = cursor.fetchone()[0]
            
            # 상위 정치인 (총점 기준)
            cursor.execute('''
                SELECT politician_name, total_score 
                FROM evaluation_scores 
                ORDER BY total_score DESC 
                LIMIT 5
            ''')
            top_politicians = cursor.fetchall()
            
            print("\n📊 데이터 연동 결과 요약")
            print(f"정치인 수: {politician_count}명")
            print(f"법안 수: {bill_count}건")
            print(f"연결 수: {connection_count}개")
            print("\n🏆 상위 정치인 (총점 기준):")
            for i, (name, score) in enumerate(top_politicians, 1):
                print(f"  {i}. {name}: {score:.1f}점")
            
        except Exception as e:
            logger.error(f"요약 출력 실패: {e}")
        finally:
            conn.close()

def main():
    """메인 함수"""
    try:
        # 실제 데이터 연동 시스템 초기화
        integration = RealDataIntegration()
        
        # 전체 데이터 연동 실행
        integration.run_full_integration()
        
    except Exception as e:
        logger.error(f"실제 데이터 연동 실패: {e}")

if __name__ == "__main__":
    main()

