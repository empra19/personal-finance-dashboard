import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>Spending by Category</h1>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center;'>Breakdown of transaction volume and spend across merchant categories.</h5>", unsafe_allow_html=True)

@st.cache_data
def load_top_by_volume():
    conn = sqlite3.connect('data/finance.db')
    return pd.read_sql_query("""
        SELECT 
            mcc_codes.description,
            COUNT(*) AS number_transactions,
            SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS total_spent,
            ROUND(AVG(CAST(REPLACE(amount, '$', '') AS REAL)), 2) AS avg_transaction
        FROM transactions
        LEFT JOIN mcc_codes ON transactions.mcc = mcc_codes.mcc
        GROUP BY mcc_codes.description
        ORDER BY number_transactions DESC
        LIMIT 10
    """, conn)

@st.cache_data
def load_top_by_avg():
    conn = sqlite3.connect('data/finance.db')
    return pd.read_sql_query("""
        SELECT 
            mcc_codes.description,
            COUNT(*) AS number_transactions,
            SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS total_spent,
            ROUND(AVG(CAST(REPLACE(amount, '$', '') AS REAL)), 2) AS avg_transaction
        FROM transactions
        LEFT JOIN mcc_codes ON transactions.mcc = mcc_codes.mcc
        GROUP BY mcc_codes.description
        ORDER BY avg_transaction DESC
        LIMIT 10
    """, conn)

df_volume = load_top_by_volume()
df_avg    = load_top_by_avg()

st.subheader('Top 10 Categories by Transaction Volume')
fig_vol = px.bar(
    df_volume, x='number_transactions', y='description',
    orientation='h',
    labels={'number_transactions': 'Number of Transactions', 'description': ''},
    template='plotly_white',
)
fig_vol.update_traces(marker_color='steelblue')
fig_vol.update_layout(
    yaxis=dict(categoryorder='total ascending'),
    xaxis=dict(tickformat='~s')
)
st.plotly_chart(fig_vol, width='stretch')

st.subheader('Top 10 Categories by Average Transaction Size')
fig_avg = px.bar(
    df_avg, x='avg_transaction', y='description',
    orientation='h',
    labels={'avg_transaction': 'Average Transaction ($)', 'description': ''},
    template='plotly_white',
)
fig_avg.update_traces(marker_color='seagreen')
fig_avg.update_layout(yaxis=dict(categoryorder='total ascending'))
st.plotly_chart(fig_avg, width='stretch')

@st.cache_data
def load_category_trends(category):
    conn = sqlite3.connect('data/finance.db')
    df = pd.read_sql_query(f"""
        SELECT 
            strftime('%Y-%m', date) AS month,
            SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS monthly_total
        FROM transactions
        LEFT JOIN mcc_codes ON transactions.mcc = mcc_codes.mcc
        WHERE mcc_codes.description = '{category}'
        GROUP BY month
        ORDER BY month ASC
    """, conn)
    df['month'] = pd.to_datetime(df['month'])
    df = df.set_index('month')
    df['ma_3']  = df['monthly_total'].rolling(window=3).mean()
    df['ma_12'] = df['monthly_total'].rolling(window=12).mean()
    return df

@st.cache_data
def load_all_categories():
    conn = sqlite3.connect('data/finance.db')
    return pd.read_sql_query("""
        SELECT DISTINCT mcc_codes.description
        FROM transactions
        LEFT JOIN mcc_codes ON transactions.mcc = mcc_codes.mcc
        WHERE mcc_codes.description IS NOT NULL
        ORDER BY mcc_codes.description ASC
    """, conn)['description'].tolist()


st.subheader('Category Spending Trends')

categories = load_all_categories()
selected = st.selectbox('Select a category', categories)

df_trend = load_category_trends(selected)

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=df_trend.index, y=df_trend['monthly_total'],
    name='Actual', line=dict(color='steelblue'), opacity=0.6
))
fig_trend.add_trace(go.Scatter(
    x=df_trend.index, y=df_trend['ma_3'],
    name='3-Month MA', line=dict(color='orange')
))
fig_trend.add_trace(go.Scatter(
    x=df_trend.index, y=df_trend['ma_12'],
    name='12-Month MA', line=dict(color='green')
))
fig_trend.update_layout(
    xaxis_title='Month',
    yaxis_title='Total Spend',
    yaxis_tickformat='.2s',
    yaxis_tickprefix='$',
    template='plotly_white',
    xaxis=dict(
        range=['2010-01-01', '2019-10-01'],
        rangeselector=dict(
            buttons=[
                dict(label='2 Years', step='year', stepmode='backward', count=2),
                dict(label='5 Years', step='year', stepmode='backward', count=5),
                dict(label='All', count=118, step='month', stepmode='backward'),
            ]
        ),
    )
)
st.plotly_chart(fig_trend, width='stretch')