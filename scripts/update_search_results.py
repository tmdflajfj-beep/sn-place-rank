#!/usr/bin/env python3
"""
자동 업데이트 스크립트
매일 오후 2시에 GitHub Actions에 의해 실행됩니다.
모든 등록된 업체와 키워드 조합에 대해 검색을 실행하고 결과를 저장합니다.
"""

import os
import sys
import logging
import time
from datetime import datetime

# 모듈 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from modules.search_engine import NaverPlaceSearchEngine
from modules.data_manager import DataManager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(current_dir, 'update.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    모든 등록된 업체와 키워드 조합에 대해 검색을 실행하고 결과를 저장합니다.
    """
    logger.info("자동 업데이트 시작")
    start_time = time.time()
    
    # 데이터 관리자 초기화
    data_dir = os.path.join(parent_dir, 'data')
    data_manager = DataManager(data_dir)
    
    # 업체 및 키워드 목록 조회
    companies = data_manager.get_companies()
    keywords = data_manager.get_keywords()
    
    if companies.empty:
        logger.warning("등록된 업체가 없습니다.")
        return
    
    if keywords.empty:
        logger.warning("등록된 키워드가 없습니다.")
        return
    
    # 검색 엔진 초기화
    search_engine = NaverPlaceSearchEngine(headless=True)
    
    # 모든 조합에 대해 검색 실행
    total_combinations = len(companies) * len(keywords)
    completed = 0
    success = 0
    failed = 0
    
    logger.info(f"총 {total_combinations}개의 검색 조합이 있습니다.")
    
    for _, company in companies.iterrows():
        company_id = company['id']
        company_name = company['name']
        
        for _, keyword in keywords.iterrows():
            keyword_id = keyword['id']
            keyword_text = keyword['text']
            
            logger.info(f"검색 중: '{keyword_text}'에서 '{company_name}'")
            
            try:
                # 검색 실행
                result = search_engine.search(keyword_text, company_name)
                
                # 검색 결과 저장
                if result["success"]:
                    data_manager.add_search_result(
                        company_id=company_id,
                        keyword_id=keyword_id,
                        rank=result["rank"],
                        search_time=result["search_time"]
                    )
                    logger.info(f"검색 성공: {result['message']}")
                    success += 1
                else:
                    logger.warning(f"검색 실패: {result['message']}")
                    # 순위를 찾지 못한 경우에도 결과 저장 (-1로 표시)
                    data_manager.add_search_result(
                        company_id=company_id,
                        keyword_id=keyword_id,
                        rank=-1,
                        search_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    failed += 1
                
            except Exception as e:
                logger.error(f"오류 발생: {type(e).__name__} - {e}")
                failed += 1
            
            # 진행 상황 업데이트
            completed += 1
            logger.info(f"진행 상황: {completed}/{total_combinations} ({completed/total_combinations*100:.1f}%)")
            
            # 네이버 서버 부하 방지를 위한 딜레이
            time.sleep(3)
    
    # 결과 요약
    elapsed_time = time.time() - start_time
    logger.info(f"자동 업데이트 완료: {elapsed_time:.1f}초 소요")
    logger.info(f"성공: {success}, 실패: {failed}, 총 검색: {completed}")

if __name__ == "__main__":
    main()
