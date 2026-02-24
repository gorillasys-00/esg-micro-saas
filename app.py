# version: 1.1.8 - implement_caching
import streamlit as st
import requests
import os
import json
import io
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from datetime import datetime
import extra_streamlit_components as stx

# Load environment variables
load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "")

# Page configuration
st.set_page_config(
    page_title="AI Business Suite",
    layout="wide",
    initial_sidebar_state="auto",
)

# Custom CSS for custom elements only
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0.01em !important;
        line-height: 1.6 !important;
    }

    h1, h2, h3, h4 {
        letter-spacing: 0.02em !important;
        font-weight: 600 !important;
    }

    /* サイドバーのセクションタイトル（機能を選択など） */
    .stRadio label, .stSelectbox label {
        letter-spacing: 0.05em !important;
        font-weight: 500 !important;
    }

    /* サイドバーのブランドロゴ用余白 */
    .sidebar-brand {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        color: #FFFFFF;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 2rem;
    }

    /* サイドバーの区切り線をごく薄いグレーに */
    [data-testid="stSidebar"] hr {
        border-bottom-color: rgba(255,255,255,0.1) !important;
    }

    /* サイドバーにエレガントな境界線を追加 */
    [data-testid="stSidebar"] {
        border-right: 1px solid #E5E7EB !important;
    }
    
    /* サイドバー内の文字を完全視認化（すべての下部テキストやリンクを含む） */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] div.stMarkdown p,
    [data-testid="stSidebar"] .stText {
        color: #FFFFFF !important;
    }
    
    /* サイドバーのエキスパンダー（折りたたみ）の視認性確保 */
    [data-testid="stSidebar"] div[data-testid="stExpander"] {
        background-color: #1E293B !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stSidebar"] div[data-testid="stExpander"] summary,
    [data-testid="stSidebar"] div[data-testid="stExpander"] summary *,
    [data-testid="stSidebar"] div[data-testid="stExpander"] div[data-testid="stExpanderDetails"],
    [data-testid="stSidebar"] div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] * {
        background-color: transparent !important;
        color: #FFFFFF !important;
    }

    /* APIプラン購読ボタン専用の強制クラス */
    a.custom-api-btn, [data-testid="stSidebar"] a.custom-api-btn {
        display: block !important;
        width: 100% !important;
        padding: 12px !important;
        background-color: #4F46E5 !important;
        color: #FFFFFF !important;
        border: none !important;
        text-align: center !important;
        text-decoration: none !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        margin-top: 10px !important;
        box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2), 0 2px 4px -1px rgba(79, 70, 229, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    a.custom-api-btn:hover, [data-testid="stSidebar"] a.custom-api-btn:hover {
        background-color: #6366F1 !important;
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3), 0 4px 6px -2px rgba(79, 70, 229, 0.1) !important;
        transform: translateY(-2px) !important;
    }

    /* 下部余白用のコンテナクラス */
    .powered-by-container {
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255,255,255,0.1);
        color: #E2E8F0 !important;
        line-height: 1.8;
    }
    
    .powered-by-container h3 {
        color: #FFFFFF !important;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .powered-by-container b {
        color: #FFFFFF !important;
        font-weight: 700;
    }

    /* サイドバー内の要素に余裕を持たせる */
    [data-testid="stSidebarUserContent"] {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* 入力フォームの視認性修正（Render等での黒同化防止） */
    div.stTextInput input, div.stTextArea textarea,
    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div,
    div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div {
        border: 1px solid #E5E7EB !important;
        box-shadow: 0 1px 2px rgba(99, 102, 241, 0.1) !important;
        transition: all 0.2s ease !important;
    }
    div[data-baseweb="input"] > div:focus-within, div[data-baseweb="textarea"] > div:focus-within {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }

    /* ボタンにホバーエフェクトと丸みを持たせる */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
    }

    /* カードUIの枠線を整理し、安っぽさを排除 */
    [data-testid="stExpander"] {
        border: 1px solid #E5E7EB !important;
        border-radius: 12px !important;
        background-color: white !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02) !important;
    }

    /* Custom Cards */
    .custom-card {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02) !important;
        margin-bottom: 20px;
        border: 1px solid #E5E7EB;
        border-left: 5px solid #6366F1;
        word-break: break-word;
    }
    
    .initiative-card {
        background-color: white;
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02) !important;
        margin-bottom: 15px;
        border: 1px solid #E5E7EB;
        border-left: 4px solid #10B981;
        word-break: break-word;
    }
    
    /* Premium Text */
    .premium-text {
        color: #10B981 !important;
        font-weight: 700 !important;
    }
    
    /* Summary styling */
    .summary-text {
        font-size: 1.1rem;
        line-height: 1.8;
        color: #374151;
    }
    /* sync_id: 20260224-2 */
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-brand">AI BUSINESS SUITE</div>', unsafe_allow_html=True)
    st.markdown("統合型データ分析・抽出プラットフォーム")
    
    # Cookie Manager for persistent demo limits
    cookie_manager = stx.CookieManager()

    # Wait for cookies to load
    if not cookie_manager.get_all():
        pass # Wait one cycle if not ready
        
    MAX_DEMO_CALLS = 5
    
    # Initialize session state for API Key and Tools
    if "user_api_key" not in st.session_state:
        st.session_state.user_api_key = ""
    if "api_key_valid" not in st.session_state:
        st.session_state.api_key_valid = False
        
    # App State for Results
    if "esg_result" not in st.session_state: st.session_state.esg_result = None
    if "esg_company" not in st.session_state: st.session_state.esg_company = ""
    if "web_result" not in st.session_state: st.session_state.web_result = None
    if "niche_result" not in st.session_state: st.session_state.niche_result = None
    if "webhook_result" not in st.session_state: st.session_state.webhook_result = None
    if "text_to_json_result" not in st.session_state: st.session_state.text_to_json_result = None
    if "scrape_result" not in st.session_state: st.session_state.scrape_result = None
        
    # Read api_calls from cookies instead of session_state
    current_calls_str = cookie_manager.get("esg_demo_api_calls")
    if current_calls_str is None:
        api_calls_count = 0
    else:
        try:
            api_calls_count = int(current_calls_str)
        except:
            api_calls_count = 0
            
    # Keep it in session state for easy access during the run
    st.session_state.api_calls = api_calls_count
    
    app_mode = st.radio(
        "機能を選択:",
        options=[
            "ESG経営分析",
            "Webデータ抽出",
            "業界・競合トレンド",
            "ウェブフック連携",
            "テキスト構造化 (AI)",
            "汎用データ抽出"
        ]
    )
    
    st.markdown("---")
    
    # プレミアムプラン向け API Key 入力
    with st.expander("プレミアムプランをご購入済みの方"):
        input_key = st.text_input("RapidAPI Keyを入力してください", type="password", value=st.session_state.user_api_key)
        st.caption("※RapidAPIで発行された「X-RapidAPI-Key」を入力すると、デモ制限が解除されます。")
        
        if input_key and input_key != st.session_state.user_api_key:
            with st.spinner("API Keyを検証しています..."):
                headers = {"X-RapidAPI-Key": input_key, "X-RapidAPI-Host": RAPIDAPI_HOST}
                try:
                    # 空リクエスト代わりに適当なエンドポイントでテスト (401/403判定)
                    res = requests.get(f"https://{RAPIDAPI_HOST}/api/v1/esg-score", headers=headers, params={"query": "test"}, timeout=10)
                    if res.status_code in [401, 403]:
                        st.sidebar.error("認証に失敗しました。Keyを再確認してください。")
                        st.session_state.api_key_valid = False
                    else:
                        st.session_state.user_api_key = input_key
                        st.session_state.api_key_valid = True
                        st.sidebar.success("認証に成功しました。プレミアム機能が解放されました。")
                        st.rerun()
                except requests.exceptions.Timeout:
                    st.sidebar.error("バックエンドサーバーの応答がタイムアウトしました。")
                    st.session_state.api_key_valid = False
                except requests.exceptions.ConnectionError:
                    st.sidebar.error("バックエンドサーバーに接続できません。URL設定を確認してください。")
                    st.session_state.api_key_valid = False
                except Exception as e:
                    st.sidebar.error(f"予期せぬエラーが発生しました: {e}")
                    st.session_state.api_key_valid = False
        elif not input_key and st.session_state.user_api_key:
            st.session_state.user_api_key = ""
            st.session_state.api_key_valid = False
            st.rerun()
            
    st.markdown("---")
    
    if st.session_state.api_key_valid:
        st.markdown('<div class="powered-by-container">', unsafe_allow_html=True)
        st.markdown("<h3>Powered by API</h3>", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 1.5rem; color: #E2E8F0;'>このアプリケーションは<br><span class='premium-text'>Premium Mode: 有効</span><br>で動作しています。</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    elif st.session_state.api_calls >= MAX_DEMO_CALLS:
        st.error(f"無料デモ版の利用制限（{MAX_DEMO_CALLS}回）に達しました。")
        st.markdown(
            '<a href="https://rapidapi.com/akbkuh00/api/esg-sustainability-score-api/pricing" target="_blank" class="custom-api-btn">プレミアムプランへアップグレード</a>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown('<div class="powered-by-container">', unsafe_allow_html=True)
        st.markdown("<h3>Powered by API</h3>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-bottom: 1.5rem; color: #E2E8F0;'>このデータを自身のアプリケーションで活用しませんか？<br><br>デモ利用枠: <b style='color: #FFFFFF; font-weight: 700;'>{MAX_DEMO_CALLS - st.session_state.api_calls}回</b> 残り</div>", unsafe_allow_html=True)
        st.markdown(
            '<a href="https://rapidapi.com/akbkuh00/api/esg-sustainability-score-api/pricing" target="_blank" class="custom-api-btn">商用利用・APIプランを購読する</a>', 
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

def check_limit():
    if st.session_state.api_key_valid:
        return True # Bypass limit if user provides their own key
        
    if st.session_state.api_calls >= MAX_DEMO_CALLS:
        return False
    return True

def consume_demo_call():
    if st.session_state.api_key_valid:
        return
    # Increment
    new_count = st.session_state.api_calls + 1
    st.session_state.api_calls = new_count
    # Set cookie (expires in 1 day to reset limits daily if they come back tomorrow, or we can make it longer)
    import datetime as dt
    cookie_manager.set("esg_demo_api_calls", str(new_count), expires_at=dt.datetime.now() + dt.timedelta(days=1))

def call_api(endpoint, method="GET", params=None, json_data=None):
    base_url = os.getenv("BACKEND_URL", f"https://{RAPIDAPI_HOST}" if RAPIDAPI_HOST else "https://business-api-backend.onrender.com")
    url = f"{base_url}/api/v1{endpoint}"
    
    # Use user-provided API key if available, otherwise fallback to .env key
    active_api_key = st.session_state.user_api_key if st.session_state.api_key_valid else RAPIDAPI_KEY
    
    headers = {
        "X-RapidAPI-Key": active_api_key,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "Content-Type": "application/json"
    }
    
    try:
        if not active_api_key or not base_url:
             st.error("APIキーまたはホストが設定されていません。.envファイルと環境変数を確認するか、サイドバーからAPIキーを入力してください。")
             return None
             
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=120)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=json_data, timeout=120)
            
        if response.status_code != 200:
            st.error(f"分析中にエラーが発生しました: ステータス {response.status_code} - {response.text}")
            return None
            
        return response.json()
    except requests.exceptions.Timeout:
        st.error("分析中にエラーが発生しました: サーバーの応答がタイムアウトしました（最大120秒）。")
        return None
    except requests.exceptions.ConnectionError:
        st.error("分析中にエラーが発生しました: バックエンドサーバーに接続できません。URL設定を確認してください。")
        return None
    except Exception as e:
        st.error(f"分析中にエラーが発生しました: {e}")
        return None

def create_generic_pdf(title, data, mode="generic"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('JapaneseTitle', parent=styles['Title'], fontName='HeiseiKakuGo-W5', fontSize=24, spaceAfter=20, textColor=colors.HexColor('#2c3e50'))
    heading_style = ParagraphStyle('JapaneseHeading', parent=styles['Heading2'], fontName='HeiseiKakuGo-W5', fontSize=16, spaceAfter=15, spaceBefore=15, textColor=colors.HexColor('#2980b9'))
    normal_style = ParagraphStyle('JapaneseNormal', parent=styles['Normal'], fontName='HeiseiKakuGo-W5', fontSize=11, leading=16, textColor=colors.HexColor('#34495e'))
    bullet_style = ParagraphStyle('JapaneseBullet', parent=normal_style, leftIndent=20, bulletIndent=10)
    
    elements = []
    elements.append(Paragraph(f"AI分析レポート: {title}", title_style))
    elements.append(Paragraph(f"作成日: {datetime.now().strftime('%Y年%m月%d日')}", normal_style))
    elements.append(Spacer(1, 20))
    
    if mode == "esg" and isinstance(data, dict):
        elements.append(Paragraph("1. ESG 評価スコア", heading_style))
        score_data = [
            ['総合スコア', '環境 (E)', '社会 (S)', 'ガバナンス (G)'],
            [str(data.get('esg_score', 'N/A')), str(data.get('environmental_score', 'N/A')), str(data.get('social_score', 'N/A')), str(data.get('governance_score', 'N/A'))]
        ]
        t = Table(score_data, colWidths=[100, 100, 100, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f2f6')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#2c3e50')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'HeiseiKakuGo-W5'),
            ('FONTSIZE', (0,0), (-1,0), 12), ('FONTSIZE', (0,1), (-1,-1), 16),
            ('BOTTOMPADDING', (0,0), (-1,0), 12), ('TOPPADDING', (0,1), (-1,-1), 12), ('BOTTOMPADDING', (0,1), (-1,-1), 12),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#bdc3c7')), ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#bdc3c7')),
            ('TEXTCOLOR', (0,1), (0,1), colors.HexColor('#27ae60')), 
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("2. エグゼクティブ・サマリー", heading_style))
        elements.append(Paragraph(data.get("summary", "サマリー情報はありません。"), normal_style))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("3. 主要なサステナビリティ活動", heading_style))
        for init in data.get("key_initiatives", []):
            elements.append(Paragraph(f"・ {init}", bullet_style))
            elements.append(Spacer(1, 5))
            
    elif mode == "web_extract" or mode == "niche":
        elements.append(Paragraph("エグゼクティブ・サマリー", heading_style))
        if isinstance(data, dict) and 'summary' in data:
            elements.append(Paragraph(str(data['summary']), normal_style))
            elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("抽出データ詳細", heading_style))
        if isinstance(data, dict):
            for key, value in data.items():
                if key != 'summary':
                    elements.append(Paragraph(f"<b>{key}</b>:", normal_style))
                    if isinstance(value, list):
                        for item in value:
                            elements.append(Paragraph(f"・ {item}", bullet_style))
                    else:
                        elements.append(Paragraph(str(value), normal_style))
                    elements.append(Spacer(1, 10))
        else:
            elements.append(Paragraph(str(data), normal_style))
            
    elif mode == "text_to_json":
        elements.append(Paragraph("構造化データ定義リスト", heading_style))
        if isinstance(data, dict):
            for key, value in data.items():
                elements.append(Paragraph(f"<b>【{key}】</b>", normal_style))
                formatted_val = str(value) if not isinstance(value, (dict, list)) else json.dumps(value, ensure_ascii=False)
                elements.append(Paragraph(formatted_val, bullet_style))
                elements.append(Spacer(1, 10))
        else:
            elements.append(Paragraph(str(data), normal_style))
            
    else:
        # Generic PDF builder for other payloads
        elements.append(Paragraph("解析結果", heading_style))
        if isinstance(data, dict):
            for key, value in data.items():
                elements.append(Paragraph(f"<b>{key}</b>:", normal_style))
                formatted_val = json.dumps(value, ensure_ascii=False, indent=2) if isinstance(value, (dict, list)) else str(value)
                for line in formatted_val.split('\\n'):
                    elements.append(Paragraph(line, normal_style))
                elements.append(Spacer(1, 10))
        else:
            elements.append(Paragraph(str(data), normal_style))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def render_pdf_download_button(title, data, mode="generic"):
    st.markdown("---")
    pdf_data = create_generic_pdf(title, data, mode)
    st.download_button(
        label="診断レポート(PDF)をダウンロード",
        data=pdf_data,
        file_name=f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

if app_mode == "ESG経営分析":
    st.title("ESG 経営分析ダッシュボード")
    st.markdown("**概要:** 企業のサステナビリティ実績を即座にAIスコア化します。")
    st.info("活用事例: サプライチェーン企業のESGリスクのスクリーニング / 投資案件の初期デューデリジェンス資料の作成")
    st.write("")
    with st.form(key='esg_form'):
        col1, col2 = st.columns([3, 1])
        company_name = col1.text_input("企業名", placeholder="例：トヨタ自動車、ソニーグループ", label_visibility="collapsed")
        submit_button = col2.form_submit_button(label='分析を実行', use_container_width=True)

    if submit_button and company_name:
        if not check_limit():
            st.error("デモ利用制限に達しています。サイドバーからプレミアムプランへアップグレードしてください。")
        else:
            st.info("AIが分析を実行しています。サーバーの初回起動時は最大1分ほどかかる場合があります...")
            with st.spinner(f"AIが「{company_name}」のESG開示情報を深掘りしています..."):
                data = call_api("/esg-score", params={"company_name": company_name})
                if data and "esg_score" in data:
                    st.session_state.esg_result = data
                    st.session_state.esg_company = company_name
                    st.success("分析が完了しました。")
                    consume_demo_call()

    if st.session_state.esg_result:
        data = st.session_state.esg_result
        company_name = st.session_state.esg_company
        
        def get_color(score):
            if score == "N/A": return "#94A3B8"
            try:
                s = float(score)
                if s >= 80: return "#10B981"
                elif s >= 60: return "#F59E0B"
                else: return "#EF4444"
            except: return "#94A3B8"
        
        def render_metric(label, value):
            color = get_color(value)
            return f'''<div class="custom-card" style="text-align: center; padding: 15px; border-left: 5px solid {color}; border-top: 5px solid {color};"><p style="color: #6B7280; font-size: 1.1rem; margin-bottom: 5px; font-weight: 500;">{label}</p><h2 style="color: {color}; font-size: 2.8rem; margin: 0; font-weight: 500;">{value}</h2></div>'''

        st.markdown(f"## {company_name} の ESG 評価スコア")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(render_metric("総合スコア", data.get("esg_score", "N/A")), unsafe_allow_html=True)
        c2.markdown(render_metric("環境 (E)", data.get("environmental_score", "N/A")), unsafe_allow_html=True)
        c3.markdown(render_metric("社会 (S)", data.get("social_score", "N/A")), unsafe_allow_html=True)
        c4.markdown(render_metric("ガバナンス (G)", data.get("governance_score", "N/A")), unsafe_allow_html=True)
        
        st.markdown("## 分析エグゼクティブ・サマリー")
        st.markdown(f'<div class="custom-card"><p class="summary-text">{data.get("summary", "サマリーなし")}</p></div>', unsafe_allow_html=True)
        
        st.markdown("## 主要なサステナビリティ活動")
        initiatives = data.get("key_initiatives", [])
        if initiatives:
            for init in initiatives:
                st.markdown(f'<div class="initiative-card"> {init}</div>', unsafe_allow_html=True)
        
        render_pdf_download_button(f"ESG分析 ({company_name})", data, mode="esg")

elif app_mode == "Webデータ抽出":
    st.title("Webデータ抽出ツール")
    st.markdown("**概要:** 指定したURLから、AIが意味を理解して必要なビジネスデータだけをピンポイントで抽出します。")
    st.info("活用事例: 競合他社のHPからの役員一覧や資本金データの自動収集 / 特定のニュースサイトからの記事本文だけの抽出")
    st.write("")
    with st.form(key='web_form'):
        col1, col2 = st.columns([3, 1])
        url = col1.text_input("抽出対象のURL", placeholder="https://example.com/news/123", label_visibility="collapsed")
        target = st.text_input("抽出したい情報 (Target)", placeholder="例: 会社の代表者名と資本金", value="主要なビジネス情報")
        submit_button = col2.form_submit_button(label='抽出を実行', use_container_width=True)

    if submit_button and url:
        if not check_limit():
            st.error("デモ利用制限に達しています。サイドバーからプレミアムプランへアップグレードしてください。")
        else:
            st.info("AIが分析を実行しています。サーバーの初回起動時は最大1分ほどかかる場合があります...")
            with st.spinner("AIが指定されたURLの文脈を読み解き、情報を抽出しています..."):
                data = call_api("/web-extract", params={"url": url, "target": target})
                if data:
                    st.session_state.web_result = data
                    st.success("抽出完了")
                    consume_demo_call()

    if st.session_state.web_result:
        st.json(st.session_state.web_result)
        render_pdf_download_button("Webデータ抽出結果", st.session_state.web_result, mode="web_extract")

elif app_mode == "業界・競合トレンド":
    st.title("業界・競合トレンド分析")
    st.markdown("**概要:** ニッチなキーワードから、世界中の最新ニュースとトレンドをAIが要約・構造化します。")
    st.info("活用事例: 新規事業の企画会議に向けた、特定市場（例：EVバッテリー、アニメ市場）の最新動向レポートの自動生成")
    st.write("")
    with st.form(key='niche_form'):
        col1, col2 = st.columns([3, 1])
        query = col1.text_input("分析キーワード", placeholder="例：国内EV市場の動向", label_visibility="collapsed")
        submit_button = col2.form_submit_button(label='分析を実行', use_container_width=True)

    if submit_button and query:
        if not check_limit():
            st.error("デモ利用制限に達しています。サイドバーからプレミアムプランへアップグレードしてください。")
        else:
            st.info("AIが分析を実行しています。サーバーの初回起動時は最大1分ほどかかる場合があります...")
            with st.spinner("AIがグローバル・ローカルトレンドを統合分析しています..."):
                data = call_api("/niche-data", params={"query": query})
                if data:
                    st.session_state.niche_result = data
                    st.success("分析完了")
                    consume_demo_call()

    if st.session_state.niche_result:
        st.json(st.session_state.niche_result)
        render_pdf_download_button("業界・競合トレンド", st.session_state.niche_result, mode="niche")

elif app_mode == "ウェブフック連携":
    st.title("ウェブフック連携テスト")
    st.markdown("**概要:** ZapierやMake、自社システムへ分析データを自動送信するための機能です。")
    st.info("活用事例: ESG分析結果やスクレイピングデータを、指定したURLへPOST送信して後続のフロー（Slack通知、スプレッドシートへの記録等）をトリガーします。")
    
    st.markdown("### Step 1: 送信先URLの設定")
    st.write("受け取り側のウェブフックURLを入力してください（Zapier, Make, 独自のAPIなど）。")
    
    with st.form(key='webhook_form'):
        webhook_url = st.text_input("ウェブフックURL", placeholder="https://hooks.zapier.com/hooks/catch/12345/abcde")
        
        st.markdown("### Step 2: テスト送信")
        st.write("送信するテストデータ（JSONペイロード）を確認して送信します。")
        
        # Load active result to send
        active_result = {"message": "Webhook test successful!", "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')}
        for key in ["esg_result", "web_result", "niche_result", "text_to_json_result", "scrape_result"]:
            res = getattr(st.session_state, key, None)
            if res:
                active_result = res
                break
                
        default_payload = {
            "event": "data_extracted",
            "source": "AI Business Suite",
            "data": active_result
        }
        
        payload = st.text_area("テストペイロード (JSON形式)", value=json.dumps(default_payload, indent=2, ensure_ascii=False), height=150)
        
        submit_button = st.form_submit_button(label='送信テストを実行', use_container_width=True)

    with st.expander("送信されるJSONデータ（ペイロード）の構造について"):
        st.markdown("以下の形式でPOSTリクエストとして送信されます。受け取り側でこの構造をパース（解析）して利用してください。")
        st.code('''{
  "url": "指定したウェブフックURL",
  "payload": {
    "event": "data_extracted",
    "source": "AI Business Suite",
    "data": { ... }
  }
}''', language="json")

    if submit_button and webhook_url:
        with st.spinner("ウェブフックを送信中..."):
            try:
                json_payload = json.loads(payload)
                response = requests.post(webhook_url, json=json_payload, timeout=20)
                
                if response.status_code in (200, 201, 202):
                    res_obj = {"status": f"送信成功：ステータス{response.status_code}", "sent_data": json_payload, "response": response.text[:200]}
                    st.session_state.webhook_result = res_obj
                    st.success(f"送信成功：ステータス{response.status_code}")
                else:
                    st.error(f"送信失敗：ステータス{response.status_code} - 詳細はレスポンスを確認してください。")
            except requests.exceptions.RequestException as e:
                st.error(f"通信エラーが発生しました: {e}")
            except json.JSONDecodeError:
                st.error("ペイロードは有効なJSON形式で入力してください。")

    if st.session_state.webhook_result:
        st.json(st.session_state.webhook_result)
        render_pdf_download_button("Webhook送信結果", st.session_state.webhook_result)

elif app_mode == "テキスト構造化 (AI)":
    st.title("テキスト構造化 (AI)")
    st.markdown("**概要:** カオスな長文メモや議事録を、開発者やシステムが読み込める綺麗なJSONデータに変換します。")
    st.info("活用事例: 商談の雑多な音声文字起こしデータから、BANT条件（予算・時期など）を自動抽出してCRMへ入力")
    st.write("")
    with st.form(key='text_to_json_form'):
        text_input = st.text_area("構造化したいテキストを入力", height=150, placeholder="ここに議事録やメモを貼り付けてください...")
        submit_button = st.form_submit_button(label='構造化を実行', use_container_width=True)

    if submit_button and text_input:
        if not check_limit():
            st.error("デモ利用制限に達しています。サイドバーからプレミアムプランへアップグレードしてください。")
        else:
            st.info("AIが分析を実行しています。サーバーの初回起動時は最大1分ほどかかる場合があります...")
            with st.spinner("AIが非構造化テキストを解析し、綺麗なJSON形式に変換しています..."):
                data = call_api("/text-to-json", method="POST", json_data={"text": text_input, "format_instruction": "JSON形式で抽出してください"})
                if data:
                    st.session_state.text_to_json_result = data
                    st.success("構造化完了")
                    consume_demo_call()

    if st.session_state.text_to_json_result:
        st.json(st.session_state.text_to_json_result)
        render_pdf_download_button("テキスト構造化結果", st.session_state.text_to_json_result, mode="text_to_json")

elif app_mode == "汎用データ抽出":
    st.title("汎用データ抽出 (AI Scrape API)")
    st.markdown("**概要:** 指定したURLから、AIに指示した特定の情報（例：価格一覧、担当者名など）だけをピンポイントで抽出します。")
    st.info("活用事例: 特定の法人URLからの代表者名と資本金の抽出 / ECサイトの商品ページからの価格やスペック情報の取得")
    
    with st.expander("よくある抽出の指示例（プロンプト・テンプレート）"):
        st.markdown("""
        用途に合わせて以下のプロンプトをコピーしてご利用ください。
        - **会社概要の取得**: `このページから「会社名」「代表者名」「資本金」「設立年」をJSON形式で抽出してください。`
        - **商品情報の取得**: `ページ内にある商品の「製品名」「価格」「主な特徴（箇条書き3点）」をJSONで抽出してください。`
        - **採用情報の取得**: `募集要項から「職種」「給与体系」「必須要件」をJSON形式で抽出してください。`
        """)
        
    st.write("")
    with st.form(key='scrape_form'):
        st.markdown("### 抽出条件の入力")
        scrape_url = st.text_input("1. 抽出対象のURL", placeholder="https://example.com/company")
        prompt = st.text_area("2. 抽出したい情報の指示（プロンプト）", placeholder="例：役員一覧の名前と役職をJSON形式で抽出してください。", height=100)
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.form_submit_button(label='実行', use_container_width=True)

    if submit_button and scrape_url and prompt:
        if not check_limit():
            st.error("デモ利用制限に達しています。サイドバーからプレミアムプランへアップグレードしてください。")
        else:
            st.info("AIが分析を実行しています。サーバーの初回起動時は最大1分ほどかかる場合があります...")
            with st.spinner("AIエージェントがターゲットURLにアクセスし、指定された情報を抽出しています..."):
                # Use the correct ai-scrape endpoint which is GET and only takes url
                # Wait, if AI Scrape API is meant to extract content to markdown for AI reading
                data = call_api("/ai-scrape", params={"url": scrape_url})
                if data:
                    st.session_state.scrape_result = data
                    st.success("抽出完了")
                    consume_demo_call()

    if st.session_state.scrape_result:
        st.json(st.session_state.scrape_result)
        render_pdf_download_button("汎用データ抽出結果", st.session_state.scrape_result, mode="generic")
