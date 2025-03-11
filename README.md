### Purpose
A sweeping data acquisition program designed to present current hotspots of activity among publicly traded companies, conglomerates, and ETF members.

### Tech Stack
- Python
    - Data Processing 
        - PyArrow (In-memory Format)
        - PySpark (Data Processing)
        - DeltaLake (Durable Format [Parquet])
        - Hive (Query Layer)
        - Airflow (Orchestration)
    - NetworkX (Graphs)
- Scala
    - Kafka (Real time Streaming)

- Monitoring
    - Prometheus -> Grafana

#### ML Inference Line
Kafka --> Spark (Arrow In-Memory) --> ML Model (Direct Predictions)
                ↘
             Prometheus --> Grafana (Real-Time Monitoring)


#### Historical Data Line
Kafka --> Spark (Batch) --> Delta Lake (Parquet + ACID)
                            ↘
                     Hive Metastore
                            ↘
                    Batch ML Retraining

#### Telemetry Line
Kafka --> Prometheus --> Grafana (Kafka lag, Spark times, Model inference time)
Spark --> Prometheus --> Grafana (Batch processing time, failure rate)
Delta --> Airflow    --> Optimize Delta, Retrain Model


- RL/DL/NLP
### To Start VENV
venv\Scripts\activate