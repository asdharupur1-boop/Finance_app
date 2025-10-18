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

# Import for PDF generation
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import base64

# Set page config
st.set_page_config(
    page_title='AI Financial Advisor — By Ayush Shukla', 
    page_icon='🤖', 
    layout='wide',
    initial_sidebar_state='auto'
)

# Enhanced Light Theme with Different Widget Colors
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
    
    /* Different text colors for better visibility */
    h1, h2, h3, h4, h5, h6 {
        color: #1e293b !important;
        font-weight: 600 !important;
    }
    
    p, div, span, label, .stMarkdown, .stText {
        color: #374151 !important;
    }
    
    /* Widget styling with different colors */
    .stNumberInput>div>div>input, .stTextInput>div>div>input {
        color: #1e293b !important;
        background-color: #f8fafc !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox>div>div>select {
        color: #1e293b !important;
        background-color: #f8fafc !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }
    
    .stSlider>div>div>div>div {
        background-color: #3b82f6 !important;
    }
    
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
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    
    /* Quiz specific styling */
    .quiz-question {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 2px solid #7dd3fc;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .quiz-option {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .quiz-option:hover {
        border-color: #3b82f6;
        background-color: #f0f9ff;
    }
    
    .quiz-option.selected {
        border-color: #3b82f6;
        background-color: #dbeafe;
    }
    
    /* Metric cards with different colors */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-color: #3b82f6;
    }
    
    /* Custom components with different colors */
    .ml-insight {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 2px solid #7dd3fc;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #0c4a6e !important;
    }
    
    .financial-sticker {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 2px solid #86efac;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #166534 !important;
    }
    
    .ai-prediction {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 2px solid #fcd34d;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #92400e !important;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border: 2px solid #fca5a5;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #dc2626 !important;
    }
    
    /* Personality result cards */
    .personality-conservative {
        background: linear-gradient(135deg, #dbeafe 0%, #93c5fd 100%);
        border: 3px solid #3b82f6;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
    }
    
    .personality-moderate {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 3px solid #f59e0b;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
    }
    
    .personality-aggressive {
        background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
        border: 3px solid #ef4444;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
    }
    
    .personality-balanced {
        background: linear-gradient(135deg, #bbf7d0 0%, #86efac 100%);
        border: 3px solid #22c55e;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
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
    
    /* Social links styling */
    .social-link {
        display: inline-block;
        padding: 10px 20px;
        margin: 5px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        text-decoration: none;
        border-radius: 8px;
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .social-link:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        color: white !important;
        text-decoration: none;
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
        max_score = len(self.questions) * 8  # 8 is max score per question
        
        score_percentage = (total_score / max_score) * 100
        
        if score_percentage <= 30:
            personality = "Conservative Defender"
            risk_level = "Low"
            description = "You prioritize capital preservation and prefer stable, low-risk investments. Safety is your top concern."
        elif score_percentage <= 50:
            personality = "Cautious Planner"
            risk_level = "Low to Moderate"
            description = "You prefer steady growth with minimal risk, balancing safety with some growth opportunities."
        elif score_percentage <= 70:
            personality = "Balanced Grower"
            risk_level = "Moderate"
            description = "You seek balanced growth through diversified investments, accepting moderate risk for better returns."
        else:
            personality = "Aggressive Builder"
            risk_level = "High"
            description = "You're comfortable with significant risk and volatility in pursuit of maximum growth potential."
        
        return {
            'personality': personality,
            'risk_level': risk_level,
            'score': total_score,
            'score_percentage': score_percentage,
            'description': description
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
                ]
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
                    'Regular portfolio reviews'
                ]
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
                    'Regular rebalancing of portfolio'
                ]
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
                ]
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
            return "Conservative", 0.3, risk_score, "Low risk appetite suitable for stable investments like FDs and debt funds"
        elif risk_score < 7:
            return "Balanced", 0.5, risk_score, "Moderate risk with balanced growth approach across equity and debt"
        else:
            return "Aggressive", 0.7, risk_score, "High risk tolerance suitable for equity-heavy portfolios for maximum returns"

# Continue with the rest of the existing classes and code...

# Update navigation to include Quiz
nav_options = [
    "📊 Snapshot", "📈 Dashboard", "🤖 ML Insights", 
    "🧠 Behavior Quiz", "💹 Investment Center", "🎯 Goals Planner", 
    "💼 Portfolio", "📥 Export", "👨‍💻 Developer"
]

# Add the Quiz Page
elif st.session_state.current_page == "🧠 Behavior Quiz":
    st.header('🧠 Financial Behavior Quiz')
    st.markdown("""
    <div class='financial-sticker'>
        <h3>Discover Your Investment Personality</h3>
        <p>This quiz will help us understand your financial behavior and provide personalized investment recommendations.</p>
        <p><strong>Time:</strong> 5-7 minutes | <strong>Questions:</strong> 8</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize quiz in session state
    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = {}
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    
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
        cols = st.columns(2)
        
        for i, option in enumerate(current_q['options']):
            with cols[i % 2]:
                is_selected = st.session_state.quiz_answers.get(current_q['id']) == i
                css_class = "quiz-option selected" if is_selected else "quiz-option"
                
                st.markdown(f"""
                <div class='{css_class}' onclick='this.style.backgroundColor="#dbeafe"'>
                    {option['text']}
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Select Option {i+1}", key=f"opt_{i}", use_container_width=True):
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
            <h2>{personality_result['personality']}</h2>
            <h3>Risk Level: {personality_result['risk_level']}</h3>
            <p>{personality_result['description']}</p>
            <p><strong>Personality Score:</strong> {personality_result['score']} ({personality_result['score_percentage']:.1f}%)</p>
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
            st.dataframe(allocation_df, use_container_width=True)
            
            # Asset allocation pie chart
            fig = px.pie(allocation_df, values='Allocation', names='Asset Class', 
                        title='Recommended Portfolio Allocation')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': 'black'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🏆 Recommended Funds")
            for i, fund in enumerate(recommendations['recommended_funds'], 1):
                st.markdown(f"{i}. **{fund}**")
            
            st.markdown("#### 🎯 Investment Strategy")
            st.info(recommendations['strategy'])
            
            st.markdown("#### 💡 Suggestions")
            for suggestion in recommendations['suggestions']:
                st.markdown(f"• {suggestion}")
        
        # Behavioral Insights
        st.markdown("### 🔍 Behavioral Insights")
        
        insights_cols = st.columns(2)
        
        with insights_cols[0]:
            st.markdown("#### 📈 Your Risk Pattern")
            risk_data = {
                'Aspect': ['Market Volatility', 'Investment Horizon', 'Risk Tolerance', 'Experience Level'],
                'Score': [
                    answers_with_scores.get(1, 0),
                    answers_with_scores.get(3, 0),
                    answers_with_scores.get(4, 0),
                    answers_with_scores.get(5, 0)
                ]
            }
            risk_df = pd.DataFrame(risk_data)
            fig = px.bar(risk_df, x='Aspect', y='Score', title='Risk Profile Breakdown',
                        color='Score', color_continuous_scale='Viridis')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': 'black'})
            st.plotly_chart(fig, use_container_width=True)
        
        with insights_cols[1]:
            st.markdown("#### 💰 Financial Behavior")
            behavior_data = {
                'Behavior': ['Emergency Fund Priority', 'Investment Allocation', 'Decision Making', 'Market Reaction'],
                'Score': [
                    answers_with_scores.get(7, 0),
                    answers_with_scores.get(6, 0),
                    answers_with_scores.get(8, 0),
                    answers_with_scores.get(1, 0)
                ]
            }
            behavior_df = pd.DataFrame(behavior_data)
            fig = px.pie(behavior_df, values='Score', names='Behavior', title='Behavioral Patterns')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': 'black'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Action Plan
        st.markdown("### 🚀 Your Action Plan")
        
        action_cols = st.columns(3)
        
        with action_cols[0]:
            st.markdown("""
            <div class='metric-card'>
                <h4>📅 Immediate Actions (1-2 weeks)</h4>
                <p>• Review emergency fund</p>
                <p>• Research recommended funds</p>
                <p>• Set up SIP if applicable</p>
            </div>
            """, unsafe_allow_html=True)
        
        with action_cols[1]:
            st.markdown("""
            <div class='metric-card'>
                <h4>📊 Short-term Goals (1-3 months)</h4>
                <p>• Implement asset allocation</p>
                <p>• Start systematic investments</p>
                <p>• Set up portfolio tracking</p>
            </div>
            """, unsafe_allow_html=True)
        
        with action_cols[2]:
            st.markdown("""
            <div class='metric-card'>
                <h4>🎯 Long-term Strategy (6+ months)</h4>
                <p>• Regular portfolio review</p>
                <p>• Rebalance as needed</p>
                <p>• Monitor performance</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Reset quiz button
        st.markdown("---")
        if st.button("🔄 Take Quiz Again", use_container_width=True):
            st.session_state.quiz_answers = {}
            st.session_state.current_question = 0
            st.session_state.quiz_completed = False
            st.rerun()

# Update the Developer page with clickable links
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
    
    # Clickable Social Links
    st.markdown("### 📱 Connect & Collaborate")
    
    contact_cols = st.columns(4)
    
    with contact_cols[0]:
        st.markdown("""
        <a href="https://github.com/ayushshukla" target="_blank" class="social-link">
            <div style='font-size: 2rem;'>🐙</div>
            <p><strong>GitHub</strong></p>
            <p style='font-size: 0.8em;'>ayushshukla</p>
        </a>
        """, unsafe_allow_html=True)
    
    with contact_cols[1]:
        st.markdown("""
        <a href="https://linkedin.com/in/ayushshukla" target="_blank" class="social-link">
            <div style='font-size: 2rem;'>💼</div>
            <p><strong>LinkedIn</strong></p>
            <p style='font-size: 0.8em;'>ayushshukla</p>
        </a>
        """, unsafe_allow_html=True)
    
    with contact_cols[2]:
        st.markdown("""
        <a href="mailto:ayush.shukla@example.com" class="social-link">
            <div style='font-size: 2rem;'>📧</div>
            <p><strong>Email</strong></p>
            <p style='font-size: 0.8em;'>Contact Me</p>
        </a>
        """, unsafe_allow_html=True)
    
    with contact_cols[3]:
        st.markdown("""
        <a href="https://ayushshukla.xyz" target="_blank" class="social-link">
            <div style='font-size: 2rem;'>🌐</div>
            <p><strong>Portfolio</strong></p>
            <p style='font-size: 0.8em;'>ayushshukla.xyz</p>
        </a>
        """, unsafe_allow_html=True)

# Continue with the rest of the existing code...
