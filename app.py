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
    page_title="ESG Analysis Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern design
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Inter', sans-serif;
    }
    
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 3rem;
        color: #27ae60;
        font-weight: bold;
    }
    
    /* Custom Cards */
    .custom-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #2980b9;
    }
    
    .initiative-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 4px solid #27ae60;
    }
    
    /* Summary styling */
    .summary-text {
        font-size: 1.1rem;
        line-height: 1.6;
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
    st.title("ESG Dashboard")
    st.markdown("Discover the environmental, social, and governance impact of companies worldwide.")
    
    st.markdown("---")
    st.markdown("### Powered by API")
    st.markdown("Want to use this data in your own applications?")
    st.markdown(
        '<a href="https://rapidapi.com/" target="_blank" style="display: block; width: 100%; padding: 10px; background-color: #8e44ad; color: white !important; text-align: center; text-decoration: none; border-radius: 5px; font-weight: bold; margin-top: 20px;">🚀 Subscribe on RapidAPI</a>', 
        unsafe_allow_html=True
    )

# Main Title
st.title("🌍 ESG Analysis Dashboard")
st.markdown("Enter a company name below to retrieve its latest ESG (Environmental, Social, and Governance) score and sustainability initiatives.")

# Search Section
with st.form(key='search_form'):
    col1, col2 = st.columns([3, 1])
    with col1:
        company_name = st.text_input("Company Name", placeholder="e.g., Apple, Microsoft, Tesla", label_visibility="collapsed")
    with col2:
        submit_button = st.form_submit_button(label='🔍 Start Analysis', use_container_width=True)

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
    with st.spinner(f"Analyzing ESG data for {company_name}..."):
        data = fetch_esg_data(company_name)
        
        if data:
            st.success("Analysis Complete!")
            
            # --- Score Section ---
            st.markdown("## 📊 ESG Scores")
            score_col1, score_col2, score_col3, score_col4 = st.columns(4)
            
            with score_col1:
                st.metric(label="Total ESG Score", value=data.get("esg_score", "N/A"))
            with score_col2:
                st.metric(label="Environmental", value=data.get("environmental_score", "N/A"))
            with score_col3:
                st.metric(label="Social", value=data.get("social_score", "N/A"))
            with score_col4:
                st.metric(label="Governance", value=data.get("governance_score", "N/A"))
            
            # --- Summary Section ---
            st.markdown("## 📝 Executive Summary")
            st.markdown(f"""
            <div class="custom-card">
                <p class="summary-text">{data.get("summary", "No summary available.")}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # --- Initiatives Section ---
            st.markdown("## 💡 Key Initiatives")
            initiatives = data.get("key_initiatives", [])
            
            if initiatives:
                for initiative in initiatives:
                    st.markdown(f"""
                    <div class="initiative-card">
                        <b>✓</b> {initiative}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No specific initiatives found.")
                
elif submit_button:
    st.warning("Please enter a company name.")
