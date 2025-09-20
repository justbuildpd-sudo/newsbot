#!/usr/bin/env python3
"""
중앙선거관리위원회 정책·공약 알리미에서 
8회 전국동시지방선거 당선자 공약 데이터 수집기
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class NECPolicyScraper:
    """중앙선거관리위원회 정책·공약 알리미 스크래퍼"""
    
    def __init__(self):
        self.base_url = "https://policy.nec.go.kr"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # 8회 전국동시지방선거 정보
        self.election_info = {
            "election_name": "제8회 전국동시지방선거",
            "election_date": "2022-06-01",
            "election_code": "20220601"  # 추정 코드
        }
        
        # 수집할 당선자 유형
        self.winner_types = [
            "광역단체장",     # 시도지사
            "기초단체장",     # 시장, 군수, 구청장
            "광역의회의원",   # 시도의회의원
            "기초의회의원",   # 시군구의회의원
            "교육감"         # 시도교육감
        ]
        
        # 수집된 데이터 저장소
        self.collected_data = {
            "election_info": self.election_info,
            "collection_date": datetime.now().isoformat(),
            "winners_data": {},
            "statistics": {
                "total_winners": 0,
                "total_pledges": 0,
                "by_position": {},
                "by_region": {}
            }
        }
    
    def get_election_overview(self) -> Dict[str, Any]:
        """선거 개요 정보 수집"""
        try:
            print("📊 8회 전국동시지방선거 개요 정보 수집 중...")
            
            # 메인 페이지 접근
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 선거 정보 추출 (실제 사이트 구조에 따라 조정 필요)
            election_info = {
                "title": "제8회 전국동시지방선거",
                "date": "2022년 6월 1일",
                "status": "완료",
                "total_positions": self._extract_total_positions(soup),
                "available_data": self._check_available_data(soup)
            }
            
            print(f"✅ 선거 개요 수집 완료: {election_info['title']}")
            return election_info
            
        except Exception as e:
            logger.error(f"선거 개요 수집 실패: {e}")
            return {"error": str(e)}
    
    def get_winners_by_position(self, position_type: str) -> List[Dict[str, Any]]:
        """직책별 당선자 목록 수집"""
        try:
            print(f"🏛️ {position_type} 당선자 목록 수집 중...")
            
            # 직책별 URL 구성 (실제 사이트 구조에 따라 조정)
            position_url = self._build_position_url(position_type)
            
            response = self.session.get(position_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            winners = []
            
            # 당선자 목록 파싱 (실제 HTML 구조에 따라 조정 필요)
            winner_elements = soup.find_all('div', class_='winner-item')  # 예시 클래스명
            
            for element in winner_elements:
                winner_data = self._parse_winner_element(element, position_type)
                if winner_data:
                    winners.append(winner_data)
            
            print(f"✅ {position_type} 당선자 {len(winners)}명 수집 완료")
            return winners
            
        except Exception as e:
            logger.error(f"{position_type} 당선자 수집 실패: {e}")
            return []
    
    def get_winner_pledges(self, winner_id: str, winner_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """개별 당선자의 공약 상세 정보 수집"""
        try:
            print(f"📋 {winner_info['name']} 공약 수집 중...")
            
            # 공약 상세 페이지 URL 구성
            pledge_url = self._build_pledge_url(winner_id)
            
            response = self.session.get(pledge_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            pledges = []
            
            # 공약 목록 파싱
            pledge_elements = soup.find_all('div', class_='pledge-item')  # 예시 클래스명
            
            for element in pledge_elements:
                pledge_data = self._parse_pledge_element(element)
                if pledge_data:
                    pledges.append(pledge_data)
            
            print(f"✅ {winner_info['name']} 공약 {len(pledges)}개 수집 완료")
            return pledges
            
        except Exception as e:
            logger.error(f"{winner_info['name']} 공약 수집 실패: {e}")
            return []
    
    def collect_all_winners_pledges(self) -> Dict[str, Any]:
        """모든 당선자의 공약 수집"""
        try:
            print("🚀 8회 전국동시지방선거 모든 당선자 공약 수집 시작!")
            print("=" * 60)
            
            # 1. 선거 개요 수집
            election_overview = self.get_election_overview()
            self.collected_data["election_overview"] = election_overview
            
            # 2. 직책별 당선자 및 공약 수집
            for position_type in self.winner_types:
                print(f"\n📊 {position_type} 처리 중...")
                
                # 당선자 목록 수집
                winners = self.get_winners_by_position(position_type)
                
                if not winners:
                    print(f"⚠️ {position_type} 당선자 데이터 없음")
                    continue
                
                position_data = {
                    "position_type": position_type,
                    "total_winners": len(winners),
                    "winners": {}
                }
                
                # 각 당선자의 공약 수집
                for i, winner in enumerate(winners, 1):
                    print(f"  📋 {i}/{len(winners)}: {winner['name']} ({winner['region']})")
                    
                    winner_id = winner.get('id', f"{position_type}_{i}")
                    
                    # 공약 수집
                    pledges = self.get_winner_pledges(winner_id, winner)
                    
                    # 데이터 통합
                    winner_full_data = {
                        **winner,
                        "pledges": pledges,
                        "pledge_count": len(pledges),
                        "collection_date": datetime.now().isoformat()
                    }
                    
                    position_data["winners"][winner_id] = winner_full_data
                    
                    # 통계 업데이트
                    self.collected_data["statistics"]["total_winners"] += 1
                    self.collected_data["statistics"]["total_pledges"] += len(pledges)
                    
                    # API 부하 방지를 위한 딜레이
                    time.sleep(0.5)
                
                self.collected_data["winners_data"][position_type] = position_data
                
                # 직책별 통계
                self.collected_data["statistics"]["by_position"][position_type] = {
                    "winners": len(winners),
                    "total_pledges": sum(len(w["pledges"]) for w in position_data["winners"].values())
                }
            
            print("\n" + "=" * 60)
            print("🎉 모든 당선자 공약 수집 완료!")
            print(f"📊 총 당선자: {self.collected_data['statistics']['total_winners']}명")
            print(f"📋 총 공약: {self.collected_data['statistics']['total_pledges']}개")
            
            return self.collected_data
            
        except Exception as e:
            logger.error(f"전체 수집 과정 실패: {e}")
            return {"error": str(e)}
    
    def _extract_total_positions(self, soup: BeautifulSoup) -> Dict[str, int]:
        """전체 선출직 수 추출"""
        # 실제 사이트 구조에 따라 구현
        return {
            "광역단체장": 17,
            "기초단체장": 226,
            "광역의회의원": 789,
            "기초의회의원": 2602,
            "교육감": 17
        }
    
    def _check_available_data(self, soup: BeautifulSoup) -> List[str]:
        """이용 가능한 데이터 유형 확인"""
        # 실제 사이트 구조에 따라 구현
        return ["당선자 정보", "공약 정보", "득표 정보", "선거구 정보"]
    
    def _build_position_url(self, position_type: str) -> str:
        """직책별 URL 구성"""
        position_codes = {
            "광역단체장": "mayor",
            "기초단체장": "district_mayor", 
            "광역의회의원": "metro_council",
            "기초의회의원": "local_council",
            "교육감": "education_chief"
        }
        
        code = position_codes.get(position_type, "unknown")
        return f"{self.base_url}/election/{self.election_info['election_code']}/{code}"
    
    def _build_pledge_url(self, winner_id: str) -> str:
        """공약 상세 페이지 URL 구성"""
        return f"{self.base_url}/pledge/{winner_id}"
    
    def _parse_winner_element(self, element, position_type: str) -> Optional[Dict[str, Any]]:
        """당선자 정보 파싱"""
        try:
            # 실제 HTML 구조에 따라 구현 필요
            name = element.find('span', class_='name')
            party = element.find('span', class_='party')
            region = element.find('span', class_='region')
            
            if not (name and party and region):
                return None
            
            return {
                "name": name.text.strip(),
                "party": party.text.strip(),
                "region": region.text.strip(),
                "position_type": position_type,
                "id": f"{position_type}_{name.text.strip()}_{region.text.strip()}"
            }
        except Exception as e:
            logger.error(f"당선자 정보 파싱 실패: {e}")
            return None
    
    def _parse_pledge_element(self, element) -> Optional[Dict[str, Any]]:
        """공약 정보 파싱"""
        try:
            # 실제 HTML 구조에 따라 구현 필요
            title = element.find('h3', class_='pledge-title')
            content = element.find('div', class_='pledge-content')
            category = element.find('span', class_='pledge-category')
            
            if not (title and content):
                return None
            
            return {
                "title": title.text.strip(),
                "content": content.text.strip(),
                "category": category.text.strip() if category else "기타",
                "parsed_date": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"공약 정보 파싱 실패: {e}")
            return None
    
    def save_collected_data(self, filename: Optional[str] = None) -> str:
        """수집된 데이터를 파일로 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nec_8th_local_election_pledges_{timestamp}.json"
        
        filepath = f"/Users/hopidaay/newsbot-kr/backend/election_data/{filename}"
        
        # 디렉토리 생성
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 데이터 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 수집된 데이터 저장 완료: {filepath}")
        return filepath

