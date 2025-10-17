import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from io import BytesIO

# PDF using reportlab for Unicode support
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register a Unicode TTF if available
try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    DEFAULT_FONT = 'DejaVuSans'
except Exception:
    DEFAULT_FONT = 'Helvetica'

# App config
st.set_page_config(page_title='AI Financial Advisor — By Ayush Shukla', page_icon='🤖', layout='wide')

# Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
body { background: linear-gradient(180deg, #ffffff 0%, #f7f8fb 100%) !important; }
.main .block-container { padding: 2rem 3rem; max-width: 1400px; margin: 0 auto; }
body, h1, h2, h3, p { font-family: 'Inter', sans-serif; color: #0f172a; }
h1 { font-weight:700; }
.metric-card, .report-section { background: linear-gradient(145deg, #ffffff, #f1f5f9); border-radius: 15px; padding: 20px; box-shadow: 0 6px 18px rgba(15,23,42,0.08); border:1px solid rgba(15,23,42,0.05); margin-bottom:15px; }
.stButton>button { background-color: #334155; color: white; border-radius:8px; padding:10px 18px; font-weight:600; }
.stButton>button:hover{ background-color: #1f2937; }
.stProgress > div > div > div > div { background-color: #334155; }
.muted { color: #6b7280; }
.small { font-size: 0.9em; color:#6b7280; }
</style>
""", unsafe_allow_html=True)

# Persistence
DATA_DIR = '.ai_financial_data'
os.makedirs(DATA_DIR, exist_ok=True)
SNAPSHOT_FILE = os.path.join(DATA_DIR, 'user_snapshot.json')
GOALS_FILE = os.path.join(DATA_DIR, 'user_goals.json')
PORTFOLIO_FILE = os.path.join(DATA_DIR, 'user_portfolio.json')

# Helpers
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

# Financial Analyzer
class FinancialAnalyzer:
    def __init__(self, user_data):
        self.user_data = user_data or {}
        self.monthly_income = float(self.user_data.get('monthly_income', 0) or 0)
        self.expenses = {k: float(v or 0) for k, v in self.user_data.get('expenses', {}).items()}
        self.investment_pct = float(self.user_data.get('investment_percentage', 0) or 0)
        self.current_savings = float(self.user_data.get('current_savings', 0) or 0)
        self.assets = {k: float(v or 0) for k, v in self.user_data.get('assets', {}).items()}
        self.liabilities = {k: float(v or 0) for k, v in self.user_data.get('liabilities', {}).items()}

    def calculate_financial_metrics(self):
        total_expenses = sum(self.expenses.values())
        monthly_savings = self.monthly_income - total_expenses
        desired_investment = self.monthly_income * (self.investment_pct / 100)
        savings_rate = (monthly_savings / self.monthly_income) * 100 if self.monthly_income > 0 else 0
        expense_ratios = {c: (a / self.monthly_income) * 100 if self.monthly_income > 0 else 0 for c, a in self.expenses.items()}
        return {'total_expenses': total_expenses,'monthly_savings': monthly_savings,'desired_investment': desired_investment,'savings_rate': savings_rate,'expense_ratios': expense_ratios}

    def calculate_advanced_metrics(self, metrics):
        debt_payments = self.expenses.get('Rent/EMI', 0) + self.expenses.get('Other Loans', 0)
        dti_ratio = (debt_payments / self.monthly_income) * 100 if self.monthly_income > 0 else 0
        emergency_fund_coverage = (self.current_savings / metrics['total_expenses']) if metrics['total_expenses'] > 0 else 0
        annual_expenses = metrics['total_expenses'] * 12
        fire_number = annual_expenses * 25
        total_assets = sum(self.assets.values())
        total_liabilities = sum(self.liabilities.values())
        net_worth = total_assets - total_liabilities
        return {'dti_ratio': dti_ratio,'emergency_fund_target': metrics['total_expenses'] * 6,'emergency_fund_coverage': emergency_fund_coverage,'fire_number': fire_number,'total_assets': total_assets,'total_liabilities': total_liabilities,'net_worth': net_worth}

    def generate_recommendations(self, metrics, advanced_metrics, risk_profile):
        recs = []
        if metrics['savings_rate'] < 15:
            recs.append('💡 Prioritize increasing your savings rate to at least 15-20% of income.')
        if advanced_metrics['dti_ratio'] > 40:
            recs.append('⚠️ Your Debt-to-Income (DTI) is high — prioritize high-interest debt reduction.')
        if advanced_metrics['emergency_fund_coverage'] < 3:
            recs.append('✅ Emergency fund low — aim for 3-6 months of essential expenses.')
        dining_ratio = metrics['expense_ratios'].get('Dining & Entertainment', 0)
        if dining_ratio > 10:
            recs.append('🍽️ Consider trimming Dining & Entertainment and redirect to savings or SIPs.')
        recs.append('Automate investments with SIPs to build discipline and leverage rupee-cost averaging.')
        if risk_profile == 'Conservative':
            recs.append('As a Conservative investor, prefer debt funds, short-duration instruments and lower equity allocation.')
        elif risk_profile == 'Aggressive':
            recs.append('Aggressive investors can lean into equity; keep a solid emergency fund first.')
        else:
            recs.append('Balanced profile: maintain a diversified mix of equity and debt.')
        return recs

# SIP Calculator
def investment_projection_calculator(monthly_investment, years, expected_return):
    monthly_rate = expected_return / 100 / 12
    months = int(years * 12)
    if monthly_rate > 0:
        future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    else:
        future_value = monthly_investment * months
    total_invested = monthly_investment * months
    return future_value, total_invested

# Load session state
if 'user_data' not in st.session_state:
    st.session_state.user_data = load_json(SNAPSHOT_FILE, {})
if 'goals' not in st.session_state:
    st.session_state.goals = load_json(GOALS_FILE, [])
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = load_json(PORTFOLIO_FILE, [])

# Tabs
tabs = st.tabs(['Snapshot','Dashboard','Investment Center','Goals Planner','Risk Quiz','Portfolio','Export / Download','About / Developer'])

# --- Snapshot Tab ---
with tabs[0]:
    st.header('Financial Snapshot')
    # Put all your original snapshot form code here (unchanged)

# --- Dashboard Tab ---
with tabs[1]:
    st.header('Dashboard')
    # Put all your original dashboard code here (unchanged)

# --- Investment Center Tab ---
with tabs[2]:
    st.header('Investment Center')
    # Your mutual fund selection + SIP calculation code

# --- Goals Planner Tab ---
with tabs[3]:
    st.header('Goals Planner')
    # Original goals planner code

# --- Risk Quiz Tab ---
with tabs[4]:
    st.header('Risk Quiz')
    # Original risk quiz code

# --- Portfolio Tab ---
with tabs[5]:
    st.header('Portfolio')
    # Original portfolio code

# --- Export / Download Tab ---
with tabs[6]:
    st.header('Export / Download')
    # Original export code

# --- About / Developer Tab ---
with tabs[7]:
    st.header('About / Developer')
    st.markdown("""
    **Ayush Shukla**  
    AI Financial Advisor Developer  

    [![GitHub](https://img.shields.io/badge/GitHub-000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/yourusername)
