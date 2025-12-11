# spark_processor/schema.py
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType, MapType

schema = StructType([
    StructField("city", StringType(), True),
    StructField("temperature", DoubleType(), True),
    StructField("humidity", IntegerType(), True),
    StructField("weather", StringType(), True),
    StructField("event_time_utc", StringType(), True),  # parse to timestamp later
    StructField("raw", StringType(), True)  # raw stored as json string
])
