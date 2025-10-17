import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from io import BytesIO

# --- PDF using reportlab for Unicode support ---
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register a Unicode TTF if available (DejaVuSans commonly present). Fallback to Helvetica.
try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    DEFAULT_FONT = 'DejaVuSans'
except Exception:
    DEFAULT_FONT = 'Helvetica'

# --- App Config ---
st.set_page_config(page_title='AI Financial Advisor — By Ayush Shukla', page_icon='🤖', layout='wide')

# --- Enhanced CSS: More Attractive Design ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.main {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.main .block-container {
    padding: 2rem 1rem;
    max-width: 1400px;
    margin: 0 auto;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    margin-top: 1rem;
    margin-bottom: 2rem;
}

body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}

h1 {
    font-weight: 800 !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 1rem !important;
}

h2 {
    font-weight: 700 !important;
    color: #1e293b !important;
    border-left: 4px solid #667eea;
    padding-left: 12px;
    margin-top: 2rem !important;
}

h3 {
    font-weight: 600 !important;
    color: #334155 !important;
}

.metric-card, .report-section {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 16px;
    padding: 25px;
    box-shadow: 0 8px 25px rgba(15,23,42,0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    margin-bottom: 1.5rem;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.metric-card:hover, .report-section:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(15,23,42,0.15);
}

.stButton>button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    border: none;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.stProgress > div > div > div > div {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.muted {
    color: #64748b !important;
}

.small {
    font-size: 0.9em;
    color: #64748b;
}

.emoji-container {
    font-size: 3rem;
    text-align: center;
    margin: 1rem 0;
}

.achievement-badge {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.8em;
    font-weight: 600;
    display: inline-block;
    margin: 5px;
}

.developer-section {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    color: white;
    padding: 2rem;
    border-radius: 16px;
    text-align: center;
    margin-top: 2rem;
}

.social-links {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 1rem;
}

.social-link {
    color: white;
    text-decoration: none;
    padding: 10px 20px;
    border-radius: 10px;
    background: rgba(255,255,255,0.1);
    transition: all 0.3s ease;
}

.social-link:hover {
    background: rgba(255,255,255,0.2);
    transform: translateY(-2px);
}

.financial-sticker {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border: 2px solid #bae6fd;
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    margin: 10px 0;
}

.positive-trend {
    color: #10b981;
    font-weight: 600;
}

.negative-trend {
    color: #ef4444;
    font-weight: 600;
}

/* Custom select box styling */
.stSelectbox>div>div {
    background: white;
    border-radius: 10px;
    border: 2px solid #e2e8f0;
}

/* Custom number input styling */
.stNumberInput>div>div>input {
    border-radius: 10px;
    border: 2px solid #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

# --- Persistence ---
DATA_DIR = '.ai_financial_data'
os.makedirs(DATA_DIR, exist_ok=True)
SNAPSHOT_FILE = os.path.join(DATA_DIR, 'user_snapshot.json')
GOALS_FILE = os.path.join(DATA_DIR, 'user_goals.json')
PORTFOLIO_FILE = os.path.join(DATA_DIR, 'user_portfolio.json')

# --- Helpers ---

def format_inr(x):
    try:
        return f"₹{x:,.0f}"
    except Exception:
        return str(x)


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

# --- Core logic classes ---
class FinancialAnalyzer:
    def __init__(self, user_data):
        self.user_data = user_data or {}
        self.monthly_income = float(self.user_data.get('monthly_income', 0) or 0)
        self.expenses = {k: float(v or 0) for k, v in self.user_data.get('expenses', {}).items()}
        self.investment_pct = float(self.user_data.get('investment_percentage', 0) or 0)
        self.current_savings = float(self.user_data.get('current_savings', 0) or 0)  # FIXED: Changed user_state to user_data
        self.assets = {k: float(v or 0) for k, v in self.user_data.get('assets', {}).items()}
        self.liabilities = {k: float(v or 0) for k, v in self.user_data.get('liabilities', {}).items()}

    def calculate_financial_metrics(self):
        total_expenses = sum(self.expenses.values())
        monthly_savings = self.monthly_income - total_expenses
        desired_investment = self.monthly_income * (self.investment_pct / 100)
        savings_rate = (monthly_savings / self.monthly_income) * 100 if self.monthly_income > 0 else 0
        expense_ratios = {c: (a / self.monthly_income) * 100 if self.monthly_income > 0 else 0 for c, a in self.expenses.items()}
        return {
            'total_expenses': total_expenses,
            'monthly_savings': monthly_savings,
            'desired_investment': desired_investment,
            'savings_rate': savings_rate,
            'expense_ratios': expense_ratios
        }

    def calculate_advanced_metrics(self, metrics):
        debt_payments = self.expenses.get('Rent/EMI', 0) + self.expenses.get('Other Loans', 0)
        dti_ratio = (debt_payments / self.monthly_income) * 100 if self.monthly_income > 0 else 0
        emergency_fund_coverage = (self.current_savings / metrics['total_expenses']) if metrics['total_expenses'] > 0 else 0
        annual_expenses = metrics['total_expenses'] * 12
        fire_number = annual_expenses * 25
        total_assets = sum(self.assets.values())
        total_liabilities = sum(self.liabilities.values())
        net_worth = total_assets - total_liabilities
        return {
            'dti_ratio': dti_ratio,
            'emergency_fund_target': metrics['total_expenses'] * 6,
            'emergency_fund_coverage': emergency_fund_coverage,
            'fire_number': fire_number,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'net_worth': net_worth
        }

    def generate_recommendations(self, metrics, advanced_metrics, risk_profile):
        recs = []
        if metrics['savings_rate'] < 15:
            recs.append('💰 Prioritize increasing your savings rate to at least 15-20% of income.')
        if advanced_metrics['dti_ratio'] > 40:
            recs.append('📉 Your Debt-to-Income (DTI) is high — prioritize high-interest debt reduction.')
        if advanced_metrics['emergency_fund_coverage'] < 3:
            recs.append('🛡️ Emergency fund low — aim for 3-6 months of essential expenses.')
        dining_ratio = metrics['expense_ratios'].get('Dining & Entertainment', 0)
        if dining_ratio > 10:
            recs.append('🍽️ Consider trimming Dining & Entertainment and redirect to savings or SIPs.')
        recs.append('⚡ Automate investments with SIPs to build discipline and leverage rupee-cost averaging.')
        if risk_profile == 'Conservative':
            recs.append('🛡️ As a Conservative investor, prefer debt funds, short-duration instruments and lower equity allocation.')
        elif risk_profile == 'Aggressive':
            recs.append('🚀 Aggressive investors can lean into equity; keep a solid emergency fund first.')
        else:
            recs.append('⚖️ Balanced profile: maintain a diversified mix of equity and debt.')
        return recs

# --- Utilities: SIP and projection calculators ---
def investment_projection_calculator(monthly_investment, years, expected_return):
    monthly_rate = expected_return / 100 / 12
    months = int(years * 12)
    if monthly_rate > 0:
        future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    else:
        future_value = monthly_investment * months
    total_invested = monthly_investment * months
    return future_value, total_invested

def fund_projection_amount(initial_amount, period_label, reported_return):
    if period_label.endswith('Y'):
        years = int(period_label[:-1])
        return initial_amount * ((1 + reported_return/100) ** years)
    elif period_label.endswith('M'):
        return initial_amount * (1 + reported_return/100)
    else:
        return initial_amount * (1 + reported_return/100)

# --- Enhanced PDF generation with graphs ---
def create_pdf_report_reportlab(metrics, advanced_metrics, recommendations, health_score, user_data, sim_data, expense_data, net_worth_data, sip_data=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    normal.fontName = DEFAULT_FONT
    heading = ParagraphStyle('heading', parent=styles['Heading1'], fontName=DEFAULT_FONT, fontSize=14)
    body = ParagraphStyle('body', parent=styles['BodyText'], fontName=DEFAULT_FONT, fontSize=10)

    elems = []
    elems.append(Paragraph('Your Financial Summary Report', heading))
    elems.append(Spacer(1, 6))
    elems.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", body))
    elems.append(Spacer(1, 12))

    # Financial Overview
    elems.append(Paragraph('📊 Key Financial Overview', styles['Heading2']))
    kv = [
        ['Monthly Income', f"INR {user_data.get('monthly_income',0):,.0f}"],
        ['Total Monthly Expenses', f"INR {metrics['total_expenses']:,.0f}"],
        ['Monthly Savings', f"INR {metrics['monthly_savings']:,.0f}"],
        ['Savings Rate', f"{metrics['savings_rate']:.1f}%"],
        ['Investment Percentage', f"{user_data.get('investment_percentage',0)}%"]
    ]
    t = Table(kv, hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(1,0),colors.whitesmoke), ('LINEBELOW',(0,0),(-1,0),1,colors.grey)]))
    elems.append(t)
    elems.append(Spacer(1,12))

    # Advanced Metrics
    elems.append(Paragraph('📈 Advanced Health Metrics', styles['Heading2']))
    adv = [
        ['Financial Health Score', f"{health_score}/100"],
        ['Debt-to-Income Ratio', f"{advanced_metrics['dti_ratio']:.1f}%"],
        ['Emergency Fund Coverage', f"{advanced_metrics['emergency_fund_coverage']:.1f} months"],
        ['Net Worth', f"INR {advanced_metrics['net_worth']:,.0f}"],
        ['Total Assets', f"INR {advanced_metrics['total_assets']:,.0f}"],
        ['Total Liabilities', f"INR {advanced_metrics['total_liabilities']:,.0f}"]
    ]
    t2 = Table(adv, hAlign='LEFT')
    elems.append(t2)
    elems.append(Spacer(1,12))

    # Expense Breakdown
    if expense_data:
        elems.append(Paragraph('💸 Expense Breakdown', styles['Heading2']))
        expense_table_data = [['Category', 'Amount (₹)', 'Percentage']]
        for category, amount in expense_data.items():
            if amount > 0:
                percentage = (amount / metrics['total_expenses']) * 100
                expense_table_data.append([category, f"{amount:,.0f}", f"{percentage:.1f}%"])
        t3 = Table(expense_table_data, hAlign='LEFT')
        elems.append(t3)
        elems.append(Spacer(1,12))

    # Net Worth Breakdown
    if net_worth_data:
        elems.append(Paragraph('🏦 Net Worth Composition', styles['Heading2']))
        nw_table_data = [['Type', 'Amount (₹)']]
        for asset, amount in net_worth_data.get('assets', {}).items():
            if amount > 0:
                nw_table_data.append([f"Asset: {asset}", f"{amount:,.0f}"])
        for liability, amount in net_worth_data.get('liabilities', {}).items():
            if amount > 0:
                nw_table_data.append([f"Liability: {liability}", f"{amount:,.0f}"])
        t4 = Table(nw_table_data, hAlign='LEFT')
        elems.append(t4)
        elems.append(Spacer(1,12))

    # SIP Projections
    if sip_data:
        elems.append(Paragraph('📈 SIP Investment Projections', styles['Heading2']))
        sip_table_data = [['Years', 'Monthly SIP (₹)', 'Total Invested (₹)', 'Future Value (₹)', 'Profit (₹)']]
        for projection in sip_data:
            sip_table_data.append([
                str(projection['years']),
                f"{projection['monthly_sip']:,.0f}",
                f"{projection['total_invested']:,.0f}",
                f"{projection['future_value']:,.0f}",
                f"{projection['profit']:,.0f}"
            ])
        t5 = Table(sip_table_data, hAlign='LEFT')
        elems.append(t5)
        elems.append(Spacer(1,12))

    # Investment Simulation
    if sim_data:
        elems.append(Paragraph('🎯 Investment Simulation Summary', styles['Heading2']))
        sim_kv = [
            ['Fund Selected', sim_data.get('fund_name','-')],
            ['Initial Investment', f"INR {sim_data.get('amount',0):,.0f}"],
            ['5Y Value (sim)', f"INR {sim_data.get('5Y_value',0):,.0f}"],
            ['5Y Gain (sim)', f"INR {sim_data.get('5Y_gain',0):,.0f}"],
            ['Return Rate', f"{sim_data.get('return_rate',0):.1f}%"]
        ]
        elems.append(Table(sim_kv))
        elems.append(Spacer(1,12))

    # Recommendations
    elems.append(Paragraph('💡 Actionable Recommendations', styles['Heading2']))
    for i, r in enumerate(recommendations, 1):
        elems.append(Paragraph(f"{i}. {r}", body))

    doc.build(elems)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# --- Simulated mutual fund data (cached) ---
@st.cache_data
def get_live_mutual_fund_data():
    data = {
        'Category': ['Large Cap', 'Large Cap', 'Mid Cap', 'Mid Cap', 'Small Cap', 'Small Cap', 'Flexi Cap', 'Flexi Cap', 'ELSS', 'ELSS', 'Debt', 'Debt', 'Index', 'Index'],
        'Fund Name': ['Axis Bluechip Fund', 'Mirae Asset Large Cap', 'Axis Midcap Fund', 'Kotak Emerging Equity', 'Axis Small Cap Fund', 'SBI Small Cap Fund', 'Parag Parikh Flexi Cap', 'PGIM India Flexi Cap', 'Mirae Asset Tax Saver', 'Canara Robeco Equity Tax Saver', 'ICICI Prudential Corporate Bond', 'HDFC Short Term Debt', 'UTI Nifty 50 Index Fund', 'HDFC Sensex Index Fund'],
        '1M Return': [1.2, 1.5, 2.5, 2.8, 4.1, 4.5, 2.1, 2.3, 1.8, 1.9, 0.6, 0.5, 1.1, 1.0],
        '6M Return': [6.5, 7.1, 12.3, 13.1, 18.2, 19.5, 10.5, 11.2, 9.8, 10.1, 3.5, 3.2, 6.8, 6.5],
        '1Y Return': [15.2, 16.1, 25.6, 27.2, 35.8, 38.2, 22.1, 24.5, 20.3, 21.1, 7.1, 6.8, 15.5, 15.1],
        '3Y CAGR': [14.5, 15.2, 22.1, 23.5, 28.9, 30.1, 19.8, 21.2, 18.5, 19.2, 6.5, 6.2, 14.8, 14.5],
        '5Y CAGR': [16.1, 17.2, 20.5, 21.8, 25.4, 26.8, 18.9, 20.1, 17.2, 18.1, 7.5, 7.2, 15.1, 14.8],
        'Risk': ['Moderately High', 'Moderately High', 'High', 'High', 'Very High', 'Very High', 'Very High', 'Very High', 'High', 'High', 'Low to Moderate', 'Low to Moderate', 'Moderately High', 'Moderately High'],
        'Rating': [5, 5, 5, 4, 5, 4, 5, 4, 5, 4, 4, 3, 5, 4]
    }
    return pd.DataFrame(data)

# --- App state load ---
if 'user_data' not in st.session_state:
    st.session_state.user_data = load_json(SNAPSHOT_FILE, {})
if 'goals' not in st.session_state:
    st.session_state.goals = load_json(GOALS_FILE, [])
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = load_json(PORTFOLIO_FILE, [])

# --- Main App UI with Top Navigation Menu ---
st.title('🤖 AI Financial Advisor')
st.markdown("""
<div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 15px; color: white; margin-bottom: 2rem;'>
    <h2 style='color: white; margin: 0;'>Your Personal Financial Companion</h2>
    <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Smart Planning • Wealth Growth • Financial Freedom</p>
</div>
""", unsafe_allow_html=True)

# Top Navigation Menu
st.markdown("---")
nav_options = [
    "📊 Snapshot", 
    "📈 Dashboard", 
    "💹 Investment Center", 
    "🎯 Goals Planner", 
    "📊 Risk Quiz", 
    "💼 Portfolio", 
    "📥 Export / Download", 
    "👨‍💻 About / Developer"
]

# Create navigation buttons
cols = st.columns(len(nav_options))
for i, option in enumerate(nav_options):
    with cols[i]:
        if st.button(option, key=f"nav_{i}", use_container_width=True):
            st.session_state.current_page = option

# Set current page if not set
if 'current_page' not in st.session_state:
    st.session_state.current_page = "📊 Snapshot"

# --- Snapshot Page ---
if st.session_state.current_page == "📊 Snapshot":
    st.header('📊 Financial Snapshot')
    st.markdown("""
    <div class='financial-sticker'>
        <div class='emoji-container'>📝</div>
        <h3>Let's Build Your Financial Profile!</h3>
        <p>Complete this form to get personalized financial insights and recommendations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form('snapshot_form'):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 💰 Income & Savings")
            monthly_income = st.number_input('Monthly Take-Home Income (₹)', min_value=0.0, 
                                           value=float(st.session_state.user_data.get('monthly_income', 75000.0)), 
                                           step=1000.0)
            current_savings = st.number_input('Current Savings / Emergency Fund (₹)', min_value=0.0, 
                                            value=float(st.session_state.user_data.get('current_savings', 50000.0)), 
                                            step=1000.0)
            investment_percentage = st.slider('% of Income to Invest', 0, 100, 
                                            int(st.session_state.user_data.get('investment_percentage', 20)))
            
        with c2:
            st.markdown("### 💸 Monthly Expenses")
            defaults = st.session_state.user_data.get('expenses', {})
            rent_emi = st.number_input('🏠 Rent/EMI', 0.0, value=float(defaults.get('Rent/EMI',20000.0)), step=500.0)
            groceries = st.number_input('🛒 Groceries', 0.0, value=float(defaults.get('Groceries',8000.0)), step=200.0)
            utilities = st.number_input('⚡ Utilities (Electricity, Water)', 0.0, value=float(defaults.get('Utilities',3000.0)), step=100.0)
            transportation = st.number_input('🚗 Transportation', 0.0, value=float(defaults.get('Transportation',4000.0)), step=100.0)
            insurance = st.number_input('🛡️ Insurance Premiums', 0.0, value=float(defaults.get('Insurance',2000.0)), step=100.0)
            loan_repayments = st.number_input('📄 Other Loan Repayments', 0.0, value=float(defaults.get('Other Loans',5000.0)), step=500.0)
            dining_entertainment = st.number_input('🍽️ Dining & Entertainment', 0.0, value=float(defaults.get('Dining & Entertainment',6000.0)), step=200.0)
            shopping = st.number_input('🛍️ Shopping', 0.0, value=float(defaults.get('Shopping',5000.0)), step=200.0)
            internet_phone = st.number_input('📱 Internet & Phone', 0.0, value=float(defaults.get('Internet/Phone',1000.0)), step=50.0)
            miscellaneous = st.number_input('📦 Miscellaneous', 0.0, value=float(defaults.get('Miscellaneous',2000.0)), step=100.0)

        st.markdown('---')
        st.markdown("### 🏦 Assets & Liabilities")
        assets_defaults = st.session_state.user_data.get('assets', {})
        liab_defaults = st.session_state.user_data.get('liabilities', {})
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 💎 Assets")
            asset_cash = st.number_input('💵 Cash & Bank Balances', 0.0, value=float(assets_defaults.get('Cash',50000.0)), step=1000.0)
            asset_stocks = st.number_input('📈 Stocks / Mutual Funds (Market Value)', 0.0, value=float(assets_defaults.get('Stocks/MF',100000.0)), step=1000.0)
            asset_property = st.number_input('🏠 Property Value (approx)', 0.0, value=float(assets_defaults.get('Property',0.0)), step=10000.0)
        with col2:
            st.markdown("#### 📄 Liabilities")
            liability_loans = st.number_input('🏦 Outstanding Loans (Home/Personal)', 0.0, value=float(liab_defaults.get('Outstanding Loans',0.0)), step=1000.0)

        save_snapshot = st.form_submit_button('💾 Save Financial Snapshot')

    if save_snapshot:
        user_data = {
            'monthly_income': monthly_income,
            'current_savings': current_savings,
            'investment_percentage': investment_percentage,
            'expenses': {
                'Rent/EMI': rent_emi,
                'Other Loans': loan_repayments,
                'Utilities': utilities,
                'Internet/Phone': internet_phone,
                'Insurance': insurance,
                'Groceries': groceries,
                'Transportation': transportation,
                'Dining & Entertainment': dining_entertainment,
                'Shopping': shopping,
                'Miscellaneous': miscellaneous
            },
            'assets': {
                'Cash': asset_cash,
                'Stocks/MF': asset_stocks,
                'Property': asset_property
            },
            'liabilities': {
                'Outstanding Loans': liability_loans
            }
        }
        st.session_state.user_data = user_data
        save_json(SNAPSHOT_FILE, user_data)
        st.success('✅ Financial Snapshot saved successfully!')
        st.balloons()

# --- Dashboard Page ---
elif st.session_state.current_page == "📈 Dashboard":
    if not st.session_state.user_data:
        st.warning("🚨 No financial snapshot found. Please create one in 'Snapshot' first!")
        st.markdown("""
        <div class='financial-sticker'>
            <div class='emoji-container'>📊</div>
            <h3>Get Started with Your Financial Journey!</h3>
            <p>Create your financial snapshot to unlock personalized insights and recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        user_data = st.session_state.user_data
        analyzer = FinancialAnalyzer(user_data)
        metrics = analyzer.calculate_financial_metrics()
        advanced = analyzer.calculate_advanced_metrics(metrics)
        risk_profile = st.session_state.get('risk_profile', 'Balanced')
        recs = analyzer.generate_recommendations(metrics, advanced, risk_profile)
        health_score = min(100, max(0, int((1 - advanced['dti_ratio']/100) * 30 + metrics['savings_rate'] * 2 + (advanced['emergency_fund_coverage']/6)*20)))

        # Top Metrics with Stickers
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='emoji-container'>💰</div>
                <h3 style='text-align: center;'>Monthly Income</h3>
                <h2 style='text-align: center; color: #059669;'>{format_inr(user_data['monthly_income'])}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='emoji-container'>📊</div>
                <h3 style='text-align: center;'>Savings Rate</h3>
                <h2 style='text-align: center; color: #dc2626;'>{metrics['savings_rate']:.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='emoji-container'>🛡️</div>
                <h3 style='text-align: center;'>Health Score</h3>
                <h2 style='text-align: center; color: #2563eb;'>{health_score}/100</h2>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='emoji-container'>🏦</div>
                <h3 style='text-align: center;'>Net Worth</h3>
                <h2 style='text-align: center; color: #7c3aed;'>{format_inr(advanced['net_worth'])}</h2>
            </div>
            """, unsafe_allow_html=True)

        # Financial Health Section
        st.markdown("### 📈 Financial Health Dashboard")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=health_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Financial Health Score"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 40], 'color': "lightcoral"},
                        {'range': [40, 70], 'color': "lightyellow"},
                        {'range': [70, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Key Metrics
            st.markdown("### 📋 Key Metrics")
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric("Emergency Fund Coverage", f"{advanced['emergency_fund_coverage']:.1f} months", 
                         delta=f"Target: 6 months", delta_color="off")
                st.metric("Debt-to-Income Ratio", f"{advanced['dti_ratio']:.1f}%")
            with metric_col2:
                st.metric("Monthly Savings", format_inr(metrics['monthly_savings']))
                st.metric("Investment Target", f"{user_data.get('investment_percentage', 0)}% of income")

        # Expense Breakdown
        st.markdown("### 💸 Expense Analysis")
        expense_df = pd.DataFrame(list(user_data['expenses'].items()), columns=['Category','Amount']).query('Amount>0').sort_values('Amount', ascending=False)
        fig_t = px.treemap(expense_df, path=['Category'], values='Amount', 
                          title='Spending Distribution by Category',
                          color='Amount', color_continuous_scale='Blues')
        st.plotly_chart(fig_t, use_container_width=True)

        # Recommendations with Stickers
        st.markdown("### 💡 Personalized Recommendations")
        for i, r in enumerate(recs[:6]):
            st.markdown(f"""
            <div class='financial-sticker'>
                <div style='display: flex; align-items: center; gap: 10px;'>
                    <span style='font-size: 1.5em;'>{r.split(' ')[0]}</span>
                    <span>{' '.join(r.split(' ')[1:])}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- Investment Center Page ---
elif st.session_state.current_page == "💹 Investment Center":
    st.header('💹 Investment Center')
    st.markdown("""
    <div class='financial-sticker'>
        <div class='emoji-container'>📈</div>
        <h3>Smart Investing Made Simple</h3>
        <p>Explore mutual funds, simulate growth, and plan your SIP investments.</p>
    </div>
    """, unsafe_allow_html=True)
    
    mf_df = get_live_mutual_fund_data()
    
    # Two main sections: Lump Sum and SIP
    tab1, tab2 = st.tabs(["💰 Lump Sum Investment", "📅 SIP Calculator"])
    
    with tab1:
        st.subheader("Lump Sum Investment Simulation")
        c1, c2 = st.columns([1,2])
        with c1:
            category = st.selectbox('Fund Category', mf_df['Category'].unique(), key='lumpsum_category')
            funds_filtered = mf_df[mf_df['Category']==category]
            fund_name = st.selectbox('Select Fund', funds_filtered['Fund Name'], key='lumpsum_fund')
            invest_amt = st.number_input('Investment Amount (₹)', min_value=1000.0, value=50000.0, step=1000.0, key='lumpsum_amt')
            selected = mf_df[mf_df['Fund Name']==fund_name].iloc[0]
            st.write('🎯 Risk:', selected['Risk'])
            st.write('⭐ Rating:', '★'*int(selected['Rating']))
            
        with c2:
            st.subheader(f"Simulated Growth for {format_inr(invest_amt)} in {fund_name}")
            periods = ['1M','6M','1Y','3Y','5Y']
            returns = [selected['1M Return'], selected['6M Return'], selected['1Y Return'], selected['3Y CAGR'], selected['5Y CAGR']]
            vals = [fund_projection_amount(invest_amt, p, r) for p,r in zip(periods, returns)]
            gains = [v - invest_amt for v in vals]
            
            st.session_state.investment_simulation = {
                'fund_name': fund_name, 
                'amount': invest_amt, 
                '5Y_value': vals[-1], 
                '5Y_gain': gains[-1],
                'return_rate': selected['5Y CAGR']
            }
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Investment', x=periods, y=[invest_amt]*len(periods), marker_color='#94a3b8'))
            fig.add_trace(go.Bar(name='Profit', x=periods, y=gains, marker_color='#10b981'))
            fig.update_layout(barmode='stack', title='Investment vs Profit', showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed returns
            returns_df = pd.DataFrame({
                'Period': periods,
                'Return %': returns,
                'Future Value': [format_inr(v) for v in vals],
                'Profit': [format_inr(g) for g in gains]
            })
            st.dataframe(returns_df, use_container_width=True)

    with tab2:
        st.subheader("SIP (Systematic Investment Plan) Calculator")
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_sip = st.number_input('Monthly SIP Amount (₹)', min_value=500.0, value=5000.0, step=500.0)
            sip_years = st.slider('Investment Period (Years)', 1, 30, 10)
            expected_return = st.slider('Expected Annual Return (%)', 5, 25, 12)
            
        with col2:
            # Calculate SIP projection
            future_value, total_invested = investment_projection_calculator(monthly_sip, sip_years, expected_return)
            profit = future_value - total_invested
            
            st.markdown(f"""
            <div class='metric-card'>
                <h3>📊 SIP Projection</h3>
                <p><strong>Monthly SIP:</strong> {format_inr(monthly_sip)}</p>
                <p><strong>Total Invested:</strong> {format_inr(total_invested)}</p>
                <p><strong>Future Value:</strong> {format_inr(future_value)}</p>
                <p><strong>Estimated Profit:</strong> {format_inr(profit)}</p>
                <p><strong>Return:</strong> {(profit/total_invested)*100:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Store SIP data for PDF export
            st.session_state.sip_data = [{
                'years': sip_years,
                'monthly_sip': monthly_sip,
                'total_invested': total_invested,
                'future_value': future_value,
                'profit': profit
            }]

    st.markdown('---')
    st.subheader('Compare Funds (Top 5 in chosen category)')
    top = funds_filtered.sort_values('5Y CAGR', ascending=False).head(5)
    st.dataframe(top[['Fund Name','5Y CAGR','3Y CAGR','1Y Return','Risk','Rating']])

# --- Goals Planner Page ---
elif st.session_state.current_page == "🎯 Goals Planner":
    st.header('🎯 Goals & SIP Planner')
    if 'goals' not in st.session_state:
        st.session_state.goals = []

    with st.form('goal_add'):
        g_name = st.text_input('Goal Name')
        g_amount = st.number_input('Target Amount (₹)', min_value=0.0, value=500000.0, step=1000.0)
        g_years = st.number_input('Years to Achieve', min_value=1, value=5)
        g_return = st.slider('Expected Annual Return (%)', 0, 20, 8)
        add = st.form_submit_button('➕ Add Goal')
        
    if add and g_name:
        st.session_state.goals.append({'name':g_name,'amount':g_amount,'years':g_years,'return':g_return})
        save_json(GOALS_FILE, st.session_state.goals)
        st.success('🎯 Goal added successfully!')

    if st.session_state.goals:
        st.markdown("### 📋 Your Financial Goals")
        df = pd.DataFrame(st.session_state.goals)
        st.dataframe(df, use_container_width=True)
        
        st.markdown('### 💰 Required Monthly SIP per Goal')
        goals_data = []
        for g in st.session_state.goals:
            r = g['return']/100/12
            n = g['years']*12
            target = g['amount']
            if r>0:
                sip = target * (r / ((1+r)**n - 1))
            else:
                sip = target / n
                
            goals_data.append({
                'Goal': g['name'],
                'Target': format_inr(target),
                'Years': g['years'],
                'Monthly SIP': format_inr(sip)
            })
            
            st.markdown(f"""
            <div class='financial-sticker'>
                <h4>🎯 {g['name']}</h4>
                <p>Target: {format_inr(target)} in {g['years']} years</p>
                <p><strong>Required SIP: {format_inr(sip)} / month</strong></p>
            </div>
            """, unsafe_allow_html=True)

# --- Risk Quiz Page ---
elif st.session_state.current_page == "📊 Risk Quiz":
    st.header('📊 Risk Profile Assessment')
    st.markdown("""
    <div class='financial-sticker'>
        <div class='emoji-container'>🎯</div>
        <h3>Discover Your Investment Personality</h3>
        <p>Answer these simple questions to understand your risk tolerance and get personalized investment advice.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form('risk_quiz'):
        st.subheader("Question 1: Market Reaction")
        q1 = st.radio('If the market falls 20% in a year, you would:', 
                      ['Sell most investments', 'Wait and review', 'Buy more at lower prices'])
        
        st.subheader("Question 2: Investment Horizon")
        q2 = st.radio('Your investment horizon is:', 
                      ['Short-term (<3 years)', 'Medium-term (3-7 years)', 'Long-term (>7 years)'])
        
        st.subheader("Question 3: Primary Goal")
        q3 = st.radio('Your primary investment goal is:', 
                      ['Capital preservation and safety', 'Balanced growth with some risk', 'Maximum growth (accept higher risk)'])
        
        calculate = st.form_submit_button('🎯 Calculate My Risk Profile')
        
    if calculate:
        map_scores = {
            'Sell most investments': 0, 
            'Wait and review': 1, 
            'Buy more at lower prices': 2,
            'Short-term (<3 years)': 0,
            'Medium-term (3-7 years)': 1,
            'Long-term (>7 years)': 2,
            'Capital preservation and safety': 0,
            'Balanced growth with some risk': 1,
            'Maximum growth (accept higher risk)': 2
        }
        
        score = map_scores[q1] + map_scores[q2] + map_scores[q3]
        
        if score <= 3:
            profile = '🛡️ Conservative'
            description = "You prefer safety and stability over high returns. Focus on debt instruments and low-risk investments."
        elif score <= 5:
            profile = '⚖️ Balanced'
            description = "You seek a balance between growth and safety. A mix of equity and debt funds would suit you."
        else:
            profile = '🚀 Aggressive'
            description = "You're comfortable with risk and seek high returns. Equity-heavy portfolios align with your goals."
            
        st.session_state.risk_profile = profile
        st.session_state.risk_score = score
        
        st.markdown(f"""
        <div class='metric-card' style='text-align: center;'>
            <h2>{profile}</h2>
            <p>{description}</p>
            <p><strong>Your Risk Score: {score}/6</strong></p>
        </div>
        """, unsafe_allow_html=True)

# --- Portfolio Page ---
elif st.session_state.current_page == "💼 Portfolio":
    st.header('💼 Portfolio Manager')
    st.markdown("""
    <div class='financial-sticker'>
        <div class='emoji-container'>📊</div>
        <h3>Track Your Investments</h3>
        <p>Add your current holdings and visualize your portfolio allocation.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form('portfolio_form'):
        cols = st.columns(3)
        name = cols[0].text_input('Holding Name')
        amt = cols[1].number_input('Amount (₹)', min_value=0.0, value=0.0, step=1000.0)
        add = cols[2].form_submit_button('➕ Add Holding')
        
        if add and name and amt>0:
            st.session_state.portfolio.append({'name':name,'amount':amt})
            save_json(PORTFOLIO_FILE, st.session_state.portfolio)
            st.success('✅ Holding added successfully!')

    if st.session_state.portfolio:
        pfdf = pd.DataFrame(st.session_state.portfolio)
        pfdf['pct'] = pfdf['amount'] / pfdf['amount'].sum() * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader('Portfolio Holdings')
            st.dataframe(pfdf, use_container_width=True)
            
        with col2:
            st.subheader('Portfolio Allocation')
            fig = px.pie(pfdf, names='name', values='amount', title='Investment Allocation')
            st.plotly_chart(fig, use_container_width=True)

        # Download option
        csv = pfdf.to_csv(index=False).encode('utf-8')
        st.download_button('📥 Download Portfolio CSV', csv, 'portfolio.csv', 'text/csv')

# --- Export / Download Page ---
elif st.session_state.current_page == "📥 Export / Download":
    st.header('📥 Export Reports & Data')
    
    if not st.session_state.user_data:
        st.info('📊 No financial data found. Please create a snapshot first.')
    else:
        analyzer = FinancialAnalyzer(st.session_state.user_data)
        metrics = analyzer.calculate_financial_metrics()
        advanced = analyzer.calculate_advanced_metrics(metrics)
        recs = analyzer.generate_recommendations(metrics, advanced, st.session_state.get('risk_profile','Balanced'))
        health_score = min(100, max(0, int((1 - advanced['dti_ratio']/100) * 30 + metrics['savings_rate'] * 2 + (advanced['emergency_fund_coverage']/6)*20)))
        sim = st.session_state.get('investment_simulation', {})
        sip_data = st.session_state.get('sip_data', [])

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📄 Report Options")
            if st.button('📊 Download Comprehensive PDF Report'):
                pdf_bytes = create_pdf_report_reportlab(
                    metrics, advanced, recs, health_score, 
                    st.session_state.user_data, sim,
                    st.session_state.user_data.get('expenses', {}),
                    {
                        'assets': st.session_state.user_data.get('assets', {}),
                        'liabilities': st.session_state.user_data.get('liabilities', {})
                    },
                    sip_data
                )
                st.download_button(
                    '📥 Download PDF Report', 
                    pdf_bytes, 
                    f'Financial_Report_{datetime.now().strftime("%Y%m%d")}.pdf', 
                    'application/pdf'
                )

        with col2:
            st.markdown("### 💾 Data Export")
            if st.button('📁 Download Snapshot JSON'):
                snapshot_json = json.dumps(st.session_state.user_data, indent=2).encode('utf-8')
                st.download_button(
                    '📥 Download JSON', 
                    snapshot_json, 
                    'financial_snapshot.json', 
                    'application/json'
                )

# --- About / Developer Page ---
# ... (keep all previous code the same until the About / Developer page section)

# --- About / Developer Page ---
elif st.session_state.current_page == "👨‍💻 About / Developer":
    st.header('👨‍💻 About the Developer')
    
    # Developer Profile Section
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div style='text-align: center;'>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>👨‍💻</div>
            <h2>Ayush Shukla</h2>
            <p style='color: #64748b;'>Full Stack Developer & FinTech Enthusiast</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <h3>🚀 About Me</h3>
            <p>Building intelligent financial solutions to empower better money management and financial literacy for everyone.</p>
            <p>Passionate about creating tools that make complex financial concepts accessible and actionable.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Social Links - Using Streamlit buttons instead of HTML
    st.markdown("### 📱 Connect With Me")
    social_cols = st.columns(4)
    
    with social_cols[0]:
        if st.button("🐙 GitHub", use_container_width=True):
            st.markdown("[Visit GitHub Profile](https://github.com/ayushshukla)")
    with social_cols[1]:
        if st.button("💼 LinkedIn", use_container_width=True):
            st.markdown("[Visit LinkedIn Profile](https://linkedin.com/in/ayushshukla)")
    with social_cols[2]:
        if st.button("🐦 Twitter", use_container_width=True):
            st.markdown("[Visit Twitter Profile](https://twitter.com/ayushshukla)")
    with social_cols[3]:
        if st.button("🌐 Portfolio", use_container_width=True):
            st.markdown("[Visit Portfolio](https://ayushshukla.xyz)")
    
    st.markdown("---")
    
    # App Information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <h3>📊 About This App</h3>
            <p><strong>AI Financial Advisor</strong> is a comprehensive personal finance management tool that helps you:</p>
            <ul>
                <li>📈 Track income and expenses</li>
                <li>💰 Plan investments and SIPs</li>
                <li>🎯 Set and achieve financial goals</li>
                <li>🛡️ Understand your risk profile</li>
                <li>📄 Generate detailed financial reports</li>
                <li>🏦 Monitor net worth growth</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <h3>🛠️ Technology Stack</h3>
            <p>Built with modern technologies for optimal performance and user experience:</p>
            <ul>
                <li><strong>Frontend:</strong> Streamlit, Plotly</li>
                <li><strong>Backend:</strong> Python, Pandas, NumPy</li>
                <li><strong>Data Visualization:</strong> Plotly Express, Graph Objects</li>
                <li><strong>PDF Generation:</strong> ReportLab with Unicode support</li>
                <li><strong>Data Storage:</strong> Secure JSON file system</li>
                <li><strong>Styling:</strong> Custom CSS with gradients</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Features Grid
    st.markdown("### ✨ Key Features")
    feature_cols = st.columns(3)
    
    with feature_cols[0]:
        st.markdown("""
        <div class='financial-sticker'>
            <div style='font-size: 2rem;'>📊</div>
            <h4>Financial Snapshot</h4>
            <p>Complete financial profile with income, expenses, assets, and liabilities</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='financial-sticker'>
            <div style='font-size: 2rem;'>💹</div>
            <h4>Investment Center</h4>
            <p>Mutual fund analysis with lump sum and SIP calculators</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_cols[1]:
        st.markdown("""
        <div class='financial-sticker'>
            <div style='font-size: 2rem;'>🎯</div>
            <h4>Goals Planning</h4>
            <p>Set financial goals and calculate required SIP amounts</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='financial-sticker'>
            <div style='font-size: 2rem;'>📈</div>
            <h4>Risk Assessment</h4>
            <p>Personalized risk profile quiz and investment recommendations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_cols[2]:
        st.markdown("""
        <div class='financial-sticker'>
            <div style='font-size: 2rem;'>💼</div>
            <h4>Portfolio Manager</h4>
            <p>Track and visualize your investment portfolio allocation</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='financial-sticker'>
            <div style='font-size: 2rem;'>📥</div>
            <h4>Export Reports</h4>
            <p>Generate comprehensive PDF reports with all your financial data</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Contact Information
    st.markdown("---")
    st.markdown("""
    <div class='metric-card' style='text-align: center;'>
        <h3>📞 Get In Touch</h3>
        <p>Have questions, suggestions, or want to collaborate on financial technology projects?</p>
        <p>I'd love to hear from you!</p>
        <p>📧 <strong>Email:</strong> ayush.shukla@example.com</p>
        <p>💼 <strong>LinkedIn:</strong> linkedin.com/in/ayushshukla</p>
        <p>🐙 <strong>GitHub:</strong> github.com/ayushshukla</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mission Statement
    st.markdown("""
    <div class='financial-sticker' style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;'>
        <h3 style='color: white;'>🎯 My Mission</h3>
        <p style='color: white;'>To democratize financial knowledge and empower individuals with tools that make 
        personal finance management accessible, understandable, and actionable for everyone.</p>
    </div>
    """, unsafe_allow_html=True)

# ... (keep the rest of the code the same)
