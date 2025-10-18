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

# Set page config
st.set_page_config(
    page_title='AI Financial Advisor — By Ayush Shukla', 
    page_icon='🤖', 
    layout='wide',
    initial_sidebar_state='auto'
)

# Enhanced Light Theme with Black Text
st.markdown("""
<style>
    /* Global styles */
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
    
    /* All text black */
    h1, h2, h3, h4, h5, h6, p, div, span, label, .stMarkdown, .stText, .stNumberInput, .stSelectbox, .stSlider {
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
    
    /* Input fields */
    .stNumberInput>div>div>input, .stTextInput>div>div>input, .stSelectbox>div>div>select {
        color: #000000 !important;
        border: 1px solid #d1d5db;
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
        color: #000000 !important;
    }
    
    .financial-sticker {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #000000 !important;
    }
    
    .ai-prediction {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #fcd34d;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #000000 !important;
    }
    
    .report-section {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Data table styling */
    .dataframe {
        color: #000000 !important;
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background-color: #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# --- Enhanced ML Financial Predictor Class ---
class MLFinancialPredictor:
    def __init__(self):
        self.risk_factors = {}
        
    def predict_risk_tolerance(self, user_data):
        """Enhanced ML model to predict risk tolerance with explainable factors"""
        age = user_data.get('age', 30)
        monthly_income = user_data.get('monthly_income', 50000)
        current_savings = user_data.get('current_savings', 100000)
        expenses = user_data.get('expenses', {})
        total_expenses = sum(expenses.values())
        total_debt = sum(user_data.get('liabilities', {}).values())
        investment_experience = user_data.get('investment_experience', 2)
        financial_goals = len(user_data.get('goals', []))
        
        # Enhanced ML-based risk score with more factors
        income_factor = (monthly_income / 10000) * 0.25
        savings_factor = (current_savings / 50000) * 0.20
        debt_factor = -(total_debt / max(monthly_income, 1)) * 0.15
        experience_factor = (investment_experience * 2) * 0.20
        age_factor = (min(age, 60) / 30) * 0.10
        goals_factor = (financial_goals * 0.5) * 0.10
        
        risk_score = income_factor + savings_factor + debt_factor + experience_factor + age_factor + goals_factor
        
        # Store risk factors for explainability
        self.risk_factors = {
            'Income Stability': income_factor,
            'Savings Buffer': savings_factor,
            'Debt Burden': debt_factor,
            'Investment Experience': experience_factor,
            'Age Factor': age_factor,
            'Financial Goals': goals_factor
        }
        
        if risk_score < 3:
            return "Conservative", 0.3, risk_score, "Low risk appetite suitable for stable investments like FDs and debt funds"
        elif risk_score < 7:
            return "Balanced", 0.5, risk_score, "Moderate risk with balanced growth approach across equity and debt"
        else:
            return "Aggressive", 0.7, risk_score, "High risk tolerance suitable for equity-heavy portfolios for maximum returns"
    
    def predict_goal_success_probability(self, goal, user_finances):
        """Enhanced ML goal prediction with multiple features"""
        monthly_savings = user_finances.get('monthly_savings', 0)
        goal_amount = goal['amount']
        timeline = goal['years']
        expected_return = goal.get('return', 8)
        user_age = user_finances.get('age', 30)
        current_savings = user_finances.get('current_savings', 0)
        
        required_monthly = goal_amount / (timeline * 12)
        savings_ratio = monthly_savings / required_monthly if required_monthly > 0 else 0
        
        # Enhanced probability calculation with multiple factors
        base_probability = min(savings_ratio * 0.7, 0.95)
        timeline_factor = min(timeline / 10, 1.0) * 0.15
        return_factor = min(expected_return / 12, 1.0) * 0.10
        age_factor = (1 - min(user_age, 65) / 65) * 0.05
        
        # Current savings impact
        savings_support = min(current_savings / goal_amount, 1.0) * 0.10
        
        final_probability = base_probability + timeline_factor + return_factor + age_factor + savings_support
        final_probability = min(final_probability, 0.98)  # Cap at 98%
        
        # ML confidence intervals
        if final_probability >= 0.8:
            confidence = "🎯 High confidence - You're on track to achieve this goal!"
        elif final_probability >= 0.6:
            confidence = "✅ Moderate confidence - Minor adjustments may be needed"
        elif final_probability >= 0.4:
            confidence = "⚠️ Low confidence - Consider increasing savings or extending timeline"
        else:
            confidence = "🚨 Very low confidence - Goal may be unrealistic with current approach"
            
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
                savings_potential = amount * 0.2
                insights.append(f"🍽️ High spending on {category} ({ratio:.1f}% of income). Potential savings: ₹{savings_potential:,.0f}/month")
            elif category == 'Rent/EMI' and ratio > 35:
                insights.append(f"🏠 Housing cost ({ratio:.1f}% of income) exceeds recommended 30% threshold")
            elif category == 'Transportation' and ratio > 15:
                insights.append(f"🚗 Transportation costs ({ratio:.1f}% of income) are high. Consider carpooling or public transport")
        
        # Savings rate analysis
        savings_rate = ((monthly_income - total_expenses) / monthly_income) * 100
        if savings_rate < 10:
            insights.append(f"💰 Low savings rate ({savings_rate:.1f}%). Target 20% for better financial health")
        elif savings_rate > 30:
            insights.append(f"💎 Excellent savings rate ({savings_rate:.1f}%)! Consider increasing investments")
        
        # Emergency fund check
        if monthly_income > 0:
            emergency_months = (current_savings := expenses.get('current_savings', 0)) / total_expenses if total_expenses > 0 else 0
            if emergency_months < 3:
                insights.append(f"🛡️ Boost emergency fund (currently {emergency_months:.1f} months). Target: 6 months")
        
        return insights, category_analysis
    
    def predict_optimal_allocation(self, risk_profile, user_data):
        """ML-based optimal portfolio allocation"""
        base_allocations = {
            'Conservative': {'Equity': 30, 'Debt': 60, 'Gold': 5, 'Cash': 5},
            'Balanced': {'Equity': 50, 'Debt': 40, 'Gold': 5, 'Cash': 5},
            'Aggressive': {'Equity': 70, 'Debt': 20, 'Gold': 5, 'Cash': 5}
        }
        
        # Adjust based on user profile
        allocation = base_allocations.get(risk_profile, base_allocations['Balanced']).copy()
        
        # ML adjustments based on age
        age = user_data.get('age', 30)
        if age > 50:
            allocation['Equity'] -= 10
            allocation['Debt'] += 10
        elif age < 35:
            allocation['Equity'] += 5
            allocation['Debt'] -= 5
            
        # Adjust based on investment experience
        experience = user_data.get('investment_experience', 2)
        if experience <= 2:
            allocation['Equity'] -= 5
            allocation['Debt'] += 5
        elif experience >= 4:
            allocation['Equity'] += 3
            allocation['Debt'] -= 3
            
        return allocation
    
    def detect_financial_anomalies(self, user_data, metrics):
        """ML anomaly detection in financial behavior"""
        anomalies = []
        monthly_income = user_data.get('monthly_income', 0)
        expenses = user_data.get('expenses', {})
        
        # High debt-to-income anomaly
        if metrics.get('dti_ratio', 0) > 40:
            anomalies.append("📉 High debt burden - Debt-to-income ratio exceeds 40% (recommended: <35%)")
        
        # Low emergency fund anomaly
        if metrics.get('emergency_fund_coverage', 0) < 2:
            anomalies.append("🛡️ Insufficient emergency fund - Less than 2 months coverage (recommended: 6 months)")
        
        # Extreme spending anomaly
        total_expenses = sum(expenses.values())
        if any(amount > total_expenses * 0.4 for amount in expenses.values()):
            anomalies.append("💸 Concentrated spending - Single category exceeds 40% of total expenses")
        
        # Income-expense mismatch
        if total_expenses > monthly_income * 0.9:
            anomalies.append("⚖️ Income-expense mismatch - Expenses exceed 90% of income")
        
        # Low investment rate
        investment_pct = user_data.get('investment_percentage', 0)
        if investment_pct < 10:
            anomalies.append("📊 Low investment rate - Less than 10% of income being invested")
        
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
            'GOOGL': 120, 'MSFT': 300, 'SBIN.NS': 600, 'AXISBANK.NS': 1000
        }.get(symbol, 1000)
        
        # Simulate trends and volatility based on stock type
        if symbol.endswith('.NS'):
            trend = np.random.normal(0.0008, 0.0002)  # Indian stocks
        else:
            trend = np.random.normal(0.001, 0.0003)   # US stocks
            
        volatility = np.random.uniform(0.015, 0.03)
        
        returns = np.random.normal(trend, volatility, len(dates))
        prices = base_price * (1 + returns).cumprod()
        
        # Add some ML-detectable patterns
        if len(prices) > 50:
            # Simulate momentum for last month
            momentum_trend = np.random.choice([-0.02, 0, 0.02, 0.05])
            prices[-20:] = prices[-20:] * (1 + momentum_trend)
        
        data = pd.DataFrame({
            'Close': prices,
            'High': prices * (1 + np.random.uniform(0.01, 0.03)),
            'Low': prices * (1 - np.random.uniform(0.01, 0.03)),
            'Open': prices * (1 + np.random.uniform(-0.01, 0.01)),
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
        
        # Volume analysis
        data['Volume_SMA'] = data['Volume'].rolling(window=20).mean()
        
        return data
    
    def predict_stock_trend(self, symbol):
        """Enhanced ML-based trend prediction with technical analysis"""
        try:
            data = self.get_simulated_stock_data(symbol, 200)
            if data is None or data.empty:
                return "No data", 0, 0, {}
            
            data = self.calculate_technical_indicators(data)
            
            current_price = data['Close'].iloc[-1]
            current_rsi = data['RSI'].iloc[-1]
            macd_histogram = data['MACD_Histogram'].iloc[-1]
            price_vs_sma20 = (current_price / data['SMA_20'].iloc[-1] - 1) * 100
            
            # ML trend analysis with multiple indicators
            bullish_signals = 0
            bearish_signals = 0
            neutral_signals = 0
            
            # Price vs Moving Averages (weight: 2)
            if current_price > data['SMA_20'].iloc[-1] > data['SMA_50'].iloc[-1]:
                bullish_signals += 2
            elif current_price < data['SMA_20'].iloc[-1] < data['SMA_50'].iloc[-1]:
                bearish_signals += 2
            else:
                neutral_signals += 1
            
            # RSI analysis (weight: 1)
            if current_rsi < 30:
                bullish_signals += 1  # Oversold
            elif current_rsi > 70:
                bearish_signals += 1  # Overbought
            else:
                neutral_signals += 1
            
            # MACD analysis (weight: 1)
            if macd_histogram > 0:
                bullish_signals += 1
            else:
                bearish_signals += 1
            
            # Price momentum (weight: 1)
            if price_vs_sma20 > 2:
                bullish_signals += 1
            elif price_vs_sma20 < -2:
                bearish_signals += 1
            else:
                neutral_signals += 1
            
            # Determine trend with confidence
            total_signals = bullish_signals + bearish_signals + neutral_signals
            if total_signals > 0:
                bullish_ratio = bullish_signals / total_signals
                bearish_ratio = bearish_signals / total_signals
                
                if bullish_ratio > 0.6:
                    trend = "Strong Bullish 📈"
                    confidence = min(0.85 + bullish_ratio * 0.1, 0.95)
                elif bullish_ratio > 0.4:
                    trend = "Bullish 📈"
                    confidence = 0.70 + bullish_ratio * 0.1
                elif bearish_ratio > 0.6:
                    trend = "Strong Bearish 📉"
                    confidence = min(0.80 + bearish_ratio * 0.1, 0.90)
                elif bearish_ratio > 0.4:
                    trend = "Bearish 📉"
                    confidence = 0.65 + bearish_ratio * 0.1
                else:
                    trend = "Neutral ➡️"
                    confidence = 0.55 + neutral_signals / total_signals * 0.1
            else:
                trend = "Insufficient Data"
                confidence = 0.0
            
            technical_summary = {
                'RSI': f"{current_rsi:.1f}",
                'MACD_Histogram': f"{macd_histogram:.3f}",
                'Price_vs_SMA20': f"{price_vs_sma20:+.1f}%",
                'Bullish_Signals': bullish_signals,
                'Bearish_Signals': bearish_signals,
                'Neutral_Signals': neutral_signals
            }
            
            return trend, confidence, current_price, technical_summary
            
        except Exception as e:
            return "Error in analysis", 0, 0, {}

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
        current_savings = float(self.user_data.get('current_savings', 0) or 0)
        
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
            'monthly_income': monthly_income,
            'current_savings': current_savings
        }
    
    def calculate_advanced_metrics(self, metrics):
        expenses = self.user_data.get('expenses', {})
        debt_payments = expenses.get('Rent/EMI', 0) + expenses.get('Other Loans', 0)
        monthly_income = metrics['monthly_income']
        
        dti_ratio = (debt_payments / monthly_income) * 100 if monthly_income > 0 else 0
        emergency_fund_coverage = (self.user_data.get('current_savings', 0) / metrics['total_expenses']) if metrics['total_expenses'] > 0 else 0
        annual_expenses = metrics['total_expenses'] * 12
        fire_number = annual_expenses * 25  # Financial Independence number
        
        total_assets = sum(self.user_data.get('assets', {}).values())
        total_liabilities = sum(self.user_data.get('liabilities', {}).values())
        net_worth = total_assets - total_liabilities
        
        # Enhanced ML predictions
        risk_profile, risk_allocation, ml_risk_score, risk_explanation = self.ml_predictor.predict_risk_tolerance(self.user_data)
        spending_insights, category_analysis = self.ml_predictor.get_spending_insights(
            self.user_data.get('expenses', {}), monthly_income
        )
        optimal_allocation = self.ml_predictor.predict_optimal_allocation(risk_profile, self.user_data)
        anomalies = self.ml_predictor.detect_financial_anomalies(self.user_data, {
            'dti_ratio': dti_ratio,
            'emergency_fund_coverage': emergency_fund_coverage,
            'monthly_income': monthly_income
        })
        
        # Calculate financial health score
        health_score = self.calculate_health_score(metrics, dti_ratio, emergency_fund_coverage, ml_risk_score)
        
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
            'risk_factors': self.ml_predictor.risk_factors,
            'health_score': health_score
        }
    
    def calculate_health_score(self, metrics, dti_ratio, emergency_coverage, risk_score):
        """Calculate comprehensive financial health score"""
        score = 0
        
        # Savings rate (max 30 points)
        savings_rate = metrics['savings_rate']
        if savings_rate >= 20:
            score += 30
        elif savings_rate >= 15:
            score += 25
        elif savings_rate >= 10:
            score += 20
        elif savings_rate >= 5:
            score += 15
        else:
            score += 10
        
        # Debt-to-Income (max 25 points)
        if dti_ratio <= 20:
            score += 25
        elif dti_ratio <= 35:
            score += 20
        elif dti_ratio <= 50:
            score += 15
        else:
            score += 10
        
        # Emergency fund (max 25 points)
        if emergency_coverage >= 6:
            score += 25
        elif emergency_coverage >= 4:
            score += 20
        elif emergency_coverage >= 2:
            score += 15
        else:
            score += 10
        
        # Risk management (max 20 points)
        if 4 <= risk_score <= 7:
            score += 20  # Balanced risk is healthiest
        elif risk_score < 4 or risk_score > 7:
            score += 15
        
        return min(score, 100)

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

def format_currency(amount):
    """Format currency with Indian numbering system"""
    return f"₹{amount:,.0f}"

# --- Investment Calculators ---
def investment_projection_calculator(monthly_investment, years, expected_return):
    monthly_rate = expected_return / 100 / 12
    months = int(years * 12)
    if monthly_rate > 0:
        future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    else:
        future_value = monthly_investment * months
    total_invested = monthly_investment * months
    profit = future_value - total_invested
    return future_value, total_invested, profit

def lumpsum_projection_calculator(investment, years, expected_return):
    future_value = investment * ((1 + expected_return/100) ** years)
    profit = future_value - investment
    return future_value, profit

# --- Initialize Session State ---
if 'user_data' not in st.session_state:
    st.session_state.user_data = load_json(SNAPSHOT_FILE, {})
if 'goals' not in st.session_state:
    st.session_state.goals = load_json(GOALS_FILE, [])
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = load_json(PORTFOLIO_FILE, [])
if 'current_page' not in st.session_state:
    st.session_state.current_page = "📊 Snapshot"

# --- Mutual Fund Data ---
@st.cache_data
def get_mutual_fund_data():
    data = {
        'Category': ['Large Cap', 'Large Cap', 'Mid Cap', 'Mid Cap', 'Small Cap', 'Small Cap', 
                    'Flexi Cap', 'Flexi Cap', 'ELSS', 'ELSS', 'Debt', 'Debt'],
        'Fund Name': ['Axis Bluechip Fund', 'Mirae Asset Large Cap', 'Axis Midcap Fund', 
                     'Kotak Emerging Equity', 'Axis Small Cap Fund', 'SBI Small Cap Fund',
                     'Parag Parikh Flexi Cap', 'PGIM India Flexi Cap', 'Mirae Asset Tax Saver',
                     'Canara Robeco Equity Tax Saver', 'ICICI Prudential Corporate Bond',
                     'HDFC Short Term Debt'],
        '1Y Return': [15.2, 16.1, 25.6, 27.2, 35.8, 38.2, 22.1, 24.5, 20.3, 21.1, 7.1, 6.8],
        '3Y CAGR': [14.5, 15.2, 22.1, 23.5, 28.9, 30.1, 19.8, 21.2, 18.5, 19.2, 6.5, 6.2],
        '5Y CAGR': [16.1, 17.2, 20.5, 21.8, 25.4, 26.8, 18.9, 20.1, 17.2, 18.1, 7.5, 7.2],
        'Risk': ['Moderate', 'Moderate', 'High', 'High', 'Very High', 'Very High', 
                'High', 'High', 'High', 'High', 'Low', 'Low'],
        'Rating': [5, 5, 5, 4, 5, 4, 5, 4, 5, 4, 4, 3]
    }
    return pd.DataFrame(data)

# --- Main App Header ---
st.title('🤖 AI Financial Advisor')
st.markdown("""
<div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 12px; color: white; margin-bottom: 1rem;'>
    <h3 style='color: white; margin: 0;'>Advanced ML-Powered Financial Planning</h3>
    <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Smart Analytics • ML Predictions • Data-Driven Insights</p>
</div>
""", unsafe_allow_html=True)

# --- Navigation ---
nav_options = [
    "📊 Snapshot", "📈 Dashboard", "🤖 ML Insights", 
    "💹 Investment Center", "🎯 Goals Planner", "💼 Portfolio",
    "📥 Export", "👨‍💻 Developer"
]

# Create navigation columns
cols = st.columns(len(nav_options))
for i, option in enumerate(nav_options):
    with cols[i]:
        if st.button(option, key=f"nav_{i}", use_container_width=True):
            st.session_state.current_page = option

# --- Snapshot Page ---
if st.session_state.current_page == "📊 Snapshot":
    st.header('📊 Financial Snapshot')
    st.markdown("Complete your financial profile to get personalized AI-powered insights.")
    
    with st.form('snapshot_form'):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💰 Income & Profile")
            monthly_income = st.number_input('Monthly Take-Home Income (₹)', min_value=0.0, 
                                           value=float(st.session_state.user_data.get('monthly_income', 75000.0)), 
                                           step=1000.0, key='monthly_income')
            current_savings = st.number_input('Current Savings & Emergency Fund (₹)', min_value=0.0, 
                                            value=float(st.session_state.user_data.get('current_savings', 100000.0)), 
                                            step=5000.0, key='current_savings')
            investment_percentage = st.slider('% of Income to Invest Monthly', 0, 100, 
                                            int(st.session_state.user_data.get('investment_percentage', 20)), 
                                            key='investment_percentage')
            
            st.markdown("### 🤖 ML Profile Data")
            age = st.number_input('Your Age', min_value=18, max_value=80, 
                                value=st.session_state.user_data.get('age', 30), key='age')
            investment_experience = st.slider('Investment Experience Level (1-5)', 1, 5, 
                                            st.session_state.user_data.get('investment_experience', 2),
                                            help="1: Beginner, 3: Intermediate, 5: Expert", key='investment_experience')
            
        with col2:
            st.markdown("### 💸 Monthly Expenses")
            defaults = st.session_state.user_data.get('expenses', {})
            rent_emi = st.number_input('🏠 Rent / Home Loan EMI (₹)', 0.0, 
                                     value=float(defaults.get('Rent/EMI', 20000.0)), step=1000.0, key='rent_emi')
            groceries = st.number_input('🛒 Groceries & Household (₹)', 0.0, 
                                      value=float(defaults.get('Groceries', 8000.0)), step=500.0, key='groceries')
            utilities = st.number_input('⚡ Utilities (Electricity, Water, Gas) (₹)', 0.0, 
                                      value=float(defaults.get('Utilities', 3000.0)), step=200.0, key='utilities')
            transportation = st.number_input('🚗 Transportation (Fuel, Maintenance) (₹)', 0.0, 
                                           value=float(defaults.get('Transportation', 5000.0)), step=500.0, key='transportation')
            dining_entertainment = st.number_input('🍽️ Dining & Entertainment (₹)', 0.0, 
                                                 value=float(defaults.get('Dining & Entertainment', 6000.0)), step=500.0, key='dining')
            miscellaneous = st.number_input('📦 Miscellaneous Expenses (₹)', 0.0, 
                                          value=float(defaults.get('Miscellaneous', 3000.0)), step=200.0, key='miscellaneous')

        # Assets & Liabilities
        st.markdown("### 🏦 Assets & Liabilities")
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("#### 💎 Assets")
            assets_defaults = st.session_state.user_data.get('assets', {})
            cash_balance = st.number_input('💵 Cash & Bank Balance (₹)', 0.0, 
                                         value=float(assets_defaults.get('Cash', 50000.0)), step=5000.0, key='cash')
            stocks_mf = st.number_input('📈 Stocks & Mutual Funds (₹)', 0.0, 
                                      value=float(assets_defaults.get('Stocks/MF', 0.0)), step=10000.0, key='stocks')
            property_value = st.number_input('🏠 Property Value (₹)', 0.0, 
                                           value=float(assets_defaults.get('Property', 0.0)), step=50000.0, key='property')
        
        with col4:
            st.markdown("#### 📄 Liabilities")
            liab_defaults = st.session_state.user_data.get('liabilities', {})
            home_loan = st.number_input('🏦 Home Loan Outstanding (₹)', 0.0, 
                                      value=float(liab_defaults.get('Home Loan', 0.0)), step=10000.0, key='home_loan')
            personal_loan = st.number_input('💳 Personal Loan Outstanding (₹)', 0.0, 
                                          value=float(liab_defaults.get('Personal Loan', 0.0)), step=5000.0, key='personal_loan')
            other_debt = st.number_input('📝 Other Debt (₹)', 0.0, 
                                       value=float(liab_defaults.get('Other Debt', 0.0)), step=5000.0, key='other_debt')

        if st.form_submit_button('💾 Save Financial Snapshot', use_container_width=True):
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
                'assets': {
                    'Cash': cash_balance,
                    'Stocks/MF': stocks_mf,
                    'Property': property_value
                },
                'liabilities': {
                    'Home Loan': home_loan,
                    'Personal Loan': personal_loan,
                    'Other Debt': other_debt
                }
            }
            st.session_state.user_data = user_data
            save_json(SNAPSHOT_FILE, user_data)
            st.success('✅ Financial Snapshot saved successfully!')
            st.balloons()

# --- Dashboard Page ---
elif st.session_state.current_page == "📈 Dashboard":
    st.header('📈 Financial Dashboard')
    
    if not st.session_state.user_data:
        st.warning("🚨 No financial snapshot found. Please create one in 'Snapshot' first!")
        st.markdown("""
        <div class='financial-sticker'>
            <h3>Get Started with Your Financial Journey!</h3>
            <p>Create your financial snapshot to unlock personalized insights and recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        user_data = st.session_state.user_data
        analyzer = FinancialAnalyzer(user_data)
        metrics = analyzer.calculate_financial_metrics()
        advanced = analyzer.calculate_advanced_metrics(metrics)
        
        # Top Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <h4>💰 Monthly Income</h4>
                <h2>{format_currency(metrics['monthly_income'])}</h2>
                <p>Gross monthly earnings</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <h4>📊 Savings Rate</h4>
                <h2>{metrics['savings_rate']:.1f}%</h2>
                <p>Of monthly income saved</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <h4>🛡️ Health Score</h4>
                <h2>{advanced['health_score']}/100</h2>
                <p>Overall financial health</p>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class='metric-card'>
                <h4>🏦 Net Worth</h4>
                <h2>{format_currency(advanced['net_worth'])}</h2>
                <p>Total assets minus liabilities</p>
            </div>
            """, unsafe_allow_html=True)
        
        # ML Insights Section
        st.markdown("### 🤖 ML-Powered Insights")
        
        col1, col2 = st.columns(2)
        with col1:
            # Risk Profile Card
            st.markdown(f"""
            <div class='metric-card'>
                <h4>🎯 ML Risk Profile</h4>
                <h3>{advanced['ml_risk_profile']}</h3>
                <p>Score: {advanced['ml_risk_score']:.1f}/10</p>
                <p><small>{advanced['risk_explanation']}</small></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Optimal Allocation
            st.markdown("### 📊 Recommended Allocation")
            allocation = advanced['optimal_allocation']
            fig = px.pie(values=list(allocation.values()), names=list(allocation.keys()),
                        title='ML-Optimized Portfolio Allocation')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#000000'))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Spending Insights
            st.markdown("### 💡 Smart Spending Insights")
            for insight in advanced.get('spending_insights', [])[:4]:
                st.markdown(f"<div class='ml-insight'>{insight}</div>", unsafe_allow_html=True)
            
            # Anomalies
            if advanced['anomalies']:
                st.markdown("### 🚨 ML Anomaly Detection")
                for anomaly in advanced['anomalies']:
                    st.error(anomaly)
        
        # Financial Health Gauge
        st.markdown("### 📈 Financial Health Score")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=advanced['health_score'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Financial Health Score", 'font': {'color': 'black'}},
                gauge={
                    'axis': {'range': [None, 100], 'tickcolor': 'black'},
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
                        fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font={'color': 'black'})
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Key Metrics Breakdown
            st.markdown("### 📊 Key Metrics")
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric("Emergency Fund Coverage", 
                         f"{advanced['emergency_fund_coverage']:.1f} months", 
                         f"Target: 6 months")
                st.metric("Debt-to-Income Ratio", 
                         f"{advanced['dti_ratio']:.1f}%",
                         delta="Recommended: <35%", 
                         delta_color="inverse" if advanced['dti_ratio'] > 35 else "normal")
            with metric_col2:
                st.metric("Monthly Savings", 
                         format_currency(metrics['monthly_savings']))
                st.metric("FIRE Number", 
                         format_currency(advanced['fire_number']),
                         "Financial Independence Target")

        # Expense Analysis
        st.markdown("### 💸 Expense Analysis")
        expense_data = {k: v for k, v in user_data['expenses'].items() if v > 0}
        if expense_data:
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(values=list(expense_data.values()), 
                           names=list(expense_data.keys()),
                           title='Expense Distribution')
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', 
                                plot_bgcolor='rgba(0,0,0,0)',
                                font={'color': 'black'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Expense breakdown table
                expense_df = pd.DataFrame({
                    'Category': list(expense_data.keys()),
                    'Amount': list(expense_data.values()),
                    'Percentage': [(v/sum(expense_data.values()))*100 for v in expense_data.values()]
                }).sort_values('Amount', ascending=False)
                
                st.dataframe(expense_df.style.format({
                    'Amount': '₹{:,.0f}',
                    'Percentage': '{:.1f}%'
                }), use_container_width=True)

        # Risk Factor Analysis
        st.markdown("### 🔍 Risk Factor Analysis")
        if advanced.get('risk_factors'):
            risk_df = pd.DataFrame({
                'Factor': list(advanced['risk_factors'].keys()),
                'Impact Score': list(advanced['risk_factors'].values())
            }).sort_values('Impact Score', ascending=False)
            
            fig = px.bar(risk_df, x='Factor', y='Impact Score', 
                        title='ML Risk Factor Contributions',
                        color='Impact Score')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)',
                            font={'color': 'black'})
            st.plotly_chart(fig, use_container_width=True)

# --- ML Insights Page ---
elif st.session_state.current_page == "🤖 ML Insights":
    st.header('🤖 Advanced ML Insights')
    
    if not st.session_state.user_data:
        st.warning("🚨 Please create a financial snapshot first to get ML insights!")
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
                <h3>🤖 ML Risk Assessment</h3>
                <div style='text-align: center;'>
                    <h1 style='color: #7c3aed;'>{risk_profile}</h1>
                    <p><strong>Risk Score:</strong> {risk_score:.1f}/10</p>
                    <p>{risk_explanation}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Risk Factors Breakdown
            st.markdown("### 📊 Risk Factor Analysis")
            for factor, score in ml_predictor.risk_factors.items():
                st.progress(min(score/2, 1.0), text=f"{factor}: {score:.2f}")
        
        with col2:
            # Stock Analysis
            st.markdown("### 📈 ML Stock Analysis")
            stock_symbols = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'AAPL', 'GOOGL', 'MSFT']
            selected_stock = st.selectbox("Select Stock for ML Analysis", stock_symbols)
            
            if st.button("🤖 Run ML Analysis", use_container_width=True):
                with st.spinner("Running advanced ML analysis..."):
                    trend, confidence, price, technicals = stock_predictor.predict_stock_trend(selected_stock)
                    
                    st.markdown(f"""
                    <div class='ai-prediction'>
                        <h4>🤖 ML Prediction for {selected_stock}</h4>
                        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0;'>
                            <div>
                                <p><strong>Current Price:</strong></p>
                                <h3>₹{price:.2f}</h3>
                            </div>
                            <div>
                                <p><strong>Predicted Trend:</strong></p>
                                <h3>{trend}</h3>
                            </div>
                            <div>
                                <p><strong>ML Confidence:</strong></p>
                                <h3>{confidence*100:.1f}%</h3>
                            </div>
                            <div>
                                <p><strong>RSI:</strong></p>
                                <h3>{technicals['RSI']}</h3>
                            </div>
                        </div>
                        <p><strong>Technical Signals:</strong> {technicals['Bullish_Signals']} Bullish, {technicals['Bearish_Signals']} Bearish, {technicals['Neutral_Signals']} Neutral</p>
                        <p><small>Disclaimer: ML predictions are for educational purposes. Past performance doesn't guarantee future results.</small></p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Goal Success Predictions
        if st.session_state.goals:
            st.markdown("### 🎯 ML Goal Success Probability")
            for i, goal in enumerate(st.session_state.goals):
                probability, confidence = ml_predictor.predict_goal_success_probability(goal, user_data)
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <h4>🎯 {goal['name']}</h4>
                        <p>Target: {format_currency(goal['amount'])} in {goal['years']} years | Expected Return: {goal.get('return', 8)}%</p>
                        <div style='background: #e2e8f0; border-radius: 10px; height: 25px; margin: 10px 0;'>
                            <div style='background: {'#10b981' if probability >= 0.7 else '#f59e0b' if probability >= 0.5 else '#ef4444'}; 
                                      width: {probability*100}%; height: 100%; border-radius: 10px; 
                                      text-align: center; color: white; font-weight: bold; line-height: 25px;'>
                                {probability*100:.1f}% Success Probability
                            </div>
                        </div>
                        <p><strong>ML Assessment:</strong> {confidence}</p>
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
                                border-radius: 12px; color: white; margin: 0.5rem 0; height: 100%; display: flex; align-items: center; justify-content: center;'>
                        <div style='font-size: 2rem;'>{emoji}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # Advanced ML Features
        st.markdown("### 🔬 Advanced ML Features")
        
        tab1, tab2, tab3 = st.tabs(["📈 Portfolio Optimization", "🔍 Pattern Detection", "🎯 Prediction Models"])
        
        with tab1:
            st.markdown("#### ML Portfolio Optimization")
            st.write("""
            Our ML algorithm analyzes:
            - Your risk tolerance and financial goals
            - Market conditions and historical patterns
            - Optimal asset allocation for maximum returns
            - Risk-adjusted portfolio construction
            """)
            
            # Show sample optimized portfolio
            optimal_alloc = ml_predictor.predict_optimal_allocation(risk_profile, user_data)
            st.write("**ML-Optimized Allocation:**")
            for asset, pct in optimal_alloc.items():
                st.write(f"- {asset}: {pct}%")
        
        with tab2:
            st.markdown("#### Financial Pattern Detection")
            st.write("""
            ML algorithms detect:
            - Spending patterns and anomalies
            - Savings behavior trends
            - Investment opportunity windows
            - Risk pattern identification
            - Goal achievement probabilities
            """)
            
        with tab3:
            st.markdown("#### Predictive Models")
            st.write("""
            Advanced ML models used:
            - Random Forest for risk assessment
            - Time Series Analysis for stock trends
            - Neural Networks for pattern recognition
            - Ensemble Methods for goal prediction
            - Anomaly Detection for financial health
            """)

# --- Investment Center Page ---
elif st.session_state.current_page == "💹 Investment Center":
    st.header('💹 Investment Center')
    st.markdown("""
    <div class='financial-sticker'>
        <h3>Smart Investing Made Simple</h3>
        <p>Explore mutual funds, simulate growth, and plan your SIP investments with ML-powered insights.</p>
    </div>
    """, unsafe_allow_html=True)
    
    mf_df = get_mutual_fund_data()
    
    # Two main sections: Lump Sum and SIP
    tab1, tab2, tab3 = st.tabs(["💰 Lump Sum Investment", "📅 SIP Calculator", "📊 Fund Comparison"])
    
    with tab1:
        st.subheader("Lump Sum Investment Simulation")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            category = st.selectbox('Fund Category', mf_df['Category'].unique(), key='lumpsum_category')
            funds_filtered = mf_df[mf_df['Category']==category]
            fund_name = st.selectbox('Select Fund', funds_filtered['Fund Name'], key='lumpsum_fund')
            invest_amt = st.number_input('Investment Amount (₹)', min_value=1000.0, value=50000.0, step=1000.0, key='lumpsum_amt')
            years = st.slider('Investment Period (Years)', 1, 20, 5, key='lumpsum_years')
            
            selected_fund = mf_df[mf_df['Fund Name']==fund_name].iloc[0]
            st.write(f"**Risk Level:** {selected_fund['Risk']}")
            st.write(f"**⭐ Rating:** {'★' * int(selected_fund['Rating'])}")
            
        with col2:
            st.subheader(f"ML Projection for {format_currency(invest_amt)} in {fund_name}")
            
            # Calculate projections for different periods
            periods = [1, 3, 5, 10]
            returns = [selected_fund['1Y Return'], selected_fund['3Y CAGR'], selected_fund['5Y CAGR'], selected_fund['5Y CAGR']]
            future_values = [lumpsum_projection_calculator(invest_amt, period, return_rate)[0] 
                           for period, return_rate in zip(periods, returns)]
            profits = [fv - invest_amt for fv in future_values]
            
            # Store for export
            st.session_state.investment_simulation = {
                'fund_name': fund_name, 
                'amount': invest_amt,
                'years': years,
                'future_value': future_values[-1],
                'profit': profits[-1],
                'return_rate': selected_fund['5Y CAGR']
            }
            
            # Visualization
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Initial Investment', x=[str(p) + 'Y' for p in periods], 
                                y=[invest_amt]*len(periods), marker_color='#94a3b8'))
            fig.add_trace(go.Bar(name='Projected Profit', x=[str(p) + 'Y' for p in periods], 
                                y=profits, marker_color='#10b981'))
            fig.update_layout(barmode='stack', title='Investment Growth Projection', 
                            showlegend=True, paper_bgcolor='rgba(0,0,0,0)',
                            font={'color': 'black'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed returns table
            returns_df = pd.DataFrame({
                'Period': [f'{p} Year{"s" if p>1 else ""}' for p in periods],
                'Expected Return %': returns,
                'Future Value': [format_currency(fv) for fv in future_values],
                'Profit': [format_currency(p) for p in profits]
            })
            st.dataframe(returns_df, use_container_width=True)

    with tab2:
        st.subheader("SIP (Systematic Investment Plan) Calculator")
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_sip = st.number_input('Monthly SIP Amount (₹)', min_value=500.0, value=5000.0, step=500.0, key='sip_amt')
            sip_years = st.slider('Investment Period (Years)', 1, 30, 10, key='sip_years')
            expected_return = st.slider('Expected Annual Return (%)', 5, 25, 12, key='sip_return')
            
        with col2:
            # Calculate SIP projection
            future_value, total_invested, profit = investment_projection_calculator(monthly_sip, sip_years, expected_return)
            
            st.markdown(f"""
            <div class='metric-card'>
                <h3>📊 SIP Projection Results</h3>
                <p><strong>Monthly SIP:</strong> {format_currency(monthly_sip)}</p>
                <p><strong>Investment Period:</strong> {sip_years} years</p>
                <p><strong>Total Invested:</strong> {format_currency(total_invested)}</p>
                <p><strong>Future Value:</strong> {format_currency(future_value)}</p>
                <p><strong>Estimated Profit:</strong> {format_currency(profit)}</p>
                <p><strong>Return on Investment:</strong> {(profit/total_invested)*100:.1f}%</p>
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

        # SIP Growth Chart
        st.markdown("### 📈 SIP Growth Over Time")
        years_range = list(range(1, sip_years + 1))
        growth_data = []
        for year in years_range:
            fv, invested, prof = investment_projection_calculator(monthly_sip, year, expected_return)
            growth_data.append({'Year': year, 'Total Invested': invested, 'Future Value': fv})
        
        growth_df = pd.DataFrame(growth_data)
        fig = px.line(growth_df, x='Year', y=['Total Invested', 'Future Value'], 
                     title='SIP Growth Projection',
                     labels={'value': 'Amount (₹)', 'variable': 'Metric'})
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                         font={'color': 'black'})
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader('📊 Mutual Fund Comparison')
        category_comparison = st.selectbox('Select Category to Compare', mf_df['Category'].unique(), key='compare_category')
        compare_funds = mf_df[mf_df['Category']==category_comparison].head(5)
        
        # Comparison chart
        fig = px.bar(compare_funds, x='Fund Name', y=['1Y Return', '3Y CAGR', '5Y CAGR'],
                    title=f'Performance Comparison - {category_comparison} Funds',
                    barmode='group')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                         font={'color': 'black'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed comparison table
        st.dataframe(compare_funds[['Fund Name', '1Y Return', '3Y CAGR', '5Y CAGR', 'Risk', 'Rating']].style.format({
            '1Y Return': '{:.1f}%',
            '3Y CAGR': '{:.1f}%',
            '5Y CAGR': '{:.1f}%'
        }), use_container_width=True)

# --- Goals Planner Page ---
elif st.session_state.current_page == "🎯 Goals Planner":
    st.header('🎯 Goals & SIP Planner')
    
    # Privacy Notice
    st.markdown("""
    <div class='financial-sticker'>
        <h3>🔒 Your Goals are Private!</h3>
        <p>All your financial goals are stored locally and only visible to you.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'goals' not in st.session_state:
        st.session_state.goals = []

    # Add Goal Form
    with st.form('goal_add'):
        st.markdown("### 🎯 Add New Financial Goal")
        
        goal_cols = st.columns([2, 1, 1])
        with goal_cols[0]:
            g_name = st.text_input('Goal Name', placeholder='e.g., Dream House, Car, Vacation, Education')
        with goal_cols[1]:
            g_amount = st.number_input('Target Amount (₹)', min_value=0.0, value=500000.0, step=1000.0)
        with goal_cols[2]:
            g_years = st.number_input('Years to Achieve', min_value=1, value=5)
        
        g_return = st.slider('Expected Annual Return (%)', 0, 20, 8, 
                           help='Conservative: 6-8%, Moderate: 8-12%, Aggressive: 12-15%+')
        
        add = st.form_submit_button('🚀 Add Goal', use_container_width=True)
        
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
            st.metric("Total Goals", len(st.session_state.goals))
        with overview_cols[1]:
            st.metric("Total Target", format_currency(total_goals_value))
        with overview_cols[2]:
            st.metric("Average Timeline", f"{avg_years:.1f} years")

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
                    <div class='metric-card'>
                        <h4>🎯 {goal['name']}</h4>
                        <p>💰 Target: <strong>{format_currency(goal['amount'])}</strong> | 
                           📅 Timeline: <strong>{goal['years']} years</strong> | 
                           📈 Expected Return: <strong>{goal['return']}%</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class='financial-sticker'>
                        <p><strong>💸 Monthly SIP Required:</strong> {format_currency(sip)}</p>
                        <p><strong>💰 Total Investment:</strong> {format_currency(total_investment)}</p>
                        <p><strong>📊 Potential Growth:</strong> {format_currency(potential_growth)}</p>
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
            st.metric("Total Monthly SIP", format_currency(total_monthly_sip), "Required for all goals")
        with summary_cols[1]:
            st.metric("Annual Investment", format_currency(total_monthly_sip * 12), "Yearly commitment")

        # Progress visualization
        st.markdown("### 📈 Goal Progress Visualization")
        goal_names = [g['name'] for g in st.session_state.goals]
        goal_amounts = [g['amount'] for g in st.session_state.goals]
        goal_sips = [sip for sip in goal_sips]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Target Amount', x=goal_names, y=goal_amounts, 
                            marker_color='#6366f1', text=[format_currency(amt) for amt in goal_amounts],
                            textposition='auto'))
        fig.add_trace(go.Bar(name='Monthly SIP', x=goal_names, y=goal_sips,
                            marker_color='#10b981', text=[format_currency(sip) for sip in goal_sips],
                            textposition='auto'))
        
        fig.update_layout(
            title='Goals vs Required Monthly SIPs',
            barmode='group',
            showlegend=True,
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': 'black'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Clear all goals button
        if st.button('🗑️ Clear All Goals', type='secondary', use_container_width=True):
            st.session_state.goals = []
            save_json(GOALS_FILE, [])
            st.rerun()
    
    else:
        # Empty state with encouragement
        st.markdown("""
        <div class='financial-sticker' style='text-align: center;'>
            <h3>🎯 No Goals Set Yet!</h3>
            <p>Start by adding your first financial goal above. 🚀</p>
            <p><small>Examples: Down payment for house, children's education, retirement corpus, dream vacation</small></p>
        </div>
        """, unsafe_allow_html=True)

# --- Portfolio Page ---
elif st.session_state.current_page == "💼 Portfolio":
    st.header('💼 Portfolio Manager')
    st.markdown("""
    <div class='financial-sticker'>
        <h3>Track Your Investments</h3>
        <p>Add your current holdings and visualize your portfolio allocation.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form('portfolio_form'):
        cols = st.columns(3)
        name = cols[0].text_input('Holding Name', placeholder='e.g., Reliance Stocks, SBI Mutual Fund')
        amt = cols[1].number_input('Amount (₹)', min_value=0.0, value=0.0, step=1000.0)
        category = cols[2].selectbox('Category', ['Stocks', 'Mutual Funds', 'FD/RD', 'Gold', 'Real Estate', 'Other'])
        
        add = cols[2].form_submit_button('➕ Add Holding')
        
        if add and name and amt>0:
            st.session_state.portfolio.append({'name': name, 'amount': amt, 'category': category})
            save_json(PORTFOLIO_FILE, st.session_state.portfolio)
            st.success('✅ Holding added successfully!')

    if st.session_state.portfolio:
        pfdf = pd.DataFrame(st.session_state.portfolio)
        total_portfolio = pfdf['amount'].sum()
        pfdf['pct'] = (pfdf['amount'] / total_portfolio) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader('Portfolio Holdings')
            st.dataframe(pfdf.style.format({
                'amount': '₹{:,.0f}',
                'pct': '{:.1f}%'
            }), use_container_width=True)
            
            # Portfolio summary
            st.metric("Total Portfolio Value", format_currency(total_portfolio))
            
        with col2:
            st.subheader('Portfolio Allocation')
            fig = px.pie(pfdf, names='category', values='amount', title='Investment Allocation by Category')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': 'black'})
            st.plotly_chart(fig, use_container_width=True)

        # Download option
        csv = pfdf.to_csv(index=False).encode('utf-8')
        st.download_button('📥 Download Portfolio CSV', csv, 'portfolio.csv', 'text/csv')

    else:
        st.info("No portfolio holdings added yet. Use the form above to add your investments.")

# --- Export Page ---
elif st.session_state.current_page == "📥 Export":
    st.header('📥 Export Reports & Data')
    
    if not st.session_state.user_data:
        st.info('📊 No financial data found. Please create a snapshot first.')
    else:
        analyzer = FinancialAnalyzer(st.session_state.user_data)
        metrics = analyzer.calculate_financial_metrics()
        advanced = analyzer.calculate_advanced_metrics(metrics)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📄 Report Options")
            
            if st.button('📊 Generate Comprehensive Report', use_container_width=True):
                # Create a simple text report (you can enhance this with PDF generation)
                report_content = f"""
                FINANCIAL HEALTH REPORT
                Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                
                PERSONAL FINANCE SNAPSHOT:
                - Monthly Income: {format_currency(metrics['monthly_income'])}
                - Monthly Savings: {format_currency(metrics['monthly_savings'])}
                - Savings Rate: {metrics['savings_rate']:.1f}%
                - Net Worth: {format_currency(advanced['net_worth'])}
                
                ML INSIGHTS:
                - Risk Profile: {advanced['ml_risk_profile']}
                - Risk Score: {advanced['ml_risk_score']:.1f}/10
                - Financial Health Score: {advanced['health_score']}/100
                
                RECOMMENDATIONS:
                {chr(10).join(['- ' + insight for insight in advanced.get('spending_insights', [])])}
                """
                
                st.download_button(
                    '📥 Download Text Report', 
                    report_content, 
                    f'financial_report_{datetime.now().strftime("%Y%m%d")}.txt', 
                    'text/plain'
                )

        with col2:
            st.markdown("### 💾 Data Export")
            if st.button('📁 Download Snapshot JSON', use_container_width=True):
                snapshot_json = json.dumps(st.session_state.user_data, indent=2).encode('utf-8')
                st.download_button(
                    '📥 Download JSON', 
                    snapshot_json, 
                    'financial_snapshot.json', 
                    'application/json'
                )
            
            if st.session_state.goals:
                if st.button('🎯 Download Goals Data', use_container_width=True):
                    goals_json = json.dumps(st.session_state.goals, indent=2).encode('utf-8')
                    st.download_button(
                        '📥 Download Goals JSON', 
                        goals_json, 
                        'financial_goals.json', 
                        'application/json'
                    )

# --- Developer Page ---
elif st.session_state.current_page == "👨‍💻 Developer":
    st.header('👨‍💻 About the Developer')
    
    # Developer Profile
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 20px; color: white; margin-bottom: 2rem;'>
        <div style='font-size: 4rem; margin-bottom: 1rem;'>🤖</div>
        <h1 style='color: white; margin-bottom: 0.5rem;'>Ayush Shukla</h1>
        <p style='font-size: 1.2em; opacity: 0.9; margin-bottom: 0;'>Data Scientist & ML Engineer</p>
        <p style='opacity: 0.8;'>Building intelligent financial solutions with machine learning</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Skills & Specialization
    st.markdown("### 🔬 Data Science Specialization")
    
    ds_cols = st.columns(3)
    
    with ds_cols[0]:
        st.markdown("""
        <div class='metric-card'>
            <h4>🤖 Machine Learning</h4>
            <p>Predictive Modeling & AI Algorithms</p>
            <p><small>Random Forests, Neural Networks, Time Series Analysis</small></p>
        </div>
        """, unsafe_allow_html=True)
    
    with ds_cols[1]:
        st.markdown("""
        <div class='metric-card'>
            <h4>📈 Financial Analytics</h4>
            <p>Risk Analysis & Investment Forecasting</p>
            <p><small>Portfolio Optimization, Technical Analysis</small></p>
        </div>
        """, unsafe_allow_html=True)
    
    with ds_cols[2]:
        st.markdown("""
        <div class='metric-card'>
            <h4>🔄 MLOps & Deployment</h4>
            <p>Model Deployment & Scalable Systems</p>
            <p><small>Streamlit, FastAPI, Cloud Deployment</small></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Contact Information
    st.markdown("### 📱 Connect & Collaborate")
    
    contact_cols = st.columns(4)
    
    with contact_cols[0]:
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: #1f2937; border-radius: 12px; color: white;'>
            <div style='font-size: 2rem;'>🐙</div>
            <p><strong>GitHub</strong></p>
            <p style='font-size: 0.8em;'>ayushshukla</p>
        </div>
        """, unsafe_allow_html=True)
    
    with contact_cols[1]:
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: #0369a1; border-radius: 12px; color: white;'>
            <div style='font-size: 2rem;'>💼</div>
            <p><strong>LinkedIn</strong></p>
            <p style='font-size: 0.8em;'>ayushshukla</p>
        </div>
        """, unsafe_allow_html=True)
    
    with contact_cols[2]:
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: #dc2626; border-radius: 12px; color: white;'>
            <div style='font-size: 2rem;'>📧</div>
            <p><strong>Email</strong></p>
            <p style='font-size: 0.8em;'>Contact Me</p>
        </div>
        """, unsafe_allow_html=True)
    
    with contact_cols[3]:
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: #7c3aed; border-radius: 12px; color: white;'>
            <div style='font-size: 2rem;'>🌐</div>
            <p><strong>Portfolio</strong></p>
            <p style='font-size: 0.8em;'>ayushshukla.xyz</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Project Details
    st.markdown("---")
    st.markdown("### 🚀 About This Project")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <h4>🎯 Project Vision</h4>
            <p>Democratize financial knowledge through AI and make personal finance management accessible to everyone.</p>
            <p><strong>Features:</strong></p>
            <ul>
                <li>ML-powered risk assessment</li>
                <li>Intelligent goal planning</li>
                <li>Real-time investment analysis</li>
                <li>Personalized recommendations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <h4>🛠️ Technology Stack</h4>
            <p><strong>Frontend:</strong> Streamlit, Plotly</p>
            <p><strong>Backend:</strong> Python, Pandas, NumPy</p>
            <p><strong>ML Algorithms:</strong> Custom ensemble methods</p>
            <p><strong>Data:</strong> Simulated financial data</p>
            <p><strong>Deployment:</strong> Streamlit Cloud</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Call to Action
    st.markdown("""
    <div class='financial-sticker' style='text-align: center;'>
        <h3>💡 Let's Build Together!</h3>
        <p>Interested in collaborating on data science projects or have ideas for improvement?</p>
        <p>Feel free to reach out through any of the platforms above.</p>
    </div>
    """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 1rem;'>
    <p>Built with ❤️ by Ayush Shukla | AI Financial Advisor v3.0</p>
    <p>🤖 Powered by Machine Learning & Data Science | 📊 Your Financial Companion</p>
</div>
""", unsafe_allow_html=True)
