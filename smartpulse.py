import streamlit as st
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from prophet import Prophet
import pandas as pd
import os
import io
import requests
import json
import base64

# إعداد الخط العربي
if not os.path.exists("/tmp/Amiri-Regular.ttf"):
    os.system("wget https://github.com/alef.type/amiri/raw/master/Amiri-Regular.ttf -O /tmp/Amiri-Regular.ttf")

# إعداد الصفحة مع تصميم محسن
st.set_page_config(page_title="SmartPulse - Ultimate Data Insights", page_icon="📊", layout="wide")
st.markdown("""
    <style>
    .main {background: linear-gradient(135deg, #1E3A8A, #60A5FA); color: #FFFFFF;}
    .stButton>button {background-color: #FFD700; color: #1E3A8A; border-radius: 10px; font-weight: bold; padding: 10px 20px;}
    .stTextInput>label, .stSelectbox>label, .stRadio>label {color: #FFD700; font-size: 18px; font-weight: bold;}
    .stMarkdown {color: #FFFFFF;}
    .share-btn {background-color: #34C759; color: white; border-radius: 5px; padding: 5px 10px;}
    </style>
""", unsafe_allow_html=True)

# عنوان ووصف
st.title("SmartPulse - World’s Ultimate Data Insights")
st.markdown("**Crafted by Anas Hani Zewail** - Unleash elite analytics instantly. Contact: +201024743503")
st.markdown('<meta name="description" content="SmartPulse by Anas Hani Zewail - World’s premier free data insights tool with premium predictive analytics for unmatched success">', unsafe_allow_html=True)
st.markdown('<meta name="keywords" content="data analysis tool, predictive insights, sentiment analysis, free analytics, iPhone 15 trends, SEO optimization">', unsafe_allow_html=True)

# بيانات PayPal Sandbox
PAYPAL_CLIENT_ID = "AQd5IZObL6YTejqYpN0LxADLMtqbeal1ahbgNNrDfFLcKzMl6goF9BihgMw2tYnb4suhUfprhI-Z8eoC"
PAYPAL_SECRET = "EPk46EBw3Xm2W-R0Uua8sLsoDLJytgSXqIzYLbbXCk_zSOkdzFx8jEbKbKxhjf07cnJId8gt6INzm6_V"
PAYPAL_API = "https://api-m.sandbox.paypal.com"  # Sandbox API (غيّر إلى api-m.paypal.com للإطلاق الحقيقي)

# واجهة المستخدم
st.subheader("Unlock Insights in Seconds")
keyword = st.text_input("Enter a Keyword (e.g., iPhone 15):", "iPhone 15", help="Analyze any topic or product instantly!")
language = st.selectbox("Select Language:", ["Arabic", "English"], index=0)
plan = st.radio("Choose Your Plan:", ["Free Insights", "Premium Insights ($10)"])
st.markdown("""
**Free Insights**: Instant sentiment analysis with a stunning chart.  
**Premium Insights ($10)**: Full report with 30-day forecasts, actionable recommendations, and PDF download.
""")

# بيانات وهمية للتجربة (استبدلها بمصادرك الفعلية لاحقًا)
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
    labels = ["إيجابي قوي", "إيجابي خفيف", "سلبي قوي", "سلبي خفيف", "محايد"] if language == "Arabic" else ["Strong Positive", "Mild Positive", "Strong Negative", "Mild Negative", "Neutral"]
    sizes = [sentiment["positive"]["strong"], sentiment["positive"]["mild"], sentiment["negative"]["strong"], sentiment["negative"]["mild"], sentiment["neutral"]]
    colors = ["#2ECC71", "#A9DFBF", "#E74C3C", "#F1948A", "#95A5A6"]
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90, shadow=True, textprops={'fontsize': 14, 'color': 'white'})
    plt.title(f"{keyword} Sentiment Analysis" if language == "English" else f"تحليل مشاعر {keyword}", fontsize=16, color="white")
    plt.gca().set_facecolor('#1E3A8A')
    plt.gcf().set_facecolor('#1E3A8A')
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
    plt.plot(df['ds'], df['y'], label="Actual", color="#2ECC71", linewidth=2)
    plt.plot(forecast['ds'], forecast['yhat'], label="Forecast", color="#FFD700", linewidth=2)
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color="#FFD700", alpha=0.2, label="Confidence")
    plt.legend(fontsize=12)
    plt.title(f"{keyword} 30-Day Forecast" if language == "English" else f"توقعات {keyword} لـ 30 يومًا", fontsize=16, color="white")
    plt.gca().set_facecolor('#1E3A8A')
    plt.gcf().set_facecolor('#1E3A8A')
    plt.xticks(color="white")
    plt.yticks(color="white")
    forecast_file = f"forecast_{keyword}.png"
    plt.savefig(forecast_file, dpi=300, bbox_inches="tight")
    plt.close()
    trend = "صاعد" if forecast['yhat'].iloc[-1] > forecast['yhat'].iloc[-31] else "هابط"
    reco = f"الاتجاه: {trend}. زِد الجهود إذا صاعد أو راجع الاستراتيجيات إذا هابط." if language == "Arabic" else f"Trend: {'upward' if trend == 'صاعد' else 'downward'}. Boost efforts if upward or review strategy if downward."
    return forecast_file, reco

