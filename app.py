# streamlit_app/app.py
import os
import streamlit as st
import pandas as pd
import mysql.connector
from emailer import send_email
from datetime import datetime, timedelta

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DB = os.getenv("MYSQL_DB", "weather_db")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")

def get_latest_weather(limit=100):
    conn = mysql.connector.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT city, temperature, humidity, weather, event_time, created_at FROM weather ORDER BY event_time DESC LIMIT %s", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return pd.DataFrame(rows)

st.title("Weather Pipeline Dashboard")

df = get_latest_weather(200)
st.write("Latest weather entries", df)

# simple aggregation: latest per city
if not df.empty:
    latest_per_city = df.sort_values("event_time").groupby("city").tail(1).set_index("city")
    st.write("Latest per city", latest_per_city[["temperature", "humidity", "weather", "event_time"]])

# email trigger
st.sidebar.header("Email Alerts")
emails = st.sidebar.text_input("Recipient emails (comma separated)")
city = st.sidebar.selectbox("City", options=["All"] + df["city"].dropna().unique().tolist())
threshold = st.sidebar.number_input("Temperature threshold (°C)", value=40)

if st.sidebar.button("Send alert"):
    if not emails:
        st.sidebar.error("Add recipient emails")
    else:
        recipients = [e.strip() for e in emails.split(",")]
        subject = f"Weather alert for {city}"
        body = f"Threshold {threshold}C triggered for {city} at {datetime.utcnow().isoformat()}Z"
        try:
            send_email(recipients, subject, body)
            st.sidebar.success("Email sent")
        except Exception as e:
            st.sidebar.error(f"Failed to send email: {e}")
