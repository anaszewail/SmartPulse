import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd
import os
import io
import requests
import json
from prophet import Prophet
import uuid
import time
from datetime import datetime, timedelta

# إعداد الخط العربي
if not os.path.exists("/tmp/Amiri-Regular.ttf"):
    os.system("wget https://github.com/alef.type/amiri/raw/master/Amiri-Regular.ttf -O /tmp/Amiri-Regular.ttf")

# إعداد الصفحة بتصميم فاخر عالمي المستوى
st.set_page_config(
    page_title="SmartPulse™ - Elite Data Intelligence",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS محسّن لتصميم فاخر وبيع مثالي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;900&display=swap');
    
    * {font-family: 'Poppins', sans-serif;}
    
    .main {
        background: linear-gradient(135deg, #0D1B2A, #1B263B);
        color: #F8FAFC;
        padding: 40px;
        border-radius: 30px;
        box-shadow: 0 12px 40px rgba(0,0,0,0.6);
    }
    
    h1, h2, h3 {
        background: linear-gradient(90deg, #FFD700, #FF8C00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        letter-spacing: -1px;
        text-shadow: 0 2px 10px rgba(255,215,0,0.3);
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #FFD700, #FF8C00);
        color: #0D1B2A;
        border-radius: 50px;
        font-weight: 700;
        padding: 18px 40px;
        font-size: 20px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: none;
        box-shadow: 0 10px 25px rgba(255,215,0,0.4);
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    .stButton>button:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 15px 35px rgba(255,215,0,0.6);
    }
    
    .stButton>button:active {
        transform: translateY(2px);
    }
    
    .stTextInput>div>div>input {
        background: rgba(255,255,255,0.1);
        border: 2px solid #FFD700;
        border-radius: 15px;
        color: #FFFFFF;
        padding: 15px;
        font-size: 18px;
        box-shadow: 0 5px 20px rgba(255,215,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #FF8C00;
        box-shadow: 0 5px 25px rgba(255,140,0,0.4);
    }
    
    .stTextInput>label, .stSelectbox>label, .stRadio>label {
        color: #FFD700;
        font-size: 26px;
        font-weight: 600;
        text-shadow: 1px 1px 5px rgba(0,0,0,0.5);
        margin-bottom: 10px;
    }
    
    .stSelectbox>div>div>div {
        background: rgba(255,255,255,0.1);
        border: 2px solid #FFD700;
        border-radius: 15px;
        color: #FFFFFF;
        padding: 15px;
        font-size: 18px;
        box-shadow: 0 5px 20px rgba(255,215,0,0.2);
    }
    
    .stRadio>div {
        background: rgba(255,255,255,0.05);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    
    .stMarkdown {
        color: #E2E8F0;
        font-size: 20px;
        line-height: 1.8;
    }
    
    .share-btn {
        background: linear-gradient(90deg, #00C853, #00E676);
        color: #FFFFFF;
        border-radius: 50px;
        padding: 15px 30px;
        text-decoration: none;
        transition: all 0.3s ease;
        box-shadow: 0 8px 20px rgba(0,200,83,0.4);
        font-size: 18px;
        font-weight: 600;
        text-align: center;
        margin: 10px 0;
    }
    
    .share-btn:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,230,118,0.6);
    }
    
    .stSpinner>div {
        border-color: #FFD700 transparent #FFD700 transparent;
    }
    
    .buy-premium-btn {
        background: linear-gradient(90deg, #FF5722, #FF9800);
        color: #FFFFFF;
        border-radius: 50px;
        font-weight: 700;
        padding: 20px 50px;
        font-size: 24px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 12px 30px rgba(255,87,34,0.5);
        text-align: center;
        width: 100%;
        text-decoration: none;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin: 30px 0;
        position: relative;
        overflow: hidden;
    }
    
    .buy-premium-btn:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 15px 40px rgba(255,152,0,0.7);
    }
    
    .buy-premium-btn:after {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: rgba(255,255,255,0.1);
        transform: rotate(30deg);
        transition: all 0.8s ease;
    }
    
    .buy-premium-btn:hover:after {
        transform: rotate(30deg) translateX(100%);
    }
    
    .countdown-timer {
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        margin: 30px 0;
        border: 2px solid rgba(255,215,0,0.3);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        animation: pulse 2s infinite;
    }
    
    .countdown-value {
        font-size: 48px;
        font-weight: 700;
        background: linear-gradient(90deg, #FFD700, #FF8C00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin-bottom: 8px;
    }
    
    .countdown-label {
        font-size: 16px;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: rgba(255,255,255,0.7);
    }
    
    @keyframes pulse {
        0% {transform: scale(1); box-shadow: 0 10px 25px rgba(255,215,0,0.4);}
        50% {transform: scale(1.03); box-shadow: 0 15px 35px rgba(255,215,0,0.6);}
        100% {transform: scale(1); box-shadow: 0 10px 25px rgba(255,215,0,0.4);}
    }
    
    .animate-in {
        animation: fadeInUp 1s forwards;
        opacity: 0;
    }
    
    @keyframes fadeInUp {
        from {opacity: 0; transform: translateY(20px);}
        to {opacity: 1; transform: translateY(0);}
    }
    </style>
""", unsafe_allow_html=True)

# تعريف الحالة الافتراضية
if "language" not in st.session_state:
    st.session_state["language"] = "English"
if "payment_verified" not in st.session_state:
    st.session_state["payment_verified"] = False
if "payment_initiated" not in st.session_state:
    st.session_state["payment_initiated"] = False
if "report_generated" not in st.session_state:
    st.session_state["report_generated"] = False
if "payment_url" not in st.session_state:
    st.session_state["payment_url"] = None

# زر كبير في الأعلى
if st.session_state["payment_url"]:
    st.markdown(f'<a href="{st.session_state["payment_url"]}" target="_blank" class="buy-premium-btn animate-in">Buy Premium Insights Now</a>', unsafe_allow_html=True)
else:
    st.markdown('<a href="#" class="buy-premium-btn animate-in">Buy Premium Insights Now</a>', unsafe_allow_html=True)

# العنوان والوصف
st.markdown("""
    <h1 style="font-size: 60px; text-align: center; animation: fadeInUp 1s forwards;">SmartPulse™</h1>
    <p style="font-size: 24px; text-align: center; opacity: 0.9; animation: fadeInUp 1s forwards; animation-delay: 0.2s;">
        Unleash Elite Data Intelligence – Dominate Your Market Today!<br>
        <em>Crafted by Anas Hani Zewail • Contact: +201024743503</em>
    </p>
""", unsafe_allow_html=True)

# واجهة المستخدم المحسنة
st.markdown("<h2 style='text-align: center; animation: fadeInUp 1s forwards; animation-delay: 0.4s;'>Master Your Data in Seconds</h2>", unsafe_allow_html=True)
keyword = st.text_input("Enter Your Topic (e.g., iPhone 15):", "iPhone 15", key="keyword_input", help="Unlock insights for any topic instantly!")
language = st.selectbox("Select Language:", ["English", "Arabic"], index=0, key="language_select")
st.session_state["language"] = language
plan = st.radio("Choose Your Plan:", ["Free Insights", "Premium Insights ($10)"], key="plan_radio")
st.markdown("""
    <p style="text-align: center; animation: fadeInUp 1s forwards; animation-delay: 0.6s;">
        <strong>Free Insights:</strong> Get a stunning chart instantly – share the brilliance!<br>
        <strong>Premium Insights ($10):</strong> Unlock 30-day forecasts, smart strategies, and a premium PDF report – payment opens automatically!
    </p>
""", unsafe_allow_html=True)

# بيانات PayPal Sandbox
PAYPAL_CLIENT_ID = "AQd5IZObL6YTejqYpN0LxADLMtqbeal1ahbgNNrDfFLcKzMl6goF9BihgMw2tYnb4suhUfprhI-Z8eoC"
PAYPAL_SECRET = "EPk46EBw3Xm2W-R0Uua8sLsoDLJytgSXqIzYLbbXCk_zSOkdzFx8jEbKbKxhjf07cnJId8gt6INzm6_V"
PAYPAL_API = "https://api-m.sandbox.paypal.com"

# دوال PayPal
def get_paypal_access_token():
    url = f"{PAYPAL_API}/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET), data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        st.error("Failed to connect to PayPal. Try again later.")
        return None

def create_payment(access_token):
    url = f"{PAYPAL_API}/v1/payments/payment"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    payment_data = {
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "transactions": [{
            "amount": {"total": "10.00", "currency": "USD"},
            "description": "SmartPulse Premium Insights"
        }],
        "redirect_urls": {
            "return_url": "https://smartpulse-nwrkb9xdsnebmnhczyt76s.streamlit.app/?success=true",
            "cancel_url": "https://smartpulse-nwrkb9xdsnebmnhczyt76s.streamlit.app/?cancel=true"
        }
    }
    response = requests.post(url, headers=headers, json=payment_data)
    if response.status_code == 201:
        for link in response.json()["links"]:
            if link["rel"] == "approval_url":
                return link["href"]
    st.error("Failed to create payment request.")
    return None

# بيانات وهمية
sentiment = {"positive": {"strong": 30, "mild": 20}, "negative": {"strong": 10, "mild": 15}, "neutral": 25}
total_posts = 100
sentiment_by_day = {
    "2025-02-20_pos_strong": 10, "2025-02-20_pos_mild": 5, "2025-02-20_neg_strong": 3,
    "2025-02-21_pos_strong": 12, "2025-02-21_pos_mild": 6, "2025-02-21_neg_strong": 4,
    "2025-02-22_pos_strong": 8, "2025-02-22_pos_mild": 4, "2025-02-22_neg_strong": 2
}
sentiment_by_country = {"Egypt": {"positive": {"strong": 20, "mild": 10}, "negative": {"strong": 5, "mild": 5}, "neutral": 10}}
countries, trends, sub_keywords, speakers = ["Egypt"], [("tech", 50)], [("phone", 30)], 80

# دوال التحليل
def generate_pie_chart(keyword, language, sentiment, total_posts):
    labels = ["Strong Positive", "Mild Positive", "Strong Negative", "Mild Negative", "Neutral"] if language == "English" else ["إيجابي قوي", "إيجابي خفيف", "سلبي قوي", "سلبي خفيف", "محايد"]
    sizes = [sentiment["positive"]["strong"], sentiment["positive"]["mild"], sentiment["negative"]["strong"], sentiment["negative"]["mild"], sentiment["neutral"]]
    colors = ["#2ECC71", "#A9DFBF", "#E74C3C", "#F1948A", "#95A5A6"]
    plt.figure(figsize=(8, 6))
    wedges, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90, shadow=True, textprops={'fontsize': 14, 'color': 'white'})
    for w in wedges:
        w.set_edgecolor('#FFD700')
        w.set_linewidth(2)
    plt.title(f"{keyword} Sentiment Analysis", fontsize=18, color="white", pad=20)
    plt.gca().set_facecolor('#0D1B2A')
    plt.gcf().set_facecolor('#0D1B2A')
    pie_file = f"pie_{keyword}.png"
    plt.savefig(pie_file, dpi=300, bbox_inches="tight")
    plt.close()
    return pie_file

def generate_forecast(keyword, language, sentiment_by_day):
    days = sorted(set(k.split("_")[0] for k in sentiment_by_day.keys()))
    total_sentiment = [sum(sentiment_by_day.get(f"{day}_{x}", 0) for x in ["pos_strong", "pos_mild"]) - sum(sentiment_by_day.get(f"{day}_{x}", 0) for x in ["neg_strong", "neg_mild"]) for day in days]
    df = pd.DataFrame({'ds': days, 'y': total_sentiment})
    df['ds'] = pd.to_datetime(df['ds'])
    model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=True)
    model.fit(df)
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    plt.figure(figsize=(10, 6))
    plt.plot(df['ds'], df['y'], label="Actual", color="#2ECC71", linewidth=2.5)
    plt.plot(forecast['ds'], forecast['yhat'], label="Forecast", color="#FFD700", linewidth=2.5)
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color="#FFD700", alpha=0.3, label="Confidence")
    plt.legend(fontsize=12, loc="upper left", facecolor="#0D1B2A", edgecolor="white", labelcolor="white")
    plt.title(f"{keyword} 30-Day Forecast", fontsize=18, color="white", pad=20)
    plt.gca().set_facecolor('#0D1B2A')
    plt.gcf().set_facecolor('#0D1B2A')
    plt.xticks(color="white", fontsize=12)
    plt.yticks(color="white", fontsize=12)
    forecast_file = f"forecast_{keyword}.png"
    plt.savefig(forecast_file, dpi=300, bbox_inches="tight")
    plt.close()
    trend = "Upward" if forecast['yhat'].iloc[-1] > forecast['yhat'].iloc[-31] else "Downward"
    reco = f"Trend: {trend}. Increase investment if upward or adjust strategy if downward."
    return forecast_file, reco

def generate_report(keyword, language, countries, trends, sub_keywords, sentiment, sentiment_by_day, sentiment_by_country, speakers, total_posts, pie_chart, forecast_chart):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontSize = 12
    style.textColor = colors.black
    try:
        pdfmetrics.registerFont(TTFont("Amiri", "/tmp/Amiri-Regular.ttf"))
        style.fontName = "Helvetica" if language == "English" else "Amiri"
    except:
        style.fontName = "Helvetica"
    
    report = f"SmartPulse Analysis Report for {keyword}\n"
    report += "=" * 50 + "\n"
    report += f"Total Sources: {total_posts}\n"
    content = [Paragraph(report if language == "English" else arabic_reshaper.reshape(report), style)]
    content.append(Image(pie_chart, width=400, height=300))
    content.append(Image(forecast_chart, width=400, height=300))
    content.append(Spacer(1, 20))
    doc.build(content)
    buffer.seek(0)
    return buffer.getvalue()

# تشغيل الأداة
if st.button("Unlock Insights Now!", key="generate_insights"):
    with st.spinner("Processing Your Insights..."):
        pie_chart = generate_pie_chart(keyword, language, sentiment, total_posts)
        st.image(pie_chart, caption="Sentiment Overview")
        
        share_url = "https://smartpulse-nwrkb9xdsnebmnhczyt76s.streamlit.app/"
        telegram_group = "https://t.me/+K7W_PUVdbGk4MDRk"
        
        st.markdown("<h3 style='text-align: center; animation: fadeInUp 1s forwards;'>Love It? Share the Power!</h3>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<a href="https://api.whatsapp.com/send?text=Try%20SmartPulse:%20{share_url}" target="_blank" class="share-btn">WhatsApp</a>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<a href="https://t.me/share/url?url={share_url}&text=SmartPulse%20rocks!" target="_blank" class="share-btn">Telegram</a>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<a href="https://www.facebook.com/sharer/sharer.php?u={share_url}" target="_blank" class="share-btn">Messenger</a>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<a href="https://discord.com/channels/@me?message=Check%20SmartPulse:%20{share_url}" target="_blank" class="share-btn">Discord</a>', unsafe_allow_html=True)
        
        st.markdown(f"<p style='text-align: center; animation: fadeInUp 1s forwards;'>Join our Telegram community: <a href='{telegram_group}' target='_blank'>Click Here</a></p>", unsafe_allow_html=True)
        
        if plan == "Premium Insights ($10)":
            if not st.session_state["payment_verified"] and not st.session_state["payment_initiated"]:
                access_token = get_paypal_access_token()
                if access_token:
                    approval_url = create_payment(access_token)
                    if approval_url:
                        st.session_state["payment_url"] = approval_url
                        st.session_state["payment_initiated"] = True
                        unique_id = uuid.uuid4()
                        st.markdown(f"""
                            <a href="{approval_url}" target="_blank" id="paypal_auto_link_{unique_id}" style="display:none;">PayPal</a>
                            <script>
                                setTimeout(function() {{
                                    document.getElementById("paypal_auto_link_{unique_id}").click();
                                }}, 100);
                            </script>
                        """, unsafe_allow_html=True)
                        st.info("Payment window opened automatically. Complete it to unlock premium insights!")
            elif st.session_state["payment_verified"]:
                forecast_chart, reco = generate_forecast(keyword, language, sentiment_by_day)
                st.image(forecast_chart, caption="30-Day Forecast")
                st.write(reco)
                pdf_data = generate_report(keyword, language, countries, trends, sub_keywords, sentiment, sentiment_by_day, sentiment_by_country, speakers, total_posts, pie_chart, forecast_chart)
                st.download_button(
                    label="Download Full Report (PDF)",
                    data=pdf_data,
                    file_name=f"{keyword}_smartpulse_report.pdf",
                    mime="application/pdf",
                    key="download_report"
                )
                st.session_state["report_generated"] = True
                st.markdown(f"Earn a FREE report! Invite 5 friends: [Share Now]({share_url})")
                st.markdown(f"Join our Telegram: [Click Here]({telegram_group})")
        else:
            st.info("Upgrade to Premium ($10) for 30-day forecasts and more!")

# زر كبير في الأسفل
if st.session_state["payment_url"]:
    st.markdown(f'<a href="{st.session_state["payment_url"]}" target="_blank" class="buy-premium-btn animate-in">Buy Premium Insights Now</a>', unsafe_allow_html=True)
else:
    st.markdown('<a href="#" class="buy-premium-btn animate-in">Buy Premium Insights Now</a>', unsafe_allow_html=True)

# التحقق من الدفع
query_params = st.query_params
if "success" in query_params and query_params["success"] == "true" and not st.session_state["payment_verified"]:
    st.session_state["payment_verified"] = True
    st.session_state["payment_initiated"] = False
    st.success("Payment successful! Your premium insights are now unlocked.")
elif "cancel" in query_params:
    st.session_state["payment_initiated"] = False
    st.warning("Payment canceled. Retry Premium for full access.")
