import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from io import BytesIO
import warnings
import random
warnings.filterwarnings('ignore')

# Import for PDF generation
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import base64

# Set page config
st.set_page_config(
    page_title='AI Financial Advisor — By Ayush Shukla', 
    page_icon='🤖', 
    layout='wide',
    initial_sidebar_state='auto'
)

# --- Financial Chatbot Class ---
class FinancialChatbot:
    def __init__(self):
        self.context = {}
        self.conversation_history = []
        
        # Define intents and responses
        self.intents = {
            'greeting': {
                'keywords': ['hello', 'hi', 'hey', 'greetings', 'namaste', 'good morning', 'good evening'],
                'responses': [
                    "👋 Hello! I'm your AI Financial Assistant. How can I help you with your financial journey today?",
                    "Hi there! Ready to explore your financial goals? Ask me anything about investments, savings, or tax planning!",
                    "Hey! I'm here to help 24/7. Whether it's SIP calculations, tax saving, or retirement planning - just ask!"
                ]
            },
            'sip': {
                'keywords': ['sip', 'systematic investment', 'monthly investment', 'recurring investment', 'sip calculator'],
                'responses': [
                    "📈 **SIP (Systematic Investment Plan)** allows you to invest a fixed amount regularly in mutual funds.\n\n**Benefits:**\n• Rupee cost averaging\n• Power of compounding\n• Disciplined investing\n• Low entry barrier (₹500/month)\n\n**Tip:** Use the SIP Calculator in Investment Center to see your potential returns!",
                    "**SIP Magic!** Investing just ₹5,000/month for 20 years at 12% returns can grow to ₹50+ lakhs!\n\nWant to calculate? Go to Investment Center → SIP Calculator or tell me your monthly amount and years!"
                ]
            },
            'lumpsum': {
                'keywords': ['lump sum', 'one-time investment', 'bulk investment', 'one time'],
                'responses': [
                    "💰 **Lump sum investment** means investing a large amount at once.\n\n**Best for:**\n• When markets are undervalued\n• Bonus, inheritance, or windfall gains\n• Short-term goals (1-3 years)\n\n**Pro tip:** Consider STP (Systematic Transfer Plan) to average your entry price!",
                    "**Lump Sum Strategy:** For ₹1 lakh invested for 10 years at 12% returns → ₹3.1 lakhs!\n\nUse our Lump Sum calculator in Investment Center for personalized projections!"
                ]
            },
            'risk': {
                'keywords': ['risk profile', 'risk tolerance', 'risk assessment', 'how much risk', 'risk capacity'],
                'responses': [
                    "🎯 **Your risk profile depends on:**\n• Age & income stability\n• Investment goals & timeline\n• Emotional tolerance to market swings\n• Emergency fund status\n\n**Take the Behavior Quiz** in the app for a complete risk assessment!",
                    "**Risk Categories:**\n• 🛡️ Conservative: Prefer safety (FDs, Debt funds)\n• ⚖️ Moderate: Balance growth & safety\n• 🚀 Aggressive: High risk for high returns\n\nBased on your snapshot, check your ML Insights for personalized risk score!"
                ]
            },
            'tax': {
                'keywords': ['tax saving', '80c', 'tax deduction', 'save tax', 'tax benefit', 'income tax'],
                'responses': [
                    "🏦 **Top tax-saving options under Section 80C:**\n• **ELSS** (3yr lock-in, market-linked, 12-15% returns)\n• **PPF** (15yr, safe 7.1% returns)\n• **Tax Saver FD** (5yr, 6-7% returns)\n• **NPS** (retirement, extra ₹50k deduction)\n\n**Pro tip:** ELSS offers best returns with shortest lock-in!",
                    "💡 **Tax Planning Strategy:**\n• Max out ₹1.5L under 80C\n• Add ₹50k more via NPS (80CCD(1B))\n• Claim HRA if paying rent\n• Health insurance under 80D\n\nUse Tax Planner section for personalized recommendations!"
                ]
            },
            'goal': {
                'keywords': ['financial goal', 'goal planning', 'achieve goal', 'saving for', 'goal setting'],
                'responses': [
                    "🎯 **Smart Goal Planning:**\n1. Set specific target amount & timeline\n2. Calculate required monthly SIP\n3. Choose appropriate investment vehicle\n4. Track progress regularly\n\n**Use Goals Planner** section to add and track your financial goals!",
                    "**Example Goal:** Want ₹50 lakhs for house down payment in 10 years?\n• Required monthly SIP: ₹22,000 (at 12% returns)\n• Total investment: ₹26.4 lakhs\n• Estimated growth: ₹23.6 lakhs\n\nAdd your goals in the Goals Planner for personalized calculations!"
                ]
            },
            'emergency': {
                'keywords': ['emergency fund', 'rainy day', 'contingency', 'safety net', 'emergency savings'],
                'responses': [
                    "🛡️ **Emergency Fund Rule:** Cover 3-6 months of expenses.\n\n**Where to keep:**\n• High-interest savings account\n• Liquid funds\n• Short-term FDs (breakable)\n\n**Based on your expenses** - Check Dashboard for exact amount needed!",
                    "**Why Emergency Fund?**\n• Job loss protection\n• Medical emergency coverage\n• Avoid selling investments at loss\n• Peace of mind\n\nBuild this before aggressive investing!"
                ]
            },
            'mutual_fund': {
                'keywords': ['mutual fund', 'mf', 'fund', 'nav', 'expense ratio', 'large cap', 'mid cap', 'small cap'],
                'responses': [
                    "📊 **Mutual Fund Types:**\n• **Large Cap** (bluechip companies, stable)\n• **Mid Cap** (medium-sized, growth potential)\n• **Small Cap** (high growth, high risk)\n• **ELSS** (tax-saving, 3yr lock-in)\n• **Debt** (stable returns, low risk)\n\nCheck Investment Center for top-rated funds!",
                    "**For beginners:** Start with\n1. Index funds (low cost, market returns)\n2. Flexi-cap funds (diversified)\n3. Large cap funds (stable growth)\n\nUse SIP for disciplined investing in mutual funds!"
                ]
            },
            'retirement': {
                'keywords': ['retirement', 'pension', 'old age', 'retire', 'retirement planning'],
                'responses': [
                    "👴 **Retirement Planning Rule:** Save 15-20% of income.\n\n**Corpus needed:** 25x annual expenses\n\n**Investment options:**\n• NPS (pension + tax benefits)\n• PPF (long-term safe returns)\n• Equity funds for growth\n• Monthly SIPs for consistency",
                    "**Power of Early Start:**\n• Start at 25: Save ₹5k/month → ₹3cr+ by 60 (12% returns)\n• Start at 35: Need ₹16k/month for same corpus\n\nStart early to benefit from compounding! Use our SIP calculator to see projections!"
                ]
            },
            'investment': {
                'keywords': ['invest', 'investment', 'where to invest', 'best investment', 'investment options'],
                'responses': [
                    "💡 **Investment Options by Timeline:**\n\n**Short-term (1-3 years):**\n• FDs (6-7%)\n• Debt funds (7-8%)\n• Arbitrage funds (6-7%)\n\n**Medium-term (3-7 years):**\n• Balanced funds (10-12%)\n• Large cap funds (12-14%)\n\n**Long-term (7+ years):**\n• Equity funds (12-15%)\n• Small caps (15-18%)\n• International funds",
                    "🎯 **Age-based Asset Allocation:**\n(100 - age)% in equity, rest in debt\n\n**Example:**\n• Age 30: 70% equity, 30% debt\n• Age 40: 60% equity, 40% debt\n• Age 50: 50% equity, 50% debt\n\nTake the Behavior Quiz for personalized allocation!"
                ]
            },
            'help': {
                'keywords': ['help', 'support', 'how to', 'what can you do', 'features', 'guide'],
                'responses': [
                    "🤖 **I can help you with:**\n\n• 📊 **Financial Dashboard** - Track income, expenses, savings\n• 🎯 **Goal & SIP Planning** - Plan and achieve financial goals\n• 💰 **Investment Recommendations** - Based on your risk profile\n• 🏦 **Tax Saving Strategies** - Maximize tax benefits\n• 📈 **ML Insights** - AI-powered predictions\n• 📚 **Financial Education** - Learn key concepts\n\nWhat would you like to explore?",
                    "**Quick Commands:**\n• 'How to start SIP?'\n• 'Best tax saving options'\n• 'Calculate emergency fund'\n• 'What's my risk profile?'\n• 'Retirement planning tips'\n\nOr use the navigation tabs above for detailed tools!"
                ]
            }
        }
        
        # Financial concepts dictionary
        self.financial_concepts = {
            'cagr': "📊 **CAGR** (Compound Annual Growth Rate) shows investment growth rate over time.\n\n**Formula:** (Ending Value/Beginning Value)^(1/years) - 1\n\n**Example:** ₹1L growing to ₹1.5L in 3 years = 14.5% CAGR",
            'xirr': "📈 **XIRR** calculates returns for irregular investments/withdrawals.\n\n**Use when:** Multiple SIPs with different amounts or timing\n**Better than:** Simple returns for complex portfolios",
            'nav': "💰 **NAV** (Net Asset Value) is mutual fund's per-unit market price.\n\n**Changes daily** based on underlying assets\n**Buy/Sell price** = NAV + entry/exit load",
            'expense_ratio': "📉 **Expense ratio** is annual fee charged by mutual funds (0.2-2%).\n\n**Impact:** Lower is better for long-term returns\n**Example:** 1% fee on ₹10L = ₹10,000/year",
        }
    
    def get_response(self, user_message):
        """Generate response based on user input"""
        user_message_lower = user_message.lower()
        
        # Check for greetings
        if any(greeting in user_message_lower for greeting in ['hi', 'hello', 'hey', 'namaste']):
            return self.intents['greeting']['responses'][0]
        
        # Check each intent
        for intent, data in self.intents.items():
            if any(keyword in user_message_lower for keyword in data['keywords']):
                response = random.choice(data['responses'])
                
                # Add personalized context if available
                if 'emergency' in intent and st.session_state.get('user_data'):
                    expenses = sum(st.session_state.user_data.get('expenses', {}).values())
                    if expenses > 0:
                        needed = expenses * 6
                        response = response.replace('Check Dashboard for exact amount needed!', f'Based on your monthly expenses of ₹{expenses:,.0f}, you need an emergency fund of ₹{needed:,.0f} (6 months expenses).')
                
                if 'investment' in intent and st.session_state.get('user_data'):
                    monthly_income = st.session_state.user_data.get('monthly_income', 0)
                    if monthly_income > 0:
                        ideal_sip = monthly_income * 0.2
                        response += f"\n\n💡 **Based on your monthly income of ₹{monthly_income:,.0f}**, you can comfortably invest ₹{ideal_sip:,.0f} per month (20% of income)."
                
                return response
        
        # Check for financial concepts
        for concept, explanation in self.financial_concepts.items():
            if concept in user_message_lower:
                return f"{explanation}\n\n📚 Want to learn more? Check the Learn section!"
        
        # Check personal data questions
        if 'my' in user_message_lower and st.session_state.get('user_data'):
            if 'income' in user_message_lower:
                income = st.session_state.user_data.get('monthly_income', 0)
                return f"💰 Based on your financial snapshot, your monthly income is **₹{income:,.0f}**. Want to optimize your savings or investment strategy?"
            elif 'expense' in user_message_lower:
                expenses = sum(st.session_state.user_data.get('expenses', {}).values())
                return f"📊 Your total monthly expenses are **₹{expenses:,.0f}**. You can view the detailed breakdown in your Dashboard!"
        
        return """🤔 I'm here to help with your financial questions! Here's what I can assist with:

**💰 Investments** • SIP vs Lump Sum • Mutual Funds • Portfolio diversification

**🏦 Tax Planning** • Section 80C options • NPS benefits • Tax-saving strategies

**🎯 Financial Planning** • Goal-based investing • Retirement planning • Emergency fund

**📊 Analysis** • Risk profile assessment • Return calculations

Try asking: 'How to start SIP?' or 'Best tax saving options?' or use the navigation tabs above! 💡"""

