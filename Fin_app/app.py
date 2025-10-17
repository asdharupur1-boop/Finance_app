import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import tempfile, shutil

# --- Developer Info ---
DEVELOPER_NAME = "Ayush Shukla"
LINKEDIN = "https://www.linkedin.com/in/ayush-shukla"
GITHUB = "https://github.com/ayush-shukla"
EMAIL = "ayush.shukla@example.com"
PORTFOLIO_LOGO_URL = "https://via.placeholder.com/100x100.png?text=Logo"

# --- PDF Font Setup ---
try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    DEFAULT_FONT = 'DejaVuSans'
except Exception:
    DEFAULT_FONT = 'Helvetica'

# --- App Config ---
st.set_page_config(page_title='AI Financial Advisor — Professional Light (Pro)',
                   page_icon='🤖', layout='wide')

# --- CSS ---
st.markdown("""
<style>
body { background: linear-gradient(180deg, #ffffff 0%, #f7f8fb 100%) !important; font-family: 'Inter', sans-serif; color: #0f172a; }
h1,h2,h3,p { font-family: 'Inter', sans-serif; color: #0f172a; }
h1 { font-weight:700; }
.metric-card, .report-section, .section-container { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 6px 18px rgba(15,23,42,0.06); border:1px solid rgba(15,23,42,0.04); margin-bottom:20px; }
.stButton>button { background-color: #334155; color: white; border-radius:8px; padding:10px 18px; font-weight:600; }
.stButton>button:hover{ background-color: #1f2937; }
.stProgress > div > div > div > div { background-color: #334155; }
.muted { color: #6b7280; }
.small { font-size: 0.9em; color:#6b7280; }
</style>
""", unsafe_allow_html=True)

# --- Data Persistence ---
DATA_DIR = os.path.join(os.getcwd(), '.ai_financial_data')
os.makedirs(DATA_DIR, exist_ok=True)
SNAPSHOT_FILE = os.path.join(DATA_DIR, 'user_snapshot.json')
GOALS_FILE = os.path.join(DATA_DIR, 'user_goals.json')
PORTFOLIO_FILE = os.path.join(DATA_DIR, 'user_portfolio.json')

# --- Helper Functions ---
def format_inr(x):
    try:
        return f"₹{x:,.0f}"
    except:
        return str(x)

def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path,'r') as f:
                return json.load(f)
    except:
        pass
    return default

