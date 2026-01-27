# Phase-6: Serving & Analytics Layer (Lakehouse Serving Plane)

## StreamLake - Analytics & BI Consumption

---

## 1. Phase-6 Objective

Phase-6 introduces the **Serving & Analytics plane** into StreamLake.

The goal of this phase is to:

- Convert raw ingested streaming data into analytics-ready datasets
- Apply business semantics and data quality rules
- Pre-compute metrics for efficient querying
- Expose governed, low-latency SQL access for analysts and BI tools

This phase **does not modify ingestion, replay, or orchestration logic**.

> Phase-6 is strictly read-only with respect to Kafka and raw ingestion.

---

## 2. Positioning Within StreamLake Architecture

StreamLake is intentionally designed with **clear system plane**

| Plane | Responsibility |
|------|---------------|
| Data Plane | Kafka, Consumers, Raw Storage |
| Control Plane | Airflow, Replay, DataOps |
| **Serving Plane** | **Analytics & BI (Phase-6)** |

Phase-6 completes StreamLake by adding the Serving Plane.


---

## 3. Scope Boundaries (Non-Negotiable)

### Phase-6 IS allowed to:
- Read from lakehouse raw data
- Apply transformation for analytics
- Enforce data quality and business rules
- Compute aggregates and metrics
- Serve data via SQL endpoints

### Phase-6 is NOT allowed to:
- ❌ Write to Kafka
- ❌ Manage Kafka offsets
- ❌ Trigger or control replay
- ❌ Modify raw zone data
- ❌ Orchestrate streaming ingestion

Kafka and Airflow remain authoritative for ingestion and control.

---

## 4. High-Level Data Flow
```
GCS Raw Zone
    ⬇
Silver Tables (Validated & Refined)
    ⬇
Gold Tables (Aggregated Metrics)
    ⬇
SQL Warehouse
    ⬇
BI Tools/Analysts
```
This flow is **incremental, replay-safe, and idempotent**

---

## 5. Silver Layer Design (Refined Data)

### Purpose of Silver Layer

The Silver layer represents **clean, trustworthy, analytics-ready facts**.

Silver answers the question:
> "What actually happened in the business?"

### Responsibilities
- Schema enforcement
- Type casting and normalization
- Deduplication using `ingestion_id`
- Late-arriving data handling (watermarks)
- Business-level validation
- Corrupt record quarantine


## 6. Gold Layer Design (Metrics & Aggregates)

## Purpose of Gold Layer

The Gold layer provides **pre-computed, business-defined metrics**.

Gold answers the question:
> "How is the business performing?"


### Examples of Gold Metrics
- Orders per minute
- Revenue per day
- Order failure rate
- SLA breach counts
- Customer-level aggregates


## Design Principles
- Metics have single authoritative definitions
- Aggregation are incremental
- Designed for BI performance
- Cost-efficient querying

Gold tables are the **primary consumption layer**.

---

## 7. Transformation Engine: Delta Live Table (DLT)

Delta Live Tables (DLT) is used to implement Silver and Gold pipelines

DLT provides:
- Managed incremental processing
- Built-in fault tolerance
- Data quality rules and expectations
- Lineage and observability
- Simplified operational overhead

### Critical Design Rule
> DLT consumes lakehouse data only - **not Kafka directly**.

This preserves the Kafka-first ingestion contract.

---

## 8. SQL Warehouse (Serving Endpoint)

### Purpose

The SQL Warehouse provides a **stable, low-latency serving layer** for analytics.

### Responsibilities
- Serve BI dashboards
- Support ad-hoc analyst queries
- Isolate compute costs
- Provide predictable query performance

### Design Principle
> Streaming systems ingest.
> Warehourses serve.


Analysts never query raw streaming tables directly.

---

## 9. Failure Handling (Phase-6 Scope)


| Failure Type | Handling Strategy |
|-------------|------------------|
| Bad records | Quarantined in Silver |
| Data quality violations | Pipeline fails visibly |
| Late-arriving data | Watermark-based handling |
| Metric logic bugs | Fixed and reprocessed via replay |


### Important
- Phase-6 never resets Kafka offsets
- Replay is initiated only through the Control Plane (Airflow)

## 10. Observability & Governance

Phase-6 provides:
- Pipeline health via DLT UI
- Data quality metrics
- Table-level lineage
- Metric freshness visibility
- Query performance monitoring

This enables analyst trust and operational confidence.

---

## 11. What Phase-6 Explicitly Does NOt Do

- ❌ Serve low-latency transactional APIs
- ❌ Trigger alerts or notifications
- ❌ Replace application databases
- ❌ Own ML feature pipelines
- ❌ Perform real-time decisioning

These are future extensions, not current scope.

---

## 12. Phase-6 Exit Criteria

Phase-6 is considered complete when:

- ✔ Silver tables are defined and populated
- ✔ Gold metrics tables are defined
- ✔ DLT pipelines are running successfully
- ✔ SQL Warehouse is queryable
- ✔ BI-style queries run reliably
- ✔ Ingestion and replay contracts remain untouched

---

## 13. Outcome

With Phase-6 complete, StreamLake becomes:

> A Kafka-first, replayable, operable data platform with a governed analytics serving layer - architected in the style of large-scale internal platforms used at FAANG companies.
