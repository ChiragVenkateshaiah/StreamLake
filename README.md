# StreamLake - Kafka-First Real-Time Event-Driven Lakehouse Platform

## Problem Statement

Modern business generate high-volume, continuous event data (orders, transactions, user actions) and require:

- Near real-time analytics
- Strong data correctness guarantees
- Replayability and failure recovery
- Governed, BI-ready datasets for analytics teams

Traditional batch-only data pipelines are insufficient for these requirements.

**StreamLake** is designed to solve this problem by providing a Kafka-first, replayable, and operable data platform that bridges real-time ingestion with governed analytics.

## Architecture Overview

StreamLake is designed as a **multi-plane system**, following patterns commonly used in large-scale internal platforms.

```text
Producers
    ⬇
Kafka (Ingestion System of Record)
    ⬇
Consumers (Streaming Sink)
    ⬇
Lakehouse (GCS + Delta)
├─ Bronze (Raw)
├─ Silver (Refined)
└─ Gold (Metrics)
    ⬇
SQL Warehouse
    ⬇
BI / Analysts
```
Airflow operates alongside this flow as a **control plane** for replay, backfill, and operational

[Architecture Diagram](/arichtecture_diagram/StreamLake_Architecture.png)

## Design Principles

- **Kafka-first architecture**
    Kafka is the authoritative system of record for ingestion.

- **Event-driven design**
    Producers and consumers are fully decoupled.

- **Immutable raw data**
    Raw data is never mutated, enabling replay and recovery.

- **Clear separation of concerns**
    Ingestion, processing, control, and serving are isolated.

- **Replayability by design**
    Recovery is achieved through Kafka replay, not storage hacks.

- **Deterministic processing guarantees**
    Ordering is guaranteed where it matters (per business key).

---

## System Planes & Components

### Data Plane
Responsible for moving and persisting data.

- Apache Kafka (Event backbone)
- Kafka producers (Ingestion boundary)
- Kafka consumers (Streaming sink)
- GCS raw storage (Bronze)
- Lakehouse tables (Silver & Gold)


### Control Plane
Responsible for operating and recovering the system.

- Apache Airflow
- Replay orchestration
- Backfill workflows
- DLQ inspection
- Data quality checks

### Serving Plane (Phase-6)
Responsible for analytics consumption.

- Delta Live Tables (Silver & Gold pipelines)
- SQL Warehouse
- BI / Analyst access

---

## Data Flow (End-to-End)

1. Business services emit events via Kafka producers
2. Events are buffered, ordered, and retained in Kafka
3. Consumers read events and safely land raw data into the lakehouse
4. Silver tables apply validataion, deduplication, and refinement
5. Gold tables compute business metrics and aggregates
6. SQL Warehouse serves analytics queries to BI tools

Kafka remains the ingestion system of record throughout.

---

## Serving & Analytics (Phase-6)

Phase-6 introduces a **read-only serving layer** on top of the lakehouse.

- Silver tables provide clean, analytics-ready facts.
- Gold tables provide pre-computed business metrics
- Delta Live Tables amanage incremental processing and quality rules
- SQL Warehouse exposes governed, low-latency SQL access

This layer enables BI consumption **without impacting ingestion, replay, or control logic**.


## Failure handling & Recovery

- Invalid or poison events are isolated using DLQ topics
- Offsets are committed only after safe storage writes
- Failure never block healthy data
- Replay is Kafka-native (offset or timestamp based)
- Airflow orchestrates replay and backfill workflows

Recovery is deterministic, auditable, and operator-controlled.

## Scalability & Trade-offs

### Scalability
- Horizontal scaling via Kafka partitions
- Consumer groups for parallel processing
- Incremental lakehouse processing
- Compute isolation via SQL Warehouse

### Trade-Offs
- At-least-once ingeston for durability
- Micro-batch processing for throughput vs latency balance
- No real-time transactional serving (by design)
- Analytics optimized over ultra-low-latency decisions


## What StreamLake Is (and Is Not)

### StreamLake Is:
- A Kafka-first ingestion platform
- A replayable, operable data system
- A governed analytics foundation
- A FAANG-style internal data platform design

### StreamLake Is Not:
- A transactional API serving layer
- A real-time alerting engine
- A CDC replication system
- A full ML feature store (future extension)

## Outcome

StreamLake demonstrates the design and implementation of a **production-grade, Kafka-first data platform**, combining real-time ingestion, operational control, and governed analytics - modeled after internal platforms used at large-scale technology companies.