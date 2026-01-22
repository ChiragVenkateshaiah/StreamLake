# Phase-5: Implementation Roadmap & Execution Order

## StreamLake - From Design -> Working System

## Phase-5 Objective

Phase-5 answers one question only:
> "In what order should I build StreamLake so that every step is testable, meaningful?"

This roadmap:
- Minimizes blockers
- Maximizes learning
- Produces visible progress early
- Matches how real teams implement platforms

## 🧭 Guiding Execution Principles
1. Infrastructure before logic
2. Kafka before API
3. Consumers before orchestration
4. Airflow last
5. Docs updated continuously


## High-Level Execution Phases
| Order | Phase           | Outcome                          |
| ----- | --------------- | -------------------------------- |
| 1     | Runtime & Infra | Kafka + Airflow running          |
| 2     | Kafka Topics    | Deterministic ingestion backbone |
| 3     | Producer        | Data enters Kafka                |
| 4     | Consumer        | Data lands in GCS                |
| 5     | Failure & DLQ   | Production-grade robustness      |
| 6     | Replay          | Recovery & reprocessing          |
| 7     | Airflow         | Operability & DataOps            |
| 8     | Polish          | Demo + README                    |


## Phase-5.1: Runtime & Infrastructure Setup

### Goal
Have a working local platform before writing business logic.

### Tasks
- Docker + Docker Compose
- Kafka broker + Zookeeper
- Airflow (LocalExecutor)
- Folder scaffolding
- Environment variables

### Deliverables
- `docker-compose.yml`
- Kafka reachable via CLI
- Airflow UI accessible


## Phase-5.2: Kafka Topic Creation
### Goal
Lock the ingestion backbone.

### Tasks
- Create RAW topic
    
    `streamlake.order.raw`

- Create DLQ topic
    
    `streamlake.orders.dlq`

- Validate partitions & retention
- Document topic config

### Deliverables
- Topics listed via CLI
- Phase-1 doc referenced in code comments


## Phase-5.3: Kafka Producer Implementation
### Goal
Get data into Kafka correctly

### Tasks
- Implement producer config
- Implement partition key logic
- Attach Kafka headers
- Handle retries & acks
- Implement DLQ producer
- Unit-test producer locally

### Deliverables
- `kafka/producer/producer.py`
- `kafka/producer/dlq_producer.py`
- Produce messages visible in Kafka


## Phase-5.4: Thin Ingestion API
### Goal
Expose a clean ingestion edge.

### Tasks
- FastAPI skeleton
- `/ingest/orders` endpoint
- Pydantic schema validation
- Call Kafka producer
- Error propagation

### Deliverables
- API accepts JSON
- Valid data -> Kafka
- Invalid data -> DLQ


## Phase-5.5: Kafka Consumer Implementation
### Goal
Safely move data out of Kafka

### Tasks
- Consumer group setup
- Manual offset commit logic
- Error handling
- Poison pill detection
- DLQ forwarding from consumer

### Deliverables
- Consumer reads from RAW topic
- Offsets commit only after success
- Failures do not crash pipelines


## Phase-5.6: Lakehouse Raw Zone Writer
### Goal
Persist data in lakehouse-style layout.

### Tasks
- GCS client setup
- Raw zone folder structure
- File batching
- Metadata file creation
- Idempotent writes (best effort)


## Deliverables
- Data visible in GCS
- Partitioned by ingestion date
- Metadata present

> StreamLake is now end-to-end functional

## Phase-5.7: Replay & Reprocessing Logic
### Goal
Prove recoverability

### Tasks
- Offset reset scripts
- Timestamp-based replay support
- Consumer restart flow
- Replay documentation

### Deliverables
- Controlled reprocessing
- No data loss
- Replay demo ready

## Phase-5.8: Airflow DAGs
### Goal
Add operability without breaking streaming

### Tasks
- Replay DAG
- Backfill DAG
- DLQ inspection DAG
- Data quality DAG
- Parameterized execution

### Deliverables
- Airflow UI shows DAGs
- Manual triggers work
- Logs explain actions clearly

> This is DataOps credibility



## Phase-5.9: End-to-End Testing & Demo

### Goal
make StreamLake demo-ready

### Tasks
- Happy-path demo
- Failure-path demo
- DLQ demo
- Replay demo
- Screenshot + logs

### Deliverables
- Repeatable demo script
- Confidence explaining every step


## Phase-5.10: Documentation & Polish
### Goal
Updated documentation

### Tasks
- Update README
- Architecture diagram
- Execution walkthrough
- Trade-offs section
- "What I would do" Section


## Execution Timeline
| Phase            | Days        |
| ---------------- | ----------- |
| Infra + Kafka    | 2           |
| Producer + API   | 3           |
| Consumer + GCS   | 3           |
| Replay + Airflow | 3           |
| Testing + Docs   | 3           |
| **Total**        | **14 days** |


## Phase-5 Exit Criteria
StreamLake is complete when:

- ✅ Data flows end-to-end
- ✅ Failures are handled
- ✅ Replay works
- ✅ Airflow orchestrates ops
- ✅ Docs explain trade-offs clearly


> Designed and bult a Kafka-first streaming ingestion and lakehouse platform with replay, DLQ handling, and Airflow-based operational orchestration on GCP.