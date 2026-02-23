import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "")

# Page configuration
st.set_page_config(
    page_title="ESG 経営分析ダッシュボード",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern design
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif !important;
    }
    
    /* Custom Cards */
    .custom-card {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        border-left: 5px solid #2980b9;
        font-family: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif !important;
    }
    
    .initiative-card {
        background-color: white;
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 4px solid #27ae60;
        font-family: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif !important;
    }
    
    /* Summary styling */
    .summary-text {
        font-size: 1.1rem;
        line-height: 1.8;
        color: #34495e;
    }
    
    /* Button styling in sidebar */
    .sidebar-btn {
        display: block;
        width: 100%;
        padding: 10px;
        background-color: #8e44ad;
        color: white !important;
        text-align: center;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        margin-top: 20px;
        transition: background-color 0.3s;
    }
    .sidebar-btn:hover {
        background-color: #9b59b6;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3038/3038290.png", width=100) # Placeholder logo
    st.title("ESG ダッシュボード")
    st.markdown("世界中の企業の環境・社会・ガバナンスへの取り組みを分析します。")
    
    st.markdown("---")
    st.markdown("### Powered by API")
    st.markdown("このデータを自身のアプリケーションで活用しませんか？")
    st.markdown(
        '<a href="https://rapidapi.com/akbkuh00/api/esg-sustainability-score-api/pricing" target="_blank" style="display: block; width: 100%; padding: 10px; background-color: #8e44ad; color: white !important; text-align: center; text-decoration: none; border-radius: 5px; font-weight: bold; margin-top: 20px;">🚀 商用利用・APIプランを購読する</a>', 
        unsafe_allow_html=True
    )

# Main Title
st.title("🌍 ESG 経営分析ダッシュボード")
st.markdown("下の検索ボックスに企業名を入力して、最新のESG評価スコアとサステナビリティに関する主要な取り組みを確認しましょう。")

# Search Section
with st.form(key='search_form'):
    col1, col2 = st.columns([3, 1])
    with col1:
        company_name = st.text_input("企業名", placeholder="例：トヨタ自動車、ソニーグループ", label_visibility="collapsed")
    with col2:
        submit_button = st.form_submit_button(label='🔍 分析を実行する', use_container_width=True)

# API Call and Data Processing
def fetch_esg_data(company_name):
    url = f"https://{RAPIDAPI_HOST}/esg-score/"
    
    querystring = {"query": company_name}
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    
    try:
        if not RAPIDAPI_KEY or not RAPIDAPI_HOST:
             # Return mock data for demonstration
             return {
                 "company": company_name,
                 "esg_score": 85,
                 "environmental_score": 88,
                 "social_score": 82,
                 "governance_score": 85,
                 "summary": f"{company_name} is demonstrating strong leadership in sustainability. The company has made significant strides in reducing its carbon footprint and promoting diversity.",
                 "key_initiatives": [
                     "Achieved 100% renewable energy for corporate operations.",
                     "Committed to zero waste to landfill across all major facilities by 2030.",
                     "Launched a $1B fund for racial equity and justice initiatives.",
                     "Implemented strict supplier code of conduct regarding labor rights."
                 ]
             }
        
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

if submit_button and company_name:
    with st.spinner(f"「{company_name}」のESGデータを分析中..."):
        data = fetch_esg_data(company_name)
        
        if data:
            st.success("分析が完了しました！")
            
            def get_color(score):
                if score == "N/A": return "#7f8c8d"
                try:
                    s = float(score)
                    if s >= 80: return "#27ae60"
                    elif s >= 60: return "#f39c12"
                    else: return "#e74c3c"
                except:
                    return "#7f8c8d"
            
            def render_metric(label, value):
                color = get_color(value)
                return f'''
                <div class="custom-card" style="text-align: center; padding: 15px; border-left: 5px solid {color}; border-top: 5px solid {color};">
                    <p style="color: #7f8c8d; font-size: 1.1rem; margin-bottom: 5px; font-weight: bold;">{label}</p>
                    <h2 style="color: {color}; font-size: 2.8rem; margin: 0;">{value}</h2>
                </div>
                '''

            # --- Score Section ---
            st.markdown("## 📊 ESG 評価スコア")
            score_col1, score_col2, score_col3, score_col4 = st.columns(4)
            
            with score_col1:
                st.markdown(render_metric("総合スコア", data.get("esg_score", "N/A")), unsafe_allow_html=True)
            with score_col2:
                st.markdown(render_metric("環境 (E)", data.get("environmental_score", "N/A")), unsafe_allow_html=True)
            with score_col3:
                st.markdown(render_metric("社会 (S)", data.get("social_score", "N/A")), unsafe_allow_html=True)
            with score_col4:
                st.markdown(render_metric("ガバナンス (G)", data.get("governance_score", "N/A")), unsafe_allow_html=True)
            
            # --- Summary Section ---
            st.markdown("## 📝 分析エグゼクティブ・サマリー")
            st.markdown(f"""
            <div class="custom-card">
                <p class="summary-text">{data.get("summary", "サマリー情報はありません。")}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # --- Initiatives Section ---
            st.markdown("## 💡 主要なサステナビリティ活動")
            initiatives = data.get("key_initiatives", [])
            
            if initiatives:
                for initiative in initiatives:
                    st.markdown(f"""
                    <div class="initiative-card">
                        <b>✓</b> {initiative}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("特筆すべき取り組みは見つかりませんでした。")
                
elif submit_button:
    st.warning("企業名を入力してください。")
