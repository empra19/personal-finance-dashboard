import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>US Consumer Spending Analysis</h1>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center;'>Exploring spending patterns, merchant trends, and financial forecasting across a synthetic US banking dataset.</h5>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: grey;'>Yasith Senanayake</p>", unsafe_allow_html=True)

@st.cache_data
def load_metrics():
    conn = sqlite3.connect('data/finance.db')
    total_spent = pd.read_sql_query("""
        SELECT SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS total_spent
        FROM transactions
    """, conn)
    total_count = pd.read_sql_query("SELECT COUNT(*) AS count FROM transactions", conn)
    unique_users = pd.read_sql_query("SELECT COUNT(DISTINCT client_id) AS count FROM transactions", conn)
    return total_spent, total_count, unique_users

@st.cache_data
def load_monthly():
    conn = sqlite3.connect('data/finance.db')
    return pd.read_sql_query("""
        SELECT 
            strftime('%Y-%m', date) AS month,
            SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS monthly_total
        FROM transactions
        GROUP BY month
        ORDER BY month ASC
    """, conn)

st.title('Spending Overview')

df_total, df_count, df_users = load_metrics()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric('Total Spend', f"${df_total['total_spent'][0]:,.2f}")
with col2:
    st.metric('Total Transactions', f"{df_count['count'][0]:,}")
with col3:
    st.metric('Unique Users', f"{df_users['count'][0]:,}")

df_monthly = load_monthly()
fig = px.line(df_monthly, x='month', y='monthly_total',
              title='Monthly Spending Over Time',
              labels={'month': 'Month', 'monthly_total': 'Total Spend ($)'})
st.plotly_chart(fig, width='stretch')