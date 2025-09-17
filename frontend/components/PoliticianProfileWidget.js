import { useState, useEffect } from 'react'
import MemberDetailWidget from './MemberDetailWidget'

const PoliticianProfileWidget = () => {
  const [politicians, setPoliticians] = useState([])
  const [billScores, setBillScores] = useState({})
  const [isLoading, setIsLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(0)
  const [hasMore, setHasMore] = useState(true)
  const [isLoadingMore, setIsLoadingMore] = useState(false)
  const [selectedMember, setSelectedMember] = useState(null)
  const itemsPerPage = 10

  useEffect(() => {
    loadPoliticians(0)
    loadBillScores()
  }, [])

  const loadBillScores = async () => {
    try {
      const response = await fetch('https://newsbot-backend-6j3p.onrender.com/api/bills/scores')
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setBillScores(data.data)
        }
      }
    } catch (error) {
      console.error('Error loading bill scores:', error)
    }
  }

  const loadPoliticians = async (page = 0) => {
    try {
      if (page === 0) {
        setIsLoading(true)
      } else {
        setIsLoadingMore(true)
      }

      const response = await fetch(`https://newsbot-backend-6j3p.onrender.com/api/assembly/members`)
      if (!response.ok) {
        throw new Error('Failed to fetch politicians')
      }
      
      const data = await response.json()
      const allPoliticians = data.data || []
      
      // 페이지네이션 적용
      const startIndex = page * itemsPerPage
      const endIndex = startIndex + itemsPerPage
      const pagePoliticians = allPoliticians.slice(startIndex, endIndex)
      
      if (page === 0) {
        setPoliticians(pagePoliticians)
      } else {
        setPoliticians(prev => [...prev, ...pagePoliticians])
      }
      
      setHasMore(endIndex < allPoliticians.length)
      setCurrentPage(page)
      
    } catch (error) {
      console.error('Error loading politicians:', error)
    } finally {
      setIsLoading(false)
      setIsLoadingMore(false)
    }
  }

  const loadMore = () => {
    if (!isLoadingMore && hasMore) {
      loadPoliticians(currentPage + 1)
    }
  }

  const getPartyColor = (party) => {
    const colors = {
      '더불어민주당': 'bg-blue-100 text-blue-800 border-blue-200',
      '국민의힘': 'bg-red-100 text-red-800 border-red-200',
      '개혁신당': 'bg-green-100 text-green-800 border-green-200',
      '새로운미래': 'bg-purple-100 text-purple-800 border-purple-200',
      '조국혁신당': 'bg-orange-100 text-orange-800 border-orange-200',
      '진보당': 'bg-pink-100 text-pink-800 border-pink-200',
      '기본소득당': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      '녹색정의당': 'bg-emerald-100 text-emerald-800 border-emerald-200',
      '무소속': 'bg-gray-100 text-gray-800 border-gray-200',
      '정당정보없음': 'bg-gray-100 text-gray-600 border-gray-200'
    }
    return colors[party] || colors['정당정보없음']
  }

  const getInitials = (name) => {
    return name ? name.charAt(0) : '?'
  }

  const getBillScore = (memberName) => {
    return billScores[memberName] || { main_proposals: 0, co_proposals: 0, total_bills: 0 }
  }

  const handleMemberClick = (memberName) => {
    setSelectedMember(memberName)
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">국회의원 현황</h2>
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4">국회의원 현황</h2>
      
      <div className="h-96 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
        <div className="grid grid-cols-1 gap-4">
          {politicians.map((politician, index) => {
            const billScore = getBillScore(politician.name)
            return (
              <div 
                key={politician.id || index} 
                className="flex items-center space-x-4 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                onClick={() => handleMemberClick(politician.name)}
              >
                {/* 프로필 영역 - 정당명 텍스트 표시 */}
                <div className="flex-shrink-0">
                  <div className={`w-12 h-12 rounded-full overflow-hidden flex items-center justify-center text-sm font-bold ${getPartyColor(politician.party)}`}>
                    {politician.photo_url ? (
                      <img 
                        src={politician.photo_url} 
                        alt={politician.name || politician.naas_nm}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.parentElement.textContent = getInitials(politician.name);
                        }}
                      />
                    ) : (
                      getInitials(politician.name)
                    )}
                  </div>
                </div>
                
                {/* 정보 영역 */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className="text-sm font-medium text-gray-900 truncate">
                      {politician.name}
                    </h3>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getPartyColor(politician.party)}`}>
                      {politician.party || '정당정보없음'}
                    </span>
                  </div>
                  
                  <div className="text-xs text-gray-500 space-y-1">
                    {politician.district && (
                      <p className="truncate">지역구: {politician.district}</p>
                    )}
                    {politician.office && (
                      <p className="truncate">소속: {politician.office}</p>
                    )}
                    {politician.terms && (
                      <p className="truncate">선거구분: {politician.terms}</p>
                    )}
                  </div>
                </div>

                {/* 발의의안 점수 영역 */}
                <div className="flex-shrink-0 text-right">
                  <div className="text-xs text-gray-500 mb-1">발의의안</div>
                  <div className="flex items-center space-x-2">
                    <div className="text-center">
                      <div className="text-sm font-bold text-blue-600">{billScore.main_proposals}</div>
                      <div className="text-xs text-gray-400">대표</div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm font-bold text-purple-600">{billScore.co_proposals}</div>
                      <div className="text-xs text-gray-400">공동</div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm font-bold text-green-600">{billScore.total_bills}</div>
                      <div className="text-xs text-gray-400">총계</div>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
      
      {/* 더 보기 버튼 */}
      {hasMore && (
        <div className="mt-4 text-center">
          <button
            onClick={loadMore}
            disabled={isLoadingMore}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoadingMore ? '로딩 중...' : '더 보기'}
          </button>
        </div>
      )}
      
      {/* 통계 정보 */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          총 {politicians.length}명 표시 중
        </p>
      </div>

      {/* 의원 상세정보 모달 */}
      {selectedMember && (
        <MemberDetailWidget 
          memberName={selectedMember}
          onClose={() => setSelectedMember(null)}
        />
      )}
    </div>
  )
}

export default PoliticianProfileWidget
