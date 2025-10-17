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
# ... (keep all the imports and setup code above until the navigation section)

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
        if st.button(option, key=f"nav_{i}"):
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
elif st.session_state.current_page == "👨‍💻 About / Developer":
    st.header('👨‍💻 About the Developer')
    
    st.markdown("""
    <div class='developer-section'>
        <h2>Ayush Shukla</h2>
        <p>Full Stack Developer & Financial Technology Enthusiast</p>
        <p>Building intelligent financial solutions to empower better money management</p>
        
        <div class='social-links'>
            <a href='https://github.com/ayushshukla' class='social-link' target='_blank'>
                📱 GitHub
            </a>
            <a href='https://linkedin.com/in/ayushshukla' class='social-link' target='_blank'>
                💼 LinkedIn
            </a>
            <a href='https://twitter.com/ayushshukla' class='social-link' target='_blank'>
                🐦 Twitter
            </a>
            <a href='https://ayushshukla.xyz' class='social-link' target='_blank'>
                🌐 Portfolio
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <h3>🚀 About This App</h3>
            <p>AI Financial Advisor is a comprehensive personal finance management tool that helps you:</p>
            <ul>
                <li>Track income and expenses</li>
                <li>Plan investments and SIPs</li>
                <li>Set and achieve financial goals</li>
                <li>Understand your risk profile</li>
                <li>Generate detailed financial reports</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <h3>🛠️ Technology Stack</h3>
            <p>Built with modern technologies for optimal performance:</p>
            <ul>
                <li><strong>Frontend:</strong> Streamlit, Plotly</li>
                <li><strong>Backend:</strong> Python, Pandas, NumPy</li>
                <li><strong>Data Visualization:</strong> Plotly, Chart.js</li>
                <li><strong>PDF Generation:</strong> ReportLab</li>
                <li><strong>Data Storage:</strong> JSON files</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='financial-sticker'>
        <h3>📞 Get In Touch</h3>
        <p>Have questions, suggestions, or want to collaborate? Feel free to reach out!</p>
        <p>📧 Email: ayush.shukla@example.com</p>
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
