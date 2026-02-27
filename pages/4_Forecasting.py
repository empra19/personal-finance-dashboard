import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error

st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>Forecasting</h1>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center;'>Time series forecasting using SARIMA - trained on 2010–2018 spending data, validated against 2019, and projected 12 months ahead.</h5>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: grey;'>by Yasith Senanayake</p>", unsafe_allow_html=True)


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
    df = df.set_index('month')
    df.index = pd.DatetimeIndex(df.index.values, freq='MS')
    return df

@st.cache_resource
def fit_eval_model():
    df = load_monthly()
    train = df[df.index < '2019-01-01']
    test  = df[df.index >= '2019-01-01']
    model = SARIMAX(train['monthly_total'], order=(1, 0, 1), seasonal_order=(1, 0, 1, 12))
    result = model.fit(disp=False)
    forecast_mean = result.get_forecast(steps=len(test)).predicted_mean
    mae  = mean_absolute_error(test['monthly_total'], forecast_mean)
    mape = (abs(test['monthly_total'] - forecast_mean) / test['monthly_total']).mean() * 100
    return mae, mape, forecast_mean

@st.cache_resource
def fit_overall_model():
    df = load_monthly()
    model = SARIMAX(df['monthly_total'], order=(1, 0, 1), seasonal_order=(1, 0, 1, 12))
    return model.fit(disp=False), df

df = load_monthly()
train = df[df.index < '2019-01-01']
test  = df[df.index >= '2019-01-01']
mae, mape, eval_mean = fit_eval_model()
result, df = fit_overall_model()

# ── Train/Test Chart ───────────────────────────────────────────────────────────
st.subheader('Model Validation: Forecast vs Actual (2019)')

fig_eval = go.Figure()
fig_eval.add_trace(go.Scatter(
    x=train.index, y=train['monthly_total'],
    name='Training', line=dict(color='steelblue')
))
fig_eval.add_trace(go.Scatter(
    x=test.index, y=test['monthly_total'],
    name='Actual', line=dict(color='orange')
))
fig_eval.add_trace(go.Scatter(
    x=eval_mean.index, y=eval_mean.values,
    name='Forecast', line=dict(color='green')
))
fig_eval.add_trace(go.Scatter(
    x=[train.index[-1], eval_mean.index[0]],
    y=[train['monthly_total'].iloc[-1], eval_mean.iloc[0]],
    line=dict(color='green', dash='dash'),
    showlegend=False
))
fig_eval.update_layout(
    xaxis_title='Date',
    yaxis_title='Total Spent',
    yaxis_tickformat='.2s',
    yaxis_tickprefix='$',
    template='plotly_white',
    xaxis=dict(
        range=['2018-01-01', '2019-10-01'],
        autorange = False,
        rangeselector=dict(
            buttons=[
                dict(label='2 Years', step='year', stepmode='backward', count=2),
                dict(label='5 Years', step='year', stepmode='backward', count=5),
                dict(label='All', count=118, step='month', stepmode='backward'),
            ]
        ),
    )
)

st.plotly_chart(fig_eval, width='stretch')
st.write('The model was trained on 2010–2018 data and tested on 2019. The forecast line shows predicted monthly spend against the actual values.')

# ── Metrics ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    st.metric('MAE', f"${mae:,.0f}")
with col2:
    st.metric('MAPE', f"{mape:.2f}%")

st.info('Average error per month in dollars (MAE) and as a percentage (MAPE). **Under 2% MAPE is considered excellent for real-world financial data**')

# ── Future Forecast Chart ──────────────────────────────────────────────────────
st.subheader('12 Month Forecast (Nov 2019 — Oct 2020)')

future_forecast = result.get_forecast(steps=12)
future_mean     = future_forecast.predicted_mean
future_ci       = future_forecast.conf_int()

fig_future = go.Figure()
fig_future.add_trace(go.Scatter(
    x=df.index, y=df['monthly_total'],
    name='Actual', line=dict(color='steelblue')
))
fig_future.add_trace(go.Scatter(
    x=future_mean.index, y=future_mean.values,
    name='Forecast', line=dict(color='green')
))
fig_future.add_trace(go.Scatter(
    x=[df.index[-1], future_mean.index[0]],
    y=[df['monthly_total'].iloc[-1], future_mean.iloc[0]],
    line=dict(color='green', dash='dash'),
    showlegend=False
))
fig_future.add_trace(go.Scatter(
    x=list(future_ci.index) + list(future_ci.index[::-1]),
    y=list(future_ci.iloc[:, 0]) + list(future_ci.iloc[:, 1][::-1]),
    fill='toself', fillcolor='rgba(0,200,100,0.15)',
    line=dict(color='rgba(255,255,255,0)'),
    name='95% Confidence Interval'
))
fig_future.update_layout(
    xaxis_title='Date',
    yaxis_title='Total Spend',
    yaxis_tickformat='.2s',
    yaxis_tickprefix='$',
    template='plotly_white',
    xaxis=dict(
    range=['2018-01-01', '2020-10-01'],
    autorange = False,
    rangeselector=dict(
        buttons=[
            dict(label='2 Years', step='year', stepmode='backward', count=2),
            dict(label='5 Years', step='year', stepmode='backward', count=5),
            dict(label='All', count=130, step='month', stepmode='backward'),
        ]
    ),
)
)
st.plotly_chart(fig_future, width='stretch')

