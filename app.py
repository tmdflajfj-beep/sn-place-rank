import streamlit as st
import pandas as pd
import os
import sys
import logging
from datetime import datetime

# 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.search_engine import NaverPlaceSearchEngine
from modules.data_manager import DataManager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 데이터 관리자 초기화
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
data_manager = DataManager(data_dir)

def run_search(keyword, shop_name):
    """
    네이버 플레이스 검색 실행
    
    Args:
        keyword (str): 검색 키워드
        shop_name (str): 상호명
        
    Returns:
        dict: 검색 결과
    """
    st.info(f"'{keyword}'에서 '{shop_name}' 검색 중... 잠시만 기다려주세요.")
    
    # 검색 엔진 초기화 및 검색 실행
    search_engine = NaverPlaceSearchEngine()
    result = search_engine.search(keyword, shop_name)
    
    # 검색 결과 저장
    if result["success"]:
        # 회사와 키워드 추가 또는 조회
        company_id = data_manager.add_company(shop_name)
        keyword_id = data_manager.add_keyword(keyword)
        
        # 검색 결과 저장
        data_manager.add_search_result(
            company_id=company_id,
            keyword_id=keyword_id,
            rank=result["rank"],
            search_time=result["search_time"]
        )
    
    return result

def main():
    st.title("네이버 플레이스 순위 검색")
    
    # 사이드바 메뉴
    st.sidebar.title("메뉴")
    menu = st.sidebar.radio(
        "선택하세요:",
        ["실시간 검색", "업체 관리", "검색 기록", "도움말"]
    )
    
    if menu == "실시간 검색":
        st.header("실시간 검색")
        
        # 검색 폼
        with st.form("search_form"):
            keyword = st.text_input("검색어 (예: 의정부 미용실)", placeholder="의정부 미용실")
            shop_name = st.text_input("상호명 (예: 준오헤어 의정부역점)", placeholder="준오헤어 의정부역점")
            
            submitted = st.form_submit_button("검색")
            
            if submitted and keyword and shop_name:
                result = run_search(keyword, shop_name)
                
                if result["success"]:
                    st.success(result["message"])
                else:
                    st.error(result["message"])
        
        # 최근 검색 결과 표시
        st.subheader("최근 검색 결과")
        results = data_manager.get_search_results()
        
        if not results.empty:
            # 최신 결과가 위에 오도록 정렬
            results = results.sort_values(by='search_time', ascending=False).head(10)
            
            # 회사명과 키워드 텍스트 추가
            results['company_name'] = results['company_id'].apply(data_manager.get_company_name)
            results['keyword_text'] = results['keyword_id'].apply(data_manager.get_keyword_text)
            
            # 표시할 열 선택 및 순서 변경
            display_results = results[['search_time', 'keyword_text', 'company_name', 'rank']]
            display_results.columns = ['검색 시간', '검색어', '상호명', '순위']
            
            st.dataframe(display_results)
        else:
            st.info("검색 결과가 없습니다.")
    
    elif menu == "업체 관리":
        st.header("업체 관리")
        
        # 업체 목록 표시
        companies = data_manager.get_companies()
        
        if not companies.empty:
            st.subheader("등록된 업체 목록")
            
            # 표시할 열 선택 및 순서 변경
            display_companies = companies[['id', 'name', 'created_at']]
            display_companies.columns = ['ID', '상호명', '등록일']
            
            st.dataframe(display_companies)
            
            # 업체 삭제
            with st.form("delete_company_form"):
                company_id = st.number_input("삭제할 업체 ID", min_value=1, step=1)
                delete_submitted = st.form_submit_button("업체 삭제")
                
                if delete_submitted:
                    if data_manager.delete_company(company_id):
                        st.success(f"ID {company_id} 업체가 삭제되었습니다.")
                        st.rerun()
                    else:
                        st.error(f"ID {company_id} 업체를 찾을 수 없습니다.")
        else:
            st.info("등록된 업체가 없습니다.")
        
        # 새 업체 추가
        st.subheader("새 업체 추가")
        with st.form("add_company_form"):
            new_company_name = st.text_input("상호명")
            add_submitted = st.form_submit_button("업체 추가")
            
            if add_submitted and new_company_name:
                company_id = data_manager.add_company(new_company_name)
                st.success(f"'{new_company_name}'이(가) 추가되었습니다. (ID: {company_id})")
                st.rerun()
    
    elif menu == "검색 기록":
        st.header("검색 기록")
        
        # 업체 선택
        companies = data_manager.get_companies()
        
        if not companies.empty:
            company_options = companies['name'].tolist()
            company_options.insert(0, "모든 업체")
            
            selected_company = st.selectbox("업체 선택", company_options)
            
            if selected_company == "모든 업체":
                results = data_manager.get_search_results()
            else:
                company_id = companies[companies['name'] == selected_company]['id'].iloc[0]
                results = data_manager.get_search_results(company_id=company_id)
            
            if not results.empty:
                # 회사명과 키워드 텍스트 추가
                results['company_name'] = results['company_id'].apply(data_manager.get_company_name)
                results['keyword_text'] = results['keyword_id'].apply(data_manager.get_keyword_text)
                
                # 표시할 열 선택 및 순서 변경
                display_results = results[['search_time', 'keyword_text', 'company_name', 'rank']]
                display_results.columns = ['검색 시간', '검색어', '상호명', '순위']
                
                st.dataframe(display_results)
                
                # CSV 다운로드 버튼
                csv = display_results.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="CSV 다운로드",
                    data=csv,
                    file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                )
            else:
                st.info("검색 결과가 없습니다.")
        else:
            st.info("등록된 업체가 없습니다.")
    
    elif menu == "도움말":
        st.header("도움말")
        st.markdown("""
        ### 네이버 플레이스 순위 검색 애플리케이션 사용법
        
        #### 실시간 검색
        1. 검색어(예: 의정부 미용실)와 상호명(예: 준오헤어 의정부역점)을 입력합니다.
        2. '검색' 버튼을 클릭하면 네이버 플레이스에서 해당 키워드로 검색했을 때 상호명의 순위를 확인합니다.
        3. 검색 결과는 자동으로 저장되며, 최근 검색 결과 목록에서 확인할 수 있습니다.
        
        #### 업체 관리
        - 새로운 업체를 추가하거나 기존 업체를 삭제할 수 있습니다.
        - 업체 정보는 검색 결과와 연동되어 관리됩니다.
        
        #### 검색 기록
        - 특정 업체 또는 모든 업체의 검색 기록을 확인할 수 있습니다.
        - 검색 결과를 CSV 파일로 다운로드할 수 있습니다.
        
        #### 자동 업데이트
        - 매일 오후 2시에 등록된 모든 업체와 키워드 조합에 대해 자동으로 검색이 실행됩니다.
        - 자동 업데이트 결과는 검색 기록에서 확인할 수 있습니다.
        """)

if __name__ == "__main__":
    main()
