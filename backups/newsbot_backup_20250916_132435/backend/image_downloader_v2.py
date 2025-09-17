#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
국회의원 이미지 다운로드 v2 - 다양한 소스 시도
"""

import requests
import json
import os
import time
from urllib.parse import urlparse
from pathlib import Path
import hashlib

class PoliticianImageDownloaderV2:
    def __init__(self):
        self.base_url = "http://apis.data.go.kr/9710000/NationalAssemblyInfoService"
        self.api_key = "RoSdWk52fty0NNpB6SxxmgXiC2vEXOpOSw1bHPcRxuBEmcXi91fT52waWOMDo67trsxWJcm59pVGNYExnLOa8A=="
        self.images_dir = Path("images/politicians")
        self.data_file = "politicians_data.json"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # 다양한 이미지 URL 패턴 시도
        self.image_url_patterns = [
            "https://www.assembly.go.kr/photo/{}.jpg",
            "http://www.assembly.go.kr/photo/{}.jpg",
            "https://assembly.go.kr/photo/{}.jpg",
            "http://assembly.go.kr/photo/{}.jpg",
            "https://www.assembly.go.kr/static/photo/{}.jpg",
            "http://www.assembly.go.kr/static/photo/{}.jpg",
            "https://www.assembly.go.kr/images/photo/{}.jpg",
            "http://www.assembly.go.kr/images/photo/{}.jpg"
        ]
        
    def _make_request(self, endpoint: str, params: dict) -> dict:
        """API 요청 실행"""
        try:
            url = f"{self.base_url}/{endpoint}"
            params['serviceKey'] = self.api_key
            
            session = requests.Session()
            session.verify = False
            
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            response = session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            items = []
            for item in root.findall('.//item'):
                item_data = {}
                for child in item:
                    item_data[child.tag] = child.text
                items.append(item_data)
            
            return {'items': items}
            
        except Exception as e:
            print(f"❌ API 요청 오류 ({endpoint}): {e}")
            return None
    
    def get_all_politicians(self):
        """모든 국회의원 정보 가져오기"""
        print("📋 국회의원 정보 수집 중...")
        
        params = {
            'numOfRows': 1000,
            'pageNo': 1
        }
        
        result = self._make_request('getMemberCurrStateList', params)
        if result and result.get('items'):
            print(f"✅ {len(result['items'])}명의 국회의원 정보 수집 완료")
            return result['items']
        else:
            print("❌ 국회의원 정보 수집 실패")
            return []
    
    def try_download_image(self, image_url: str, filename: str) -> bool:
        """이미지 다운로드 시도"""
        try:
            if not image_url or not filename:
                return False
                
            response = requests.get(image_url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Content-Type 확인
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                print(f"⚠️  이미지가 아닌 파일: {filename} (Content-Type: {content_type})")
                return False
            
            file_path = self.images_dir / filename
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 파일 크기 확인
            if file_path.stat().st_size < 1000:  # 1KB 미만이면 실패로 간주
                file_path.unlink()  # 파일 삭제
                return False
            
            print(f"✅ 이미지 다운로드 완료: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ 이미지 다운로드 실패 ({filename}): {e}")
            return False
    
    def download_image_with_patterns(self, member_number: str, name: str) -> tuple:
        """다양한 URL 패턴으로 이미지 다운로드 시도"""
        safe_name = name.replace(' ', '_').replace('/', '_')
        filename = f"{safe_name}_{member_number}.jpg"
        
        for pattern in self.image_url_patterns:
            image_url = pattern.format(member_number)
            print(f"🔄 시도 중: {image_url}")
            
            if self.try_download_image(image_url, filename):
                return image_url, filename
        
        return None, filename
    
    def process_politicians(self):
        """국회의원 데이터 처리 및 이미지 다운로드"""
        politicians = self.get_all_politicians()
        
        if not politicians:
            print("❌ 처리할 국회의원 데이터가 없습니다.")
            return
        
        processed_data = []
        success_count = 0
        error_count = 0
        
        print(f"\n🖼️  {len(politicians)}명의 국회의원 이미지 다운로드 시작...")
        
        for i, politician in enumerate(politicians, 1):
            try:
                name = politician.get('empNm', '')
                member_number = politician.get('num', '')
                
                if not name:
                    print(f"⚠️  [{i}/{len(politicians)}] 이름이 없는 의원 건너뜀")
                    error_count += 1
                    continue
                
                # 다양한 패턴으로 이미지 다운로드 시도
                image_url, filename = self.download_image_with_patterns(member_number, name)
                image_downloaded = image_url is not None
                
                # 처리된 데이터 저장
                processed_politician = {
                    'id': member_number,
                    'dept_code': politician.get('deptCd', ''),
                    'name': name,
                    'name_hanja': politician.get('hjNm', ''),
                    'name_english': politician.get('engNm', ''),
                    'district': politician.get('origNm', ''),
                    'terms': politician.get('reeleGbnNm', ''),
                    'office': politician.get('secretNm', ''),
                    'phone': politician.get('telno', ''),
                    'email': politician.get('email', ''),
                    'website': politician.get('homepage', ''),
                    'member_number': member_number,
                    'image_url': image_url,
                    'local_image_path': f"images/politicians/{filename}" if image_downloaded else None,
                    'image_downloaded': image_downloaded,
                    'processed_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                processed_data.append(processed_politician)
                success_count += 1
                
                print(f"✅ [{i}/{len(politicians)}] {name} - {'이미지 다운로드 완료' if image_downloaded else '이미지 없음'}")
                
                # API 부하 방지를 위한 딜레이
                time.sleep(0.2)
                
            except Exception as e:
                print(f"❌ [{i}/{len(politicians)}] {name} 처리 실패: {e}")
                error_count += 1
                continue
        
        # 데이터 저장
        self.save_data(processed_data)
        
        print(f"\n📊 처리 완료:")
        print(f"   - 성공: {success_count}명")
        print(f"   - 실패: {error_count}명")
        print(f"   - 총 처리: {len(processed_data)}명")
        print(f"   - 데이터 파일: {self.data_file}")
        print(f"   - 이미지 폴더: {self.images_dir}")
    
    def save_data(self, data):
        """데이터를 JSON 파일로 저장"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 데이터 저장 완료: {self.data_file}")
        except Exception as e:
            print(f"❌ 데이터 저장 실패: {e}")
    
    def load_data(self):
        """저장된 데이터 로드"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return []

if __name__ == "__main__":
    downloader = PoliticianImageDownloaderV2()
    downloader.process_politicians()
