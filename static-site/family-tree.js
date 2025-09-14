// MacFamilyTree 스타일 정치인 인맥관계도 JavaScript
// D3.js를 활용한 인터랙티브 네트워크 시각화

class PoliticalFamilyTree {
    constructor() {
        this.data = null;
        this.currentView = 'network';
        this.filters = {
            party: '',
            committee: '',
            relationship: ''
        };
        this.selectedNode = null;
        this.networkSvg = null;
        this.simulation = null;
        this.tooltip = null;
        
        this.init();
    }

    async init() {
        await this.loadData();
        this.setupEventListeners();
        this.renderNetworkView();
        this.updateStatistics();
        this.generateInsights();
    }

    async loadData() {
        // 실제로는 API에서 데이터를 가져옴
        this.data = {
            nodes: [
                {
                    id: '윤석열',
                    name: '윤석열',
                    party: 'people-power',
                    position: '대통령',
                    committee: 'executive',
                    region: '서울',
                    influence: 10,
                    connections: 15
                },
                {
                    id: '이재명',
                    name: '이재명',
                    party: 'democratic',
                    position: '대표',
                    committee: 'executive',
                    region: '경기',
                    influence: 9,
                    connections: 12
                },
                {
                    id: '안철수',
                    name: '안철수',
                    party: 'people-party',
                    position: '대표',
                    committee: 'executive',
                    region: '서울',
                    influence: 7,
                    connections: 8
                },
                {
                    id: '조국',
                    name: '조국',
                    party: 'democratic',
                    position: '의원',
                    committee: 'justice',
                    region: '서울',
                    influence: 6,
                    connections: 6
                },
                {
                    id: '김기현',
                    name: '김기현',
                    party: 'people-power',
                    position: '의원',
                    committee: 'defense',
                    region: '경기',
                    influence: 5,
                    connections: 5
                },
                {
                    id: '박정훈',
                    name: '박정훈',
                    party: 'democratic',
                    position: '의원',
                    committee: 'budget',
                    region: '서울',
                    influence: 4,
                    connections: 4
                }
            ],
            links: [
                { source: '윤석열', target: '김기현', type: 'party', strength: 8 },
                { source: '이재명', target: '조국', type: 'party', strength: 7 },
                { source: '이재명', target: '박정훈', type: 'party', strength: 6 },
                { source: '윤석열', target: '이재명', type: 'executive', strength: 5 },
                { source: '안철수', target: '조국', type: 'academic', strength: 4 },
                { source: '김기현', target: '박정훈', type: 'committee', strength: 3 },
                { source: '조국', target: '박정훈', type: 'committee', strength: 2 }
            ]
        };
    }

