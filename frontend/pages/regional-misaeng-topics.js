import React from 'react';
import Head from 'next/head';
import StaticRegionalMinsaengTopicsWidget from '../components/StaticRegionalMinsaengTopicsWidget';

const RegionalMinsaengTopicsPage = () => {
  return (
    <>
      <Head>
        <title>지역별 민생토픽 분석 | NewsBot 정세분석</title>
        <meta 
          name="description" 
          content="정책선거문화 빅데이터 분석을 통한 지역별 민생토픽 현황. 광역시도부터 읍면동까지 계층적 분석 결과 제공." 
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* 헤더 */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-sm">NB</span>
                  </div>
                  <h1 className="text-xl font-bold text-gray-800">
                    NewsBot 정세분석
                  </h1>
                </div>
                <span className="bg-orange-100 text-orange-800 px-3 py-1 rounded-full text-sm font-medium">
                  민생토픽 분석
                </span>
              </div>
              
              <nav className="flex items-center space-x-6">
                <a href="/" className="text-gray-600 hover:text-gray-900 transition-colors">
                  홈
                </a>
                <a href="/election-search" className="text-gray-600 hover:text-gray-900 transition-colors">
                  선거검색
                </a>
                <a href="/regional-misaeng-topics" className="text-blue-600 font-medium">
                  민생토픽
                </a>
              </nav>
            </div>
          </div>
        </header>

        {/* 메인 컨텐츠 */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* 페이지 제목 및 설명 */}
          <div className="mb-8">
            <div className="text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                시군구별 민생토픽 분석
              </h1>
              <p className="text-lg text-gray-600 mb-6 max-w-3xl mx-auto">
                207개 시군구의 2,612개 정책 공약을 분석하여 
                각 지역의 주요 민생토픽과 정책 이슈를 상세히 파악합니다.
              </p>
              
              {/* 분석 개요 */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
                <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
                  <div className="text-2xl font-bold text-blue-600">635</div>
                  <div className="text-sm text-gray-600">분석 페이지</div>
                </div>
                <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
                  <div className="text-2xl font-bold text-green-600">66</div>
                  <div className="text-sm text-gray-600">분석 지역</div>
                </div>
                <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
                  <div className="text-2xl font-bold text-purple-600">8</div>
                  <div className="text-sm text-gray-600">토픽 카테고리</div>
                </div>
                <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
                  <div className="text-2xl font-bold text-orange-600">279</div>
                  <div className="text-sm text-gray-600">추출 공약</div>
                </div>
              </div>
            </div>
          </div>

          {/* 민생토픽 분석 위젯 */}
          <div className="mb-8">
            <StaticRegionalMinsaengTopicsWidget />
          </div>

          {/* 추가 정보 섹션 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* 분석 방법론 */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <span className="text-blue-500 mr-2">📊</span>
                분석 방법론
              </h3>
              <div className="space-y-4 text-sm text-gray-600">
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">1. 텍스트 마이닝</h4>
                  <p>635페이지 정책선거문화 빅데이터 문서에서 지역별 키워드 추출 및 빈도 분석</p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">2. 토픽 모델링</h4>
                  <p>8개 민생토픽 카테고리별 점수 계산 및 지역별 주요 관심사 도출</p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">3. 계층적 분석</h4>
                  <p>광역시도 → 시군구 → 읍면동 3단계 행정구역별 세분화 분석</p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">4. 공약 추출</h4>
                  <p>정규표현식 기반 정책 공약성 표현 자동 추출 및 분류</p>
                </div>
              </div>
            </div>

            {/* 민생토픽 카테고리 */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <span className="text-orange-500 mr-2">🏷️</span>
                민생토픽 카테고리
              </h3>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { name: '경제정책', icon: '💼', color: 'blue' },
                  { name: '주거정책', icon: '🏠', color: 'green' },
                  { name: '교육정책', icon: '📚', color: 'purple' },
                  { name: '복지정책', icon: '🤝', color: 'pink' },
                  { name: '환경정책', icon: '🌱', color: 'emerald' },
                  { name: '교통정책', icon: '🚇', color: 'orange' },
                  { name: '문화정책', icon: '🎭', color: 'indigo' },
                  { name: '안전정책', icon: '🛡️', color: 'red' }
                ].map((topic) => (
                  <div 
                    key={topic.name}
                    className={`p-3 rounded-lg border bg-${topic.color}-50 border-${topic.color}-200`}
                  >
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">{topic.icon}</span>
                      <span className={`text-sm font-medium text-${topic.color}-800`}>
                        {topic.name}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 데이터 출처 */}
          <div className="mt-8 bg-gray-100 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">데이터 출처</h3>
            <div className="text-sm text-gray-600 space-y-2">
              <p>
                <strong>분석 문서:</strong> 231215_정책선거문화_확산을_위한_언론기사_빅데이터_분석.pdf
              </p>
              <p>
                <strong>분석 기간:</strong> 2025년 9월 20일 기준
              </p>
              <p>
                <strong>분석 범위:</strong> 전국 광역시도, 주요 시군구, 읍면동 총 66개 지역
              </p>
              <p>
                <strong>분석 도구:</strong> Python, PyMuPDF, 한국어 텍스트마이닝, 정규표현식 기반 패턴 매칭
              </p>
            </div>
          </div>
        </main>

        {/* 푸터 */}
        <footer className="bg-white border-t border-gray-200 mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center text-sm text-gray-500">
              <p>© 2025 NewsBot 정세분석. 정책선거문화 빅데이터 분석 시스템.</p>
              <p className="mt-2">
                지역별 민생토픽 분석을 통한 정책 관심사 파악 및 공약 추출 서비스
              </p>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
};

export default RegionalMinsaengTopicsPage;
