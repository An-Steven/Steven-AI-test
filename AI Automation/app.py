import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
import numpy as np
import requests
import os
from github_config import (
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    CALLBACK_URL,
    AUTHORIZE_URL,
    ACCESS_TOKEN_URL,
    API_BASE_URL,
    SCOPES
)

# 页面标题和说明
st.title('Excel文本相似度分析器')
st.markdown('### 请上传Excel文件并选择需要分析的Sheet')

# 文件上传组件
uploaded_file = st.file_uploader('选择Excel文件', type=['xlsx', 'xls'])

if uploaded_file:
    # 读取Excel文件的所有Sheet名称
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    
    # Sheet选择组件
    selected_sheet = st.selectbox('选择要分析的Sheet', sheet_names)
    
    if selected_sheet:
        # 读取选定Sheet的数据
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
        
        # 检查是否存在description列
        if 'description' in df.columns:
            # 加载Sentence-BERT模型
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # 文本向量化
            descriptions = df['description'].astype(str).tolist()
            embeddings = model.encode(descriptions)
            
            # 使用DBSCAN进行密度聚类
            clustering = DBSCAN(eps=0.5, min_samples=2).fit(embeddings)
            
            # 创建结果DataFrame
            result_df = pd.DataFrame({
                '原始描述': descriptions,
                '聚类标签': clustering.labels_
            })
            
            # 统计各聚类出现次数
            cluster_counts = result_df.groupby('聚类标签').agg(
                典型描述=('原始描述', lambda x: x.mode()[0]),
                出现次数=('原始描述', 'count')
            ).reset_index()
            
            # 展示结果
            st.subheader('分析结果')
            st.dataframe(cluster_counts[['典型描述', '出现次数']])
            
            # 显示原始数据参考
            with st.expander('查看原始数据'):
                st.dataframe(df)
        else:
            st.error('未找到"description"列，请检查文件格式')

# 添加GitHub认证路由
@st.cache_resource
def init_github_oauth():
    st.session_state.setdefault('github_token', None)

# 处理OAuth回调
def handle_github_callback():
    code = st.experimental_get_query_params().get('code')
    if code:
        data = {
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'code': code,
            'redirect_uri': CALLBACK_URL
        }
        headers = {'Accept': 'application/json'}
        response = requests.post(ACCESS_TOKEN_URL, data=data, headers=headers)
        if response.status_code == 200:
            st.session_state.github_token = response.json().get('access_token')

# 在文件末尾添加认证组件
if __name__ == '__main__':
    init_github_oauth()
    handle_github_callback()
    
    # 添加登录按钮
    if not st.session_state.github_token:
        auth_url = f"{AUTHORIZE_URL}?client_id={GITHUB_CLIENT_ID}&redirect_uri={CALLBACK_URL}&scope={' '.join(SCOPES)}"
        st.markdown(f'[GitHub登录]({auth_url})')
    else:
        st.success('已通过GitHub认证')