import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.data_manager import DataManager

# 데이터 관리자 초기화
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
data_manager = DataManager(data_dir)

def main():
    st.title("검색 결과 시각화")
    
    # 업체 선택
    companies = data_manager.get_companies()
    
    if companies.empty:
        st.info("등록된 업체가 없습니다. '업체 관리' 메뉴에서 업체를 추가해주세요.")
        return
    
    # 업체 선택 옵션
    company_options = companies['name'].tolist()
    selected_company = st.selectbox("업체 선택", company_options)
    company_id = companies[companies['name'] == selected_company]['id'].iloc[0]
    
    # 키워드 선택 옵션
    keywords = data_manager.get_keywords()
    if keywords.empty:
        st.info("등록된 키워드가 없습니다. '실시간 검색' 메뉴에서 검색을 실행해주세요.")
        return
    
    keyword_options = keywords['text'].tolist()
    keyword_options.insert(0, "모든 키워드")
    selected_keyword = st.selectbox("키워드 선택", keyword_options)
    
    # 기간 선택
    col1, col2 = st.columns(2)
    with col1:
        days = st.slider("조회 기간 (일)", 1, 30, 7)
    
    with col2:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        st.write(f"기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
    
    # 검색 결과 조회
    results = data_manager.get_search_results(company_id=company_id)
    
    if results.empty:
        st.info(f"'{selected_company}'의 검색 결과가 없습니다.")
        return
    
    # 키워드 필터링
    if selected_keyword != "모든 키워드":
        keyword_id = keywords[keywords['text'] == selected_keyword]['id'].iloc[0]
        results = results[results['keyword_id'] == keyword_id]
    
    if results.empty:
        st.info(f"선택한 키워드에 대한 검색 결과가 없습니다.")
        return
    
    # 키워드 텍스트 추가
    results['keyword_text'] = results['keyword_id'].apply(data_manager.get_keyword_text)
    
    # 날짜 형식 변환
    results['search_date'] = pd.to_datetime(results['search_time'])
    
    # 기간 필터링
    results = results[(results['search_date'] >= start_date) & (results['search_date'] <= end_date)]
    
    if results.empty:
        st.info(f"선택한 기간에 대한 검색 결과가 없습니다.")
        return
    
    # 시각화 1: 시간에 따른 순위 변화 (선 그래프)
    st.subheader("시간에 따른 순위 변화")
    
    if selected_keyword == "모든 키워드":
        # 키워드별로 그룹화하여 시각화
        fig = px.line(
            results, 
            x='search_date', 
            y='rank', 
            color='keyword_text',
            markers=True,
            title=f"{selected_company}의 시간별 순위 변화",
            labels={'search_date': '검색 일시', 'rank': '순위', 'keyword_text': '키워드'}
        )
        
        # Y축 역순으로 표시 (1위가 위에 오도록)
        fig.update_layout(yaxis=dict(autorange="reversed"))
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        # 단일 키워드 시각화
        fig = px.line(
            results, 
            x='search_date', 
            y='rank',
            markers=True,
            title=f"{selected_company}의 '{selected_keyword}' 키워드 순위 변화",
            labels={'search_date': '검색 일시', 'rank': '순위'}
        )
        
        # Y축 역순으로 표시 (1위가 위에 오도록)
        fig.update_layout(yaxis=dict(autorange="reversed"))
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 시각화 2: 최근 순위 현황 (게이지 차트)
    st.subheader("최근 순위 현황")
    
    # 키워드별 최신 데이터 추출
    latest_results = results.sort_values('search_date').groupby('keyword_id').last().reset_index()
    
    # 키워드 텍스트 추가
    latest_results['keyword_text'] = latest_results['keyword_id'].apply(data_manager.get_keyword_text)
    
    # 게이지 차트 생성
    for _, row in latest_results.iterrows():
        keyword_text = row['keyword_text']
        rank = row['rank']
        search_time = row['search_time']
        
        # 순위에 따른 색상 설정
        if rank <= 3:
            color = "green"
        elif rank <= 10:
            color = "blue"
        elif rank <= 20:
            color = "orange"
        else:
            color = "red"
        
        # 게이지 차트 생성
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=rank,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"'{keyword_text}' 키워드 순위"},
            gauge={
                'axis': {'range': [1, 50], 'tickwidth': 1},
                'bar': {'color': color},
                'steps': [
                    {'range': [1, 3], 'color': "rgba(0, 255, 0, 0.1)"},
                    {'range': [3, 10], 'color': "rgba(0, 0, 255, 0.1)"},
                    {'range': [10, 20], 'color': "rgba(255, 165, 0, 0.1)"},
                    {'range': [20, 50], 'color': "rgba(255, 0, 0, 0.1)"}
                ]
            }
        ))
        
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"마지막 업데이트: {search_time}")
    
    # 시각화 3: 순위 분포 (히스토그램)
    if len(results) > 5:  # 데이터가 충분할 때만 표시
        st.subheader("순위 분포")
        
        fig = px.histogram(
            results, 
            x='rank',
            nbins=20,
            title=f"{selected_company}의 순위 분포",
            labels={'rank': '순위', 'count': '빈도'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 원본 데이터 표시
    with st.expander("원본 데이터 보기"):
        display_results = results[['search_time', 'keyword_text', 'rank']]
        display_results.columns = ['검색 시간', '키워드', '순위']
        st.dataframe(display_results.sort_values('검색 시간', ascending=False))

if __name__ == "__main__":
    main()