def save_json_atomic(path, data):
    dirpath = os.path.dirname(path) or '.'
    os.makedirs(dirpath, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dirpath, suffix='.tmp')
    try:
        with os.fdopen(fd,'w') as f:
            json.dump(data,f,indent=2)
            f.flush()
            os.fsync(f.fileno())
        shutil.move(tmp,path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

def investment_projection_calculator(monthly_investment, years, expected_return):
    monthly_rate = expected_return/100/12
    months = int(max(0,years*12))
    if months==0: return 0.0,0.0
    if monthly_rate!=0:
        fv = monthly_investment*((1+monthly_rate)**months -1)/monthly_rate
    else:
        fv = monthly_investment*months
    total_invested = monthly_investment*months
    return fv,total_invested

def fund_projection_amount(initial_amount: float, period_label: str, reported_return: float) -> float:
    r = reported_return/100.0
    period_label = str(period_label).upper().strip()
    if period_label.endswith('Y'):
        years = float(period_label[:-1]) if period_label[:-1] else 1.0
        return initial_amount*((1+r)**years)
    if period_label.endswith('M'):
        return initial_amount*(1+r)
    return initial_amount*(1+r)

# --- Load Session State ---
if 'user_data' not in st.session_state: st.session_state.user_data = load_json(SNAPSHOT_FILE,{})
if 'goals' not in st.session_state: st.session_state.goals = load_json(GOALS_FILE,[])
if 'portfolio' not in st.session_state: st.session_state.portfolio = load_json(PORTFOLIO_FILE,[])
if 'risk_profile' not in st.session_state: st.session_state.risk_profile = 'Balanced'

# --- Developer Info Display ---
dev_col1, dev_col2 = st.columns([1,3])
with dev_col1:
    st.image(PORTFOLIO_LOGO_URL, width=80)
with dev_col2:
    st.markdown(f"**Developer:** {DEVELOPER_NAME}  \n**LinkedIn:** [link]({LINKEDIN})  \n**GitHub:** [link]({GITHUB})  \n**Email:** {EMAIL}")
    st.markdown("🔒 No worries, it is confidential 😎")
st.markdown("---")

# --- App Sections as Expanders ---
# Snapshot Section
with st.expander("💰 Financial Snapshot", expanded=True):
    st.subheader("Enter Your Current Financial Details")
    with st.form("snapshot_form"):
        c1,c2 = st.columns(2)
        with c1:
            monthly_income = st.number_input("Monthly Take-Home Income (₹)",0.0,value=float(st.session_state.user_data.get('monthly_income',75000.0)),step=1000.0)
            current_savings = st.number_input("Current Savings / Emergency Fund (₹)",0.0,value=float(st.session_state.user_data.get('current_savings',50000.0)),step=1000.0)
            investment_percentage = st.slider("% of Income to Invest",0,100,int(st.session_state.user_data.get('investment_percentage',20)))
        with c2:
            st.subheader("Expenses (monthly)")
            defaults = st.session_state.user_data.get('expenses',{})
            rent_emi = st.number_input("Rent/EMI",0.0,value=float(defaults.get('Rent/EMI',20000.0)),step=500.0)
            groceries = st.number_input("Groceries",0.0,value=float(defaults.get('Groceries',8000.0)),step=200.0)
            utilities = st.number_input("Utilities",0.0,value=float(defaults.get('Utilities',3000.0)),step=100.0)
            transportation = st.number_input("Transportation",0.0,value=float(defaults.get('Transportation',4000.0)),step=100.0)
            insurance = st.number_input("Insurance Premiums",0.0,value=float(defaults.get('Insurance',2000.0)),step=100.0)
            loan_repayments = st.number_input("Other Loan Repayments",0.0,value=float(defaults.get('Other Loans',5000.0)),step=500.0)
            dining_entertainment = st.number_input("Dining & Entertainment",0.0,value=float(defaults.get('Dining & Entertainment',6000.0)),step=200.0)
            shopping = st.number_input("Shopping",0.0,value=float(defaults.get('Shopping',5000.0)),step=200.0)
            internet_phone = st.number_input("Internet & Phone",0.0,value=float(defaults.get('Internet/Phone',1000.0)),step=50.0)
            miscellaneous = st.number_input("Miscellaneous",0.0,value=float(defaults.get('Miscellaneous',2000.0)),step=100.0)
        st.markdown("---")
        st.subheader("Assets & Liabilities")
        assets_defaults = st.session_state.user_data.get('assets',{})
        liab_defaults = st.session_state.user_data.get('liabilities',{})
        asset_cash = st.number_input("Cash & Bank Balances",0.0,value=float(assets_defaults.get('Cash',50000.0)),step=1000.0)
        asset_stocks = st.number_input("Stocks / Mutual Funds (Market Value)",0.0,value=float(assets_defaults.get('Stocks/MF',100000.0)),step=1000.0)
        asset_property = st.number_input("Property Value (approx)",0.0,value=float(assets_defaults.get('Property',0.0)),step=10000.0)
        liability_loans = st.number_input("Outstanding Loans (Home/Personal)",0.0,value=float(liab_defaults.get('Outstanding Loans',0.0)),step=1000.0)
        save_snapshot = st.form_submit_button("Save Snapshot")
    if save_snapshot:
        user_data = {
            "monthly_income": monthly_income,
            "current_savings": current_savings,
            "investment_percentage": investment_percentage,
            "expenses":{
                "Rent/EMI":rent_emi,
                "Other Loans":loan_repayments,
                "Utilities":utilities,
                "Internet/Phone":internet_phone,
                "Insurance":insurance,
                "Groceries":groceries,
                "Transportation":transportation,
                "Dining & Entertainment":dining_entertainment,
                "Shopping":shopping,
                "Miscellaneous":miscellaneous
            },
            "assets":{"Cash":asset_cash,"Stocks/MF":asset_stocks,"Property":asset_property},
            "liabilities":{"Outstanding Loans":liability_loans}
        }
        st.session_state.user_data = user_data
        save_json_atomic(SNAPSHOT_FILE,user_data)
        st.success("Snapshot saved ✔️")

# --- Load Financial Analyzer ---
class FinancialAnalyzer:
    def __init__(self,user_data):
        self.user_data=user_data or {}
        self.monthly_income=float(self.user_data.get('monthly_income',0) or 0)
        self.expenses={k:float(v or 0) for k,v in self.user_data.get('expenses',{}).items()}
        self.investment_pct=float(self.user_data.get('investment_percentage',0) or 0)
        self.current_savings=float(self.user_data.get('current_savings',0) or 0)
        self.assets={k:float(v or 0) for k,v in self.user_data.get('assets',{}).items()}
        self.liabilities={k:float(v or 0) for k,v in self.user_data.get('liabilities',{}).items()}
    def calculate_financial_metrics(self):
        total_expenses=sum(self.expenses.values())
        monthly_savings=self.monthly_income-total_expenses
        desired_investment=self.monthly_income*(self.investment_pct/100)
        savings_rate=(monthly_savings/self.monthly_income)*100 if self.monthly_income>0 else 0
        expense_ratios={c:(a/self.monthly_income)*100 if self.monthly_income>0 else 0 for c,a in self.expenses.items()}
        return {"total_expenses":total_expenses,"monthly_savings":monthly_savings,"desired_investment":desired_investment,"savings_rate":savings_rate,"expense_ratios":expense_ratios}
    def calculate_advanced_metrics(self,metrics):
        debt_payments=self.expenses.get('Rent/EMI',0)+self.expenses.get('Other Loans',0)
        dti_ratio=(debt_payments/self.monthly_income)*100 if self.monthly_income>0 else 0
        emergency_fund_coverage=(self.current_savings/metrics['total_expenses']) if metrics['total_expenses']>0 else 0
        annual_expenses=metrics['total_expenses']*12
        fire_number=annual_expenses*25
        total_assets=sum(self.assets.values())
        total_liabilities=sum(self.liabilities.values())
        net_worth=total_assets-total_liabilities
        return {"dti_ratio":dti_ratio,"emergency_fund_target":metrics['total_expenses']*6,"emergency_fund_coverage":emergency_fund_coverage,"fire_number":fire_number,"total_assets":total_assets,"total_liabilities":total_liabilities,"net_worth":net_worth}
    def generate_recommendations(self,metrics,advanced_metrics,risk_profile):
        recs=[]
        if metrics['savings_rate']<15: recs.append('Prioritize increasing your savings rate to at least 15-20% of income.')
        if advanced_metrics['dti_ratio']>40: recs.append('Your Debt-to-Income (DTI) is high — prioritize high-interest debt reduction.')
        if advanced_metrics['emergency_fund_coverage']<3: recs.append('Emergency fund low — aim for 3-6 months of essential expenses.')
        dining_ratio=metrics['expense_ratios'].get('Dining & Entertainment',0)
        if dining_ratio>10: recs.append('Consider trimming Dining & Entertainment and redirect to savings or SIPs.')
        recs.append('Automate investments with SIPs to build discipline and leverage rupee-cost averaging.')
        if risk_profile=='Conservative': recs.append('As a Conservative investor, prefer debt funds, short-duration instruments and lower equity allocation.')
        elif risk_profile=='Aggressive': recs.append('Aggressive investors can lean into equity; keep a solid emergency fund first.')
        else: recs.append('Balanced profile: maintain a diversified mix of equity and debt.')
        return recs

# --- Dashboard Section ---
with st.expander("📊 Dashboard Analysis",expanded=True):
    if not st.session_state.user_data:
        st.info("No snapshot found. Please create one above.")
    else:
        user_data=st.session_state.user_data
        analyzer=FinancialAnalyzer(user_data)
        metrics=analyzer.calculate_financial_metrics()
        advanced=analyzer.calculate_advanced_metrics(metrics)
        risk_profile=st.session_state.get('risk_profile','Balanced')
        recs=analyzer.generate_recommendations(metrics,advanced,risk_profile)
        health_score = min(100,max(0,int((1-advanced['dti_ratio']/100)*30+metrics['savings_rate']*2+(advanced['emergency_fund_coverage']/6)*20)))
        
        # Metrics Cards
        col1,col2,col3=st.columns(3)
        col1.metric("Monthly Income",format_inr(user_data['monthly_income']))
        col2.metric("Total Expenses",format_inr(metrics['total_expenses']))
        col3.metric("Monthly Savings",format_inr(metrics['monthly_savings']),f"{metrics['savings_rate']:.1f}%")
        
        # Income vs Expenses vs Savings Bar
        bar_df=pd.DataFrame({
            "Category":["Income","Expenses","Savings"],
            "Amount":[user_data['monthly_income'],metrics['total_expenses'],metrics['monthly_savings']]
        })
        fig_bar=px.bar(bar_df,x='Category',y='Amount',text='Amount',color='Category',color_discrete_map={'Income':'#10b981','Expenses':'#ef4444','Savings':'#3b82f6'})
        st.plotly_chart(fig_bar,use_container_width=True)
        
        # Expense Pie Chart
        expense_df=pd.DataFrame(list(user_data['expenses'].items()),columns=['Category','Amount']).query("Amount>0")
        fig_pie=px.pie(expense_df,names='Category',values='Amount',title='Expense Breakdown')
        st.plotly_chart(fig_pie,use_container_width=True)
        
        # Asset Allocation Pie
        asset_df=pd.DataFrame(list(user_data['assets'].items()),columns=['Asset','Amount']).query("Amount>0")
        fig_asset=px.pie(asset_df,names='Asset',values='Amount',title='Asset Allocation')
        st.plotly_chart(fig_asset,use_container_width=True)
        
        # Top Recommendations
        st.subheader("Top Recommendations")
        for r in recs[:6]:
            st.info(r)
