# StreamLake - Kafka Consumer Code Skeleton

## Phase-3: Consumption, Offset Management & Raw Zone Landing

### Goal of this step
By the end of this step, you will have:
- A long-running Kafka consumer
- Manual offset management
- Clear success vs failure paths
- DLQ handling from the consumer side
- A structure that prevents data loss

> Golden rule:
Never commit offsets before data is safely handled.

## 1. Consumer Folder Structure
From the project root:
```bash
mkdir -p kafka/consumer
touch kafka/consumer/__init__.py
touch kafka/consumer/config.py
touch kafka/consumer/handler.py
touch kafka/consumer/commit_manager.py
touch kafka/consumer/dlq_handler.py
```
Final structure:
```bash
kafka/
└── consumer/
    ├── __init__.py
    ├── config.py
    ├── consumer.py
    ├── handler.py
    ├── commit_manager.py
    └── dlq_handler.py
```
This separation is intentional and production-style.

## 2. Consumer Configuration (config.py)

```python
from typing import Dict
import os


def get_kafka_consumer_config(group_id: str) -> Dict[str, object]:
    """
    Centralized Kafka consumer configuration for StreamLake.
    """
    return {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092"),
        "group.id": group_id,

        # Disable auto-commit (CRITICAL)
        "enable.auto.commit": False,

        # Start from earliest if no offset exists
        "auto.offset.reset": "earliest",

        # Stability settings
        "session.timeout.ms": 30000,
        "max.poll.interval.ms": 300000,
    }
```
Why this matters
- `enable.auto.commit = False` you control correctness
- Offsets move only after successful processing
- This is non-negotiable in real pipelines

## 3. Core Consumer Loop (`consumer.py`)
```python
from confluent_kafka import Consumer
from kafka.consumer.config import get_kafka_consumer_config
from kafka.consumer.handler import handle_record
from kafka.consumer.commit_manager import commit_offset
from kafka.consumer.dlq_handler import send_to_dlq


class StreamLakeConsumer:
    """
    Long-running Kafka consumer for StreamLake.
    """

    def __init__(self, topic: str, dataset: str):
        self.topic = topic
        self.dataset = dataset
        self.group_id = f"streamlake-consumer-{dataset}"

        self.consumer = Consumer(
            get_kafka_consumer_config(self.group_id)
        )
        self.consumer.subscribe([self.topic])

    def start(self):
        """
        Start polling Kafka indefinitely.
        """
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    print(f"[ERROR] Consumer error: {msg.error()}")
                    continue

                try:
                    handle_record(msg, self.dataset)
                    commit_offset(self.consumer, msg)

                except Exception as exc:
                    send_to_dlq(msg, exc)
                    commit_offset(self.consumer, msg)

        except KeyboardInterrupt:
            print("Shutting down consumer...")

        finally:
            self.consumer.close()
```

## 4. Record Handler (handler.py)
```python
import json


def handle_record(msg, dataset: str):
    """
    Process a single Kafka record.

    This function represents the 'safe handling boundary'.
    """
    key = msg.key().decode("utf-8") if msg.key() else None
    value = json.loads(msg.value().decode("utf-8"))

    headers = dict(msg.headers() or [])

    # For now, just log the record
    print(
        f"[PROCESSING] dataset={dataset} "
        f"key={key} "
        f"partition={msg.partition()} "
        f"offset={msg.offset()}"
    )

    # Later:
    # - write to GCS raw zone
    # - validate metadata
    # - enforce idempotency
```
Why this separation matters
- Business logic stays out of the consumer loop
- Easy to test
- Easy to extend for GCS writes

## 5. Offset Commit Logic (`commit_manager.py`)
```python
from confluent_kafka import TopicPartition

def commit_offset(consumer, msg):
    """
    Commit offset for a successfully handled message.
    """

    tp = TopicPartition(
        msg.topic(),
        msg.partition(),
        msg.offset() + 1
    )

    consumer.commit(
        offsets=[tp],
        asynchronous=False,
    )


    print(
        f"[COMMIT] topic={msg.topic()}"
        f"partition={msg.partition()}"
        f"offset={msg.offset()}"
    )
```
Why offset + 1?
Kafka commits the next offset to read, not the current one.
This detail is frequently misunderstood

## DLQ Handler (`dlq_handler.py`)
```python
import json
from datetime import datetime
from kafka.producer.dlq_producer import StreamLakeDLQProducer


dlq_producer = StreamLakeDLQProducer(
    dlq_topic="streamlake.orders.dlq"
)


def send_to_dlq(msg, exception: Exception):
    """
    Send failed record to DLQ with context.
    """
    payload = json.loads(msg.value().decode("utf-8"))

    headers = dict(msg.headers() or {})
    headers["consumer_failed_at"] = datetime.utcnow().isoformat()
    headers["consumer_error"] = str(exception)

    key = msg.key().decode("utf-8") if msg.key() else None

    dlq_producer.send_to_dlq(
        key=key,
        payload=payload,
        error_reason=str(exception),
        original_headers=headers,
    )

    print(
        f"[DLQ] key={key} "
        f"partition={msg.partition()} "
        f"offset={msg.offset()}"
    )
```

## 7. Consumer Execution Script
`scripts/run_consumer.py`
```python
from kafka.consumer.consumer import StreamLakeConsumer

consumer = StreamLakeConsumer(
    topic="streamlake.orders.raw",
    dataset="orders"
)

consumer.start()
```
## 8. Offset Management Theory
| Scenario              | Offset committed? |
| --------------------- | ----------------- |
| Successful processing | ✅ Yes             |
| DLQ write success     | ✅ Yes             |
| Crash before handling | ❌ No              |
| Crash after commit    | ✅ Yes             |

What this guarantees
- At-least-once delivery
- No silent data loss
- Safe reprocessing via replay

This is exactly what real pipelines do.

## 9. What This Consumer Does Not Do (Locked)
- ❌ Auto-commit offsets
- ❌ Swallow exceptions
- ❌ Perform transformations
- ❌ Handle replay logic
- ❌ Run in Airflow

This keeps responsibilities clean.

## Phase-3 Code Exit Criteria
Before moving on, ensure:
- Consumer reads messages
- Offsets commit only after handling
- Failures go to DLQ
- Consumer restarts safely
- No auto-commit enabled