# --- Enhanced Data Persistence with Auto-Save ---
DATA_DIR = '.ai_financial_data'
os.makedirs(DATA_DIR, exist_ok=True)
SNAPSHOT_FILE = os.path.join(DATA_DIR, 'user_snapshot.json')
GOALS_FILE = os.path.join(DATA_DIR, 'user_goals.json')
PORTFOLIO_FILE = os.path.join(DATA_DIR, 'user_portfolio.json')
QUIZ_FILE = os.path.join(DATA_DIR, 'quiz_results.json')
TAX_FILE = os.path.join(DATA_DIR, 'tax_investments.json')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')
os.makedirs(BACKUP_DIR, exist_ok=True)

def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return default

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    backup_path = os.path.join(BACKUP_DIR, f"{os.path.basename(path)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(backup_path, 'w') as f:
        json.dump(data, f, indent=2)

def auto_save_all():
    if st.session_state.user_data:
        save_json(SNAPSHOT_FILE, st.session_state.user_data)
    if st.session_state.goals:
        save_json(GOALS_FILE, st.session_state.goals)
    if st.session_state.portfolio:
        save_json(PORTFOLIO_FILE, st.session_state.portfolio)

# --- Super Impressive Enhanced Light Theme ---
st.markdown("""
<style>
    .main { background-color: #ffffff; }
    .stApp { background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); }
    .main .block-container {
        background-color: #ffffff;
        padding: 2rem 1.5rem;
        border-radius: 20px;
        box-shadow: 0 8px 40px rgba(0,0,0,0.12);
        margin: 1rem auto;
        max-width: 1400px;
    }
    h1, h2, h3, h4, h5, h6 { color: #1e293b !important; font-weight: 700 !important; }
    p, div, span, label { color: #374151 !important; font-size: 1rem; line-height: 1.6; }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.1); border-color: #667eea; }
    .metric-value { font-size: 2.5rem !important; font-weight: 800 !important; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .financial-sticker {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 2px solid #86efac;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #22c55e;
    }
    .recommendation-card {
        background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
        border: 2px solid #c4b5fd;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #8b5cf6;
    }
    .quiz-question {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 2px solid #7dd3fc;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f8fafc;
        border-radius: 12px 12px 0 0;
        padding: 12px 20px;
        font-weight: 600;
        border: 1px solid #e2e8f0;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    @media (max-width: 768px) {
        .main .block-container { padding: 1rem; }
        .metric-value { font-size: 1.8rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- Floating Chatbot Widget (Appears on Every Page) ---
def init_floating_chatbot():
    """Initialize chatbot session state"""
    if 'floating_chat_messages' not in st.session_state:
        st.session_state.floating_chat_messages = [
            {'role': 'assistant', 'content': "👋 Hi! I'm your AI Financial Assistant. Ask me about investments, taxes, SIP, retirement, or any financial topic!"}
        ]
    if 'show_floating_chat' not in st.session_state:
        st.session_state.show_floating_chat = False
    if 'floating_chatbot' not in st.session_state:
        st.session_state.floating_chatbot = FinancialChatbot()

def get_floating_chat_response(user_input):
    """Get response from chatbot"""
    return st.session_state.floating_chatbot.get_response(user_input)

# Initialize floating chatbot
init_floating_chatbot()

# Floating Chatbot CSS
st.markdown("""
<style>
.floating-chat-button {
    position: fixed;
    bottom: 25px;
    right: 25px;
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.5);
    transition: all 0.3s ease;
    z-index: 1000;
    border: none;
    font-size: 28px;
    color: white;
}
.floating-chat-button:hover {
    transform: scale(1.1);
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.7);
}
.floating-chat-window {
    position: fixed;
    bottom: 100px;
    right: 25px;
    width: 380px;
    height: 520px;
    background: white;
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.25);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    z-index: 999;
    border: 1px solid #e2e8f0;
    animation: slideUp 0.3s ease;
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}
.floating-chat-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: bold;
}
.floating-chat-header button {
    background: none;
    border: none;
    color: white;
    font-size: 20px;
    cursor: pointer;
    font-weight: bold;
}
.floating-chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    background: #f8fafc;
}
.floating-message-user {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 8px 14px;
    border-radius: 18px;
    margin: 6px 0;
    text-align: right;
    max-width: 85%;
    margin-left: auto;
    word-wrap: break-word;
    font-size: 13px;
}
.floating-message-bot {
    background: #f0fdf4;
    border: 1px solid #86efac;
    color: #166534;
    padding: 8px 14px;
    border-radius: 18px;
    margin: 6px 0;
    max-width: 85%;
    word-wrap: break-word;
    font-size: 13px;
}
.floating-chat-input {
    padding: 10px;
    border-top: 1px solid #e2e8f0;
    display: flex;
    gap: 8px;
    background: white;
}
.floating-chat-input input {
    flex: 1;
    padding: 10px;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    outline: none;
    font-size: 13px;
}
.floating-chat-input input:focus {
    border-color: #667eea;
}
.floating-chat-input button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 20px;
    cursor: pointer;
    font-size: 13px;
}
.floating-quick-actions {
    padding: 8px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    background: #f8fafc;
    border-top: 1px solid #e2e8f0;
}
.floating-quick-btn {
    background: white;
    border: 1px solid #c4b5fd;
    border-radius: 15px;
    padding: 4px 10px;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.2s;
    color: #5b21b6;
}
.floating-quick-btn:hover {
    background: #f3e8ff;
    border-color: #8b5cf6;
}
</style>
""", unsafe_allow_html=True)

# Floating Chat Button
st.markdown("""
<button class="floating-chat-button" onclick="document.querySelector('.floating-chat-window').style.display='flex'">
    💬
