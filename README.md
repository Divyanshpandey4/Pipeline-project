✅Weather Data Collection & Real-Time Processing System

A complete end-to-end project that fetches live weather data, processes it using Apache Spark Structured Streaming, stores it in a MySQL database, and displays insights on a Streamlit dashboard with optional automated email alerts.

🚀 Project Overview

This project simulates a real-world data engineering pipeline. It:

Fetches live weather data from the OpenWeather API

Writes raw JSON events into a folder that Spark continuously monitors

Processes data in real time using PySpark Structured Streaming

Upserts cleaned data into MySQL (ensures no duplicates)

Displays insights (temperature, humidity, weather summary) on a Streamlit UI

Sends email alerts when temperature crosses a threshold (SendGrid or SMTP)

This project demonstrates:

Data ingestion (API → JSON)

Real-time ETL processing (Spark)

Database storage (MySQL)

Analytics and visualization (Streamlit)

Notification system (SendGrid or SMTP)

Perfect for Data Engineering, MLOps, and Cloud portfolio projects.

🧱 Tech Stack
Component	Technology
Data Fetching	Python, Requests
Real-Time Processing	Apache Spark Structured Streaming (PySpark)
Database	MySQL
Dashboard	Streamlit
Alerting	SendGrid API or SMTP
Orchestration	Environment variables
Optional	Docker / Docker Compose
📚 Folder Structure


    ├── fetcher/
    │   └── fetch_weather.py
    ├── spark_processor/
    │   ├── process_stream.py
    │   └── schema.py
    ├── streamlit_app/
    │   ├── app.py
    │   └── emailer.py
    ├── infra/
    │   └── docker-compose.yml (optional)
    ├── data/
    │   └── incoming/ (auto-created for raw JSON logs)
    └── README.md

🔐 API Keys & Credentials Setup

This project requires three types of credentials:

🟦 1. OpenWeatherMap API Key (for Weather Data)

Get your free API key from:
👉 https://home.openweathermap.org/api_keys

Example API call:

https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY

🟩 2. SendGrid API Key (for Email Alerts)

If you want email alerting, your SendGrid key looks like:

SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx


Create one using:

https://sendgrid.com/free

Navigate to Settings → API Keys

Create a Full Access key

Copy it securely

🟨 3. Optional: SMTP (instead of SendGrid)

If you cannot or do not want to use SendGrid, you can use:

    Gmail SMTP
    smtp.gmail.com
    Port: 587
    Username: your Gmail
    Password: App Password (NOT your Gmail login)

    Outlook SMTP
    smtp.office365.com
    Port: 587
    Username: Outlook email
    Password: Outlook App Password


This project supports both SendGrid and SMTP (configured in emailer.py).

⚙️ Environment Variables Setup
Windows CMD (your system)
set OPENWEATHER_API_KEY=YOUR_OPENWEATHER_KEY
set WEATHER_OUTPUT_DIR=.\data\incoming
set SENDGRID_API_KEY=YOUR_SENDGRID_KEY
set FROM_EMAIL=your_verified_email@example.com

Windows PowerShell
setx OPENWEATHER_API_KEY "YOUR_OPENWEATHER_KEY"
setx WEATHER_OUTPUT_DIR "data\incoming"
setx SENDGRID_API_KEY "YOUR_SENDGRID_KEY"
setx FROM_EMAIL "your_verified_email@example.com"

Linux / Mac / WSL
export OPENWEATHER_API_KEY="YOUR_OPENWEATHER_KEY"
export WEATHER_OUTPUT_DIR="./data/incoming"
export SENDGRID_API_KEY="YOUR_SENDGRID_KEY"
export FROM_EMAIL="your_verified_email@example.com"

▶️ How to Run the Project

This project requires three terminals running at the same time.

🟦 Terminal 1 — Run Fetcher (Weather Collector)

This script downloads weather data and writes JSON files.

    cd fetcher
    python fetch_weather.py


You should see messages like:

Wrote event file data/incoming/xxxxx.json

🟧 Terminal 2 — Run Spark Real-Time Processor

Ensure PySpark and MySQL connector are installed:

    pip install pyspark mysql-connector-python


Run Spark:

    cd spark_processor
    spark-submit --jars mysql-connector-java-8.0.33.jar process_stream.py


Spark will:

Watch the folder data/incoming

Process each incoming JSON in real time

Upsert rows into MySQL using ON DUPLICATE KEY UPDATE (prevents duplicates)

🟩 Terminal 3 — Run Streamlit Dashboard

    cd streamlit_app
    streamlit run app.py


Open:

👉 http://localhost:8501/

Features in dashboard:

Latest weather data

Per-city summary

Temperature trends

Email alert controls

🗄️ MySQL Database Schema

Spark automatically creates the required tables:

weather_staging

Temporary batch load table.

weather

Final table with unique constraint:

UNIQUE KEY uniq_city_event (city, event_time)


Prevents duplicate weather readings.

📤 Sending Email Alerts

Alerts can be sent via:

✔️ SendGrid (recommended for production)
✔️ SMTP (Gmail/Outlook) – easier for personal users

Set your preference in emailer.py.

The alert is triggered manually via Streamlit sidebar:

Enter emails

Select city

Set temperature threshold

🧪 Testing the Pipeline

Run the fetcher → ensure JSON files appear in data/incoming

Run Spark → ensure MySQL table weather gets populated

Run Streamlit → ensure dashboard updates

Trigger an alert → ensure email is delivered

🐞 Troubleshooting
❌ "export is not recognized"

You're using Windows CMD. Use set or setx.

❌ Spark not finding MySQL driver

Download connector:
https://dev.mysql.com/downloads/connector/j/

Pass it to Spark:

--jars mysql-connector-java-8.0.33.jar

❌ Streamlit cannot connect to MySQL

Check:

    MySQL service is running

    Host = 127.0.0.1

    User/password are correct

    ❌ No emails received

If using SendGrid:

    Verify FROM_EMAIL

    Verify domain

    Check spam folder

    If using Gmail SMTP:

    Enable App Passwords

Disable “Less Secure App Access” (Google removed this)

📈 Future Enhancements

      Deploy pipeline using Docker Compose

      Deploy dashboard on Streamlit Cloud

      Store raw & processed data in AWS S3

      Replace MySQL with PostgreSQL or Snowflake

      Add Airflow for scheduling

      Add automated alert rules (not manual)

      Add Grafana dashboard via Prometheus metrics

❤️ Contributions

Open to suggestions, pull requests, and improvements!

📄 License
