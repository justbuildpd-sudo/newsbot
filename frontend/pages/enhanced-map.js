import { useState, useEffect } from 'react'
import Head from 'next/head'
import HexGridMapWidget from '../components/HexGridMapWidget'
import PoliticianDetailModal from '../components/PoliticianDetailModal'

export default function EnhancedMapPage() {
  const [politicians, setPoliticians] = useState([])
  const [selectedPolitician, setSelectedPolitician] = useState(null)
  const [selectedDistrict, setSelectedDistrict] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [stats, setStats] = useState({})

  useEffect(() => {
    loadPoliticiansData()
  }, [])

  const loadPoliticiansData = async () => {
    try {
      setLoading(true)
      
      // 정치인 데이터 로드
      const response = await fetch('/api/politicians')
      if (response.ok) {
        const data = await response.json()
        setPoliticians(data.politicians || data || [])
        setStats(data.stats || {})
      } else {
        // 로컬 데이터 로드 시도
        const localData = await loadLocalData()
        setPoliticians(localData)
      }
      
    } catch (err) {
      console.error('데이터 로드 실패:', err)
      setError('데이터를 불러오는 중 오류가 발생했습니다.')
      
      // 샘플 데이터로 대체
      const sampleData = generateSampleData()
      setPoliticians(sampleData)
      
    } finally {
      setLoading(false)
    }
  }

  const loadLocalData = async () => {
    // 로컬 JSON 파일에서 데이터 로드
    try {
      const response = await fetch('/data/politicians.json')
      if (response.ok) {
        const data = await response.json()
        return Array.isArray(data) ? data : []
      }
    } catch (error) {
      console.error('로컬 데이터 로드 실패:', error)
    }
    return []
  }

  const generateSampleData = () => {
    return [
      {
        name: '김철수',
        party: '더불어민주당',
        district: '서울특별시 강남구갑',
        region: '서울특별시',
        phone: '02-788-1234',
        email: 'kim@assembly.go.kr',
        office: '국회의사당 본관 123호'
      },
      {
        name: '이영희',
        party: '국민의힘',
        district: '부산광역시 해운대구을',
        region: '부산광역시',
        phone: '051-123-4567',
        email: 'lee@assembly.go.kr',
        office: '국회의사당 본관 456호'
      },
      {
        name: '박민수',
        party: '정의당',
        district: '경기도 수원시갑',
        region: '경기도',
        phone: '031-234-5678',
        email: 'park@assembly.go.kr',
        office: '국회의사당 본관 789호'
      },
      {
        name: '최지영',
        party: '국민의당',
        district: '인천광역시 남동구갑',
        region: '인천광역시',
        phone: '032-345-6789',
        email: 'choi@assembly.go.kr',
        office: '국회의사당 본관 321호'
      },
      {
        name: '정한국',
        party: '개혁신당',
        district: '대구광역시 중구남구',
        region: '대구광역시',
        phone: '053-456-7890',
        email: 'jung@assembly.go.kr',
        office: '국회의사당 본관 654호'
      }
    ]
  }

  const handlePoliticianSelect = (name, politician) => {
    // 정치인 선택 시 상세 정보 모달 열기
    const selectedPol = politician || politicians.find(p => p.name === name)
    setSelectedPolitician(selectedPol)
  }

  const handleDistrictSelect = (districtKey, members) => {
    // 선거구 선택 시 해당 지역 정보 표시
    setSelectedDistrict({
      key: districtKey,
      members: members || []
    })
    console.log('선택된 선거구:', districtKey, members)
  }

  const closeModal = () => {
    setSelectedPolitician(null)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">정치인 데이터를 불러오는 중...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">⚠️</div>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadPoliticiansData}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            다시 시도
          </button>
        </div>
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>선거구 지도 - 정치인 정보 시스템</title>
        <meta name="description" content="대한민국 선거구별 정치인 정보를 직관적인 육각형 그리드 지도로 확인하세요" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen bg-gray-100">
        {/* 헤더 */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-gray-900">선거구 지도</h1>
                <span className="ml-3 px-2 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full">
                  Enhanced
                </span>
              </div>
              
              {/* 통계 정보 */}
              <div className="flex items-center space-x-6 text-sm text-gray-600">
                <div className="text-center">
                  <div className="font-bold text-lg text-gray-900">{politicians.length}</div>
                  <div>총 정치인</div>
                </div>
                <div className="text-center">
                  <div className="font-bold text-lg text-gray-900">
                    {new Set(politicians.map(p => p.district)).size}
                  </div>
                  <div>선거구</div>
                </div>
                <div className="text-center">
                  <div className="font-bold text-lg text-gray-900">
                    {new Set(politicians.map(p => p.party)).size}
                  </div>
                  <div>정당</div>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* 메인 콘텐츠 */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            
            {/* 지도 영역 */}
            <div className="lg:col-span-3">
              <div className="bg-white rounded-lg shadow-md">
                <HexGridMapWidget
                  politicians={politicians}
                  onSelectPolitician={handlePoliticianSelect}
                  onDistrictSelect={handleDistrictSelect}
                />
              </div>
            </div>

            {/* 사이드바 */}
            <div className="lg:col-span-1 space-y-6">
              
              {/* 선택된 선거구 정보 */}
              {selectedDistrict && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold mb-4">선택된 선거구</h3>
                  <div className="space-y-3">
                    <div className="text-sm text-gray-600">
                      선거구: {selectedDistrict.members[0]?.district || selectedDistrict.key}
                    </div>
                    <div className="text-sm text-gray-600">
                      의원 수: {selectedDistrict.members.length}명
                    </div>
                    
                    {selectedDistrict.members.map((member, index) => (
                      <div 
                        key={index}
                        className="border rounded p-3 hover:bg-gray-50 cursor-pointer"
                        onClick={() => handlePoliticianSelect(member.name, member)}
                      >
                        <div className="font-medium">{member.name}</div>
                        <div className="text-sm text-gray-500">{member.party}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 최근 활동 */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4">시스템 정보</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">데이터 업데이트:</span>
                    <span className="font-medium">{new Date().toLocaleDateString('ko-KR')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">지도 유형:</span>
                    <span className="font-medium">육각형 그리드</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">검색 지원:</span>
                    <span className="font-medium text-green-600">활성화</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">실시간 연동:</span>
                    <span className="font-medium text-blue-600">지원</span>
                  </div>
                </div>
              </div>

              {/* 도움말 */}
              <div className="bg-blue-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-blue-900 mb-4">사용 방법</h3>
                <div className="space-y-2 text-sm text-blue-800">
                  <div className="flex items-start">
                    <span className="mr-2">🔍</span>
                    <span>검색창에서 정치인, 정당, 선거구명으로 검색</span>
                  </div>
                  <div className="flex items-start">
                    <span className="mr-2">🗺️</span>
                    <span>지도의 육각형을 클릭하여 해당 지역 의원 확인</span>
                  </div>
                  <div className="flex items-start">
                    <span className="mr-2">👤</span>
                    <span>의원 이름을 클릭하면 상세 정보 조회</span>
                  </div>
                  <div className="flex items-start">
                    <span className="mr-2">🎨</span>
                    <span>색상은 정당별로 구분되어 표시</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>

        {/* 정치인 상세 정보 모달 */}
        <PoliticianDetailModal
          politician={selectedPolitician}
          isOpen={!!selectedPolitician}
          onClose={closeModal}
        />

        {/* 푸터 */}
        <footer className="bg-white border-t mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center text-gray-500 text-sm">
              <p>© 2025 정치인 정보 시스템. 선거관리위원회 및 국회 공개 데이터 활용</p>
              <p className="mt-2">
                데이터 출처: 국회사무처, 선거관리위원회 | 
                마지막 업데이트: {new Date().toLocaleDateString('ko-KR')}
              </p>
            </div>
          </div>
        </footer>
      </div>
    </>
  )
}
