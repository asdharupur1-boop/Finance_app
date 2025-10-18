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

# Super Impressive Enhanced Light Theme
st.markdown("""
<style>
    /* Global styles */
    .main {
        background-color: #ffffff;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    .main .block-container {
        background-color: #ffffff;
        padding: 2.5rem 1.5rem;
        border-radius: 20px;
        box-shadow: 0 8px 40px rgba(0,0,0,0.12);
        margin: 1.5rem auto;
        max-width: 1400px;
        border: 1px solid #f1f5f9;
    }
    
    /* Perfect text visibility */
    h1, h2, h3, h4, h5, h6 {
        color: #1e293b !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif;
    }
    
    h1 { font-size: 2.75rem !important; margin-bottom: 1rem !important; }
    h2 { font-size: 2.25rem !important; margin-bottom: 0.75rem !important; }
    h3 { font-size: 1.75rem !important; margin-bottom: 0.5rem !important; }
    h4 { font-size: 1.5rem !important; margin-bottom: 0.5rem !important; }
    
    p, div, span, label, .stMarkdown, .stText {
        color: #374151 !important;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        line-height: 1.7;
    }
    
    /* Enhanced widget styling */
    .stNumberInput>div>div>input, .stTextInput>div>div>input {
        color: #1e293b !important;
        background-color: #ffffff !important;
        border: 2.5px solid #e2e8f0 !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        padding: 14px 18px !important;
    }
    
    .stSelectbox>div>div>select {
        color: #1e293b !important;
        background-color: #ffffff !important;
        border: 2.5px solid #e2e8f0 !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        padding: 12px !important;
    }
    
    .stSlider>div>div>div>div {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
        height: 8px !important;
        border-radius: 10px !important;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 16px 32px;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.4s ease;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        margin: 8px 0;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.6);
    }
    
    /* Enhanced metric cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 2.5px solid #f1f5f9;
        border-radius: 20px;
        padding: 2.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        transition: all 0.4s ease;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.15);
        border-color: #3b82f6;
    }
    
    .metric-value {
        font-size: 3rem !important;
        font-weight: 800 !important;
        color: #1e293b !important;
        margin: 1rem 0;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-label {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
        margin-bottom: 1rem;
    }
    
    /* Enhanced custom components */
    .ml-insight {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 3px solid #7dd3fc;
        border-radius: 16px;
        padding: 1.75rem;
        margin: 1.25rem 0;
        color: #0c4a6e !important;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 6px 20px rgba(125, 211, 252, 0.2);
        border-left: 6px solid #0ea5e9;
    }
    
    .financial-sticker {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 3px solid #86efac;
        border-radius: 16px;
        padding: 1.75rem;
        margin: 1.25rem 0;
        color: #166534 !important;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 6px 20px rgba(134, 239, 172, 0.2);
        border-left: 6px solid #22c55e;
    }
    
    .ai-prediction {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 3px solid #fcd34d;
        border-radius: 16px;
        padding: 1.75rem;
        margin: 1.25rem 0;
        color: #92400e !important;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 6px 20px rgba(252, 211, 77, 0.2);
        border-left: 6px solid #f59e0b;
    }
    
    /* Quiz specific styling */
    .quiz-question {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 3px solid #7dd3fc;
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 8px 30px rgba(125, 211, 252, 0.25);
    }
    
    .quiz-option {
        background: white;
        border: 2.5px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.5rem;
        margin: 1rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .quiz-option:hover {
        border-color: #3b82f6;
        background-color: #f0f9ff;
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.15);
    }
    
    .quiz-option.selected {
        border-color: #3b82f6;
        background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 100%);
        color: #1e40af;
        font-weight: 700;
        transform: translateY(-2px);
    }
    
    /* Personality result cards */
    .personality-conservative {
        background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 100%);
        border: 4px solid #3b82f6;
        border-radius: 24px;
        padding: 3rem;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 12px 40px rgba(59, 130, 246, 0.25);
    }
    
    .personality-moderate {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 4px solid #f59e0b;
        border-radius: 24px;
        padding: 3rem;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 12px 40px rgba(245, 158, 11, 0.25);
    }
    
    .personality-aggressive {
        background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
        border: 4px solid #ef4444;
        border-radius: 24px;
        padding: 3rem;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 12px 40px rgba(239, 68, 68, 0.25);
    }
    
    .personality-balanced {
        background: linear-gradient(135deg, #bbf7d0 0%, #86efac 100%);
        border: 4px solid #22c55e;
        border-radius: 24px;
        padding: 3rem;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 12px 40px rgba(34, 197, 94, 0.25);
    }
    
    /* Enhanced progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
        border-radius: 12px !important;
        height: 10px !important;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1.5rem 1rem;
            margin: 1rem;
        }
        
        .metric-card {
            padding: 2rem;
            margin: 1rem 0;
        }
        
        .metric-value {
            font-size: 2.5rem !important;
        }
    }
    
    /* Plotly graph enhancements */
    .js-plotly-plot .plotly, .js-plotly-plot .plotly div {
        background-color: transparent !important;
    }
    
    /* Enhanced social links */
    .social-link {
        display: inline-block;
        padding: 18px 28px;
        margin: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        text-decoration: none;
        border-radius: 14px;
        transition: all 0.4s ease;
        text-align: center;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .social-link:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.6);
        color: white !important;
        text-decoration: none;
    }
    
    /* Data table enhancements */
    .dataframe {
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12) !important;
        font-size: 1.1rem !important;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin: 2.5rem 0 1.5rem 0;
        text-align: center;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4);
    }
    
    /* Tab enhancements */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        padding: 0 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 70px;
        white-space: pre-wrap;
        background-color: #f8fafc;
        border-radius: 16px 16px 0 0;
        gap: 10px;
        padding: 20px 24px;
        font-weight: 700;
        font-size: 1.1rem;
        border: 2px solid #e2e8f0;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-color: #667eea !important;
    }
    
    /* Form enhancements */
    .stForm {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 2.5px solid #f1f5f9;
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

# --- Financial Behavior Quiz Class ---
class FinancialBehaviorQuiz:
    def __init__(self):
        self.questions = [
            {
                'id': 1,
                'question': '💰 How do you react when the stock market drops by 20% in a short period?',
                'options': [
                    {'text': 'Sell everything immediately to prevent further losses', 'score': 1, 'type': 'risk_aversion'},
                    {'text': 'Hold my investments and wait for recovery', 'score': 3, 'type': 'patience'},
                    {'text': 'Review my portfolio but maintain my strategy', 'score': 5, 'type': 'discipline'},
                    {'text': 'Buy more stocks at discounted prices', 'score': 7, 'type': 'opportunistic'}
                ]
            },
            {
                'id': 2,
                'question': '📈 What is your primary investment goal?',
                'options': [
                    {'text': 'Capital preservation and safety of principal', 'score': 2, 'type': 'conservative'},
                    {'text': 'Steady growth with minimal volatility', 'score': 4, 'type': 'moderate'},
                    {'text': 'Balanced growth with some risk for better returns', 'score': 6, 'type': 'balanced'},
                    {'text': 'Maximum growth potential, accepting higher volatility', 'score': 8, 'type': 'aggressive'}
                ]
            },
            {
                'id': 3,
                'question': '⏰ What is your preferred investment time horizon?',
                'options': [
                    {'text': 'Short-term (1-2 years) for specific goals', 'score': 2, 'type': 'short_term'},
                    {'text': 'Medium-term (3-5 years) for planned expenses', 'score': 4, 'type': 'medium_term'},
                    {'text': 'Long-term (5-10 years) for wealth building', 'score': 6, 'type': 'long_term'},
                    {'text': 'Very long-term (10+ years) for retirement', 'score': 8, 'type': 'retirement'}
                ]
            },
            {
                'id': 4,
                'question': '🎯 How much volatility can you tolerate in your portfolio?',
                'options': [
                    {'text': 'Minimal - I prefer stable, predictable returns', 'score': 1, 'type': 'low_volatility'},
                    {'text': 'Low - Small fluctuations are acceptable', 'score': 3, 'type': 'moderate_volatility'},
                    {'text': 'Moderate - I can handle typical market swings', 'score': 5, 'type': 'medium_volatility'},
                    {'text': 'High - I can withstand significant ups and downs', 'score': 7, 'type': 'high_volatility'}
                ]
            },
            {
                'id': 5,
                'question': '📊 How experienced are you with investing?',
                'options': [
                    {'text': 'Beginner - Just starting to learn about investing', 'score': 2, 'type': 'novice'},
                    {'text': 'Some experience - Have made a few investments', 'score': 4, 'type': 'intermediate'},
                    {'text': 'Experienced - Regular investor with good knowledge', 'score': 6, 'type': 'experienced'},
                    {'text': 'Expert - Extensive experience and advanced knowledge', 'score': 8, 'type': 'expert'}
                ]
            },
            {
                'id': 6,
                'question': '💸 What percentage of your income are you comfortable investing?',
                'options': [
                    {'text': 'Less than 10% - Prefer to keep most cash available', 'score': 2, 'type': 'low_investment'},
                    {'text': '10-20% - Regular savings with some investment', 'score': 4, 'type': 'moderate_investment'},
                    {'text': '20-30% - Significant portion for wealth building', 'score': 6, 'type': 'high_investment'},
                    {'text': 'Over 30% - Maximum allocation for growth', 'score': 8, 'type': 'aggressive_investment'}
                ]
            },
            {
                'id': 7,
                'question': '🛡️ How important is having an emergency fund to you?',
                'options': [
                    {'text': 'Extremely important - 6+ months of expenses', 'score': 2, 'type': 'conservative_safety'},
                    {'text': 'Very important - 3-6 months of expenses', 'score': 4, 'type': 'moderate_safety'},
                    {'text': 'Somewhat important - 1-3 months of expenses', 'score': 6, 'type': 'balanced_safety'},
                    {'text': 'Minimal - Prefer to invest most available funds', 'score': 8, 'type': 'aggressive_safety'}
                ]
            },
            {
                'id': 8,
                'question': '🎲 How do you approach financial decisions?',
                'options': [
                    {'text': 'Very cautious - Extensive research before any decision', 'score': 2, 'type': 'cautious'},
                    {'text': 'Careful - Research and consult before deciding', 'score': 4, 'type': 'deliberate'},
                    {'text': 'Balanced - Research but willing to take calculated risks', 'score': 6, 'type': 'calculated'},
                    {'text': 'Opportunistic - Quick to act on good opportunities', 'score': 8, 'type': 'opportunistic'}
                ]
            }
        ]
    
    def calculate_personality(self, answers):
        """Calculate investment personality based on quiz answers"""
        total_score = sum(answers.values())
        max_score = len(self.questions) * 8
        
        score_percentage = (total_score / max_score) * 100
        
        if score_percentage <= 30:
            personality = "🛡️ Conservative Defender"
            risk_level = "Low"
            description = "You prioritize capital preservation and prefer stable, low-risk investments. Safety is your top concern with focus on guaranteed returns."
            color = "#3b82f6"
        elif score_percentage <= 50:
            personality = "📊 Cautious Planner"
            risk_level = "Low to Moderate"
            description = "You prefer steady growth with minimal risk, balancing safety with some growth opportunities through diversified approach."
            color = "#f59e0b"
        elif score_percentage <= 70:
            personality = "⚖️ Balanced Grower"
            risk_level = "Moderate"
            description = "You seek balanced growth through diversified investments, accepting moderate risk for better returns with systematic approach."
            color = "#22c55e"
        else:
            personality = "🚀 Aggressive Builder"
            risk_level = "High"
            description = "You're comfortable with significant risk and volatility in pursuit of maximum growth potential through equity-focused investments."
            color = "#ef4444"
        
        return {
            'personality': personality,
            'risk_level': risk_level,
            'score': total_score,
            'score_percentage': score_percentage,
            'description': description,
            'color': color
        }
    
    def get_recommendations(self, personality_result):
        """Get personalized investment recommendations based on personality"""
        personality = personality_result['personality']
        
        if "Conservative" in personality:
            return {
                'asset_allocation': {
                    'Debt Funds & FDs': '60-70%',
                    'Large Cap Equity': '20-25%',
                    'Gold': '5-10%',
                    'Cash': '5%'
                },
                'recommended_funds': [
                    'ICICI Prudential Corporate Bond Fund',
                    'HDFC Short Term Debt Fund',
                    'SBI Magnum Gilt Fund',
                    'Axis Bluechip Fund'
                ],
                'strategy': 'Focus on capital preservation with stable returns. Ideal for short-term goals and low-risk tolerance.',
                'suggestions': [
                    'Build a strong emergency fund (6+ months)',
                    'Prioritize debt instruments and fixed deposits',
                    'Consider tax-saving fixed deposits',
                    'Start with small SIPs in large cap funds'
                ],
                'risk_notes': 'Your portfolio will have minimal volatility with focus on capital protection.'
            }
        elif "Cautious" in personality:
            return {
                'asset_allocation': {
                    'Debt Funds': '50-60%',
                    'Large Cap Equity': '30-35%',
                    'Gold': '5%',
                    'Mid Cap Equity': '5-10%'
                },
                'recommended_funds': [
                    'Mirae Asset Large Cap Fund',
                    'Kotak Corporate Bond Fund',
                    'Axis Midcap Fund',
                    'SBI Gold Fund'
                ],
                'strategy': 'Balanced approach with focus on steady growth while managing risk effectively.',
                'suggestions': [
                    'Maintain 4-6 months emergency fund',
                    'Systematic Investment Plans (SIPs) in diversified funds',
                    'Consider balanced advantage funds',
                    'Regular portfolio reviews every 6 months'
                ],
                'risk_notes': 'Moderate growth with controlled risk exposure.'
            }
        elif "Balanced" in personality:
            return {
                'asset_allocation': {
                    'Equity Funds': '60-70%',
                    'Debt Funds': '20-25%',
                    'Gold': '5%',
                    'International Funds': '5-10%'
                },
                'recommended_funds': [
                    'Parag Parikh Flexi Cap Fund',
                    'ICICI Prudential Bluechip Fund',
                    'Kotak Emerging Equity Fund',
                    'Motilal Oswal NASDAQ 100 ETF'
                ],
                'strategy': 'Growth-oriented approach with diversified portfolio across market caps and asset classes.',
                'suggestions': [
                    '3-4 months emergency fund sufficient',
                    'Aggressive SIPs for long-term goals',
                    'Consider sectoral funds for diversification',
                    'Regular rebalancing of portfolio annually'
                ],
                'risk_notes': 'Balanced risk-reward ratio for optimal growth.'
            }
        else:  # Aggressive
            return {
                'asset_allocation': {
                    'Equity Funds': '75-85%',
                    'Debt Funds': '10-15%',
                    'Small Cap Funds': '5-10%',
                    'International Funds': '5%'
                },
                'recommended_funds': [
                    'SBI Small Cap Fund',
                    'Axis Small Cap Fund',
                    'Mirae Asset Emerging Bluechip Fund',
                    'PGIM India Midcap Opportunities Fund'
                ],
                'strategy': 'Maximum growth focus with high equity exposure, suitable for long-term wealth creation.',
                'suggestions': [
                    '2-3 months emergency fund adequate',
                    'Direct equity investments can be considered',
                    'Sector rotation strategies',
                    'Systematic Transfer Plans for lump sum investments'
                ],
                'risk_notes': 'High growth potential with significant volatility exposure.'
            }

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
            return "🛡️ Conservative", 0.3, risk_score, "Low risk appetite suitable for stable investments like FDs and debt funds"
        elif risk_score < 7:
            return "⚖️ Balanced", 0.5, risk_score, "Moderate risk with balanced growth approach across equity and debt"
        else:
            return "🚀 Aggressive", 0.7, risk_score, "High risk tolerance suitable for equity-heavy portfolios for maximum returns"
    
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
            color = "#10b981"
        elif final_probability >= 0.6:
            confidence = "✅ Moderate confidence - Minor adjustments may be needed"
            color = "#f59e0b"
        elif final_probability >= 0.4:
            confidence = "⚠️ Low confidence - Consider increasing savings or extending timeline"
            color = "#f97316"
        else:
            confidence = "🚨 Very low confidence - Goal may be unrealistic with current approach"
            color = "#ef4444"
            
        return final_probability, confidence, color

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

# --- Initialize Session State ---
if 'user_data' not in st.session_state:
    st.session_state.user_data = load_json(SNAPSHOT_FILE, {})
if 'goals' not in st.session_state:
    st.session_state.goals = load_json(GOALS_FILE, [])
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = load_json(PORTFOLIO_FILE, [])
if 'current_page' not in st.session_state:
    st.session_state.current_page = "📊 Snapshot"
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False

# --- Enhanced Mutual Fund Data ---
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
        'Rating': [5, 5, 5, 4, 5, 4, 5, 4, 5, 4, 4, 3],
        'Expense Ratio': [0.5, 0.6, 0.8, 0.75, 1.0, 1.1, 0.7, 0.8, 0.6, 0.65, 0.3, 0.35]
    }
    return pd.DataFrame(data)

# --- Enhanced Plotly Theme ---
def apply_plotly_theme(fig):
    """Apply consistent theme to all Plotly charts"""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="Inter, sans-serif",
            size=16,
            color="#1e293b"
        ),
        title=dict(
            font=dict(
                size=22,
                color="#1e293b",
                family="Inter, sans-serif"
            ),
            x=0.5,
            xanchor='center'
        ),
        legend=dict(
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='#e2e8f0',
            borderwidth=2,
            font=dict(
                size=14,
                color="#374151"
            )
        ),
        xaxis=dict(
            gridcolor='#e2e8f0',
            gridwidth=2,
            tickfont=dict(size=14, color="#64748b")
        ),
        yaxis=dict(
            gridcolor='#e2e8f0',
            gridwidth=2,
            tickfont=dict(size=14, color="#64748b")
        )
    )
    return fig

# --- Main App Header ---
st.title('🤖 AI Financial Advisor')
st.markdown("""
<div class='section-header'>
    <h2 style='color: white; margin: 0;'>Advanced ML-Powered Financial Planning</h2>
    <p style='color: white; margin: 0.5rem 0 0 0; opacity: 0.95; font-size: 1.3rem; font-weight: 500;'>
    Smart Analytics • ML Predictions • Data-Driven Insights • Personalized Recommendations
    </p>
</div>
""", unsafe_allow_html=True)

# --- Enhanced Navigation ---
nav_options = [
    "📊 Snapshot", "📈 Dashboard", "🤖 ML Insights", 
    "🧠 Behavior Quiz", "💹 Investment Center", "🎯 Goals Planner", 
    "💼 Portfolio", "📥 Export", "👨‍💻 Developer"
]

# Create enhanced navigation columns
st.markdown("<br>", unsafe_allow_html=True)
cols = st.columns(len(nav_options))
for i, option in enumerate(nav_options):
    with cols[i]:
        if st.button(option, key=f"nav_{i}", use_container_width=True):
            st.session_state.current_page = option

st.markdown("---")

# --- Snapshot Page ---
if st.session_state.current_page == "📊 Snapshot":
    st.header('📊 Financial Snapshot')
    st.markdown("""
    <div class='financial-sticker'>
        <h3>🚀 Build Your Complete Financial Profile</h3>
        <p>Complete this detailed snapshot to unlock personalized AI-powered financial insights and recommendations.</p>
    </div>
    """, unsafe_allow_html=True)
    
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
                                            help="1: Beginner, 2: Some knowledge, 3: Intermediate, 4: Experienced, 5: Expert")
            
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
                'assets': st.session_state.user_data.get('assets', {}),
                'liabilities': st.session_state.user_data.get('liabilities', {})
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
        analyzer = MLFinancialPredictor()
        metrics = {
            'monthly_income': user_data.get('monthly_income', 0),
            'total_expenses': sum(user_data.get('expenses', {}).values()),
            'monthly_savings': user_data.get('monthly_income', 0) - sum(user_data.get('expenses', {}).values()),
            'savings_rate': ((user_data.get('monthly_income', 0) - sum(user_data.get('expenses', {}).values())) / user_data.get('monthly_income', 1)) * 100,
            'current_savings': user_data.get('current_savings', 0)
        }
        
        # Top Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>💰 Monthly Income</div>
                <div class='metric-value'>{format_currency(metrics['monthly_income'])}</div>
                <p>Gross monthly earnings</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>📊 Savings Rate</div>
                <div class='metric-value'>{metrics['savings_rate']:.1f}%</div>
                <p>Of monthly income saved</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            risk_profile, _, risk_score, _ = analyzer.predict_risk_tolerance(user_data)
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>🛡️ Risk Profile</div>
                <div class='metric-value'>{risk_profile}</div>
                <p>Score: {risk_score:.1f}/10</p>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            net_worth = sum(user_data.get('assets', {}).values()) - sum(user_data.get('liabilities', {}).values())
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>🏦 Net Worth</div>
                <div class='metric-value'>{format_currency(net_worth)}</div>
                <p>Total assets minus liabilities</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Expense Analysis
        st.markdown("### 💸 Expense Analysis")
        expense_data = {k: v for k, v in user_data.get('expenses', {}).items() if v > 0}
        if expense_data:
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(values=list(expense_data.values()), 
                           names=list(expense_data.keys()),
                           title='Expense Distribution')
                fig = apply_plotly_theme(fig)
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

# --- ML Insights Page ---
elif st.session_state.current_page == "🤖 ML Insights":
    st.header('🤖 Advanced ML Insights')
    
    if not st.session_state.user_data:
        st.warning("🚨 Please create a financial snapshot first to get ML insights!")
    else:
        user_data = st.session_state.user_data
        analyzer = MLFinancialPredictor()
        
        # Enhanced Risk Analysis
        st.markdown("### 🎯 Deep Risk Analysis")
        risk_profile, risk_allocation, risk_score, risk_explanation = analyzer.predict_risk_tolerance(user_data)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>🤖 ML Risk Assessment</h3>
                <div style='text-align: center;'>
                    <h1 style='color: #7c3aed; font-size: 2.5rem;'>{risk_profile}</h1>
                    <p style='font-size: 1.2rem;'><strong>Risk Score:</strong> {risk_score:.1f}/10</p>
                    <p style='font-size: 1.1rem;'>{risk_explanation}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Risk Factors Breakdown
            st.markdown("### 📊 Risk Factor Analysis")
            for factor, score in analyzer.risk_factors.items():
                st.progress(min(score/2, 1.0), text=f"{factor}: {score:.2f}")
        
        with col2:
            # Goal Success Predictions
            if st.session_state.goals:
                st.markdown("### 🎯 ML Goal Success Probability")
                for goal in st.session_state.goals:
                    probability, confidence, color = analyzer.predict_goal_success_probability(goal, user_data)
                    
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"""
                        <div class='metric-card'>
                            <h4>🎯 {goal['name']}</h4>
                            <p>Target: {format_currency(goal['amount'])} in {goal['years']} years | Expected Return: {goal.get('return', 8)}%</p>
                            <div style='background: #e2e8f0; border-radius: 12px; height: 30px; margin: 15px 0;'>
                                <div style='background: {color}; 
                                          width: {probability*100}%; height: 100%; border-radius: 12px; 
                                          text-align: center; color: white; font-weight: bold; line-height: 30px; font-size: 1.1rem;'>
                                    {probability*100:.1f}% Success Probability
                                </div>
                            </div>
                            <p style='font-size: 1.1rem;'><strong>ML Assessment:</strong> {confidence}</p>
                        </div>
                        """, unsafe_allow_html=True)

# --- Behavior Quiz Page ---
elif st.session_state.current_page == "🧠 Behavior Quiz":
    st.header('🧠 Financial Behavior Quiz')
    st.markdown("""
    <div class='financial-sticker'>
        <h3>Discover Your Investment Personality</h3>
        <p>This quiz will help us understand your financial behavior and provide personalized investment recommendations.</p>
        <p><strong>Time:</strong> 5-7 minutes | <strong>Questions:</strong> 8</p>
    </div>
    """, unsafe_allow_html=True)
    
    quiz = FinancialBehaviorQuiz()
    
    if not st.session_state.quiz_completed:
        # Show current question
        current_q = quiz.questions[st.session_state.current_question]
        
        st.markdown(f"""
        <div class='quiz-question'>
            <h3>Question {st.session_state.current_question + 1} of {len(quiz.questions)}</h3>
            <h4>{current_q['question']}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Display options
        selected_option = None
        
        for i, option in enumerate(current_q['options']):
            is_selected = st.session_state.quiz_answers.get(current_q['id']) == i
            css_class = "quiz-option selected" if is_selected else "quiz-option"
            
            st.markdown(f"""
            <div class='{css_class}'>
                {option['text']}
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Select Option {i+1}", key=f"opt_{current_q['id']}_{i}", use_container_width=True):
                st.session_state.quiz_answers[current_q['id']] = i
                st.rerun()
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.session_state.current_question > 0:
                if st.button("⬅️ Previous", use_container_width=True):
                    st.session_state.current_question -= 1
                    st.rerun()
        
        with col2:
            progress = (st.session_state.current_question + 1) / len(quiz.questions)
            st.progress(progress, text=f"Progress: {int(progress*100)}%")
        
        with col3:
            if st.session_state.current_question < len(quiz.questions) - 1:
                if st.button("Next ➡️", use_container_width=True):
                    if current_q['id'] in st.session_state.quiz_answers:
                        st.session_state.current_question += 1
                        st.rerun()
                    else:
                        st.warning("Please select an option before proceeding.")
            else:
                if st.button("Complete Quiz 🎯", type="primary", use_container_width=True):
                    if current_q['id'] in st.session_state.quiz_answers:
                        st.session_state.quiz_completed = True
                        st.rerun()
                    else:
                        st.warning("Please select an option to complete the quiz.")
    
    else:
        # Quiz completed - show results
        st.balloons()
        st.success("🎉 Quiz Completed! Here's Your Investment Personality Analysis")
        
        # Calculate results
        quiz = FinancialBehaviorQuiz()
        answers_with_scores = {}
        
        for q_id, option_index in st.session_state.quiz_answers.items():
            question = next(q for q in quiz.questions if q['id'] == q_id)
            selected_option = question['options'][option_index]
            answers_with_scores[q_id] = selected_option['score']
        
        personality_result = quiz.calculate_personality(answers_with_scores)
        recommendations = quiz.get_recommendations(personality_result)
        
        # Display Personality Results
        st.markdown("### 🎯 Your Investment Personality")
        
        personality_class = ""
        if "Conservative" in personality_result['personality']:
            personality_class = "personality-conservative"
        elif "Cautious" in personality_result['personality']:
            personality_class = "personality-moderate"
        elif "Balanced" in personality_result['personality']:
            personality_class = "personality-balanced"
        else:
            personality_class = "personality-aggressive"
        
        st.markdown(f"""
        <div class='{personality_class}'>
            <h2 style='font-size: 2.5rem; margin-bottom: 1rem;'>{personality_result['personality']}</h2>
            <h3 style='font-size: 1.8rem; color: {personality_result["color"]};'>Risk Level: {personality_result['risk_level']}</h3>
            <p style='font-size: 1.3rem; line-height: 1.8;'>{personality_result['description']}</p>
            <p style='font-size: 1.2rem;'><strong>Personality Score:</strong> {personality_result['score']} ({personality_result['score_percentage']:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display Recommendations
        st.markdown("### 💡 Personalized Investment Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Recommended Asset Allocation")
            allocation_data = []
            for asset, percentage in recommendations['asset_allocation'].items():
                allocation_data.append([asset, percentage])
            
            allocation_df = pd.DataFrame(allocation_data, columns=['Asset Class', 'Allocation'])
            st.dataframe(allocation_df.style.set_properties(**{
                'font-size': '1.2rem',
                'text-align': 'center'
            }), use_container_width=True)
            
            # Asset allocation pie chart
            fig = px.pie(allocation_df, values='Allocation', names='Asset Class', 
                        title='Recommended Portfolio Allocation')
            fig = apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🏆 Recommended Funds")
            for i, fund in enumerate(recommendations['recommended_funds'], 1):
                st.markdown(f"**{i}. {fund}**")
            
            st.markdown("#### 🎯 Investment Strategy")
            st.markdown(f"""
            <div class='ai-prediction'>
                <p style='font-size: 1.2rem;'>{recommendations['strategy']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 💡 Suggestions")
            for suggestion in recommendations['suggestions']:
                st.markdown(f"• {suggestion}")
        
        # Reset quiz button
        st.markdown("---")
        if st.button("🔄 Take Quiz Again", use_container_width=True):
            st.session_state.quiz_answers = {}
            st.session_state.current_question = 0
            st.session_state.quiz_completed = False
            st.rerun()

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
            st.subheader(f"Projection for {format_currency(invest_amt)} in {fund_name}")
            
            # Calculate projections for different periods
            periods = [1, 3, 5, 10]
            returns = [selected_fund['1Y Return'], selected_fund['3Y CAGR'], selected_fund['5Y CAGR'], selected_fund['5Y CAGR']]
            future_values = [invest_amt * ((1 + return_rate/100) ** period) 
                           for period, return_rate in zip(periods, returns)]
            profits = [fv - invest_amt for fv in future_values]
            
            # Visualization
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Initial Investment', x=[str(p) + 'Y' for p in periods], 
                                y=[invest_amt]*len(periods), marker_color='#94a3b8'))
            fig.add_trace(go.Bar(name='Projected Profit', x=[str(p) + 'Y' for p in periods], 
                                y=profits, marker_color='#10b981'))
            fig.update_layout(barmode='stack', title='Investment Growth Projection', 
                            showlegend=True)
            fig = apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed returns table
            returns_df = pd.DataFrame({
                'Period': [f'{p} Year{"s" if p>1 else ""}' for p in periods],
                'Expected Return %': returns,
                'Future Value': [format_currency(fv) for fv in future_values],
                'Profit': [format_currency(p) for p in profits]
            })
            st.dataframe(returns_df.style.format({
                'Expected Return %': '{:.1f}%'
            }), use_container_width=True)

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
            fig = apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

# --- Export Page ---
elif st.session_state.current_page == "📥 Export":
    st.header('📥 Export Reports & Data')
    
    if not st.session_state.user_data:
        st.info('📊 No financial data found. Please create a snapshot first.')
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📄 Report Options")
            
            if st.button('📊 Generate Comprehensive Report', use_container_width=True):
                # Create a simple text report
                report_content = f"""
                FINANCIAL HEALTH REPORT
                Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                
                PERSONAL FINANCE SNAPSHOT:
                - Monthly Income: {format_currency(st.session_state.user_data.get('monthly_income', 0))}
                - Monthly Expenses: {format_currency(sum(st.session_state.user_data.get('expenses', {}).values()))}
                - Current Savings: {format_currency(st.session_state.user_data.get('current_savings', 0))}
                - Investment Percentage: {st.session_state.user_data.get('investment_percentage', 0)}%
                
                FINANCIAL GOALS:
                {chr(10).join(['- ' + goal['name'] + f" (₹{goal['amount']:,})" for goal in st.session_state.goals])}
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

# --- Developer Page ---
elif st.session_state.current_page == "👨‍💻 Developer":
    st.header('👨‍💻 About the Developer')
    
    # Developer Profile
    st.markdown("""
    <div style='text-align: center; padding: 2.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 24px; color: white; margin-bottom: 2.5rem;'>
        <div style='font-size: 4.5rem; margin-bottom: 1.5rem;'>🤖</div>
        <h1 style='color: white; margin-bottom: 0.75rem; font-size: 3rem;'>Ayush Shukla</h1>
        <p style='font-size: 1.5rem; opacity: 0.95; margin-bottom: 0;'>Data Scientist & ML Engineer</p>
        <p style='opacity: 0.9; font-size: 1.2rem;'>Building intelligent financial solutions with machine learning</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Clickable Social Links
    st.markdown("### 📱 Connect & Collaborate")
    
    contact_cols = st.columns(4)
    
    with contact_cols[0]:
        st.markdown("""
        <a href="https://github.com/asdharupur1-boop/Finance_app" target="_blank" class="social-link">
            <div style='font-size: 2.5rem;'>🐙</div>
            <p><strong>GitHub</strong></p>
            <p style='font-size: 1rem;'>ayushshukla</p>
        </a>
        """, unsafe_allow_html=True)
    
    with contact_cols[1]:
        st.markdown("""
        <a href="https://www.linkedin.com/in/ayush-shukla-890072337" target="_blank" class="social-link">
            <div style='font-size: 2.5rem;'>💼</div>
            <p><strong>LinkedIn</strong></p>
            <p style='font-size: 1rem;'>ayushshukla</p>
        </a>
        """, unsafe_allow_html=True)
    
    with contact_cols[2]:
        st.markdown("""
        <a href="mailto:Asdharupur1@gmail.com" class="social-link">
            <div style='font-size: 2.5rem;'>📧</div>
            <p><strong>Email</strong></p>
            <p style='font-size: 1rem;'>Contact Me</p>
        </a>
        """, unsafe_allow_html=True)
    
    with contact_cols[3]:
        st.markdown("""
        <a href="https://github.com/asdharupur1-boop" target="_blank" class="social-link">
            <div style='font-size: 2.5rem;'>🌐</div>
            <p><strong>Portfolio</strong></p>
            <p style='font-size: 1rem;'>ayushshukla.xyz</p>
        </a>
        """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 2rem;'>
    <p style='font-size: 1.2rem; font-weight: 600;'>Built with ❤️ by Ayush Shukla | AI Financial Advisor v4.0</p>
    <p style='font-size: 1.1rem;'>🤖 Powered by Machine Learning & Data Science | 📊 Your Financial Companion</p>
</div>
""", unsafe_allow_html=True)

