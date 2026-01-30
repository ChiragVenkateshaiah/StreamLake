import json
import uuid
from datetime import datetime, timezone
from confluent_kafka import Producer
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
            print("f[ERROR] Delivery failed: {err}")
        else:
            print(
                f"[SUCCESS] Topic={msg.topic()} "
                f"Partition={msg.partition()} "
                f"Offset={msg.offset()}"
            )
    
    def produce(
            self,
            key: str,
            payload: Dict[str, Any],
            dataset: str,
            schema_version: str = "v1",
    ):
        """
        Produce a validated event to Kafka
        """

        ingestion_id = str(uuid.uuid4())
        event_time = datetime.now(timezone.utc).isoformat()


        headers = {
            "dataset": dataset,
            "schema_version": schema_version,
            "ingestion_id": ingestion_id,
            "ingested_at": event_time,
            "producer_service": "streamlake-producer",
        }

        value = json.dumps(payload).encode("utf-8")
        key_bytes = key.encode("utf-8")

        self.producer.produce(
            topic=self.topic,
            key=key,
            value=value,
            headers=headers,
            on_delivery=self._delivery_report,
        )

        # Force delivery (safe for learning & small workloads)
        self.producer.flush()