import { useState, useEffect } from 'react'

const OptimizedNewsWidget = () => {
  const [news, setNews] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadRecentNews()
    
    // 30초마다 자동 업데이트
    const interval = setInterval(loadRecentNews, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadRecentNews = async () => {
    try {
      setError(null)
      
      // 실시간 뉴스 API 호출 (18건으로 증가)
      const response = await fetch('https://newsbot-backend-6j3p.onrender.com/api/news/trending?limit=18')
      
      if (response.ok) {
        const data = await response.json()
        
        if (data.success) {
          setNews(data.data || [])
          console.log('✅ 실시간 뉴스 로드:', data.data?.length + '건')
        } else {
          throw new Error(data.error || '뉴스 로드 실패')
        }
      } else {
        throw new Error(`API 오류: ${response.status}`)
      }
      
    } catch (err) {
      console.error('뉴스 로드 오류:', err)
      setError(err.message)
      
      // 폴백: 최신 정치 뉴스 샘플
      const fallbackNews = [
        {
          title: "결국 구속된 권성동 '이재명 정권 정치탄압의 신호탄'",
          description: "권성동 국민의힘 의원이 구속되면서 정치권에 큰 파장이 일고 있다",
          pub_date: "Wed, 17 Sep 2025 16:00:00 +0900",
          politician: "이재명",
          sentiment: "negative"
        },
        {
          title: "배현진, 국민의힘 서울시당위원장 당선···한동훈 '응원한다'",
          description: "배현진 의원이 국민의힘 서울시당위원장에 당선되었다",
          pub_date: "Wed, 17 Sep 2025 15:30:00 +0900", 
          politician: "한동훈",
          sentiment: "neutral"
        },
        {
          title: "조국 '조희대 탄핵안 이미 준비…파기환송 판결 특검도 필요'",
          description: "조국 조국혁신당 비상대책위원장이 대법원장 탄핵안을 준비했다고 밝혔다",
          pub_date: "Wed, 17 Sep 2025 14:45:00 +0900",
          politician: "조국", 
          sentiment: "neutral"
        },
        {
          title: "'성비위 사태' 조국혁신당, 전 의원 등 대상 성희롱 예방 교육",
          description: "조국혁신당이 성비위 사태와 관련해 성희롱 예방 교육을 실시했다",
          pub_date: "Wed, 17 Sep 2025 14:00:00 +0900",
          politician: "조국",
          sentiment: "negative"
        },
        {
          title: "한동훈 '민주당, 계엄 확신 근거 공개하고 특검에 제출해야'",
          description: "한동훈 전 국민의힘 대표가 민주당에 계엄 관련 근거 공개를 요구했다",
          pub_date: "Wed, 17 Sep 2025 13:30:00 +0900",
          politician: "한동훈",
          sentiment: "neutral"
        }
      ]
      setNews(fallbackNews)
    } finally {
      setIsLoading(false)
    }
  }

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return '😊'
      case 'negative':
        return '😠'
      default:
        return '😐'
    }
  }

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return 'text-green-400 bg-green-900/20'
      case 'negative':
        return 'text-red-400 bg-red-900/20'
      default:
        return 'text-gray-400 bg-gray-900/20'
    }
  }

  const formatDate = (dateString) => {
    try {
      // RFC 2822 형식 파싱
      const date = new Date(dateString)
      return date.toLocaleDateString('ko-KR', { 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return '날짜 정보 없음'
    }
  }

  return (
    <div className="bg-dark-800 rounded-lg p-6 border border-dark-700 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white">실시간 뉴스</h2>
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1 text-sm text-primary-400">
            <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></div>
            <span>30초마다 업데이트</span>
          </div>
          <button 
            onClick={loadRecentNews}
            className="text-primary-500 hover:text-primary-400 transition-colors"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>

      {/* 스크롤 가능한 뉴스 목록 */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2 scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="h-4 bg-dark-700 rounded mb-2"></div>
                <div className="h-3 bg-dark-700 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <div className="text-red-400 mb-2">
              <svg className="h-8 w-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        ) : news.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-gray-400 mb-2">
              <svg className="h-8 w-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9.5a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
              </svg>
            </div>
            <p className="text-gray-400 text-sm">뉴스 데이터가 없습니다.</p>
          </div>
        ) : (
          news.map((item, index) => (
            <div key={index} className="border-b border-dark-700 pb-4 last:border-b-0 hover:bg-dark-700/50 p-2 rounded transition-colors">
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-sm font-medium text-white line-clamp-2 flex-1 mr-2">
                  {item.title}
                </h3>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSentimentColor(item.sentiment)}`}>
                  {getSentimentIcon(item.sentiment)}
                </span>
              </div>
              
              <p className="text-xs text-gray-400 mb-2 line-clamp-2">
                {item.description}
              </p>
              
              <div className="flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-primary-400">
                    {item.politician}
                  </span>
                  <span className="text-gray-500">•</span>
                  <span>정치</span>
                </div>
                <span>{formatDate(item.pub_date)}</span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* 하단 버튼 */}
      <div className="mt-4 pt-4 border-t border-dark-700">
        <button className="w-full text-center text-primary-500 hover:text-primary-400 text-sm font-medium transition-colors">
          모든 뉴스 보기 →
        </button>
      </div>
    </div>
  )
}

export default OptimizedNewsWidget
