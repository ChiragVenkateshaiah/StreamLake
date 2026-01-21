# 8. Resource and Deployment Model

## Compute

- Single GCP VM
- Used for development and runtime
- Hosts Kafka, API, consumers, and Airflow

## Deployment Model

- Docker Compose for Kafka and Airflow
- Services run locally on the VM
- No managed cloud services required

## Cost Model

- Apache Kafka: Free (open source)
- Airflow: Free (open source)
- GCS: Free tier usage
- VM: Free tier eligible
