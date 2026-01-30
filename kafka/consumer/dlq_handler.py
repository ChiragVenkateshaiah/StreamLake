import json
from datetime import datetime, timezone
from kafka.producer.dlq_producer import StreamLakeDLQProducer


dlq_producer = StreamLakeDLQProducer(
    dlq_topic = "streamlake.orders.dlq"
)


def send_to_dlq(msg, exception: Exception):
    """
    Send failed record to DLQ with context.
    """
    payload = json.loads(msg.value().decode("utf-8"))

    headers = dict(msg.headers() or {})
    headers["consumer_failed_at"] = datetime.now(timezone.utc).isoformat()
    headers["consumer_error"] = str(exception)

    key = msg.key().decode("utf-8") if msg.key() else None

    dlq_producer.send_to_dlq(
        key=key,
        payload=payload,
        error_reason=str(exception),
        original_headers=headers,
    )

    print(
        f"[DLQ] key={key}"
        f"partition={msg.partition()}"
        f"offset={msg.offset()}"
    )