// newsbot.kr JavaScript
// 정치 뉴스 분석 플랫폼 프론트엔드 로직

// 전역 변수
let currentPeriod = 'week';
let trendChart = null;
let newsData = []; // 뉴스 데이터를 전역 변수로 저장

// API 설정
const API_BASE_URL = window.location.hostname === 'newsbot.kr' 
    ? 'https://newsbot-backend-6j3p.onrender.com'  // 프로덕션 (Render)
    : 'http://localhost:8001';  // 로컬 개발

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
    
    // 언급 분석 실행
    setTimeout(() => {
        analyzePoliticianMentions();
    }, 3000);
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

// 뉴스 데이터 로드 (API에서 가져오기)
async function loadNewsData() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/news`);
        const result = await response.json();
        
        if (result.success) {
            const news = result.data.map((item, index) => ({
                id: index + 1,
                title: item.title,
                description: item.description || "상세 내용을 확인하려면 클릭하세요.",
                pubDate: item.pubDate,
                category: "politics",
                link: item.link
            }));
            newsData = news; // 전역 변수에 저장
            renderNewsList(news);
        } else {
            console.error('뉴스 데이터 가져오기 실패:', result);
            loadMockNewsData();
        }
    } catch (error) {
        console.error('API 연결 오류:', error);
        loadMockNewsData();
    }
}

// 모의 뉴스 데이터 (API 연결 실패시 사용)
function loadMockNewsData() {
    const mockNews = [
        {
            id: 1,
            title: "국회 예산안 심의 시작, 여야 대립 심화",
            description: "2024년 예산안 심의가 시작되면서 여야 간 대립이 심화되고 있다...",
            pubDate: "2024-01-15T10:30:00Z",
            category: "politics",
            link: "https://example.com/news1"
        },
        {
            id: 2,
            title: "정부, 새로운 경제정책 발표",
            description: "정부가 내년 경제성장을 위한 새로운 정책을 발표했다...",
            pubDate: "2024-01-15T09:15:00Z",
            category: "economy",
            link: "https://example.com/news2"
        },
        {
            id: 3,
            title: "국방위원회, 안보정책 논의",
            description: "국방위원회에서 최근 안보 상황에 대한 논의가 진행되었다...",
            pubDate: "2024-01-15T08:45:00Z",
            category: "defense",
            link: "https://example.com/news3"
        },
        {
            id: 4,
            title: "교육정책 개혁안 제출",
            description: "교육부가 새로운 교육정책 개혁안을 국회에 제출했다...",
            pubDate: "2024-01-15T07:20:00Z",
            category: "education",
            link: "https://example.com/news4"
        },
        {
            id: 5,
            title: "환경정책 관련 법안 통과",
            description: "환경정책 관련 법안이 국회를 통과했다...",
            pubDate: "2024-01-15T06:30:00Z",
            category: "environment",
            link: "https://example.com/news5"
        }
    ];
    
    newsData = mockNews; // 전역 변수에 저장
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

// 정치인 데이터 로드 (뉴스 언급 수 기준 랭킹)
async function loadPoliticianData() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/politicians/ranking?limit=8`);
        const result = await response.json();
        
        if (result.success && result.data.length > 0) {
            const politicians = result.data.map((politician, index) => ({
                id: politician.id,
                name: politician.name,
                party: getPartyCode(politician.party),
                position: politician.committee || "위원회 정보 없음",
                mentionCount: politician.mention_count || 0,
                sentiment: Math.random() * 0.4 - 0.2, // -0.2 ~ 0.2
                recentStatement: "최근 언급된 뉴스가 있습니다.",
                district: politician.district || "지역 정보 없음",
                terms: "재선",
                orientation: "중도",
                keyIssues: ["환경", "노동"],
                ranking: index + 1,
                influenceScore: politician.influence_score || 0
            }));
            
            renderPoliticianList(politicians);
        } else {
            console.log('뉴스에서 언급된 정치인이 없습니다. 기본 데이터를 로드합니다.');
            loadFeaturedPoliticians();
        }
    } catch (error) {
        console.error('정치인 랭킹 로드 오류:', error);
        loadFeaturedPoliticians();
    }
}

