import os
import pandas as pd
import csv
from datetime import datetime

class DataManager:
    """데이터 관리 클래스"""
    
    def __init__(self, data_dir):
        """
        데이터 관리자 초기화
        
        Args:
            data_dir (str): 데이터 디렉토리 경로
        """
        self.data_dir = data_dir
        self.companies_file = os.path.join(data_dir, 'companies.csv')
        self.keywords_file = os.path.join(data_dir, 'keywords.csv')
        self.results_file = os.path.join(data_dir, 'search_results.csv')
        
        # 데이터 디렉토리 및 파일 초기화
        self._initialize_data_files()
    
    def _initialize_data_files(self):
        """데이터 파일 초기화"""
        # 데이터 디렉토리 생성
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 회사 데이터 파일 초기화
        if not os.path.exists(self.companies_file):
            with open(self.companies_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'name', 'created_at'])
        
        # 키워드 데이터 파일 초기화
        if not os.path.exists(self.keywords_file):
            with open(self.keywords_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'text', 'created_at'])
        
        # 검색 결과 데이터 파일 초기화
        if not os.path.exists(self.results_file):
            with open(self.results_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'company_id', 'keyword_id', 'rank', 'search_time'])
    
    def get_companies(self):
        """
        모든 회사 정보 조회
        
        Returns:
            pandas.DataFrame: 회사 정보
        """
        try:
            return pd.read_csv(self.companies_file)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=['id', 'name', 'created_at'])
    
    def get_keywords(self):
        """
        모든 키워드 정보 조회
        
        Returns:
            pandas.DataFrame: 키워드 정보
        """
        try:
            return pd.read_csv(self.keywords_file)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=['id', 'text', 'created_at'])
    
    def get_search_results(self, company_id=None, keyword_id=None):
        """
        검색 결과 조회
        
        Args:
            company_id (int, optional): 회사 ID 필터
            keyword_id (int, optional): 키워드 ID 필터
            
        Returns:
            pandas.DataFrame: 검색 결과
        """
        try:
            df = pd.read_csv(self.results_file)
            
            if company_id is not None:
                df = df[df['company_id'] == company_id]
            
            if keyword_id is not None:
                df = df[df['keyword_id'] == keyword_id]
            
            return df
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=['id', 'company_id', 'keyword_id', 'rank', 'search_time'])
    
    def add_company(self, name):
        """
        회사 추가
        
        Args:
            name (str): 회사명
            
        Returns:
            int: 생성된 회사 ID
        """
        companies = self.get_companies()
        
        # 이미 존재하는 회사인지 확인
        if not companies.empty and name in companies['name'].values:
            existing = companies[companies['name'] == name]
            return existing['id'].iloc[0]
        
        # 새 ID 생성
        new_id = 1 if companies.empty else companies['id'].max() + 1
        
        # 새 회사 추가
        new_company = pd.DataFrame({
            'id': [new_id],
            'name': [name],
            'created_at': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        })
        
        # 파일에 추가
        if companies.empty:
            new_company.to_csv(self.companies_file, index=False)
        else:
            pd.concat([companies, new_company]).to_csv(self.companies_file, index=False)
        
        return new_id
    
    def add_keyword(self, text):
        """
        키워드 추가
        
        Args:
            text (str): 키워드 텍스트
            
        Returns:
            int: 생성된 키워드 ID
        """
        keywords = self.get_keywords()
        
        # 이미 존재하는 키워드인지 확인
        if not keywords.empty and text in keywords['text'].values:
            existing = keywords[keywords['text'] == text]
            return existing['id'].iloc[0]
        
        # 새 ID 생성
        new_id = 1 if keywords.empty else keywords['id'].max() + 1
        
        # 새 키워드 추가
        new_keyword = pd.DataFrame({
            'id': [new_id],
            'text': [text],
            'created_at': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        })
        
        # 파일에 추가
        if keywords.empty:
            new_keyword.to_csv(self.keywords_file, index=False)
        else:
            pd.concat([keywords, new_keyword]).to_csv(self.keywords_file, index=False)
        
        return new_id
    
    def add_search_result(self, company_id, keyword_id, rank, search_time=None):
        """
        검색 결과 추가
        
        Args:
            company_id (int): 회사 ID
            keyword_id (int): 키워드 ID
            rank (int): 검색 순위
            search_time (str, optional): 검색 시간
            
        Returns:
            int: 생성된 결과 ID
        """
        results = self.get_search_results()
        
        # 새 ID 생성
        new_id = 1 if results.empty else results['id'].max() + 1
        
        # 검색 시간이 없으면 현재 시간 사용
        if search_time is None:
            search_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 새 검색 결과 추가
        new_result = pd.DataFrame({
            'id': [new_id],
            'company_id': [company_id],
            'keyword_id': [keyword_id],
            'rank': [rank],
            'search_time': [search_time]
        })
        
        # 파일에 추가
        if results.empty:
            new_result.to_csv(self.results_file, index=False)
        else:
            pd.concat([results, new_result]).to_csv(self.results_file, index=False)
        
        return new_id
    
    def get_company_name(self, company_id):
        """
        회사 ID로 회사명 조회
        
        Args:
            company_id (int): 회사 ID
            
        Returns:
            str: 회사명
        """
        companies = self.get_companies()
        if companies.empty:
            return None
        
        company = companies[companies['id'] == company_id]
        if company.empty:
            return None
        
        return company['name'].iloc[0]
    
    def get_keyword_text(self, keyword_id):
        """
        키워드 ID로 키워드 텍스트 조회
        
        Args:
            keyword_id (int): 키워드 ID
            
        Returns:
            str: 키워드 텍스트
        """
        keywords = self.get_keywords()
        if keywords.empty:
            return None
        
        keyword = keywords[keywords['id'] == keyword_id]
        if keyword.empty:
            return None
        
        return keyword['text'].iloc[0]
    
    def delete_company(self, company_id):
        """
        회사 삭제
        
        Args:
            company_id (int): 삭제할 회사 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        companies = self.get_companies()
        if companies.empty:
            return False
        
        # 회사 삭제
        new_companies = companies[companies['id'] != company_id]
        if len(new_companies) == len(companies):
            return False
        
        new_companies.to_csv(self.companies_file, index=False)
        
        # 관련 검색 결과도 삭제
        results = self.get_search_results()
        if not results.empty:
            new_results = results[results['company_id'] != company_id]
            new_results.to_csv(self.results_file, index=False)
        
        return True
    
    def delete_keyword(self, keyword_id):
        """
        키워드 삭제
        
        Args:
            keyword_id (int): 삭제할 키워드 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        keywords = self.get_keywords()
        if keywords.empty:
            return False
        
        # 키워드 삭제
        new_keywords = keywords[keywords['id'] != keyword_id]
        if len(new_keywords) == len(keywords):
            return False
        
        new_keywords.to_csv(self.keywords_file, index=False)
        
        # 관련 검색 결과도 삭제
        results = self.get_search_results()
        if not results.empty:
            new_results = results[results['keyword_id'] != keyword_id]
            new_results.to_csv(self.results_file, index=False)
        
        return True
