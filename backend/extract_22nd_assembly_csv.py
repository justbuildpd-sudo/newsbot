#!/usr/bin/env python3
"""
다운로드 폴더 국회의원정보통합.csv에서 22대 국회의원만 추출
"""
import csv
import json
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_22nd_assembly_from_csv():
    """CSV에서 22대 국회의원만 추출"""
    
    csv_file_path = '/Users/hopidaay/Downloads/국회의원정보통합.csv'
    
    try:
        # 다양한 인코딩으로 시도
        encodings = ['utf-8', 'cp949', 'euc-kr', 'utf-8-sig']
        csv_data = None
        
        for encoding in encodings:
            try:
                with open(csv_file_path, 'r', encoding=encoding) as f:
                    csv_reader = csv.DictReader(f)
                    csv_data = list(csv_reader)
                logger.info(f"CSV 파일 로드 성공: {encoding} 인코딩 ({len(csv_data)}행)")
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.warning(f"{encoding} 인코딩 실패: {e}")
                continue
        
        if not csv_data:
            logger.error("CSV 파일을 읽을 수 없음")
            return False
        
        # 헤더 확인
        if csv_data:
            headers = list(csv_data[0].keys())
            logger.info(f"CSV 헤더: {headers[:5]}...")
        
        # 22대 국회의원 필터링
        assembly_22nd = []
        
        for row in csv_data:
            # 22대 국회의원 식별 (당선회수나 기수 정보 확인)
            term_info = ''
            for key, value in row.items():
                if '22' in str(value) or '당선' in str(value) or '기수' in str(value):
                    term_info = str(value)
                    break
            
            # 22대 관련 키워드 확인
            is_22nd = False
            for key, value in row.items():
                if value and ('22대' in str(value) or '제22대' in str(value)):
                    is_22nd = True
                    break
            
            if is_22nd:
                # 의원 정보 추출
                member_info = {}
                for key, value in row.items():
                    if '이름' in key or '성명' in key or 'name' in key.lower():
                        member_info['name'] = str(value).strip() if value else ''
                    elif '정당' in key or 'party' in key.lower():
                        member_info['party'] = str(value).strip() if value else ''
                    elif '지역' in key or 'district' in key.lower():
                        member_info['district'] = str(value).strip() if value else ''
                    elif '위원회' in key or 'committee' in key.lower():
                        member_info['committee'] = str(value).strip() if value else ''
                    elif '사진' in key or 'photo' in key.lower() or 'URL' in key:
                        member_info['photo_url'] = str(value).strip() if value else ''
                
                if member_info.get('name'):
                    assembly_22nd.append(member_info)
        
        logger.info(f"22대 국회의원 추출: {len(assembly_22nd)}명")
        
        # 추출된 데이터 저장
        if assembly_22nd:
            with open('csv_extracted_22nd_assembly.json', 'w', encoding='utf-8') as f:
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
        
        return True
        
    except Exception as e:
        logger.error(f"CSV 추출 실패: {e}")
        return False

if __name__ == "__main__":
    extract_22nd_assembly_from_csv()
