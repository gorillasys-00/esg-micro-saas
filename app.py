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
    page_title="AI ビジネススイート",
    page_icon="🤖",
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
    
    /* Enforce light theme text colors for main content only */
    .block-container h1, .block-container h2, .block-container h3, 
    .block-container p, .block-container span, .block-container label, .block-container div {
        color: #333333 !important;
    }
    
    /* 1. Sidebar specific styling */
    [data-testid="stSidebar"] {
        padding-top: 2rem !important;
    }
    
    /* 2. Enforce light background for inputs */
    div[data-baseweb="input"] {
        background-color: #ffffff !important;
    }
    input, textarea {
        background-color: #ffffff !important;
        color: #333333 !important;
        -webkit-text-fill-color: #333333 !important;
    }
    
    /* Placeholder text specific styling */
    ::placeholder {
        color: #888888 !important;
        opacity: 1 !important;
    }

    /* Hide Streamlit elements *except* header on mobile so hamburger menu works */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Mobile header visibility, z-index, and notch support */
    header {
        background-color: #ffffff !important;
        z-index: 999999 !important;
        padding-top: env(safe-area-inset-top) !important;
    }
    
    /* Force hamburger menu icon color (Header/collapsed should be theme color, Sidebar close button should be white) */
    header button svg, button[kind="header"] svg, [data-testid="collapsedControl"] svg {
        fill: #4F46E5 !important;
        color: #4F46E5 !important;
    }
    [data-testid="stSidebar"] button svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }
    
    /* Headers */
    h1, h2, h3 {
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
        word-break: break-word; /* Prevent text overflow */
    }
    .custom-card p, .custom-card h2 {
        color: #333333 !important;
    }
    
    .initiative-card {
        background-color: white;
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 4px solid #27ae60;
        font-family: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif !important;
        color: #333333 !important;
        word-break: break-word;
    }
    
    /* Summary styling */
    .summary-text {
        font-size: 1.1rem;
        line-height: 1.8;
        color: #34495e !important;
    }

    /* 3. Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%; /* Default to full width for better tapping */
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.15) !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border-color: transparent !important;
    }
    
    /* 4. Responsive Design (Mobile) */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        h1 {
            font-size: 1.8rem !important;
            word-break: break-word;
        }
        h2 {
            font-size: 1.5rem !important;
            word-break: break-word;
        }
        h3 {
            font-size: 1.3rem !important;
            word-break: break-word;
        }
        .custom-card, .initiative-card {
            padding: 16px !important;
        }
        .custom-card h2 {
            font-size: 2rem !important; /* Scale down metric numbers */
        }
        .stButton>button {
            padding: 12px 20px !important; /* Larger touch target */
            font-size: 1rem !important;
        }
        .summary-text {
            font-size: 1rem !important;
        }
        
        /* Ensure columns stack or take proper width on mobile */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3038/3038290.png", width=100) # Placeholder logo
    st.title("AI ビジネススイート")
    st.markdown("統合型データ分析・抽出プラットフォーム")
    
    st.markdown("---")
    
    # Cookie Manager for persistent demo limits
    cookie_manager = stx.CookieManager()

    # Wait for cookies to load
    if not cookie_manager.get_all():
        pass # Wait one cycle if not ready
        
    MAX_DEMO_CALLS = 5
    
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
            "🟢 ESG経営分析",
            "🌐 Webデータ抽出",
            "📊 業界・競合トレンド",
            "🔗 ウェブフック連携",
            "📑 テキスト構造化 (AI)",
            "🔬 汎用データ抽出"
        ]
    )
    
    st.markdown("---")
    
    # プレミアムプラン向け API Key 入力
    with st.expander("🔑 プレミアムプランをご購入済みの方"):
        user_api_key = st.text_input("RapidAPI Keyを入力してください", type="password")
        st.caption("※RapidAPIで発行された「X-RapidAPI-Key」を入力すると、デモ制限が解除されます。")
        
    st.markdown("---")
    
    if user_api_key:
        st.success("✅ プレミアムモード（制限なし）")
    elif st.session_state.api_calls >= MAX_DEMO_CALLS:
        st.error(f"⚠️ 無料デモ版の利用制限（{MAX_DEMO_CALLS}回）に達しました。")
        st.markdown(
            '<a href="https://rapidapi.com/akbkuh00/api/esg-sustainability-score-api/pricing" target="_blank" style="display: block; width: 100%; padding: 10px; background-color: #e74c3c; color: white !important; text-align: center; text-decoration: none; border-radius: 5px; font-weight: bold; margin-top: 20px; animation: blinker 1.5s linear infinite;">🚀 プレミアムプラン（月額）へアップグレード</a>', 
            unsafe_allow_html=True
        )
        st.markdown("""<style>@keyframes blinker { 50% { opacity: 0.5; } }</style>""", unsafe_allow_html=True)
    else:
        st.markdown("### Powered by API")
        st.markdown("このデータを自身のアプリケーションで活用しませんか？")
        st.markdown(f"**デモ利用枠:** {MAX_DEMO_CALLS - st.session_state.api_calls}回 残り")
        st.markdown(
            '<a href="https://rapidapi.com/akbkuh00/api/esg-sustainability-score-api/pricing" target="_blank" style="display: block; width: 100%; padding: 10px; background-color: #8e44ad; color: white !important; text-align: center; text-decoration: none; border-radius: 5px; font-weight: bold; margin-top: 10px;">🚀 商用利用・APIプランを購読する</a>', 
            unsafe_allow_html=True
        )