</button>
""", unsafe_allow_html=True)

# Chat Window Toggle
col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
with col5:
    if st.button("💬 Chat", key="toggle_chat_btn", help="Open AI Assistant"):
        st.session_state.show_floating_chat = not st.session_state.show_floating_chat
        st.rerun()

# Chat Window
if st.session_state.show_floating_chat:
    with st.container():
        st.markdown('<div class="floating-chat-window">', unsafe_allow_html=True)
        
        # Header
        st.markdown("""
        <div class="floating-chat-header">
            <span>🤖 AI Financial Assistant</span>
            <button onclick="parent.document.querySelector(\'.floating-chat-window\').style.display=\'none\'">✕</button>
        </div>
        """, unsafe_allow_html=True)
        
        # Messages
        st.markdown('<div class="floating-chat-messages">', unsafe_allow_html=True)
        for msg in st.session_state.floating_chat_messages[-15:]:
            if msg['role'] == 'user':
                st.markdown(f'<div class="floating-message-user">👤 {msg["content"][:200]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="floating-message-bot">🤖 {msg["content"][:300]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick Actions
        st.markdown('<div class="floating-quick-actions">', unsafe_allow_html=True)
        quick_btns = ["💰 SIP", "🏦 Tax Saving", "🎯 Emergency Fund", "📈 Mutual Funds"]
        for qb in quick_btns:
            if st.button(qb, key=f"float_q_{qb}"):
                st.session_state.floating_chat_messages.append({'role': 'user', 'content': f"Tell me about {qb}"})
                response = get_floating_chat_response(f"Tell me about {qb}")
                st.session_state.floating_chat_messages.append({'role': 'assistant', 'content': response})
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Input Area
        st.markdown('<div class="floating-chat-input">', unsafe_allow_html=True)
        chat_input = st.text_input("", key="float_chat_input", placeholder="Ask me anything about finance...", label_visibility="collapsed")
        send_clicked = st.button("Send", key="float_send_btn")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if send_clicked and chat_input:
            st.session_state.floating_chat_messages.append({'role': 'user', 'content': chat_input})
            response = get_floating_chat_response(chat_input)
            st.session_state.floating_chat_messages.append({'role': 'assistant', 'content': response})
            st.rerun()

# --- Load saved data on startup ---
def load_all_saved_data():
    saved_snapshot = load_json(SNAPSHOT_FILE, None)
    if saved_snapshot and not st.session_state.user_data:
        st.session_state.user_data = saved_snapshot
    saved_goals = load_json(GOALS_FILE, None)
    if saved_goals and not st.session_state.goals:
        st.session_state.goals = saved_goals
    saved_portfolio = load_json(PORTFOLIO_FILE, None)
    if saved_portfolio and not st.session_state.portfolio:
        st.session_state.portfolio = saved_portfolio

# --- Auto-save check ---
if 'last_auto_save' not in st.session_state:
    st.session_state.last_auto_save = datetime.now()
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'goals' not in st.session_state:
    st.session_state.goals = []
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = "📊 Snapshot"
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False
if 'tax_investments' not in st.session_state:
    st.session_state.tax_investments = {}
if 'quiz_results' not in st.session_state:
    st.session_state.quiz_results = None

# Load saved data
load_all_saved_data()

# Auto-save every 5 minutes
current_time = datetime.now()
if (current_time - st.session_state.last_auto_save).seconds >= 300:
    auto_save_all()
    st.session_state.last_auto_save = current_time

# --- Helper Functions ---
def format_currency(amount):
    return f"₹{amount:,.0f}"

def investment_projection_calculator(monthly_investment, years, expected_return):
    monthly_rate = expected_return / 100 / 12
    months = int(years * 12)
    if monthly_rate > 0:
        future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    else:
        future_value = monthly_investment * months
    total_invested = monthly_investment * months
    profit = future_value - total_invested
    return future_value, total_invested, profit

def apply_plotly_theme(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=14, color="#1e293b"),
        title=dict(font=dict(size=20, color="#1e293b"), x=0.5),
        legend=dict(bgcolor='rgba(255,255,255,0.9)', bordercolor='#e2e8f0', borderwidth=1)
    )
    return fig

@st.cache_data
def get_mutual_fund_data():
    data = {
        'Category': ['Large Cap', 'Large Cap', 'Mid Cap', 'Mid Cap', 'Small Cap', 'Small Cap', 'Flexi Cap', 'ELSS', 'ELSS', 'Debt', 'Debt'],
        'Fund Name': ['Axis Bluechip Fund', 'Mirae Asset Large Cap', 'Axis Midcap Fund', 'Kotak Emerging Equity', 'Axis Small Cap Fund', 'SBI Small Cap Fund', 'Parag Parikh Flexi Cap', 'Mirae Asset Tax Saver', 'Canara Robeco Equity Tax Saver', 'ICICI Prudential Corporate Bond', 'HDFC Short Term Debt'],
        '1Y Return': [15.2, 16.1, 25.6, 27.2, 35.8, 38.2, 22.1, 20.3, 21.1, 7.1, 6.8],
        '3Y CAGR': [14.5, 15.2, 22.1, 23.5, 28.9, 30.1, 19.8, 18.5, 19.2, 6.5, 6.2],
        '5Y CAGR': [16.1, 17.2, 20.5, 21.8, 25.4, 26.8, 18.9, 17.2, 18.1, 7.5, 7.2],
        'Risk': ['Moderate', 'Moderate', 'High', 'High', 'Very High', 'Very High', 'High', 'High', 'High', 'Low', 'Low'],
        'Rating': [5, 5, 5, 4, 5, 4, 5, 5, 4, 4, 3]
    }
    return pd.DataFrame(data)

# --- Enhanced PDF Report Generator ---
class PDFReportGenerator:
    def create_comprehensive_pdf(self, user_data, goals, portfolio, quiz_results=None, ml_insights=None):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=72, bottomMargin=72)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1e293b'), spaceAfter=30, alignment=1)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#374151'), spaceAfter=12)
        normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#4b5563'), spaceAfter=6)
        
        story = []
        story.append(Paragraph("AI Financial Advisor - Comprehensive Report", title_style))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}", normal_style))
        story.append(Spacer(1, 20))
        
        total_expenses = sum(user_data.get('expenses', {}).values())
        monthly_savings = user_data.get('monthly_income', 0) - total_expenses
        story.append(Paragraph(f"Monthly Income: ₹{user_data.get('monthly_income', 0):,}", normal_style))
        story.append(Paragraph(f"Monthly Savings: ₹{monthly_savings:,}", normal_style))
        story.append(Spacer(1, 15))
        
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data

# --- ML Financial Predictor ---
class MLFinancialPredictor:
    def predict_risk_tolerance(self, user_data):
        monthly_income = user_data.get('monthly_income', 50000)
        current_savings = user_data.get('current_savings', 100000)
        risk_score = (monthly_income / 100000) * 5 + (current_savings / 500000) * 5
        if risk_score < 4:
            return "🛡️ Conservative", 0.3, risk_score, "Low risk appetite"
        elif risk_score < 7:
            return "⚖️ Balanced", 0.5, risk_score, "Moderate risk"
        else:
            return "🚀 Aggressive", 0.7, risk_score, "High risk tolerance"

    def get_financial_recommendations(self, user_data, metrics):
        recommendations = []
        monthly_income = user_data.get('monthly_income', 0)
        total_expenses = sum(user_data.get('expenses', {}).values())
        savings_rate = ((monthly_income - total_expenses) / monthly_income) * 100 if monthly_income > 0 else 0
        
        if savings_rate < 10:
            recommendations.append("🚨 Increase your savings rate to at least 15-20%")
        elif savings_rate < 15:
            recommendations.append("📈 Good progress! Try to reach 20% savings rate")
        else:
            recommendations.append("🎉 Excellent savings rate! Maintain this discipline")
        
        emergency_months = user_data.get('current_savings', 0) / total_expenses if total_expenses > 0 else 0
        if emergency_months < 3:
            recommendations.append("🛡️ Build emergency fund to cover 3-6 months of expenses")
        
        return recommendations

# --- Financial Behavior Quiz ---
class FinancialBehaviorQuiz:
    def __init__(self):
        self.questions = [
            {'id': 1, 'question': '💰 How do you react when the stock market drops by 20%?', 
             'options': [{'text': 'Sell everything', 'score': 1}, {'text': 'Hold and wait', 'score': 3}, {'text': 'Review but maintain', 'score': 5}, {'text': 'Buy more', 'score': 7}]},
            {'id': 2, 'question': '📈 What is your primary investment goal?',
             'options': [{'text': 'Capital preservation', 'score': 2}, {'text': 'Steady growth', 'score': 4}, {'text': 'Balanced growth', 'score': 6}, {'text': 'Maximum growth', 'score': 8}]},
            {'id': 3, 'question': '⏰ What is your preferred investment time horizon?',
             'options': [{'text': '1-2 years', 'score': 2}, {'text': '3-5 years', 'score': 4}, {'text': '5-10 years', 'score': 6}, {'text': '10+ years', 'score': 8}]},
            {'id': 4, 'question': '🎯 How much volatility can you tolerate?',
             'options': [{'text': 'Minimal', 'score': 1}, {'text': 'Low', 'score': 3}, {'text': 'Moderate', 'score': 5}, {'text': 'High', 'score': 7}]}
        ]
    
    def calculate_personality(self, answers):
        total_score = sum(answers.values())
        max_score = len(self.questions) * 8
        score_percentage = (total_score / max_score) * 100
        
        if score_percentage <= 30:
            return {'personality': '🛡️ Conservative Defender', 'risk_level': 'Low', 'score': total_score, 'score_percentage': score_percentage}
        elif score_percentage <= 50:
            return {'personality': '📊 Cautious Planner', 'risk_level': 'Low to Moderate', 'score': total_score, 'score_percentage': score_percentage}
        elif score_percentage <= 70:
            return {'personality': '⚖️ Balanced Grower', 'risk_level': 'Moderate', 'score': total_score, 'score_percentage': score_percentage}
        else:
            return {'personality': '🚀 Aggressive Builder', 'risk_level': 'High', 'score': total_score, 'score_percentage': score_percentage}

# --- Main App Header ---
st.markdown("""
<div style='text-align: center; margin-bottom: 1.5rem;'>
    <h1 style='font-size: 3rem; margin-bottom: 0.5rem;'>🤖 AI Financial Advisor</h1>
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 16px; margin: 0.5rem auto; max-width: 700px;'>
        <h2 style='color: white; margin: 0; font-size: 1.5rem;'>Advanced ML-Powered Financial Planning</h2>
        <p style='color: white; margin: 0.3rem 0 0 0; opacity: 0.95; font-size: 1rem;'>Smart Analytics • ML Predictions • AI Chatbot • Personalized Recommendations</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Privacy Banner ---