    setupEventListeners() {
        // 검색 기능
        document.getElementById('politicianSearch').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchPolitician();
            }
        });

        // 필터 변경
        document.getElementById('partyFilter').addEventListener('change', () => {
            this.filters.party = document.getElementById('partyFilter').value;
            this.applyFilters();
        });

        document.getElementById('committeeFilter').addEventListener('change', () => {
            this.filters.committee = document.getElementById('committeeFilter').value;
            this.applyFilters();
        });

        document.getElementById('relationshipFilter').addEventListener('change', () => {
            this.filters.relationship = document.getElementById('relationshipFilter').value;
            this.applyFilters();
        });
    }

    renderNetworkView() {
        const container = document.getElementById('networkCanvas');
        const svg = d3.select('#networkSvg');
        
        // 기존 내용 제거
        svg.selectAll('*').remove();
        
        // SVG 설정
        const width = container.clientWidth;
        const height = 600;
        
        svg.attr('width', width).attr('height', height);
        
        // 필터링된 데이터 가져오기
        const filteredData = this.getFilteredData();
        
        // 시뮬레이션 설정
        this.simulation = d3.forceSimulation(filteredData.nodes)
            .force('link', d3.forceLink(filteredData.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(30));
        
        // 연결선 그리기
        const link = svg.append('g')
            .selectAll('line')
            .data(filteredData.links)
            .enter().append('line')
            .attr('class', d => `network-link link-${d.type}`)
            .attr('stroke-width', d => Math.sqrt(d.strength) * 2);
        
        // 노드 그리기
        const node = svg.append('g')
            .selectAll('g')
            .data(filteredData.nodes)
            .enter().append('g')
            .attr('class', d => `network-node node-${d.party}`)
            .call(d3.drag()
                .on('start', this.dragstarted.bind(this))
                .on('drag', this.dragged.bind(this))
                .on('end', this.dragended.bind(this))
            );
        
        // 노드 원
        node.append('circle')
            .attr('r', d => Math.sqrt(d.influence) * 3 + 10);
        
        // 노드 텍스트
        node.append('text')
            .text(d => d.name)
            .attr('dy', 0.35 + 'em');
        
        // 노드 클릭 이벤트
        node.on('click', (event, d) => {
            this.showNodeDetail(d);
        });
        
        // 노드 호버 이벤트
        node.on('mouseover', (event, d) => {
            this.showTooltip(event, d);
        });
        
        node.on('mouseout', () => {
            this.hideTooltip();
        });
        
        // 시뮬레이션 업데이트
        this.simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node
                .attr('transform', d => `translate(${d.x},${d.y})`);
        });
    }

    renderTreeView() {
        const container = document.getElementById('treeContainer');
        container.innerHTML = '';
        
        const filteredData = this.getFilteredData();
        
        // 트리 구조 생성
        const treeData = this.buildTreeStructure(filteredData);
        
        // 트리 렌더링
        this.renderTreeNodes(container, treeData);
    }

    renderTimelineView() {
        const container = document.getElementById('timelineContainer');
        container.innerHTML = '';
        
        // 타임라인 데이터 생성
        const timelineData = this.generateTimelineData();
        
        // 타임라인 렌더링
        this.renderTimeline(container, timelineData);
    }

    buildTreeStructure(data) {
        // 중심 인물을 기준으로 트리 구조 생성
        const centerNode = data.nodes.find(node => node.influence === Math.max(...data.nodes.map(n => n.influence)));
        const tree = { ...centerNode, children: [] };
        
        // 1차 연결 노드들 추가
        const firstDegreeLinks = data.links.filter(link => 
            link.source.id === centerNode.id || link.target.id === centerNode.id
        );
        
        firstDegreeLinks.forEach(link => {
            const connectedNode = link.source.id === centerNode.id ? link.target : link.source;
            tree.children.push({ ...connectedNode, children: [] });
        });
        
        return tree;
    }

    renderTreeNodes(container, node, level = 0) {
        const nodeElement = document.createElement('div');
        nodeElement.className = 'tree-node fade-in-up';
        nodeElement.style.marginLeft = `${level * 2}rem`;
        
        nodeElement.innerHTML = `
            <div class="tree-node-content" onclick="familyTree.showNodeDetail(${JSON.stringify(node).replace(/"/g, '&quot;')})">
                <div class="tree-node-avatar" style="background-color: ${this.getPartyColor(node.party)}">
                    ${node.name.charAt(0)}
                </div>
                <div class="tree-node-name">${node.name}</div>
                <div class="tree-node-party">${this.getPartyLabel(node.party)}</div>
                <div class="tree-node-position">${node.position}</div>
            </div>
        `;
        
        container.appendChild(nodeElement);
        
        // 자식 노드들 렌더링
        if (node.children && node.children.length > 0) {
            node.children.forEach(child => {
                this.renderTreeNodes(container, child, level + 1);
            });
        }
    }

    renderTimeline(container, timelineData) {
        const timelineElement = document.createElement('div');
        timelineElement.className = 'timeline-container';
        
        timelineElement.innerHTML = `
            <div class="timeline-axis"></div>
            ${timelineData.map((year, index) => `
                <div class="timeline-year" style="top: ${index * 100}px">${year.year}</div>
                ${year.events.map(event => `
                    <div class="timeline-event" style="top: ${index * 100 + 20}px" onclick="familyTree.showEventDetail('${event.id}')">
                        <div class="timeline-event-title">${event.title}</div>
                        <div class="timeline-event-description">${event.description}</div>
                    </div>
                `).join('')}
            `).join('')}
        `;
        
        container.appendChild(timelineElement);
    }

    getFilteredData() {
        let filteredNodes = this.data.nodes;
        let filteredLinks = this.data.links;
        
        // 정당 필터
        if (this.filters.party) {
            filteredNodes = filteredNodes.filter(node => node.party === this.filters.party);
            const filteredNodeIds = new Set(filteredNodes.map(node => node.id));
            filteredLinks = filteredLinks.filter(link => 
                filteredNodeIds.has(link.source.id) && filteredNodeIds.has(link.target.id)
            );
        }
        
        // 위원회 필터
        if (this.filters.committee) {
            filteredNodes = filteredNodes.filter(node => node.committee === this.filters.committee);
            const filteredNodeIds = new Set(filteredNodes.map(node => node.id));
            filteredLinks = filteredLinks.filter(link => 
                filteredNodeIds.has(link.source.id) && filteredNodeIds.has(link.target.id)
            );
        }
        
        // 관계 유형 필터
        if (this.filters.relationship) {
            filteredLinks = filteredLinks.filter(link => link.type === this.filters.relationship);
            const connectedNodeIds = new Set();
            filteredLinks.forEach(link => {
                connectedNodeIds.add(link.source.id);
                connectedNodeIds.add(link.target.id);
            });
            filteredNodes = filteredNodes.filter(node => connectedNodeIds.has(node.id));
        }
        
        return { nodes: filteredNodes, links: filteredLinks };
    }

    applyFilters() {
        if (this.currentView === 'network') {
            this.renderNetworkView();
        } else if (this.currentView === 'tree') {
            this.renderTreeView();
        } else if (this.currentView === 'timeline') {
            this.renderTimelineView();
        }
        this.updateStatistics();
    }

    updateStatistics() {
        const filteredData = this.getFilteredData();
        
        document.getElementById('totalPoliticians').textContent = filteredData.nodes.length;
        document.getElementById('totalRelationships').textContent = filteredData.links.length;
        
        const avgConnections = filteredData.nodes.length > 0 
            ? (filteredData.links.length * 2 / filteredData.nodes.length).toFixed(1)
            : 0;
        document.getElementById('avgConnections').textContent = avgConnections;
        
        const maxInfluence = filteredData.nodes.length > 0
            ? Math.max(...filteredData.nodes.map(node => node.influence))
            : 0;
        document.getElementById('maxInfluence').textContent = maxInfluence;
    }

    generateInsights() {
        const insights = [
            {
                title: '가장 영향력 있는 정치인',
                description: '윤석열 대통령이 가장 많은 연결을 가지고 있습니다.'
            },
            {
                title: '정당 내 결속력',
                description: '국민의힘과 더불어민주당이 강한 내부 결속력을 보입니다.'
            },
            {
                title: '위원회 간 협력',
                description: '국방위원회와 예산위원회 간 협력이 활발합니다.'
            }
        ];
        
        const insightsList = document.getElementById('insightsList');
        insightsList.innerHTML = insights.map(insight => `
            <div class="insight-item">
                <h4>${insight.title}</h4>
                <p>${insight.description}</p>
            </div>
        `).join('');
    }

    showNodeDetail(node) {
        const modal = document.getElementById('detailModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        
        modalTitle.textContent = `${node.name} 상세 정보`;
        modalBody.innerHTML = `
            <div class="politician-detail">
                <div class="detail-header">
                    <div class="detail-avatar" style="background-color: ${this.getPartyColor(node.party)}">
                        ${node.name.charAt(0)}
                    </div>
                    <div class="detail-info">
                        <h3>${node.name}</h3>
                        <p class="detail-party">${this.getPartyLabel(node.party)}</p>
                        <p class="detail-position">${node.position}</p>
                    </div>
                </div>
                <div class="detail-stats">
                    <div class="stat-item">
                        <span class="stat-label">영향력</span>
                        <span class="stat-value">${node.influence}/10</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">연결 수</span>
                        <span class="stat-value">${node.connections}개</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">위원회</span>
                        <span class="stat-value">${this.getCommitteeLabel(node.committee)}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">지역</span>
                        <span class="stat-value">${node.region}</span>
                    </div>
                </div>
            </div>
        `;
        
        modal.classList.add('active');
    }

    showTooltip(event, node) {
        if (this.tooltip) {
            this.tooltip.remove();
        }
        
        this.tooltip = d3.select('body')
            .append('div')
            .attr('class', 'tooltip')
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px')
            .html(`
                <strong>${node.name}</strong><br>
                ${this.getPartyLabel(node.party)}<br>
                ${node.position}<br>
                영향력: ${node.influence}/10
            `);
    }

    hideTooltip() {
        if (this.tooltip) {
            this.tooltip.remove();
            this.tooltip = null;
        }
    }

    // 드래그 이벤트 핸들러
    dragstarted(event, d) {
        if (!event.active) this.simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    dragended(event, d) {
        if (!event.active) this.simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    // 유틸리티 함수들
    getPartyColor(party) {
        const colors = {
            'people-power': '#ef4444',
            'democratic': '#3b82f6',
            'people-party': '#eab308',
            'justice': '#10b981'
        };
        return colors[party] || '#6b7280';
    }

    getPartyLabel(party) {
        const labels = {
            'people-power': '국민의힘',
            'democratic': '더불어민주당',
            'people-party': '국민의당',
            'justice': '정의당'
        };
        return labels[party] || party;
    }

    getCommitteeLabel(committee) {
        const labels = {
            'executive': '행정부',
            'defense': '국방위원회',
            'justice': '법무위원회',
            'budget': '예산위원회'
        };
        return labels[committee] || committee;
    }

    generateTimelineData() {
        return [
            {
                year: '2024',
                events: [
                    {
                        id: 'event1',
                        title: '윤석열-이재명 정상회담',
                        description: '대통령과 야당 대표 간 정상회담이 열렸습니다.'
                    },
                    {
                        id: 'event2',
                        title: '국방위원회 개편',
                        description: '국방위원회 구성이 변경되었습니다.'
                    }
                ]
            },
            {
                year: '2023',
                events: [
                    {
                        id: 'event3',
                        title: '정치개혁 논의',
                        description: '정치개혁 관련 논의가 시작되었습니다.'
                    }
                ]
            }
        ];
    }
}

// 전역 함수들
function changeView(view) {
    // 모든 뷰 비활성화
    document.querySelectorAll('.view-container').forEach(container => {
        container.classList.remove('active');
    });
    
    // 모든 버튼 비활성화
    document.querySelectorAll('.control-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // 선택된 뷰 활성화
    document.getElementById(view + 'View').classList.add('active');
    document.getElementById(view + 'View').classList.add('active');
    
    familyTree.currentView = view;
    
    if (view === 'network') {
        familyTree.renderNetworkView();
    } else if (view === 'tree') {
        familyTree.renderTreeView();
    } else if (view === 'timeline') {
        familyTree.renderTimelineView();
    }
}

function searchPolitician() {
    const query = document.getElementById('politicianSearch').value;
    if (!query.trim()) return;
    
    // 검색 로직 구현
    console.log('검색:', query);
    alert(`"${query}" 검색 기능은 구현 예정입니다.`);
}

function applyFilters() {
    familyTree.applyFilters();
}

function resetView() {
    familyTree.renderNetworkView();
}

function exportView() {
    alert('내보내기 기능은 구현 예정입니다.');
}

function expandAll() {
    alert('전체 펼치기 기능은 구현 예정입니다.');
}

function collapseAll() {
    alert('전체 접기 기능은 구현 예정입니다.');
}

function playTimeline() {
    alert('타임라인 재생 기능은 구현 예정입니다.');
}

function pauseTimeline() {
    alert('타임라인 일시정지 기능은 구현 예정입니다.');
}

function closeModal() {
    document.getElementById('detailModal').classList.remove('active');
}

// 전역 인스턴스 생성
let familyTree;

// DOM 로드 완료 후 초기화
document.addEventListener('DOMContentLoaded', function() {
    familyTree = new PoliticalFamilyTree();
});
