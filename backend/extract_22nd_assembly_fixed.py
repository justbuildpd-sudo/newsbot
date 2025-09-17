#!/usr/bin/env python3
"""
국회의원정보통합.csv에서 22대 국회의원만 정확히 추출
"""
import csv
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_22nd_assembly_fixed():
    """CSV에서 22대 국회의원만 정확히 추출"""
    
    csv_file_path = '/Users/hopidaay/Downloads/국회의원정보통합.csv'
    
    try:
        with open(csv_file_path, 'r', encoding='cp949') as f:
            csv_reader = csv.DictReader(f)
            
            assembly_22nd = []
            
            for row in csv_reader:
                # 22대 국회의원 식별
                is_22nd = False
                
                # 당선대수에서 22대 확인
                term_info = row.get('당선대수', '')
                if '제22대' in str(term_info):
                    is_22nd = True
                
                # 약력에서 22대 확인
                career = row.get('약력', '')
                if '제22대' in str(career) or '22대 국회의원' in str(career):
                    is_22nd = True
                
                # 현직의원이면서 최근 데이터인 경우
                status = row.get('-', '')
                if status == '현직의원':
                    # 2024년 이후 데이터면 22대로 간주
                    if '2024' in str(career):
                        is_22nd = True
                
                if is_22nd:
                    # 의원 정보 추출
                    member_info = {
                        'name': row.get('국회의원명', '').strip(),
                        'party': row.get('정당명', '').strip(),
                        'district': row.get('선거구명', '').strip(),
                        'committee': row.get('소속위원회명', '').strip(),
                        'terms': row.get('당선대수', '').strip(),
                        'photo_url': row.get('국회의원사진', '').strip(),
                        'id': row.get('국회의원코드', '').strip(),
                        'phone': row.get('전화번호', '').strip(),
                        'email': row.get('국회의원이메일주소', '').strip()
                    }
                    
                    # 기본 검증
                    if member_info['name'] and len(member_info['name']) > 1:
                        assembly_22nd.append(member_info)
            
            logger.info(f"22대 국회의원 추출: {len(assembly_22nd)}명")
            
            if assembly_22nd:
                # 추출된 데이터 저장
                with open('verified_22nd_assembly_from_csv.json', 'w', encoding='utf-8') as f:
                    json.dump(assembly_22nd, f, ensure_ascii=False, indent=2)
                
                # 샘플 출력
                logger.info("추출된 22대 의원 샘플:")
                for i, member in enumerate(assembly_22nd[:10]):
                    name = member.get('name', '이름없음')
                    party = member.get('party', '정당없음')
                    district = member.get('district', '지역없음')
                    logger.info(f"  {i+1}. {name} ({party}) - {district}")
                
                # 정당별 통계
                party_stats = {}
                for member in assembly_22nd:
                    party = member.get('party', '무소속')
                    party_stats[party] = party_stats.get(party, 0) + 1
                
                logger.info("정당별 분포:")
                for party, count in sorted(party_stats.items(), key=lambda x: x[1], reverse=True):
                    logger.info(f"  {party}: {count}명")
                
                # HTML과 비교
                html_members = [
                    '김승수', '김선교', '권영세', '김정재', '김한규', '김희정', 
                    '김성원', '강유정', '문금주', '김영배', '강대식', '김용만',
                    '고민정', '구자근', '김정호', '곽규택', '김상훈', '김예지',
                    '김선민', '김문수', '남인순', '김영진', '김윤덕', '김미애',
                    '고동진', '김남희', '김주영', '권칠승', '강민국', '나경원',
                    '권성동', '정청래', '강득구', '김민석'
                ]
                
                extracted_names = [m['name'] for m in assembly_22nd]
                found_html_members = [name for name in html_members if name in extracted_names]
                
                logger.info(f"HTML 의원 중 발견: {len(found_html_members)}/{len(html_members)}명")
                if found_html_members:
                    logger.info(f"발견된 HTML 의원: {found_html_members[:10]}")
            else:
                logger.warning("22대 국회의원 데이터를 찾을 수 없음")
        
        return True
        
    except Exception as e:
        logger.error(f"CSV 추출 실패: {e}")
        return False

if __name__ == "__main__":
    extract_22nd_assembly_fixed()
