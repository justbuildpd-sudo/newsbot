#!/usr/bin/env python3
"""
열린국회정보 Open API 통합 시스템
올바른 API 주소와 방식으로 6개의 API 키를 모두 사용
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

class OpenAssemblyAPIIntegration:
    """열린국회정보 Open API 통합 시스템"""
    
    def __init__(self, db_path: str = "open_assembly_data.db"):
        self.db_path = db_path
        
        # API 키 설정 파일에서 로드
        from api_key_config import API_KEYS, API_CONFIG, HEADERS, ENDPOINTS, API_KEY_REQUIRED_MESSAGE
        self.api_keys = API_KEYS
        self.api_config = API_CONFIG
        self.headers = HEADERS
        self.endpoints = ENDPOINTS
        self.api_key_message = API_KEY_REQUIRED_MESSAGE
        
        # API 키 유효성 검사
        self.validate_api_keys()
        
        # API 키 인덱스 (로테이션용)
        self.current_key_index = 0
        
        # 열린국회정보 Open API 기본 URL
        self.base_url = self.api_config["base_url"]
        
        # 데이터베이스 초기화
        self.init_database()
    
    def validate_api_keys(self):
        """API 키 유효성 검사"""
        invalid_keys = []
        for i, key in enumerate(self.api_keys):
            if key.startswith("YOUR_API_KEY_"):
                invalid_keys.append(f"키 {i+1}")
        
        if invalid_keys:
            logger.warning("⚠️  API 키가 설정되지 않았습니다!")
            logger.warning(f"다음 키들이 실제 키로 교체되어야 합니다: {', '.join(invalid_keys)}")
            logger.warning("API 키 발급 방법:")
            logger.warning("1. 열린국회정보 홈페이지 (https://open.assembly.go.kr) 방문")
            logger.warning("2. 회원가입 후 API 키 발급 신청")
            logger.warning("3. 발급받은 키를 api_key_config.py 파일에 입력")
            logger.warning("")
            logger.warning("현재는 샘플 데이터로 테스트를 진행합니다.")
    
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
        """열린국회정보 Open API 요청 (올바른 방식)"""
        max_retries = self.api_config["retry_count"]
        
        for attempt in range(max_retries):
            try:
                # API 키 로테이션
                api_key = self.get_next_api_key()
                api_key_index = self.current_key_index - 1
                if api_key_index < 0:
                    api_key_index = len(self.api_keys) - 1
                
                # 기본 파라미터 설정 (열린국회정보 Open API 방식)
                request_params = {
                    'serviceKey': api_key,    # 인증키 (필수)
                    'resultType': 'xml',      # 호출문서 (기본값: xml)
                    'pageNo': 1,              # 페이지 위치 (기본값: 1)
                    'numOfRows': 100          # 페이지당 요청숫자 (기본값: 100)
                }
                
                # 요청인자 추가
                request_params.update(params)
                
                # URL 구성 (열린국회정보 Open API 방식)
                url = f"{self.base_url}/{endpoint}"
                
                # 요청 전송
                logger.info(f"API 요청 시도 {attempt + 1}/{max_retries}: {endpoint} (키: {api_key_index + 1})")
                logger.info(f"요청 URL: {url}")
                logger.info(f"요청 파라미터: {request_params}")
                
                response = requests.get(url, params=request_params, headers=self.headers, timeout=self.api_config["timeout"])
                
                # 응답 상태 로그
                self.log_api_call(api_key_index, endpoint, response.status_code, response.status_code == 200)
                
                if response.status_code == 200:
                    # XML 파싱
                    try:
                        root = ET.fromstring(response.text)
                        
                        # 에러 체크 (열린국회정보 Open API 응답 형식)
                        result_code = root.find('.//resultCode')
                        if result_code is not None and result_code.text != '00':
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
            # 열린국회정보 Open API 파라미터
            params = {
                'numOfRows': 300  # 한 번에 최대 300명까지 조회
            }
            
            result = self.make_api_request(self.endpoints["members"], params)
            
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
                if member_data.get('era', '') == '제22대':
                    members.append({
                        'name': member_data.get('name', ''),
                        'party': member_data.get('party', ''),
                        'district': member_data.get('district', ''),
                        'committee': member_data.get('committee', ''),
                        'position': '국회의원',
                        'term': '22대',
                        'photo_url': f"https://via.placeholder.com/120x150/3498db/ffffff?text={member_data.get('name', '')[:2]}"
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
                # 열린국회정보 Open API 파라미터
                params = {
                    'billId': str(bill_no)  # 법안번호
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
                    if bill_data.get('era', '') == '제22대':
                        bills.append({
                            'bill_id': bill_data.get('billId', ''),
                            'bill_name': bill_data.get('billName', ''),
                            'proposer_name': bill_data.get('proposer', ''),
                            'proposer_party': bill_data.get('proposerParty', ''),
                            'committee': bill_data.get('committee', ''),
                            'status': bill_data.get('status', ''),
                            'proposal_date': bill_data.get('proposalDate', ''),
                            'content': bill_data.get('content', '')
                        })
                        logger.info(f"법안 수집: {bill_data.get('billName', '')} (번호: {bill_data.get('billId', '')})")
                
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
            
            print("\n📊 열린국회정보 Open API 호출 통계")
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
    
    def create_sample_data(self):
        """샘플 데이터 생성 (API 키가 없을 때 사용)"""
        logger.info("샘플 데이터 생성 중...")
        
        # 샘플 의원 데이터
        sample_politicians = [
            {
                'name': '정청래',
                'party': '더불어민주당',
                'district': '서울 마포구을',
                'committee': '기획재정위원회',
                'position': '국회의원',
                'term': '22대',
                'photo_url': 'https://via.placeholder.com/120x150/3498db/ffffff?text=정청래'
            },
            {
                'name': '김주영',
                'party': '국민의힘',
                'district': '경기 김포시갑',
                'committee': '과학기술정보방송통신위원회',
                'position': '국회의원',
                'term': '22대',
                'photo_url': 'https://via.placeholder.com/120x150/e74c3c/ffffff?text=김주영'
            },
            {
                'name': '신장식',
                'party': '더불어민주당',
                'district': '비례대표',
                'committee': '환경노동위원회',
                'position': '국회의원',
                'term': '22대',
                'photo_url': 'https://via.placeholder.com/120x150/2ecc71/ffffff?text=신장식'
            }
        ]
        
        # 샘플 법안 데이터
        sample_bills = [
            {
                'bill_id': '2200001',
                'bill_name': '국가재정법 일부개정법률안',
                'proposer_name': '정청래',
                'proposer_party': '더불어민주당',
                'committee': '기획재정위원회',
                'status': '위원회심사',
                'proposal_date': '2024-05-30',
                'content': '국가재정의 효율적 운영을 위한 개정안'
            },
            {
                'bill_id': '2200002',
                'bill_name': '과학기술기본법 일부개정법률안',
                'proposer_name': '김주영',
                'proposer_party': '국민의힘',
                'committee': '과학기술정보방송통신위원회',
                'status': '본회의통과',
                'proposal_date': '2024-06-01',
                'content': '과학기술 발전을 위한 기본법 개정'
            },
            {
                'bill_id': '2200003',
                'bill_name': '환경정책기본법 일부개정법률안',
                'proposer_name': '신장식',
                'proposer_party': '더불어민주당',
                'committee': '환경노동위원회',
                'status': '위원회심사',
                'proposal_date': '2024-06-05',
                'content': '환경보전을 위한 정책기본법 개정'
            }
        ]
        
        # 샘플 데이터 저장
        self.save_politicians(sample_politicians)
        self.save_bills(sample_bills)
        
        logger.info(f"샘플 데이터 생성 완료: 의원 {len(sample_politicians)}명, 법안 {len(sample_bills)}건")
        return sample_politicians, sample_bills

    def run_full_integration(self):
        """전체 데이터 연동 실행"""
        try:
            logger.info("열린국회정보 Open API를 사용한 데이터 연동 시작...")
            logger.info(f"사용할 API 키 수: {len(self.api_keys)}개")
            logger.info(f"API 기본 URL: {self.base_url}")
            
            # API 키 유효성 검사
            has_valid_keys = any(not key.startswith("YOUR_API_KEY_") for key in self.api_keys)
            
            if not has_valid_keys:
                logger.warning("유효한 API 키가 없습니다. 샘플 데이터를 생성합니다.")
                self.create_sample_data()
                return
            
            # 1. 의원 정보 수집
            politicians = self.fetch_assembly_members()
            if politicians:
                self.save_politicians(politicians)
            else:
                logger.warning("의원 정보 수집 실패. 샘플 데이터를 생성합니다.")
                self.create_sample_data()
            
            # 2. 법안 정보 수집 (제한적으로)
            bills = self.fetch_assembly_bills(limit=50)  # 테스트용으로 50개만
            if bills:
                self.save_bills(bills)
            
            # 3. API 호출 통계 출력
            self.print_api_statistics()
            
            logger.info("열린국회정보 Open API 데이터 연동 완료")
            
        except Exception as e:
            logger.error(f"데이터 연동 실패: {e}")
            logger.info("샘플 데이터를 생성합니다.")
            self.create_sample_data()

def main():
    """메인 함수"""
    try:
        # 열린국회정보 Open API 통합 시스템 초기화
        integration = OpenAssemblyAPIIntegration()
        
        # 전체 데이터 연동 실행
        integration.run_full_integration()
        
    except Exception as e:
        logger.error(f"열린국회정보 Open API 통합 실패: {e}")

if __name__ == "__main__":
    main()
