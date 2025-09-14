// newsbot.kr JavaScript
// 정치 뉴스 분석 플랫폼 프론트엔드 로직

// 전역 변수
let currentPeriod = 'week';
let trendChart = null;

// DOM 로드 완료 후 실행
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 앱 초기화
function initializeApp() {
    // 로딩 오버레이 숨기기
    setTimeout(() => {
        hideLoadingOverlay();
    }, 2000);
    
    // 데이터 로드
    loadNewsData();
    loadHotIssuesData();
    loadPoliticianData();
    loadReportData();
    initializeNetworkVisualization();
    initializeTrendChart();
    
    // 이벤트 리스너 등록
    setupEventListeners();
}

// 이벤트 리스너 설정
function setupEventListeners() {
    // 검색 입력 엔터키 이벤트
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
}

// 로딩 오버레이 숨기기
function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}

// 뉴스 데이터 로드
function loadNewsData() {
    const mockNews = [
        {
            id: 1,
            title: "국회 예산안 심의 시작, 여야 대립 심화",
            description: "2024년 예산안 심의가 시작되면서 여야 간 대립이 심화되고 있다...",
            pubDate: "2024-01-15T10:30:00Z",
            category: "politics"
        },
        {
            id: 2,
            title: "정부, 새로운 경제정책 발표",
            description: "정부가 내년 경제성장을 위한 새로운 정책을 발표했다...",
            pubDate: "2024-01-15T09:15:00Z",
            category: "economy"
        },
        {
            id: 3,
            title: "국방위원회, 안보정책 논의",
            description: "국방위원회에서 최근 안보 상황에 대한 논의가 진행되었다...",
            pubDate: "2024-01-15T08:45:00Z",
            category: "defense"
        },
        {
            id: 4,
            title: "교육정책 개혁안 제출",
            description: "교육부가 새로운 교육정책 개혁안을 국회에 제출했다...",
            pubDate: "2024-01-15T07:20:00Z",
            category: "education"
        },
        {
            id: 5,
            title: "환경정책 관련 법안 통과",
            description: "환경정책 관련 법안이 국회를 통과했다...",
            pubDate: "2024-01-15T06:30:00Z",
            category: "environment"
        }
    ];
    
    renderNewsList(mockNews);
}

// 뉴스 목록 렌더링
function renderNewsList(news) {
    const newsList = document.getElementById('newsList');
    if (!newsList) return;
    
    newsList.innerHTML = news.map(item => `
        <div class="news-item fade-in">
            <div class="news-header">
                <h3 class="news-title">${item.title}</h3>
                <span class="news-category ${item.category}">${getCategoryLabel(item.category)}</span>
            </div>
            <p class="news-description">${item.description}</p>
            <div class="news-meta">
                <span>${formatDate(item.pubDate)}</span>
                <a href="#" class="news-link" onclick="showNewsDetail(${item.id})">자세히 보기 →</a>
            </div>
        </div>
    `).join('');
}

// 핫이슈 데이터 로드
function loadHotIssuesData() {
    const mockHotIssues = [
        { keyword: "예산안", count: 1250, trend: "up", change: "+15%" },
        { keyword: "국방정책", count: 980, trend: "up", change: "+8%" },
        { keyword: "교육개혁", count: 850, trend: "down", change: "-3%" },
        { keyword: "환경정책", count: 720, trend: "up", change: "+12%" },
        { keyword: "경제정책", count: 680, trend: "stable", change: "0%" },
        { keyword: "복지정책", count: 590, trend: "up", change: "+5%" },
        { keyword: "외교정책", count: 520, trend: "down", change: "-2%" },
        { keyword: "법무정책", count: 480, trend: "up", change: "+7%" }
    ];
    
    renderHotIssuesList(mockHotIssues);
}

// 핫이슈 목록 렌더링
function renderHotIssuesList(issues) {
    const hotIssuesList = document.getElementById('hotIssuesList');
    if (!hotIssuesList) return;
    
    hotIssuesList.innerHTML = issues.map((issue, index) => `
        <div class="hot-issue-item fade-in" onclick="showHotIssueDetail('${issue.keyword}')">
            <div class="hot-issue-info">
                <span class="hot-issue-rank">${index + 1}</span>
                <div class="hot-issue-details">
                    <h3>${issue.keyword}</h3>
                    <p>${issue.count.toLocaleString()}회 언급</p>
                </div>
            </div>
            <div class="hot-issue-trend">
                ${getTrendIcon(issue.trend)}
                <span class="trend-value ${issue.trend}">${issue.change}</span>
            </div>
        </div>
    `).join('');
}

