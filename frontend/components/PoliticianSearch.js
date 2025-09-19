import { useState, useEffect, useRef } from 'react'

const PoliticianSearch = ({ onSelectPolitician }) => {
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [searchResults, setSearchResults] = useState([])
  const [isSearching, setIsSearching] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [error, setError] = useState(null)
  const searchRef = useRef(null)

  useEffect(() => {
    // 클릭 외부 감지
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowSuggestions(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    // 검색어 변경 시 자동완성
    if (query.length >= 1) {
      loadSuggestions(query)
    } else {
      setSuggestions([])
      setShowSuggestions(false)
    }
  }, [query])

  const loadSuggestions = async (searchQuery) => {
    try {
      const response = await fetch(`https://newsbot-backend-6j3p.onrender.com/api/search/suggestions?q=${encodeURIComponent(searchQuery)}`)
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setSuggestions(data.suggestions || [])
          setShowSuggestions(data.suggestions?.length > 0)
        }
      }
    } catch (error) {
      console.error('자동완성 로드 실패:', error)
    }
  }

  const handleSearch = async (searchQuery = query) => {
    if (!searchQuery.trim()) {
      setError('정치인 이름을 입력해주세요.')
      return
    }

    try {
      setIsSearching(true)
      setError(null)
      setShowSuggestions(false)

      const response = await fetch(`https://newsbot-backend-6j3p.onrender.com/api/search/politicians?q=${encodeURIComponent(searchQuery)}&limit=10`)
      
      if (response.ok) {
        const data = await response.json()
        
        if (data.success) {
          setSearchResults(data.results || [])
          if (data.results?.length === 0) {
            setError('검색 결과가 없습니다.')
          }
        } else {
          setError(data.error || '검색에 실패했습니다.')
          // 추천 검색어가 있으면 표시
          if (data.suggestions?.length > 0) {
            setSuggestions(data.suggestions)
            setShowSuggestions(true)
          }
        }
      } else {
        setError('검색 서비스에 연결할 수 없습니다.')
      }
    } catch (err) {
      setError('검색 중 오류가 발생했습니다.')
      console.error('Search error:', err)
    } finally {
      setIsSearching(false)
    }
  }

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion.name)
    setShowSuggestions(false)
    handleSearch(suggestion.name)
  }

  const handleResultClick = (politician) => {
    if (onSelectPolitician) {
      onSelectPolitician(politician)
    }
  }

  const getPartyColor = (party) => {
    switch (party) {
      case '더불어민주당':
        return 'text-blue-600 bg-blue-50'
      case '국민의힘':
        return 'text-red-600 bg-red-50'
      case '조국혁신당':
        return 'text-purple-600 bg-purple-50'
      case '개혁신당':
        return 'text-green-600 bg-green-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="relative" ref={searchRef}>
      {/* 검색 입력창 */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
          placeholder="정치인 이름을 검색하세요..."
          className="block w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
        
        <button
          onClick={() => handleSearch()}
          disabled={isSearching}
          className="absolute inset-y-0 right-0 pr-3 flex items-center"
        >
          {isSearching ? (
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
          ) : (
            <svg className="h-5 w-5 text-gray-400 hover:text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          )}
        </button>
      </div>

      {/* 자동완성 드롭다운 */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {suggestions.map((suggestion, index) => (
            <div
              key={index}
              onClick={() => handleSuggestionClick(suggestion)}
              className="px-4 py-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">{suggestion.name}</div>
                  <div className="text-sm text-gray-500">{suggestion.district}</div>
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPartyColor(suggestion.party)}`}>
                  {suggestion.party}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 오류 메시지 */}
      {error && (
        <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <svg className="h-5 w-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <span className="text-red-700 text-sm">{error}</span>
          </div>
        </div>
      )}

      {/* 검색 결과 */}
      {searchResults.length > 0 && (
        <div className="mt-4">
          <div className="text-sm text-gray-600 mb-3">
            검색 결과: {searchResults.length}명의 정치인
          </div>
          
          <div className="space-y-2">
            {searchResults.map((result, index) => (
              <div
                key={index}
                onClick={() => handleResultClick(result)}
                className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center text-lg font-bold">
                      {result.name[0]}
                    </div>
                    <div>
                      <div className="font-semibold">{result.name}</div>
                      <div className="text-sm text-gray-500">
                        {result.info?.district || '비례대표'}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className={`px-3 py-1 text-sm font-medium rounded-full ${getPartyColor(result.info?.party_name || '무소속')}`}>
                      {result.info?.party_name || '무소속'}
                    </span>
                    <div className="text-xs text-gray-500 mt-1">
                      매칭도: {(result.match_score * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 검색 안내 */}
      {!query && !searchResults.length && (
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start">
            <svg className="h-5 w-5 text-blue-400 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="text-blue-700 text-sm">
              <div className="font-medium mb-1">정치인 검색 가이드</div>
              <ul className="space-y-1 text-xs">
                <li>• 22대 국회의원 이름만 검색 가능</li>
                <li>• 예시: "이재명", "한동훈", "조국"</li>
                <li>• 부분 검색 지원: "이재", "한동"</li>
                <li>• 정당명, 일반 키워드 검색 불가</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PoliticianSearch

