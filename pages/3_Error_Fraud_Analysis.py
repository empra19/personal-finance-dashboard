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
st.markdown("<h1 style='text-align: center;'>Error & Fraud Analysis</h1>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center;'>Exploring transaction errors, their relationship to fraud, and where they occur.</h5>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: grey;'>by Yasith Senanayake</p>", unsafe_allow_html=True)

# ── Chart 1: Error Distribution ────────────────────────────────────────────────
@st.cache_data
def load_error_distribution():
    conn = sqlite3.connect('data/finance.db')
    return pd.read_sql_query("""
        SELECT 
            errors,
            COUNT(*) AS transaction_count
        FROM transactions
        WHERE errors != 'No Error'
        AND errors NOT LIKE '%,%'
        GROUP BY errors
        ORDER BY transaction_count DESC
        LIMIT 10
    """, conn)

df_errors = load_error_distribution()

st.subheader('Distribution of Transaction Errors')
fig_errors = px.bar(
    df_errors, x='transaction_count', y='errors',
    orientation='h',
    labels={'transaction_count': 'Number of Transactions', 'errors': ''},
    template='plotly_white',
)
fig_errors.update_traces(marker_color='steelblue')
fig_errors.update_layout(yaxis=dict(categoryorder='total ascending'))
st.plotly_chart(fig_errors, width='stretch')

# ── Loading pre-loaded data (for long queries) ────────────────────────────────────────────────
@st.cache_data
def load_fraud_by_error():
    df = pd.read_csv('data/fraud_by_error.csv')
    df['errors'] = df['errors'].fillna('No Error')
    return df

@st.cache_data
def load_fraud_over_time():
    return pd.read_csv('data/fraud_over_time.csv')

@st.cache_data
def load_fraud_amounts():
    return pd.read_csv('data/fraud_amounts.csv')

df_fraud_error = load_fraud_by_error()
df_fraud_amounts = load_fraud_amounts()

# ── Chart 2 & 3: Fraud Rate by Error + Avg Transaction Amount ─────────────────
col1, col2 = st.columns([4, 1])

with col1:
    st.subheader('Fraud Rate by Error Type')
    df_fraud_error['colour'] = df_fraud_error['errors'].apply(
        lambda x: 'steelblue' if x == 'No Error' else 'darkorange'
    )
    fig_fraud_error = px.bar(
        df_fraud_error, x='fraud_rate', y='errors',
        orientation='h',
        labels={'fraud_rate': 'Fraud Rate (%)', 'errors': ''},
        template='plotly_white',
        color='colour',
        color_discrete_map={'steelblue': 'steelblue', 'darkorange': 'darkorange'}
    )
    fig_fraud_error.update_layout(
        yaxis=dict(categoryorder='total ascending'),
        showlegend=False
    )
    st.plotly_chart(fig_fraud_error, width='stretch')

with col2:
    st.subheader('How Much Do Fraudsters Spend?')
    with st.container(border=True):
        st.metric('Typical Transaction (avg)', f"${df_fraud_amounts[df_fraud_amounts['is_fraud'] == 'No']['avg_amount'].values[0]:,.2f}")
    with st.container(border=True):
        st.metric('Fraudulent Transaction (avg)', f"${df_fraud_amounts[df_fraud_amounts['is_fraud'] == 'Yes']['avg_amount'].values[0]:,.2f}")

# ── Chart 4: Fraud Rate by Merchant Category ──────────────────────────────────
@st.cache_data
def load_fraud_by_category():
    return pd.read_csv('data/fraud_by_category.csv')

df_fraud_cat = load_fraud_by_category()

st.subheader('Fraud Rate by Merchant Category: Top 10')

top10 = df_fraud_cat.head(10)
bot10 = df_fraud_cat.tail(10).sort_values('fraud_rate', ascending=False)

fig_top = px.bar(
    top10, x='fraud_rate', y='description',
    orientation='h',
    labels={'fraud_rate': 'Fraud Rate (%)', 'description': ''},
    template='plotly_white'
)
fig_top.update_traces(marker_color='steelblue')
fig_top.update_layout(yaxis=dict(categoryorder='total ascending'))
st.plotly_chart(fig_top, width='stretch')

