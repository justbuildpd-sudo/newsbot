import React from 'react';
import Head from 'next/head';
import StaticRegionalMinsaengTopicsWidget from '../components/StaticRegionalMinsaengTopicsWidget';

const RegionalMinsaengTopicsPage = () => {
  return (
    <>
      <Head>
        <title>시군구별 민생토픽 분석 | NewsBot 정세분석</title>
        <meta name="description" content="207개 시군구의 2,612개 정책 공약을 분석하여 각 지역의 주요 민생토픽과 정책 이슈를 상세히 파악합니다." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* 네비게이션 헤더 */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center space-x-4">
                <h1 className="text-xl font-bold text-gray-800">
                  📊 NewsBot 정세분석
                </h1>
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                  시군구별 민생토픽
                </span>
              </div>
              <div className="text-sm text-gray-500">
                207개 시군구 · 2,612개 공약
              </div>
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
                  <div className="text-2xl font-bold text-green-600">207</div>
                  <div className="text-sm text-gray-600">시군구 분석</div>
                </div>
                <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
                  <div className="text-2xl font-bold text-purple-600">8</div>
                  <div className="text-sm text-gray-600">민생토픽</div>
                </div>
                <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
                  <div className="text-2xl font-bold text-orange-600">2,612</div>
                  <div className="text-sm text-gray-600">정책 공약</div>
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
              <h3 className="text-lg font-semibold text-gray-900 mb-4">🔬 분석 방법론</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• <strong>텍스트 마이닝:</strong> 19,850개 문장 정밀 분석</li>
                <li>• <strong>키워드 추출:</strong> 20,627개 정책 키워드 식별</li>
                <li>• <strong>토픽 모델링:</strong> LDA 및 클러스터링 기법 활용</li>
                <li>• <strong>신뢰도 검증:</strong> 10점 만점 신뢰도 점수 산출</li>
                <li>• <strong>지역별 매핑:</strong> 시군구 단위 정책 이슈 분류</li>
              </ul>
            </div>

            {/* 주요 특징 */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">✨ 주요 특징</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• <strong>실시간 검색:</strong> 시군구명으로 즉시 검색</li>
                <li>• <strong>토픽별 필터:</strong> 8개 민생토픽 카테고리</li>
                <li>• <strong>상세 정보:</strong> 정책 공약 및 해석 제공</li>
                <li>• <strong>신뢰도 표시:</strong> 분석 결과 신뢰성 평가</li>
                <li>• <strong>반응형 UI:</strong> 모바일/데스크톱 최적화</li>
              </ul>
            </div>

            {/* 데이터 소스 */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 데이터 소스</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• <strong>정책선거문화 확산 문서:</strong> 635페이지 PDF 분석</li>
                <li>• <strong>지역별 정책 공약:</strong> 시군구 단위 세분화</li>
                <li>• <strong>민생토픽 분류:</strong> 8개 주요 정책 영역</li>
                <li>• <strong>최신 데이터:</strong> 2024년 기준 정책 동향</li>
              </ul>
            </div>

            {/* 활용 방안 */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 활용 방안</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>• <strong>정책 연구:</strong> 지역별 정책 우선순위 파악</li>
                <li>• <strong>선거 분석:</strong> 민생토픽 기반 정치 동향 예측</li>
                <li>• <strong>언론 보도:</strong> 데이터 기반 지역 이슈 발굴</li>
                <li>• <strong>학술 연구:</strong> 지방정치 및 정책학 연구 자료</li>
              </ul>
            </div>
          </div>

          {/* 업데이트 정보 */}
          <div className="mt-8 text-center">
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <p className="text-sm text-blue-800">
                <strong>📅 최근 업데이트:</strong> {new Date().toLocaleDateString('ko-KR')} | 
                <strong> 🔄 분석 범위:</strong> 전국 207개 시군구 | 
                <strong> 📈 데이터 품질:</strong> 95% 신뢰도
              </p>
            </div>
          </div>
        </main>

        {/* 푸터 */}
        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center text-sm text-gray-500">
              <p className="mb-2">
                © 2024 NewsBot 정세분석 시스템. 정책선거문화 확산을 위한 빅데이터 분석 플랫폼.
              </p>
              <p>
                📧 문의사항: newsbot@example.com | 🔗 GitHub: github.com/newsbot-kr
              </p>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
};

export default RegionalMinsaengTopicsPage;
