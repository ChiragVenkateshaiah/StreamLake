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
        f"[PROCESSING] dataset={dataset}"
        f"key={key}"
        f"partition={msg.partition()}"
        f"offset={msg.offset()}"
    )

    # Later:
    # - write to GCS raw zone
    # - validate metadata
    # - enforce idempotency
