import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Financial Advisor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for "Gradient Aura" Light Theme with Animations ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Force the gradient background on the main body */
    body {
        background-image: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
        background-attachment: fixed;
    }

    /* Make the primary container transparent to show the body's gradient */
    .main .block-container {
        padding: 2rem 5rem;
        background: transparent;
    }
    
    /* Font styles for high contrast */
    body, h1, h2, h3, h4, h5, h6, p, .stMarkdown {
        font-family: 'Inter', sans-serif;
        color: #1e293b; /* Dark Slate Gray for text */
    }
    h1 { font-weight: 700; color: #0f172a; }
    h2 {
        border-bottom: 2px solid #6366f1; /* Indigo accent */
        padding-bottom: 5px;
        margin-top: 40px;
    }
    
    /* Keyframe Animations */
    @keyframes slideInUp {
        from { opacity: 0; transform: translateY(50px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7); }
        70% { transform: scale(1.05); box-shadow: 0 0 0 10px rgba(99, 102, 241, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
    }

    /* Metric Card Styling with Staggered Animation */
    .metric-card {
        background-color: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.9);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        opacity: 0; /* Initially hidden for animation */
        animation: slideInUp 0.6s ease-out forwards;
    }
    /* Stagger the animation for each card */
    [data-testid="column"]:nth-of-type(1) .metric-card { animation-delay: 0.2s; }
    [data-testid="column"]:nth-of-type(2) .metric-card { animation-delay: 0.3s; }
    [data-testid="column"]:nth-of-type(3) .metric-card { animation-delay: 0.4s; }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    /* Button Styling with Pulse Animation */
    .stButton>button {
        background-color: #6366f1;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 1.1em;
        transition: background-color 0.3s ease;
        animation: pulse 2s infinite; /* Add pulse animation */
    }
    .stButton>button:hover {
        background-color: #4f46e5;
        animation: none; /* Stop pulsing on hover */
    }

    .stProgress > div > div > div > div {
        background-color: #6366f1;
    }
    
    .report-section {
        background-color: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(5px);
        border-radius: 12px;
        padding: 25px;
        margin-top: 2rem;
        animation: slideInUp 0.8s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'report_generated' not in st.session_state:
    st.session_state.report_generated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'investment_simulation' not in st.session_state:
    st.session_state.investment_simulation = {}


# --- Financial Analyzer Class ---
class FinancialAnalyzer:
    def __init__(self, user_data):
        self.user_data = user_data
        self.monthly_income = user_data.get('monthly_income', 0)
        self.expenses = user_data.get('expenses', {})
        self.investment_pct = user_data.get('investment_percentage', 0)
        self.current_savings = user_data.get('current_savings', 0)

    def calculate_financial_metrics(self):
        total_expenses = sum(self.expenses.values())
        monthly_savings = self.monthly_income - total_expenses
        return {
            'total_expenses': total_expenses,
            'monthly_savings': monthly_savings,
            'desired_investment': self.monthly_income * (self.investment_pct / 100),
            'savings_rate': (monthly_savings / self.monthly_income) * 100 if self.monthly_income > 0 else 0,
            'expense_ratios': {c: (a / self.monthly_income) * 100 if self.monthly_income > 0 else 0 for c, a in self.expenses.items()}
        }
    
    def calculate_advanced_metrics(self, metrics):
        debt_payments = self.expenses.get('Rent/EMI', 0) + self.expenses.get('Other Loans', 0)
        dti_ratio = (debt_payments / self.monthly_income) * 100 if self.monthly_income > 0 else 0
        emergency_fund_coverage = (self.current_savings / metrics['total_expenses']) if metrics['total_expenses'] > 0 else 0
        annual_expenses = metrics['total_expenses'] * 12
        fire_number = annual_expenses * 25
        
        return {
            'dti_ratio': dti_ratio,
            'emergency_fund_target': metrics['total_expenses'] * 6,
            'emergency_fund_coverage': emergency_fund_coverage,
            'fire_number': fire_number
        }

    def generate_recommendations(self, metrics, advanced_metrics):
        recommendations = []
        if metrics['savings_rate'] < 15:
            recommendations.append("🚀 **Prioritize Savings:** Your savings rate is below the recommended 15-20%. Focus on reducing variable expenses to free up more cash.")
        
        if advanced_metrics['dti_ratio'] > 40:
             recommendations.append("📈 **High Debt-to-Income:** Your DTI ratio is high. Prioritize paying down high-interest debt to improve your financial flexibility.")
        
        if advanced_metrics['emergency_fund_coverage'] < 3:
            recommendations.append("🛡️ **Build a Safety Net:** Your emergency fund is low. Aim to build a fund covering 3-6 months of essential living expenses before making aggressive investments.")

        dining_ratio = metrics['expense_ratios'].get('Dining & Entertainment', 0)
        if dining_ratio > 10:
             recommendations.append("🧠 **Behavioral Nudge:** High spending on 'Dining & Entertainment' can indicate 'Present Bias' (prioritizing short-term wants). A small reduction here can significantly boost long-term wealth.")

        recommendations.append("🤖 **Automate Your Wealth:** Set up a Systematic Investment Plan (SIP) to automatically invest your desired amount each month. This builds discipline and leverages dollar-cost averaging.")
        
        return recommendations

# --- PDF Report Generation ---
class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, 'Your Financial Summary Report', align='C', ln=1)
        self.set_font('Helvetica', 'I', 9)
        self.cell(0, 5, "Generated by AI Financial Advisor | Developed by Ayush Shukla", ln=1, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')
        
    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 6, title, ln=1, align='L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 5, body, align='L')
        self.ln()

def clean_text_for_pdf(text):
    text = str(text)
    text = text.replace('**', '').replace("🚀", "").replace("👍", "").replace("🎉", "").replace("🔧", "").replace("🔍", "").replace("🤖", "").replace("🛡️", "").replace("🧠", "").replace("📈", "")
    return text.strip()

def create_pdf_report(metrics, advanced_metrics, recommendations, health_score, user_data, sim_data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 10, f"Report for: User | Date: {datetime.now().strftime('%Y%m%d')}", ln=1)
    
    pdf.chapter_title("Key Financial Overview")
    pdf.chapter_body(
        f"Monthly Income: INR {user_data['monthly_income']:,.0f}\n"
        f"Total Monthly Expenses: INR {metrics['total_expenses']:,.0f}\n"
        f"Monthly Savings: INR {metrics['monthly_savings']:,.0f}\n"
        f"Savings Rate: {metrics['savings_rate']:.1f}%"
    )
    
    pdf.chapter_title("Advanced Health Metrics")
    pdf.chapter_body(
        f"Financial Health Score: {health_score}/100\n"
        f"Debt-to-Income Ratio: {advanced_metrics['dti_ratio']:.1f}%\n"
        f"Emergency Fund Coverage: {advanced_metrics['emergency_fund_coverage']:.1f} months"
    )

    if sim_data:
        pdf.chapter_title("Investment Simulation Summary")
        pdf.chapter_body(
            f"Fund Selected: {sim_data['fund_name']}\n"
            f"Initial Investment: INR {sim_data['amount']:,.0f}\n"
            f"Growth over 5 Years (Simulated): INR {sim_data['5Y_value']:,.0f} (Gain of INR {sim_data['5Y_gain']:,.0f})"
        )

    pdf.chapter_title("Actionable Recommendations")
    for i, rec in enumerate(recommendations, 1):
        rec_text = clean_text_for_pdf(rec)
        pdf.multi_cell(0, 5, f"{i}. {rec_text}", align='L')
    
    return pdf.output(dest='S').encode('latin-1')

# --- Data & Calculation Functions ---
@st.cache_data
def get_live_mutual_fund_data():
    # SIMULATED REAL-TIME DATA: In a real app, this would come from an API
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

def investment_projection_calculator(monthly_investment, years, expected_return):
    monthly_rate = expected_return / 100 / 12
    months = years * 12
    if monthly_rate > 0:
        future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    else:
        future_value = monthly_investment * months
    total_invested = monthly_investment * months
    return future_value, total_invested

# --- UI Application Flow ---

def data_entry_page():
    st.title("Welcome to your AI Financial Advisor 🤖")
    st.markdown("Let's start by gathering some basic financial details to generate your personalized report.")
    st.markdown("---")
    
    st.header("Step 1: Your Financial Snapshot")
    
    with st.form(key='financial_form'):
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("💰 Income & Savings")
            monthly_income = st.number_input("Monthly Take-Home Income (₹)", 0, 10000000, 75000, 1000)
            current_savings = st.number_input("Current Savings / Emergency Fund (₹)", 0, 100000000, 50000, 5000)
            
            st.subheader("📈 Investment Goal")
            investment_percentage = st.slider("% of Income to Invest", 0, 100, 20)

        with c2:
            st.subheader("💸 Expenses")
            exp_c1, exp_c2 = st.columns(2)
            with exp_c1:
                rent_emi = st.number_input("Rent/EMI", 0, 1000000, 20000, 500)
                groceries = st.number_input("Groceries", 0, 100000, 8000, 200)
                utilities = st.number_input("Utilities (Electricity, Water)", 0, 50000, 3000, 100)
                transportation = st.number_input("Transportation", 0, 50000, 4000, 100)
                insurance = st.number_input("Insurance Premiums", 0, 100000, 2000, 100)
            with exp_c2:
                loan_repayments = st.number_input("Other Loan Repayments", 0, 500000, 5000, 500)
                dining_entertainment = st.number_input("Dining & Entertainment", 0, 100000, 6000, 200)
                shopping = st.number_input("Shopping", 0, 100000, 5000, 200)
                internet_phone = st.number_input("Internet & Phone", 0, 20000, 1000, 50)
                miscellaneous = st.number_input("Miscellaneous", 0, 100000, 2000, 100)

        submitted = st.form_submit_button(label="✨ Generate My Financial Report")

    if submitted:
        if monthly_income == 0:
            st.error("Monthly Income cannot be zero.")
        else:
            st.session_state.user_data = {
                'monthly_income': monthly_income, 'current_savings': current_savings,
                'investment_percentage': investment_percentage,
                'expenses': {
                    'Rent/EMI': rent_emi, 'Other Loans': loan_repayments, 'Utilities': utilities,
                    'Internet/Phone': internet_phone, 'Insurance': insurance, 'Groceries': groceries,
                    'Transportation': transportation, 'Dining & Entertainment': dining_entertainment,
                    'Shopping': shopping, 'Miscellaneous': miscellaneous
                }
            }
            st.session_state.report_generated = True
            st.rerun()

def analytics_report_page():
    user_data = st.session_state.user_data
    analyzer = FinancialAnalyzer(user_data)
    metrics = analyzer.calculate_financial_metrics()
    advanced_metrics = analyzer.calculate_advanced_metrics(metrics)
    recommendations = analyzer.generate_recommendations(metrics, advanced_metrics)
    health_score = min(100, max(0, int((1 - advanced_metrics['dti_ratio']/100) * 30 + metrics['savings_rate'] * 2 + (advanced_metrics['emergency_fund_coverage']/6)*20)))
    
    st.title("Your Personalized Financial Report")

    # --- Section 1: At-a-Glance Summary ---
    st.header("📊 At-a-Glance Summary")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="metric-card"><h4>💰 Monthly Income</h4><h3>₹{user_data["monthly_income"]:,.0f}</h3></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><h4>💸 Total Expenses</h4><h3>₹{metrics["total_expenses"]:,.0f}</h3></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card"><h4>🏦 Monthly Savings</h4><h3>₹{metrics["monthly_savings"]:,.0f}</h3><p style="color: #10b981; font-weight: bold;">{metrics["savings_rate"]:.1f}% Savings Rate</p></div>', unsafe_allow_html=True)
    
    # --- Section 2: Financial Health Deep-Dive ---
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.header("❤️ Financial Health Deep-Dive")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Overall Health Score")
        fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=health_score, title={'text': "Score"},
            gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#6366f1"}, 'steps': [{'range': [0, 40], 'color': "#fee2e2"}, {'range': [40, 70], 'color': "#fef3c7"}, {'range': [70, 100], 'color': '#dcfce7'}]}))
        fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gauge, use_container_width=True)
    with c2:
        st.subheader("Debt-to-Income (DTI) Ratio")
        dti_val = advanced_metrics['dti_ratio']
        fig_dti = go.Figure(go.Indicator(mode="gauge+number", value=dti_val, title={'text': "% of Income"},
            gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#6366f1"}, 'steps': [{'range': [0, 35], 'color': '#dcfce7'}, {'range': [35, 43], 'color': "#fef3c7"}, {'range': [43, 100], 'color': '#fee2e2'}]}))
        fig_dti.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_dti, use_container_width=True)

    st.subheader("Emergency Fund Status")
    coverage = advanced_metrics['emergency_fund_coverage']
    st.progress(min(1.0, coverage / 6.0))
    st.markdown(f"You have **{coverage:.1f} months** of expenses covered. (Target: 6 months)")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Section 3: Expense Analysis ---
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.header("💸 Expense Breakdown")
    expense_df = pd.DataFrame(list(user_data['expenses'].items()), columns=['Category', 'Amount']).sort_values('Amount', ascending=False)
    expense_df = expense_df[expense_df['Amount'] > 0]
    fig_treemap = px.treemap(expense_df, path=['Category'], values='Amount', title='Visualizing Your Spending Categories', color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_treemap.update_layout(margin=dict(t=50, l=10, r=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_treemap, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- NEW Section 4: Investment Center & Market Analysis ---
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.header("🔍 Investment Center & Market Analysis")
    st.info("This section provides simulated real-time data for popular mutual funds to help you make informed decisions.")

    mf_df = get_live_mutual_fund_data()

    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Fund Explorer")
        category = st.selectbox("Select Fund Category", mf_df['Category'].unique())
        
        filtered_funds = mf_df[mf_df['Category'] == category]
        fund_name = st.selectbox("Select Fund", filtered_funds['Fund Name'])
        
        investment_amount = st.number_input("Enter Investment Amount (₹)", 1000, 10000000, 50000, 1000)
        
        selected_fund = mf_df[mf_df['Fund Name'] == fund_name].iloc[0]
        
        st.subheader("Fund Details")
        st.markdown(f"**Risk Level:** `{selected_fund['Risk']}`")
        st.markdown(f"**Rating:** {'★' * selected_fund['Rating']}{'☆' * (5 - selected_fund['Rating'])}")

    with c2:
        st.subheader(f"Simulated Growth of ₹{investment_amount:,.0f} in {fund_name}")
        
        periods = ['1M', '6M', '1Y', '3Y', '5Y']
        returns = [selected_fund['1M Return'], selected_fund['6M Return'], selected_fund['1Y Return'], selected_fund['3Y CAGR'], selected_fund['5Y CAGR']]
        
        final_values = []
        for i, period in enumerate(periods):
            num_years = {'1M': 1/12, '6M': 0.5, '1Y': 1, '3Y': 3, '5Y': 5}[period]
            is_cagr = 'CAGR' in period or 'Y' in period
            if is_cagr:
                final_value = investment_amount * ((1 + returns[i]/100) ** num_years)
            else: # Simple return for periods < 1 year
                final_value = investment_amount * (1 + returns[i]/100)
            final_values.append(final_value)

        gains = [val - investment_amount for val in final_values]
        
        # Store for PDF
        st.session_state.investment_simulation = {
            'fund_name': fund_name, 'amount': investment_amount, 
            '5Y_value': final_values[-1], '5Y_gain': gains[-1]
        }

        fig_growth = go.Figure(data=[
            go.Bar(name='Initial Investment', x=periods, y=[investment_amount]*len(periods), marker_color='#94a3b8'),
            go.Bar(name='Profit', x=periods, y=gains, marker_color='#10b981')
        ])
        fig_growth.update_layout(barmode='stack', title_text='Investment vs. Profit', xaxis_title='Time Period', yaxis_title='Value (₹)', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_growth, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # --- Section 5: Future Projections ---
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.header("💰 Future Projections (SIP)")
    monthly_investment = metrics['desired_investment']
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Your Target Monthly Investment (SIP)", f"₹{monthly_investment:,.0f}")
        proj_years = st.slider("Investment Horizon (Years)", 5, 40, 20, key='sip_years')
    with c2:
        st.metric(" ", " ") # Placeholder for alignment
        proj_return = st.slider("Assumed Annual Return (%)", 5, 20, 12, key='sip_return')
    
    if monthly_investment > 0:
        years = np.arange(0, proj_years + 1)
        values = [investment_projection_calculator(monthly_investment, y, proj_return) for y in years]
        proj_df = pd.DataFrame({'Year': years, 'Projected Value': [v[0] for v in values], 'Total Invested': [v[1] for v in values]})
        
        fig_proj = go.Figure()
        fig_proj.add_trace(go.Scatter(x=proj_df['Year'], y=proj_df['Projected Value'], mode='lines', name='Projected Value', fill='tozeroy', line_color='#6366f1'))
        fig_proj.add_trace(go.Scatter(x=proj_df['Year'], y=proj_df['Total Invested'], mode='lines', name='Amount Invested', line=dict(color='#94a3b8', dash='dash')))
        fig_proj.update_layout(title=f"SIP Growth over {proj_years} years at {proj_return}%", xaxis_title='Years', yaxis_title='Portfolio Value (₹)', legend=dict(x=0.01, y=0.98), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_proj, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Section 6: Action Plan & Download ---
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.header("🎯 Your Action Plan")
    for rec in recommendations:
        st.success(rec)

    st.markdown("---")
    c1, c2 = st.columns([2,1])
    with c1:
        st.subheader("📥 Download Full Report")
        pdf_data = create_pdf_report(metrics, advanced_metrics, recommendations, health_score, user_data, st.session_state.investment_simulation)
        st.download_button("Download as PDF", pdf_data, f"Financial_Report_{datetime.now().strftime('%Y%m%d')}.pdf", "application/pdf")
    with c2:
        if st.button("Start Over & Edit Inputs"):
            st.session_state.report_generated = False
            st.session_state.investment_simulation = {}
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- Main App Router ---
if st.session_state.report_generated:
    analytics_report_page()
else:
    data_entry_page()

