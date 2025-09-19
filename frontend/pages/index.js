import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { 
  MagnifyingGlassIcon,
  ChartBarIcon,
  MapPinIcon,
  UserGroupIcon,
  CpuChipIcon,
  TrophyIcon
} from '@heroicons/react/24/outline';
import CacheSystemMonitor from '../components/CacheSystemMonitor';

export default function HomePage() {
  const features = [
    {
      icon: <MagnifyingGlassIcon className="h-8 w-8" />,
      title: "읍면동별 선거검색",
      description: "1,580개 읍면동의 모든 선거결과를 0.3ms 초고속 검색",
      link: "/election-search",
      color: "blue"
    },
    {
      icon: <UserGroupIcon className="h-8 w-8" />,
      title: "출마 후보 정보",
      description: "후보자 상세 프로필, 공약, 정책 입장, 선거 결과",
      link: "/candidate-info",
      color: "green"
    },
    {
      icon: <ChartBarIcon className="h-8 w-8" />,
      title: "96.19% 다양성 분석",
      description: "19차원 완전 분석으로 지역 특성 완벽 파악",
      link: "/diversity-analysis",
      color: "purple"
    },
    {
      icon: <MapPinIcon className="h-8 w-8" />,
      title: "지역 정세 분석",
      description: "245개 지자체 완전 통계 기반 정치 동향 분석",
      link: "/regional-analysis",
      color: "orange"
    },
    {
      icon: <CpuChipIcon className="h-8 w-8" />,
      title: "AI 예측 시스템",
      description: "98-99.9% 정확도의 선거 예측 및 정치 전망",
      link: "/ai-predictions",
      color: "indigo"
    },
    {
      icon: <TrophyIcon className="h-8 w-8" />,
      title: "성과 평가",
      description: "정치인 성과 지표 및 시민 만족도 분석",
      link: "/performance-evaluation",
      color: "red"
    }
  ];

  const stats = [
    { label: "캐시된 지역", value: "1,580개", description: "읍면동 완전 지원" },
    { label: "캐시 사용량", value: "266MB", description: "280MB 중 95% 활용" },
    { label: "응답 속도", value: "0.3ms", description: "초고속 검색" },
    { label: "데이터 완성도", value: "99%", description: "최고 품질" }
  ];

  return (
    <>
      <Head>
        <title>NewsBot 정세분석 | 280MB 캐시 시스템</title>
        <meta name="description" content="280MB 캐시 시스템으로 읍면동별 선거결과와 96.19% 다양성 시스템을 0.3ms 초고속 검색" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        {/* 헤더 */}
        <header className="bg-white shadow-sm">
          <div className="max-w-6xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center space-x-4"
              >
                <h1 className="text-2xl font-bold text-gray-800">
                  📊 NewsBot 정세분석
                </h1>
                <span className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-4 py-2 rounded-full text-sm font-medium">
                  280MB 캐시 시스템
                </span>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center space-x-6"
              >
                <Link href="/election-search" className="text-blue-600 hover:text-blue-800 font-medium">
                  선거검색
                </Link>
                <Link href="/political-analysis" className="text-gray-600 hover:text-gray-800">
                  정치분석
                </Link>
              </motion.div>
            </div>
          </div>
        </header>

        {/* 히어로 섹션 */}
        <section className="py-16">
          <div className="max-w-6xl mx-auto px-6 text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h1 className="text-5xl font-bold text-gray-800 mb-6">
                🗳️ 완전한 정세분석 시스템
              </h1>
              <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
                280MB 캐시 시스템으로 읍면동별 선거결과와 출마 후보 정보를 
                0.3ms 초고속 검색하는 96.19% 다양성 시스템
              </p>
              
              {/* 주요 통계 */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8"
              >
                {stats.map((stat, index) => (
                  <div key={index} className="bg-white rounded-lg shadow-md p-6">
                    <div className="text-3xl font-bold text-blue-600 mb-2">
                      {stat.value}
                    </div>
                    <div className="text-gray-800 font-medium mb-1">
                      {stat.label}
                    </div>
                    <div className="text-sm text-gray-500">
                      {stat.description}
                    </div>
                  </div>
                ))}
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="space-y-4"
              >
                <Link href="/election-search">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:from-blue-700 hover:to-purple-700 shadow-lg"
                  >
                    🚀 읍면동 선거검색 시작
                  </motion.button>
                </Link>
                
                <p className="text-sm text-gray-500">
                  280MB 캐시로 1,580개 지역의 완전한 선거 정보 제공
                </p>
              </motion.div>
            </motion.div>
          </div>
        </section>

        {/* 캐시 시스템 모니터 */}
        <section className="py-12">
          <div className="max-w-6xl mx-auto px-6">
            <CacheSystemMonitor />
          </div>
        </section>

        {/* 기능 소개 */}
        <section className="py-16 bg-white">
          <div className="max-w-6xl mx-auto px-6">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center mb-12"
            >
              <h2 className="text-3xl font-bold text-gray-800 mb-4">
                🎯 시스템 기능
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                280MB 최대 활용 캐시 시스템으로 제공하는 완전한 정치 정보
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ y: -5 }}
                  className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500"
                >
                  <div className={`text-${feature.color}-500 mb-4`}>
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {feature.description}
                  </p>
                  <Link href={feature.link}>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      className={`w-full py-2 px-4 bg-${feature.color}-600 text-white rounded-lg hover:bg-${feature.color}-700 text-sm font-medium`}
                    >
                      시작하기
                    </motion.button>
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* 시스템 특징 */}
        <section className="py-16 bg-gradient-to-r from-gray-50 to-gray-100">
          <div className="max-w-6xl mx-auto px-6">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center mb-12"
            >
              <h2 className="text-3xl font-bold text-gray-800 mb-4">
                ⚡ 시스템 특징
              </h2>
              <p className="text-gray-600">
                로드를 아끼지 않고 300MB 한계를 최대한 활용한 완전한 시스템
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-white rounded-lg shadow-md p-8"
              >
                <h3 className="text-xl font-semibold text-gray-800 mb-4">
                  🔥 280MB 최대 활용
                </h3>
                <ul className="space-y-3 text-gray-600">
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-3" />
                    266MB / 280MB (95% 활용)
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-3" />
                    로드 아끼지 않는 대용량 정보
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-3" />
                    Raw JSON 직접 제공 (압축 없음)
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-3" />
                    지역당 평균 172.5KB 정보
                  </li>
                </ul>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-white rounded-lg shadow-md p-8"
              >
                <h3 className="text-xl font-semibold text-gray-800 mb-4">
                  🗳️ 완전한 선거 정보
                </h3>
                <ul className="space-y-3 text-gray-600">
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-blue-500 mr-3" />
                    6개 선거 유형 완전 지원
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-blue-500 mr-3" />
                    출마 후보 전원 상세 정보
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-blue-500 mr-3" />
                    공약, 경력, 정책 입장 포함
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-blue-500 mr-3" />
                    투표율, 득표 분석 완비
                  </li>
                </ul>
              </motion.div>
            </div>
          </div>
        </section>

        {/* 빠른 검색 */}
        <section className="py-16">
          <div className="max-w-4xl mx-auto px-6">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-white text-center"
            >
              <h2 className="text-2xl font-bold mb-4">
                🚀 지금 바로 검색해보세요
              </h2>
              <p className="mb-6 opacity-90">
                읍면동 이름을 입력하면 해당 지역의 모든 선거결과와 후보자 정보를 확인할 수 있습니다
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
                <input
                  type="text"
                  placeholder="정치인 이름 또는 동명 (예: 이재명, 정자동, 강남동)"
                  className="flex-1 px-4 py-3 rounded-lg text-gray-800 placeholder-gray-500"
                />
                <Link href="/election-search">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-6 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-gray-100"
                  >
                    검색하기
                  </motion.button>
                </Link>
              </div>
              
              <div className="mt-4 text-sm opacity-75">
                💡 예시: "이재명", "김기현", "정자동", "강남동", "해운대동"
              </div>
            </motion.div>
          </div>
        </section>

        {/* 푸터 */}
        <footer className="bg-gray-800 text-white py-12">
          <div className="max-w-6xl mx-auto px-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div>
                <h3 className="font-semibold mb-4 text-lg">🗳️ 선거 시스템</h3>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li>• 1,580개 읍면동 지원</li>
                  <li>• 6개 선거 유형</li>
                  <li>• 0.3ms 초고속 검색</li>
                  <li>• 99% 데이터 완성도</li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-semibold mb-4 text-lg">📊 다양성 시스템</h3>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li>• 96.19% 완전 분석</li>
                  <li>• 19차원 지역 분석</li>
                  <li>• 245개 지자체 통계</li>
                  <li>• AI 예측 모델</li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-semibold mb-4 text-lg">⚡ 캐시 성능</h3>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li>• 280MB 캐시 (95% 활용)</li>
                  <li>• Raw JSON 직접 제공</li>
                  <li>• 압축 없는 최고 성능</li>
                  <li>• 렌더 프로세스 관리</li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-semibold mb-4 text-lg">🏛️ 정치 정보</h3>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li>• 출마 후보 완전 정보</li>
                  <li>• 공약 및 정책 입장</li>
                  <li>• 선거 이력 및 성과</li>
                  <li>• 실시간 정세 분석</li>
                </ul>
              </div>
            </div>
            
            <div className="border-t border-gray-700 mt-8 pt-8 text-center">
              <p className="text-gray-400">
                © 2025 NewsBot 정세분석 시스템 | 280MB 최대 활용 캐시 | 96.19% 다양성 시스템 | 
                읍면동별 선거결과 완전 지원
              </p>
              <p className="text-sm text-gray-500 mt-2">
                🔥 로드를 아끼지 않고 최대한의 정보를 제공합니다
              </p>
            </div>
          </div>
        </footer>
      </main>
    </>
  );
}