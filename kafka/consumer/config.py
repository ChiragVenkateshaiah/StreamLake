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