def check_limit_and_increment():
    if user_api_key:
        return True # Bypass limit if user provides their own key
        
    if st.session_state.api_calls >= MAX_DEMO_CALLS:
        return False
    # Increment
    new_count = st.session_state.api_calls + 1
    st.session_state.api_calls = new_count
    # Set cookie (expires in 1 day to reset limits daily if they come back tomorrow, or we can make it longer)
    import datetime as dt
    cookie_manager.set("esg_demo_api_calls", str(new_count), expires_at=dt.datetime.now() + dt.timedelta(days=1))
    return True

def call_api(endpoint, method="GET", params=None, json_data=None):
    url = f"https://{RAPIDAPI_HOST}/api/v1{endpoint}"
    
    # Use user-provided API key if available, otherwise fallback to .env key
    active_api_key = user_api_key if user_api_key else RAPIDAPI_KEY
    
    headers = {
        "X-RapidAPI-Key": active_api_key,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "Content-Type": "application/json"
    }
    
    try:
        if not active_api_key or not RAPIDAPI_HOST:
             st.error("APIキーまたはホストが設定されていません。.envファイルと環境変数を確認するか、サイドバーからAPIキーを入力してください。")
             return None
             
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=json_data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"APIリクエストエラー: {e}")
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
        label="📄 診断レポート(PDF)をダウンロード",
        data=pdf_data,
        file_name=f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

