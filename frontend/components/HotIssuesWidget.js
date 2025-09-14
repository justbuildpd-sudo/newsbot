import { useState, useEffect } from 'react'

const HotIssuesWidget = () => {
  const [hotIssues, setHotIssues] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 핫이슈 데이터 로딩 시뮬레이션
    const mockHotIssues = [
      { keyword: "예산안", count: 1250, trend: "up", change: "+15%" },
      { keyword: "국방정책", count: 980, trend: "up", change: "+8%" },
      { keyword: "교육개혁", count: 850, trend: "down", change: "-3%" },
      { keyword: "환경정책", count: 720, trend: "up", change: "+12%" },
      { keyword: "경제정책", count: 680, trend: "stable", change: "0%" },
      { keyword: "복지정책", count: 590, trend: "up", change: "+5%" },
      { keyword: "외교정책", count: 520, trend: "down", change: "-2%" },
      { keyword: "법무정책", count: 480, trend: "up", change: "+7%" }
    ]

    setTimeout(() => {
      setHotIssues(mockHotIssues)
      setIsLoading(false)
    }, 1000)
  }, [])

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up':
        return (
          <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 17l9.2-9.2M17 17V7H7" />
          </svg>
        )
      case 'down':
        return (
          <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 7l-9.2 9.2M7 7v10h10" />
          </svg>
        )
      default:
        return (
          <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
          </svg>
        )
    }
  }

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'up':
        return 'text-green-500'
      case 'down':
        return 'text-red-500'
      default:
        return 'text-gray-500'
    }
  }

  if (isLoading) {
    return (
      <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
        <div className="animate-pulse">
          <div className="h-6 bg-dark-700 rounded mb-4"></div>
          <div className="space-y-3">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="h-4 bg-dark-700 rounded w-1/3"></div>
                <div className="h-4 bg-dark-700 rounded w-1/4"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white flex items-center">
          <svg className="w-5 h-5 mr-2 text-secondary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          핫이슈 랭킹
        </h2>
        <span className="text-sm text-dark-400">실시간</span>
      </div>
      
      <div className="space-y-3">
        {hotIssues.map((issue, index) => (
          <div key={issue.keyword} className="flex items-center justify-between p-3 bg-dark-700 rounded-lg hover:bg-dark-600 transition-colors cursor-pointer">
            <div className="flex items-center space-x-3">
              <span className="text-lg font-bold text-white w-6 text-center">
                {index + 1}
              </span>
              <div>
                <h3 className="text-sm font-medium text-white">
                  {issue.keyword}
                </h3>
                <p className="text-xs text-dark-400">
                  {issue.count.toLocaleString()}회 언급
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                {getTrendIcon(issue.trend)}
                <span className={`text-xs font-medium ${getTrendColor(issue.trend)}`}>
                  {issue.change}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t border-dark-700">
        <button className="w-full text-center text-sm text-secondary-500 hover:text-secondary-400 transition-colors">
          상세 분석 보기
        </button>
      </div>
    </div>
  )
}

export default HotIssuesWidget
