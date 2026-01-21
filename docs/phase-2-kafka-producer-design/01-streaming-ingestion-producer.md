# Phase-2: Kafka Producer Design

## StreamLake - Streaming Ingestion Producer

## 1. Phase-2 Objective
Phase-2 defines how data enters Kafka in StreamLake.

By the end of this phase, we answer:
- How producers ar structured
- What guarantees producers provide
- How metadata is attached to events
- How failures are handled at producer level
- How DLQ publishing works

This phase is still design first - but it maps directly to code.


## 2. Producer Role in StreamLake (Context)
In StreamLake:
- The producer is the ingestion boundary
- It converts external events into durable Kafka records
- It enforces schema + metadata discipline
- It does NOT do business logic

> Once an event is written to Kafka successfully, ingestion is considered complete.

## 3. Producer Placement in Repository
```arduino
streamlake/
└── kafka/
    └── producer/
        ├── __init__.py
        ├── producer.py
        ├── config.py
        └── dlq_producer.py
```

This separation:
- Keeps Kafka logic isolated
- Makes testing easier
- Signals clean architecture

## 4. Producer Design Principles
### 🔒 Principle 1: At-Least-Once Delivery
- Producer retries are enabled
- Duplicate events are possible
- Downstream consumers must be idempotent

This is correct and realistic for data platforms

### 🔒 Principle 2: Deterministic Partitioning
- Producer always sets a key
- Key = business identifier (e.g. `order_id`)
- Kafka decides partition deterministically

### 🔒 Principle 3: Metadata is First-Class
- Business payload ≠ operational metadata
- Metadata lives in Kafka headers
- Headers are immutable and traceable


## 5. Producer Configuration
### Required Producer Properties
| Property             | Value               | Why                        |
| -------------------- | ------------------- | -------------------------- |
| `acks`               | `all`               | Strong durability          |
| `retries`            | `> 0`               | Transient failure handling |
| `linger.ms`          | small (e.g. 5–10ms) | Batching                   |
| `enable.idempotence` | optional            | Bonus signal               |
| `key.serializer`     | String              | Deterministic partitioning |
| `value.serializer`   | JSON                | Simplicity                 |

On a single VM, simplicity > Extreme tuning


## 6. Event Structure
#### Message Value (Payload)

```json
{
    "order_id": "ORD-123",
    "customer_id": "CUST-42",
    "amount": 199.99,
    "event_time": "2026-01-21T10:00:00Z"
}
```
#### Kafka Headers (Metadata)
```ini
dataset=orders
schema_version=v1
ingestion_id=<uuid>
producer_service=ingestion-api
ingested_at=<timestamp>
```
Why this matters:
- Debugging
- Replay tracing
- DLQ analysis
- Auditability

## 7. Producer Flow (Step-by-Step)
1. Receive validation payload from API
2. Extract partition key
3. Generate `ingestion_id`
4. Attach metadata headers
5. Serialize payload
6. Produce to RAW topic
7. Wait for Kafka acknowledgment
8. Return success / failure to caller

No side effects.
No downstream dependencies.

## 8. Error Handling Strategy (Producer Side)
### Producer-Level Failures
Examples:
- Broker unavailable
- Timeout
- Serialization error

Strategy
- Retry automatically (Kafka client)
- If retries exhausted -> surface error
- Do NOT silently drop data

Producer failure = ingestion failure.

## 9. DLQ Producer Design
DLQ is used only when the event is invalid, not when Kafka is down.

When Producer Sends to DLQ
- Schema validation failure
- Mandatory field missing
- Payload cannot be serialized

DLQ Message Contains
- Original payload
- Error reason
- Stack trace (optional)
- Original metadata headers

DLQ producer is a separate, explicit component.
```text
dlq_producer.py
```
This separation is intentional and clean.

## 10. What Producer Does NOT Do (Non-Negotiable)
- ❌ Transform data
- ❌ Enrich from databases
- ❌ Perform joins
- ❌ Handle replay
- ❌ Write to storage

If it does these, it is no longer an ingestion producer.


## 11. Observability (Minimal but correct)
Producer logs:
- Topic name
- Partition
- Offset (on success)
- Ingestion ID
- Error details (on failure)

This is enough for:
- Debugging


## 12. Phase-2 Exit Criteria
Phase-2 is considered complete when:
- Producer responsibilities are frozen
- Message structure is finalized
- Header strategy is defined
- Error & DLQ behavior is defined
- Code structure is clear