def generate_report(keyword, language, countries, trends, sub_keywords, sentiment, sentiment_by_day, sentiment_by_country, speakers, total_posts, pie_chart, forecast_chart):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontSize = 12
    try:
        pdfmetrics.registerFont(TTFont("Amiri", "/tmp/Amiri-Regular.ttf"))
        style.fontName = "Amiri" if language == "Arabic" else "Helvetica"
    except:
        style.fontName = "Helvetica"
    
    report = f"تقرير تحليل {keyword} باللغة العربية\n" if language == "Arabic" else f"{keyword} Analysis Report\n"
    report += "=" * 50 + "\n"
    report += f"إجمالي المصادر: {total_posts}\n" if language == "Arabic" else f"Total Sources: {total_posts}\n"
    content = [Paragraph(arabic_reshaper.reshape(report) if language == "Arabic" else report, style)]
    content.append(Image(pie_chart, width=400, height=300))
    content.append(Image(forecast_chart, width=400, height=300))
    content.append(Spacer(1, 20))
    doc.build(content)
    buffer.seek(0)
    return buffer.getvalue()

# وظيفة للحصول على رمز الوصول من PayPal
def get_paypal_access_token():
    url = f"{PAYPAL_API}/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET), data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        st.error("Failed to connect to PayPal. Please try again later.")
        return None

# وظيفة لإنشاء طلب دفع
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

# إدارة حالة الدفع
if "payment_verified" not in st.session_state:
    st.session_state["payment_verified"] = False

# تشغيل الأداة
if st.button("Unlock Insights Now"):
    with st.spinner("Processing your request..." if language == "English" else "جارٍ معالجة طلبك..."):
        pie_chart = generate_pie_chart(keyword, language, sentiment, total_posts)
        st.image(pie_chart, caption="Sentiment Overview" if language == "English" else "نظرة عامة على المشاعر")
        share_url = "https://smartpulse-nwrkb9xdsnebmnhczyt76s.streamlit.app/"
        telegram_group = "https://t.me/+K7W_PUVdbGk4MDRk"
        
        # أزرار مشاركة مباشرة
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<a href="https://api.whatsapp.com/send?text=Check%20out%20SmartPulse:%20{share_url}" target="_blank" class="share-btn">Share on WhatsApp</a>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<a href="https://t.me/share/url?url={share_url}&text=Try%20SmartPulse!" target="_blank" class="share-btn">Share on Telegram</a>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<a href="https://www.facebook.com/sharer/sharer.php?u={share_url}" target="_blank" class="share-btn">Share on Messenger</a>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<a href="https://discord.com/channels/@me?message=Try%20SmartPulse:%20{share_url}" target="_blank" class="share-btn">Share on Discord</a>', unsafe_allow_html=True)
        
        st.markdown(f"Join our Telegram community for support or discussion: [Click here]({telegram_group})" if language == "English" else 
                    f"انضم إلى مجموعتنا على تليجرام للدعم أو النقاش: [اضغط هنا]({telegram_group})")
        
        if plan == "Premium ($10 - Full Insights)":
            if not st.session_state["payment_verified"]:
                access_token = get_paypal_access_token()
                if access_token:
                    approval_url = create_payment(access_token)
                    if approval_url:
                        st.markdown(f"Please complete payment via PayPal: [Click here]({approval_url})" if language == "English" else 
                                    f"يرجى إتمام الدفع عبر PayPal: [اضغط هنا]({approval_url})")
                        st.info("After successful payment, reload the page to unlock premium insights." if language == "English" else 
                                "بعد الدفع الناجح، أعد تحميل الصفحة لفتح الرؤى المميزة.")
            else:
                forecast_chart, reco = generate_forecast(keyword, language, sentiment_by_day)
                st.image(forecast_chart, caption="30-Day Forecast" if language == "English" else "توقعات 30 يومًا")
                st.write(reco)
                pdf_data = generate_report(keyword, language, countries, trends, sub_keywords, sentiment, sentiment_by_day, sentiment_by_country, speakers, total_posts, pie_chart, forecast_chart)
                st.download_button(
                    label="Download Full Insights (PDF)" if language == "English" else "تحميل الرؤى الكاملة (PDF)",
                    data=pdf_data,
                    file_name=f"{keyword}_insights.pdf",
                    mime="application/pdf"
                )
                st.markdown(f"Earn a FREE report! Invite 5 friends via WhatsApp, Telegram, Messenger, or Discord: [Share Now]({share_url})" if language == "English" else 
                            f"احصل على تقرير مجاني! ادعُ 5 أصدقاء عبر واتساب، تليجرام، مسنجر، أو ديسكورد: [شارك الآن]({share_url})")
                st.markdown(f"Join our Telegram community: [Click here]({telegram_group})" if language == "English" else 
                            f"انضم إلى مجموعتنا على تليجرام: [اضغط هنا]({telegram_group})")
        else:
            st.info("Upgrade to Premium ($10) for full insights with forecasts and more!" if language == "English" else 
                    "ترقية إلى النسخة المميزة ($10) للحصول على رؤى كاملة مع توقعات والمزيد!")

# التحقق من الدفع
query_params = st.query_params
if "success" in query_params and query_params["success"] == "true":
    st.session_state["payment_verified"] = True
    st.success("Payment successful! Enjoy your premium insights." if language == "English" else "تم الدفع بنجاح! استمتع برؤاك المميزة.")
elif "cancel" in query_params:
    st.warning("Payment canceled. Retry Premium for full access." if language == "English" else "تم إلغاء الدفع. أعد المحاولة للوصول الكامل.")
