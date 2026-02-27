import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go

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
st.markdown("<p style='text-align: center; color: grey;'>by Yasith Senanayake</p>", unsafe_allow_html=True)

# ── Data Loaders ───────────────────────────────────────────────────────────────
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
    df = pd.read_sql_query("""
        SELECT 
            strftime('%Y-%m', date) AS month,
            SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS monthly_total
        FROM transactions
        GROUP BY month
        ORDER BY month ASC
    """, conn)
    df['month'] = pd.to_datetime(df['month'])
    df['ma_3']  = df['monthly_total'].rolling(window=3).mean()
    df['ma_12'] = df['monthly_total'].rolling(window=12).mean()
    return df

st.subheader('Spending Overview')
# ── Metrics ────────────────────────────────────────────────────────────────────
df_total, df_count, df_users = load_metrics()

col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        st.metric('Total Spent', f"${df_total['total_spent'][0]:,.2f}")
with col2:
    with st.container(border=True):
        st.metric('Number of Transactions', f"{df_count['count'][0]:,}")
with col3:
    with st.container(border=True):
        st.metric('Unique Users', f"{df_users['count'][0]:,}")

# ── Chart: Monthly Spending with Moving Averages ───────────────────────────────
df_monthly = load_monthly()
st.markdown("<h3 style='text-align: center;'>Monthly Spending over Time</h3>", unsafe_allow_html=True)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_monthly['month'], y=df_monthly['monthly_total'],
    name='Actual', line=dict(color='steelblue'), opacity=0.6
))
fig.add_trace(go.Scatter(
    x=df_monthly['month'], y=df_monthly['ma_3'],
    name='3-Month MA', line=dict(color='orange')
))
fig.add_trace(go.Scatter(
    x=df_monthly['month'], y=df_monthly['ma_12'],
    name='12-Month MA', line=dict(color='green')
))
fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Total Spend',
    yaxis_tickformat='.2s',
    yaxis_tickprefix='$',
    template='plotly_white',
    xaxis=dict(
        rangeselector=dict(
            buttons=[
                dict(label='2 Years', step='year', stepmode='backward', count=2),
                dict(label='5 Years', step='year', stepmode='backward', count=5),
                dict(label='All', count=118, step='month', stepmode='backward'),
            ]
        ),
    )
)
st.plotly_chart(fig, width='stretch')