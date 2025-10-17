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
st.set_page_config(page_title='AI Financial Advisor — Professional Light (Pro)', page_icon='🤖', layout='wide')

# --- CSS: Professional Light theme ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
body { background: linear-gradient(180deg, #ffffff 0%, #f7f8fb 100%) !important; }
.main .block-container { padding: 2rem 3rem; max-width: 1400px; margin: 0 auto; }
body, h1, h2, h3, p { font-family: 'Inter', sans-serif; color: #0f172a; }
h1 { font-weight:700; }
.metric-card, .report-section { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 6px 18px rgba(15,23,42,0.06); border:1px solid rgba(15,23,42,0.04); }
.stButton>button { background-color: #334155; color: white; border-radius:8px; padding:10px 18px; font-weight:600; }
.stButton>button:hover{ background-color: #1f2937; }
.stProgress > div > div > div > div { background-color: #334155; }
.muted { color: #6b7280; }
.small { font-size: 0.9em; color:#6b7280; }
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
        self.current_savings = float(self.user_data.get('current_savings', 0) or 0)
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
            recs.append('Prioritize increasing your savings rate to at least 15-20% of income.')
        if advanced_metrics['dti_ratio'] > 40:
            recs.append('Your Debt-to-Income (DTI) is high — prioritize high-interest debt reduction.')
        if advanced_metrics['emergency_fund_coverage'] < 3:
            recs.append('Emergency fund low — aim for 3-6 months of essential expenses.')
        dining_ratio = metrics['expense_ratios'].get('Dining & Entertainment', 0)
        if dining_ratio > 10:
            recs.append('Consider trimming Dining & Entertainment and redirect to savings or SIPs.')
        recs.append('Automate investments with SIPs to build discipline and leverage rupee-cost averaging.')
        if risk_profile == 'Conservative':
            recs.append('As a Conservative investor, prefer debt funds, short-duration instruments and lower equity allocation.')
        elif risk_profile == 'Aggressive':
            recs.append('Aggressive investors can lean into equity; keep a solid emergency fund first.')
        else:
            recs.append('Balanced profile: maintain a diversified mix of equity and debt.')
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

# improved fund projection: month vs year detection

def fund_projection_amount(initial_amount, period_label, reported_return):
    # reported_return is assumed to be percent over the period for month-based and annualized for year-based
    if period_label.endswith('Y'):
        years = int(period_label[:-1])
        return initial_amount * ((1 + reported_return/100) ** years)
    elif period_label.endswith('M'):
        return initial_amount * (1 + reported_return/100)
    else:
        return initial_amount * (1 + reported_return/100)

# --- PDF generation using reportlab (Unicode-capable) ---

def create_pdf_report_reportlab(metrics, advanced_metrics, recommendations, health_score, user_data, sim_data):
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

    elems.append(Paragraph('Key Financial Overview', styles['Heading2']))
    kv = [
        ['Monthly Income', f"INR {user_data.get('monthly_income',0):,.0f}"],
        ['Total Monthly Expenses', f"INR {metrics['total_expenses']:,.0f}"],
        ['Monthly Savings', f"INR {metrics['monthly_savings']:,.0f}"],
        ['Savings Rate', f"{metrics['savings_rate']:.1f}%"]
    ]
    t = Table(kv, hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(1,0),colors.whitesmoke), ('LINEBELOW',(0,0),(-1,0),1,colors.grey)]))
    elems.append(t)
    elems.append(Spacer(1,12))

    elems.append(Paragraph('Advanced Health Metrics', styles['Heading2']))
    adv = [
        ['Financial Health Score', f"{health_score}/100"],
        ['Debt-to-Income Ratio', f"{advanced_metrics['dti_ratio']:.1f}%"],
        ['Emergency Fund Coverage', f"{advanced_metrics['emergency_fund_coverage']:.1f} months"],
        ['Net Worth', f"INR {advanced_metrics['net_worth']:,.0f}"]
    ]
    t2 = Table(adv, hAlign='LEFT')
    elems.append(t2)
    elems.append(Spacer(1,12))

    if sim_data:
        elems.append(Paragraph('Investment Simulation Summary', styles['Heading2']))
        sim_kv = [
            ['Fund Selected', sim_data.get('fund_name','-')],
            ['Initial Investment', f"INR {sim_data.get('amount',0):,.0f}"],
            ['5Y Value (sim)', f"INR {sim_data.get('5Y_value',0):,.0f}"],
            ['5Y Gain (sim)', f"INR {sim_data.get('5Y_gain',0):,.0f}"]
        ]
        elems.append(Table(sim_kv))
        elems.append(Spacer(1,12))

    elems.append(Paragraph('Actionable Recommendations', styles['Heading2']))
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

# --- App UI ---
st.title('AI Financial Advisor — Professional Light (Pro)')
st.write('A polished light UI with net-worth, goals, risk profiling, portfolio visualizer and Unicode PDF export.')

# Top-level navigation
page = st.sidebar.selectbox('Navigate', ['Snapshot', 'Dashboard', 'Investment Center', 'Goals Planner', 'Risk Quiz', 'Portfolio', 'Export / Download', 'Settings'])

# Snapshot page
if page == 'Snapshot':
    st.header('Financial Snapshot')
    with st.form('snapshot_form'):
        c1, c2 = st.columns(2)
        with c1:
            monthly_income = st.number_input('Monthly Take-Home Income (₹)', min_value=0.0, value=float(st.session_state.user_data.get('monthly_income', 75000.0)), step=1000.0)
            current_savings = st.number_input('Current Savings / Emergency Fund (₹)', min_value=0.0, value=float(st.session_state.user_data.get('current_savings', 50000.0)), step=1000.0)
            investment_percentage = st.slider('% of Income to Invest', 0, 100, int(st.session_state.user_data.get('investment_percentage', 20)))
        with c2:
            st.subheader('Expenses (monthly)')
            defaults = st.session_state.user_data.get('expenses', {})
            rent_emi = st.number_input('Rent/EMI', 0.0, value=float(defaults.get('Rent/EMI',20000.0)), step=500.0)
            groceries = st.number_input('Groceries', 0.0, value=float(defaults.get('Groceries',8000.0)), step=200.0)
            utilities = st.number_input('Utilities (Electricity, Water)', 0.0, value=float(defaults.get('Utilities',3000.0)), step=100.0)
            transportation = st.number_input('Transportation', 0.0, value=float(defaults.get('Transportation',4000.0)), step=100.0)
            insurance = st.number_input('Insurance Premiums', 0.0, value=float(defaults.get('Insurance',2000.0)), step=100.0)
            loan_repayments = st.number_input('Other Loan Repayments', 0.0, value=float(defaults.get('Other Loans',5000.0)), step=500.0)
            dining_entertainment = st.number_input('Dining & Entertainment', 0.0, value=float(defaults.get('Dining & Entertainment',6000.0)), step=200.0)
            shopping = st.number_input('Shopping', 0.0, value=float(defaults.get('Shopping',5000.0)), step=200.0)
            internet_phone = st.number_input('Internet & Phone', 0.0, value=float(defaults.get('Internet/Phone',1000.0)), step=50.0)
            miscellaneous = st.number_input('Miscellaneous', 0.0, value=float(defaults.get('Miscellaneous',2000.0)), step=100.0)

        st.markdown('---')
        st.subheader('Assets & Liabilities (Net Worth)')
        assets_defaults = st.session_state.user_data.get('assets', {})
        liab_defaults = st.session_state.user_data.get('liabilities', {})
        asset_cash = st.number_input('Cash & Bank Balances', 0.0, value=float(assets_defaults.get('Cash',50000.0)), step=1000.0)
        asset_stocks = st.number_input('Stocks / Mutual Funds (Market Value)', 0.0, value=float(assets_defaults.get('Stocks/MF',100000.0)), step=1000.0)
        asset_property = st.number_input('Property Value (approx)', 0.0, value=float(assets_defaults.get('Property',0.0)), step=10000.0)
        liability_loans = st.number_input('Outstanding Loans (Home/Personal)', 0.0, value=float(liab_defaults.get('Outstanding Loans',0.0)), step=1000.0)

        save_snapshot = st.form_submit_button('Save Snapshot')

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
        st.success('Snapshot saved ✔️')

# Dashboard
elif page == 'Dashboard':
    if not st.session_state.user_data:
        st.info('No snapshot found. Please create one in Snapshot.')
    else:
        user_data = st.session_state.user_data
        analyzer = FinancialAnalyzer(user_data)
        metrics = analyzer.calculate_financial_metrics()
        advanced = analyzer.calculate_advanced_metrics(metrics)
        risk_profile = st.session_state.get('risk_profile', 'Balanced')
        recs = analyzer.generate_recommendations(metrics, advanced, risk_profile)
        health_score = min(100, max(0, int((1 - advanced['dti_ratio']/100) * 30 + metrics['savings_rate'] * 2 + (advanced['emergency_fund_coverage']/6)*20)))

        st.header('Overview')
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric('Monthly Income', format_inr(user_data['monthly_income']))
        c2.metric('Total Expenses', format_inr(metrics['total_expenses']))
        c3.metric('Monthly Savings', format_inr(metrics['monthly_savings']), f"{metrics['savings_rate']:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="report-section">', unsafe_allow_html=True)
        st.subheader('Financial Health')
        col1, col2 = st.columns([1,2])
        with col1:
            fig = go.Figure(go.Indicator(mode='gauge+number', value=health_score, gauge={'axis':{'range':[None,100]}, 'bar':{'color':'#334155'}}))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.write(f"**DTI:** {advanced['dti_ratio']:.1f}%")
            st.write(f"**Emergency fund:** {advanced['emergency_fund_coverage']:.1f} months (Target: 6 months)")
            st.write(f"**Net Worth:** {format_inr(advanced['net_worth'])}")

        st.markdown('---')
        st.subheader('Expense Breakdown')
        expense_df = pd.DataFrame(list(user_data['expenses'].items()), columns=['Category','Amount']).query('Amount>0').sort_values('Amount', ascending=False)
        fig_t = px.treemap(expense_df, path=['Category'], values='Amount', title='Spending by Category')
        st.plotly_chart(fig_t, use_container_width=True)

        st.markdown('---')
        st.subheader('Top Recommendations')
        for r in recs[:6]:
            st.info(r)
        st.markdown('</div>', unsafe_allow_html=True)

# Investment Center
elif page == 'Investment Center':
    st.header('Investment Center')
    mf_df = get_live_mutual_fund_data()
    c1, c2 = st.columns([1,2])
    with c1:
        category = st.selectbox('Fund Category', mf_df['Category'].unique())
        funds_filtered = mf_df[mf_df['Category']==category]
        fund_name = st.selectbox('Fund', funds_filtered['Fund Name'])
        invest_amt = st.number_input('Investment Amount (₹)', min_value=1000.0, value=50000.0, step=1000.0)
        selected = mf_df[mf_df['Fund Name']==fund_name].iloc[0]
        st.write('Risk:', selected['Risk'])
        st.write('Rating:', '★'*int(selected['Rating']))
    with c2:
        st.subheader(f"Simulated Growth for {format_inr(invest_amt)} in {fund_name}")
        periods = ['1M','6M','1Y','3Y','5Y']
        returns = [selected['1M Return'], selected['6M Return'], selected['1Y Return'], selected['3Y CAGR'], selected['5Y CAGR']]
        vals = [fund_projection_amount(invest_amt, p, r) for p,r in zip(periods, returns)]
        gains = [v - invest_amt for v in vals]
        st.session_state.investment_simulation = {'fund_name':fund_name, 'amount': invest_amt, '5Y_value': vals[-1], '5Y_gain': gains[-1]}
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Investment', x=periods, y=[invest_amt]*len(periods), marker_color='#94a3b8'))
        fig.add_trace(go.Bar(name='Profit', x=periods, y=gains, marker_color='#10b981'))
        fig.update_layout(barmode='stack', title='Investment vs Profit')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('---')
    st.subheader('Compare Funds (Top 5 in chosen category)')
    top = funds_filtered.sort_values('5Y CAGR', ascending=False).head(5)
    st.dataframe(top[['Fund Name','5Y CAGR','3Y CAGR','1Y Return','Risk','Rating']])

# Goals Planner
elif page == 'Goals Planner':
    st.header('Goals & SIP Planner')
    if 'goals' not in st.session_state:
        st.session_state.goals = []

    with st.form('goal_add'):
        g_name = st.text_input('Goal Name')
        g_amount = st.number_input('Target Amount (₹)', min_value=0.0, value=500000.0, step=1000.0)
        g_years = st.number_input('Years to Achieve', min_value=1, value=5)
        g_return = st.slider('Expected Annual Return (%)', 0, 20, 8)
        add = st.form_submit_button('Add Goal')
    if add and g_name:
        st.session_state.goals.append({'name':g_name,'amount':g_amount,'years':g_years,'return':g_return})
        save_json(GOALS_FILE, st.session_state.goals)
        st.success('Goal added')

    if st.session_state.goals:
        df = pd.DataFrame(st.session_state.goals)
        st.dataframe(df)
        st.markdown('### Required Monthly SIP per Goal')
        for g in st.session_state.goals:
            r = g['return']/100/12
            n = g['years']*12
            target = g['amount']
            if r>0:
                sip = target * (r / ((1+r)**n - 1))
            else:
                sip = target / n
            st.write(f"{g['name']}: target {format_inr(target)} in {g['years']} years → SIP {format_inr(sip)} / month")

# Risk Quiz
elif page == 'Risk Quiz':
    st.header('Risk Profile Quiz (Short)')
    q1 = st.radio('If the market falls 20% in a year, you would:', ['Sell most investments', 'Wait and review', 'Buy more'])
    q2 = st.radio('Your investment horizon is:', ['<3 years', '3-7 years', '>7 years'])
    q3 = st.radio('Primary goal:', ['Capital preservation', 'Balanced growth', 'Max growth'])
    map_scores = {'Sell most investments':0, 'Wait and review':1, 'Buy more':2, '<3 years':0, '3-7 years':1, '>7 years':2, 'Capital preservation':0, 'Balanced growth':1, 'Max growth':2}
    if st.button('Calculate Profile'):
        score = map_scores[q1] + map_scores[q2] + map_scores[q3]
        if score <= 3:
            profile = 'Conservative'
        elif score <=5:
            profile = 'Balanced'
        else:
            profile = 'Aggressive'
        st.session_state.risk_profile = profile
        st.success(f'Your profile: {profile}')

# Portfolio
elif page == 'Portfolio':
    st.header('Portfolio Visualizer & Export')
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []

    with st.form('pf'): 
        cols = st.columns(3)
        name = cols[0].text_input('Holding Name')
        amt = cols[1].number_input('Amount (₹)', min_value=0.0, value=0.0, step=1000.0)
        add = cols[2].form_submit_button('Add Holding')
        if add and name and amt>0:
            st.session_state.portfolio.append({'name':name,'amount':amt})
            save_json(PORTFOLIO_FILE, st.session_state.portfolio)
            st.success('Holding added')

    if st.session_state.portfolio:
        pfdf = pd.DataFrame(st.session_state.portfolio)
        pfdf['pct'] = pfdf['amount'] / pfdf['amount'].sum() * 100
        st.dataframe(pfdf)
        fig = px.pie(pfdf, names='name', values='amount', title='Allocation')
        st.plotly_chart(fig, use_container_width=True)
        csv = pfdf.to_csv(index=False).encode('utf-8')
        st.download_button('Download Portfolio CSV', csv, 'portfolio.csv', 'text/csv')

# Export / Download
elif page == 'Export / Download':
    st.header('Export Reports & Data')
    if not st.session_state.user_data:
        st.info('No data to export.')
    else:
        analyzer = FinancialAnalyzer(st.session_state.user_data)
        metrics = analyzer.calculate_financial_metrics()
        advanced = analyzer.calculate_advanced_metrics(metrics)
        recs = analyzer.generate_recommendations(metrics, advanced, st.session_state.get('risk_profile','Balanced'))
        health_score = min(100, max(0, int((1 - advanced['dti_ratio']/100) * 30 + metrics['savings_rate'] * 2 + (advanced['emergency_fund_coverage']/6)*20)))
        sim = st.session_state.get('investment_simulation', {})

        if st.button('Download PDF Report'):
            pdf_bytes = create_pdf_report_reportlab(metrics, advanced, recs, health_score, st.session_state.user_data, sim)
            st.download_button('Download PDF', pdf_bytes, f'Financial_Report_{datetime.now().strftime("%Y%m%d")}.pdf', 'application/pdf')

        if st.button('Download Snapshot JSON'):
            st.download_button('Download JSON', json.dumps(st.session_state.user_data, indent=2).encode('utf-8'), 'snapshot.json', 'application/json')

# Settings
elif page == 'Settings':
    st.header('Settings & Accessibility')
    st.write('Personalization and toggles')
    animations = st.checkbox('Enable subtle animations (may affect perf)', value=True)
    show_emoji = st.checkbox('Show emojis in recommendations', value=False)
    if st.button('Save Settings'):
        st.success('Settings saved locally (session only)')

# End

# final note
st.sidebar.markdown('---')
st.sidebar.markdown('Built with ❤️  • Professional Light Theme')
