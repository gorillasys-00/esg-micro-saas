# AI Business Suite - Technical Documentation (Frontend)

## 1. Overview
A premium Streamlit-based dashboard for business data visualization and AI analysis.

## 2. Key Features
- **ESG Analysis**: Visual scorecards with PDF export.
- **Trend Monitoring**: Real-time niche intelligence.
- **Webhook Integration**: Direct external data routing (Zapier/Make support).
- **Premium Mode**: Dynamic limit management via RapidAPI Key validation.

## 3. Core Logic (app.py)
- **Session State**: Manages state for analysis results and demo limits.
- **Persistence**: `extra_streamlit_components` (CookieManager) used to track usage limits across refreshes.
- **Direct Webhook**: Logic to post payloads directly to external URLs, bypassing backend proxying for maximum compatibility.

## 4. UI/UX Specifications
- **Theme**: High-contrast, vibrant professional palette.
- **Typography**: Inter (Google Fonts).
- **Responsive Elements**: Custom CSS for cards, buttons, and sidebar visibility.

## 5. Version History
- `v1.1.7`: JSON Schema Alignment.
- `v1.1.8`: AI Caching Integration.
- `v1.1.9`: Webhook Usage Enhancement (Current Stable).
