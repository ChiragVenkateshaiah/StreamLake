import json
from datetime import datetime, timezone
from confluent_kafka import Producer
from typing import Dict, Any

from kafka.producer.config import get_kafka_producer_config



class StreamLakeDLQProducer:
    """
    Kafka producer responsible for publishing invalid
    or poison pill events to DLQ topics.
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

        key_bytes = key.encode("utf-8") if key else None
        value_bytes = json.dumps(dlq_record).encode("utf-8")


        headers = {
            **original_headers,
            "dlq_reason": error_reason,
        }


        self.producer.produce(
            topic=self.dlq_topic,
            headers=headers,
            key=key_bytes,
            value=value_bytes,
        )

        self.producer.flush()