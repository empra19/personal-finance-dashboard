import pandas as pd
import sqlite3
import json

# Load CSVs
transactions = pd.read_csv('data/transactions_data.csv')
cards        = pd.read_csv('data/cards_data.csv')
users        = pd.read_csv('data/users_data.csv')

# Load MCC codes
with open('data/mcc_codes.json') as f:
    mcc_raw = json.load(f)

mcc_codes = pd.DataFrame([
    {'mcc': int(k), 'description': v}
    for k, v in mcc_raw.items()
])

# Load fraud labels
with open('data/train_fraud_labels.json') as f:
    fraud_raw = json.load(f)

fraud_labels = pd.DataFrame([
    {'transaction_id': int(k), 'is_fraud': v}
    for k, v in fraud_raw['target'].items()
])

# Connect to SQLite
conn = sqlite3.connect('data/finance.db')

# Write tables
transactions.to_sql('transactions', conn, if_exists='replace', index=False)
cards.to_sql('cards',        conn, if_exists='replace', index=False)
users.to_sql('users',        conn, if_exists='replace', index=False)
mcc_codes.to_sql('mcc_codes',    conn, if_exists='replace', index=False)
fraud_labels.to_sql('fraud_labels', conn, if_exists='replace', index=False)

conn.close()

print('Database built successfully')