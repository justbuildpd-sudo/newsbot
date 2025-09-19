import { useState, useEffect } from 'react'

const PoliticianDetailModal = ({ politician, isOpen, onClose }) => {
  const [loading, setLoading] = useState(false)
  const [detailData, setDetailData] = useState(null)
  const [activeTab, setActiveTab] = useState('basic')

  useEffect(() => {
    if (isOpen && politician) {
      fetchDetailData()
    }
  }, [isOpen, politician])

  const fetchDetailData = async () => {
    setLoading(true)
    try {
      // 추가 상세 정보 API 호출 (선택사항)
      const response = await fetch(`/api/politicians/${encodeURIComponent(politician.name)}`)
      if (response.ok) {
        const data = await response.json()
        setDetailData(data)
      }
    } catch (error) {
      console.error('상세 정보 로드 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  if (!isOpen || !politician) return null

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={handleOverlayClick}
    >
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden shadow-2xl">
        {/* 헤더 */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 relative">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-white hover:text-gray-200 text-2xl font-bold"
          >
            ×
          </button>
          
          <div className="flex items-start space-x-4">
            {/* 프로필 이미지 영역 */}
            <div className="w-24 h-24 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
              <span className="text-3xl font-bold text-white">
                {politician.name?.charAt(0) || '?'}
              </span>
            </div>
            
            {/* 기본 정보 */}
            <div className="flex-1">
              <h2 className="text-2xl font-bold mb-2">{politician.name}</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-white rounded-full mr-2"></span>
                  {politician.party || '정당 정보 없음'}
                </div>
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-white rounded-full mr-2"></span>
                  {politician.district || '선거구 정보 없음'}
                </div>
                {politician.phone && (
                  <div className="flex items-center">
                    <span className="w-2 h-2 bg-white rounded-full mr-2"></span>
                    📞 {politician.phone}
                  </div>
                )}
                {politician.email && (
                  <div className="flex items-center">
                    <span className="w-2 h-2 bg-white rounded-full mr-2"></span>
                    ✉️ {politician.email}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* 탭 네비게이션 */}
        <div className="border-b border-gray-200">
          <nav className="flex">
            <button
              onClick={() => setActiveTab('basic')}
              className={`px-6 py-3 text-sm font-medium ${
                activeTab === 'basic'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              기본 정보
            </button>
            <button
              onClick={() => setActiveTab('activity')}
              className={`px-6 py-3 text-sm font-medium ${
                activeTab === 'activity'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              의정 활동
            </button>
            <button
              onClick={() => setActiveTab('news')}
              className={`px-6 py-3 text-sm font-medium ${
                activeTab === 'news'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              관련 뉴스
            </button>
            <button
              onClick={() => setActiveTab('contact')}
              className={`px-6 py-3 text-sm font-medium ${
                activeTab === 'contact'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              연락처
            </button>
          </nav>
        </div>

        {/* 탭 콘텐츠 */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <>
              {/* 기본 정보 탭 */}
              {activeTab === 'basic' && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-gray-800">개인 정보</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-600">이름:</span>
                          <span className="font-medium">{politician.name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">소속 정당:</span>
                          <span className="font-medium">{politician.party || '-'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">선거구:</span>
                          <span className="font-medium">{politician.district || '-'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">지역:</span>
                          <span className="font-medium">{politician.region || '-'}</span>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-gray-800">의정 정보</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-600">당선 횟수:</span>
                          <span className="font-medium">{detailData?.electionCount || '-'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">의정 경력:</span>
                          <span className="font-medium">{detailData?.experience || '-'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">주요 위원회:</span>
                          <span className="font-medium">{detailData?.committee || '-'}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* 프로필 요약 */}
                  {detailData?.profile && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800 mb-3">프로필</h3>
                      <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-gray-700 leading-relaxed">
                          {detailData.profile}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 의정 활동 탭 */}
              {activeTab === 'activity' && (
                <div className="space-y-6">
                  <h3 className="text-lg font-semibold text-gray-800">최근 의정 활동</h3>
                  
                  {/* 법안 발의 */}
                  <div>
                    <h4 className="font-medium text-gray-700 mb-3">주요 법안 발의</h4>
                    <div className="space-y-2">
                      {detailData?.bills?.length > 0 ? (
                        detailData.bills.slice(0, 5).map((bill, index) => (
                          <div key={index} className="border-l-4 border-blue-200 pl-4 py-2">
                            <div className="font-medium text-sm">{bill.title}</div>
                            <div className="text-xs text-gray-500">{bill.date}</div>
                          </div>
                        ))
                      ) : (
                        <p className="text-gray-500 text-sm">법안 발의 정보가 없습니다.</p>
                      )}
                    </div>
                  </div>

                  {/* 국정감사 */}
                  <div>
                    <h4 className="font-medium text-gray-700 mb-3">국정감사 활동</h4>
                    <div className="space-y-2">
                      {detailData?.inspections?.length > 0 ? (
                        detailData.inspections.slice(0, 3).map((inspection, index) => (
                          <div key={index} className="border-l-4 border-green-200 pl-4 py-2">
                            <div className="font-medium text-sm">{inspection.title}</div>
                            <div className="text-xs text-gray-500">{inspection.date}</div>
                          </div>
                        ))
                      ) : (
                        <p className="text-gray-500 text-sm">국정감사 활동 정보가 없습니다.</p>
                      )}
                    </div>
                  </div>

                  {/* 통계 */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-blue-50 rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {detailData?.stats?.billCount || 0}
                      </div>
                      <div className="text-sm text-gray-600">법안 발의</div>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {detailData?.stats?.questionCount || 0}
                      </div>
                      <div className="text-sm text-gray-600">국정감사</div>
                    </div>
                    <div className="bg-yellow-50 rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-yellow-600">
                        {detailData?.stats?.attendanceRate || 0}%
                      </div>
                      <div className="text-sm text-gray-600">출석률</div>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {detailData?.stats?.committeeCount || 0}
                      </div>
                      <div className="text-sm text-gray-600">위원회</div>
                    </div>
                  </div>
                </div>
              )}

              {/* 관련 뉴스 탭 */}
              {activeTab === 'news' && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-800">관련 뉴스</h3>
                  {detailData?.news?.length > 0 ? (
                    detailData.news.map((article, index) => (
                      <div key={index} className="border rounded-lg p-4 hover:bg-gray-50">
                        <h4 className="font-medium text-gray-800 mb-2">{article.title}</h4>
                        <p className="text-sm text-gray-600 mb-2">{article.summary}</p>
                        <div className="flex justify-between items-center text-xs text-gray-500">
                          <span>{article.source}</span>
                          <span>{article.date}</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-gray-500">관련 뉴스를 불러오는 중...</p>
                    </div>
                  )}
                </div>
              )}

              {/* 연락처 탭 */}
              {activeTab === 'contact' && (
                <div className="space-y-6">
                  <h3 className="text-lg font-semibold text-gray-800">연락처 정보</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h4 className="font-medium text-gray-700">국회 사무실</h4>
                      <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                        {politician.office && (
                          <div className="flex items-center">
                            <span className="text-gray-600 mr-3">🏢</span>
                            <span>{politician.office}</span>
                          </div>
                        )}
                        {politician.phone && (
                          <div className="flex items-center">
                            <span className="text-gray-600 mr-3">📞</span>
                            <a href={`tel:${politician.phone}`} className="text-blue-600 hover:underline">
                              {politician.phone}
                            </a>
                          </div>
                        )}
                        {politician.email && (
                          <div className="flex items-center">
                            <span className="text-gray-600 mr-3">✉️</span>
                            <a href={`mailto:${politician.email}`} className="text-blue-600 hover:underline">
                              {politician.email}
                            </a>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h4 className="font-medium text-gray-700">지역구 사무실</h4>
                      <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                        {detailData?.localOffice ? (
                          <>
                            <div className="flex items-start">
                              <span className="text-gray-600 mr-3 mt-1">🏢</span>
                              <span>{detailData.localOffice.address}</span>
                            </div>
                            <div className="flex items-center">
                              <span className="text-gray-600 mr-3">📞</span>
                              <span>{detailData.localOffice.phone}</span>
                            </div>
                          </>
                        ) : (
                          <p className="text-gray-500 text-sm">지역구 사무실 정보가 없습니다.</p>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* 소셜 미디어 */}
                  {detailData?.socialMedia && (
                    <div>
                      <h4 className="font-medium text-gray-700 mb-3">소셜 미디어</h4>
                      <div className="flex space-x-4">
                        {detailData.socialMedia.facebook && (
                          <a 
                            href={detailData.socialMedia.facebook}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800"
                          >
                            Facebook
                          </a>
                        )}
                        {detailData.socialMedia.twitter && (
                          <a 
                            href={detailData.socialMedia.twitter}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-400 hover:text-blue-600"
                          >
                            Twitter
                          </a>
                        )}
                        {detailData.socialMedia.instagram && (
                          <a 
                            href={detailData.socialMedia.instagram}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-pink-600 hover:text-pink-800"
                          >
                            Instagram
                          </a>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        {/* 푸터 */}
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-500">
              마지막 업데이트: {new Date().toLocaleDateString('ko-KR')}
            </div>
            <div className="space-x-2">
              <button
                onClick={onClose}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-colors"
              >
                닫기
              </button>
              <button
                onClick={() => window.open(`https://www.assembly.go.kr/portal/main/main.do`, '_blank')}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                국회 홈페이지
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PoliticianDetailModal
