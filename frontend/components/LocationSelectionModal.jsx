import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MapPinIcon, 
  BuildingOfficeIcon,
  HomeModernIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

const LocationSelectionModal = ({ isOpen, onClose, searchTerm, options, onSelect }) => {
  if (!isOpen || !options) return null;

  const getLevelIcon = (level) => {
    switch (level) {
      case 'sido':
        return <BuildingOfficeIcon className="h-5 w-5 text-blue-500" />;
      case 'sigungu':
        return <BuildingOfficeIcon className="h-5 w-5 text-green-500" />;
      case 'gu':
        return <HomeModernIcon className="h-5 w-5 text-purple-500" />;
      case 'dong':
        return <MapPinIcon className="h-5 w-5 text-orange-500" />;
      default:
        return <MapPinIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getLevelDescription = (level) => {
    switch (level) {
      case 'sido':
        return '광역단체장급 (시장/도지사)';
      case 'sigungu':
        return '기초단체장급 (시장/군수)';
      case 'gu':
        return '구청장급 (구청장)';
      case 'dong':
        return '동장급 (동장)';
      case 'station':
        return '교통 중심지 (역 주변)';
      case 'landmark':
        return '랜드마크 (특별 지역)';
      default:
        return '기타 지역';
    }
  };

  const getLevelColor = (level) => {
    switch (level) {
      case 'sido':
        return 'bg-blue-50 border-blue-200 hover:bg-blue-100';
      case 'sigungu':
        return 'bg-green-50 border-green-200 hover:bg-green-100';
      case 'gu':
        return 'bg-purple-50 border-purple-200 hover:bg-purple-100';
      case 'dong':
        return 'bg-orange-50 border-orange-200 hover:bg-orange-100';
      default:
        return 'bg-gray-50 border-gray-200 hover:bg-gray-100';
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white rounded-lg max-w-lg w-full max-h-[80vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="p-6">
            {/* 헤더 */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-800">
                  🔍 지역 선택
                </h2>
                <p className="text-gray-600 mt-1">
                  '<span className="font-medium text-blue-600">{searchTerm}</span>'에 해당하는 지역을 선택해주세요
                </p>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            {/* 선택 옵션 */}
            <div className="space-y-3">
              {options.map((option, index) => (
                <motion.button
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => onSelect(option)}
                  className={`w-full p-4 rounded-lg border-2 text-left transition-all ${getLevelColor(option.level)}`}
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-1">
                      {getLevelIcon(option.level)}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold text-gray-800">
                          {option.description || option.key}
                        </h3>
                        <span className="text-xs bg-white px-2 py-1 rounded-full text-gray-600 border">
                          {getLevelDescription(option.level)}
                        </span>
                      </div>
                      
                      {/* 추가 정보 */}
                      {option.data && (
                        <div className="text-sm text-gray-600 space-y-1">
                          {option.data.population && (
                            <div>
                              👥 인구: {option.data.population.toLocaleString()}명
                            </div>
                          )}
                          {option.data.elected_position && (
                            <div>
                              🏛️ 선출직: {option.data.elected_position}
                            </div>
                          )}
                          {option.data.parent_sido && (
                            <div>
                              📍 상위지역: {option.data.parent_sido}
                            </div>
                          )}
                        </div>
                      )}
                      
                      {/* 하위 지역 미리보기 */}
                      {option.data && option.data.districts && (
                        <div className="mt-2 text-xs text-gray-500">
                          📋 하위지역: {option.data.districts.slice(0, 3).join(', ')}
                          {option.data.districts.length > 3 && ` 외 ${option.data.districts.length - 3}개`}
                        </div>
                      )}
                      
                      {option.data && option.data.dongs && (
                        <div className="mt-2 text-xs text-gray-500">
                          🏘️ 포함동: {option.data.dongs.slice(0, 3).join(', ')}
                          {option.data.dongs.length > 3 && ` 외 ${option.data.dongs.length - 3}개`}
                        </div>
                      )}
                    </div>
                  </div>
                </motion.button>
              ))}
            </div>

            {/* 안내 메시지 */}
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <div className="flex items-start space-x-2">
                <div className="text-blue-500 mt-0.5">
                  💡
                </div>
                <div className="text-sm text-blue-800">
                  <p className="font-medium mb-1">선택 가이드:</p>
                  <ul className="space-y-1 text-blue-700">
                    <li>• <strong>광역단체장급</strong>: 시장/도지사 정보</li>
                    <li>• <strong>기초단체장급</strong>: 시장/군수 정보</li>
                    <li>• <strong>구청장급</strong>: 구청장 정보</li>
                    <li>• <strong>동장급</strong>: 동장 + 해당 국회의원 정보</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default LocationSelectionModal;
