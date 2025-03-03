import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd
import io
import requests
import json
from prophet import Prophet
import uuid
import arabic_reshaper
from bidi.algorithm import get_display

# إعداد الصفحة بتصميم فاخر
st.set_page_config(
    page_title="SmartPulse™ - Ultimate Data Insights",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS محسّن لتصميم جذاب وحديث
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;900&display=swap');
    
    * {font-family: 'Poppins', sans-serif;}
    
    .main {
        background: linear-gradient(135deg, #1A1A40, #2A4066);
        color: #F8FAFC;
        padding: 40px;
        border-radius: 30px;
        box-shadow: 0 15px 50px rgba(0,0,0,0.7);
    }
    
    h1, h2, h3 {
        background: linear-gradient(90deg, #FF6F61, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        letter-spacing: -1px;
        text-shadow: 0 3px 15px rgba(255,111,97,0.5);
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #FF6F61, #FFAA00);
        color: #FFFFFF;
        border-radius: 50px;
        font-weight: 700;
        padding: 18px 40px;
        font-size: 20px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: none;
        box-shadow: 0 10px 25px rgba(255,111,97,0.5);
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    .stButton>button:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 15px 40px rgba(255,170,0,0.7);
    }
    
    .stTextInput>div>div>input {
        background: rgba(255,255,255,0.15);
        border: 2px solid #FF6F61;
        border-radius: 15px;
        color: #FFAA00;
        font-weight: bold;
        padding: 15px;
        font-size: 18px;
        box-shadow: 0 5px 20px rgba(255,111,97,0.3);
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #FFD700;
        box-shadow: 0 5px 25px rgba(255,215,0,0.5);
    }
    
    .stSelectbox>label, .stRadio>label {
        color: #FFAA00;
        font-size: 26px;
        font-weight: 600;
        text-shadow: 1px 1px 5px rgba(0,0,0,0.5);
    }
    
    .stSelectbox>div>div>button {
        background: rgba(255,255,255,0.15);
        border: 2px solid #FF6F61;
        border-radius: 15px;
        color: #F8FAFC;
        padding: 15px;
        font-size: 18px;
        box-shadow: 0 5px 20px rgba(255,111,97,0.3);
    }
    
    .stRadio>div {
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    }
    
    .stMarkdown {
        color: #E2E8F0;
        font-size: 20px;
        line-height: 1.8;
        text-shadow: 0 1px 3px rgba(0,0,0,0.5);
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
    }
    
    .share-btn:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,230,118,0.6);
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
if "pie_chart_buffer" not in st.session_state:
    st.session_state["pie_chart_buffer"] = None
if "forecast_chart_buffer" not in st.session_state:
    st.session_state["forecast_chart_buffer"] = None

# العنوان والترحيب
st.markdown("""
    <h1 style='font-size: 60px; text-align: center; animation: fadeInUp 1s forwards;'>SmartPulse™</h1>
    <p style='font-size: 24px; text-align: center; animation: fadeInUp 1s forwards; animation-delay: 0.2s;'>
        Discover Insights That Drive Success – Instantly!<br>
        <em>By Anas Hani Zewail • Contact: +201024743503</em>
    </p>
""", unsafe_allow_html=True)

# واجهة المستخدم
st.markdown("<h2 style='text-align: center; animation: fadeInUp 1s forwards;'>Unlock Your Data Power</h2>", unsafe_allow_html=True)
keyword = st.text_input("Enter Your Topic (e.g., Tesla Trends):", "Tesla Trends", help="Get insights on any topic!")
language = st.selectbox("Select Language:", ["English", "Arabic"])
st.session_state["language"] = language
plan = st.radio("Choose Your Plan:", ["Free Preview", "Basic Insights ($5)", "Premium Insights ($10)", "Elite Insights ($20)", "Monthly Subscription ($15/month)"])
st.markdown("""
    <p style='text-align: center;'>
        <strong>Free Preview:</strong> Quick chart sneak peek<br>
        <strong>Basic ($5):</strong> Chart + Basic Report<br>
        <strong>Premium ($10):</strong> Chart + Forecast + Full Report<br>
        <strong>Elite ($20):</strong> All + Advanced Analytics<br>
        <strong>Monthly ($15/month):</strong> Unlimited Insights!
    </p>
""", unsafe_allow_html=True)

# بيانات PayPal Sandbox
PAYPAL_CLIENT_ID = "AQd5IZObL6YTejqYpN0LxADLMtqbeal1ahbgNNrDfFLcKzMl6goF9BihgMw2tYnb4suhUfprhI-Z8eoC"
PAYPAL_SECRET = "EPk46EBw3Xm2W-R0Uua8sLsoDLJytgSXqIzYLbbXCk_zSOkdzFx8jEbKbKxhjf07cnJId8gt6INzm6_V"
PAYPAL_API = "https://api-m.sandbox.paypal.com"

# دوال PayPal مع معالجة الأخطاء
def get_paypal_access_token():
    try:
        url = f"{PAYPAL_API}/v1/oauth2/token"
        headers = {"Accept": "application/json", "Accept-Language": "en_US"}
        data = {"grant_type": "client_credentials"}
        response = requests.post(url, headers=headers, auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET), data=data)
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        st.error(f"Failed to connect to PayPal: {e}")
        return None

def create_payment(access_token, amount, description):
    try:
        url = f"{PAYPAL_API}/v1/payments/payment"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        payment_data = {
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "transactions": [{
                "amount": {"total": amount, "currency": "USD"},
                "description": description
            }],
            "redirect_urls": {
                "return_url": "https://smartpulse-nwrkb9xdsnebmnhczyt76s.streamlit.app/?success=true",
                "cancel_url": "https://smartpulse-nwrkb9xdsnebmnhczyt76s.streamlit.app/?cancel=true"
            }
        }
        response = requests.post(url, headers=headers, json=payment_data)
        response.raise_for_status()
        for link in response.json()["links"]:
            if link["rel"] == "approval_url":
                return link["href"]
        st.error("Failed to extract payment URL.")
        return None
    except Exception as e:
        st.error(f"Failed to create payment request: {e}")
        return None

# بيانات وهمية واقعية
sentiment = {"positive": {"strong": 45, "mild": 25}, "negative": {"strong": 10, "mild": 15}, "neutral": 20}
total_posts = 150
sentiment_by_day = {
    "2025-02-25_pos_strong": 15, "2025-02-25_pos_mild": 10, "2025-02-25_neg_strong": 5,
    "2025-02-26_pos_strong": 20, "2025-02-26_pos_mild": 8, "2025-02-26_neg_strong": 3,
    "2025-02-27_pos_strong": 10, "2025-02-27_pos_mild": 7, "2025-02-27_neg_strong": 2
}
sentiment_by_country = {"USA": {"positive": {"strong": 30, "mild": 15}, "negative": {"strong": 5, "mild": 5}, "neutral": 10}}
countries, trends, sub_keywords, speakers = ["USA"], [("innovation", 60)], [("tech", 40)], 120

# دوال التحليل مع معالجة الصور في الذاكرة
def generate_pie_chart(keyword, language, sentiment, total_posts):
    try:
        labels = ["Strong Positive", "Mild Positive", "Strong Negative", "Mild Negative", "Neutral"] if language == "English" else ["إيجابي قوي", "إيجابي خفيف", "سلبي قوي", "سلبي خفيف", "محايد"]
        sizes = [sentiment["positive"]["strong"], sentiment["positive"]["mild"], sentiment["negative"]["strong"], sentiment["negative"]["mild"], sentiment["neutral"]]
        colors = ["#2ECC71", "#A9DFBF", "#E74C3C", "#F1948A", "#95A5A6"]
        plt.figure(figsize=(8, 6))
        wedges, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90, shadow=True, textprops={'fontsize': 14, 'color': 'white'})
        for w in wedges:
            w.set_edgecolor('#FFD700')
            w.set_linewidth(2)
        plt.title(f"{keyword} Sentiment Analysis", fontsize=18, color="white", pad=20)
        plt.gca().set_facecolor('#1A1A40')
        plt.gcf().set_facecolor('#1A1A40')
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches="tight")
        img_buffer.seek(0)
        plt.close()
        return img_buffer
    except Exception as e:
        st.error(f"Failed to generate pie chart: {e}")
        return None