def create_sample_data():
    """실제 수집 전 샘플 데이터 생성"""
    sample_data = {
        "election_info": {
            "election_name": "제8회 전국동시지방선거",
            "election_date": "2022-06-01",
            "election_code": "20220601"
        },
        "collection_date": datetime.now().isoformat(),
        "winners_data": {
            "광역단체장": {
                "position_type": "광역단체장",
                "total_winners": 17,
                "winners": {
                    "seoul_mayor": {
                        "name": "오세훈",
                        "party": "국민의힘",
                        "region": "서울특별시",
                        "position_type": "광역단체장",
                        "pledges": [
                            {
                                "title": "서울 청년주택 10만호 공급",
                                "content": "청년층의 주거 부담 완화를 위해 10만호 규모의 청년 전용 주택을 공급하겠습니다.",
                                "category": "주거정책"
                            },
                            {
                                "title": "지하철 심야버스 운행 확대",
                                "content": "시민들의 야간 교통편의를 위해 심야버스 노선을 확대 운영하겠습니다.",
                                "category": "교통정책"
                            }
                        ],
                        "pledge_count": 2
                    }
                }
            }
        },
        "statistics": {
            "total_winners": 1,
            "total_pledges": 2,
            "by_position": {
                "광역단체장": {"winners": 1, "total_pledges": 2}
            }
        }
    }
    
    return sample_data

def main():
    """메인 실행 함수"""
    print("🗳️ 중앙선거관리위원회 8회 지방선거 공약 수집기")
    print("=" * 60)
    
    # 스크래퍼 초기화
    scraper = NECPolicyScraper()
    
    try:
        # 실제 수집 시도
        print("🔍 실제 데이터 수집 시도 중...")
        collected_data = scraper.collect_all_winners_pledges()
        
        if "error" in collected_data:
            print(f"❌ 실제 수집 실패: {collected_data['error']}")
            print("📋 샘플 데이터로 대체합니다.")
            collected_data = create_sample_data()
        
        # 데이터 저장
        saved_file = scraper.save_collected_data()
        
        print("\n📊 수집 결과 요약:")
        print(f"  총 당선자: {collected_data['statistics']['total_winners']}명")
        print(f"  총 공약: {collected_data['statistics']['total_pledges']}개")
        print(f"  저장 파일: {saved_file}")
        
        return collected_data
        
    except Exception as e:
        logger.error(f"메인 실행 실패: {e}")
        print(f"❌ 수집 실패: {e}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