// 주요 정치인 데이터 로드 (백업용)
async function loadFeaturedPoliticians() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/politicians`);
        const result = await response.json();
        
        if (result.success) {
            const politicians = result.data.map((politician, index) => ({
                id: politician.id,
                name: politician.name,
                party: getPartyCode(politician.party),
                position: politician.committee || "위원회 정보 없음",
                mentionCount: Math.floor(Math.random() * 100) + 10, // 낮은 언급 수
                sentiment: Math.random() * 0.4 - 0.2,
                recentStatement: "최근 언급된 뉴스가 있습니다.",
                district: politician.district || "지역 정보 없음",
                terms: "재선",
                orientation: "중도",
                keyIssues: ["환경", "노동"],
                ranking: index + 1,
                influenceScore: 0
            }));
            
            renderPoliticianList(politicians);
        } else {
            loadMockPoliticianData();
        }
    } catch (error) {
        console.error('주요 정치인 로드 오류:', error);
        loadMockPoliticianData();
    }
}

// 정당 코드 변환
function getPartyCode(party) {
    const partyMap = {
        '더불어민주당': 'democratic',
        '국민의힘': 'people-power',
        '조국혁신당': 'innovation',
        '개혁신당': 'reform',
        '무소속': 'independent'
    };
    return partyMap[party] || 'independent';
}

// 정당 라벨 변환
function getPartyLabel(partyCode) {
    const partyLabels = {
        'democratic': '더불어민주당',
        'people-power': '국민의힘',
        'innovation': '조국혁신당',
        'reform': '개혁신당',
        'independent': '무소속'
    };
    return partyLabels[partyCode] || partyCode;
}

// 모의 정치인 데이터 (백업용)
function loadMockPoliticianData() {
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
            <div class="politician-ranking">
                ${politician.ranking > 0 ? `#${politician.ranking}` : ''}
            </div>
            <div class="politician-avatar">${politician.name.charAt(0)}</div>
            <div class="politician-info">
                <div class="politician-name">
                    ${politician.name}
                    ${politician.ranking > 0 ? `<span class="ranking-badge">${politician.ranking}위</span>` : ''}
                </div>
                <span class="politician-party ${politician.party}">${getPartyLabel(politician.party)}</span>
                <div class="politician-position">${politician.position}</div>
                <p class="politician-statement">"${politician.recentStatement}"</p>
                <div class="politician-stats">
                    <span class="mention-count">언급 ${politician.mentionCount.toLocaleString()}회</span>
                    ${politician.influenceScore > 0 ? `<span class="influence-score">영향력 ${politician.influenceScore}</span>` : ''}
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
    // 뉴스 데이터에서 해당 ID의 뉴스 찾기
    const newsItem = newsData.find(item => item.id === newsId);
    if (newsItem) {
        showNewsModal(newsItem);
    } else {
        showNotification('뉴스 정보를 찾을 수 없습니다.', 'error');
    }
}

// 뉴스 모달 표시
function showNewsModal(newsItem) {
    // 로딩 모달 먼저 표시
    showLoadingModal(newsItem);
    
    // 기사 전문 가져오기
    loadNewsContent(newsItem);
}

