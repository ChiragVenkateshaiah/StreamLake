# Phase-4: Airflow Orchestration Design

## StreamLake - Operational Control Plane

## Phase-4 Objective
Phase-4 introduced operational orchestration into StreamLake.

The goal is not to control streaming, but to:

- Coordinate replay
- Enable backfills
- Operate DLQ workflows
- Run batch data-quality checks
- Provide audit & operational visibility

This phase elevates StreamLake from:

> *"streaming pipeline" -> "operable data platform"*

## 2. Airflow's Role is StreamLake
### Airflow is the Control Plane, NOT the Data Plane
| Component   | Role                       |
| ----------- | -------------------------- |
| Kafka       | Streaming system of record |
| Consumers   | Continuous data movement   |
| GCS         | Durable raw storage        |
| **Airflow** | Operational orchestration  |

> Airflow never runs continuously.
>
> Kafka consumers always do.

This separation is industry-correct.


## 3. Airflow Placement in Repository
```markdown
streamlake/
└── airflow/
    ├── dags/
    │   ├── replay_dag.py
    │   ├── backfill_dag.py
    │   ├── dlq_inspection_dag.py
    │   └── data_quality_dag.py
    ├── plugins/
    └── README.md
```
Only 4 DAGs.
No sprawl. No overengineering.


## 4. Airflow Execution Model
- Executor: LocalExecutor
- Deployment: Docker Compose
- Schedule: Manual or ad-hoc
- Trigger style: On-demand

Why?
- Replay & backfill are human-initiated
- Not cron-driven pipelines


## 5. DAG-1: Kafka Replay DAG (CORE)
### Purpose
Reprocess historical data from Kafka safely.

### When Used:
- Downstream bug fixed
- Storage failure recovered
- Data corruption detected

### High-Level Steps
1. Stop Kafka consumer
2. Reset offsets (offset or timestamp based)
3. Restart consumer
4. Monitor reprocessing

### Why This is Powerful
- Replay uses Kafka, not storage
- We replay from Kafka because it is the ingestion system of record

## 6. DAG-2: Backfill DAG
### Purpose
Re-ingest data for a specific date range or dataset

### Example Use Case
- Reprocessing `orders` for `2026-01-15 -> 2026-01-16`

### What it Does
- Parameterized execution
- Triggers replay logic
- Tracks completion status

Backfill is orchestrated, not streamed.


## 7. DAG-3: DLQ Inspection DAG
### Purpose
Operational visibility into bad data.

### What it Does
- Consume DLQ topic (batch mode)
- Summarize error reasons
- Generate report:
    - error type
    - record count
    - timestamps

### Why This Matters
Most pipelines fail silently.

StreamLake will not. DataOps is channelized


## 8. DAG-4: Data Quality Check DAG
### Purpose
Lighweight, batch-oriented validation.

### Example Checks
- Files exist for expected date
- Row count > 0
- Metadata file present
- No unexpected empty partitions

### Important
- This is not a full DQ framework
- Just enough to show operational awareness

## 9. What Airflow Will NOT Do
- ❌ Run Kafka consumers
- ❌ Schedule streaming ingestion
- ❌ Process individual Kafka messages
- ❌ Replace offset management

### Why?
- Airflow is batch-oriented and unsuitable for low-latency streaming. Kafka consumers must be long-running services.


## 10. Parameters & Config Strategy
Airflow DAGs accept:
- `dataset`
- `topic`
- `start_offset`
- `end_offset`
- `start_timestamp`

This makes DAGs:
- Reusable
- Explicit
- Operator-friendly


## 11. Observability & Ops Signals
### Each DAG logs:
- Dataset name
- Topic name
- Offset range
- Execution time
- Success / failure

### Enough for:
- Debugging
- Demo


## 12. Phase-4 Exit Criteria
Phase-4 is complete when:
- ✔ Airflow's role is clearly defined
- ✔ Replay DAG exists
- ✔ Backfill DAG exists
- ✔ DLQ inspection DAG exists
- ✔ DQ DAG exists
- ✔ No overlap with Kafka streaming logic


>**Note: StreamLake is a completely operable data platform**