#!/usr/bin/env python3
"""
엑셀 회의록 파일 처리 시스템
국회 회의록 엑셀 파일들을 읽어서 발언 데이터를 추출하고 데이터베이스에 저장합니다.
"""

import os
import sqlite3
import pandas as pd
import logging
import re
from typing import Dict, List, Tuple
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class ExcelMeetingProcessor:
    def __init__(self, db_path: str = "meeting_records_processed.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # 회의 테이블
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetings (
                meeting_id TEXT PRIMARY KEY,
                title TEXT,
                date TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 발언 테이블
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS speeches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meeting_id TEXT,
                speaker_name TEXT,
                speech_content TEXT,
                speech_order INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (meeting_id) REFERENCES meetings (meeting_id)
            )
        ''')
        
        # 발언 통계 테이블
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS speech_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                politician_name TEXT,
                total_speeches INTEGER DEFAULT 0,
                total_words INTEGER DEFAULT 0,
                avg_speech_length REAL DEFAULT 0.0,
                committee_diversity INTEGER DEFAULT 0,
                last_speech_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        logger.info("데이터베이스 초기화 완료")
    
    def extract_politician_name_from_filename(self, filename: str) -> str:
        """파일명에서 정치인 이름 추출"""
        # 파일명 패턴: 통합검색_국회회의록_발언자목록_강득구+(姜得求)_2025-08-16.xlsx
        match = re.search(r'발언자목록_([^+]+)', filename)
        if match:
            return match.group(1).strip()
        return "알수없음"
    
    def extract_date_from_filename(self, file_path: str) -> str:
        """파일명에서 날짜 추출"""
        filename = os.path.basename(file_path)
        match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        if match:
            return match.group(1)
        return datetime.now().strftime('%Y-%m-%d')
    
    def process_excel_file(self, file_path: str) -> Dict:
        """개별 엑셀 파일 처리"""
        try:
            # 파일명에서 정치인 이름 추출
            filename = os.path.basename(file_path)
            politician_name = self.extract_politician_name_from_filename(filename)
            
            logger.info(f"처리 중: {politician_name} - {filename}")
            
            # 여러 엔진으로 엑셀 파일 읽기 시도
            df = None
            for engine in ['openpyxl', 'xlrd']:
                try:
                    df = pd.read_excel(file_path, engine=engine)
                    logger.info(f"엔진 {engine}으로 파일 읽기 성공")
                    break
                except Exception as e:
                    logger.warning(f"엔진 {engine} 실패: {e}")
                    continue
            
            if df is None:
                logger.error(f"모든 엔진으로 파일 읽기 실패: {file_path}")
                return {"success": False, "error": "파일 읽기 실패"}
            
            # 컬럼명 확인 및 정리
            df.columns = df.columns.astype(str)
            logger.info(f"컬럼명: {list(df.columns)}")
            
            # 발언자와 발언내용 컬럼 찾기
            speaker_col = None
            content_col = None
            
            for col in df.columns:
                col_lower = col.lower()
                if '발언자' in col or 'speaker' in col_lower or '이름' in col:
                    speaker_col = col
                elif '발언' in col or 'content' in col_lower or '내용' in col or '말씀' in col:
                    content_col = col
            
            if not speaker_col or not content_col:
                logger.warning(f"발언자 또는 발언내용 컬럼을 찾을 수 없습니다")
                logger.warning(f"사용 가능한 컬럼: {list(df.columns)}")
                return {"success": False, "error": "컬럼을 찾을 수 없음"}
            
            logger.info(f"발언자 컬럼: {speaker_col}, 발언내용 컬럼: {content_col}")
            
            # 회의 정보 생성
            meeting_id = f"meeting_{hash(file_path) % 1000000}"
            meeting_date = self.extract_date_from_filename(file_path)
            meeting_title = f"국회회의록_{politician_name}_{meeting_date}"
            
            # 회의 데이터 저장
            self.cursor.execute('''
                INSERT OR IGNORE INTO meetings (meeting_id, title, date, file_path)
                VALUES (?, ?, ?, ?)
            ''', (meeting_id, meeting_title, meeting_date, file_path))
            
            # 발언 데이터 처리
            speeches_processed = 0
            for idx, row in df.iterrows():
                speaker = str(row[speaker_col]).strip()
                content = str(row[content_col]).strip()
                
                if speaker and content and speaker != 'nan' and content != 'nan' and len(content) > 10:
                    # 발언 데이터 저장
                    self.cursor.execute('''
                        INSERT INTO speeches (meeting_id, speaker_name, speech_content, speech_order)
                        VALUES (?, ?, ?, ?)
                    ''', (meeting_id, speaker, content, speeches_processed + 1))
                    
                    speeches_processed += 1
            
            self.conn.commit()
            logger.info(f"✅ {filename}: {speeches_processed}발언 처리")
            
            return {
                "success": True,
                "politician_name": politician_name,
                "speeches_processed": speeches_processed,
                "meeting_id": meeting_id
            }
            
        except Exception as e:
            logger.error(f"파일 처리 실패 ({file_path}): {e}")
            return {"success": False, "error": str(e)}
    
    def process_all_files(self, directory_path: str) -> Dict:
        """디렉토리 내 모든 엑셀 파일 처리"""
        excel_files = [f for f in os.listdir(directory_path) if f.endswith('.xlsx')]
        total_files = len(excel_files)
        successful_files = 0
        total_speeches = 0
        total_meetings = 0
        
        logger.info(f"총 {total_files}개의 엑셀 파일을 처리합니다.")
        
        for filename in excel_files:
            file_path = os.path.join(directory_path, filename)
            result = self.process_excel_file(file_path)
            
            if result["success"]:
                successful_files += 1
                total_speeches += result.get("speeches_processed", 0)
                total_meetings += 1
            else:
                logger.error(f"❌ {filename}: {result.get('error', '알 수 없는 오류')}")
        
        logger.info(f"처리 완료: {successful_files}/{total_files} 파일 성공")
        logger.info(f"총 회의: {total_meetings}, 총 발언: {total_speeches}")
        
        return {
            "total_files": total_files,
            "successful_files": successful_files,
            "total_meetings": total_meetings,
            "total_speeches": total_speeches
        }
    
    def generate_speech_statistics(self):
        """발언 통계 생성"""
        try:
            # 기존 통계 삭제
            self.cursor.execute('DELETE FROM speech_statistics')
            
            # 발언자별 통계 계산
            self.cursor.execute('''
                SELECT 
                    speaker_name,
                    COUNT(*) as total_speeches,
                    SUM(LENGTH(speech_content)) as total_words,
                    AVG(LENGTH(speech_content)) as avg_speech_length,
                    COUNT(DISTINCT meeting_id) as committee_diversity,
                    MAX(m.date) as last_speech_date
                FROM speeches s
                JOIN meetings m ON s.meeting_id = m.meeting_id
                GROUP BY speaker_name
                ORDER BY total_speeches DESC
            ''')
            
            stats_data = self.cursor.fetchall()
            
            for row in stats_data:
                self.cursor.execute('''
                    INSERT INTO speech_statistics 
                    (politician_name, total_speeches, total_words, avg_speech_length, 
                     committee_diversity, last_speech_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', row)
            
            self.conn.commit()
            logger.info(f"발언 통계 생성 완료: {len(stats_data)}명")
            
        except Exception as e:
            logger.error(f"발언 통계 생성 실패: {e}")
    
    def get_statistics(self) -> Dict:
        """처리 결과 통계 조회"""
        try:
            # 총 회의 수
            self.cursor.execute('SELECT COUNT(*) FROM meetings')
            total_meetings = self.cursor.fetchone()[0]
            
            # 총 발언 수
            self.cursor.execute('SELECT COUNT(*) FROM speeches')
            total_speeches = self.cursor.fetchone()[0]
            
            # 발언자 수
            self.cursor.execute('SELECT COUNT(DISTINCT speaker_name) FROM speeches')
            total_speakers = self.cursor.fetchone()[0]
            
            # 상위 발언자
            self.cursor.execute('''
                SELECT speaker_name, total_speeches, total_words
                FROM speech_statistics
                ORDER BY total_speeches DESC
                LIMIT 10
            ''')
            top_speakers = self.cursor.fetchall()
            
            return {
                "total_meetings": total_meetings,
                "total_speeches": total_speeches,
                "total_speakers": total_speakers,
                "top_speakers": top_speakers
            }
            
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {}
    
    def print_statistics(self):
        """통계 출력"""
        stats = self.get_statistics()
        
        print("\n" + "="*50)
        print("회의록 처리 결과 통계")
        print("="*50)
        print(f"총 회의 수: {stats.get('total_meetings', 0):,}")
        print(f"총 발언 수: {stats.get('total_speeches', 0):,}")
        print(f"총 발언자 수: {stats.get('total_speakers', 0):,}")
        
        print("\n상위 발언자 (발언 수 기준):")
        print("-" * 50)
        for i, (speaker, speeches, words) in enumerate(stats.get('top_speakers', []), 1):
            print(f"{i:2d}. {speaker:15s} | 발언: {speeches:4d}회 | 단어: {words:6d}개")
        
        print("="*50)
    
    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()

def main():
    """메인 실행 함수"""
    # 데이터 디렉토리 경로
    data_dir = "../data/meeting_records"
    
    if not os.path.exists(data_dir):
        logger.error(f"데이터 디렉토리가 존재하지 않습니다: {data_dir}")
        return
    
    # 프로세서 초기화
    processor = ExcelMeetingProcessor()
    
    try:
        # 모든 엑셀 파일 처리
        result = processor.process_all_files(data_dir)
        
        # 발언 통계 생성
        processor.generate_speech_statistics()
        
        # 결과 출력
        processor.print_statistics()
        
    except Exception as e:
        logger.error(f"처리 중 오류 발생: {e}")
    finally:
        processor.close()

if __name__ == "__main__":
    main()

