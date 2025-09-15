import { useState, useEffect } from 'react'

const NewsWidget = () => {
  const [news, setNews] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 뉴스 데이터 로딩 시뮬레이션
    const mockNews = [
      {
        id: 1,
        title: "국회 예산안 심의 시작, 여야 대립 심화",
        description: "2024년 예산안 심의가 시작되면서 여야 간 대립이 심화되고 있다...",
        pubDate: "2024-01-15T10:30:00Z",
        category: "정치"
      },
      {
        id: 2,
        title: "정부, 새로운 경제정책 발표",
        description: "정부가 내년 경제성장을 위한 새로운 정책을 발표했다...",
        pubDate: "2024-01-15T09:15:00Z",
        category: "경제"
      },
      {
        id: 3,
        title: "국방위원회, 안보정책 논의",
        description: "국방위원회에서 최근 안보 상황에 대한 논의가 진행되었다...",
        pubDate: "2024-01-15T08:45:00Z",
        category: "국방"
      },
      {
        id: 4,
        title: "교육정책 개혁안 제출",
        description: "교육부가 새로운 교육정책 개혁안을 국회에 제출했다...",
        pubDate: "2024-01-15T07:20:00Z",
        category: "교육"
      },
      {
        id: 5,
        title: "환경정책 관련 법안 통과",
        description: "환경정책 관련 법안이 국회를 통과했다...",
        pubDate: "2024-01-15T06:30:00Z",
        category: "환경"
      }
    ]

    setTimeout(() => {
      setNews(mockNews)
      setIsLoading(false)
    }, 1000)
  }, [])

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString('ko-KR', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getCategoryColor = (category) => {
    const colors = {
      '정치': 'bg-red-100 text-red-800',
      '경제': 'bg-green-100 text-green-800',
      '국방': 'bg-blue-100 text-blue-800',
      '교육': 'bg-purple-100 text-purple-800',
      '환경': 'bg-emerald-100 text-emerald-800'
    }
    return colors[category] || 'bg-gray-100 text-gray-800'
  }

  if (isLoading) {
    return (
      <div className="bg-dark-800 rounded-lg p-6 border border-dark-700">
        <div className="animate-pulse">
          <div className="h-6 bg-dark-700 rounded mb-4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 bg-dark-700 rounded"></div>
                <div className="h-3 bg-dark-700 rounded w-3/4"></div>
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
          <svg className="w-5 h-5 mr-2 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
          </svg>
          실시간 뉴스
        </h2>
        <span className="text-sm text-dark-400">30초마다 업데이트</span>
      </div>
      
      <div className="space-y-4">
        {news.map((item) => (
          <div key={item.id} className="border-b border-dark-700 pb-4 last:border-b-0">
            <div className="flex items-start justify-between mb-2">
              <h3 className="text-sm font-medium text-white line-clamp-2 hover:text-primary-400 cursor-pointer transition-colors">
                {item.title}
              </h3>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(item.category)} ml-2 flex-shrink-0`}>
                {item.category}
              </span>
            </div>
            <p className="text-sm text-dark-400 line-clamp-2 mb-2">
              {item.description}
            </p>
            <div className="flex items-center justify-between text-xs text-dark-500">
              <span>{formatDate(item.pubDate)}</span>
              <button className="text-primary-500 hover:text-primary-400 transition-colors">
                자세히 보기 →
              </button>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t border-dark-700">
        <button className="w-full text-center text-sm text-primary-500 hover:text-primary-400 transition-colors">
          모든 뉴스 보기
        </button>
      </div>
    </div>
  )
}

export default NewsWidget
