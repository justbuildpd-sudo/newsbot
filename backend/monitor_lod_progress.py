#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOD 데이터 수집 진행 상황 모니터링 스크립트
"""

import time
import json
import os
from datetime import datetime

def monitor_progress():
    """LOD 데이터 수집 진행 상황을 모니터링합니다."""
    
    print("🔄 LOD 데이터 수집 모니터링 시작")
    print("=" * 60)
    
    start_time = datetime.now()
    
    while True:
        try:
            # 로그 파일에서 최신 진행 상황 확인
            if os.path.exists("lod_full_processing.log"):
                with open("lod_full_processing.log", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    
                # 최근 진행 상황 추출
                progress_lines = [line for line in lines[-20:] if "처리 중:" in line]
                success_lines = [line for line in lines if "✅ 성공:" in line]
                failed_lines = [line for line in lines if "❌" in line or "실패" in line]
                
                if progress_lines:
                    latest_progress = progress_lines[-1].strip()
                    # 진행률 추출
                    if "/" in latest_progress:
                        parts = latest_progress.split()
                        for part in parts:
                            if "/" in part and part.replace("/", "").replace("693", "").isdigit():
                                current, total = part.split("/")
                                progress_percent = (int(current) / int(total)) * 100
                                
                                elapsed = datetime.now() - start_time
                                if int(current) > 0:
                                    estimated_total = elapsed * (int(total) / int(current))
                                    remaining = estimated_total - elapsed
                                else:
                                    remaining = "계산 중..."
                                
                                print(f"\r📊 진행률: {progress_percent:.1f}% ({current}/{total}) | "
                                      f"성공: {len(success_lines)}명 | "
                                      f"실패: {len(failed_lines)}명 | "
                                      f"남은시간: {str(remaining).split('.')[0] if remaining != '계산 중...' else remaining}", end="")
                                break
                
                # 완료 확인
                completion_lines = [line for line in lines if "전체 수집:" in line and "성공" in line]
                if completion_lines:
                    print(f"\n\n🎉 데이터 수집 완료!")
                    print(f"⏰ 총 소요시간: {datetime.now() - start_time}")
                    
                    # 결과 파일 확인
                    if os.path.exists("candidate_details_full.json"):
                        with open("candidate_details_full.json", "r", encoding="utf-8") as f:
                            result_data = json.load(f)
                            print(f"✅ 수집 성공: {result_data['success_count']}명")
                            print(f"❌ 수집 실패: {result_data['failure_count']}명")
                            
                            if result_data['candidates']:
                                print(f"\n📋 수집된 데이터 샘플:")
                                for i, candidate in enumerate(result_data['candidates'][:3]):
                                    print(f"  {i+1}. {candidate['name']} - {candidate.get('party', 'N/A')} - "
                                          f"{candidate.get('district', 'N/A')} - {candidate.get('vote_count', 'N/A'):,}표")
                    break
                    
            else:
                print("📋 로그 파일 대기 중...")
            
            time.sleep(5)  # 5초마다 업데이트
            
        except KeyboardInterrupt:
            print(f"\n\n⏹️ 모니터링 중단")
            break
        except Exception as e:
            print(f"\n❌ 모니터링 오류: {e}")
            time.sleep(5)
            continue

if __name__ == "__main__":
    monitor_progress()

