import Head from 'next/head'
import { useState, useEffect } from 'react'
import NewsWidget from '../components/NewsWidget'
import RecentBillsWidget from '../components/RecentBillsWidget'
import TrendChartWidget from '../components/TrendChartWidget'
import PoliticianProfileWidget from '../components/PoliticianProfileWidget'
import ConnectivityNetworkWidget from '../components/ConnectivityNetworkWidget'
import AnalysisReportWidget from '../components/AnalysisReportWidget'
import PoliticianEvaluationWidget from '../components/PoliticianEvaluationWidget'

export default function Home() {
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 초기 로딩 시뮬레이션
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 2000)

    return () => clearTimeout(timer)
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-dark-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-500 mx-auto"></div>
          <p className="mt-4 text-white text-lg">newsbot.kr 로딩 중...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-dark-900">
      <Head>
        <title>newsbot.kr - 정치 뉴스 분석 플랫폼</title>
        <meta name="description" content="국회 발언과 뉴스 데이터를 연결하여 정치적 인사이트를 제공하는 혁신적인 플랫폼" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      {/* 헤더 */}
      <header className="bg-dark-800 border-b border-dark-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-white">
                newsbot<span className="text-primary-500">.kr</span>
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <input
                  type="text"
                  placeholder="뉴스 검색..."
                  className="w-64 px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                  <svg className="h-5 w-5 text-dark-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
              </div>
              <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
                검색
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 컨텐츠 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 대시보드 위젯 그리드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* 실시간 뉴스 위젯 */}
          <div className="lg:col-span-1">
            <NewsWidget />
          </div>

          {/* 최근 입법 위젯 */}
          <div className="lg:col-span-1">
            <RecentBillsWidget />
          </div>

          {/* 트렌드 차트 위젯 */}
          <div className="lg:col-span-1">
            <TrendChartWidget />
          </div>

          {/* 정치인 프로필 위젯 - 더 큰 크기로 조정 */}
          <div className="lg:col-span-2">
            <PoliticianProfileWidget />
          </div>

          {/* 연결성 네트워크 위젯 */}
          <div className="lg:col-span-1">
            <ConnectivityNetworkWidget />
          </div>

          {/* 정치인 종합 평가 위젯 */}
          <div className="lg:col-span-2">
            <PoliticianEvaluationWidget />
          </div>

          {/* 분석 리포트 위젯 */}
          <div className="lg:col-span-1">
            <AnalysisReportWidget />
          </div>
        </div>
      </main>

      {/* 푸터 */}
      <footer className="bg-dark-800 border-t border-dark-700 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-dark-400">
            <p>&copy; 2024 newsbot.kr. All rights reserved.</p>
            <p className="mt-2">정치 뉴스 분석 플랫폼</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
