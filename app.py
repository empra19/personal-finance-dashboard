import streamlit as st

st.set_page_config(page_title='Personal Finance Dashboard', layout='wide')
hide_pages = st.navigation([
    st.Page('pages/1_Spending_Overview.py', title='Spending Overview'),
    st.Page('pages/2_Spending_by_Category.py', title='Spending by Category'),
    st.Page('pages/3_Error_Fraud_Analysis.py', title='Error & Fraud Analysis'),
    st.Page('pages/4_Forecasting.py', title='Forecasting'),
])
hide_pages.run()