st.markdown("""
<div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 1rem; border-radius: 12px; margin: 0 0 1rem 0; text-align: center;'>
    <h3 style='color: white; margin: 0; font-size: 1.2rem;'>🔒 100% Private & Secure</h3>
    <p style='color: white; margin: 0.3rem 0 0 0; font-size: 0.9rem;'>All data stored locally • No data shared • Auto-saved every 5 minutes • AI Chatbot for instant help</p>
</div>
""", unsafe_allow_html=True)

# --- Quick Actions ---
st.markdown("### 🚀 Quick Actions")
qcols = st.columns(6)
qactions = [("📊", "Dashboard", "📈 Dashboard"), ("🎯", "Add Goal", "🎯 Goals Planner"), ("💰", "Invest", "💹 Investment Center"), ("📥", "Export", "📥 Export"), ("🧠", "Quiz", "🧠 Behavior Quiz"), ("💬", "Chat", "💬 Chat Assistant")]
for i, (icon, label, page) in enumerate(qactions):
    with qcols[i]:
        if st.button(f"{icon} {label}", key=f"qa_{i}", use_container_width=True):
            st.session_state.current_page = page
            st.rerun()

st.markdown("---")

# --- Navigation ---
nav_options = ["📊 Snapshot", "📈 Dashboard", "🤖 ML Insights", "🧠 Behavior Quiz", "💹 Investment Center", "🎯 Goals Planner", "💼 Portfolio", "🏦 Tax Planner", "📚 Learn", "📥 Export", "👨‍💻 Developer"]

