# 6. Data Flow and Guarantees

## Event Lifecycle

1. Event is received by the ingestion API
2. Schema validation is performed
3. Event is written to Kafka
4. Consumer processes the event
5. Data is written to GCS
6. Offset is committed

## Delivery Semantics

- At-least-once delivery
- Idempotent consumer writes (best effort)


## Ordering Guarantees

- Ordering is guaranteed within a Kafka partition
- Partitioning is based on a business key

## Replay Strategy

- Offset-based replay
- Timestamp-based replay (optional)


## Failure Handling

- Invalid events go to DLQ topics
- Errors are captured in Kafka headers
- Reprocessing occurs via replay
