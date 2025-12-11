# spark_processor/process_stream.py
import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp, lit
from schema import schema

# DB config via env vars
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "weather_db")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
JDBC_URL = f"jdbc:mysql://{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?serverTimezone=UTC"

INPUT_DIR = os.getenv("WEATHER_OUTPUT_DIR", "../data/incoming")  # relative to spark_processor

logging.basicConfig(level=logging.INFO)

def start():
    spark = SparkSession.builder \
        .appName("WeatherIngest") \
        .config("spark.driver.extraClassPath", "/path/to/mysql-connector-java.jar") \
        .getOrCreate()

    # read JSON files as streaming source
    raw_df = spark.readStream \
        .format("json") \
        .schema(schema) \
        .option("maxFilesPerTrigger", 1) \
        .load(INPUT_DIR)

    # transform: cast event_time_utc -> timestamp, add ingest_time
    processed = raw_df \
        .withColumn("event_time", to_timestamp(col("event_time_utc"))) \
        .withColumn("source", lit("openweather_api")) \
        .select("city", "temperature", "humidity", "weather", "event_time", "raw")

    # Ensure idempotency: write to a staging table or use JDBC upsert if MySQL supports (we'll write to a table with unique key and use 'INSERT ... ON DUPLICATE KEY UPDATE')
    def foreach_batch_function(df, epoch_id):
        if df.rdd.isEmpty():
            return
        # write to a temporary table via JDBC then run upsert
        tmp_table = "weather_staging"
        df_to_write = df.withColumn("raw", col("raw"))  # ensure column exists

        # write batch to JDBC
        df_to_write.write \
            .format("jdbc") \
            .option("url", JDBC_URL) \
            .option("dbtable", tmp_table) \
            .option("user", MYSQL_USER) \
            .option("password", MYSQL_PASSWORD) \
            .option("driver", "com.mysql.cj.jdbc.Driver") \
            .mode("append") \
            .save()

        # Now run upsert SQL to move from staging -> weather (idempotent)
        # We'll use connector via spark to run the SQL through JDBC:
        connection_properties = {
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "driver": "com.mysql.cj.jdbc.Driver"
        }
        # Use spark to execute SQL using JDBC
        # We will create the target table if not exists and ensure (city, event_time) unique key is present
        spark._sc._jvm.java.lang.System.out.println("Batch written to staging. Please ensure upsert SQL is run externally or create a MySQL trigger/script.")
        # For simplicity we will rely on a MySQL procedure or run a raw SQL via python-mysql connector here:
        import mysql.connector
        conn = mysql.connector.connect(
            host=MYSQL_HOST, port=int(MYSQL_PORT), user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB
        )
        cursor = conn.cursor()
        # Create target table if not exists (idempotent)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            city VARCHAR(128),
            temperature DOUBLE,
            humidity INT,
            weather VARCHAR(255),
            event_time TIMESTAMP,
            raw JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uniq_city_event (city, event_time)
        ) ENGINE=InnoDB;
        """)
        # Upsert from staging to weather
        cursor.execute("""
        INSERT INTO weather (city, temperature, humidity, weather, event_time, raw)
        SELECT city, temperature, humidity, weather, event_time, CAST(raw AS JSON)
        FROM weather_staging
        ON DUPLICATE KEY UPDATE
          temperature = VALUES(temperature),
          humidity = VALUES(humidity),
          weather = VALUES(weather),
          raw = VALUES(raw);
        """)
        # clear staging
        cursor.execute("TRUNCATE TABLE weather_staging;")
        conn.commit()
        conn.close()

    query = processed.writeStream \
        .foreachBatch(foreach_batch_function) \
        .outputMode("update") \
        .option("checkpointLocation", "/tmp/spark_checkpoint_weather") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    start()
