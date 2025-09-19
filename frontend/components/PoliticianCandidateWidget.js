import React, { useState, useEffect } from 'react';

const PoliticianCandidateWidget = ({ candidateName, onClose }) => {
  const [candidateData, setCandidateData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('basic');
  const [newsArticles, setNewsArticles] = useState([]);
  const [loadingNews, setLoadingNews] = useState(false);

  useEffect(() => {
    if (candidateName) {
      fetchCandidateData();
    }
  }, [candidateName]);

  const fetchCandidateData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 통합된 정치인 데이터에서 후보자 정보 조회
      const response = await fetch('/api/politicians/candidate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: candidateName })
      });

      if (response.ok) {
        const data = await response.json();
        setCandidateData(data);
      } else {
        throw new Error('후보자 정보를 불러올 수 없습니다');
      }
    } catch (err) {
      console.error('Error fetching candidate data:', err);
      setError(err.message);
      
      // 폴백 데이터 사용
      setCandidateData({
        basic_info: {
          name: candidateName,
          category: 'election_candidate',
          party: '정보 없음',
          district: '정보 없음',
          age: null,
          gender: null,
          education: null,
          career: null
        },
        election_info: {
          vote_count: null,
          vote_rate: null,
          is_elected: false,
          election_symbol: null,
          vote_grade: null
        },
        news_section: {
          articles: [],
          count: 0,
          placeholder_message: `${candidateName} 관련 최신 기사를 불러오는 중...`
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchNewsArticles = async () => {
    try {
      setLoadingNews(true);
      
      // 정치인 + 국회의원 기사 검색 (추후 구현)
      const response = await fetch(`/api/news/politician/${encodeURIComponent(candidateName)}`);
      
      if (response.ok) {
        const newsData = await response.json();
        setNewsArticles(newsData.articles || []);
      }
    } catch (err) {
      console.error('Error fetching news:', err);
      // 샘플 기사 데이터 (실제 구현 전까지)
      setNewsArticles([
        {
          title: `${candidateName} 관련 최신 뉴스 1`,
          url: '#',
          publishedAt: '2024-04-10',
          source: '뉴스 소스'
        },
        {
          title: `${candidateName} 관련 최신 뉴스 2`,
          url: '#',
          publishedAt: '2024-04-09',
          source: '뉴스 소스'
        }
      ]);
    } finally {
      setLoadingNews(false);
    }
  };

  const getPartyColor = (party) => {
    const partyColors = {
      '더불어민주당': 'bg-blue-600',
      '국민의힘': 'bg-red-600',
      '개혁신당': 'bg-orange-500',
      '진보당': 'bg-green-600',
      '새로운미래': 'bg-purple-600',
      '녹색정의당': 'bg-green-500',
      '무소속': 'bg-gray-600'
    };
    return partyColors[party] || 'bg-gray-500';
  };

  const getVoteGradeColor = (grade) => {
    const gradeColors = {
      '압승': 'text-green-600 font-bold',
      '승리': 'text-blue-600 font-semibold',
      '근소승': 'text-blue-500',
      '근소패': 'text-orange-500',
      '패배': 'text-red-500'
    };
    return gradeColors[grade] || 'text-gray-500';
  };

  const formatVoteCount = (count) => {
    if (!count) return '정보 없음';
    return count.toLocaleString() + '표';
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-center mt-4 text-gray-600">후보자 정보를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error && !candidateData) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <div className="text-red-500 mb-4">
              <svg className="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <p className="text-red-500 mb-4">{error}</p>
            <button
              onClick={onClose}
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 transition-colors"
            >
              닫기
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!candidateData) return null;

  const { basic_info, election_info, news_section } = candidateData;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* 헤더 */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
          <div className="flex justify-between items-start">
            <div className="flex items-center space-x-4">
              {/* 프로필 이미지 영역 */}
              <div className="w-24 h-24 bg-white bg-opacity-20 rounded-full flex items-center justify-center text-2xl font-bold">
                {basic_info.name ? basic_info.name.charAt(0) : '?'}
              </div>
              
              <div>
                <h2 className="text-3xl font-bold">{basic_info.name}</h2>
                <div className="flex items-center space-x-2 mt-2">
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getPartyColor(basic_info.party)} text-white`}>
                    {basic_info.party || '정당 미상'}
                  </span>
                  <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full text-sm">
                    22대 선거 출마자
                  </span>
                </div>
                <p className="text-blue-100 mt-1">{basic_info.district || '선거구 미상'}</p>
              </div>
            </div>
            
            <button
              onClick={onClose}
              className="text-white hover:text-gray-300 transition-colors"
            >
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* 탭 메뉴 */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('basic')}
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                activeTab === 'basic'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              기본 정보
            </button>
            <button
              onClick={() => setActiveTab('election')}
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                activeTab === 'election'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              선거 결과
            </button>
            <button
              onClick={() => {
                setActiveTab('news');
                if (newsArticles.length === 0) {
                  fetchNewsArticles();
                }
              }}
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                activeTab === 'news'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              관련 기사
            </button>
          </nav>
        </div>

        {/* 탭 콘텐츠 */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {activeTab === 'basic' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* 개인 정보 */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">👤 개인 정보</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">나이:</span>
                      <span className="font-medium">{basic_info.age ? `${basic_info.age}세` : '정보 없음'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">성별:</span>
                      <span className="font-medium">{basic_info.gender || '정보 없음'}</span>
                    </div>
                  </div>
                </div>

                {/* 소속 정보 */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">🏛️ 소속 정보</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">정당:</span>
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${getPartyColor(basic_info.party)} text-white`}>
                        {basic_info.party || '정보 없음'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">출마 선거구:</span>
                      <span className="font-medium">{basic_info.district || '정보 없음'}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* 학력 및 경력 */}
              {(basic_info.education || basic_info.career) && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">🎓 학력 및 경력</h3>
                  {basic_info.education && (
                    <div className="mb-3">
                      <span className="text-gray-600 text-sm">학력:</span>
                      <p className="mt-1 text-sm">{basic_info.education}</p>
                    </div>
                  )}
                  {basic_info.career && (
                    <div>
                      <span className="text-gray-600 text-sm">경력:</span>
                      <p className="mt-1 text-sm">{basic_info.career}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {activeTab === 'election' && election_info && (
            <div className="space-y-6">
              {/* 선거 결과 요약 */}
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg border">
                <h3 className="text-xl font-bold text-gray-800 mb-4">🗳️ 22대 국회의원선거 결과</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {formatVoteCount(election_info.vote_count)}
                    </div>
                    <div className="text-sm text-gray-600">득표수</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {election_info.vote_rate ? `${election_info.vote_rate.toFixed(1)}%` : '정보 없음'}
                    </div>
                    <div className="text-sm text-gray-600">득표율</div>
                  </div>
                  <div className="text-center">
                    <div className={`text-2xl font-bold ${election_info.is_elected ? 'text-green-600' : 'text-red-500'}`}>
                      {election_info.is_elected ? '당선' : '낙선'}
                    </div>
                    <div className="text-sm text-gray-600">결과</div>
                  </div>
                </div>
              </div>

              {/* 상세 선거 정보 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-3">📊 선거 상세</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">기호:</span>
                      <span className="font-medium">{election_info.election_symbol || '정보 없음'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">득표 등급:</span>
                      <span className={getVoteGradeColor(election_info.vote_grade)}>
                        {election_info.vote_grade || '정보 없음'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-3">🏆 선거 결과</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">당선 여부:</span>
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        election_info.is_elected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {election_info.is_elected ? '당선' : '낙선'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'news' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-800">📰 관련 기사</h3>
                <button
                  onClick={fetchNewsArticles}
                  disabled={loadingNews}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium disabled:opacity-50"
                >
                  {loadingNews ? '불러오는 중...' : '새로고침'}
                </button>
              </div>

              {loadingNews ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="text-gray-600 mt-2">기사를 불러오는 중...</p>
                </div>
              ) : newsArticles.length > 0 ? (
                <div className="space-y-4">
                  {newsArticles.map((article, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                      <h4 className="font-medium text-gray-800 mb-2">{article.title}</h4>
                      <div className="flex items-center justify-between text-sm text-gray-600">
                        <span>{article.source}</span>
                        <span>{article.publishedAt}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 bg-gray-50 rounded-lg">
                  <div className="text-gray-500 mb-2">
                    <svg className="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                    </svg>
                  </div>
                  <p className="text-gray-600">{news_section?.placeholder_message || '관련 기사가 없습니다.'}</p>
                  <p className="text-sm text-gray-500 mt-2">추후 정치인 + 국회의원 기사 검색 기능이 추가됩니다.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PoliticianCandidateWidget;

