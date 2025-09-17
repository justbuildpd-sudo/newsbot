#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
엑셀 회의록 처리 시스템
OneDrive에서 가져온 회의록 엑셀 파일들을 분석하여 발화록 데이터를 추출
"""

import pandas as pd
import sqlite3
import os
import glob
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelMeetingProcessor:
    def __init__(self, excel_dir: str = "../data/meeting_records", db_path: str = "meeting_records_from_excel.db"):
        self.excel_dir = excel_dir
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 회의 정보 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meeting_id TEXT UNIQUE,
                meeting_title TEXT,
                meeting_date TEXT,
                committee_name TEXT,
                session_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 발언자 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS speakers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meeting_id TEXT,
                speaker_name TEXT,
                speaker_title TEXT,
                speech_content TEXT,
                speech_order INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (meeting_id) REFERENCES meetings (meeting_id)
            )
        ''')
        
        # 발언 통계 테이블
        cursor.execute('''
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
        
        conn.commit()
        conn.close()
        logger.info("엑셀 회의록 데이터베이스 초기화 완료")
    
    def extract_politician_name_from_filename(self, filename: str) -> str:
        """파일명에서 정치인 이름 추출"""
        # 파일명 패턴: 통합검색_국회회의록_발언자목록_강득구+(姜得求)_2025-08-16.xlsx
        match = re.search(r'발언자목록_([^+]+)', filename)
        if match:
            return match.group(1).strip()
        return "알수없음"
    
    def process_excel_file(self, file_path: str) -> Dict:
        """개별 엑셀 파일 처리"""
        try:
            # 파일명에서 정치인 이름 추출
            filename = os.path.basename(file_path)
            politician_name = self.extract_politician_name_from_filename(filename)
            
            logger.info(f"처리 중: {politician_name} - {filename}")
            
            # 엑셀 파일 읽기
            df = pd.read_excel(file_path)
            
            # 컬럼명 확인 및 정리
            df.columns = df.columns.astype(str)
            
            # 발언자와 발언 내용 컬럼 찾기
            speaker_col = None
            content_col = None
            date_col = None
            committee_col = None
            
            for col in df.columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in ['발언자', 'speaker', '이름', 'name']):
                    speaker_col = col
                elif any(keyword in col_lower for keyword in ['발언', '내용', 'content', 'speech']):
                    content_col = col
                elif any(keyword in col_lower for keyword in ['날짜', 'date', '일자']):
                    date_col = col
                elif any(keyword in col_lower for keyword in ['위원회', 'committee', '소관']):
                    committee_col = col
            
            if not speaker_col or not content_col:
                logger.warning(f"발언자 또는 발언 내용 컬럼을 찾을 수 없음: {filename}")
                return {"success": False, "reason": "컬럼을 찾을 수 없음"}
            
            # 데이터 정리
            meetings_data = []
            speakers_data = []
            
            for idx, row in df.iterrows():
                speaker_name = str(row[speaker_col]).strip() if pd.notna(row[speaker_col]) else ""
                speech_content = str(row[content_col]).strip() if pd.notna(row[content_col]) else ""
                
                if not speaker_name or not speech_content or speaker_name == "nan" or speech_content == "nan":
                    continue
                
                # 회의 정보 추출
                meeting_date = str(row[date_col]).strip() if date_col and pd.notna(row[date_col]) else ""
                committee_name = str(row[committee_col]).strip() if committee_col and pd.notna(row[committee_col]) else ""
                
                # 회의 ID 생성
                meeting_id = f"{politician_name}_{filename}_{idx}"
                
                # 회의 정보 저장
                meeting_info = {
                    "meeting_id": meeting_id,
                    "meeting_title": f"{politician_name} 발언록",
                    "meeting_date": meeting_date,
                    "committee_name": committee_name,
                    "session_name": ""
                }
                
                # 발언자 정보 저장
                speaker_info = {
                    "meeting_id": meeting_id,
                    "speaker_name": speaker_name,
                    "speaker_title": "",
                    "speech_content": speech_content,
                    "speech_order": idx
                }
                
                meetings_data.append(meeting_info)
                speakers_data.append(speaker_info)
            
            # 데이터베이스에 저장
            self.save_to_database(meetings_data, speakers_data)
            
            return {
                "success": True,
                "politician_name": politician_name,
                "meetings_count": len(meetings_data),
                "speakers_count": len(speakers_data)
            }
            
        except Exception as e:
            logger.error(f"파일 처리 실패 ({file_path}): {e}")
            return {"success": False, "reason": str(e)}
    
    def save_to_database(self, meetings_data: List[Dict], speakers_data: List[Dict]):
        """데이터베이스에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 회의 정보 저장
        for meeting in meetings_data:
            cursor.execute('''
                INSERT OR REPLACE INTO meetings 
                (meeting_id, meeting_title, meeting_date, committee_name, session_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                meeting["meeting_id"],
                meeting["meeting_title"],
                meeting["meeting_date"],
                meeting["committee_name"],
                meeting["session_name"]
            ))
        
        # 발언자 정보 저장
        for speaker in speakers_data:
            cursor.execute('''
                INSERT INTO speakers 
                (meeting_id, speaker_name, speaker_title, speech_content, speech_order)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                speaker["meeting_id"],
                speaker["speaker_name"],
                speaker["speaker_title"],
                speaker["speech_content"],
                speaker["speech_order"]
            ))
        
        conn.commit()
        conn.close()
    
    def process_all_excel_files(self):
        """모든 엑셀 파일 처리"""
        excel_files = glob.glob(os.path.join(self.excel_dir, "*.xlsx"))
        
        if not excel_files:
            logger.error(f"엑셀 파일을 찾을 수 없음: {self.excel_dir}")
            return
        
        logger.info(f"총 {len(excel_files)}개의 엑셀 파일 처리 시작")
        
        success_count = 0
        total_meetings = 0
        total_speakers = 0
        
        for file_path in excel_files:
            result = self.process_excel_file(file_path)
            if result["success"]:
                success_count += 1
                total_meetings += result["meetings_count"]
                total_speakers += result["speakers_count"]
                logger.info(f"✅ {result['politician_name']}: {result['meetings_count']}회의, {result['speakers_count']}발언")
            else:
                logger.error(f"❌ {os.path.basename(file_path)}: {result['reason']}")
        
        logger.info(f"처리 완료: {success_count}/{len(excel_files)} 파일 성공")
        logger.info(f"총 회의: {total_meetings}, 총 발언: {total_speakers}")
        
        # 통계 생성
        self.generate_statistics()
    
    def generate_statistics(self):
        """발언 통계 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 통계 삭제
        cursor.execute('DELETE FROM speech_statistics')
        
        # 정치인별 발언 통계 계산
        cursor.execute('''
            SELECT 
                speaker_name,
                COUNT(*) as total_speeches,
                SUM(LENGTH(speech_content)) as total_words,
                AVG(LENGTH(speech_content)) as avg_speech_length,
                COUNT(DISTINCT m.committee_name) as committee_diversity,
                MAX(m.meeting_date) as last_speech_date
            FROM speakers s
            LEFT JOIN meetings m ON s.meeting_id = m.meeting_id
            WHERE speaker_name IS NOT NULL AND speaker_name != ''
            GROUP BY speaker_name
            ORDER BY total_speeches DESC
        ''')
        
        stats = cursor.fetchall()
        
        for stat in stats:
            cursor.execute('''
                INSERT INTO speech_statistics 
                (politician_name, total_speeches, total_words, avg_speech_length, 
                 committee_diversity, last_speech_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', stat)
        
        conn.commit()
        conn.close()
        
        logger.info(f"발언 통계 생성 완료: {len(stats)}명")
    
    def get_statistics(self) -> Dict:
        """통계 정보 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 전체 통계
        cursor.execute('SELECT COUNT(DISTINCT meeting_id) FROM meetings')
        total_meetings = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM speakers')
        total_speeches = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT speaker_name) FROM speakers')
        unique_speakers = cursor.fetchone()[0]
        
        # 상위 발언자
        cursor.execute('''
            SELECT politician_name, total_speeches, total_words, avg_speech_length
            FROM speech_statistics
            ORDER BY total_speeches DESC
            LIMIT 20
        ''')
        top_speakers = cursor.fetchall()
        
        # 위원회별 통계
        cursor.execute('''
            SELECT committee_name, COUNT(DISTINCT meeting_id) as meeting_count,
                   COUNT(*) as speech_count
            FROM meetings m
            JOIN speakers s ON m.meeting_id = s.meeting_id
            WHERE committee_name IS NOT NULL AND committee_name != ''
            GROUP BY committee_name
            ORDER BY speech_count DESC
            LIMIT 10
        ''')
        committee_stats = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_meetings": total_meetings,
            "total_speeches": total_speeches,
            "unique_speakers": unique_speakers,
            "top_speakers": top_speakers,
            "committee_stats": committee_stats
        }
    
    def print_statistics(self):
        """통계 출력"""
        stats = self.get_statistics()
        
        print("\n=== 엑셀 회의록 처리 결과 ===")
        print(f"총 회의 수: {stats['total_meetings']:,}")
        print(f"총 발언 수: {stats['total_speeches']:,}")
        print(f"고유 발언자 수: {stats['unique_speakers']:,}")
        
        print("\n=== 상위 발언자 (발언 횟수) ===")
        for i, (name, speeches, words, avg_length) in enumerate(stats['top_speakers'][:10]):
            print(f"{i+1:2d}. {name:15s} - {speeches:4d}회, {words:6,}자, 평균 {avg_length:5.0f}자")
        
        print("\n=== 위원회별 발언 통계 ===")
        for committee, meetings, speeches in stats['committee_stats'][:5]:
            print(f"{committee:20s} - {meetings:3d}회의, {speeches:4d}발언")

if __name__ == "__main__":
    processor = ExcelMeetingProcessor()
    processor.process_all_excel_files()
    processor.print_statistics()

