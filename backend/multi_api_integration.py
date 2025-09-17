#!/usr/bin/env python3
"""
다중 API 키 통합 시스템
6개의 API 키를 모두 사용하여 안정적인 데이터 수집
이전에 해결했던 방식을 적용하여 호출 방법 문제 해결
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

class MultiAPIIntegration:
    """다중 API 키 통합 시스템"""
    
    def __init__(self, db_path: str = "multi_api_data.db"):
        self.db_path = db_path
        
        # API 키 설정 파일에서 로드
        from api_key_config import API_KEYS, API_CONFIG, HEADERS
        self.api_keys = API_KEYS
        self.api_config = API_CONFIG
        self.headers = HEADERS
        
        # API 키 인덱스 (로테이션용)
        self.current_key_index = 0
        
        # 국회 API 기본 URL
        self.base_url = self.api_config["base_url"]
        
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
        
        # API 호출 로그 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_call_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key_index INTEGER,
                endpoint TEXT,
                status_code INTEGER,
                success BOOLEAN,
                error_message TEXT,
                call_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("데이터베이스 초기화 완료")
    
    def get_next_api_key(self) -> str:
        """다음 API 키 가져오기 (로테이션)"""
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key
    
    def log_api_call(self, api_key_index: int, endpoint: str, status_code: int, success: bool, error_message: str = None):
        """API 호출 로그 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO api_call_logs 
                (api_key_index, endpoint, status_code, success, error_message)
                VALUES (?, ?, ?, ?, ?)
            ''', (api_key_index, endpoint, status_code, success, error_message))
            
            conn.commit()
        except Exception as e:
            logger.error(f"API 호출 로그 저장 실패: {e}")
        finally:
            conn.close()
    
    def make_api_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """API 요청 (이전에 해결했던 방식 적용)"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # API 키 로테이션
                api_key = self.get_next_api_key()
                api_key_index = self.current_key_index - 1
                if api_key_index < 0:
                    api_key_index = len(self.api_keys) - 1
                
                # 파라미터에 API 키 추가
                params['KEY'] = api_key
                
                # URL 구성
                url = f"{self.base_url}/{endpoint}"
                
                # 헤더 설정 (이전에 해결했던 방식)
                headers = self.headers
                
                # 요청 전송
                logger.info(f"API 요청 시도 {attempt + 1}/{max_retries}: {endpoint} (키: {api_key_index + 1})")
                response = requests.get(url, params=params, headers=headers, timeout=self.api_config["timeout"])
                
                # 응답 상태 로그
                self.log_api_call(api_key_index, endpoint, response.status_code, response.status_code == 200)
                
                if response.status_code == 200:
                    # XML 파싱
                    try:
                        root = ET.fromstring(response.text)
                        
                        # 에러 체크
                        result_code = root.find('.//RESULT/CODE')
                        if result_code is not None and result_code.text != 'INFO-000':
                            error_msg = f"API 에러: {result_code.text}"
                            logger.warning(error_msg)
                            self.log_api_call(api_key_index, endpoint, response.status_code, False, error_msg)
                            
                            # 다음 API 키로 재시도
                            time.sleep(self.api_config["retry_delay"])
                            continue
                        
                        # 성공적인 응답
                        logger.info(f"API 호출 성공: {endpoint} (키: {api_key_index + 1})")
                        return {
                            'success': True,
                            'data': root,
                            'api_key_used': api_key_index + 1
                        }
                        
                    except ET.ParseError as e:
                        error_msg = f"XML 파싱 실패: {e}"
                        logger.warning(error_msg)
                        self.log_api_call(api_key_index, endpoint, response.status_code, False, error_msg)
                        
                        # 다음 API 키로 재시도
                        time.sleep(self.api_config["retry_delay"])
                        continue
                
                else:
                    error_msg = f"HTTP 에러: {response.status_code}"
                    logger.warning(error_msg)
                    self.log_api_call(api_key_index, endpoint, response.status_code, False, error_msg)
                    
                    # 다음 API 키로 재시도
                    time.sleep(self.api_config["retry_delay"])
                    continue
                    
            except requests.exceptions.Timeout:
                error_msg = "요청 타임아웃"
                logger.warning(error_msg)
                self.log_api_call(api_key_index, endpoint, 0, False, error_msg)
                time.sleep(self.api_config["retry_delay"] * 2)
                continue
                
            except requests.exceptions.RequestException as e:
                error_msg = f"요청 실패: {e}"
                logger.warning(error_msg)
                self.log_api_call(api_key_index, endpoint, 0, False, error_msg)
                time.sleep(self.api_config["retry_delay"] * 2)
                continue
        
        # 모든 재시도 실패
        logger.error(f"API 호출 최종 실패: {endpoint}")
        return {
            'success': False,
            'error': '모든 API 키로 호출 실패'
        }
    
    def fetch_assembly_members(self) -> List[Dict]:
        """22대 국회의원 정보 수집"""
        members = []
        
        try:
            params = {
                'Type': 'xml',
                'pIndex': 1,
                'pSize': 300
            }
            
            result = self.make_api_request('getMemberCurrStateList', params)
            
            if not result or not result['success']:
                logger.error("의원 정보 수집 실패")
                return members
            
            root = result['data']
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
    
    def fetch_assembly_bills(self, limit: int = 100) -> List[Dict]:
        """22대 법안 정보 수집"""
        bills = []
        
        try:
            logger.info("22대 법안 정보 수집 시작...")
            
            # 22대 국회 법안 번호 범위 (2200001 ~ 2299999)
            start_bill_no = 2200001
            end_bill_no = min(2200001 + limit, 2299999)
            
            for bill_no in range(start_bill_no, end_bill_no + 1):
                params = {
                    'Type': 'xml',
                    'pIndex': 1,
                    'pSize': 1,
                    'BILL_NO': str(bill_no)
                }
                
                result = self.make_api_request('getBillInfoList', params)
                
                if not result or not result['success']:
                    continue
                
                root = result['data']
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
                
                # API 호출 제한 고려
                time.sleep(self.api_config["rate_limit_delay"])
                
                # 진행 상황 출력
                if (bill_no - start_bill_no + 1) % 50 == 0:
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
    
    def print_api_statistics(self):
        """API 호출 통계 출력"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 전체 통계
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_calls,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_calls,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_calls
                FROM api_call_logs
            ''')
            stats = cursor.fetchone()
            
            # API 키별 통계
            cursor.execute('''
                SELECT 
                    api_key_index + 1 as key_number,
                    COUNT(*) as total_calls,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_calls,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_calls
                FROM api_call_logs
                GROUP BY api_key_index
                ORDER BY api_key_index
            ''')
            key_stats = cursor.fetchall()
            
            print("\n📊 API 호출 통계")
            print(f"전체 호출: {stats[0]}회")
            print(f"성공: {stats[1]}회 ({stats[1]/stats[0]*100:.1f}%)")
            print(f"실패: {stats[2]}회 ({stats[2]/stats[0]*100:.1f}%)")
            
            print("\n🔑 API 키별 통계:")
            for key_stat in key_stats:
                key_num, total, success, failed = key_stat
                success_rate = (success / total * 100) if total > 0 else 0
                print(f"  키 {key_num}: {total}회 호출, 성공 {success}회 ({success_rate:.1f}%)")
            
        except Exception as e:
            logger.error(f"통계 출력 실패: {e}")
        finally:
            conn.close()
    
    def run_full_integration(self):
        """전체 데이터 연동 실행"""
        try:
            logger.info("다중 API 키를 사용한 데이터 연동 시작...")
            
            # 1. 의원 정보 수집
            politicians = self.fetch_assembly_members()
            if politicians:
                self.save_politicians(politicians)
            
            # 2. 법안 정보 수집 (제한적으로)
            bills = self.fetch_assembly_bills(limit=50)  # 테스트용으로 50개만
            if bills:
                self.save_bills(bills)
            
            # 3. API 호출 통계 출력
            self.print_api_statistics()
            
            logger.info("다중 API 키 데이터 연동 완료")
            
        except Exception as e:
            logger.error(f"데이터 연동 실패: {e}")

def main():
    """메인 함수"""
    try:
        # 다중 API 통합 시스템 초기화
        integration = MultiAPIIntegration()
        
        # 전체 데이터 연동 실행
        integration.run_full_integration()
        
    except Exception as e:
        logger.error(f"다중 API 통합 실패: {e}")

if __name__ == "__main__":
    main()
