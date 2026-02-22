import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

conn = sqlite3.connect('data/finance.db')

st.title('Spending Overview')

col1, col2, col3 = st.columns(3)

with col1:
    df_total = pd.read_sql_query("""
        SELECT SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS total_spent
        FROM transactions
    """, conn)
    st.metric('Total Spend', f"${df_total['total_spent'][0]:,.2f}")

with col2:
    df_count = pd.read_sql_query("SELECT COUNT(*) AS count FROM transactions", conn)
    st.metric('Total Transactions', f"{df_count['count'][0]:,}")

with col3:
    df_users = pd.read_sql_query("SELECT COUNT(DISTINCT client_id) AS count FROM transactions", conn)
    st.metric('Unique Users', f"{df_users['count'][0]:,}")

df_monthly = pd.read_sql_query("""
    SELECT 
        strftime('%Y-%m', date) AS month,
        SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS monthly_total
    FROM transactions
    GROUP BY month
    ORDER BY month ASC
""", conn)

fig = px.line(df_monthly, x='month', y='monthly_total', 
              title='Monthly Spending Over Time',
              labels={'month': 'Month', 'monthly_total': 'Total Spend ($)'})

st.plotly_chart(fig, width='stretch')

st.subheader('Top 10 Users by Spend')
df_users_spend = pd.read_sql_query("""
    SELECT 
        client_id,
        SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS total_spent,
        COUNT(*) AS total_transactions
    FROM transactions
    GROUP BY client_id
    ORDER BY total_spent DESC
    LIMIT 10
""", conn)
df_users_spend['total_spent'] = df_users_spend['total_spent'].apply(lambda x: f"${x:,.2f}")
df_users_spend.columns = ['Client ID', 'Total Spent', 'Total Transactions']
st.dataframe(df_users_spend, hide_index=True, use_container_width=False)