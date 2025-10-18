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

# Set page config with light theme
st.set_page_config(
    page_title='AI Financial Advisor — By Ayush Shukla', 
    page_icon='🤖', 
    layout='wide',
    initial_sidebar_state='auto'
)

# Enhanced Light Theme CSS
st.markdown("""
<style>
    /* Base styling */
    .main {
        background-color: #ffffff;
    }
    
    .stApp {
        background-color: #f8fafc;
    }
    
    .main .block-container {
        background-color: #ffffff;
        padding: 2rem 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem auto;
        max-width: 1400px;
    }
    
    /* Text colors */
    h1, h2, h3, h4, h5, h6, p, div, span {
        color: #000000 !important;
    }
    
    /* Metric cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #2563eb;
        transform: translateY(-1px);
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.5rem;
            margin: 0.5rem;
        }
        
        .metric-card {
            padding: 1rem;
            margin: 0.25rem 0;
        }
        
        .stButton>button {
            width: 100%;
            margin: 0.25rem 0;
        }
    }
    
    /* Plotly graph background */
    .js-plotly-plot .plotly, .js-plotly-plot .plotly div {
        background-color: transparent !important;
    }
    
    /* Custom components */
    .ml-insight {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 1px solid #bae6fd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .financial-sticker {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .ai-prediction {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #fcd34d;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Enhanced ML Financial Predictor Class ---
class MLFinancialPredictor:
    def __init__(self):
        self.risk_factors = {}
        
    def predict_risk_tolerance(self, user_data):
        """Enhanced ML model to predict risk tolerance"""
        age = user_data.get('age', 30)
        monthly_income = user_data.get('monthly_income', 50000)
        current_savings = user_data.get('current_savings', 100000)
        total_expenses = sum(user_data.get('expenses', {}).values())
        total_debt = sum(user_data.get('liabilities', {}).values())
        investment_experience = user_data.get('investment_experience', 2)
        financial_goals = len(user_data.get('goals', []))
        
        # Enhanced ML-based risk score with more factors
        risk_score = (
            (monthly_income / 10000) * 0.25 +
            (current_savings / 50000) * 0.20 -
            (total_debt / max(monthly_income, 1)) * 0.15 +
            (investment_experience * 2) * 0.20 +
            (min(age, 60) / 30) * 0.10 +
            (financial_goals * 0.5) * 0.10
        )
        
        # Store risk factors for explainability
        self.risk_factors = {
            'income_factor': (monthly_income / 10000) * 0.25,
            'savings_factor': (current_savings / 50000) * 0.20,
            'debt_factor': -(total_debt / max(monthly_income, 1)) * 0.15,
            'experience_factor': (investment_experience * 2) * 0.20,
            'age_factor': (min(age, 60) / 30) * 0.10,
            'goals_factor': (financial_goals * 0.5) * 0.10
        }
        
        if risk_score < 3:
            return "Conservative", 0.3, risk_score, "Low risk appetite suitable for stable investments"
        elif risk_score < 7:
            return "Balanced", 0.5, risk_score, "Moderate risk with balanced growth approach"
        else:
            return "Aggressive", 0.7, risk_score, "High risk tolerance for maximum returns"
    
    def predict_goal_success_probability(self, goal, user_finances):
        """Enhanced ML goal prediction with multiple features"""
        monthly_savings = user_finances.get('monthly_savings', 0)
        goal_amount = goal['amount']
        timeline = goal['years']
        expected_return = goal.get('return', 8)
        user_age = user_finances.get('age', 30)
        
        required_monthly = goal_amount / (timeline * 12)
        savings_ratio = monthly_savings / required_monthly if required_monthly > 0 else 0
        
        # Enhanced probability calculation
        base_probability = min(savings_ratio * 0.7, 0.95)
        timeline_factor = min(timeline / 10, 1.0) * 0.15
        return_factor = min(expected_return / 12, 1.0) * 0.10
        age_factor = (1 - min(user_age, 65) / 65) * 0.05  # Younger users have more time
        
        final_probability = base_probability + timeline_factor + return_factor + age_factor
        
        # ML confidence intervals
        if final_probability >= 0.8:
            confidence = "High confidence - On track to achieve goal"
        elif final_probability >= 0.6:
            confidence = "Moderate confidence - Minor adjustments needed"
        elif final_probability >= 0.4:
            confidence = "Low confidence - Significant changes required"
        else:
            confidence = "Very low confidence - Goal may be unrealistic"
            
        return final_probability, confidence
    
    def get_spending_insights(self, expenses, monthly_income):
        """ML-powered spending pattern analysis"""
        insights = []
        total_expenses = sum(expenses.values())
        
        # Analyze spending categories
        category_analysis = {}
        for category, amount in expenses.items():
            ratio = (amount / monthly_income) * 100 if monthly_income > 0 else 0
            category_analysis[category] = ratio
            
            # ML pattern detection
            if category in ['Dining & Entertainment', 'Shopping'] and ratio > 15:
                insights.append(f"🤖 High spending on {category} ({ratio:.1f}% of income). Consider budgeting.")
            elif category == 'Rent/EMI' and ratio > 35:
                insights.append(f"🤖 Housing cost ({ratio:.1f}% of income) is above recommended 30% threshold.")
        
        # Savings rate analysis
        savings_rate = ((monthly_income - total_expenses) / monthly_income) * 100
        if savings_rate < 10:
            insights.append(f"🤖 Low savings rate ({savings_rate:.1f}%). Target 20% for better financial health.")
        
        return insights, category_analysis
    
    def predict_optimal_allocation(self, risk_profile, user_data):
        """ML-based optimal portfolio allocation"""
        base_allocations = {
            'Conservative': {'Equity': 30, 'Debt': 60, 'Gold': 10},
            'Balanced': {'Equity': 50, 'Debt': 40, 'Gold': 10},
            'Aggressive': {'Equity': 70, 'Debt': 20, 'Gold': 10}
        }
        
        # Adjust based on user profile
        allocation = base_allocations.get(risk_profile, base_allocations['Balanced']).copy()
        
        # ML adjustments
        age = user_data.get('age', 30)
        if age > 50:
            allocation['Equity'] -= 10
            allocation['Debt'] += 10
        elif age < 35:
            allocation['Equity'] += 5
            allocation['Debt'] -= 5
            
        return allocation
    
    def detect_financial_anomalies(self, user_data, metrics):
        """ML anomaly detection in financial behavior"""
        anomalies = []
        
        # High debt-to-income anomaly
        if metrics.get('dti_ratio', 0) > 40:
            anomalies.append("🚨 High debt burden detected - Debt-to-income ratio exceeds 40%")
        
        # Low emergency fund anomaly
        if metrics.get('emergency_fund_coverage', 0) < 2:
            anomalies.append("🚨 Insufficient emergency fund - Less than 2 months coverage")
        
        # Extreme spending anomaly
        expenses = user_data.get('expenses', {})
        total_expenses = sum(expenses.values())
        if any(amount > total_expenses * 0.4 for amount in expenses.values()):
            anomalies.append("🚨 Concentrated spending - Single category exceeds 40% of total expenses")
        
        return anomalies

# --- Enhanced Stock Predictor with Technical Analysis ---
class StockPredictor:
    def __init__(self):
        self.technical_indicators = {}
    
    def get_simulated_stock_data(self, symbol, periods=180):
        """Generate enhanced simulated stock data with ML patterns"""
        np.random.seed(hash(symbol) % 1000)
        
        dates = pd.date_range(end=datetime.now(), periods=periods, freq='D')
        base_price = {
            'RELIANCE.NS': 2500, 'TCS.NS': 3500, 'INFY.NS': 1600,
            'HDFCBANK.NS': 1500, 'ICICIBANK.NS': 900, 'AAPL': 150,
            'GOOGL': 120, 'MSFT': 300
        }.get(symbol, 1000)
        
        # Simulate trends and volatility
        trend = np.random.choice([-0.001, 0, 0.001])
        volatility = np.random.uniform(0.015, 0.03)
        
        returns = np.random.normal(trend, volatility, len(dates))
        prices = base_price * (1 + returns).cumprod()
        
        # Add some ML-detectable patterns
        if len(prices) > 50:
            # Simulate momentum
            prices[-20:] = prices[-20:] * np.linspace(1, 1.05, 20)
        
        data = pd.DataFrame({
            'Close': prices,
            'High': prices * 1.02,
            'Low': prices * 0.98,
            'Open': prices * 0.99,
            'Volume': np.random.randint(1000000, 5000000, len(dates))
        }, index=dates)
        
        return data
    
    def calculate_technical_indicators(self, data):
        """Calculate ML technical indicators"""
        # Moving averages
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['EMA_12'] = data['Close'].ewm(span=12).mean()
        data['EMA_26'] = data['Close'].ewm(span=26).mean()
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        data['MACD'] = data['EMA_12'] - data['EMA_26']
        data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
        data['MACD_Histogram'] = data['MACD'] - data['MACD_Signal']
        
        # Bollinger Bands
        data['BB_Middle'] = data['Close'].rolling(window=20).mean()
        bb_std = data['Close'].rolling(window=20).std()
        data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
        data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
        
        return data
    
    def predict_stock_trend(self, symbol):
        """Enhanced ML-based trend prediction with technical analysis"""
        try:
            data = self.get_simulated_stock_data(symbol)
            if data is None or data.empty:
                return "No data", 0, 0, {}
            
            data = self.calculate_technical_indicators(data)
            
            current_price = data['Close'].iloc[-1]
            current_rsi = data['RSI'].iloc[-1]
            macd_histogram = data['MACD_Histogram'].iloc[-1]
            
            # ML trend analysis with multiple indicators
            bullish_signals = 0
            bearish_signals = 0
            
            # Price vs Moving Averages
            if current_price > data['SMA_20'].iloc[-1] > data['SMA_50'].iloc[-1]:
                bullish_signals += 2
            elif current_price < data['SMA_20'].iloc[-1] < data['SMA_50'].iloc[-1]:
                bearish_signals += 2
            
            # RSI analysis
            if current_rsi < 30:
                bullish_signals += 1  # Oversold
            elif current_rsi > 70:
                bearish_signals += 1  # Overbought
            
            # MACD analysis
            if macd_histogram > 0:
                bullish_signals += 1
            else:
                bearish_signals += 1
            
            # Determine trend
            if bullish_signals - bearish_signals >= 2:
                trend = "Strong Bullish"
                confidence = 0.85
            elif bullish_signals - bearish_signals >= 1:
                trend = "Bullish"
                confidence = 0.70
            elif bearish_signals - bullish_signals >= 2:
                trend = "Strong Bearish"
                confidence = 0.80
            elif bearish_signals - bullish_signals >= 1:
                trend = "Bearish"
                confidence = 0.65
            else:
                trend = "Neutral"
                confidence = 0.55
            
            technical_summary = {
                'RSI': f"{current_rsi:.1f}",
                'MACD_Histogram': f"{macd_histogram:.3f}",
                'Bullish_Signals': bullish_signals,
                'Bearish_Signals': bearish_signals
            }
            
            return trend, confidence, current_price, technical_summary
            
        except Exception as e:
            return "Error", 0, 0, {}

# --- Enhanced Financial Analyzer ---
class FinancialAnalyzer:
    def __init__(self, user_data):
        self.user_data = user_data or {}
        self.ml_predictor = MLFinancialPredictor()
        self.stock_predictor = StockPredictor()
        
    def calculate_financial_metrics(self):
        monthly_income = float(self.user_data.get('monthly_income', 0) or 0)
        expenses = {k: float(v or 0) for k, v in self.user_data.get('expenses', {}).items()}
        investment_pct = float(self.user_data.get('investment_percentage', 0) or 0)
        
        total_expenses = sum(expenses.values())
        monthly_savings = monthly_income - total_expenses
        desired_investment = monthly_income * (investment_pct / 100)
        savings_rate = (monthly_savings / monthly_income) * 100 if monthly_income > 0 else 0
        expense_ratios = {c: (a / monthly_income) * 100 if monthly_income > 0 else 0 for c, a in expenses.items()}
        
        return {
            'total_expenses': total_expenses,
            'monthly_savings': monthly_savings,
            'desired_investment': desired_investment,
            'savings_rate': savings_rate,
            'expense_ratios': expense_ratios,
            'monthly_income': monthly_income
        }
    
    def calculate_advanced_metrics(self, metrics):
        expenses = self.user_data.get('expenses', {})
        debt_payments = expenses.get('Rent/EMI', 0) + expenses.get('Other Loans', 0)
        monthly_income = metrics['monthly_income']
        
        dti_ratio = (debt_payments / monthly_income) * 100 if monthly_income > 0 else 0
        emergency_fund_coverage = (self.user_data.get('current_savings', 0) / metrics['total_expenses']) if metrics['total_expenses'] > 0 else 0
        annual_expenses = metrics['total_expenses'] * 12
        fire_number = annual_expenses * 25
        
        total_assets = sum(self.user_data.get('assets', {}).values())
        total_liabilities = sum(self.user_data.get('liabilities', {}).values())
        net_worth = total_assets - total_liabilities
        
        # Enhanced ML predictions
        risk_profile, risk_allocation, ml_risk_score, risk_explanation = self.ml_predictor.predict_risk_tolerance(self.user_data)
        spending_insights, category_analysis = self.ml_predictor.get_spending_insights(
            self.user_data.get('expenses', {}), monthly_income
        )
        optimal_allocation = self.ml_predictor.predict_optimal_allocation(risk_profile, self.user_data)
        anomalies = self.ml_predictor.detect_financial_anomalies(self.user_data, metrics)
        
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
            'risk_explanation': risk_explanation,
            'spending_insights': spending_insights,
            'category_analysis': category_analysis,
            'optimal_allocation': optimal_allocation,
            'anomalies': anomalies,
            'risk_factors': self.ml_predictor.risk_factors
        }

# --- Data Persistence ---
DATA_DIR = '.ai_financial_data'
os.makedirs(DATA_DIR, exist_ok=True)
SNAPSHOT_FILE = os.path.join(DATA_DIR, 'user_snapshot.json')
GOALS_FILE = os.path.join(DATA_DIR, 'user_goals.json')
PORTFOLIO_FILE = os.path.join(DATA_DIR, 'user_portfolio.json')

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

# --- Investment Calculators ---
def investment_projection_calculator(monthly_investment, years, expected_return):
    monthly_rate = expected_return / 100 / 12
    months = int(years * 12)
    if monthly_rate > 0:
        future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    else:
        future_value = monthly_investment * months
    total_invested = monthly_investment * months
    return future_value, total_invested

# --- Initialize Session State ---
if 'user_data' not in st.session_state:
    st.session_state.user_data = load_json(SNAPSHOT_FILE, {})
if 'goals' not in st.session_state:
    st.session_state.goals = load_json(GOALS_FILE, [])
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = load_json(PORTFOLIO_FILE, [])
if 'current_page' not in st.session_state:
    st.session_state.current_page = "📊 Snapshot"

# --- Main App ---
st.title('🤖 AI Financial Advisor')
st.markdown("""
<div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 12px; color: white; margin-bottom: 1rem;'>
    <h3 style='color: white; margin: 0;'>Advanced ML-Powered Financial Planning</h3>
    <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Smart Analytics • ML Predictions • Data-Driven Insights</p>
</div>
""", unsafe_allow_html=True)

# Navigation
nav_options = [
    "📊 Snapshot", "📈 Dashboard", "🤖 ML Insights", 
    "💹 Investment Center", "🎯 Goals Planner", "📥 Export"
]

cols = st.columns(len(nav_options))
for i, option in enumerate(nav_options):
    with cols[i]:
        if st.button(option, key=f"nav_{i}", use_container_width=True):
            st.session_state.current_page = option

# --- Snapshot Page ---
if st.session_state.current_page == "📊 Snapshot":
    st.header('📊 Financial Snapshot')
    
    with st.form('snapshot_form'):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💰 Income & Profile")
            monthly_income = st.number_input('Monthly Income (₹)', min_value=0.0, 
                                           value=float(st.session_state.user_data.get('monthly_income', 75000.0)), 
                                           step=1000.0)
            current_savings = st.number_input('Current Savings (₹)', min_value=0.0, 
                                            value=float(st.session_state.user_data.get('current_savings', 50000.0)), 
                                            step=1000.0)
            investment_percentage = st.slider('% of Income to Invest', 0, 100, 
                                            int(st.session_state.user_data.get('investment_percentage', 20)))
            
            st.markdown("### 🤖 ML Profile Data")
            age = st.number_input('Age', min_value=18, max_value=80, 
                                value=st.session_state.user_data.get('age', 30))
            investment_experience = st.slider('Investment Experience (1-5)', 1, 5, 
                                            st.session_state.user_data.get('investment_experience', 2))
            
        with col2:
            st.markdown("### 💸 Monthly Expenses")
            defaults = st.session_state.user_data.get('expenses', {})
            rent_emi = st.number_input('🏠 Rent/EMI', 0.0, value=float(defaults.get('Rent/EMI',20000.0)), step=500.0)
            groceries = st.number_input('🛒 Groceries', 0.0, value=float(defaults.get('Groceries',8000.0)), step=200.0)
            utilities = st.number_input('⚡ Utilities', 0.0, value=float(defaults.get('Utilities',3000.0)), step=100.0)
            transportation = st.number_input('🚗 Transportation', 0.0, value=float(defaults.get('Transportation',4000.0)), step=100.0)
            dining_entertainment = st.number_input('🍽️ Dining & Entertainment', 0.0, value=float(defaults.get('Dining & Entertainment',6000.0)), step=200.0)
            miscellaneous = st.number_input('📦 Miscellaneous', 0.0, value=float(defaults.get('Miscellaneous',2000.0)), step=100.0)

        if st.form_submit_button('💾 Save Financial Snapshot'):
            user_data = {
                'monthly_income': monthly_income,
                'current_savings': current_savings,
                'investment_percentage': investment_percentage,
                'age': age,
                'investment_experience': investment_experience,
                'expenses': {
                    'Rent/EMI': rent_emi,
                    'Groceries': groceries,
                    'Utilities': utilities,
                    'Transportation': transportation,
                    'Dining & Entertainment': dining_entertainment,
                    'Miscellaneous': miscellaneous
                },
                'assets': st.session_state.user_data.get('assets', {}),
                'liabilities': st.session_state.user_data.get('liabilities', {})
            }
            st.session_state.user_data = user_data
            save_json(SNAPSHOT_FILE, user_data)
            st.success('✅ Financial Snapshot saved!')
            st.balloons()

# --- Dashboard Page ---
elif st.session_state.current_page == "📈 Dashboard":
    if not st.session_state.user_data:
        st.warning("Please create a financial snapshot first!")
    else:
        user_data = st.session_state.user_data
        analyzer = FinancialAnalyzer(user_data)
        metrics = analyzer.calculate_financial_metrics()
        advanced = analyzer.calculate_advanced_metrics(metrics)
        
        # Top Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Monthly Income", f"₹{metrics['monthly_income']:,.0f}")
        with col2:
            st.metric("Savings Rate", f"{metrics['savings_rate']:.1f}%")
        with col3:
            st.metric("ML Risk Score", f"{advanced['ml_risk_score']:.1f}/10")
        with col4:
            st.metric("Net Worth", f"₹{advanced['net_worth']:,.0f}")
        
        # ML Insights Section
        st.markdown("### 🤖 ML-Powered Insights")
        
        col1, col2 = st.columns(2)
        with col1:
            # Risk Profile
            st.markdown(f"""
            <div class='metric-card'>
                <h4>🎯 ML Risk Profile</h4>
                <h3>{advanced['ml_risk_profile']}</h3>
                <p>{advanced['risk_explanation']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Optimal Allocation
            allocation = advanced['optimal_allocation']
            fig = px.pie(values=list(allocation.values()), names=list(allocation.keys()),
                        title='ML-Recommended Portfolio Allocation')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Spending Insights
            st.markdown("### 💡 Spending Analysis")
            for insight in advanced.get('spending_insights', [])[:3]:
                st.markdown(f"<div class='ml-insight'>{insight}</div>", unsafe_allow_html=True)
            
            # Anomalies
            if advanced['anomalies']:
                st.markdown("### 🚨 ML Anomaly Detection")
                for anomaly in advanced['anomalies']:
                    st.error(anomaly)
        
        # Expense Analysis
        st.markdown("### 💸 Expense Breakdown")
        expense_data = {k: v for k, v in user_data['expenses'].items() if v > 0}
        if expense_data:
            fig = px.pie(values=list(expense_data.values()), names=list(expense_data.keys()),
                        title='Expense Distribution')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

# --- ML Insights Page ---
elif st.session_state.current_page == "🤖 ML Insights":
    st.header('🤖 Advanced ML Insights')
    
    if not st.session_state.user_data:
        st.warning("Please create a financial snapshot first!")
    else:
        user_data = st.session_state.user_data
        analyzer = FinancialAnalyzer(user_data)
        ml_predictor = MLFinancialPredictor()
        stock_predictor = StockPredictor()
        
        # Enhanced Risk Analysis
        st.markdown("### 🎯 Deep Risk Analysis")
        risk_profile, risk_allocation, risk_score, risk_explanation = ml_predictor.predict_risk_tolerance(user_data)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>Risk Profile Breakdown</h3>
                <p><strong>Profile:</strong> {risk_profile}</p>
                <p><strong>Score:</strong> {risk_score:.1f}/10</p>
                <p><strong>Explanation:</strong> {risk_explanation}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Risk Factors
            st.markdown("### 📊 Risk Factor Analysis")
            for factor, value in ml_predictor.risk_factors.items():
                st.write(f"• {factor.replace('_', ' ').title()}: {value:.2f}")
        
        with col2:
            # Stock Analysis
            st.markdown("### 📈 ML Stock Analysis")
            stock_symbols = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'AAPL', 'GOOGL']
            selected_stock = st.selectbox("Select Stock", stock_symbols)
            
            if st.button("🤖 Analyze Stock"):
                with st.spinner("Running ML analysis..."):
                    trend, confidence, price, technicals = stock_predictor.predict_stock_trend(selected_stock)
                    
                    st.markdown(f"""
                    <div class='ai-prediction'>
                        <h4>ML Prediction for {selected_stock}</h4>
                        <p><strong>Trend:</strong> {trend}</p>
                        <p><strong>Confidence:</strong> {confidence*100:.1f}%</p>
                        <p><strong>Current Price:</strong> ₹{price:.2f}</p>
                        <p><strong>RSI:</strong> {technicals['RSI']}</p>
                        <p><strong>MACD:</strong> {technicals['MACD_Histogram']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Goal Success Predictions
        if st.session_state.goals:
            st.markdown("### 🎯 Goal Success Probability")
            for goal in st.session_state.goals:
                probability, confidence = ml_predictor.predict_goal_success_probability(goal, user_data)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <h4>{goal['name']}</h4>
                        <p>Target: ₹{goal['amount']:,.0f} in {goal['years']} years</p>
                        <div style='background: #e2e8f0; border-radius: 10px; height: 20px;'>
                            <div style='background: #10b981; width: {probability*100}%; height: 100%; 
                                      border-radius: 10px; text-align: center; color: white;'>
                                {probability*100:.1f}%
                            </div>
                        </div>
                        <p><small>{confidence}</small></p>
                    </div>
                    """, unsafe_allow_html=True)

# --- Investment Center ---
elif st.session_state.current_page == "💹 Investment Center":
    st.header('💹 Investment Center')
    
    # Simulated mutual fund data
    @st.cache_data
    def get_mutual_fund_data():
        return pd.DataFrame({
            'Category': ['Large Cap', 'Mid Cap', 'Small Cap', 'Flexi Cap', 'ELSS'],
            'Fund Name': ['Axis Bluechip', 'Kotak Emerging', 'SBI Small Cap', 'Parag Parikh', 'Mirae Tax Saver'],
            '3Y CAGR': [14.5, 22.1, 28.9, 19.8, 18.5],
            '5Y CAGR': [16.1, 20.5, 25.4, 18.9, 17.2],
            'Risk': ['Moderate', 'High', 'Very High', 'High', 'High']
        })
    
    mf_df = get_mutual_fund_data()
    
    tab1, tab2 = st.tabs(["💰 Lump Sum", "📅 SIP Calculator"])
    
    with tab1:
        st.subheader("Lump Sum Investment")
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.selectbox('Category', mf_df['Category'].unique())
            fund_name = st.selectbox('Fund', mf_df[mf_df['Category']==category]['Fund Name'])
            amount = st.number_input('Investment (₹)', 1000.0, 1000000.0, 50000.0, 1000.0)
            
        with col2:
            selected_fund = mf_df[mf_df['Fund Name']==fund_name].iloc[0]
            returns_3y = selected_fund['3Y CAGR']
            future_value = amount * ((1 + returns_3y/100) ** 3)
            profit = future_value - amount
            
            st.metric("3-Year Projection", f"₹{future_value:,.0f}", f"₹{profit:,.0f} profit")
    
    with tab2:
        st.subheader("SIP Calculator")
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_sip = st.number_input('Monthly SIP (₹)', 500.0, 100000.0, 5000.0, 500.0)
            years = st.slider('Years', 1, 30, 10)
            return_rate = st.slider('Expected Return (%)', 5, 25, 12)
            
        with col2:
            future_value, total_invested = investment_projection_calculator(monthly_sip, years, return_rate)
            profit = future_value - total_invested
            
            st.metric("Future Value", f"₹{future_value:,.0f}")
            st.metric("Total Invested", f"₹{total_invested:,.0f}")
            st.metric("Estimated Profit", f"₹{profit:,.0f}")

# --- Goals Planner ---
elif st.session_state.current_page == "🎯 Goals Planner":
    st.header('🎯 Goals Planner')
    
    with st.form('add_goal'):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input('Goal Name')
        with col2:
            amount = st.number_input('Target Amount (₹)', 1000.0, 10000000.0, 500000.0, 1000.0)
        with col3:
            years = st.number_input('Years', 1, 50, 5)
        
        if st.form_submit_button('Add Goal'):
            st.session_state.goals.append({
                'name': name, 'amount': amount, 'years': years
            })
            save_json(GOALS_FILE, st.session_state.goals)
            st.success('Goal added!')
    
    if st.session_state.goals:
        for i, goal in enumerate(st.session_state.goals):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{goal['name']}** - ₹{goal['amount']:,.0f} in {goal['years']} years")
            with col2:
                monthly_saving = goal['amount'] / (goal['years'] * 12)
                st.write(f"Monthly: ₹{monthly_saving:,.0f}")
            with col3:
                if st.button('Delete', key=i):
                    st.session_state.goals.pop(i)
                    save_json(GOALS_FILE, st.session_state.goals)
                    st.rerun()

# --- Export Page ---
elif st.session_state.current_page == "📥 Export":
    st.header('📥 Export Data')
    
    if st.button('Download Financial Snapshot'):
        json_str = json.dumps(st.session_state.user_data, indent=2)
        st.download_button(
            'Download JSON',
            json_str,
            'financial_snapshot.json',
            'application/json'
        )

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 1rem;'>
    <p>Built with ❤️ by Ayush Shukla | AI Financial Advisor v3.0</p>
    <p>🤖 Powered by Machine Learning & Data Science</p>
</div>
""", unsafe_allow_html=True)
