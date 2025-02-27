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

# إعداد الخط العربي (Amiri)
if not os.path.exists("/tmp/Amiri-Regular.ttf"):
    os.system("wget https://github.com/alef.type/amiri/raw/master/Amiri-Regular.ttf -O /tmp/Amiri-Regular.ttf")

# إعداد الصفحة
st.set_page_config(page_title="SmartPulse", page_icon="📊", layout="wide")
st.title("SmartPulse - World’s Best Data Insights Tool")
st.markdown("**By Anas Hani Zewail** - Elite predictive analytics at your fingertips. Contact: +201024743503")

# واجهة المستخدم
keyword = st.text_input("Enter a Keyword (e.g., iPhone 15):", "iPhone 15")
language = st.selectbox("Select Language:", ["ar", "en"], index=0)
plan = st.radio("Choose Your Plan:", ["Free (Basic Sentiment)", "Premium ($10 - Full Report)"])
st.markdown("Free: Sentiment pie chart. Premium: Full report with charts, heatmap, and 30-day forecast.")

# بيانات وهمية للتجربة (استبدلها بمصادرك الفعلية لاحقًا)
sentiment = {"positive": {"strong": 30, "mild": 20}, "negative": {"strong": 10, "mild": 15}, "neutral": 25}
total_posts = 100
sentiment_by_day = {
    "2025-02-20_pos_strong": 10, "2025-02-20_pos_mild": 5, "2025-02-20_neg_strong": 3,
    "2025-02-21_pos_strong": 12, "2025-02-21_pos_mild": 6, "2025-02-21_neg_strong": 4,
    "2025-02-22_pos_strong": 8, "2025-02-22_pos_mild": 4, "2025-02-22_neg_strong": 2
}
sentiment_by_country = {
    "Egypt": {"positive": {"strong": 20, "mild": 10}, "negative": {"strong": 5, "mild": 5}, "neutral": 10}
}
countries, trends, sub_keywords, speakers = ["Egypt"], [("tech", 50)], [("phone", 30)], 80

# دوال التحليل من الكود الأصلي (محسنة للأداة)
def generate_pie_chart(keyword, language, sentiment, total_posts):
    labels = ["إيجابي قوي", "إيجابي خفيف", "سلبي قوي", "سلبي خفيف", "محايد"] if language == "ar" else ["Strong Positive", "Mild Positive", "Strong Negative", "Mild Negative", "Neutral"]
    sizes = [sentiment["positive"]["strong"], sentiment["positive"]["mild"], sentiment["negative"]["strong"], sentiment["negative"]["mild"], sentiment["neutral"]]
    colors = ["#2ECC71", "#A9DFBF", "#E74C3C", "#F1948A", "#95A5A6"]
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90, shadow=True)
    plt.title(f"{keyword} Sentiment Analysis" if language == "en" else f"تحليل مشاعر {keyword}")
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
    plt.plot(df['ds'], df['y'], label="Actual", color="#2ECC71")
    plt.plot(forecast['ds'], forecast['yhat'], label="Forecast", color="#3498DB")
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color="#3498DB", alpha=0.2, label="Confidence")
    plt.legend()
    plt.title(f"{keyword} 30-Day Forecast" if language == "en" else f"توقعات {keyword} لـ 30 يومًا")
    forecast_file = f"forecast_{keyword}.png"
    plt.savefig(forecast_file, dpi=300, bbox_inches="tight")
    plt.close()
    trend = "صاعد" if forecast['yhat'].iloc[-1] > forecast['yhat'].iloc[-31] else "هابط"
    reco = f"الاتجاه: {trend}. زِد الجهود التسويقية إذا صاعد أو راجع الاستراتيجيات إذا هابط." if language == "ar" else f"Trend: {'upward' if trend == 'صاعد' else 'downward'}. Boost marketing if upward or review strategy if downward."
    return forecast_file, reco

def generate_report(keyword, language, countries, trends, sub_keywords, sentiment, sentiment_by_day, sentiment_by_country, speakers, total_posts, pie_chart):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontSize = 12
    try:
        pdfmetrics.registerFont(TTFont("Amiri", "/tmp/Amiri-Regular.ttf"))
        style.fontName = "Amiri" if language == "ar" else "Helvetica"
    except:
        style.fontName = "Helvetica"
    
    report = f"تقرير تحليل {keyword} باللغة العربية\n" if language == "ar" else f"{keyword} Analysis Report\n"
    report += "=" * 50 + "\n"
    report += f"إجمالي المصادر: {total_posts}\n" if language == "ar" else f"Total Sources: {total_posts}\n"
    content = [Paragraph(arabic_reshaper.reshape(report) if language == "ar" else report, style)]
    content.append(Image(pie_chart, width=400, height=300))
    content.append(Spacer(1, 20))
    doc.build(content)
    buffer.seek(0)
    return buffer.getvalue()

# تشغيل الأداة
if st.button("Generate Insights"):
    with st.spinner("Processing your request..."):
        pie_chart = generate_pie_chart(keyword, language, sentiment, total_posts)
        st.image(pie_chart, caption="نظرة عامة على المشاعر" if language == "ar" else "Sentiment Overview")
        
        if plan == "Premium ($10 - Full Report)":
            forecast_chart, reco = generate_forecast(keyword, language, sentiment_by_day)
            st.image(forecast_chart, caption="توقعات 30 يومًا" if language == "ar" else "30-Day Forecast")
            st.write(reco)
            pdf_data = generate_report(keyword, language, countries, trends, sub_keywords, sentiment, sentiment_by_day, sentiment_by_country, speakers, total_posts, pie_chart)
            st.download_button(
                label="تحميل التقرير الكامل (PDF)" if language == "ar" else "Download Full Report (PDF)",
                data=pdf_data,
                file_name=f"{keyword}_report.pdf",
                mime="application/pdf"
            )
        else:
            st.info("ترقية إلى النسخة المميزة ($10) للحصول على التقرير الكامل مع توقعات 30 يومًا! الدفع عبر PayPal: [paypal.me/AnasZewail/10](https://paypal.me/AnasZewail/10)" if language == "ar" else 
                    "Upgrade to Premium ($10) for the full report with 30-day forecast! Pay via PayPal: [paypal.me/AnasZewail/10](https://paypal.me/AnasZewail/10)")