if app_mode == "🟢 ESG経営分析":
    st.title("🌍 ESG 経営分析ダッシュボード")
    st.markdown("**概要:** 企業のサステナビリティ実績を即座にAIスコア化します。")
    st.info("**💡 活用事例:** サプライチェーン企業のESGリスクのスクリーニング / 投資案件の初期デューデリジェンス資料の作成")
    st.write("")
    with st.form(key='esg_form'):
        col1, col2 = st.columns([3, 1])
        company_name = col1.text_input("企業名", placeholder="例：トヨタ自動車、ソニーグループ", label_visibility="collapsed")
        submit_button = col2.form_submit_button(label='🔍 分析を実行', use_container_width=True)

    if submit_button and company_name:
        if not check_limit_and_increment():
            st.error("デモ利用制限に達しています。サイドバーからプレミアムプランへアップグレードしてください。")
        else:
            with st.spinner(f"AIが「{company_name}」のESG開示情報を深掘りしています..."):
                data = call_api("/esg-score", params={"query": company_name})
                
                if data and "esg_score" in data:
                    st.success("分析が完了しました！")
                    
                    def get_color(score):
                        if score == "N/A": return "#7f8c8d"
                        try:
                            s = float(score)
                            if s >= 80: return "#27ae60"
                            elif s >= 60: return "#f39c12"
                            else: return "#e74c3c"
                        except: return "#7f8c8d"
                    
                    def render_metric(label, value):
                        color = get_color(value)
                        return f'''<div class="custom-card" style="text-align: center; padding: 15px; border-left: 5px solid {color}; border-top: 5px solid {color};"><p style="color: #7f8c8d; font-size: 1.1rem; margin-bottom: 5px; font-weight: bold;">{label}</p><h2 style="color: {color}; font-size: 2.8rem; margin: 0;">{value}</h2></div>'''
    
                    st.markdown("## 📊 ESG 評価スコア")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.markdown(render_metric("総合スコア", data.get("esg_score", "N/A")), unsafe_allow_html=True)
                    c2.markdown(render_metric("環境 (E)", data.get("environmental_score", "N/A")), unsafe_allow_html=True)
                    c3.markdown(render_metric("社会 (S)", data.get("social_score", "N/A")), unsafe_allow_html=True)
                    c4.markdown(render_metric("ガバナンス (G)", data.get("governance_score", "N/A")), unsafe_allow_html=True)
                    
                    st.markdown("## 📝 分析エグゼクティブ・サマリー")
                    st.markdown(f'<div class="custom-card"><p class="summary-text">{data.get("summary", "サマリーなし")}</p></div>', unsafe_allow_html=True)
                    
                    st.markdown("## 💡 主要なサステナビリティ活動")
                    initiatives = data.get("key_initiatives", [])
                    if initiatives:
                        for init in initiatives:
                            st.markdown(f'<div class="initiative-card"><b>✓</b> {init}</div>', unsafe_allow_html=True)
                    
                    render_pdf_download_button(f"ESG分析 ({company_name})", data, mode="esg")

elif app_mode == "🌐 Webデータ抽出":
    st.title("🌐 Webデータ抽出ツール")
    st.markdown("**概要:** 指定したURLから、AIが意味を理解して必要なビジネスデータだけをピンポイントで抽出します。")
    st.info("**💡 活用事例:** 競合他社のHPからの役員一覧や資本金データの自動収集 / 特定のニュースサイトからの記事本文だけの抽出")
    st.write("")
    with st.form(key='web_form'):
        col1, col2 = st.columns([3, 1])
        url = col1.text_input("抽出対象のURL", placeholder="https://example.com/news/123", label_visibility="collapsed")
        submit_button = col2.form_submit_button(label='⚡ 抽出を実行', use_container_width=True)

    if submit_button and url:
        if not check_limit_and_increment():
            st.error("デモ利用制限に達しています。サイドバーからプレミアムプランへアップグレードしてください。")
        else:
            with st.spinner("AIが指定されたURLの文脈を読み解き、情報を抽出しています..."):
                data = call_api("/web-extract", params={"url": url})
                if data:
                    st.success("抽出完了")
                    st.json(data)
                    render_pdf_download_button("Webデータ抽出結果", data, mode="web_extract")

elif app_mode == "📊 業界・競合トレンド":
    st.title("📊 業界・競合トレンド分析")
    st.markdown("**概要:** ニッチなキーワードから、世界中の最新ニュースとトレンドをAIが要約・構造化します。")
    st.info("**💡 活用事例:** 新規事業の企画会議に向けた、特定市場（例：EVバッテリー、アニメ市場）の最新動向レポートの自動生成")
    st.write("")
    with st.form(key='niche_form'):
        col1, col2 = st.columns([3, 1])
        query = col1.text_input("分析キーワード", placeholder="例：国内EV市場の動向", label_visibility="collapsed")
        submit_button = col2.form_submit_button(label='📈 分析を実行', use_container_width=True)

    if submit_button and query:
        if not check_limit_and_increment():
            st.error("デモ利用制限に達しています。サイドバーからプレミアムプランへアップグレードしてください。")
        else:
            with st.spinner("AIがグローバル・ローカルトレンドを統合分析しています..."):
                data = call_api("/niche-data", params={"query": query})
                if data:
                    st.success("分析完了")
                    st.json(data)
                    render_pdf_download_button("業界・競合トレンド", data, mode="niche")