// 로딩 모달 표시
function showLoadingModal(newsItem) {
    const modalHTML = `
        <div class="news-modal-overlay" onclick="closeNewsModal()">
            <div class="news-modal" onclick="event.stopPropagation()">
                <div class="news-modal-header">
                    <h2 class="news-modal-title">${newsItem.title}</h2>
                    <button class="news-modal-close" onclick="closeNewsModal()">
                        <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                <div class="news-modal-content">
                    <div class="news-modal-meta">
                        <span class="news-modal-category ${newsItem.category}">${getCategoryLabel(newsItem.category)}</span>
                        <span class="news-modal-time">${formatDate(newsItem.pubDate)}</span>
                    </div>
                    <div class="news-loading">
                        <div class="loading-spinner"></div>
                        <p>기사 내용을 불러오는 중...</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 모달을 body에 추가
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // 모달 애니메이션
    const modal = document.querySelector('.news-modal-overlay');
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
    
    // ESC 키로 닫기
    document.addEventListener('keydown', handleModalKeydown);
}

// 기사 전문 가져오기
async function loadNewsContent(newsItem) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/news/content?url=${encodeURIComponent(newsItem.link)}`);
        const result = await response.json();
        
        if (result.success) {
            updateNewsModal(newsItem, result.data);
        } else {
            showErrorModal(newsItem, '기사 내용을 가져올 수 없습니다.');
        }
    } catch (error) {
        console.error('기사 내용 가져오기 오류:', error);
        showErrorModal(newsItem, '기사 내용을 불러오는 중 오류가 발생했습니다.');
    }
}

// 뉴스 모달 업데이트 (기사 전문 포함)
function updateNewsModal(newsItem, contentData) {
    const modal = document.querySelector('.news-modal-overlay');
    if (!modal) return;
    
    const contentDiv = modal.querySelector('.news-modal-content');
    
    // 이미지 HTML 생성
    let imagesHTML = '';
    if (contentData.images && contentData.images.length > 0) {
        imagesHTML = `
            <div class="news-modal-images">
                ${contentData.images.map(img => `
                    <div class="news-modal-image">
                        <img src="${img.src}" alt="${img.alt}" loading="lazy" />
                        <p class="image-caption">${img.alt}</p>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    contentDiv.innerHTML = `
        <div class="news-modal-meta">
            <span class="news-modal-category ${newsItem.category}">${getCategoryLabel(newsItem.category)}</span>
            <span class="news-modal-time">${formatDate(newsItem.pubDate)}</span>
        </div>
        ${imagesHTML}
        <div class="news-modal-description">
            <h3>기사 요약</h3>
            <p>${newsItem.description}</p>
        </div>
        <div class="news-modal-full-content">
            <h3>기사 전문</h3>
            <div class="news-content-text">
                ${contentData.content || '기사 전문을 가져올 수 없습니다.'}
            </div>
        </div>
        <div class="news-modal-actions">
            <button class="news-modal-btn primary" onclick="openNewsLink('${newsItem.link}')">
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                </svg>
                원문 보기
            </button>
            <button class="news-modal-btn secondary" onclick="shareNews('${newsItem.title}', '${newsItem.link}')">
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"></path>
                </svg>
                공유하기
            </button>
        </div>
    `;
}

// 오류 모달 표시
function showErrorModal(newsItem, errorMessage) {
    const modal = document.querySelector('.news-modal-overlay');
    if (!modal) return;
    
    const contentDiv = modal.querySelector('.news-modal-content');
    contentDiv.innerHTML = `
        <div class="news-modal-meta">
            <span class="news-modal-category ${newsItem.category}">${getCategoryLabel(newsItem.category)}</span>
            <span class="news-modal-time">${formatDate(newsItem.pubDate)}</span>
        </div>
        <div class="news-modal-description">
            <h3>기사 요약</h3>
            <p>${newsItem.description}</p>
        </div>
        <div class="news-error">
            <div class="error-icon">⚠️</div>
            <p>${errorMessage}</p>
        </div>
        <div class="news-modal-actions">
            <button class="news-modal-btn primary" onclick="openNewsLink('${newsItem.link}')">
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                </svg>
                원문 보기
            </button>
            <button class="news-modal-btn secondary" onclick="shareNews('${newsItem.title}', '${newsItem.link}')">
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"></path>
                </svg>
                공유하기
            </button>
        </div>
    `;
}

// 모달 닫기
function closeNewsModal() {
    const modal = document.querySelector('.news-modal-overlay');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
    document.removeEventListener('keydown', handleModalKeydown);
}

// ESC 키 처리
function handleModalKeydown(event) {
    if (event.key === 'Escape') {
        closeNewsModal();
    }
}

// 뉴스 링크 열기
function openNewsLink(url) {
    if (url) {
        window.open(url, '_blank');
    } else {
        showNotification('뉴스 링크가 없습니다.', 'error');
    }
}

// 뉴스 공유하기
function shareNews(title, url) {
    if (navigator.share) {
        navigator.share({
            title: title,
            url: url
        }).catch(err => {
            console.log('공유 실패:', err);
            copyToClipboard(url);
        });
    } else {
        copyToClipboard(url);
    }
}

// 클립보드에 복사
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('링크가 클립보드에 복사되었습니다!', 'success');
    }).catch(err => {
        console.log('복사 실패:', err);
        showNotification('복사에 실패했습니다.', 'error');
    });
}

