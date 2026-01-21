# Phase-1: Kafka Design for StreamLake

This directory contains the Phase-1 design documentation for **StreamLake**, focused specifically

Phase-1 builds on the fronzen Phase-0 architecture and defines how Kafka is used as the **streaming backhone and system of record** for ingestion.

All decisions documented here are considered **locked** for the remainder of the project unless explicitly revisited in a future phase.

---

## Purpose of Phase-1

The purpose of Phase-1 is to establish a **clear, production-grade Kafka design** that answer the following questions:

- How Kafka topics are named
- How partitions are defined
- How ordering guarantees are achieved
- How failures are isolated using DLQ
- How replay and reprocessing are enabled
- How consumers are scaled using consumer groups

This phase focuses on **design clarity and correctness**, not implementation.


---

## Scope of This Phase

### In Scope
- Kafka topic naming conventions
- Partitioning strategy and key selection
- Consumer group design
- Replay semantics using offsets and timestamps
- Dead Letter Queue (DLQ) strategy

### Out of Scope
- Kafka producer implementation details
- Kafka consumer implementation details
- Stream processing or transformations
- Orchestration logic (handled later by Airflow)
- Infrastructure automation

---

## Design Principles

The Kafka design in StreamLake follows these principles:

1. Kafka is the **system of record** for ingestion
2. Ordering is guaranteed **only within partitions**
3. Replayability is mandatory
4. Failures must be isolated, not hidden
5. Simplicity is preferred over premature optimization

These principles align with real-world data engineering practices.

---

## Documents in This Phase

- **01-topic-and-partition-strategy.md**
  Defines Kafka topic structure, paritioning rules, ordering guarantees, and DLQ design.


---

## Relationship to Other Phases

- **Phase-0** defines the overall architecture and scope
- **Phase-1** defines Kafka-specigic design decisions
- **Phase-2** will implement Kafka producers
- **Phase-3** will implement Kafka consumers and storage landing
- **Phase-4** will introduce orchestration using Airflow


---


## Phase-1 Exit Criteria

Phase-1 is considered complete when:
- Kafka topic naming is finalized
- Partition and key strategy is finalized
- Replay and DLQ behavior is clearly defined
- No ambiguity remains about Kafka usage