st.write('The model was refit on the full dataset before forecasting. The shaded area shows where the predictions are expected to fall with 95% confidence')

@st.cache_data
def load_top_categories():
    conn = sqlite3.connect('data/finance.db')
    return pd.read_sql_query("""
        SELECT 
            mcc_codes.description,
            COUNT(*) AS total_transactions
        FROM transactions
        LEFT JOIN mcc_codes ON transactions.mcc = mcc_codes.mcc
        GROUP BY mcc_codes.description
        ORDER BY total_transactions DESC
        LIMIT 10
    """, conn)['description'].tolist()

@st.cache_resource
def fit_category_model(category):
    conn = sqlite3.connect('data/finance.db')
    df_cat = pd.read_sql_query(f"""
        SELECT 
            strftime('%Y-%m', date) AS month,
            SUM(CAST(REPLACE(amount, '$', '') AS REAL)) AS monthly_total
        FROM transactions
        LEFT JOIN mcc_codes ON transactions.mcc = mcc_codes.mcc
        WHERE mcc_codes.description = '{category}'
        GROUP BY month
        ORDER BY month ASC
    """, conn)
    df_cat['month'] = pd.to_datetime(df_cat['month'])
    df_cat = df_cat.set_index('month')
    df_cat.index = pd.DatetimeIndex(df_cat.index.values, freq='MS')
    
    train = df_cat[df_cat.index < '2019-01-01']
    test  = df_cat[df_cat.index >= '2019-01-01']
    
    model = SARIMAX(df_cat['monthly_total'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    result = model.fit(disp=False)
    future_mean = result.get_forecast(steps=12).predicted_mean
    future_ci   = result.get_forecast(steps=12).conf_int()
    
    eval_model  = SARIMAX(train['monthly_total'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    eval_result = eval_model.fit(disp=False)
    eval_mean   = eval_result.get_forecast(steps=len(test)).predicted_mean
    mae  = mean_absolute_error(test['monthly_total'], eval_mean)
    mape = (abs(test['monthly_total'] - eval_mean) / test['monthly_total']).mean() * 100
    
    return df_cat, future_mean, future_ci, mae, mape

st.subheader('Forecast by Industry')

categories = load_top_categories()
selected = st.selectbox('Select a category', categories)

df_cat, future_mean_cat, future_ci_cat, mae_cat, mape_cat = fit_category_model(selected)

fig_cat = go.Figure()
fig_cat.add_trace(go.Scatter(
    x=df_cat.index, y=df_cat['monthly_total'],
    name='Actual', line=dict(color='steelblue')
))
fig_cat.add_trace(go.Scatter(
    x=future_mean_cat.index, y=future_mean_cat.values,
    name='Forecast', line=dict(color='green')
))
fig_cat.add_trace(go.Scatter(
    x=list(future_ci_cat.index) + list(future_ci_cat.index[::-1]),
    y=list(future_ci_cat.iloc[:, 0]) + list(future_ci_cat.iloc[:, 1][::-1]),
    fill='toself', fillcolor='rgba(0,200,100,0.15)',
    line=dict(color='rgba(255,255,255,0)'),
    name='95% Confidence Interval'
))
fig_cat.add_trace(go.Scatter(
    x=[df_cat.index[-1], future_mean_cat.index[0]],
    y=[df_cat['monthly_total'].iloc[-1], future_mean_cat.iloc[0]],
    line=dict(color='green', dash='dash'),
    showlegend=False
))
fig_cat.update_layout(
    xaxis_title='Date',
    yaxis_title='Total Spend',
    yaxis_tickformat='.2s',
    yaxis_tickprefix='$',
    template='plotly_white',
    xaxis=dict(
        range=['2018-01-01', '2020-10-01'],
        autorange = False,
        rangeselector=dict(
            buttons=[
                dict(label='2 Years', step='year', stepmode='backward', count=2),
                dict(label='5 Years', step='year', stepmode='backward', count=5),
                dict(label='All', count=130, step='month', stepmode='backward'),
            ]
        ),
    )
)
st.plotly_chart(fig_cat, width='stretch')

col1, col2 = st.columns(2)
with col1:
    st.metric('MAE (2019 validation)', f"${mae_cat:,.0f}")
with col2:
    st.metric('MAPE (2019 validation)', f"{mape_cat:.2f}%")