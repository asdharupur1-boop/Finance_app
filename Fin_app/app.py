import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
import re
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Financial Advisor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- NEW Custom CSS for a "Modern Minimalist" Theme ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Main container and background */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 5rem;
        padding-right: 5rem;
        background-color: #f0f2f6; 
    }
    
    /* Font styles */
    body, h1, h2, h3, h4, h5, h6, p, .stMarkdown {
        font-family: 'Inter', sans-serif;
        color: #1e293b; /* Dark Slate Gray for text */
    }
    h1 {
        font-weight: 700;
        color: #0f172a;
    }
    h2 {
        border-bottom: 2px solid #3b82f6;
        padding-bottom: 5px;
        margin-top: 40px;
    }
    
    /* Metric Card Styling */
    .metric-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    /* Button Styling */
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 1.1em;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2563eb;
    }
    
    /* Animation for report sections */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .report-section {
        animation: fadeIn 0.8s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'report_generated' not in st.session_state:
    st.session_state.report_generated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# --- Financial Analyzer Class ---
class FinancialAnalyzer:
    """A class to analyze user's financial data."""
    def __init__(self, user_data):
        self.user_data = user_data
        self.monthly_income = user_data.get('monthly_income', 0)
        self.expenses = user_data.get('expenses', {})
        self.investment_pct = user_data.get('investment_percentage', 0)

    def calculate_financial_metrics(self):
        """Calculate key financial metrics."""
        total_expenses = sum(self.expenses.values())
        monthly_savings = self.monthly_income - total_expenses
        desired_investment = self.monthly_income * (self.investment_pct / 100)
        savings_rate = (monthly_savings / self.monthly_income) * 100 if self.monthly_income > 0 else 0
        expense_ratios = {category: (amount / self.monthly_income) * 100 if self.monthly_income > 0 else 0
                         for category, amount in self.expenses.items()}
        
        return {
            'total_expenses': total_expenses,
            'monthly_savings': monthly_savings,
            'desired_investment': desired_investment,
            'savings_rate': savings_rate,
            'expense_ratios': expense_ratios
        }

    def generate_recommendations(self, metrics):
        """Generate actionable recommendations."""
        recommendations = []
        if metrics['savings_rate'] < 15:
            recommendations.append("🚀 **Prioritize Savings:** Your savings rate is below the recommended 15-20%. Focus on reducing variable expenses like 'Dining Out' or 'Shopping' to free up more cash for your goals.")
        elif metrics['savings_rate'] < 30:
             recommendations.append("👍 **Good Savings Foundation:** You're on the right track. Consider automating a slightly higher portion of your income towards investments to accelerate wealth building.")
        else:
            recommendations.append("🎉 **Excellent Saver:** Your high savings rate is a powerful wealth-building engine. Ensure these savings are invested effectively to maximize their growth potential.")

        if metrics['desired_investment'] > metrics['monthly_savings']:
            shortfall = metrics['desired_investment'] - metrics['monthly_savings']
            recommendations.append(f"🔧 **Bridge the Investment Gap:** There's a **₹{shortfall:,.0f}** gap between your goal and your savings. A detailed budget review can help close this.")
        
        if metrics['expense_ratios']:
            high_expense = max(metrics['expense_ratios'], key=metrics['expense_ratios'].get)
            if metrics['expense_ratios'][high_expense] > 20: 
                recommendations.append(f"🔍 **Expense Deep-Dive:** Your highest expense category is **{high_expense.replace('_', ' ').title()}**. Scrutinizing this area could unlock significant savings.")
        
        recommendations.append("🤖 **Automate Your Wealth:** Set up a Systematic Investment Plan (SIP) to invest your desired amount automatically each month. This builds discipline and leverages dollar-cost averaging.")
        recommendations.append("🛡️ **Build a Safety Net:** Ensure you have an emergency fund covering 3-6 months of essential living expenses before making aggressive investments.")

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
    text = text.replace('**', '').replace("🚀", "").replace("👍", "").replace("🎉", "").replace("🔧", "").replace("🔍", "").replace("🤖", "").replace("🛡️", "")
    return text.strip()

def create_pdf_report(metrics, recommendations, health_score, user_data):
    pdf = PDF()
    pdf.add_page()
    
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 10, f"Report for: User | Date: {datetime.now().strftime('%Y-%m-%d')}", ln=1)
    
    pdf.chapter_title("Key Financial Overview")
    metrics_text = (
        f"Monthly Income: INR {user_data['monthly_income']:,.0f}\n"
        f"Total Monthly Expenses: INR {metrics['total_expenses']:,.0f}\n"
        f"Monthly Savings: INR {metrics['monthly_savings']:,.0f}\n"
        f"Savings Rate: {metrics['savings_rate']:.1f}%\n"
        f"Financial Health Score: {health_score}/100"
    )
    pdf.chapter_body(metrics_text)

    pdf.chapter_title("Actionable Recommendations")
    for i, rec in enumerate(recommendations, 1):
        rec_text = clean_text_for_pdf(rec)
        pdf.multi_cell(0, 5, f"{i}. {rec_text}", align='L')
    
    return pdf.output(dest='S').encode('latin-1')

