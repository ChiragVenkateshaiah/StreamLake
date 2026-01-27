# StreamLake - Kafka Producer Code Skeleton

## Goal of this step
- A reusable Kafka producer
- Deterministic partitioning via keys
- Metadata in Kafka headers
- Clear separation between RAW producer and DLQ producer
- A structure that maps directly to theory

Producer stands alone first.

## Folder Structure
From the project root:
```bash
mkdir -p kafka/producer
touch kafka/producer/__init__.py
touch kafka/producer/config.py
touch kafka/producer/producer.py
touch kafka/producer/dlq_producer.py
```

Final Structure:
```arduino
kafka/
└── producer/
    ├── __init__.py
    ├── config.py
    ├── producer.py
    └── dlq_producer.py
```
This separation is intentional and professional

## 2. Producer Configuration (`config.py`)
```python
from typing import Dict
import os


def get_kafka_producer_config() -> Dict[str, object]:
    """
    Centralized Kafka producer configuration for StreamLake.
    """
    return {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),

        # Strong durability
        "acks": "all",

        # Retry on transient failures
        "retries": 5,


        # Small batching for efficiency
        "linger.ms": 10,


        ## Serializer configuration
        "key.serializer": str.encode,
        "value.serializer": lambda v: v.encode("utf-8"),
    }
```
### Why this matters
- Config is centralized
- Easy to tune later
- Mirrors real production setups


## 3. Core Producer (`producer.py`)
```python
import json
import uuid
from confluent_kafka import Producer
from datetime import datetime, timezone
from typing import Dict, Any

from kafka.producer.config import get_kafka_producer_config


class StreamLakeProducer:
    """
    Kafka producer responsible for publishing valid events
    to StreamLake RAW topics.
    """

    def __init__(self, topic: str):
        self.topic = topic
        self.producer = Producer(get_kafka_producer_config())

    def _delivery_report(self, err, msg):
        """
        Callback for delivery confirmation.
        """
        if err is not None:
            print(f"[ERROR] Delivery failed: {err}")
        else:
            print(
                f"[SUCCESS] Topic={msg.topic()} "
                f"Partition={msg.partition()} "
                f"Offset={msg.offset()} "
            )
        
    def produce(
        self,
        key: str,
        payload: Dict[str, Any],
        dataset: str,
        schema_version: str = "v1",
    ):

        """
        Produce a validation event to Kafka.
        """

        ingestion_id = str(uuid.uuid4())
        event_time = datetime.now(timezone.utc).isoformat()

        headers = {
            "dataset": dataset,
            "schema_version": schema_version,
            "ingestion_id": ingestion_id,
            "producer_services": "streamlake-producer",
        }

        value - json.dumps(payload)

        self.producer.produce(
            topic=self.topic,
            key=key,
            value=value,
            headers=headers,
            on_delivery=self._delivery_reports,
        )

        # Force delivery (safe for learning & small workloads)
        self.producer.flush()
```

## DLQ Producer (`dlq_producer.py`)
```python
import json
from datetime import datetime, timezone
from confluent_kafka import Producer
from typing import Dict, Any

from kafka.producer.config import get_kafka_producer_config



class StreamLakeDLQProducer:
    """
    Kafka producer responsible for publishing invalid
    or poison pill events for DLQ topics
    """


    def __init__(self, dlq_topic: str):
        self.dlq_topic = dlq_topic
        self.producer = Producer(get_kafka_producer_config())


    def send_to_dlq(
        self,
        key: str,
        payload: Dict[str, Any],
        error_reason: str,
        original_headers: Dict[str, Any],
    ):

        """
        Publish failed record to DLQ with error context.
        """


        dlq_record = {
            "payload": payload,
            "error_reason": error_reason,
            "failed_at": datetime.now(timezone.utc).isoformat(),
        }

        headers = {
            **original_headers,
            "dlq_reason": error_reason,
        }

        self.producer.produce(
            topic=self.dlq_topic,
            key=key,
            value=json.dump(dlq_record),
            headers=headers,
        )

        self.producer.flush()
```

## 5. Why this skeleton is correct
#### ✅ Deterministic partitioning
```python
key=key
```
same key -> same partition -> ordering preserved


#### ✅Metadata in headers
Headers ≠ payload
Headers = operational context

This is very important in real pipelines.


#### ✅ At-least-once semantics
- Retries enabled
- Flush after produce
- Consumer will handle duplicates

#### ✅ DLQ separation
- DLQ is explicit
- DLQ is observable
- DLQ is auditable

Exactly how production systems work.


## 7. Quick Manual Test
Create a simple test file:
```bash
touch scripts/test_producer.py
```

```python
from kafka.producer.producer import StreamLakeProducer

producer = StreamLakeProducer(topic="streamlake.orders.raw")


producer.produce(
    key="ORD-100",
    payload={
        "order_id": "ORD-100",
        "amount": 250.50
    },
    dataset="orders"
)
```

Run:
```bash
python scripts/test_producer.py
```

Then consume:
```bash
kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic streamlake.orders.raw \
    --from beginning
```
producer worked if message received.