// 정치인 데이터 로드
function loadPoliticianData() {
    const mockPoliticians = [
        {
            id: 1,
            name: "윤석열",
            party: "people-power",
            position: "대통령",
            mentionCount: 1250,
            sentiment: 0.3,
            recentStatement: "경제 회복을 위한 정책을 추진하겠습니다."
        },
        {
            id: 2,
            name: "이재명",
            party: "democratic",
            position: "대표",
            mentionCount: 980,
            sentiment: -0.1,
            recentStatement: "정부의 정책에 대해 우려를 표명합니다."
        },
        {
            id: 3,
            name: "안철수",
            party: "people-party",
            position: "대표",
            mentionCount: 720,
            sentiment: 0.1,
            recentStatement: "새로운 정치를 제안합니다."
        },
        {
            id: 4,
            name: "조국",
            party: "democratic",
            position: "의원",
            mentionCount: 650,
            sentiment: -0.2,
            recentStatement: "법무정책 개혁이 필요합니다."
        }
    ];
    
    renderPoliticianList(mockPoliticians);
}

// 정치인 목록 렌더링
function renderPoliticianList(politicians) {
    const politicianList = document.getElementById('politicianList');
    if (!politicianList) return;
    
    politicianList.innerHTML = politicians.map(politician => `
        <div class="politician-item fade-in" onclick="showPoliticianDetail(${politician.id})">
            <div class="politician-avatar">${politician.name.charAt(0)}</div>
            <div class="politician-info">
                <div class="politician-name">${politician.name}</div>
                <span class="politician-party ${politician.party}">${getPartyLabel(politician.party)}</span>
                <div class="politician-position">${politician.position}</div>
                <p class="politician-statement">"${politician.recentStatement}"</p>
                <div class="politician-stats">
                    <span>언급 ${politician.mentionCount.toLocaleString()}회</span>
                    <span class="sentiment-${getSentimentClass(politician.sentiment)}">${getSentimentLabel(politician.sentiment)}</span>
                    <a href="#" class="politician-link" onclick="event.stopPropagation(); showPoliticianDetail(${politician.id})">자세히 →</a>
                </div>
            </div>
        </div>
    `).join('');
}

// 리포트 데이터 로드
function loadReportData() {
    const mockReport = {
        insights: [
            {
                title: '예산안 논의가 핫이슈로 부상',
                description: '국회 예산안 심의와 관련된 언급이 15% 증가했습니다.',
                impact: 'high',
                trend: 'up'
            },
            {
                title: '국방정책 관련 긍정적 반응 증가',
                description: '국방정책에 대한 긍정적 언급이 전주 대비 8% 증가했습니다.',
                impact: 'medium',
                trend: 'up'
            },
            {
                title: '교육개혁 논의 감소',
                description: '교육개혁 관련 언급이 전주 대비 3% 감소했습니다.',
                impact: 'low',
                trend: 'down'
            }
        ],
        predictions: [
            '예산안 논의가 다음 주까지 지속될 것으로 예상됩니다.',
            '국방정책 관련 긍정적 여론이 계속될 가능성이 높습니다.',
            '교육개혁 이슈는 새로운 정책 발표 시 다시 부상할 것으로 예상됩니다.'
        ],
        statistics: {
            totalNews: 1250,
            totalMentions: 3450,
            avgSentiment: 0.2,
            topKeyword: '예산안',
            topPolitician: '윤석열'
        }
    };
    
    renderReportContent(mockReport);
}

// 리포트 내용 렌더링
function renderReportContent(report) {
    const reportContent = document.getElementById('reportContent');
    if (!reportContent) return;
    
    reportContent.innerHTML = `
        <div class="report-section">
            <h3>주요 인사이트</h3>
            ${report.insights.map(insight => `
                <div class="insight-item">
                    <div class="insight-content">
                        <h4>${insight.title}</h4>
                        <p>${insight.description}</p>
                    </div>
                    <div class="insight-meta">
                        ${getTrendIcon(insight.trend)}
                        <span class="insight-impact ${insight.impact}">${getImpactLabel(insight.impact)}</span>
                    </div>
                </div>
            `).join('')}
        </div>
        
        <div class="report-section">
            <h3>예측 분석</h3>
            <ul class="prediction-list">
                ${report.predictions.map(prediction => `
                    <li class="prediction-item">
                        <div class="prediction-bullet"></div>
                        <span>${prediction}</span>
                    </li>
                `).join('')}
            </ul>
        </div>
        
        <div class="report-section">
            <h3>통계 요약</h3>
            <div class="report-stats">
                <div class="stat-item">
                    <span class="stat-label">총 뉴스</span>
                    <span class="stat-value">${report.statistics.totalNews.toLocaleString()}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">총 언급</span>
                    <span class="stat-value">${report.statistics.totalMentions.toLocaleString()}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">평균 감정</span>
                    <span class="stat-value positive">${report.statistics.avgSentiment.toFixed(2)}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">핫 키워드</span>
                    <span class="stat-value">${report.statistics.topKeyword}</span>
                </div>
            </div>
        </div>
    `;
}