# --- Data & Calculation Functions ---
@st.cache_data
def get_mutual_fund_returns_data():
    mf_data = {'Category': ['Large Cap', 'Flexi Cap', 'ELSS', 'Mid Cap', 'Small Cap', 'Hybrid','Debt', 'Index'],'1_Year_Return': [12.15, 14.95, 16.05, 19.50, 23.40, 11.00, 8.00, 12.00],'3_Year_CAGR': [14.00, 16.20, 17.00, 20.15, 24.15, 11.90, 8.70, 13.65],'5_Year_CAGR': [13.50, 15.50, 16.30, 18.65, 22.65, 11.35, 8.35, 13.05],'Risk_Level': ['Medium', 'Medium-High', 'High', 'High', 'Very High', 'Low-Medium','Low', 'Medium']}
    return pd.DataFrame(mf_data)

def investment_projection_calculator(monthly_investment, years, expected_return):
    monthly_rate = expected_return / 100 / 12
    months = years * 12
    if monthly_rate > 0:
        future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    else:
        future_value = monthly_investment * months
    total_invested = monthly_investment * months
    estimated_gains = future_value - total_invested
    return future_value, total_invested, estimated_gains

# --- UI Application Flow ---

def data_entry_page():
    """Page for user to input their financial data."""
    st.title("Welcome to your AI Financial Advisor 🤖")
    st.markdown("Let's start by gathering some basic financial details to generate your personalized report. All data is processed in-memory and is not stored.")
    
    st.markdown("---")
    
    # --- Input Form ---
    st.header("Step 1: Your Financial Snapshot")
    
    with st.form(key='financial_form'):
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("💰 Income")
            monthly_income = st.number_input("Monthly Take-Home Income (₹)", min_value=0, value=75000, step=1000)
            
            st.subheader("📈 Investment Goal")
            investment_percentage = st.slider("% of Income to Invest", 0, 100, 20, help="What percentage of your income do you aim to invest each month?")

        with c2:
            st.subheader("💸 Expenses")
            st.write("Enter your typical monthly expenses.")
            
            # Grouping expenses for better UX
            exp_c1, exp_c2 = st.columns(2)
            with exp_c1:
                rent_emi = st.number_input("Rent/EMI", min_value=0, value=20000, step=500)
                groceries = st.number_input("Groceries", min_value=0, value=8000, step=200)
                utilities = st.number_input("Utilities (Electricity, Water)", min_value=0, value=3000, step=100)
                transportation = st.number_input("Transportation", min_value=0, value=4000, step=100)
                insurance = st.number_input("Insurance Premiums", min_value=0, value=2000, step=100)
            with exp_c2:
                loan_repayments = st.number_input("Other Loan Repayments", min_value=0, value=5000, step=500)
                dining_entertainment = st.number_input("Dining & Entertainment", min_value=0, value=6000, step=200)
                shopping = st.number_input("Shopping", min_value=0, value=5000, step=200)
                internet_phone = st.number_input("Internet & Phone Bills", min_value=0, value=1000, step=50)
                miscellaneous = st.number_input("Miscellaneous", min_value=0, value=2000, step=100)

        submitted = st.form_submit_button(label="✨ Generate My Financial Report")

    if submitted:
        if monthly_income == 0:
            st.error("Monthly Income cannot be zero. Please enter a valid amount to generate the report.")
        else:
            st.session_state.user_data = {
                'monthly_income': monthly_income,
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
    """Page to display the full financial analysis report."""
    user_data = st.session_state.user_data
    analyzer = FinancialAnalyzer(user_data)
    metrics = analyzer.calculate_financial_metrics()
    recommendations = analyzer.generate_recommendations(metrics)
    health_score = min(100, max(0, int(metrics['savings_rate'] * 3.5 + 30)))
    
    st.title("Your Personalized Financial Report")

    # --- Section 1: At-a-Glance Summary ---
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.header("📊 At-a-Glance Summary")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><h4>💰 Monthly Income</h4><h3>₹{user_data["monthly_income"]:,.0f}</h3></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><h4>💸 Total Expenses</h4><h3>₹{metrics["total_expenses"]:,.0f}</h3></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><h4>🏦 Monthly Savings</h4><h3>₹{metrics["monthly_savings"]:,.0f}</h3><p style="color: #2ecc71; font-weight: bold;">{metrics["savings_rate"]:.1f}% Savings Rate</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Section 2: Financial Health & Cash Flow ---
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.header("❤️ Financial Health Analysis")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Health Score")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=health_score,
            title={'text': "Overall Score"},
            gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#3b82f6"},
                   'steps': [{'range': [0, 40], 'color': "#ef4444"}, {'range': [40, 70], 'color': "#f59e0b"}, {'range': [70, 100], 'color': '#10b981'}]}))
        fig_gauge.update_layout(height=280, margin=dict(l=10, r=10, t=60, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gauge, use_container_width=True)
    with c2:
        st.subheader("Monthly Cash Flow")
        fig_waterfall = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "total"],
            x=["Income", "Expenses", "Savings"],
            y=[user_data['monthly_income'], -metrics['total_expenses'], metrics['monthly_savings']],
            connector={"line": {"color": "#64748b"}},
            increasing={"marker":{"color":"#10b981"}},
            decreasing={"marker":{"color":"#ef4444"}},
            totals={"marker":{"color":"#3b82f6"}}
        ))
        fig_waterfall.update_layout(showlegend=False, height=280, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_waterfall, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Section 3: Expense Analysis ---
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.header("💸 Expense Breakdown")
    
    expense_df = pd.DataFrame(list(user_data['expenses'].items()), columns=['Category', 'Amount']).sort_values('Amount', ascending=False)
    expense_df = expense_df[expense_df['Amount'] > 0]

    fig_treemap = px.treemap(expense_df, path=['Category'], values='Amount',
                             title='Visualizing Your Spending Categories',
                             color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_treemap.update_layout(margin=dict(t=50, l=10, r=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_treemap, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Section 4: Investment Center ---
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.header("📈 Investment Center")
    mf_df = get_mutual_fund_returns_data()
    fig_mf = go.Figure()
    fig_mf.add_trace(go.Bar(
        x=mf_df['Category'], y=mf_df['5_Year_CAGR'], name='5-Year Avg. Return',
        marker_color='#3b82f6'
    ))
    fig_mf.update_layout(
        title='Historical Mutual Fund Performance by Category (CAGR)',
        xaxis_title='Fund Category', yaxis_title='5-Year Average Return (%)',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_mf, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Section 5: Future Projections ---
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.header("💰 Future Projections")
    c1, c2 = st.columns([1,2])
    with c1:
        st.subheader("Growth Calculator")
        monthly_investment = metrics['desired_investment']
        st.metric("Your Target Monthly Investment", f"₹{monthly_investment:,.0f}")
        
        proj_years = st.slider("Investment Horizon (Years)", 5, 40, 20)
        proj_return = st.slider("Assumed Annual Return (%)", 5, 20, 12)
    
    with c2:
        if monthly_investment > 0:
            years = np.arange(0, proj_years + 1)
            values = [investment_projection_calculator(monthly_investment, y, proj_return)[0] for y in years]
            invested = [monthly_investment * y * 12 for y in years]
            proj_df = pd.DataFrame({'Year': years, 'Projected Value': values, 'Total Invested': invested})
            
            fig_proj = go.Figure()
            fig_proj.add_trace(go.Scatter(x=proj_df['Year'], y=proj_df['Projected Value'], mode='lines', name='Projected Value', fill='tozeroy', line_color='#3b82f6'))
            fig_proj.add_trace(go.Scatter(x=proj_df['Year'], y=proj_df['Total Invested'], mode='lines', name='Amount Invested', line=dict(color='#94a3b8', dash='dash')))
            fig_proj.update_layout(title=f"Portfolio Growth over {proj_years} years at {proj_return}%", xaxis_title='Years', yaxis_title='Portfolio Value (₹)', legend=dict(x=0.01, y=0.98), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_proj, use_container_width=True)
        else:
            st.info("Your desired investment is currently zero. Increase your savings or investment goal to see projections.")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Section 6: Action Plan & Download ---
    st.markdown('<div class="report-section">', unsafe_allow_html=True)
    st.header("🎯 Your Action Plan")
    for rec in recommendations:
        st.info(rec)

    st.markdown("---")
    c1, c2 = st.columns([2,1])
    with c1:
        st.subheader("📥 Download Full Report")
        pdf_data = create_pdf_report(metrics, recommendations, health_score, user_data)
        st.download_button(
            label="Download as PDF",
            data=pdf_data,
            file_name=f"Financial_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
    with c2:
        if st.button("Start Over & Edit Inputs"):
            st.session_state.report_generated = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- Main App Router ---
if st.session_state.report_generated:
    analytics_report_page()
else:
    data_entry_page()

