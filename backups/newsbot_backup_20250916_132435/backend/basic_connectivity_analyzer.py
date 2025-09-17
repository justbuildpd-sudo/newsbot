#!/usr/bin/env python3
"""
기본 연결성 분석 시스템
1단계: 기본 연결 관계 파악
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class BasicConnectivityAnalyzer:
    def __init__(self, db_path: str = "data/legislative_data_standalone.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """기본 연결성 분석을 위한 데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기본 연결성 분석 결과 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS basic_connectivity_analysis (
                politician_name TEXT PRIMARY KEY,
                total_connections INTEGER DEFAULT 0,
                legislative_connections INTEGER DEFAULT 0,
                committee_connections INTEGER DEFAULT 0,
                political_connections INTEGER DEFAULT 0,
                connectivity_score REAL DEFAULT 0.0,
                main_connections TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("기본 연결성 분석 데이터베이스 초기화 완료")
    
    def analyze_basic_connectivity(self, politician_name: str) -> Dict:
        """기본 연결성 분석"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 1. 공동발의자 연결 분석
            legislative_connections = self.find_legislative_connections(politician_name, cursor)
            
            # 2. 위원회 연결 분석
            committee_connections = self.find_committee_connections(politician_name, cursor)
            
            # 3. 정당 연결 분석
            political_connections = self.find_political_connections(politician_name, cursor)
            
            # 4. 연결성 점수 계산
            total_connections = len(legislative_connections) + len(committee_connections) + len(political_connections)
            connectivity_score = min(total_connections * 2, 100)  # 최대 100점
            
            # 5. 주요 연결점 식별 (상위 5개)
            all_connections = legislative_connections + committee_connections + political_connections
            main_connections = sorted(all_connections, key=lambda x: x.get('strength', 0), reverse=True)[:5]
            
            return {
                "politician_name": politician_name,
                "total_connections": total_connections,
                "legislative_connections": len(legislative_connections),
                "committee_connections": len(committee_connections),
                "political_connections": len(political_connections),
                "connectivity_score": connectivity_score,
                "main_connections": main_connections,
                "all_connections": all_connections
            }
            
        except Exception as e:
            logger.error(f"기본 연결성 분석 실패 ({politician_name}): {e}")
            return {}
        finally:
            conn.close()
    
    def find_legislative_connections(self, politician_name: str, cursor) -> List[Dict]:
        """공동발의자 연결 찾기"""
        connections = []
        
        # 해당 의원이 발의한 법안들의 공동발의자 찾기
        cursor.execute('''
            SELECT bill_name, co_proposers, proposal_date, committee_name
            FROM real_assembly_bills_22nd
            WHERE proposer_name = ? AND co_proposers IS NOT NULL AND co_proposers != ''
        ''', (politician_name,))
        
        bills = cursor.fetchall()
        
        for bill_name, co_proposers, proposal_date, committee_name in bills:
            if co_proposers:
                # 공동발의자 파싱 (간단한 형태)
                co_proposer_list = [name.strip() for name in co_proposers.split(',') if name.strip()]
                
                for co_proposer in co_proposer_list:
                    if co_proposer != politician_name:
                        connections.append({
                            "connected_to": co_proposer,
                            "connection_type": "입법_연결",
                            "connection_meaning": f"공동발의: {bill_name[:30]}...",
                            "strength": 0.8,  # 기본 강도
                            "details": {
                                "bill_name": bill_name,
                                "proposal_date": proposal_date,
                                "committee": committee_name
                            }
                        })
        
        return connections
    
    def find_committee_connections(self, politician_name: str, cursor) -> List[Dict]:
        """위원회 연결 찾기"""
        connections = []
        
        # 해당 의원의 주요 위원회 찾기
        cursor.execute('''
            SELECT committee_name, COUNT(*) as bill_count
            FROM real_assembly_bills_22nd
            WHERE proposer_name = ?
            GROUP BY committee_name
            ORDER BY bill_count DESC
            LIMIT 3
        ''', (politician_name,))
        
        main_committees = cursor.fetchall()
        
        for committee_name, bill_count in main_committees:
            if committee_name:
                # 같은 위원회에서 활동하는 다른 의원들 찾기
                cursor.execute('''
                    SELECT DISTINCT proposer_name, COUNT(*) as shared_bills
                    FROM real_assembly_bills_22nd
                    WHERE committee_name = ? AND proposer_name != ?
                    GROUP BY proposer_name
                    ORDER BY shared_bills DESC
                    LIMIT 5
                ''', (committee_name, politician_name))
                
                committee_members = cursor.fetchall()
                
                for member, shared_bills in committee_members:
                    strength = min(shared_bills * 0.2, 1.0)  # 최대 1.0
                    
                    connections.append({
                        "connected_to": member,
                        "connection_type": "위원회_연결",
                        "connection_meaning": f"같은 위원회: {committee_name}",
                        "strength": strength,
                        "details": {
                            "committee": committee_name,
                            "shared_bills": shared_bills
                        }
                    })
        
        return connections
    
    def find_political_connections(self, politician_name: str, cursor) -> List[Dict]:
        """정치적 연결 찾기 (정당)"""
        connections = []
        
        # 해당 의원의 정당 정보 찾기
        cursor.execute('''
            SELECT party
            FROM politician_profiles
            WHERE politician_name = ?
        ''', (politician_name,))
        
        result = cursor.fetchone()
        if not result or not result[0]:
            return connections
        
        party = result[0]
        
        # 같은 정당 의원들 찾기
        cursor.execute('''
            SELECT DISTINCT proposer_name, COUNT(*) as bill_count
            FROM real_assembly_bills_22nd b
            JOIN politician_profiles p ON b.proposer_name = p.politician_name
            WHERE p.party = ? AND b.proposer_name != ?
            GROUP BY proposer_name
            ORDER BY bill_count DESC
            LIMIT 10
        ''', (party, politician_name))
        
        party_members = cursor.fetchall()
        
        for member, bill_count in party_members:
            strength = min(bill_count * 0.1, 1.0)  # 최대 1.0
            
            connections.append({
                "connected_to": member,
                "connection_type": "정치적_연결",
                "connection_meaning": f"같은 정당: {party}",
                "strength": strength,
                "details": {
                    "party": party,
                    "bill_count": bill_count
                }
            })
        
        return connections
    
    def run_basic_analysis(self):
        """기본 연결성 분석 실행"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 분석 결과 삭제
        cursor.execute('DELETE FROM basic_connectivity_analysis')
        
        # 모든 발의자 목록 조회
        cursor.execute('''
            SELECT DISTINCT proposer_name
            FROM real_assembly_bills_22nd
            WHERE proposer_name IS NOT NULL AND proposer_name != ''
            ORDER BY proposer_name
        ''')
        
        politicians = cursor.fetchall()
        logger.info(f"총 {len(politicians)}명 정치인의 기본 연결성 분석 시작")
        
        analyzed_count = 0
        
        for politician in politicians:
            politician_name = politician[0]
            
            try:
                # 기본 연결성 분석
                analysis_result = self.analyze_basic_connectivity(politician_name)
                
                if analysis_result:
                    # 결과 저장
                    cursor.execute('''
                        INSERT INTO basic_connectivity_analysis (
                            politician_name, total_connections, legislative_connections,
                            committee_connections, political_connections, connectivity_score,
                            main_connections
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        politician_name,
                        analysis_result["total_connections"],
                        analysis_result["legislative_connections"],
                        analysis_result["committee_connections"],
                        analysis_result["political_connections"],
                        analysis_result["connectivity_score"],
                        json.dumps(analysis_result["main_connections"], ensure_ascii=False)
                    ))
                    
                    analyzed_count += 1
                    
                    if analyzed_count % 50 == 0:
                        logger.info(f"기본 연결성 분석 완료: {analyzed_count}명")
                
            except Exception as e:
                logger.error(f"기본 연결성 분석 실패 ({politician_name}): {e}")
                continue
        
        conn.commit()
        conn.close()
        logger.info(f"기본 연결성 분석 완료: {analyzed_count}명")
    
    def generate_basic_report(self) -> Dict:
        """기본 연결성 분석 보고서 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 전체 통계
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_analyzed,
                    AVG(connectivity_score) as avg_connectivity,
                    MAX(connectivity_score) as max_connectivity,
                    MIN(connectivity_score) as min_connectivity,
                    AVG(total_connections) as avg_connections
                FROM basic_connectivity_analysis
            ''')
            
            stats = cursor.fetchone()
            
            # 상위 연결성 의원들
            cursor.execute('''
                SELECT politician_name, connectivity_score, total_connections,
                       legislative_connections, committee_connections, political_connections
                FROM basic_connectivity_analysis
                ORDER BY connectivity_score DESC
                LIMIT 10
            ''')
            
            top_connected = []
            for row in cursor.fetchall():
                top_connected.append({
                    "name": row[0],
                    "connectivity_score": round(row[1], 2),
                    "total_connections": row[2],
                    "legislative_connections": row[3],
                    "committee_connections": row[4],
                    "political_connections": row[5]
                })
            
            report = {
                "analysis_date": datetime.now().isoformat(),
                "total_analyzed_politicians": stats[0],
                "average_connectivity_score": round(stats[1], 2),
                "max_connectivity_score": round(stats[2], 2),
                "min_connectivity_score": round(stats[3], 2),
                "average_total_connections": round(stats[4], 2),
                "top_connected_politicians": top_connected
            }
            
            # 보고서 저장
            with open("data/basic_connectivity_report.json", 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info("기본 연결성 분석 보고서 생성 완료")
            return report
            
        except Exception as e:
            logger.error(f"기본 연결성 보고서 생성 실패: {e}")
            return {}
        finally:
            conn.close()

if __name__ == "__main__":
    analyzer = BasicConnectivityAnalyzer()
    analyzer.run_basic_analysis()
    report = analyzer.generate_basic_report()
    
    if report:
        print("✅ 기본 연결성 분석이 성공적으로 완료되었습니다.")
        print(f"📊 분석된 정치인 수: {report.get('total_analyzed_politicians', 0)}명")
        print(f"📈 평균 연결성 점수: {report.get('average_connectivity_score', 0)}점")
    else:
        print("❌ 기본 연결성 분석 중 오류가 발생했습니다.")