// 뉴스 새로고침
async function refreshNews() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/news/refresh`);
        const result = await response.json();
        
        if (result.success) {
            const news = result.data.map((item, index) => ({
                id: index + 1,
                title: item.title,
                description: item.description || "상세 내용을 확인하려면 클릭하세요.",
                pubDate: item.pubDate,
                category: "politics",
                link: item.link
            }));
            newsData = news; // 전역 변수에 저장
            renderNewsList(news);
            
            // 성공 메시지 표시
            showNotification('뉴스가 새로고침되었습니다!', 'success');
        } else {
            console.error('뉴스 새로고침 실패:', result);
            showNotification('뉴스 새로고침에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('뉴스 새로고침 오류:', error);
        showNotification('뉴스 새로고침 중 오류가 발생했습니다.', 'error');
    }
}

// 알림 표시
function showNotification(message, type = 'info') {
    // 간단한 알림 구현
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 4px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    
    if (type === 'success') {
        notification.style.backgroundColor = '#10b981';
    } else if (type === 'error') {
        notification.style.backgroundColor = '#ef4444';
    } else {
        notification.style.backgroundColor = '#3b82f6';
    }
    
    document.body.appendChild(notification);
    
    // 3초 후 제거
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function showHotIssueDetail(keyword) {
    alert(`"${keyword}" 핫이슈 상세 보기 기능은 구현 예정입니다.`);
}

function showPoliticianDetail(politicianId) {
    alert(`정치인 ${politicianId} 상세 보기 기능은 구현 예정입니다.`);
}

// 정치인 언급 분석
async function analyzePoliticianMentions() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/news/analyze-mentions`);
        const data = await response.json();
        
        if (data.success && data.analysis) {
            console.log('정치인 언급 분석 완료:', data.analysis);
            // 언급 분석 결과를 UI에 반영
            updatePoliticianInfluence(data.analysis.mention_counts);
        }
    } catch (error) {
        console.error('정치인 언급 분석 오류:', error);
    }
}

// 정치인 영향력 업데이트
function updatePoliticianInfluence(mentionCounts) {
    const politicianCards = document.querySelectorAll('.politician-card');
    
    politicianCards.forEach(card => {
        const nameElement = card.querySelector('.politician-name');
        if (nameElement) {
            const name = nameElement.textContent.trim();
            // 해당 정치인의 언급 횟수 찾기
            const politician = Object.keys(mentionCounts).find(id => {
                // 실제로는 ID로 매칭해야 하지만, 여기서는 이름으로 간단히 처리
                return name.includes(name);
            });
            
            if (politician && mentionCounts[politician] > 0) {
                const influenceScore = Math.min(mentionCounts[politician] * 0.1, 10);
                const influenceElement = card.querySelector('.influence-score');
                if (influenceElement) {
                    influenceElement.textContent = `영향력: ${influenceScore.toFixed(1)}점`;
                }
            }
        }
    });
}

function showNetworkNodeDetail(nodeId) {
    alert(`"${nodeId}" 네트워크 노드 상세 보기 기능은 구현 예정입니다.`);
}