nav_cols = st.columns(len(nav_options))
for i, option in enumerate(nav_options):
    with nav_cols[i]:
        if st.button(option, key=f"nav_{i}", use_container_width=True):
            st.session_state.current_page = option
            st.rerun()

st.markdown("---")

# ========== PAGE ROUTING ==========

# --- Snapshot Page ---
if st.session_state.current_page == "📊 Snapshot":
    st.header('📊 Financial Snapshot')
    
    with st.form('snapshot_form'):
        col1, col2 = st.columns(2)
        with col1:
            monthly_income = st.number_input('Monthly Income (₹)', min_value=0.0, value=st.session_state.user_data.get('monthly_income', 0.0), step=1000.0)
            current_savings = st.number_input('Current Savings (₹)', min_value=0.0, value=st.session_state.user_data.get('current_savings', 0.0), step=5000.0)
            investment_percentage = st.slider('% of Income to Invest', 0, 100, st.session_state.user_data.get('investment_percentage', 0))
            age = st.number_input('Your Age', min_value=18, max_value=80, value=st.session_state.user_data.get('age', 30))
        with col2:
            rent = st.number_input('🏠 Rent/EMI (₹)', 0.0, value=st.session_state.user_data.get('expenses', {}).get('Rent', 0.0), step=1000.0)
            groceries = st.number_input('🛒 Groceries (₹)', 0.0, value=st.session_state.user_data.get('expenses', {}).get('Groceries', 0.0), step=500.0)
            transport = st.number_input('🚗 Transport (₹)', 0.0, value=st.session_state.user_data.get('expenses', {}).get('Transport', 0.0), step=500.0)
            entertainment = st.number_input('🍽️ Entertainment (₹)', 0.0, value=st.session_state.user_data.get('expenses', {}).get('Entertainment', 0.0), step=500.0)
        
        if st.form_submit_button('💾 Save Financial Snapshot', use_container_width=True):
            st.session_state.user_data = {
                'monthly_income': monthly_income,
                'current_savings': current_savings,
                'investment_percentage': investment_percentage,
                'age': age,
                'expenses': {'Rent': rent, 'Groceries': groceries, 'Transport': transport, 'Entertainment': entertainment},
                'assets': {'Cash': 0, 'Investments': 0},
                'liabilities': {'Loans': 0}
            }
            save_json(SNAPSHOT_FILE, st.session_state.user_data)
            st.success('✅ Financial Snapshot saved! Data auto-saved every 5 minutes.')
            st.balloons()

