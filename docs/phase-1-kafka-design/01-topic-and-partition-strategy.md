# Phase-1: Kafka Topic & Partition Strategy

## StreamLake (Kafka-First Streaming Ingestion Platform)

## Phase-1 Objective
Phase-1 defines how Kafka is used correctly in StreamLake.

By the end of this phase, we must have clear answers to:
- How topics are named
- How partitions are chosen
- How ordering is guaranteed
- How failures are isolated
- How replay is enabled

If this phase is solid, everything else becomes easy.

## 2. Kafka Design Principles
🔒 Principle 1: Kafka Is the Ingestion System of Record
- Producers write once
- Consumer replay when needed
- Storage failures never cause data loss

🔒 Principle 2: Ordering Is Guaranteed Only Where It Matters
- Ordering is per partition
- Partition key must be business-meaningful

🔒 Principle 3: Failures Are Isolated, Not Hidden
- Bad data goes to DLQ
- Healthy data continues flowing

These are core Data Engineering principles.

## 3. Topic Naming Convention (Final)

### Naming Pattern
```php-template
streamlake.<dataset>.<purpose>
```
### Topic We Will Create
| Topic                   | Purpose                 |
| ----------------------- | ----------------------- |
| `streamlake.orders.raw` | Valid incoming events   |
| `streamlake.orders.dlq` | Invalid / poison events |

#### Example dataset: `orders`
Later datasets can reuse the same pattern


## 4. Why Only TWO Topics per Dataset?
This is intentional and mature design.

❌ We are NOT creating:
- retry topics
- validated topics
- enriched topics

Why?

- This is ingestion, not transformation
- Extra topics add noise, not value (at this stage)

## 5. Partition Strategy

### Partition Key
```ini
partition_key = business_id
```

Examples:
- `order_id`
- `customer_id`
- `transaction_id`

### Why This Is Correct
- ✔ Guarantees ordering per business entity
- ✔ Enables deterministic replay
- ✔ Prevents random partition skew
- ✔ Matches real-world systems

## 6. Number of Partitions (VM-Friendly & Scalable)
### Initial Setup
```java
Partitions = 3
Replication Factor = 1
```

Why:
- Works on a single VM
- Enough to demonstrate parallelisn
- Easy to reason about rebalancing

"Partition count is configurable based on throughput requirements"

## 7. Ordering Guarantees
What We Guarantee
✔ Ordering within a partition

What We Do NOT Guarantee
❌ Global ordering across partitions

This distinction is critical and often misunderstood

## 8. Producer Semantics
### Producer Guarantees
- At-least-once delivery
- Retries enabled
- Metadata in headers

### Headers to Include
```ini
dataset=orders
schema_version=v1
ingestion_id=<uuid>
event_timestamp=<ts>
```
These headers are useful for debugging and replay.


## 9. Consumer Group Strategy

### Consumer Group Name
```
streamlake-consumer-orders
```
Why Consumer Groups Matter
- Horizontal scalability
- Partition ownership
- Fault tolerance

Each partition -> consumed by only one consumer in the group

## 10. Replay Strategy (Kafka Native)
Supported Replays
- ✔ Offset-based replay
- ✔ Timestamp-based replay

How Replay Works
- Stop consumer
- Reset offsets
- Restart consumer
- Reprocess data

Airflow will orchestrate this later -- Kafka owns the data.

## 11. DLQ Strategy (Production-Grade)

When Events Go to DLQ
- Schema mismatch
- Deserialization failure
- Poison pill record
- Business-critical validation failure

DLQ Message Contains
- Original payload
- Error reason
- Stack trace (if applicable)
- Original headers

This is non-negotiable in real systems.

## 12. Topic Creation (Declarative)
Topics will be created via:
- Kafka CLI
- Or a Python admin script

Example:
```yaml
streamlake.orders.raw
    partitions: 3
    retention.ms: default

streamlake.orders.dlq
    partitions:1
    retention.ms: longer
```
DLQ does NOT need high parallelism.


## 13. What This Phase Proves
- ✔ Kafka partitions
- ✔ Ordering guarantees
- ✔ Consumer groups
- ✔ Replay semantics
- ✔ DLQ design
- ✔ Production trade-offs

This is core Data Engineering competency

