# 7. Airflow Orchestration Model

Apache Airflow is used strictly as an orchestration and operations layer.

## What Airflow Does

- Trigger Kafka replay jobs
- Orchestrate backfills
- Run batch data-quality checks
- Inspect DLQ topics
- Generate audit summaries

## What Airflow Does NOT Do

- Run streaming consumers
- Schedule ingestion
- Replace Kafka offset management

Airflow controls actions around Kafka, not Kafka itself.