# --- Dashboard Page ---
elif st.session_state.current_page == "📈 Dashboard":
    st.header('📈 Financial Dashboard')
    
    if not st.session_state.user_data:
        st.warning("⚠️ No financial snapshot found. Please create one in 'Snapshot' first!")
    else:
        user_data = st.session_state.user_data
        total_expenses = sum(user_data.get('expenses', {}).values())
        monthly_savings = user_data.get('monthly_income', 0) - total_expenses
        savings_rate = (monthly_savings / max(user_data.get('monthly_income', 1), 1)) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Monthly Income", format_currency(user_data.get('monthly_income', 0)))
        with col2:
            st.metric("💸 Monthly Expenses", format_currency(total_expenses))
        with col3:
            st.metric("📊 Savings Rate", f"{savings_rate:.1f}%")
        with col4:
            st.metric("🏦 Net Worth", format_currency(user_data.get('current_savings', 0)))
        
        # Expense Chart
        if total_expenses > 0:
            expense_df = pd.DataFrame(list(user_data.get('expenses', {}).items()), columns=['Category', 'Amount'])
            fig = px.pie(expense_df, values='Amount', names='Category', title='Expense Breakdown')
            fig = apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

# --- ML Insights Page ---
elif st.session_state.current_page == "🤖 ML Insights":
    st.header('🤖 ML Insights')
    
    if not st.session_state.user_data:
        st.warning("⚠️ Please create a financial snapshot first!")
    else:
        analyzer = MLFinancialPredictor()
        risk_profile, _, risk_score, _ = analyzer.predict_risk_tolerance(st.session_state.user_data)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='metric-card'><h3>🎯 Risk Profile</h3><h1 style='color:#667eea'>{risk_profile}</h1><p>Risk Score: {risk_score:.1f}/10</p></div>", unsafe_allow_html=True)
        with col2:
            metrics = {'monthly_income': st.session_state.user_data.get('monthly_income', 0), 'total_expenses': sum(st.session_state.user_data.get('expenses', {}).values()), 'monthly_savings': 0, 'savings_rate': 0, 'current_savings': st.session_state.user_data.get('current_savings', 0)}
            recommendations = analyzer.get_financial_recommendations(st.session_state.user_data, metrics)
            for rec in recommendations[:2]:
                st.markdown(f"<div class='recommendation-card'>{rec}</div>", unsafe_allow_html=True)

