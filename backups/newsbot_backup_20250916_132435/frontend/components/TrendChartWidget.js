import { useState, useEffect } from 'react'

const TrendChartWidget = () => {
  const [trendData, setTrendData] = useState([])
  const [selectedPeriod, setSelectedPeriod] = useState('week')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 트렌드 데이터 로딩 시뮬레이션
    const mockTrendData = {
      week: [
        { date: '2024-01-08', value: 45, sentiment: 0.2 },
        { date: '2024-01-09', value: 52, sentiment: 0.3 },
        { date: '2024-01-10', value: 48, sentiment: 0.1 },
        { date: '2024-01-11', value: 61, sentiment: 0.4 },
        { date: '2024-01-12', value: 58, sentiment: 0.3 },
        { date: '2024-01-13', value: 55, sentiment: 0.2 },
        { date: '2024-01-14', value: 62, sentiment: 0.5 }
      ],
      month: [
        { date: '2024-01-01', value: 42, sentiment: 0.1 },
        { date: '2024-01-08', value: 45, sentiment: 0.2 },
        { date: '2024-01-15', value: 62, sentiment: 0.5 }
      ]
    }

    setTimeout(() => {
      setTrendData(mockTrendData[selectedPeriod])
      setIsLoading(false)
    }, 1000)
  }, [selectedPeriod])

  const getMaxValue = () => {
    return Math.max(...trendData.map(item => item.value))
  }

  const getSentimentColor = (sentiment) => {
    if (sentiment > 0.3) return 'text-green-500'
    if (sentiment < -0.3) return 'text-red-500'
    return 'text-yellow-500'
  }

  const getSentimentLabel = (sentiment) => {
    if (sentiment > 0.3) return '긍정'
    if (sentiment < -0.3) return '부정'
    return '중립'
  }

  if (isLoading) {
    return (
      <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
        <div className="animate-pulse">
          <div className="h-6 bg-dark-700 rounded mb-4"></div>
          <div className="h-32 bg-dark-700 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white flex items-center">
          <svg className="w-5 h-5 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          트렌드 차트
        </h2>
        <div className="flex space-x-2">
          <button
            onClick={() => setSelectedPeriod('week')}
            className={`px-3 py-1 text-xs rounded-full transition-colors ${
              selectedPeriod === 'week'
                ? 'bg-primary-600 text-white'
                : 'bg-dark-700 text-dark-400 hover:bg-dark-600'
            }`}
          >
            주간
          </button>
          <button
            onClick={() => setSelectedPeriod('month')}
            className={`px-3 py-1 text-xs rounded-full transition-colors ${
              selectedPeriod === 'month'
                ? 'bg-primary-600 text-white'
                : 'bg-dark-700 text-dark-400 hover:bg-dark-600'
            }`}
          >
            월간
          </button>
        </div>
      </div>
      
      <div className="space-y-4">
        {/* 간단한 막대 차트 */}
        <div className="h-32 flex items-end space-x-1">
          {trendData.map((item, index) => {
            const height = (item.value / getMaxValue()) * 100
            return (
              <div key={index} className="flex flex-col items-center flex-1">
                <div
                  className="bg-primary-500 rounded-t w-full transition-all duration-300 hover:bg-primary-400"
                  style={{ height: `${height}%` }}
                ></div>
                <span className="text-xs text-dark-400 mt-1">
                  {new Date(item.date).getDate()}
                </span>
              </div>
            )
          })}
        </div>
        
        {/* 통계 정보 */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-dark-700 rounded-lg p-3">
            <p className="text-xs text-dark-400 mb-1">평균 언급 수</p>
            <p className="text-lg font-semibold text-white">
              {Math.round(trendData.reduce((sum, item) => sum + item.value, 0) / trendData.length)}
            </p>
          </div>
          <div className="bg-dark-700 rounded-lg p-3">
            <p className="text-xs text-dark-400 mb-1">평균 감정</p>
            <p className={`text-lg font-semibold ${getSentimentColor(trendData[trendData.length - 1]?.sentiment || 0)}`}>
              {getSentimentLabel(trendData[trendData.length - 1]?.sentiment || 0)}
            </p>
          </div>
        </div>
        
        {/* 최근 트렌드 요약 */}
        <div className="bg-dark-700 rounded-lg p-3">
          <p className="text-xs text-dark-400 mb-2">최근 트렌드</p>
          <div className="flex items-center space-x-2">
            <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 17l9.2-9.2M17 17V7H7" />
            </svg>
            <span className="text-sm text-white">
              지난 7일간 정치 뉴스 언급량이 15% 증가했습니다.
            </span>
          </div>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-dark-700">
        <button className="w-full text-center text-sm text-green-500 hover:text-green-400 transition-colors">
          상세 분석 보기
        </button>
      </div>
    </div>
  )
}

export default TrendChartWidget
