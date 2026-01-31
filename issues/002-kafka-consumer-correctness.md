# ISSUE-002: Kafka Producer-Consumer Correctness & Plane Responsibility

## Context

This issue documents the debugging, validation, and correctness verification of StreamLake's Kafka producer and consumer interaction.

The goal was not just to make the pipeline "work", but to **prove correctness** with respect to:

- Kafka control plane vs data plane responsibility
- Deterministic partitioning
- Offset progression
- At-least-once delivery semantics

---

## Observed Behavior (Expected & Verified)

### Producer Behavior

Multiple producer executions resulted in **monotonically increasing offsets** for the same partition and key.

Example output:

```bash
[SUCCESS] Topic=streamlake.orders.raw Partition=1 Offset=2
[SUCCESS] Topic=streamlake.orders.raw Partition=1 Offset=3
[SUCCESS] Topic=streamlake.orders.raw Partition=1 Offset=4
[SUCCESS] Topic=streamlake.orders.raw Partition=1 Offset=5
[SUCCESS] Topic=streamlake.orders.raw Partition=1 Offset=6
[SUCCESS] Topic=streamlake.orders.raw Partition=1 Offset=7
```

Key observations:
- Same business key (`ORD-100`) consistently mapped to **Partition 1**
- Offsets increased sequentially without gaps
- Confirms deterministic partitioning via key

---

### Consumer Behavior

The consumer processed messages **in strict offset order** and committed offsets only after successful processing.

Example output:
```bash
[PROCESSING] dataset=orders key=ORD-100 partition=1 offset=0
[COMMIT] topic=streamlake.orders.raw partition=1 offset=0

[PROCESSING] dataset=orders key=ORD-100 partition=1 offset=1
[COMMIT] topic=streamlake.orders.raw partition=1 offset=1

...

[PROCESSING] dataset=orders key=ORD-100 partition=1 offset=7
[COMMIT] topic=streamlake.orders.raw partition=1 offset=7
```
Key obervations:
- Processing order strictly followed Kafka offsets
- No skipped or duplicated offsets
- Commit happened **after** processing
- Confirms manual offset management correctness

---

## Key Debugging Learnings

### 1. Control Plane vs Data Plane Responsibility

- **Kafka control plane**
    - Partition assignment
    - Offset tracking
    - Consumer group coordination

- **Application data plane**
    - Message processing
    - DLQ routing
    - Explicit offset commits

The application does **not** manage offsets implicitly; it only advances them after safe handling.

---

### 2. Correct Offset Commit Semantics (confluent-kafka)

The consumer uses `TopicPartition` objects for commits:

```python
TopicPartition(topic, partition, offset + 1)
```

This required by the `confluent-kafka` client and ensures:
- No silent failures
- Correct resume behavior after restarts

---

### 3. At-Least-Once Delivery (By Design)

Observed behavior confirms:
- Messages may be reprocessed if a crash happens before commit
- No data loss occurs
- Duplicate handling is delegated downstream

This matches StreamLake's design goals.

---

### Conclusion

This issue validates that StreamLake's Kafka ingestion layer behaves correctly under real execution:

- Deteministic partitioning
- Ordered consumption
- Explicit and offset advancement
- Clear separation of responsibilities

This correctness proof is foundational before extending the system to:
- Lakehouse raw-zone writes
- Idempotent storage
- Airflow-based replay and backfill

---

##  Status

### What I validated beyond "it works"

One important milestone in Phase-2 was **proving correctness**, not just producing data.

I verified that:
- Kafka partitions are assigned deterministically via business keys
- Offsets increase monotomically per partition
- Consumers are committed **only after successful processing**
- Offsets are committed **only after successful processing**

Seeing the producer advance offsets (2 -> 7) and the consumer replay and commit those offsets cleanly gave confidence that **control-plane and data-plane responsibilities are correctly separated**.

This kind of validation is easy to skip - but it's where real streaming systems either become reliable or fragile.