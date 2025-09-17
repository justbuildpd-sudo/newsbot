import { useState, useEffect, useCallback, useRef } from 'react'

/**
 * 최적화된 데이터 로딩 훅
 * 캐싱, 병렬 로딩, 에러 재시도 등 성능 최적화 기능 제공
 */
export const useOptimizedData = () => {
  const [data, setData] = useState({
    politicians: [],
    billScores: {},
    news: {},
    trends: null
  })
  const [loading, setLoading] = useState({
    politicians: true,
    billScores: true,
    news: true,
    trends: true
  })
  const [errors, setErrors] = useState({})
  
  // 캐시 관리
  const cache = useRef(new Map())
  const cacheTimestamps = useRef(new Map())
  
  // 캐시 TTL (밀리초)
  const CACHE_TTL = {
    politicians: 30 * 60 * 1000,  // 30분
    billScores: 15 * 60 * 1000,   // 15분
    news: 5 * 60 * 1000,          // 5분
    trends: 30 * 60 * 1000        // 30분
  }

  // 캐시 확인
  const getCachedData = useCallback((key) => {
    const cached = cache.current.get(key)
    const timestamp = cacheTimestamps.current.get(key)
    
    if (cached && timestamp) {
      const now = Date.now()
      const ttl = CACHE_TTL[key] || 5 * 60 * 1000
      
      if (now - timestamp < ttl) {
        return cached
      } else {
        // 만료된 캐시 삭제
        cache.current.delete(key)
        cacheTimestamps.current.delete(key)
      }
    }
    
    return null
  }, [])

  // 캐시 설정
  const setCachedData = useCallback((key, value) => {
    cache.current.set(key, value)
    cacheTimestamps.current.set(key, Date.now())
  }, [])

  // 병렬 API 호출 함수
  const fetchAllData = useCallback(async () => {
    const baseUrl = 'https://newsbot-backend-6j3p.onrender.com'
    
    // 캐시 확인
    const cachedPoliticians = getCachedData('politicians')
    const cachedBillScores = getCachedData('billScores')
    const cachedNews = getCachedData('news')
    const cachedTrends = getCachedData('trends')
    
    // 필요한 API 호출만 수행
    const promises = []
    const promiseKeys = []
    
    if (!cachedPoliticians) {
      promises.push(fetch(`${baseUrl}/api/assembly/members`))
      promiseKeys.push('politicians')
    } else {
      setData(prev => ({ ...prev, politicians: cachedPoliticians }))
      setLoading(prev => ({ ...prev, politicians: false }))
    }
    
    if (!cachedBillScores) {
      promises.push(fetch(`${baseUrl}/api/bills/scores`))
      promiseKeys.push('billScores')
    } else {
      setData(prev => ({ ...prev, billScores: cachedBillScores }))
      setLoading(prev => ({ ...prev, billScores: false }))
    }
    
    if (!cachedNews) {
      promises.push(fetch(`${baseUrl}/api/news/stats`))
      promiseKeys.push('news')
    } else {
      setData(prev => ({ ...prev, news: cachedNews }))
      setLoading(prev => ({ ...prev, news: false }))
    }
    
    if (!cachedTrends) {
      promises.push(fetch(`${baseUrl}/api/trends/chart`))
      promiseKeys.push('trends')
    } else {
      setData(prev => ({ ...prev, trends: cachedTrends }))
      setLoading(prev => ({ ...prev, trends: false }))
    }
    
    // 병렬 실행
    if (promises.length > 0) {
      try {
        const responses = await Promise.allSettled(promises)
        
        for (let i = 0; i < responses.length; i++) {
          const response = responses[i]
          const key = promiseKeys[i]
          
          if (response.status === 'fulfilled' && response.value.ok) {
            try {
              const jsonData = await response.value.json()
              
              if (jsonData.success) {
                let processedData
                
                switch (key) {
                  case 'politicians':
                    processedData = jsonData.data
                    break
                  case 'billScores':
                    processedData = jsonData.data
                    break
                  case 'news':
                    processedData = jsonData.data
                    break
                  case 'trends':
                    processedData = jsonData.data
                    break
                  default:
                    processedData = jsonData.data
                }
                
                // 데이터 설정 및 캐싱
                setData(prev => ({ ...prev, [key]: processedData }))
                setCachedData(key, processedData)
                
                console.log(`✅ ${key} 로드 완료 (${jsonData.cached ? '캐시' : '실시간'})`)
              } else {
                throw new Error(jsonData.error || 'API 응답 실패')
              }
            } catch (parseError) {
              console.error(`${key} JSON 파싱 오류:`, parseError)
              setErrors(prev => ({ ...prev, [key]: 'JSON 파싱 실패' }))
            }
          } else {
            const errorMsg = response.status === 'rejected' 
              ? response.reason.message 
              : `HTTP ${response.value.status}`
            
            console.error(`${key} API 오류:`, errorMsg)
            setErrors(prev => ({ ...prev, [key]: errorMsg }))
          }
          
          // 로딩 상태 업데이트
          setLoading(prev => ({ ...prev, [key]: false }))
        }
      } catch (error) {
        console.error('병렬 API 호출 오류:', error)
        
        // 모든 로딩 상태 해제
        setLoading({
          politicians: false,
          billScores: false,
          news: false,
          trends: false
        })
      }
    }
  }, [getCachedData, setCachedData])

  // 개별 데이터 새로고침
  const refreshData = useCallback(async (dataType) => {
    setLoading(prev => ({ ...prev, [dataType]: true }))
    setErrors(prev => ({ ...prev, [dataType]: null }))
    
    // 해당 캐시 삭제
    cache.current.delete(dataType)
    cacheTimestamps.current.delete(dataType)
    
    // 데이터 다시 로드
    await fetchAllData()
  }, [fetchAllData])

  // 전체 데이터 새로고침
  const refreshAllData = useCallback(async () => {
    // 모든 캐시 삭제
    cache.current.clear()
    cacheTimestamps.current.clear()
    
    // 로딩 상태 리셋
    setLoading({
      politicians: true,
      billScores: true,
      news: true,
      trends: true
    })
    
    setErrors({})
    
    await fetchAllData()
  }, [fetchAllData])

  // 초기 데이터 로드
  useEffect(() => {
    fetchAllData()
  }, [fetchAllData])

  // 캐시 정리 (5분마다)
  useEffect(() => {
    const cleanupInterval = setInterval(() => {
      const now = Date.now()
      const keysToDelete = []
      
      for (const [key, timestamp] of cacheTimestamps.current.entries()) {
        const ttl = CACHE_TTL[key] || 5 * 60 * 1000
        if (now - timestamp > ttl) {
          keysToDelete.push(key)
        }
      }
      
      keysToDelete.forEach(key => {
        cache.current.delete(key)
        cacheTimestamps.current.delete(key)
      })
      
      if (keysToDelete.length > 0) {
        console.log(`🗑️ 만료된 캐시 정리: ${keysToDelete.length}개`)
      }
    }, 5 * 60 * 1000)  // 5분마다
    
    return () => clearInterval(cleanupInterval)
  }, [])

  // 로딩 상태 계산
  const isLoading = Object.values(loading).some(Boolean)
  const hasErrors = Object.keys(errors).length > 0

  return {
    data,
    loading,
    errors,
    isLoading,
    hasErrors,
    refreshData,
    refreshAllData,
    cacheStats: {
      size: cache.current.size,
      keys: Array.from(cache.current.keys())
    }
  }
}

export default useOptimizedData
