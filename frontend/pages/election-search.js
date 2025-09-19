import React from 'react';
import Head from 'next/head';
import ElectionResultsWidget from '../components/ElectionResultsWidget';

export default function ElectionSearchPage() {
  return (
    <>
      <Head>
        <title>읍면동별 선거결과 검색 | NewsBot 정세분석</title>
        <meta name="description" content="280MB 캐시 시스템으로 읍면동별 선거결과와 출마 후보 정보를 0.3ms 초고속 검색" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        {/* 네비게이션 바 */}
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-6xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <h1 className="text-xl font-bold text-gray-800">
                  📊 NewsBot 정세분석
                </h1>
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                  280MB 캐시 시스템
                </span>
              </div>
              
              <div className="flex items-center space-x-4">
                <a href="/" className="text-gray-600 hover:text-gray-800 text-sm">
                  홈
                </a>
                <a href="/political-analysis" className="text-gray-600 hover:text-gray-800 text-sm">
                  정치분석
                </a>
                <a href="/election-search" className="text-blue-600 font-medium text-sm">
                  선거검색
                </a>
              </div>
            </div>
          </div>
        </nav>

        {/* 메인 컨텐츠 */}
        <ElectionResultsWidget />

        {/* 푸터 */}
        <footer className="bg-gray-800 text-white py-8 mt-12">
          <div className="max-w-6xl mx-auto px-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div>
                <h3 className="font-semibold mb-4">🗳️ 선거 정보 시스템</h3>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li>• 1,580개 읍면동 완전 지원</li>
                  <li>• 6개 선거 유형 전체 결과</li>
                  <li>• 출마 후보 상세 정보</li>
                  <li>• 0.3ms 초고속 검색</li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-semibold mb-4">📊 96.19% 다양성 시스템</h3>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li>• 19차원 완전 분석</li>
                  <li>• 245개 지자체 통계</li>
                  <li>• AI 예측 모델</li>
                  <li>• 실시간 업데이트</li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-semibold mb-4">⚡ 시스템 성능</h3>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li>• 280MB 캐시 (95% 활용)</li>
                  <li>• Raw JSON 직접 제공</li>
                  <li>• 99% 데이터 완성도</li>
                  <li>• 렌더 프로세스 관리</li>
                </ul>
              </div>
            </div>
            
            <div className="border-t border-gray-700 mt-8 pt-8 text-center">
              <p className="text-sm text-gray-400">
                © 2025 NewsBot 정세분석 시스템 | 280MB 최대 활용 캐시 | 96.19% 다양성 시스템
              </p>
            </div>
          </div>
        </footer>
      </main>
    </>
  );
}
