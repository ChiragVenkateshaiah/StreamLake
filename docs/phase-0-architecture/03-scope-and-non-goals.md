# 3. Scope and Non-Goals

## In Scope

- Streaming ingestion using Apache Kafka
- Thin ingestion API using FastAPI
- Schema validation using Pydantic
- Failure handling using DLQ topics
- Replay and reprocessing via Kafka offsets
- Raw data landing in GCS
- Operational orchestration using Airflow

## Explicit Non-Goals

StreamLake does NOT include:

- User interfaces or dashboards
- Managed Kafka services
- Batch processing engines (Spark, Flink)
- CDC pipelines
- Delta Lake or Iceberg table formats
- Full governance or policy engines
- Authentication and authorization systems


Non-goals are intentional to maintain focus and prevent overengineering.