def generate_forecast(keyword, language, sentiment_by_day):
    try:
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
        plt.legend(fontsize=12, loc="upper left", facecolor="#1A1A40", edgecolor="white", labelcolor="white")
        plt.title(f"{keyword} 30-Day Forecast", fontsize=18, color="white", pad=20)
        plt.gca().set_facecolor('#1A1A40')
        plt.gcf().set_facecolor('#1A1A40')
        plt.xticks(color="white", fontsize=12)
        plt.yticks(color="white", fontsize=12)
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches="tight")
        img_buffer.seek(0)
        plt.close()
        trend = "Upward" if forecast['yhat'].iloc[-1] > forecast['yhat'].iloc[-31] else "Downward"
        reco = f"Trend: {trend}. Invest more if upward, adjust if downward."
        return img_buffer, reco
    except Exception as e:
        st.error(f"Failed to generate forecast: {e}")
        return None, None

def generate_report(keyword, language, countries, trends, sub_keywords, sentiment, sentiment_by_day, sentiment_by_country, speakers, total_posts, pie_chart_buffer, forecast_chart_buffer=None, plan="Basic"):
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.fontSize = 12
        style.textColor = colors.black
        style.fontName = "Helvetica"  # خط مدمج مع Streamlit

        report = f"SmartPulse Analysis Report for {keyword}\n"
        report += "=" * 50 + "\n"
        report += f"Plan: {plan}\n"
        report += f"Total Sources: {total_posts}\n"
        if language == "Arabic":
            report = arabic_reshaper.reshape(report)
            report = get_display(report)

        content = [Paragraph(report, style)]
        content.append(Image(pie_chart_buffer, width=400, height=300))
        
        if forecast_chart_buffer and plan in ["Premium Insights ($10)", "Elite Insights ($20)", "Monthly Subscription ($15/month)"]:
            content.append(Image(forecast_chart_buffer, width=400, height=300))
            content.append(Spacer(1, 20))
        
        if plan == "Elite Insights ($20)":
            content.append(Paragraph("Advanced Analytics: Sentiment by Country - USA: 60% Positive, 20% Negative, 20% Neutral", style))
        
        doc.build(content)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Failed to generate report: {e}")
        return None

