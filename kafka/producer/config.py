from typing import Dict
import os


def get_kafka_producer_config() -> Dict[str, object]:
    """
    Centralized Kafka producer configuration for StreamLake.
    """

    return {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVICES", "127.0.0.1:9092"),

        # Strong durability
        "acks": "all",

        # Retry on transient failures
        "retries": 5,

        # Small batching for efficiency
        "linger.ms": 10,

        # Serializer configuration
        ## "key.serializer": str.encode,
        ## "value.serializer": lambda v: v.encode("utf-8"),
    }