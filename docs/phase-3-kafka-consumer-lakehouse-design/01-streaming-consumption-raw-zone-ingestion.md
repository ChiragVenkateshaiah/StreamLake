# Phase-3: Kafka Consumer & Lakehouse Landing Design

## StreamLake - Streaming Consumption & Raw Zone Ingestion

## 1. Phase-3 Objective
Phase-3 defines how data exits Kafka safely and is landed into a lakehouse raw zone.

By the end of this phase, we answer:
- How consumers are structured
- How failures are handled
- How idempotency is achieved
- How raw data is written to GCS
- How replay is safely supported

This phase proves real production ingestion

## 2. Consumer Role in StreamLake (Context)
In StreamLake:
- Consumer are long-running services
- Kafka remains the system of record
- Storage is downstream
- Offsets are committed only after safe writes

> Never commit offsets before data is safely written

## 3. Consumer Placement in Repository
```markdown
streamlake/
└── kafka/
    └── consumer/
        ├── __init__.py
        ├── consumer.py
        ├── handler.py
        ├── commit_manager.py
        └── dlq_handler.py
```

This separation:
- Improves clarity
- Makes testing easier
- Signals production-grade thinking

## 4. Consumer Group Strategy
### Consumer Group Name
```text
streamlake-consumer-<dataset>
```
Example:
```text
streamlake-consumer-orders
```
### Why Consumer Groups Matter
- Horizontal scalability
- Fault tolerance
- Partition ownership
- Rebalance handling

Each partition is processed by exactly one consumer in the group.

## 5. Offset Management Strategy
### 🔒 Offset Commit Policy
Manual offset commits only

### Commit Timing
1. Poll records
2. Process record
3. Write to GCS successfully
4. Commit offset

If any step fails:
- Offset is NOT committed
- Record will be reprocessed

This guarantees at-least-once delivery

## 6. Failure Handling Strategy (Consumer Side)
### Failure Categories

#### 1. Recoverable Failures
- Temporary GCS outrage
- Network issues
- Transient errors

> Consumer retries automatically

> Offset NOT committed

#### 2. Non-Recoverable Failures (Poison Pills)
- Schema mismatch
- Corrupt payload
- Business-critical validataion failure

> Record sent to DLQ

> Offset committed after DLQ write

This prevents infinite loops.

## 7. DLQ Consumption Model
DLQ handling is explicit, not implicit

### DLQ Record Contains
- Original payload
- Error reason
- Exception trace
- Original Kafka headers
- Failure timestamp

DLQ is observable, auditable, and replayable.


## 8. Lakehouse Raw Zone Design (GCS)
### Raw Zone Layout (Final)
```pgsql
gs://<bucket-name>/
 └── raw/
     └── dataset=<dataset-name>/
         └── ingestion_date=YYYY-MM-DD/
             ├── part-0001.json
             ├── part-0002.json
             └── _metadata.json
```
### Why This Layout is correct
- Partitioned by ingestion date
- Dataset isolation
- Easy downstream consumption
- Replay-friendly

>No transformations.
>
>Raw means raw.

## 9. Idempotency Strategy (Best-Effort)
### Why Idempotency is needed
At-least-once delivery means duplicates are possible.

### Strategy Used
- `ingestion_id` included in every record
- Metadata written alongside data
- Consumers avoid overwriting existing files
- Reprocessing creates new partitions/files

This mirrors how many real systems handle raw zones.

## 10. Replay & Reprocessing Model
Replay is Kafka-native, not storage-driven

### Supported Replays
- Offsets-based replay
- Timestamp-based replay

### Replay Steps
1. Stop consumer
2. Reset offsets
3. Restart consumer
4. Re-write raw data

Airflow will orchestrate this.

## 11. Observability & Logging (Minimal but correct)
Consumer logs include:
- Topic
- Partition
- Offset
- Ingestion ID
- Write path
- Error details

This is enough for:
- Debugging


## 12. What Consumers Do Not Do
- ❌ Transform data
- ❌ Enrich records
- ❌ Join streams
- ❌ Perform aggregations
- ❌ Manage scheduling

Consumers only move data safely.

## 13. Phase-3 Exit Criteria
Phase-3 is complete when:

- Consumer group strategy is frozen
- Offset commit logic is defined
- DLQ behavior is finalized
- GCS raw layout is frozen
- Replay model is clear

