# Kafka-First Streaming Ingestion & Lakehouse Platform (with Airflow Orchestration)

## Objective
1. What exactly are we building?
2. What are we explicitly not building?
3. How Kafka and Airflow coexist correctly?

## Final Problem Statement (Locked)

> Build a Kafka-first streaming ingestion & lakehouse platform where Kafka is the system of record for ingestion, Airflow orchestrates operational workflows (replay, backfill, checks), and data lands in a lakehouse-style raw zone on GCP.

Inspiration: OpenLakeTx(transactions), LakeGuard(governance)

## Architecture North-Star Principles
🔒 Principle 1: Kafka is the system of record
- All replay originates from Kafka
- Storage is downstream & replacable
- Failures are solved via reprocessing, not overwrites

🔒 Principle 2: Streaming is not equal to Orchestration
- Kafka -> Event-driven, continuous
- Airflow -> Batch, control-plane, operational
- They must not overlap responsibilities

🔒 Principle 3: Thin Edges, Strong Core
- API is thin
- Kafka is deep
- Consumers are reliable
- Orchestration is explicit

These principles are industry-correct.

## Final High-Level Architecture
```
External Producers
        ↓
Thin Ingestion API (FastAPI)
        ↓
Apache Kafka
  ├── RAW Topics
  └── DLQ Topics
        ↓
Long-Running Kafka Consumers
        ↓
GCS Lakehouse (Raw Zone)
            ↑
       Apache Airflow
 (Replay / Backfill / Ops / DQ)
```

## 5. Component Responsibilities

### 1. Think Ingestion API (FastAPI)
Purpose:
- Accept JSON events
- Validate schema (Pydantic)
- Add metadata
- Produce to Kafka

Explicitly NOT doing:
- ❌Transformations
- ❌Aggregations
- ❌State management
- ❌Scheduling

> API exists to feed Kafka, not replace it.

### 2. Streaming Backbone -- Apache Kafka (CORE)
Responsibilities:
- Topic partitioning
- Ordering guarantees (within partition)
- At-least-once delivery
- Consumer groups
- Manual offset commits
- Replay (offset & timestamp)
- DLQ handling

### 3. Lakehouse Raw Zone - GCS
Purpose:
- Durable storage
- Auditability
- Analytics readiness

Layout:
```perl
gs://<bucket>/
 └── raw/
     └── dataset=<name>/
         └── ingestion_date=YYYY-MM-DD/
             ├── data.json / parquet
             └── _metadata.json
```
No curated zone in this project

### 4. Failure Handling (Mandatory)
**Failures we MUST handle:**
- Schema mismatch
- Poison pill records
- Consumer crash
- Storage write failure

How:
- DLQ Kafka topics
- Error metadata in headers
- Replay via Kafka offsets


### 5. Airflow (Orchestration Layer -- Explicit Scope)
What Airflow WILL Do
- ✔ Trigger Kafka replay jobs
- ✔ Run backfills (date / offset range)
- ✔ Perform batch data-quality checks
- ✔ Inspect DLQ topics
- ✔ Generate audit / ops summaries

What Airflow WILL NOT Do
- ❌ Run streaming consumers
- ❌ Schedule ingestion
- ❌ Replace Kafka semantics

> Airflow controls actions around Kafka, not Kafka itself.

### 6. Explicit Non-Goals
We are NOT building:
- ❌ UI dashboards
- ❌ Managed Kafka / PubSub
- ❌ Spark / Flink jobs
- ❌ Delta / Iceberg engines
- ❌ CDC pipelines
- ❌ Full governance engine
- ❌ Auth systems (OAuth, RBAC)

These are intentional exclusions, not missing features.

### 7. Technology Stack
| Layer         | Tool                         |
| ------------- | ---------------------------- |
| Streaming     | Apache Kafka                 |
| Orchestration | Apache Airflow (later phase) |
| API           | FastAPI                      |
| Validation    | Pydantic                     |
| Storage       | GCS                          |
| Runtime       | Docker                       |
| Language      | Python                       |
| Compute       | GCP VM                       |

All open source + cloud

### 8. Data Guarantees
- Delivery: At-least-once
- Ordering: Within partition
- Idempotency: Best-effort consumer writes
- Replay: Offset-based + timestamp-based
- Failure isolation: DLQ topics

### 9. Repository Structure
```
streaming-lakehouse/
 ├── api/
 ├── kafka/
 │   ├── producer/
 │   ├── consumer/
 │   └── topics.py
 ├── airflow/
 │   └── dags/
 ├── storage/
 │   └── gcs/
 ├── contracts/
 ├── scripts/
 ├── docs/
 └── docker-compose.yml
```

