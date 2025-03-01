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
import os
import io
import requests
import json
from prophet import Prophet
import uuid
import arabic_reshaper
from bidi.algorithm import get_display

# إعداد الخط العربي
if not os.path.exists("/tmp/Amiri-Regular.ttf"):
    try:
        os.system("wget https://github.com/alef.type/amiri/raw/master/Amiri-Regular.ttf -O /tmp/Amiri-Regular.ttf")
    except Exception as e:
        st.error(f"Failed to download font: {e}")

# إعداد الصفحة بتصميم فاخر
st.set_page_config(
    page_title="SmartPulse™ - Elite Data Intelligence",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS محسّن لتناسق النصوص مع الخلفية وجعل iPhone 15 أحمر وعريض
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
        color: #FF0000;  /* لون أحمر لـ iPhone 15 */
        font-weight: bold;  /* خط عريض */
        padding: 15px;
        font-size: 18px;
        box-shadow: 0 5px 20px rgba(255,215,0,0.2);
        transition: all 0.3s ease;
        text-shadow: 0 1px 2px rgba(0,0,0,0.5);  /* ظل خفيف للنص */
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
    
    .stSelectbox>div>div>button {
        background: rgba(255,255,255,0.1);
        border: 2px solid #FFD700;
        border-radius: 15px;
        color: #F8FAFC;
        padding: 15px;
        font-size: 18px;
        box-shadow: 0 5px 20px rgba(255,215,0,0.2);
        text-shadow: 0 1px 2px rgba(0,0,0,0.5);
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

# تعريف الحالة الافتراضية مع معالجة الأخطاء
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
    <h1 style='font-size: 60px; text-align: center; animation: fadeInUp 1s forwards;'>SmartPulse™</h1>
    <p style='font-size: 24px; text-align: center; opacity: 0.9; animation: fadeInUp 1s forwards; animation-delay: 0.2s;'>
        Unleash Elite Data Insights – Dominate Your Market!<br>
        <em>Crafted by Anas Hani Zewail • Contact: +201024743503</em>
    </p>
""", unsafe_allow_html=True)

# واجهة المستخدم المحسنة
st.markdown("<h2 style='text-align: center; animation: fadeInUp 1s forwards; animation-delay: 0.4s;'>Master Your Data in Seconds</h2>", unsafe_allow_html=True)
try:
    # حقل الإدخال مع قيمة افتراضية واضحة (أحمر وعريض)
    keyword = st.text_input("Enter Your Topic (e.g., iPhone 15):", value="iPhone 15", key="keyword_input", help="Unlock insights for any topic instantly!")
    
    # قائمة اللغة مع خيارات واضحة
    language = st.selectbox("Select Language:", options=["English", "Arabic"], index=0, key="language_select")
    st.session_state["language"] = language
    
    # خيارات الخطة
    plan = st.radio("Choose Your Plan:", ["Free Insights", "Premium Insights ($10)"], key="plan_radio")
    st.markdown("""
        <p style='text-align: center; animation: fadeInUp 1s forwards; animation-delay: 0.6s;'>
            <strong>Free Insights:</strong> Instant stunning charts – share the brilliance!<br>
            <strong>Premium Insights ($10):</strong> 30-day forecasts, smart strategies, premium PDF – auto-payment opens!
        </p>
    """, unsafe_allow_html=True)
except Exception as e:
    st.error(f"Error in input section: {e}")

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

def create_payment(access_token):
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
                "amount": {"total": "10.00", "currency": "USD"},
                "description": "SmartPulse Premium Insights"
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

# دوال التحليل مع معالجة الأخطاء
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
        plt.gca().set_facecolor('#0D1B2A')
        plt.gcf().set_facecolor('#0D1B2A')
        pie_file = f"pie_{keyword}.png"
        plt.savefig(pie_file, dpi=300, bbox_inches="tight")
        plt.close()
        return pie_file
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
    except Exception as e:
        st.error(f"Failed to generate forecast: {e}")
        return None, None

def generate_report(keyword, language, countries, trends, sub_keywords, sentiment, sentiment_by_day, sentiment_by_country, speakers, total_posts, pie_chart, forecast_chart):
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.fontSize = 12
        style.textColor = colors.black
        try:
            pdfmetrics.registerFont(TTFont("Amiri", "/tmp/Amiri-Regular.ttf"))
            style.fontName = "Helvetica" if language == "English" else "Amiri"
        except Exception as e:
            style.fontName = "Helvetica"
            st.warning(f"Font loading failed: {e}. Using Helvetica.")
        
        # معالجة النصوص العربية باستخدام arabic_reshaper و python-bidi
        report = f"SmartPulse Analysis Report for {keyword}\n"
        report += "=" * 50 + "\n"
        report += f"Total Sources: {total_posts}\n"
        if language == "Arabic":
            report = arabic_reshaper.reshape(report)
            report = get_display(report)  # ترتيب النصوص من اليمين إلى اليسار
        
        content = [Paragraph(report, style)]
        content.append(Image(pie_chart, width=400, height=300))
        content.append(Image(forecast_chart, width=400, height=300))
        content.append(Spacer(1, 20))
        doc.build(content)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Failed to generate report: {e}")
        return None

# تشغيل الأداة مع معالجة الأخطاء
try:
    if st.button("Unlock Insights Now!", key="generate_insights"):
        with st.spinner("Processing Your Insights..."):
            pie_chart = generate_pie_chart(keyword, language, sentiment, total_posts)
            if pie_chart:
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
                        if forecast_chart and reco:
                            st.image(forecast_chart, caption="30-Day Forecast")
                            st.write(reco)
                            pdf_data = generate_report(keyword, language, countries, trends, sub_keywords, sentiment, sentiment_by_day, sentiment_by_country, speakers, total_posts, pie_chart, forecast_chart)
                            if pdf_data:
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
except Exception as e:
    st.error(f"Error in processing insights: {e}")

# زر كبير في الأسفل
if st.session_state["payment_url"]:
    st.markdown(f'<a href="{st.session_state["payment_url"]}" target="_blank" class="buy-premium-btn animate-in">Buy Premium Insights Now</a>', unsafe_allow_html=True)
else:
    st.markdown('<a href="#" class="buy-premium-btn animate-in">Buy Premium Insights Now</a>', unsafe_allow_html=True)

# التحقق من الدفع مع معالجة الأخطاء
query_params = st.query_params
try:
    if "success" in query_params and query_params["success"] == "true" and not st.session_state["payment_verified"]:
        st.session_state["payment_verified"] = True
        st.session_state["payment_initiated"] = False
        st.success("Payment successful! Your premium insights are now unlocked.")
    elif "cancel" in query_params:
        st.session_state["payment_initiated"] = False
        st.warning("Payment canceled. Retry Premium for full access!")
except Exception as e:
    st.error(f"Error in payment verification: {e}")
