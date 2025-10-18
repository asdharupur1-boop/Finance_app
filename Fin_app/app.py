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
warnings.filterwarnings('ignore')

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

.ml-insight {
    background: linear-gradient(135deg, #fef3c7 0%, #f59e0b 100%);
    border: 2px solid #f59e0b;
    border-radius: 12px;
    padding: 15px;
    margin: 10px 0;
}

.ai-prediction {
    background: linear-gradient(135deg, #dbeafe 0%, #3b82f6 100%);
    color: white;
    border-radius: 12px;
    padding: 15px;
    margin: 10px 0;
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

# --- ML Financial Predictor Class (No external dependencies) ---
class MLFinancialPredictor:
    def __init__(self):
        pass
    
    def predict_risk_tolerance(self, user_data):
        """ML model to predict risk tolerance based on user profile"""
        # Features: age, income, expenses, savings, debt, investment experience
        age = user_data.get('age', 30)
        monthly_income = user_data.get('monthly_income', 50000)
        current_savings = user_data.get('current_savings', 100000)
        total_expenses = sum(user_data.get('expenses', {}).values())
        total_debt = sum(user_data.get('liabilities', {}).values())
        investment_experience = user_data.get('investment_experience', 2)  # 1-5 scale
        
        # ML-based risk score calculation
        risk_score = (
            (monthly_income / 10000) * 0.3 +
            (current_savings / 50000) * 0.25 -
            (total_debt / 10000) * 0.2 +
            (investment_experience * 2) * 0.15 +
            (min(age, 60) / 30) * 0.1
        )
        
        if risk_score < 3:
            return "Conservative", 0.3, risk_score
        elif risk_score < 7:
            return "Balanced", 0.5, risk_score
        else:
            return "Aggressive", 0.7, risk_score
    
    def predict_goal_success_probability(self, goal, user_finances):
        """Predict probability of achieving financial goal using ML patterns"""
        monthly_savings = user_finances.get('monthly_savings', 0)
        goal_amount = goal['amount']
        timeline = goal['years']
        expected_return = goal.get('return', 8)
        
        required_monthly = goal_amount / (timeline * 12)
        savings_ratio = monthly_savings / required_monthly if required_monthly > 0 else 0
        
        # ML probability calculation with multiple factors
        base_probability = min(savings_ratio * 0.8, 0.95)  # Base on savings ratio
        timeline_factor = min(timeline / 10, 1.0)  # Longer timelines have higher success
        return_factor = min(expected_return / 15, 1.0)  # Reasonable returns help
        
        final_probability = (base_probability * 0.6 + timeline_factor * 0.3 + return_factor * 0.1)
        
        if final_probability >= 0.8:
            confidence = "High confidence"
        elif final_probability >= 0.6:
            confidence = "Moderate confidence"
        elif final_probability >= 0.4:
            confidence = "Low confidence"
        else:
            confidence = "Very low confidence"
            
        return final_probability, confidence
    
    def get_ml_recommendations(self, user_data, metrics):
        """Generate ML-powered personalized recommendations"""
        recommendations = []
        
        # Analyze spending patterns
        expenses = user_data.get('expenses', {})
        total_expenses = sum(expenses.values())
        
        # ML pattern: High dining expenses
        dining_ratio = expenses.get('Dining & Entertainment', 0) / total_expenses if total_expenses > 0 else 0
        if dining_ratio > 0.15:
            savings_potential = int(expenses.get('Dining & Entertainment', 0) * 0.3)
            recommendations.append(f"🤖 ML Insight: Your dining expenses are {dining_ratio*100:.1f}% of total spending. Consider meal planning to save ₹{savings_potential} monthly.")
        
        # ML pattern: Low emergency fund
        emergency_ratio = user_data.get('current_savings', 0) / metrics['total_expenses'] if metrics['total_expenses'] > 0 else 0
        if emergency_ratio < 3:
            recommendations.append(f"🤖 ML Insight: Emergency fund covers only {emergency_ratio:.1f} months. Target 6 months for better security.")
        
        # ML pattern: High debt-to-income
        if metrics.get('dti_ratio', 0) > 35:
            recommendations.append("🤖 ML Insight: Your debt-to-income ratio is high. Focus on debt reduction before new investments.")
        
        # ML pattern: Investment allocation
        investment_pct = user_data.get('investment_percentage', 0)
        if investment_pct < 15:
            recommendations.append(f"🤖 ML Insight: You're investing only {investment_pct}% of income. Consider increasing to 20% for better wealth accumulation.")
        
        return recommendations
    
    def cluster_user_profile(self, user_data, metrics):
        """Cluster user into financial personality types"""
        savings_rate = metrics.get('savings_rate', 0)
        dti_ratio = metrics.get('dti_ratio', 0)
        
        if savings_rate > 20 and dti_ratio < 20:
            return "Wealth Builder", "You're on an excellent path to financial freedom!"
        elif savings_rate > 10 and dti_ratio < 35:
            return "Balanced Saver", "Good financial habits with room for optimization"
        else:
            return "Needs Attention", "Focus on reducing debt and increasing savings"

# --- Stock Prediction ML (Simulated without external dependencies) ---
class StockPredictor:
    def __init__(self):
        pass
    
    def get_simulated_stock_data(self, symbol):
        """Generate simulated stock data"""
        # Simulate stock prices with some randomness
        np.random.seed(hash(symbol) % 1000)  # Consistent randomness per symbol
        
        dates = pd.date_range(end=datetime.now(), periods=180, freq='D')
        base_price = {
            'RELIANCE.NS': 2500,
            'TCS.NS': 3500,
            'INFY.NS': 1600,
            'HDFCBANK.NS': 1500,
            'ICICIBANK.NS': 900
        }.get(symbol, 1000)
        
        returns = np.random.normal(0.0005, 0.02, len(dates))
        prices = base_price * (1 + returns).cumprod()
        
        data = pd.DataFrame({
            'Close': prices,
            'Date': dates
        }).set_index('Date')
        
        return data
    
    def predict_stock_trend(self, symbol):
        """Simple ML-based trend prediction using simulated data"""
        try:
            data = self.get_simulated_stock_data(symbol)
            if data is None or data.empty:
                return "No data", 0, 0
            
            # Calculate simple moving averages
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            data['SMA_50'] = data['Close'].rolling(window=50).mean()
            
            current_price = data['Close'].iloc[-1]
            sma_20 = data['SMA_20'].iloc[-1]
            sma_50 = data['SMA_50'].iloc[-1]
            
            # ML-like trend analysis
            if current_price > sma_20 > sma_50:
                trend = "Bullish"
                confidence = 0.75 + np.random.random() * 0.1
            elif current_price < sma_20 < sma_50:
                trend = "Bearish"
                confidence = 0.70 + np.random.random() * 0.1
            else:
                trend = "Neutral"
                confidence = 0.55 + np.random.random() * 0.1
                
            return trend, confidence, current_price
            
        except Exception as e:
            return "Error", 0, 0

# --- Core logic classes ---
class FinancialAnalyzer:
    def __init__(self, user_data):
        self.user_data = user_data or {}
        self.monthly_income = float(self.user_data.get('monthly_income', 0) or 0)
        self.expenses = {k: float(v or 0) for k, v in self.user_data.get('expenses', {}).items()}
        self.investment_pct = float(self.user_data.get('investment_percentage', 0) or 0)
        self.current_savings = float(self.user_data.get('current_savings', 0) or 0)
        self.assets = {k: float(v or 0) for k, v in self.user_data.get('assets', {}).items()}
        self.liabilities = {k: float(v or 0) for k, v in self.user_data.get('liabilities', {}).items()}
        self.ml_predictor = MLFinancialPredictor()
        self.stock_predictor = StockPredictor()

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
        
        # Get ML predictions
        risk_profile, risk_score, ml_risk_score = self.ml_predictor.predict_risk_tolerance(self.user_data)
        user_cluster, cluster_message = self.ml_predictor.cluster_user_profile(self.user_data, metrics)
        ml_recommendations = self.ml_predictor.get_ml_recommendations(self.user_data, metrics)
        
        return {
            'dti_ratio': dti_ratio,
            'emergency_fund_target': metrics['total_expenses'] * 6,
            'emergency_fund_coverage': emergency_fund_coverage,
            'fire_number': fire_number,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'net_worth': net_worth,
            'ml_risk_profile': risk_profile,
            'ml_risk_score': ml_risk_score,
            'user_cluster': user_cluster,
            'cluster_message': cluster_message,
            'ml_recommendations': ml_recommendations
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
        
        # Add ML-based recommendations
        recs.extend(advanced_metrics.get('ml_recommendations', []))
        
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

    # ML Insights
    elems.append(Paragraph('🤖 ML Insights', styles['Heading2']))
    ml_data = [
        ['Risk Profile', advanced_metrics.get('ml_risk_profile', 'Unknown')],
        ['User Cluster', advanced_metrics.get('user_cluster', 'Unknown')],
        ['ML Risk Score', f"{advanced_metrics.get('ml_risk_score', 0):.1f}"]
    ]
    t_ml = Table(ml_data, hAlign='LEFT')
    elems.append(t_ml)
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
    "🤖 AI Insights",
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
            
            # Additional ML-relevant fields
            st.markdown("### 🤖 ML Profile Data")
            age = st.number_input('Your Age', min_value=18, max_value=80, 
                                value=st.session_state.user_data.get('age', 30))
            investment_experience = st.slider('Investment Experience (1-5)', 1, 5, 
                                            st.session_state.user_data.get('investment_experience', 2),
                                            help="1: Beginner, 5: Expert")
            
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
            'age': age,
            'investment_experience': investment_experience,
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

        # ML Insights Section
        st.markdown("### 🤖 AI-Powered Insights")
        ml_col1, ml_col2 = st.columns(2)
        
        with ml_col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='emoji-container'>🎯</div>
                <h3 style='text-align: center;'>ML Risk Profile</h3>
                <h2 style='text-align: center; color: #7c3aed;'>{advanced.get('ml_risk_profile', 'Unknown')}</h2>
                <p style='text-align: center; color: #64748b;'>Based on your financial behavior</p>
            </div>
            """, unsafe_allow_html=True)
        
        with ml_col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='emoji-container'>👤</div>
                <h3 style='text-align: center;'>Financial Personality</h3>
                <h2 style='text-align: center; color: #059669;'>{advanced.get('user_cluster', 'Unknown')}</h2>
                <p style='text-align: center; color: #64748b;'>{advanced.get('cluster_message', '')}</p>
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
                st.metric("ML Risk Score", f"{advanced.get('ml_risk_score', 0):.1f}")

        # Expense Breakdown
        st.markdown("### 💸 Expense Analysis")
        expense_df = pd.DataFrame(list(user_data['expenses'].items()), columns=['Category','Amount']).query('Amount>0').sort_values('Amount', ascending=False)
        fig_t = px.treemap(expense_df, path=['Category'], values='Amount', 
                          title='Spending Distribution by Category',
                          color='Amount', color_continuous_scale='Blues')
        st.plotly_chart(fig_t, use_container_width=True)

        # Recommendations with Stickers
        st.markdown("### 💡 Personalized Recommendations")
        for i, r in enumerate(recs[:8]):
            if r.startswith('🤖 ML Insight'):
                st.markdown(f"""
                <div class='ml-insight'>
                    <div style='display: flex; align-items: center; gap: 10px;'>
                        <span style='font-size: 1.5em;'>🤖</span>
                        <span>{r.replace('🤖 ML Insight: ', '')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='financial-sticker'>
                    <div style='display: flex; align-items: center; gap: 10px;'>
                        <span style='font-size: 1.5em;'>{r.split(' ')[0]}</span>
                        <span>{' '.join(r.split(' ')[1:])}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- AI Insights Page (NEW) ---
elif st.session_state.current_page == "🤖 AI Insights":
    st.header('🤖 AI-Powered Financial Insights')
    
    if not st.session_state.user_data:
        st.warning("🚨 No financial snapshot found. Please create one in 'Snapshot' first!")
    else:
        user_data = st.session_state.user_data
        analyzer = FinancialAnalyzer(user_data)
        metrics = analyzer.calculate_financial_metrics()
        advanced = analyzer.calculate_advanced_metrics(metrics)
        ml_predictor = MLFinancialPredictor()
        stock_predictor = StockPredictor()
        
        # ML Risk Analysis
        st.markdown("### 🎯 ML Risk Profile Analysis")
        risk_profile, risk_allocation, risk_score = ml_predictor.predict_risk_tolerance(user_data)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>🤖 Your AI-Determined Risk Profile</h3>
                <div style='text-align: center; margin: 1rem 0;'>
                    <div style='font-size: 3rem;'>🎯</div>
                    <h2 style='color: #7c3aed;'>{risk_profile}</h2>
                    <p>ML Risk Score: {risk_score:.1f}/10</p>
                </div>
                <p><strong>Recommended Asset Allocation:</strong></p>
                <ul>
                    <li>Equity: {risk_allocation*100:.0f}%</li>
                    <li>Debt: {(1-risk_allocation)*100:.0f}%</li>
                    <li>Gold: 5-10%</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Risk allocation pie chart
            allocation_data = {
                'Asset': ['Equity', 'Debt', 'Gold'],
                'Percentage': [risk_allocation*90, (1-risk_allocation)*90, 10]
            }
            fig = px.pie(allocation_data, values='Percentage', names='Asset', 
                        title='Recommended Portfolio Allocation',
                        color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)
        
        # Goal Success Predictions
        if st.session_state.goals:
            st.markdown("### 📊 Goal Success Probability (ML Predictions)")
            for goal in st.session_state.goals:
                probability, confidence = ml_predictor.predict_goal_success_probability(goal, metrics)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div style='padding: 1rem; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                                border-radius: 12px; margin: 0.5rem 0;'>
                        <h4>🎯 {goal['name']}</h4>
                        <p>Target: {format_inr(goal['amount'])} in {goal['years']} years</p>
                        <div style='background: #e2e8f0; border-radius: 10px; height: 20px; margin: 10px 0;'>
                            <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                                        width: {probability*100}%; height: 100%; border-radius: 10px; 
                                        text-align: center; color: white; font-weight: bold;'>
                                {probability*100:.1f}%
                            </div>
                        </div>
                        <p><strong>AI Confidence:</strong> {confidence}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if probability >= 0.7:
                        emoji = "🎉"
                        color = "#10b981"
                    elif probability >= 0.5:
                        emoji = "👍"
                        color = "#f59e0b"
                    else:
                        emoji = "⚠️"
                        color = "#ef4444"
                    
                    st.markdown(f"""
                    <div style='text-align: center; padding: 1rem; background: {color}; 
                                border-radius: 12px; color: white; margin: 0.5rem 0;'>
                        <div style='font-size: 2rem;'>{emoji}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Stock Predictions
        st.markdown("### 📈 AI Stock Trend Analysis")
        stock_symbols = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS']
        
        selected_stock = st.selectbox("Select Stock for Analysis", stock_symbols)
        
        if st.button("🔮 Analyze Stock Trend"):
            with st.spinner("🤖 AI is analyzing market trends..."):
                trend, confidence, current_price = stock_predictor.predict_stock_trend(selected_stock)
                
                if trend != "Error":
                    st.markdown(f"""
                    <div class='ai-prediction'>
                        <h3>🤖 AI Prediction for {selected_stock}</h3>
                        <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; text-align: center; margin: 1rem 0;'>
                            <div>
                                <h4>Current Price</h4>
                                <h2>₹{current_price:.2f}</h2>
                            </div>
                            <div>
                                <h4>Predicted Trend</h4>
                                <h2>{trend}</h2>
                            </div>
                            <div>
                                <h4>AI Confidence</h4>
                                <h2>{confidence*100:.1f}%</h2>
                            </div>
                        </div>
                        <p><strong>Disclaimer:</strong> AI predictions are for educational purposes only. Past performance doesn't guarantee future results.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Could not fetch stock data. Please try again later.")
        
        # Financial Behavior Insights
        st.markdown("### 🧠 ML Financial Behavior Analysis")
        ml_recommendations = ml_predictor.get_ml_recommendations(user_data, metrics)
        
        for rec in ml_recommendations:
            st.markdown(f"""
            <div class='ml-insight'>
                <div style='display: flex; align-items: start; gap: 10px;'>
                    <span style='font-size: 1.5em;'>🤖</span>
                    <div>
                        <strong>AI Insight</strong>
                        <p style='margin: 0;'>{rec.replace('🤖 ML Insight: ', '')}</p>
                    </div>
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
    
    # Privacy Notice
    st.markdown("""
    <div class='financial-sticker' style='background: linear-gradient(135deg, #fef3c7 0%, #f59e0b 100%);'>
        <div class='emoji-container'>🔒</div>
        <h3 style='color: #92400e;'>Your Goals are Private!</h3>
        <p style='color: #92400e;'>All your financial goals are stored locally and only visible to you.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'goals' not in st.session_state:
        st.session_state.goals = []

    # Add Goal Form with Enhanced UI
    with st.form('goal_add'):
        st.markdown("### 🎯 Add New Financial Goal")
        
        goal_cols = st.columns([2, 1, 1])
        with goal_cols[0]:
            g_name = st.text_input('Goal Name', placeholder='e.g., Dream House, Car, Vacation')
        with goal_cols[1]:
            g_amount = st.number_input('Target Amount (₹)', min_value=0.0, value=500000.0, step=1000.0)
        with goal_cols[2]:
            g_years = st.number_input('Years to Achieve', min_value=1, value=5)
        
        g_return = st.slider('Expected Annual Return (%)', 0, 20, 8, 
                           help='Conservative: 6-8%, Moderate: 8-12%, Aggressive: 12-15%+')
        
        add = st.form_submit_button('🚀 Add Goal')
        
    if add and g_name:
        new_goal = {
            'name': g_name,
            'amount': g_amount,
            'years': g_years,
            'return': g_return,
            'created_date': datetime.now().strftime('%Y-%m-%d')
        }
        st.session_state.goals.append(new_goal)
        save_json(GOALS_FILE, st.session_state.goals)
        st.success(f'🎯 Goal "{g_name}" added successfully!')
        st.balloons()

    if st.session_state.goals:
        # Goals Overview
        total_goals_value = sum(g['amount'] for g in st.session_state.goals)
        avg_years = np.mean([g['years'] for g in st.session_state.goals])
        
        st.markdown("### 📊 Goals Overview")
        overview_cols = st.columns(3)
        with overview_cols[0]:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='emoji-container'>🎯</div>
                <h3 style='text-align: center;'>Total Goals</h3>
                <h2 style='text-align: center; color: #7c3aed;'>{len(st.session_state.goals)}</h2>
            </div>
            """, unsafe_allow_html=True)
        with overview_cols[1]:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='emoji-container'>💰</div>
                <h3 style='text-align: center;'>Total Target</h3>
                <h2 style='text-align: center; color: #059669;'>{format_inr(total_goals_value)}</h2>
            </div>
            """, unsafe_allow_html=True)
        with overview_cols[2]:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='emoji-container'>📅</div>
                <h3 style='text-align: center;'>Avg Timeline</h3>
                <h2 style='text-align: center; color: #dc2626;'>{avg_years:.1f} years</h2>
            </div>
            """, unsafe_allow_html=True)

        # Goals List with Progress
        st.markdown("### 📋 Your Financial Goals")
        for i, goal in enumerate(st.session_state.goals):
            # Calculate required SIP
            r = goal['return']/100/12
            n = goal['years']*12
            target = goal['amount']
            if r > 0:
                sip = target * (r / ((1+r)**n - 1))
            else:
                sip = target / n
            
            total_investment = sip * n
            potential_growth = target - total_investment
            
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='padding: 1rem; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                                border-radius: 12px; border-left: 4px solid #0369a1; margin: 0.5rem 0;'>
                        <h4 style='margin: 0; color: #0c4a6e;'>🎯 {goal['name']}</h4>
                        <p style='margin: 0.25rem 0; color: #475569;'>
                            💰 Target: <strong>{format_inr(goal['amount'])}</strong> | 
                            📅 Timeline: <strong>{goal['years']} years</strong> | 
                            📈 Expected Return: <strong>{goal['return']}%</strong>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style='padding: 1rem; background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); 
                                border-radius: 12px; border-left: 4px solid #16a34a; margin: 0.5rem 0;'>
                        <p style='margin: 0; color: #166534; font-weight: 600;'>
                            💸 Monthly SIP: {format_inr(sip)}
                        </p>
                        <p style='margin: 0; color: #15803d; font-size: 0.9em;'>
                            Total Investment: {format_inr(total_investment)}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    if st.button('🗑️', key=f'delete_{i}', help='Delete this goal'):
                        st.session_state.goals.pop(i)
                        save_json(GOALS_FILE, st.session_state.goals)
                        st.rerun()

        # SIP Summary
        st.markdown("### 💰 SIP Investment Summary")
        
        # Calculate all required SIPs
        goal_sips = []
        for goal in st.session_state.goals:
            r = goal['return']/100/12
            n = goal['years']*12
            target = goal['amount']
            if r > 0:
                sip = target * (r / ((1+r)**n - 1))
            else:
                sip = target / n
            goal_sips.append(sip)
        
        total_monthly_sip = sum(goal_sips)
        
        summary_cols = st.columns(2)
        with summary_cols[0]:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='emoji-container'>💸</div>
                <h3 style='text-align: center;'>Total Monthly SIP</h3>
                <h2 style='text-align: center; color: #dc2626;'>{format_inr(total_monthly_sip)}</h2>
                <p style='text-align: center; color: #64748b;'>Required to achieve all goals</p>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_cols[1]:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='emoji-container'>📊</div>
                <h3 style='text-align: center;'>Annual Investment</h3>
                <h2 style='text-align: center; color: #059669;'>{format_inr(total_monthly_sip * 12)}</h2>
                <p style='text-align: center; color: #64748b;'>Yearly commitment needed</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Progress visualization
        st.markdown("### 📈 Goal Progress Visualization")
        goal_names = [g['name'] for g in st.session_state.goals]
        goal_amounts = [g['amount'] for g in st.session_state.goals]
        goal_sips = [sip for sip in goal_sips]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Target Amount', x=goal_names, y=goal_amounts, 
                            marker_color='#6366f1', text=[format_inr(amt) for amt in goal_amounts],
                            textposition='auto'))
        fig.add_trace(go.Bar(name='Monthly SIP', x=goal_names, y=goal_sips,
                            marker_color='#10b981', text=[format_inr(sip) for sip in goal_sips],
                            textposition='auto'))
        
        fig.update_layout(
            title='Goals vs Required Monthly SIPs',
            barmode='group',
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Clear all goals button
        if st.button('🗑️ Clear All Goals', type='secondary'):
            st.session_state.goals = []
            save_json(GOALS_FILE, [])
            st.rerun()
    
    else:
        # Empty state with encouragement
        st.markdown("""
        <div class='financial-sticker' style='text-align: center; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);'>
            <div class='emoji-container'>🎯</div>
            <h3 style='color: #0369a1;'>No Goals Set Yet!</h3>
            <p style='color: #475569;'>Start by adding your first financial goal above. 🚀</p>
            <p style='color: #64748b; font-size: 0.9em;'>
                Examples: Down payment for house, children's education, retirement corpus, dream vacation
            </p>
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
elif st.session_state.current_page == "👨‍💻 About / Developer":
    st.header('👨‍💻 About the Developer')
    
    # Enhanced Developer Profile with Better Visuals
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 20px; color: white; margin-bottom: 2rem;'>
        <div style='font-size: 4rem; margin-bottom: 1rem;'>👨‍💻</div>
        <h1 style='color: white; margin-bottom: 0.5rem;'>Ayush Shukla</h1>
        <p style='font-size: 1.2em; opacity: 0.9; margin-bottom: 0;'>Full Stack Developer & FinTech Enthusiast</p>
        <p style='opacity: 0.8;'>Building the future of financial technology</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Social Links
    st.markdown("### 📱 Connect With Me")
    social_cols = st.columns(4)
    
    with social_cols[0]:
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                    border-radius: 12px; color: white;'>
            <div style='font-size: 2rem;'>🐙</div>
            <p><strong>GitHub</strong></p>
            <p style='font-size: 0.8em;'>ayushshukla</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button('Visit GitHub', key='github_btn', use_container_width=True):
            st.markdown("[Open GitHub](https://github.com/ayushshukla)")
    
    with social_cols[1]:
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #0369a1 0%, #0ea5e9 100%); 
                    border-radius: 12px; color: white;'>
            <div style='font-size: 2rem;'>💼</div>
            <p><strong>LinkedIn</strong></p>
            <p style='font-size: 0.8em;'>ayushshukla</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button('Visit LinkedIn', key='linkedin_btn', use_container_width=True):
            st.markdown("[Open LinkedIn](https://linkedin.com/in/ayushshukla)")
    
    with social_cols[2]:
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); 
                    border-radius: 12px; color: white;'>
            <div style='font-size: 2rem;'>📧</div>
            <p><strong>Email</strong></p>
            <p style='font-size: 0.8em;'>Contact Me</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button('Send Email', key='email_btn', use_container_width=True):
            st.markdown("[Compose Email](mailto:ayush.shukla@example.com)")
    
    with social_cols[3]:
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%); 
                    border-radius: 12px; color: white;'>
            <div style='font-size: 2rem;'>🌐</div>
            <p><strong>Portfolio</strong></p>
            <p style='font-size: 0.8em;'>ayushshukla.xyz</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button('Visit Portfolio', key='portfolio_btn', use_container_width=True):
            st.markdown("[Open Portfolio](https://ayushshukla.xyz)")
    
    # Enhanced App Features
    st.markdown("---")
    st.markdown("### ✨ App Features & Technology")
    
    feature_cols = st.columns(2)
    
    with feature_cols[0]:
        st.markdown("""
        <div class='metric-card'>
            <h3>🎯 What This App Does</h3>
            <div style='display: grid; gap: 1rem; margin-top: 1rem;'>
                <div style='display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem; background: #f1f5f9; border-radius: 8px;'>
                    <span style='font-size: 1.5rem;'>📊</span>
                    <div>
                        <strong>Financial Snapshot</strong>
                        <p style='margin: 0; font-size: 0.9em; color: #64748b;'>Complete financial profiling</p>
                    </div>
                </div>
                <div style='display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem; background: #f1f5f9; border-radius: 8px;'>
                    <span style='font-size: 1.5rem;'>💹</span>
                    <div>
                        <strong>Investment Planning</strong>
                        <p style='margin: 0; font-size: 0.9em; color: #64748b;'>SIP & mutual fund analysis</p>
                    </div>
                </div>
                <div style='display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem; background: #f1f5f9; border-radius: 8px;'>
                    <span style='font-size: 1.5rem;'>🎯</span>
                    <div>
                        <strong>Goal Tracking</strong>
                        <p style='margin: 0; font-size: 0.9em; color: #64748b;'>Set and achieve financial goals</p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_cols[1]:
        st.markdown("""
        <div class='metric-card'>
            <h3>🛠️ Built With</h3>
            <div style='display: grid; gap: 1rem; margin-top: 1rem;'>
                <div style='display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem; background: #f0f9ff; border-radius: 8px; border-left: 4px solid #0369a1;'>
                    <span style='font-size: 1.5rem;'>🐍</span>
                    <div>
                        <strong>Python & Streamlit</strong>
                        <p style='margin: 0; font-size: 0.9em; color: #64748b;'>Backend & frontend framework</p>
                    </div>
                </div>
                <div style='display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem; background: #f0fdf4; border-radius: 8px; border-left: 4px solid #16a34a;'>
                    <span style='font-size: 1.5rem;'>📊</span>
                    <div>
                        <strong>Plotly & Pandas</strong>
                        <p style='margin: 0; font-size: 0.9em; color: #64748b;'>Data visualization & analysis</p>
                    </div>
                </div>
                <div style='display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem; background: #faf5ff; border-radius: 8px; border-left: 4px solid #7c3aed;'>
                    <span style='font-size: 1.5rem;'>📄</span>
                    <div>
                        <strong>ReportLab</strong>
                        <p style='margin: 0; font-size: 0.9em; color: #64748b;'>PDF report generation</p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Mission Statement
    st.markdown("""
    <div class='financial-sticker' style='background: linear-gradient(135deg, #1e293b 0%, #334155 100%); color: white; text-align: center;'>
        <h3 style='color: white;'>🚀 My Mission</h3>
        <p style='color: white; font-size: 1.1em;'>
            To democratize financial knowledge and create tools that make personal finance 
            management accessible, understandable, and actionable for everyone.
        </p>
        <div style='font-size: 3rem; margin-top: 1rem;'>💡</div>
    </div>
    """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 2rem;'>
    <p>Built with ❤️ by Ayush Shukla | AI Financial Advisor v2.0</p>
    <p>💡 Your financial journey starts here!</p>
</div>
""", unsafe_allow_html=True)
