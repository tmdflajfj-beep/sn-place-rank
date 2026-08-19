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
    st.title("업체 관리")
    
    # 업체 목록 표시
    companies = data_manager.get_companies()
    
    st.header("등록된 업체 목록")
    if not companies.empty:
        # 표시할 열 선택 및 순서 변경
        display_companies = companies[['id', 'name', 'created_at']]
        display_companies.columns = ['ID', '상호명', '등록일']
        
        st.dataframe(display_companies)
    else:
        st.info("등록된 업체가 없습니다.")
    
    # 새 업체 추가
    st.header("새 업체 추가")
    with st.form("add_company_form"):
        new_company_name = st.text_input("상호명")
        add_submitted = st.form_submit_button("업체 추가")
        
        if add_submitted and new_company_name:
            company_id = data_manager.add_company(new_company_name)
            st.success(f"'{new_company_name}'이(가) 추가되었습니다. (ID: {company_id})")
            st.rerun()
    
    # 업체 삭제
    if not companies.empty:
        st.header("업체 삭제")
        with st.form("delete_company_form"):
            company_id = st.number_input("삭제할 업체 ID", min_value=1, step=1)
            delete_submitted = st.form_submit_button("업체 삭제")
            
            if delete_submitted:
                if data_manager.delete_company(company_id):
                    st.success(f"ID {company_id} 업체가 삭제되었습니다.")
                    st.rerun()
                else:
                    st.error(f"ID {company_id} 업체를 찾을 수 없습니다.")

if __name__ == "__main__":
    main()
