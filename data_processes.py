from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("MyApp") \
    .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.0.0") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Create a test Delta table
df = spark.range(10)
df.write.format("delta").save("/tmp/delta-table")

# Read it back
df_read = spark.read.format("delta").load("/tmp/delta-table")
df_read.show()

spark.stop()