// 네트워크 시각화 초기화
function initializeNetworkVisualization() {
    const networkContainer = document.getElementById('networkVisualization');
    if (!networkContainer) return;
    
    const nodes = [
        { id: '윤석열', type: 'politician', x: 50, y: 50 },
        { id: '이재명', type: 'politician', x: 150, y: 50 },
        { id: '안철수', type: 'politician', x: 250, y: 50 },
        { id: '예산안', type: 'issue', x: 100, y: 150 },
        { id: '국방정책', type: 'issue', x: 200, y: 150 },
        { id: '교육개혁', type: 'issue', x: 300, y: 150 }
    ];
    
    networkContainer.innerHTML = nodes.map(node => `
        <div class="network-node ${node.type}" 
             style="left: ${node.x}px; top: ${node.y}px;"
             onclick="showNetworkNodeDetail('${node.id}')">
            ${node.id.charAt(0)}
        </div>
    `).join('');
}

// 트렌드 차트 초기화
function initializeTrendChart() {
    const ctx = document.getElementById('trendChart');
    if (!ctx) return;
    
    const data = {
        labels: ['1/8', '1/9', '1/10', '1/11', '1/12', '1/13', '1/14'],
        datasets: [{
            label: '뉴스 언급 수',
            data: [45, 52, 48, 61, 58, 55, 62],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4,
            fill: true
        }]
    };
    
    const config = {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        color: '#374151'
                    },
                    ticks: {
                        color: '#9ca3af'
                    }
                },
                y: {
                    grid: {
                        color: '#374151'
                    },
                    ticks: {
                        color: '#9ca3af'
                    }
                }
            }
        }
    };
    
    trendChart = new Chart(ctx, config);
}

// 기간 변경
function changePeriod(period) {
    currentPeriod = period;
    
    // 버튼 상태 업데이트
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // 차트 데이터 업데이트
    if (trendChart) {
        const newData = period === 'week' 
            ? [45, 52, 48, 61, 58, 55, 62]
            : [42, 45, 62];
        
        trendChart.data.datasets[0].data = newData;
        trendChart.update();
    }
}

// 검색 실행
function performSearch() {
    const query = document.getElementById('searchInput').value;
    if (!query.trim()) return;
    
    // 검색 로직 구현 (실제로는 API 호출)
    console.log('검색 쿼리:', query);
    alert(`"${query}" 검색 기능은 구현 예정입니다.`);
}

// 유틸리티 함수들
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getCategoryLabel(category) {
    const labels = {
        'politics': '정치',
        'economy': '경제',
        'defense': '국방',
        'education': '교육',
        'environment': '환경'
    };
    return labels[category] || '기타';
}

function getPartyLabel(party) {
    const labels = {
        'people-power': '국민의힘',
        'democratic': '더불어민주당',
        'people-party': '국민의당'
    };
    return labels[party] || party;
}

function getSentimentLabel(sentiment) {
    if (sentiment > 0.2) return '긍정';
    if (sentiment < -0.2) return '부정';
    return '중립';
}

function getSentimentClass(sentiment) {
    if (sentiment > 0.2) return 'positive';
    if (sentiment < -0.2) return 'negative';
    return 'neutral';
}

function getImpactLabel(impact) {
    const labels = {
        'high': '높음',
        'medium': '보통',
        'low': '낮음'
    };
    return labels[impact] || impact;
}

function getTrendIcon(trend) {
    const icons = {
        'up': '<svg class="trend-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 17l9.2-9.2M17 17V7H7"></path></svg>',
        'down': '<svg class="trend-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 7l-9.2 9.2M7 7v10h10"></path></svg>',
        'stable': '<svg class="trend-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path></svg>'
    };
    return icons[trend] || icons['stable'];
}

// 위젯 버튼 이벤트 핸들러들
function showAllNews() {
    alert('모든 뉴스 보기 기능은 구현 예정입니다.');
}

function showHotIssues() {
    alert('핫이슈 상세 분석 기능은 구현 예정입니다.');
}

function showTrendAnalysis() {
    alert('트렌드 상세 분석 기능은 구현 예정입니다.');
}

function showAllPoliticians() {
    alert('모든 정치인 보기 기능은 구현 예정입니다.');
}

function showNetworkAnalysis() {
    alert('네트워크 확대 보기 기능은 구현 예정입니다.');
}

function downloadReport() {
    alert('PDF 다운로드 기능은 구현 예정입니다.');
}

function showDetailedReport() {
    alert('상세 리포트 보기 기능은 구현 예정입니다.');
}

// 상세 보기 이벤트 핸들러들
function showNewsDetail(newsId) {
    alert(`뉴스 ${newsId} 상세 보기 기능은 구현 예정입니다.`);
}

function showHotIssueDetail(keyword) {
    alert(`"${keyword}" 핫이슈 상세 보기 기능은 구현 예정입니다.`);
}

function showPoliticianDetail(politicianId) {
    alert(`정치인 ${politicianId} 상세 보기 기능은 구현 예정입니다.`);
}

function showNetworkNodeDetail(nodeId) {
    alert(`"${nodeId}" 네트워크 노드 상세 보기 기능은 구현 예정입니다.`);
}