# تشغيل الأداة
if st.button("Get Insights Now!", key="generate_insights"):
    with st.spinner("Unlocking Your Insights..."):
        pie_chart_buffer = generate_pie_chart(keyword, language, sentiment, total_posts)
        if pie_chart_buffer:
            st.session_state["pie_chart_buffer"] = pie_chart_buffer.getvalue()
            st.image(pie_chart_buffer, caption="Sentiment Overview")
            
            share_url = "https://smartpulse-nwrkb9xdsnebmnhczyt76s.streamlit.app/"
            telegram_group = "https://t.me/+K7W_PUVdbGk4MDRk"
            
            st.markdown("<h3 style='text-align: center;'>Share the Power!</h3>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<a href="https://api.whatsapp.com/send?text=Try%20SmartPulse:%20{share_url}" target="_blank" class="share-btn">WhatsApp</a>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<a href="https://t.me/share/url?url={share_url}&text=SmartPulse%20rocks!" target="_blank" class="share-btn">Telegram</a>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<a href="https://www.facebook.com/sharer/sharer.php?u={share_url}" target="_blank" class="share-btn">Messenger</a>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<a href="https://discord.com/channels/@me?message=Check%20SmartPulse:%20{share_url}" target="_blank" class="share-btn">Discord</a>', unsafe_allow_html=True)
            
            st.markdown(f"<p style='text-align: center;'>Join our Telegram: <a href='{telegram_group}' target='_blank'>Click Here</a> - Invite 5 friends for a FREE report!</p>", unsafe_allow_html=True)
            
            if plan == "Free Preview":
                st.info("Upgrade to unlock full reports and forecasts!")
            else:
                if not st.session_state["payment_verified"] and not st.session_state["payment_initiated"]:
                    access_token = get_paypal_access_token()
                    if access_token:
                        amount = {"Basic Insights ($5)": "5.00", "Premium Insights ($10)": "10.00", "Elite Insights ($20)": "20.00", "Monthly Subscription ($15/month)": "15.00"}[plan]
                        approval_url = create_payment(access_token, amount, f"SmartPulse {plan}")
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
                            st.info(f"Payment window opened for {plan}. Complete it to unlock your insights!")
                elif st.session_state["payment_verified"]:
                    forecast_chart_buffer, reco = generate_forecast(keyword, language, sentiment_by_day) if plan in ["Premium Insights ($10)", "Elite Insights ($20)", "Monthly Subscription ($15/month)"] else (None, None)
                    if forecast_chart_buffer:
                        st.session_state["forecast_chart_buffer"] = forecast_chart_buffer.getvalue()
                        st.image(forecast_chart_buffer, caption="30-Day Forecast")
                        st.write(reco)
                    
                    pie_chart_buffer = io.BytesIO(st.session_state["pie_chart_buffer"])
                    forecast_chart_buffer = io.BytesIO(st.session_state["forecast_chart_buffer"]) if st.session_state["forecast_chart_buffer"] else None
                    pdf_data = generate_report(keyword, language, countries, trends, sub_keywords, sentiment, sentiment_by_day, sentiment_by_country, speakers, total_posts, pie_chart_buffer, forecast_chart_buffer, plan)
                    if pdf_data:
                        st.download_button(
                            label=f"Download Your {plan.split(' (')[0]} Report",
                            data=pdf_data,
                            file_name=f"{keyword}_smartpulse_report.pdf",
                            mime="application/pdf",
                            key="download_report"
                        )
                        st.session_state["report_generated"] = True
                        st.success(f"{plan.split(' (')[0]} Report Ready! Invite friends for more perks!")
