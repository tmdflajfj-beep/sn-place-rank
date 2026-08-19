import streamlit as st
import pandas as pd
import os
import sys

# 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.data_manager import DataManager

# 데이터 관리자 초기화
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
data_manager = DataManager(data_dir)

def main():
    st.title("검색 기록")
    
    # 업체 선택
    companies = data_manager.get_companies()
    
    if companies.empty:
        st.info("등록된 업체가 없습니다. '업체 관리' 메뉴에서 업체를 추가해주세요.")
        return
    
    company_options = companies['name'].tolist()
    company_options.insert(0, "모든 업체")
    
    selected_company = st.selectbox("업체 선택", company_options)
    
    if selected_company == "모든 업체":
        results = data_manager.get_search_results()
    else:
        company_id = companies[companies['name'] == selected_company]['id'].iloc[0]
        results = data_manager.get_search_results(company_id=company_id)
    
    if results.empty:
        st.info("검색 결과가 없습니다.")
        return
    
    # 회사명과 키워드 텍스트 추가
    results['company_name'] = results['company_id'].apply(data_manager.get_company_name)
    results['keyword_text'] = results['keyword_id'].apply(data_manager.get_keyword_text)
    
    # 날짜 필터링 옵션
    st.subheader("날짜 필터링")
    
    # 날짜 형식 변환
    results['search_date'] = pd.to_datetime(results['search_time'])
    
    # 날짜 범위 계산
    min_date = results['search_date'].min().date()
    max_date = results['search_date'].max().date()
    
    # 날짜 선택기
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("시작일", min_date)
    with col2:
        end_date = st.date_input("종료일", max_date)
    
    # 날짜 필터링
    filtered_results = results[
        (results['search_date'].dt.date >= start_date) & 
        (results['search_date'].dt.date <= end_date)
    ]
    
    if filtered_results.empty:
        st.info("선택한 기간에 검색 결과가 없습니다.")
        return
    
    # 표시할 열 선택 및 순서 변경
    display_results = filtered_results[['search_time', 'keyword_text', 'company_name', 'rank']]
    display_results.columns = ['검색 시간', '검색어', '상호명', '순위']
    
    # 정렬 옵션
    sort_option = st.selectbox(
        "정렬 기준",
        ["검색 시간 (최신순)", "검색 시간 (오래된순)", "순위 (높은순)", "순위 (낮은순)"]
    )
    
    if sort_option == "검색 시간 (최신순)":
        display_results = display_results.sort_values(by='검색 시간', ascending=False)
    elif sort_option == "검색 시간 (오래된순)":
        display_results = display_results.sort_values(by='검색 시간', ascending=True)
    elif sort_option == "순위 (높은순)":
        display_results = display_results.sort_values(by='순위', ascending=True)
    elif sort_option == "순위 (낮은순)":
        display_results = display_results.sort_values(by='순위', ascending=False)
    
    # 결과 표시
    st.subheader("검색 결과")
    st.dataframe(display_results)
    
    # CSV 다운로드 버튼
    csv = display_results.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="CSV 다운로드",
        data=csv,
        file_name=f"search_results_{start_date}_{end_date}.csv",
        mime="text/csv",
    )
    
    # 통계 정보
    st.subheader("통계 정보")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("총 검색 횟수", len(display_results))
    
    with col2:
        avg_rank = display_results[display_results['순위'] > 0]['순위'].mean()
        st.metric("평균 순위", f"{avg_rank:.1f}" if not pd.isna(avg_rank) else "N/A")
    
    with col3:
        best_rank = display_results[display_results['순위'] > 0]['순위'].min()
        st.metric("최고 순위", int(best_rank) if not pd.isna(best_rank) else "N/A")

if __name__ == "__main__":
    main()
