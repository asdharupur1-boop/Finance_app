import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Financial Advisor",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for a more professional look ---
st.markdown("""
<style>
    /* Main container and text styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    /* Metric cards styling */
    .stMetric {
        background-color: #ecf0f1;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #3498db;
    }
    .stMetric:nth-child(2) { border-left-color: #e74c3c; }
    .stMetric:nth-child(3) { border-left-color: #2ecc71; }
    .stMetric .st-emotion-cache-1g6gooi { /* Metric label */
        font-size: 1.1em;
        font-weight: bold;
        color: #34495e;
    }
    /* Section containers */
    .section-container {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)


# --- Financial Analyzer Class (from your notebook) ---
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

    def generate_spending_alerts(self, metrics):
        """Generate alerts for high spending categories and low savings."""
        alerts = []
        expense_ratios = metrics['expense_ratios']
        
        high_spending_threshold = 25
        
        for category, ratio in expense_ratios.items():
            if ratio >= high_spending_threshold:
                alerts.append({
                    'severity': 'HIGH',
                    'message': f"High Spending: Your spending on **{category.replace('_', ' ').title()}** is **{ratio:.1f}%** of your income, which is quite high. Consider reviewing this category for potential savings."
                })
        
        if metrics['savings_rate'] < 10:
            alerts.append({
                'severity': 'HIGH',
                'message': f"Low Savings Rate: You're currently saving only **{metrics['savings_rate']:.1f}%** of your income. Aiming for at least 15-20% is recommended for strong financial health."
            })
        elif metrics['savings_rate'] < 20:
             alerts.append({
                'severity': 'MEDIUM',
                'message': f"Good Start on Savings: Your savings rate is **{metrics['savings_rate']:.1f}%**. Consider pushing this towards 20% or more to accelerate your financial goals."
            })

        if metrics['desired_investment'] > metrics['monthly_savings']:
            shortfall = metrics['desired_investment'] - metrics['monthly_savings']
            alerts.append({
                'severity': 'HIGH',
                'message': f"Investment Shortfall: Your desired investment of **₹{metrics['desired_investment']:,.0f}** is more than your current savings of **₹{metrics['monthly_savings']:,.0f}**. You have a shortfall of **₹{shortfall:,.0f}**."
            })
            
        return alerts

# --- PDF Report Generation ---
class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, 'Your Financial Summary Report', align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')
        
    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, title, ln=1, align='L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Helvetica', '', 11)
        self.multi_cell(0, 8, body, align='L') # FIX: Explicitly set align to 'L'
        self.ln()

def clean_text_for_pdf(text):
    # Remove markdown bold tags and emojis
    text = text.replace('**', '')
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text).strip()

def create_pdf_report(metrics, alerts, recommendations, health_score): # FIX: Changed recommendations_list to recommendations
    pdf = PDF()
    pdf.add_page()
    
    # Developer Details
    pdf.set_font('Helvetica', 'I', 9)
    pdf.cell(0, 5, "Generated by AI Financial Advisor | Developed by Ayush Shukla", ln=1, align='C')
    pdf.cell(0, 5, "Contact: shuklaayush552@gmail.com", ln=1, align='C')
    pdf.ln(10)

    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 10, f"Report generated on: {datetime.now().strftime('%Y-%m-%d')}", ln=1)
    
    pdf.chapter_title("Key Financial Overview")
    metrics_text = (
        f"Monthly Income: INR {metrics.get('monthly_income', 0):,.0f}\n"
        f"Total Monthly Expenses: INR {metrics.get('total_expenses', 0):,.0f}\n"
        f"Monthly Savings: INR {metrics.get('monthly_savings', 0):,.0f}\n"
        f"Savings Rate: {metrics.get('savings_rate', 0):.1f}%\n"
        f"Financial Health Score: {health_score}/100"
    )
    pdf.chapter_body(metrics_text)

    if alerts:
        pdf.chapter_title("Personal Recommender Alerts")
        for alert in alerts:
            message = clean_text_for_pdf(alert['message'])
            pdf.multi_cell(0, 8, f"- {message}", align='L') # FIX: Explicitly set align to 'L'
        pdf.ln()

    pdf.chapter_title("Actionable Recommendations")
    for i, rec in enumerate(recommendations, 1): # FIX: Changed recommendations_list to recommendations
        rec_text = clean_text_for_pdf(rec)
        pdf.multi_cell(0, 8, f"{i}. {rec_text}", align='L') # FIX: Explicitly set align to 'L'
    
    return pdf.output(dest='S').encode('latin-1')

# --- Data & Calculation Functions ---
@st.cache_data
def get_mutual_fund_returns_data():
    mf_data = {
        'Category': ['Large Cap', 'Large Cap', 'Flexi Cap', 'Flexi Cap', 'ELSS', 'ELSS', 
                    'Mid Cap', 'Mid Cap', 'Small Cap', 'Small Cap', 'Hybrid', 'Hybrid',
                    'Debt', 'Debt', 'Index', 'Index'],
        'Fund_Name': ['ABC Bluechip Fund', 'XYZ Large Cap Fund', 'PQR Flexi Cap Fund', 'LMN Dynamic Fund', 'Tax Saver Pro', 'Future Growth ELSS','Mid Cap Opportunities', 'Emerging Stars Fund', 'Small Cap Champion','Micro Marvel Fund', 'Balanced Advantage', 'Hybrid Wealth','Corporate Bond Fund', 'Gilt Fund', 'Nifty 50 Index', 'Sensex Index'],
        '1_Year_Return': [12.5, 11.8, 15.2, 14.7, 16.3, 15.8, 18.9, 20.1, 22.5, 24.3, 11.2, 10.8, 7.8, 8.2, 12.1, 11.9],
        '3_Year_CAGR': [14.2, 13.8, 16.5, 15.9, 17.2, 16.8, 19.5, 20.8, 23.1, 25.2, 12.1, 11.7, 8.5, 8.9, 13.8, 13.5],
        '5_Year_CAGR': [13.8, 13.2, 15.8, 15.2, 16.5, 16.1, 18.2, 19.1, 21.5, 23.8, 11.5, 11.2, 8.2, 8.5, 13.2, 12.9],
        'Risk_Level': ['Medium', 'Medium', 'Medium-High', 'Medium-High', 'High', 'High','High', 'High', 'Very High', 'Very High', 'Low-Medium', 'Low-Medium','Low', 'Low', 'Medium', 'Medium']
    }
    return pd.DataFrame(mf_data)

def investment_projection_calculator(monthly_investment, years, expected_return):
    monthly_rate = expected_return / 100 / 12
    months = years * 12
    future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    total_invested = monthly_investment * months
    estimated_gains = future_value - total_invested
    return future_value, total_invested, estimated_gains

# --- UI Layout ---

# --- Sidebar for User Input ---
with st.sidebar:
    st.image("https://www.svgrepo.com/show/493636/investment.svg", width=80)
    st.title("AI Financial Advisor")
    st.write("Enter your financial details for a personalized analysis.")

    with st.expander("💰 **Monthly Income**", expanded=True):
        monthly_income = st.number_input("Take-Home Income (₹)", min_value=0, value=75000, step=1000)

    with st.expander("💸 **Monthly Expenses**"):
        rent_emi = st.number_input("Rent/EMI", min_value=0, value=20000, step=500)
        loan_repayments = st.number_input("Other Loans", min_value=0, value=5000, step=500)
        utilities = st.number_input("Utilities", min_value=0, value=3000, step=100)
        internet_phone = st.number_input("Internet/Phone", min_value=0, value=1000, step=50)
        insurance = st.number_input("Insurance", min_value=0, value=2000, step=100)
        groceries = st.number_input("Groceries", min_value=0, value=8000, step=200)
        transportation = st.number_input("Transportation", min_value=0, value=4000, step=100)
        dining_entertainment = st.number_input("Dining/Entertainment", min_value=0, value=6000, step=200)
        shopping = st.number_input("Shopping", min_value=0, value=5000, step=200)
        subscriptions = st.number_input("Subscriptions", min_value=0, value=1000, step=50)
        miscellaneous = st.number_input("Miscellaneous", min_value=0, value=2000, step=100)

    with st.expander("📈 **Investment Goal**", expanded=True):
        investment_percentage = st.slider("% of Income to Invest", 0, 100, 20)

    st.markdown("---")
    with st.expander("🔗 **Connect with the Developer**"):
        st.markdown(
            """
            <div style="display: flex; justify-content: space-around; align-items: center; padding: 5px 0;">
                <div style="text-align: left;">
                    <p style="margin: 0; font-weight: bold; font-size: 1em;">Ayush Shukla</p>
                    <p style="margin: 0; font-size: 0.9em; color: #888;">Data Scientist & AI Developer</p>
                </div>
                <div style="display: flex; gap: 15px; align-items: center;">
                    <a href="https://www.linkedin.com/in/ayush-shukla-35a402239/" target="_blank" title="LinkedIn"><img src="https://i.imgur.com/v4pjeS4.png" width="28"></a>
                    <a href="https://github.com/Ayushshukla24" target="_blank" title="GitHub"><img src="https://i.imgur.com/2cn43Xz.png" width="28"></a>
                    <a href="https://ayushshukla-portfolio.netlify.app/" target="_blank" title="Portfolio"><img src="https://i.imgur.com/p1p4i7A.png" width="28"></a>
                    <a href="mailto:shuklaayush552@gmail.com" target="_blank" title="Email"><img src="https://i.imgur.com/P1p8s7a.png" width="28"></a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# --- Main Dashboard ---
st.title("Your Financial Dashboard")
st.markdown("A personalized overview of your financial health, projections, and actionable recommendations.")

if monthly_income == 0:
    st.warning("Please enter your monthly income in the sidebar to get started.")
else:
    # --- Data Processing ---
    user_expenses = {
        'Rent/EMI': rent_emi, 'Loans': loan_repayments, 'Utilities': utilities,
        'Internet/Phone': internet_phone, 'Insurance': insurance, 'Groceries': groceries,
        'Transportation': transportation, 'Dining/Entertainment': dining_entertainment,
        'Shopping': shopping, 'Subscriptions': subscriptions, 'Miscellaneous': miscellaneous
    }
    user_data = { 'monthly_income': monthly_income, 'expenses': user_expenses, 'investment_percentage': investment_percentage }

    analyzer = FinancialAnalyzer(user_data)
    metrics = analyzer.calculate_financial_metrics()
    alerts = analyzer.generate_spending_alerts(metrics)
    
    # --- Key Metrics ---
    st.markdown("###  Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Monthly Income", f"₹{monthly_income:,.0f}")
    col2.metric("💸 Total Expenses", f"₹{metrics['total_expenses']:,.0f}")
    col3.metric("🏦 Monthly Savings", f"₹{metrics['monthly_savings']:,.0f}", delta=f"{metrics['savings_rate']:.1f}% Savings Rate")
    
    st.markdown("<hr>", unsafe_allow_html=True)

    # --- Financial Health & Alerts ---
    col_health, col_alerts = st.columns([1, 2])
    with col_health:
        st.markdown("### Financial Health")
        health_score = min(100, max(0, int(metrics['savings_rate'] * 3.5 + 30)))
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=health_score,
            title={'text': "Health Score"},
            gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#3498db"},
                   'steps': [{'range': [0, 40], 'color': "#e74c3c"}, {'range': [40, 70], 'color': "#f1c40f"}, {'range': [70, 100], 'color': '#2ecc71'}]}))
        fig_gauge.update_layout(height=250, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_alerts:
        st.markdown("### Recommender Alerts")
        if alerts:
            for alert in alerts:
                if alert['severity'] == 'HIGH': st.error(f"**Alert:** {alert['message']}")
                else: st.warning(f"**Suggestion:** {alert['message']}")
        else:
            st.success("Excellent! No critical financial issues detected. Your budget looks healthy.")

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- Financial Breakdown Section ---
    st.markdown("### Financial Breakdown")
    col_waterfall, col_sunburst = st.columns(2)
    
    with col_waterfall:
        st.markdown("##### Monthly Cash Flow (Waterfall)")
        fig_waterfall = go.Figure(go.Waterfall(
            name="Cash Flow", orientation="v",
            measure=["absolute", "relative", "total"],
            x=["Income", "Expenses", "Savings"],
            y=[monthly_income, -metrics['total_expenses'], metrics['monthly_savings']],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker":{"color":"#2ecc71"}},
            decreasing={"marker":{"color":"#e74c3c"}},
            totals={"marker":{"color":"#3498db"}}
        ))
        fig_waterfall.update_layout(title="From Income to Savings", showlegend=False, height=450)
        st.plotly_chart(fig_waterfall, use_container_width=True)

    with col_sunburst:
        st.markdown("##### Expense Categories (Sunburst)")
        fixed_expenses = {'Rent/EMI': rent_emi, 'Loans': loan_repayments, 'Utilities': utilities, 'Internet/Phone': internet_phone, 'Insurance': insurance, 'Subscriptions': subscriptions}
        variable_expenses = {'Groceries': groceries, 'Transportation': transportation, 'Dining/Entertainment': dining_entertainment, 'Shopping': shopping, 'Miscellaneous': miscellaneous}
        
        labels = ["Expenses"]
        parents = [""]
        values = [0] # Placeholder for the root
        
        for cat_name, cat_expenses in [("Fixed", fixed_expenses), ("Variable", variable_expenses)]:
            labels.append(cat_name)
            parents.append("Expenses")
            values.append(sum(cat_expenses.values()))
            for name, value in cat_expenses.items():
                if value > 0:
                    labels.append(name)
                    parents.append(cat_name)
                    values.append(value)

        fig_sunburst = go.Figure(go.Sunburst(labels=labels, parents=parents, values=values, branchvalues="total"))
        fig_sunburst.update_layout(margin=dict(t=20, l=10, r=10, b=10), title="Fixed vs. Variable Spending", height=450)
        st.plotly_chart(fig_sunburst, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- Investment Center (NEW SECTION) ---
    st.markdown("### 📊 Investment Center")
    mf_df = get_mutual_fund_returns_data()
    category_performance = mf_df.groupby('Category')[['1_Year_Return', '3_Year_CAGR', '5_Year_CAGR']].mean().reset_index()

    fig_mf = go.Figure()
    for col in ['1_Year_Return', '3_Year_CAGR', '5_Year_CAGR']:
        fig_mf.add_trace(go.Bar(
            x=category_performance['Category'],
            y=category_performance[col],
            name=col.replace('_', ' ')
        ))
    fig_mf.update_layout(
        title='Average Mutual Fund Returns by Category (Informational)',
        xaxis_title='Fund Category',
        yaxis_title='Average Annualized Return (%)',
        barmode='group',
        legend_title='Return Period'
    )
    st.plotly_chart(fig_mf, use_container_width=True)


    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- Projections & Recommendations ---
    st.markdown("### 💰 Investment & Growth")
    proj_col1, proj_col2 = st.columns([1, 2])

    with proj_col1:
        st.markdown("##### Projection Calculator")
        monthly_investment = metrics['desired_investment']
        st.metric("Desired Monthly Investment", f"₹{monthly_investment:,.0f}")
        
        proj_years = st.slider("Horizon (Years)", 5, 40, 20, key="proj_years_slider")
        proj_return = st.slider("Expected Return (%)", 5, 20, 12, key="proj_return_slider")
        
        st.markdown("##### 💡 Recommendations")
        recommendations = []
        if metrics['savings_rate'] < 20: recommendations.append("🚀 **Boost Savings:** Your rate is below 20%. Review variable expenses.")
        if metrics['desired_investment'] > metrics['monthly_savings']: recommendations.append(f"🔧 **Bridge the Gap:** Increase savings by **₹{metrics['desired_investment'] - metrics['monthly_savings']:,.0f}** to meet your goal.")
        
        if metrics['expense_ratios']:
            high_expense = max(metrics['expense_ratios'], key=metrics['expense_ratios'].get)
            if metrics['expense_ratios'][high_expense] > 20: recommendations.append(f"📉 **Review Spending:** Your top expense is **{high_expense.replace('_', ' ').title()}**. Start there for savings.")
        
        recommendations.append("📊 **Diversify:** Consider a mix of Equity and Debt funds based on your risk tolerance.")
        recommendations.append("🧠 **Pay Yourself First:** Automate your investments with a Systematic Investment Plan (SIP).")
        
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"_{i}. {rec}_")

    with proj_col2:
        if monthly_investment > 0:
            future_val, total_inv, gains = investment_projection_calculator(monthly_investment, proj_years, proj_return)
            st.markdown(f"##### Portfolio Growth Over **{proj_years} years** at **{proj_return}%** return")
            
            years = np.arange(0, proj_years + 1)
            values = [investment_projection_calculator(monthly_investment, y, proj_return)[0] for y in years]
            invested = [monthly_investment * y * 12 for y in years]
            proj_df = pd.DataFrame({'Year': years, 'Projected Value': values, 'Total Invested': invested})
            
            fig_proj = go.Figure()
            fig_proj.add_trace(go.Scatter(x=proj_df['Year'], y=proj_df['Projected Value'], mode='lines', name='Projected Value', fill='tozeroy', line_color='#3498db'))
            fig_proj.add_trace(go.Scatter(x=proj_df['Year'], y=proj_df['Total Invested'], mode='lines', name='Amount Invested', line=dict(color='#95a5a6', dash='dash')))
            fig_proj.update_layout(xaxis_title='Years', yaxis_title='Value (₹)', legend=dict(x=0.01, y=0.98))
            st.plotly_chart(fig_proj, use_container_width=True)
        else:
            st.warning("Increase your savings or investment % to see projections.")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- Download Report Section ---
    st.markdown("### 📥 Download Your Report")
    pdf_data = create_pdf_report(metrics, alerts, recommendations, health_score)
    st.download_button(
        label="Download Full Financial Report (PDF)",
        data=pdf_data,
        file_name=f"Financial_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf"
    )