# --- Behavior Quiz Page ---
elif st.session_state.current_page == "🧠 Behavior Quiz":
    st.header('🧠 Financial Behavior Quiz')
    
    quiz = FinancialBehaviorQuiz()
    
    if not st.session_state.quiz_completed:
        current_q = quiz.questions[st.session_state.current_question]
        st.markdown(f"<div class='quiz-question'><h3>Question {st.session_state.current_question + 1} of {len(quiz.questions)}</h3><h4>{current_q['question']}</h4></div>", unsafe_allow_html=True)
        
        for i, opt in enumerate(current_q['options']):
            if st.button(opt['text'], key=f"q{current_q['id']}_opt{i}", use_container_width=True):
                st.session_state.quiz_answers[current_q['id']] = opt['score']
                if st.session_state.current_question < len(quiz.questions) - 1:
                    st.session_state.current_question += 1
                else:
                    st.session_state.quiz_completed = True
                st.rerun()
        
        progress = (st.session_state.current_question + 1) / len(quiz.questions)
        st.progress(progress, text=f"Progress: {int(progress*100)}%")
    else:
        st.balloons()
        result = quiz.calculate_personality(st.session_state.quiz_answers)
        st.session_state.quiz_results = result
        st.markdown(f"<div class='financial-sticker'><h2>{result['personality']}</h2><h3>Risk Level: {result['risk_level']}</h3><p>Score: {result['score']} ({result['score_percentage']:.1f}%)</p></div>", unsafe_allow_html=True)
        
        if st.button("🔄 Take Quiz Again", use_container_width=True):
            st.session_state.quiz_answers = {}
            st.session_state.current_question = 0
            st.session_state.quiz_completed = False
            st.rerun()

