# 4. Component Responsibilities

## FastAPI - Ingestion Edge

Responsibilities:
- Accept JSON events
- Validate payloads against schemas
- Enrich metadata
- Produce events to Kafka


Non-responsibilities:
- Transformations
- Aggregations
- Scheduling
- State management


## Apache Kafka - Streaming Backbone

Responsibilities:
- Event buffering
- Partitioning and ordering
- Delivery guarantees
- Replay capability
- DLQ handling


Kafka is the central system of record.

## Kafka Consumers

Responsibilities:
- Consume events from Kafka
- Handle failures and retries
- Write data to GCS
- Commit offsets manually


## GCS - Lakehouse Raw Zone


Responsibilities:
- Durable storage
- Auditability
- Downstream analytics readiness

## Apache Airflow - Orchestration


Responsibilities:
- Replay workflows
- Backfill orchestration
- Data quality checks
- Operational reporting

