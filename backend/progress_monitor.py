#!/usr/bin/env python3
"""
22대 국회 발의안 수집 진행상황 모니터링 스크립트
5분 단위로 남은 시간과 진행률을 알려줍니다.
"""

import sqlite3
import time
import os
from datetime import datetime, timedelta

def get_progress_info():
    """현재 진행상황 정보를 가져옵니다."""
    try:
        conn = sqlite3.connect('assembly_validated_data.db')
        cursor = conn.cursor()
        
        # 현재 수집된 데이터 확인
        cursor.execute('SELECT COUNT(*) FROM bills_22nd_allbill')
        total_collected = cursor.fetchone()[0]
        
        conn.close()
        
        # 1단계에서의 수집률 (2200001~2201000 범위에서 167건)
        range_1 = 1000
        collected_1 = 167
        success_rate = collected_1 / range_1
        
        # 전체 22대 범위 예상
        total_range = 99999  # 2200001~2299999
        estimated_total = int(total_range * success_rate)
        
        # API 호출 시간 계산 (0.1초 간격)
        api_time_per_call = 0.1  # seconds
        total_api_time = total_range * api_time_per_call
        
        # 현재 진행률
        current_progress = (total_collected / estimated_total) * 100 if estimated_total > 0 else 0
        
        # 남은 시간 계산
        remaining_calls = total_range - (total_collected / success_rate) if success_rate > 0 else total_range
        remaining_time_seconds = remaining_calls * api_time_per_call
        remaining_time_hours = remaining_time_seconds / 3600
        
        return {
            'total_collected': total_collected,
            'estimated_total': estimated_total,
            'current_progress': current_progress,
            'remaining_time_hours': remaining_time_hours,
            'remaining_time_minutes': remaining_time_seconds / 60,
            'success_rate': success_rate
        }
        
    except Exception as e:
        print(f"진행상황 조회 오류: {e}")
        return None

def monitor_progress():
    """5분 단위로 진행상황을 모니터링합니다."""
    print("=" * 60)
    print("22대 국회 발의안 수집 진행상황 모니터링")
    print("=" * 60)
    
    start_time = datetime.now()
    last_collected = 0
    
    while True:
        try:
            progress_info = get_progress_info()
            
            if progress_info is None:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 진행상황 조회 실패")
                time.sleep(300)  # 5분 대기
                continue
            
            current_time = datetime.now()
            elapsed_time = current_time - start_time
            
            # 수집 속도 계산 (최근 5분간)
            if last_collected > 0:
                collection_rate = (progress_info['total_collected'] - last_collected) / 5  # 5분당 수집량
            else:
                collection_rate = 0
            
            print(f"\n[{current_time.strftime('%H:%M:%S')}] 진행상황 업데이트")
            print(f"수집된 발의안: {progress_info['total_collected']:,}건 / {progress_info['estimated_total']:,}건")
            print(f"진행률: {progress_info['current_progress']:.2f}%")
            print(f"수집 성공률: {progress_info['success_rate']:.3f}")
            print(f"경과 시간: {elapsed_time}")
            print(f"남은 예상 시간: {progress_info['remaining_time_hours']:.2f}시간 ({progress_info['remaining_time_minutes']:.1f}분)")
            
            if collection_rate > 0:
                print(f"최근 5분간 수집 속도: {collection_rate:.1f}건/분")
            
            # 완료 조건 확인
            if progress_info['current_progress'] >= 100:
                print("\n🎉 수집 완료!")
                break
            
            last_collected = progress_info['total_collected']
            
            # 5분 대기
            print(f"다음 업데이트까지 5분 대기...")
            time.sleep(300)
            
        except KeyboardInterrupt:
            print("\n모니터링을 중단합니다.")
            break
        except Exception as e:
            print(f"모니터링 오류: {e}")
            time.sleep(60)  # 1분 대기 후 재시도

if __name__ == "__main__":
    monitor_progress()