# --- Investment Center Page ---
elif st.session_state.current_page == "💹 Investment Center":
    st.header('💹 Investment Center')
    
    mf_df = get_mutual_fund_data()
    tab1, tab2 = st.tabs(["💰 Lump Sum Calculator", "📅 SIP Calculator"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            invest_amt = st.number_input('Investment Amount (₹)', min_value=1000.0, value=50000.0, step=1000.0)
            years = st.slider('Investment Period (Years)', 1, 20, 5)
            returns = st.slider('Expected Return (%)', 5, 20, 12)
        with col2:
            future_value = invest_amt * ((1 + returns/100) ** years)
            st.markdown(f"<div class='metric-card'><h3>📊 Projection</h3><p>Future Value: <strong>{format_currency(future_value)}</strong></p><p>Total Profit: <strong>{format_currency(future_value - invest_amt)}</strong></p></div>", unsafe_allow_html=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            monthly_sip = st.number_input('Monthly SIP (₹)', min_value=500.0, value=5000.0, step=500.0)
            sip_years = st.slider('Investment Period (Years)', 1, 30, 10)
            sip_returns = st.slider('Expected Return (%)', 5, 20, 12)
        with col2:
            future_value, total_invested, profit = investment_projection_calculator(monthly_sip, sip_years, sip_returns)
            st.markdown(f"<div class='metric-card'><h3>📊 SIP Projection</h3><p>Future Value: <strong>{format_currency(future_value)}</strong></p><p>Total Invested: {format_currency(total_invested)}</p><p>Profit: {format_currency(profit)}</p></div>", unsafe_allow_html=True)

# --- Goals Planner Page ---
elif st.session_state.current_page == "🎯 Goals Planner":
    st.header('🎯 Goals Planner')
    
    with st.form('goal_form'):
        col1, col2, col3 = st.columns(3)
        with col1:
            goal_name = st.text_input('Goal Name', placeholder='e.g., Dream House')
        with col2:
            goal_amount = st.number_input('Target Amount (₹)', min_value=0.0, value=500000.0, step=10000.0)
        with col3:
            goal_years = st.number_input('Years to Achieve', min_value=1, value=5)
        
        if st.form_submit_button('🎯 Add Goal', use_container_width=True) and goal_name:
            st.session_state.goals.append({'name': goal_name, 'amount': goal_amount, 'years': goal_years, 'return': 12})
            save_json(GOALS_FILE, st.session_state.goals)
            st.success(f'Goal "{goal_name}" added!')
            st.rerun()
    
    if st.session_state.goals:
        for i, goal in enumerate(st.session_state.goals):
            r = 12/100/12
            n = goal['years']*12
            sip = goal['amount'] * (r / ((1+r)**n - 1)) if r > 0 else goal['amount'] / n
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"<div class='metric-card'><h4>🎯 {goal['name']}</h4><p>Target: {format_currency(goal['amount'])} | Timeline: {goal['years']} years</p><p><strong>Monthly SIP Required: {format_currency(sip)}</strong></p></div>", unsafe_allow_html=True)
            with col2:
                if st.button('🗑️ Delete', key=f'del_{i}'):
                    st.session_state.goals.pop(i)
                    save_json(GOALS_FILE, st.session_state.goals)
                    st.rerun()

# --- Portfolio Page ---
elif st.session_state.current_page == "💼 Portfolio":
    st.header('💼 Portfolio Manager')
    
    with st.form('portfolio_form'):
        col1, col2, col3 = st.columns(3)
        with col1:
            holding_name = st.text_input('Holding Name')
        with col2:
            amount = st.number_input('Amount (₹)', min_value=0.0, step=1000.0)
        with col3:
            category = st.selectbox('Category', ['Stocks', 'Mutual Funds', 'FD', 'Gold', 'Other'])
        
        if st.form_submit_button('➕ Add Holding', use_container_width=True) and holding_name and amount>0:
            st.session_state.portfolio.append({'name': holding_name, 'amount': amount, 'category': category})
            save_json(PORTFOLIO_FILE, st.session_state.portfolio)
            st.success('Holding added!')
            st.rerun()
    
    if st.session_state.portfolio:
        pf_df = pd.DataFrame(st.session_state.portfolio)
        total = pf_df['amount'].sum()
        if total > 0:
            fig = px.pie(pf_df, values='amount', names='category', title='Portfolio Allocation')
            fig = apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(pf_df.style.format({'amount': '₹{:,.0f}'}), use_container_width=True)

# --- Tax Planner Page ---
elif st.session_state.current_page == "🏦 Tax Planner":
    st.header('🏦 Tax Planner')
    
    st.markdown("""
    <div class='financial-sticker'>
        <h3>💡 Top Tax Saving Options</h3>
        <p><strong>ELSS</strong> - 3yr lock-in, 12-15% returns, up to ₹1.5L deduction<br>
        <strong>PPF</strong> - 15yr, 7.1% safe returns, tax-free<br>
        <strong>NPS</strong> - Retirement, extra ₹50k deduction<br>
        <strong>Health Insurance</strong> - Up to ₹25k/₹50k deduction</p>
    </div>
    """, unsafe_allow_html=True)
    
    annual_income = st.session_state.user_data.get('monthly_income', 0) * 12 if st.session_state.user_data else 0
    if annual_income > 0:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Annual Income", format_currency(annual_income))
        with col2:
            if annual_income <= 700000:
                tax = 0
            elif annual_income <= 900000:
                tax = (annual_income - 700000) * 0.05
            elif annual_income <= 1200000:
                tax = 10000 + (annual_income - 900000) * 0.20
            else:
                tax = 70000 + (annual_income - 1200000) * 0.30
            st.metric("Estimated Tax", format_currency(tax))

# --- Learn Page ---
elif st.session_state.current_page == "📚 Learn":
    st.header('📚 Financial Education')
    
    topics = {
        '💰 SIP Investing': 'SIP allows you to invest small amounts regularly. Benefits: Rupee cost averaging, power of compounding, disciplined investing.',
        '🏦 Tax Saving': 'Section 80C allows ₹1.5L deduction. Best options: ELSS (3yr lock-in, 12-15% returns), PPF (safe 7.1%), NPS (extra ₹50k).',
        '🎯 Risk Management': 'Asset allocation is key. Rule: (100 - age)% in equity. Diversify across large cap, mid cap, debt, and gold.',
        '📈 Mutual Funds': 'Types: Large Cap (stable), Mid Cap (growth), Small Cap (high risk), Debt (safe), ELSS (tax saving).'
    }
    
    for title, content in topics.items():
        with st.expander(f"📖 {title}", expanded=True):
            st.write(content)

# --- Export Page ---
elif st.session_state.current_page == "📥 Export":
    st.header('📥 Export Reports')
    
    if st.button('📊 Generate PDF Report', use_container_width=True) and st.session_state.user_data:
        pdf_gen = PDFReportGenerator()
        analyzer = MLFinancialPredictor()
        risk_profile, _, _, _ = analyzer.predict_risk_tolerance(st.session_state.user_data)
        pdf_data = pdf_gen.create_comprehensive_pdf(st.session_state.user_data, st.session_state.goals, st.session_state.portfolio, st.session_state.quiz_results, {'risk_profile': risk_profile})
        st.download_button('📥 Download PDF', pdf_data, f'financial_report_{datetime.now().strftime("%Y%m%d")}.pdf', 'application/pdf')
        st.success("PDF generated!")

# --- Developer Page ---
elif st.session_state.current_page == "👨‍💻 Developer":
    st.header('👨‍💻 About Developer')
    
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; color: white;'>
        <div style='font-size: 3rem;'>🤖</div>
        <h1 style='color: white;'>Ayush Shukla</h1>
        <p>Data Scientist & ML Engineer</p>
        <p>Building intelligent financial solutions with machine learning</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("[🐙 GitHub](https://github.com/asdharupur1-boop/Finance_app)")
    with col2:
        st.markdown("[💼 LinkedIn](https://www.linkedin.com/in/ayush-shukla-890072337/)")
    with col3:
        st.markdown("[📧 Email](mailto:Asdharupur1@gmail.com)")

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 1rem;'>
    <p>Built with ❤️ by Ayush Shukla | AI Financial Advisor v5.0</p>
    <p>🤖 Powered by ML & AI Chatbot | 🔒 100% Private | 💾 Auto-saves every 5 minutes</p>
</div>
""", unsafe_allow_html=True)
