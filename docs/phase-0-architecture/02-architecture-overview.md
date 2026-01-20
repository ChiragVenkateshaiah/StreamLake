# 2. Architecture Overview

StreamLake follows a **Kafka-first architecture**.

## High-Level Flow

External producers send events to a thin ingestion API.
validated events are written to Kafka topics.
Long-running consumers process events and write them to a lakehouse-style raw zone in GCS.
Apache Airflow orchestrates operational workflows around the streaming system.
```
Producers
    ⬇
FastAPI (Thin Ingestion Layer)
    ⬇
Apache Kafka (RAW / DLQ Topics)
    ⬇
Kafka Consumers
    ⬇
GCS Lakehouse (Raw Zone)
    ⬆
Apache Airflow
```


## Architectural Principles

1. Kafka is the system of record
2. Streaming and orchestration are separate concerns
3. APIs remain thin; Kafka holds state
4. Replayability is mandatory
5. Storage is downstream and replaceable

This architecture mirrors patterns used in production data platforms.