elif app_mode == "🔗 ウェブフック連携":
    st.title("🔗 ウェブフック連携テスト")
    st.markdown("**概要:** ZapierやMake、自社システムへ分析データを自動送信するための機能です。")
    st.info("**💡 活用事例:** ESG分析結果やスクレイピングデータを、指定したURLへPOST送信して後続のフロー（Slack通知、スプレッドシートへの記録等）をトリガーします。")
    
    st.markdown("### Step 1: 送信先URLの設定")
    st.write("受け取り側のウェブフックURLを入力してください（Zapier, Make, 独自のAPIなど）。")
    
    with st.form(key='webhook_form'):
        webhook_url = st.text_input("ウェブフックURL", placeholder="https://hooks.zapier.com/hooks/catch/12345/abcde")
        
        st.markdown("### Step 2: テスト送信")
        st.write("送信するテストデータ（JSONペイロード）を確認して送信します。")
        payload = st.text_area("テストペイロード (JSON形式)", value='{\n  "event": "data_extracted",\n  "source": "AI Business Suite",\n  "data": {\n    "message": "Webhook test successful!",\n    "timestamp": "2024-02-24T12:00:00Z"\n  }\n}', height=150)
        
        submit_button = st.form_submit_button(label='🚀 送信テストを実行', use_container_width=True)

    with st.expander("👉 送信されるJSONデータ（ペイロード）の構造について"):
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
                data = call_api("/webhook", method="POST", json_data={"url": webhook_url, "payload": json_payload})
                if data:
                    st.success("送信完了")
                    st.json(data)
                    render_pdf_download_button("Webhook送信結果", data)
            except json.JSONDecodeError:
                st.error("ペイロードは有効なJSON形式で入力してください。")

elif app_mode == "📑 テキスト構造化 (AI)":
    st.title("📑 テキスト構造化 (AI)")
    st.markdown("**概要:** カオスな長文メモや議事録を、開発者やシステムが読み込める綺麗なJSONデータに変換します。")
    st.info("**💡 活用事例:** 商談の雑多な音声文字起こしデータから、BANT条件（予算・時期など）を自動抽出してCRMへ入力")
    st.write("")
    with st.form(key='text_to_json_form'):
        text_input = st.text_area("構造化したいテキストを入力", height=150, placeholder="ここに議事録やメモを貼り付けてください...")
        submit_button = st.form_submit_button(label='✨ 構造化を実行', use_container_width=True)

    if submit_button and text_input:
        if not check_limit_and_increment():
            st.error("デモ利用制限に達しています。サイドバーからプレミアムプランへアップグレードしてください。")
        else:
            with st.spinner("AIが非構造化テキストを解析し、綺麗なJSON形式に変換しています..."):
                data = call_api("/text-to-json", method="POST", json_data={"text": text_input})
                if data:
                    st.success("構造化完了")
                    st.json(data)
                    render_pdf_download_button("テキスト構造化結果", data, mode="text_to_json")

elif app_mode == "🔬 汎用データ抽出":
    st.title("🔬 汎用データ抽出 (AI Scrape API)")
    st.markdown("**概要:** 指定したURLから、AIに指示した特定の情報（例：価格一覧、担当者名など）だけをピンポイントで抽出します。")
    st.info("**💡 活用事例:** 特定の法人URLからの代表者名と資本金の抽出 / ECサイトの商品ページからの価格やスペック情報の取得")
    
    with st.expander("📋 よくある抽出の指示例（プロンプト・テンプレート）"):
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
        submit_button = st.form_submit_button(label='🕷️ AIでスクレイピングを実行', use_container_width=True)

    if submit_button and scrape_url and prompt:
        if not check_limit_and_increment():
            st.error("デモ利用制限に達しています。サイドバーからプレミアムプランへアップグレードしてください。")
        else:
            with st.spinner("AIエージェントがターゲットURLにアクセスし、指定された情報を抽出しています..."):
                data = call_api("/ai_scrape_api_v1_ai_scrape_post", method="POST", json_data={"url": scrape_url, "prompt": prompt})
                if data:
                    st.success("抽出完了")
                    st.json(data)
                    render_pdf_download_button("汎用データ抽出結果", data, mode="generic")
