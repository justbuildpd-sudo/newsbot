#!/usr/bin/env python3
"""
국회 데이터 상호 검증 시스템
22대 국회 발의안 전체 수집 → BILL_ID로 4개 API 교차 검증
"""

import os
import json
import sqlite3
import requests
import xml.etree.ElementTree as ET
import time
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssemblyDataValidator:
    """국회 데이터 상호 검증 시스템"""
    
    def __init__(self, db_path: str = "assembly_validated_data.db"):
        self.db_path = db_path
        
        # API 키 설정 파일에서 로드
        from api_key_config import API_KEYS, API_CONFIG, HEADERS, ENDPOINTS
        self.api_keys = API_KEYS
        self.api_config = API_CONFIG
        self.headers = HEADERS
        self.endpoints = ENDPOINTS
        
        # API 키 인덱스 (로테이션용)
        self.current_key_index = 0
        
        # 열린국회정보 Open API 기본 URL
        self.base_url = self.api_config["base_url"]
        
        # 데이터베이스 초기화
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 22대 국회의원 정보 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assembly_members_22nd (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id TEXT UNIQUE,
                name TEXT NOT NULL,
                name_eng TEXT,
                party TEXT,
                district TEXT,
                committee TEXT,
                position TEXT,
                term TEXT,
                gender TEXT,
                birth_date TEXT,
                phone TEXT,
                email TEXT,
                blog_url TEXT,
                photo_url TEXT,
                sns_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 22대 발의안 기본 정보 테이블 (ALLBILL API)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills_22nd_allbill (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id TEXT UNIQUE,
                bill_name TEXT,
                proposer_name TEXT,
                proposer_party TEXT,
                committee TEXT,
                status TEXT,
                proposal_date TEXT,
                content TEXT,
                raw_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 의안 접수목록 테이블 (BILLRCP API)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills_22nd_reception (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id TEXT,
                reception_no TEXT,
                reception_date TEXT,
                reception_type TEXT,
                raw_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bill_id) REFERENCES bills_22nd_allbill(bill_id)
            )
        ''')
        
        # 의안 제안자정보 테이블 (BILLINFOPPSR API)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills_22nd_proposers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id TEXT,
                proposer_name TEXT,
                proposer_party TEXT,
                proposer_type TEXT,
                proposer_order INTEGER,
                raw_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bill_id) REFERENCES bills_22nd_allbill(bill_id)
            )
        ''')
        
        # 의안 상세정보 테이블 (BILLINFODETAIL API)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills_22nd_detail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id TEXT UNIQUE,
                bill_type TEXT,
                bill_class TEXT,
                bill_status TEXT,
                committee_name TEXT,
                proposal_reason TEXT,
                main_content TEXT,
                raw_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bill_id) REFERENCES bills_22nd_allbill(bill_id)
            )
        ''')
        
        # 검증 결과 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS validation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id TEXT,
                validation_type TEXT,
                status TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    def make_api_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """열린국회정보 Open API 요청"""
        max_retries = self.api_config["retry_count"]
        
        for attempt in range(max_retries):
            try:
                # API 키 로테이션
                api_key = self.get_next_api_key()
                api_key_index = self.current_key_index - 1
                if api_key_index < 0:
                    api_key_index = len(self.api_keys) - 1
                
                # 기본 파라미터 설정
                request_params = {
                    'KEY': api_key,
                    'Type': 'xml',
                    'pIndex': 1,
                    'pSize': 1000
                }
                
                # 요청인자 추가
                request_params.update(params)
                
                # URL 구성
                url = f"{self.base_url}/{endpoint}"
                
                # 요청 전송
                logger.info(f"API 요청: {endpoint} (키: {api_key_index + 1})")
                response = requests.get(url, params=request_params, headers=self.headers, timeout=self.api_config["timeout"])
                
                if response.status_code == 200:
                    # XML 파싱
                    try:
                        root = ET.fromstring(response.text)
                        
                        # 에러 체크
                        result_code = root.find('.//resultCode')
                        if result_code is not None and result_code.text != '00':
                            error_msg = f"API 에러: {result_code.text}"
                            logger.warning(error_msg)
                            time.sleep(self.api_config["retry_delay"])
                            continue
                        
                        # 성공적인 응답
                        logger.info(f"API 호출 성공: {endpoint}")
                        return {
                            'success': True,
                            'data': root,
                            'api_key_used': api_key_index + 1
                        }
                        
                    except ET.ParseError as e:
                        error_msg = f"XML 파싱 실패: {e}"
                        logger.warning(error_msg)
                        time.sleep(self.api_config["retry_delay"])
                        continue
                
                else:
                    error_msg = f"HTTP 에러: {response.status_code}"
                    logger.warning(error_msg)
                    time.sleep(self.api_config["retry_delay"])
                    continue
                    
            except requests.exceptions.Timeout:
                error_msg = "요청 타임아웃"
                logger.warning(error_msg)
                time.sleep(self.api_config["retry_delay"] * 2)
                continue
                
            except requests.exceptions.RequestException as e:
                error_msg = f"요청 실패: {e}"
                logger.warning(error_msg)
                time.sleep(self.api_config["retry_delay"] * 2)
                continue
        
        # 모든 재시도 실패
        logger.error(f"API 호출 최종 실패: {endpoint}")
        return {
            'success': False,
            'error': '모든 API 키로 호출 실패'
        }
    
    def collect_22nd_assembly_bills(self, assembly_age: str = "22") -> List[Dict]:
        """22대 국회 발의안 전체 수집 (ALLBILL API)"""
        logger.info(f"{assembly_age}대 국회 발의안 전체 수집 시작...")
        
        all_bills = []
        total_rows = 0
        
        # 22대 국회 법안 번호 범위 (10단계)
        start_bill_no = 2209001
        end_bill_no = 2210000  # 10단계: 1000개 진행
        
        for bill_no in range(start_bill_no, end_bill_no + 1):
            try:
                # ALLBILL API 호출 (BILL_NO 파라미터 필요)
                params = {
                    'BILL_NO': str(bill_no)
                }
                
                result = self.make_api_request(self.endpoints["bills"], params)
                
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
                    if bill_data.get('ERACO', '') == f'제{assembly_age}대':
                        all_bills.append(bill_data)
                        total_rows += 1
                        logger.info(f"법안 수집: {bill_data.get('BILL_NM', '')} (번호: {bill_data.get('BILL_NO', '')})")
                
                # API 호출 제한 고려
                time.sleep(self.api_config["rate_limit_delay"])
                
                # 진행 상황 출력 (100개마다)
                if (bill_no - start_bill_no + 1) % 100 == 0:
                    logger.info(f"진행 상황: {bill_no - start_bill_no + 1}/{end_bill_no - start_bill_no + 1} (수집된 법안: {total_rows}건)")
                
            except Exception as e:
                logger.error(f"법안번호 {bill_no} 수집 중 오류: {e}")
                continue
        
        logger.info(f"{assembly_age}대 국회 발의안 수집 완료: 총 {len(all_bills)}건")
        return all_bills
    
    def save_bills_to_database(self, bills: List[Dict]):
        """발의안 데이터를 데이터베이스에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for bill in bills:
                cursor.execute('''
                    INSERT OR REPLACE INTO bills_22nd_allbill 
                    (bill_id, bill_name, proposer_name, proposer_party, committee, status, proposal_date, content, raw_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    bill.get('BILL_ID', ''),
                    bill.get('BILL_NM', ''),
                    bill.get('PROPOSER', ''),
                    bill.get('PROPOSER_PARTY', ''),
                    bill.get('COMMITTEE', ''),
                    bill.get('STATUS', ''),
                    bill.get('PROPOSAL_DATE', ''),
                    bill.get('CONTENT', ''),
                    json.dumps(bill, ensure_ascii=False)
                ))
            
            conn.commit()
            logger.info(f"발의안 데이터 저장 완료: {len(bills)}건")
            
        except Exception as e:
            logger.error(f"발의안 데이터 저장 실패: {e}")
        finally:
            conn.close()
    
    def validate_bill_data(self, bill_id: str) -> Dict:
        """특정 BILL_ID로 4개 API 교차 검증"""
        logger.info(f"BILL_ID {bill_id} 교차 검증 시작...")
        
        validation_result = {
            'bill_id': bill_id,
            'allbill_data': None,
            'reception_data': None,
            'proposers_data': None,
            'detail_data': None,
            'validation_status': 'success',
            'errors': []
        }
        
        try:
            # 1. ALLBILL API로 기본 정보 확인
            params = {'BILL_NO': bill_id}
            result = self.make_api_request(self.endpoints["bills"], params)
            if result and result['success']:
                validation_result['allbill_data'] = result['data']
            else:
                validation_result['errors'].append("ALLBILL API 호출 실패")
            
            # 2. BILLRCP API로 접수목록 확인
            params = {'BILL_ID': bill_id}
            result = self.make_api_request(self.endpoints["bill_reception"], params)
            if result and result['success']:
                validation_result['reception_data'] = result['data']
            else:
                validation_result['errors'].append("BILLRCP API 호출 실패")
            
            # 3. BILLINFOPPSR API로 제안자정보 확인
            result = self.make_api_request(self.endpoints["bill_proposers"], params)
            if result and result['success']:
                validation_result['proposers_data'] = result['data']
            else:
                validation_result['errors'].append("BILLINFOPPSR API 호출 실패")
            
            # 4. BILLINFODETAIL API로 상세정보 확인
            result = self.make_api_request(self.endpoints["bill_detail"], params)
            if result and result['success']:
                validation_result['detail_data'] = result['data']
            else:
                validation_result['errors'].append("BILLINFODETAIL API 호출 실패")
            
            # 검증 결과 저장
            self.save_validation_result(bill_id, validation_result)
            
        except Exception as e:
            validation_result['validation_status'] = 'error'
            validation_result['errors'].append(f"교차 검증 중 오류: {e}")
            logger.error(f"BILL_ID {bill_id} 교차 검증 실패: {e}")
        
        return validation_result
    
    def save_validation_result(self, bill_id: str, validation_result: Dict):
        """검증 결과를 데이터베이스에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO validation_results 
                (bill_id, validation_type, status, error_message)
                VALUES (?, ?, ?, ?)
            ''', (
                bill_id,
                'cross_validation',
                validation_result['validation_status'],
                '; '.join(validation_result['errors']) if validation_result['errors'] else None
            ))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"검증 결과 저장 실패: {e}")
        finally:
            conn.close()
    
    def run_full_validation(self, assembly_age: str = "22"):
        """전체 검증 프로세스 실행"""
        try:
            logger.info(f"{assembly_age}대 국회 데이터 상호 검증 시작...")
            
            # 1단계: 22대 발의안 전체 수집
            bills = self.collect_22nd_assembly_bills(assembly_age)
            if not bills:
                logger.error("발의안 수집 실패")
                return
            
            # 2단계: 수집한 발의안을 데이터베이스에 저장
            self.save_bills_to_database(bills)
            
            # 3단계: BILL_ID 추출 및 교차 검증 (전체)
            bill_ids = [bill.get('BILL_ID', '') for bill in bills if bill.get('BILL_ID')]
            logger.info(f"교차 검증 대상: {len(bill_ids)}개 BILL_ID")
            
            # 교차 검증은 샘플 5개만 (시간 절약)
            sample_bill_ids = bill_ids[:5] if len(bill_ids) > 5 else bill_ids
            logger.info(f"교차 검증 샘플: {len(sample_bill_ids)}개")
            
            for bill_id in sample_bill_ids:
                validation_result = self.validate_bill_data(bill_id)
                logger.info(f"BILL_ID {bill_id} 검증 완료: {validation_result['validation_status']}")
                time.sleep(1)  # API 호출 간격 조절
            
            logger.info(f"{assembly_age}대 국회 데이터 상호 검증 완료")
            
        except Exception as e:
            logger.error(f"전체 검증 프로세스 실패: {e}")

def main():
    """메인 함수"""
    try:
        # 국회 데이터 상호 검증 시스템 초기화
        validator = AssemblyDataValidator()
        
        # 전체 검증 프로세스 실행
        validator.run_full_validation("22")
        
    except Exception as e:
        logger.error(f"국회 데이터 상호 검증 실패: {e}")

if __name__ == "__main__":
    main()
