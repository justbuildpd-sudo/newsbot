#!/usr/bin/env python3
"""
연결성 시각화 샘플 생성
실제 네트워크 그래프를 생성하여 보여주기
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np
from connectivity_visualizer import ConnectivityVisualizer
import json

def create_connectivity_sample():
    """연결성 시각화 샘플 생성"""
    visualizer = ConnectivityVisualizer()
    
    # 샘플 데이터 생성
    sample_data = {
        "politician_name": "강대식의원 등 12인",
        "connectivity_score": 50.0,
        "network_data": {
            "nodes": [
                {"id": "강대식의원 등 12인", "name": "강대식의원 등 12인", "type": "center", "level": 0, "size": 25, "color": "#FFD700"},
                {"id": "권영세의원 등 10인", "name": "권영세의원 등 10인", "type": "connection", "level": 1, "size": 18, "color": "#4ECDC4"},
                {"id": "한병도의원 등 10인", "name": "한병도의원 등 10인", "type": "connection", "level": 1, "size": 18, "color": "#45B7D1"},
                {"id": "김선교의원 등 10인", "name": "김선교의원 등 10인", "type": "connection", "level": 1, "size": 18, "color": "#45B7D1"},
                {"id": "김승수의원 등 11인", "name": "김승수의원 등 11인", "type": "connection", "level": 1, "size": 18, "color": "#45B7D1"},
                {"id": "박수현의원 등 8인", "name": "박수현의원 등 8인", "type": "connection", "level": 1, "size": 18, "color": "#96CEB4"},
                {"id": "이재정의원 등 9인", "name": "이재정의원 등 9인", "type": "connection", "level": 2, "size": 15, "color": "#FFEAA7"},
                {"id": "정부수의원 등 7인", "name": "정부수의원 등 7인", "type": "connection", "level": 2, "size": 15, "color": "#DDA0DD"},
                {"id": "최민호의원 등 6인", "name": "최민호의원 등 6인", "type": "connection", "level": 2, "size": 15, "color": "#FF6B6B"},
                {"id": "서지영의원 등 5인", "name": "서지영의원 등 5인", "type": "connection", "level": 3, "size": 12, "color": "#4ECDC4"},
                {"id": "김영배의원 등 4인", "name": "김영배의원 등 4인", "type": "connection", "level": 3, "size": 12, "color": "#45B7D1"}
            ],
            "edges": [
                {"source": "강대식의원 등 12인", "target": "권영세의원 등 10인", "type": "위원회_연결", "strength": 1.0, "width": 8.0, "color": "#4ECDC4", "style": "-"},
                {"source": "강대식의원 등 12인", "target": "한병도의원 등 10인", "type": "정치적_연결", "strength": 1.0, "width": 8.0, "color": "#45B7D1", "style": "-"},
                {"source": "강대식의원 등 12인", "target": "김선교의원 등 10인", "type": "정치적_연결", "strength": 1.0, "width": 8.0, "color": "#45B7D1", "style": "-"},
                {"source": "강대식의원 등 12인", "target": "김승수의원 등 11인", "type": "정치적_연결", "strength": 1.0, "width": 8.0, "color": "#45B7D1", "style": "-"},
                {"source": "강대식의원 등 12인", "target": "박수현의원 등 8인", "type": "지역_연결", "strength": 0.8, "width": 6.0, "color": "#96CEB4", "style": "-."},
                {"source": "권영세의원 등 10인", "target": "이재정의원 등 9인", "type": "정책_연결", "strength": 0.6, "width": 4.0, "color": "#FFEAA7", "style": "-"},
                {"source": "한병도의원 등 10인", "target": "정부수의원 등 7인", "type": "시간_연결", "strength": 0.7, "width": 4.0, "color": "#DDA0DD", "style": "-"},
                {"source": "김선교의원 등 10인", "target": "최민호의원 등 6인", "type": "입법_연결", "strength": 0.5, "width": 2.0, "color": "#FF6B6B", "style": "-"},
                {"source": "이재정의원 등 9인", "target": "서지영의원 등 5인", "type": "위원회_연결", "strength": 0.4, "width": 2.0, "color": "#4ECDC4", "style": ":"},
                {"source": "정부수의원 등 7인", "target": "김영배의원 등 4인", "type": "정치적_연결", "strength": 0.3, "width": 1.0, "color": "#45B7D1", "style": "--"}
            ]
        }
    }
    
    # 네트워크 그래프 생성
    G = nx.Graph()
    
    # 노드 추가
    for node in sample_data["network_data"]["nodes"]:
        G.add_node(node["id"], 
                  name=node["name"], 
                  type=node["type"], 
                  level=node["level"], 
                  size=node["size"], 
                  color=node["color"])
    
    # 엣지 추가
    for edge in sample_data["network_data"]["edges"]:
        G.add_edge(edge["source"], edge["target"], 
                  type=edge["type"], 
                  strength=edge["strength"], 
                  width=edge["width"], 
                  color=edge["color"], 
                  style=edge["style"])
    
    # 그래프 레이아웃 설정
    pos = nx.spring_layout(G, k=3, iterations=50)
    
    # 중심 노드 위치 고정
    center_node = "강대식의원 등 12인"
    pos[center_node] = (0, 0)
    
    # 레벨별 위치 조정
    for node, (x, y) in pos.items():
        node_data = next(n for n in sample_data["network_data"]["nodes"] if n["id"] == node)
        level = node_data["level"]
        
        if level == 1:
            # 1단계: 중심 주변 원형 배치
            angle = list(pos.keys()).index(node) * 2 * np.pi / len([n for n in sample_data["network_data"]["nodes"] if n["level"] == 1])
            pos[node] = (1.5 * np.cos(angle), 1.5 * np.sin(angle))
        elif level == 2:
            # 2단계: 1단계 외곽
            angle = list(pos.keys()).index(node) * 2 * np.pi / len([n for n in sample_data["network_data"]["nodes"] if n["level"] == 2])
            pos[node] = (3.0 * np.cos(angle), 3.0 * np.sin(angle))
        elif level == 3:
            # 3단계: 2단계 외곽
            angle = list(pos.keys()).index(node) * 2 * np.pi / len([n for n in sample_data["network_data"]["nodes"] if n["level"] == 3])
            pos[node] = (4.5 * np.cos(angle), 4.5 * np.sin(angle))
    
    # 그래프 그리기
    plt.figure(figsize=(16, 12))
    plt.title("🔗 정치인 연결성 네트워크 시각화\n강대식의원 등 12인", fontsize=20, fontweight='bold', pad=20)
    
    # 노드 그리기
    for node in sample_data["network_data"]["nodes"]:
        node_id = node["id"]
        if node_id in pos:
            x, y = pos[node_id]
            size = node["size"] * 50  # 크기 조정
            color = node["color"]
            
            if node["type"] == "center":
                # 중심 노드: 별 모양
                plt.scatter(x, y, s=size*2, c=color, marker='*', edgecolors='black', linewidth=2, zorder=3)
                plt.text(x, y+0.3, node["name"], ha='center', va='bottom', fontsize=10, fontweight='bold', 
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
            else:
                # 연결 노드: 원형
                plt.scatter(x, y, s=size, c=color, edgecolors='black', linewidth=1, zorder=2)
                plt.text(x, y-0.4, node["name"], ha='center', va='top', fontsize=8, 
                        bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.7))
    
    # 엣지 그리기
    for edge in sample_data["network_data"]["edges"]:
        source = edge["source"]
        target = edge["target"]
        
        if source in pos and target in pos:
            x1, y1 = pos[source]
            x2, y2 = pos[target]
            
            # 선 스타일 설정
            linestyle = edge["style"]
            if linestyle == "--":
                linestyle = (0, (5, 5))  # 점선
            elif linestyle == ":":
                linestyle = (0, (1, 1))  # 점선
            elif linestyle == "-.":
                linestyle = (0, (3, 5, 1, 5))  # 점쇄선
            
            plt.plot([x1, x2], [y1, y2], 
                    color=edge["color"], 
                    linewidth=edge["width"], 
                    linestyle=linestyle, 
                    alpha=0.7, 
                    zorder=1)
    
    # 범례 생성
    legend_elements = []
    
    # 연결 유형별 색상 범례
    connection_types = [
        ("입법_연결", "#FF6B6B", "공동발의"),
        ("위원회_연결", "#4ECDC4", "같은 위원회"),
        ("정치적_연결", "#45B7D1", "같은 정당"),
        ("지역_연결", "#96CEB4", "같은 지역구"),
        ("정책_연결", "#FFEAA7", "유사 정책"),
        ("시간_연결", "#DDA0DD", "동시기 활동")
    ]
    
    for conn_type, color, meaning in connection_types:
        legend_elements.append(mpatches.Patch(color=color, label=f"{meaning} ({conn_type})"))
    
    # 연결 강도별 굵기 범례
    strength_types = [
        ("매우강함", 8.0, "0.8-1.0"),
        ("강함", 6.0, "0.6-0.8"),
        ("보통", 4.0, "0.4-0.6"),
        ("약함", 2.0, "0.2-0.4"),
        ("매우약함", 1.0, "0.0-0.2")
    ]
    
    for strength, width, range_str in strength_types:
        legend_elements.append(plt.Line2D([0], [0], color='black', linewidth=width, 
                                        label=f"{strength} ({range_str})"))
    
    # 범례 표시
    plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1), 
              fontsize=10, frameon=True, fancybox=True, shadow=True)
    
    # 레벨별 구분선 추가
    for level, radius in [(1, 1.5), (2, 3.0), (3, 4.5)]:
        circle = plt.Circle((0, 0), radius, fill=False, linestyle='--', alpha=0.3, color='gray')
        plt.gca().add_patch(circle)
        plt.text(radius+0.2, 0, f"{level}단계", fontsize=12, fontweight='bold', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.7))
    
    # 축 설정
    plt.axis('equal')
    plt.axis('off')
    plt.tight_layout()
    
    # 그래프 저장
    plt.savefig('connectivity_sample.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.show()
    
    print("✅ 연결성 시각화 샘플이 생성되었습니다!")
    print("📁 파일명: connectivity_sample.png")
    print("🔗 연결성 점수: 50.0점")
    print("📊 총 노드 수: 11개")
    print("🔗 총 연결 수: 10개")
    print()
    print("🎨 시각화 특징:")
    print("  - 중심 노드: 강대식의원 등 12인 (금색 별)")
    print("  - 1단계: 직접 연결 (5개)")
    print("  - 2단계: 간접 연결 (3개)")
    print("  - 3단계: 확장 연결 (2개)")
    print("  - 색상: 연결 유형별 구분")
    print("  - 굵기: 연결 강도별 구분")
    print("  - 선 스타일: 연결 대상별 구분")

if __name__ == "__main__":
    create_connectivity_sample()

