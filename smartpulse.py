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

# Set up fonts (for Arabic compatibility if needed)
if not os.path.exists("/tmp/Amiri-Regular.ttf"):
    os.system("wget https://github.com/alef.type/amiri/raw/master/Amiri-Regular.ttf -O /tmp/Amiri-Regular.ttf")

# Page configuration with premium design
st.set_page_config(
    page_title="SmartPulse™ - Elite Data Intelligence", 
    page_icon="✨", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS with animations and premium design elements
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');
    
    * {font-family: 'Montserrat', sans-serif;}
    
    .main {
        background: linear-gradient(135deg, #0F172A, #1E293B);
        color: #F8FAFC;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 35px rgba(0,0,0,0.5);
    }
    
    h1, h2, h3 {
        background: linear-gradient(90deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #FFD700, #FFA500);
        color: #0F172A;
        border-radius: 50px;
        font-weight: 600;
        padding: 15px 35px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: none;
        box-shadow: 0 10px 20px rgba(255,215,0,0.3);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 15px 30px rgba(255,215,0,0.4);
    }
    
    .stButton>button:active {
        transform: translateY(2px);
    }
    
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: rgba(255,255,255,0.1);
        border: 2px solid rgba(255,215,0,0.3);
        border-radius: 12px;
        color: white;
        padding: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus {
        border-color: #FFD700;
        box-shadow: 0 5px 25px rgba(255,215,0,0.4);
    }
    
    .stTextInput>label, .stSelectbox>label, .stRadio>label {
        color: #FFD700;
        font-size: 20px;
        font-weight: 600;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.5);
        margin-bottom: 8px;
    }
    
    .stMarkdown {
        color: #E2E8F0;
        font-size: 18px;
        line-height: 1.8;
    }
    
    .stRadio>div {
        background-color: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .testimonial-card {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        border-left: 5px solid #FFD700;
        margin: 20px 0;
        transition: all 0.3s ease;
    }
    
    .testimonial-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    
    .feature-card {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        border-top: 5px solid #FFD700;
        margin: 10px 0;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        background: rgba(255,255,255,0.08);
    }
    
    .feature-icon {
        font-size: 36px;
        margin-bottom: 15px;
        background: linear-gradient(90deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .premium-badge {
        background: linear-gradient(90deg, #FFD700, #FFA500);
        color: #0F172A;
        padding: 8px 16px;
        border-radius: 50px;
        font-weight: 600;
        font-size: 14px;
        display: inline-block;
        margin-bottom: 10px;
        box-shadow: 0 5px 15px rgba(255,215,0,0.3);
    }
    
    .share-btn {
        background: rgba(255,255,255,0.1);
        color: white;
        border-radius: 50px;
        padding: 12px 25px;
        text-decoration: none;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        display: block;
        text-align: center;
        margin: 5px 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .share-btn:hover {
        background: rgba(255,255,255,0.2);
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    }
    
    .stSpinner>div {
        border-color: #FFD700 transparent #FFD700 transparent;
    }
    
    .buy-premium-btn {
        background: linear-gradient(90deg, #FFD700, #FFA500);
        color: #0F172A;
        border-radius: 50px;
        font-weight: 700;
        padding: 18px 40px;
        font-size: 22px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 10px 25px rgba(255,215,0,0.4);
        text-align: center;
        display: block;
        width: 100%;
        text-decoration: none;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin: 30px 0;
        position: relative;
        overflow: hidden;
    }
    
    .buy-premium-btn:hover {
        transform: translateY(-5px) scale(1.03);
        box-shadow: 0 15px 35px rgba(255,215,0,0.5);
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
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 30px 0;
        border: 2px solid rgba(255,215,0,0.3);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .countdown-value {
        font-size: 40px;
        font-weight: 700;
        background: linear-gradient(90deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin-bottom: 5px;
    }
    
    .countdown-label {
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: rgba(255,255,255,0.7);
    }
    
    .price-tag {
        position: relative;
        display: inline-block;
        font-size: 28px;
        font-weight: 700;
        color: #FFD700;
        margin: 10px 0;
    }
    
    .price-tag .original {
        position: relative;
        color: rgba(255,255,255,0.5);
        font-size: 22px;
        margin-left: 10px;
    }
    
    .price-tag .original:after {
        content: "";
        position: absolute;
        left: 0;
        top: 50%;
        width: 100%;
        height: 2px;
        background-color: rgba(255,0,0,0.5);
        transform: rotate(-10deg);
    }
    
    .guarantee-badge {
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 15px;
        margin: 20px 0;
        border: 1px solid rgba(255,215,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% {
            transform: scale(1);
            box-shadow: 0 10px 25px rgba(255,215,0,0.4);
        }
        50% {
            transform: scale(1.05);
            box-shadow: 0 15px 35px rgba(255,215,0,0.6);
        }
        100% {
            transform: scale(1);
            box-shadow: 0 10px 25px rgba(255,215,0,0.4);
        }
    }
    
    .animate-in {
        animation: fadeInUp 1s forwards;
        opacity: 0;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background-color: #FFD700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables
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
if "visitor_count" not in st.session_state:
    st.session_state["visitor_count"] = 3852 + int(time.time()) % 100
if "offer_ends" not in st.session_state:
    # Set offer to end in 24 hours
    st.session_state["offer_ends"] = datetime.now() + timedelta(hours=24)

# Header with logos and branding
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
        <div style="text-align: center; animation: fadeInUp 1s forwards;">
            <h1 style="font-size: 48px; margin-bottom: 5px;">SmartPulse™</h1>
            <p style="font-size: 22px; opacity: 0.8; margin-top: 0;">Elite Data Intelligence Platform</p>
            <div style="margin: 20px 0;">
                <span class="premium-badge">TRUSTED BY FORTUNE 500</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Live visitor counter
st.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px; font-size: 14px; color: rgba(255,255,255,0.7);">
        <span style="margin-right: 10px;">🔴 LIVE</span>
        <span>{st.session_state["visitor_count"]} people viewing this page right now</span>
    </div>
""", unsafe_allow_html=True)

# Limited time offer countdown
time_difference = st.session_state["offer_ends"] - datetime.now()
hours = time_difference.seconds // 3600
minutes = (time_difference.seconds % 3600) // 60
seconds = time_difference.seconds % 60

st.markdown(f"""
    <div class="countdown-timer pulse-animation">
        <div style="margin-bottom: 10px; font-size: 18px; font-weight: 600;">LIMITED TIME OFFER ENDS IN:</div>
        <div style="display: flex; justify-content: center;">
            <div style="margin: 0 10px;">
                <div class="countdown-value">{hours:02d}</div>
                <div class="countdown-label">Hours</div>
            </div>
            <div style="margin: 0 10px;">
                <div class="countdown-value">{minutes:02d}</div>
                <div class="countdown-label">Minutes</div>
            </div>
            <div style="margin: 0 10px;">
                <div class="countdown-value">{seconds:02d}</div>
                <div class="countdown-label">Seconds</div>
            </div>
        </div>
        <div style="margin-top: 15px; font-size: 16px;">
            <div class="price-tag">$9.99 <span class="original">$29.99</span></div>
            <div>66% DISCOUNT TODAY ONLY!</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Main content area
st.markdown("""
    <div style="animation: fadeInUp 1s forwards; animation-delay: 0.2s; opacity: 0;">
        <h2>Unlock Game-Changing Insights For Your Business</h2>
        <p>SmartPulse™ delivers professional-grade market intelligence that used to cost thousands - now at your fingertips.</p>
    </div>
""", unsafe_allow_html=True)

# Input form with enhanced styling
keyword = st.text_input("Enter Your Topic to Analyze:", "iPhone 15", 
                      key="keyword_input", 
                      help="Enter any product, brand, topic, or trend to analyze")

# Language selection
language = st.selectbox("Select Language:", ["English", "Arabic"], index=0, key="language_select")
st.session_state["language"] = language

# Improved plan selection with benefits
st.markdown("""<div style="animation: fadeInUp 1s forwards; animation-delay: 0.4s; opacity: 0;"><h3>Choose Your Intelligence Package:</h3></div>""", unsafe_allow_html=True)

plan_col1, plan_col2 = st.columns(2)

with plan_col1:
    st.markdown("""
        <div class="feature-card">
            <div style="font-size: 24px; font-weight: 600; margin-bottom: 15px;">Free Insights</div>
            <div style="font-size: 36px; margin: 20px 0;">$0</div>
            <div>✅ Basic sentiment analysis</div>
            <div>✅ Single visualization</div>
            <div>✅ Limited data sources</div>
            <div>❌ No predictive analytics</div>
            <div>❌ No competitive intelligence</div>
            <div>❌ No strategic recommendations</div>
        </div>
    """, unsafe_allow_html=True)

with plan_col2:
    st.markdown("""
        <div class="feature-card" style="border-color: #FFD700; background: rgba(255,215,0,0.05);">
            <div style="font-size: 24px; font-weight: 600; margin-bottom: 15px;">Premium Insights</div>
            <div style="font-size: 36px; margin: 20px 0;">$9.99 <span style="font-size: 18px; text-decoration: line-through; opacity: 0.7;">$29.99</span></div>
            <div>✅ Advanced sentiment analysis</div>
            <div>✅ Multiple visualizations & charts</div>
            <div>✅ 30-day future trend forecasting</div>
            <div>✅ Competitive intelligence report</div>
            <div>✅ AI strategic recommendations</div>
            <div>✅ Premium PDF report</div>
        </div>
    """, unsafe_allow_html=True)

plan = st.radio("Select Your Package:", ["Free Insights", "Premium Insights ($9.99)"], 
               key="plan_radio", 
               index=1)  # Default to Premium

# Money-back guarantee badge
st.markdown("""
    <div class="guarantee-badge">
        <div style="font-size: 36px; margin-bottom: 10px;">🛡️</div>
        <div style="font-weight: 600; font-size: 18px;">100% Money-Back Guarantee</div>
        <div style="opacity: 0.8; font-size: 14px; margin-top: 5px;">Not satisfied? Get a full refund within 30 days, no questions asked!</div>
    </div>
""", unsafe_allow_html=True)

# PayPal Sandbox configuration
PAYPAL_CLIENT_ID = "AQd5IZObL6YTejqYpN0LxADLMtqbeal1ahbgNNrDfFLcKzMl6goF9BihgMw2tYnb4suhUfprhI-Z8eoC"
PAYPAL_SECRET = "EPk46EBw3Xm2W-R0Uua8sLsoDLJytgSXqIzYLbbXCk_zSOkdzFx8jEbKbKxhjf07cnJId8gt6INzm6_V"
PAYPAL_API = "https://api-m.sandbox.paypal.com"

# Function to get PayPal access token
def get_paypal_access_token():
    url = f"{PAYPAL_API}/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET), data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        st.error("Payment service temporarily unavailable. Please try again in a few moments.")
        return None

# Function to create payment request
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
            "amount": {"total": "9.99", "currency": "USD"},
            "description": "SmartPulse Premium Insights - Limited Time Offer"
        }],
        "redirect_urls": {
            "return_url": "https://smartpulse-premium.streamlit.app/?success=true",
            "cancel_url": "https://smartpulse-premium.streamlit.app/?cancel=true"
        }
    }
    response = requests.post(url, headers=headers, json=payment_data)
    if response.status_code == 201:
        for link in response.json()["links"]:
            if link["rel"] == "approval_url":
                return link["href"]
    st.error("Payment processing temporarily unavailable. Please try again.")
    return None

# Mock data generation functions
def get_mock_sentiment_data(keyword):
    # More realistic sentiment distribution
    sentiment = {
        "positive": {"strong": np.random.randint(25, 45), "mild": np.random.randint(15, 25)},
        "negative": {"strong": np.random.randint(5, 15), "mild": np.random.randint(10, 20)},
        "neutral": np.random.randint(15, 30)
    }
    total_posts = sum([sentiment["positive"]["strong"], sentiment["positive"]["mild"], 
                      sentiment["negative"]["strong"], sentiment["negative"]["mild"],
                      sentiment["neutral"]])
    
    # Generate daily sentiment data
    days = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(14, -1, -1)]
    sentiment_by_day = {}
    
    # Create a trend pattern with some variability
    pos_trend = np.linspace(40, 60, len(days)) + np.random.normal(0, 5, len(days))
    neg_trend = np.linspace(30, 20, len(days)) + np.random.normal(0, 3, len(days))
    
    for i, day in enumerate(days):
        sentiment_by_day[f"{day}_pos_strong"] = int(pos_trend[i] * 0.6)
        sentiment_by_day[f"{day}_pos_mild"] = int(pos_trend[i] * 0.4)
        sentiment_by_day[f"{day}_neg_strong"] = int(neg_trend[i] * 0.4)
        sentiment_by_day[f"{day}_neg_mild"] = int(neg_trend[i] * 0.6)
        sentiment_by_day[f"{day}_neutral"] = int(100 - pos_trend[i] - neg_trend[i])
    
    countries = ["United States", "United Kingdom", "Germany", "Japan", "Australia", "Canada", "France", "Egypt"]
    sentiment_by_country = {}
    
    for country in countries:
        country_sentiment = {
            "positive": {
                "strong": np.random.randint(20, 40),
                "mild": np.random.randint(10, 25)
            },
            "negative": {
                "strong": np.random.randint(5, 15),
                "mild": np.random.randint(5, 20)
            },
            "neutral": np.random.randint(10, 25)
        }
        sentiment_by_country[country] = country_sentiment
    
    trends = [(f"{keyword} features", np.random.randint(40, 80)),
              (f"{keyword} price", np.random.randint(30, 70)),
              (f"{keyword} reviews", np.random.randint(20, 60)),
              (f"{keyword} comparison", np.random.randint(15, 55)),
              (f"{keyword} problems", np.random.randint(10, 50))]
    
    related_keywords = [(f"{keyword} Pro", np.random.randint(30, 70)),
                       (f"New {keyword}", np.random.randint(25, 65)),
                       (f"{keyword} vs competition", np.random.randint(20, 60)),
                       (f"Best {keyword} deals", np.random.randint(15, 55)),
                       (f"{keyword} accessories", np.random.randint(10, 50))]
    
    return sentiment, total_posts, sentiment_by_day, sentiment_by_country, days, trends, related_keywords

# Advanced visualization functions
def generate_pie_chart(keyword, language, sentiment, total_posts):
    labels = ["Strong Positive", "Mild Positive", "Strong Negative", "Mild Negative", "Neutral"] if language == "English" else ["إيجابي قوي", "إيجابي خفيف", "سلبي قوي", "سلبي خفيف", "محايد"]
    sizes = [sentiment["positive"]["strong"], sentiment["positive"]["mild"], sentiment["negative"]["strong"], sentiment["negative"]["mild"], sentiment["neutral"]]
    colors = ["#4CAF50", "#8BC34A", "#F44336", "#FF9800", "#9E9E9E"]
    
    plt.figure(figsize=(10, 7))
    wedges, texts, autotexts = plt.pie(sizes, 
                                      labels=labels, 
                                      colors=colors, 
                                      autopct="%1.1f%%", 
                                      startangle=90, 
                                      shadow=True, 
                                      textprops={'fontsize': 14, 'color': 'white', 'fontweight': 'bold'})
    
    for w in wedges:
        w.set_edgecolor('#FFD700')
        w.set_linewidth(2)
    
    plt.title(f"{keyword} Sentiment Analysis", fontsize=22, color="white", pad=20, fontweight='bold')
    plt.gca().set_facecolor('#1E293B')
    plt.gcf().set_facecolor('#1E293B')
    
    # Add a fancy border and gradient background
    fig = plt.gcf()
    fig.patch.set_alpha(0.0)  # Make figure background transparent
    ax = plt.gca()
    ax.set_facecolor('#0F172A')  # Dark blue background
    
    # Add annotation with total posts
    plt.annotate(f"Total Data Sources: {total_posts:,}", 
                xy=(0.5, 0.02), 
                xycoords='figure fraction', 
                ha='center',
                fontsize=12, 
                color='white',
                bbox=dict(boxstyle="round,pad=0.5", 
                         facecolor='rgba(255, 215, 0, 0.2)',
                         edgecolor='#FFD700',
                         alpha=0.8))
    
    pie_file = f"pie_{keyword}.png"
    plt.tight_layout()
    plt.savefig(pie_file, dpi=300, bbox_inches="tight", facecolor='#0F172A')
    plt.close()
    return pie_file

def generate_trend_chart(keyword, days, sentiment_by_day):
    positive_values = []
    negative_values = []
    
    for day in days:
        pos = sentiment_by_day.get(f"{day}_pos_strong", 0) + sentiment_by_day.get(f"{day}_pos_mild", 0)
        neg = sentiment_by_day.get(f"{day}_neg_strong", 0) + sentiment_by_day.get(f"{day}_neg_mild", 0)
        positive_values.append(pos)
        negative_values.append(neg)
    
    plt.figure(figsize=(12, 7))
    plt.plot(days, positive_values, 'o-', color='#4CAF50', linewidth=3, markersize=8, label='Positive Sentiment')
    plt.plot(days, negative_values, 'o-', color='#F44336', linewidth=3, markersize=8, label='Negative Sentiment')
    
    plt.fill_between(days, positive_values, alpha=0.3, color='#4CAF50')
    plt.fill_between(days, negative_values, alpha=0.3, color='#F44336')
    
    plt.title(f"{keyword} Sentiment Trends", fontsize=22, color="white", pad=20, fontweight='bold')
    plt.ylabel('Sentiment Volume', fontsize=14, color='white')
    plt.xlabel('Date', fontsize=14, color='white')
    
    plt.xticks(rotation=45, color='white', fontsize=10)
    plt.yticks(color='white', fontsize=12)
    
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(fontsize=12, loc="upper left", facecolor="#0F172A", edgecolor="#FFD700", labelcolor="white")
    
    plt.gca().set_facecolor('#0F172A')
    plt.gcf().set_facecolor('#0F172A')
    
    # Add trend indicators
    if positive_values[-1] > positive_values[0]:
        plt.annotate('↑ Upward Trend', xy=(0.75, 0.9), xycoords='axes fraction', 
                    fontsize=14, color='#4CAF50', 
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='rgba(76, 175, 80, 0.2)', alpha=0.8))
    else:
        plt.annotate('↓ Downward Trend', xy=(0.75, 0.9), xycoords='axes fraction', 
                    fontsize
