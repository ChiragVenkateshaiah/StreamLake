import json
from storage.gcs.path_builder import build_raw_path
from storage.gcs.raw_writer import write_raw_record

def handle_record(msg, dataset: str):
    """
    Process a single Kafka record.
    
    This function represents the 'safe handling boundary'.
    """
    key = msg.key().decode("utf-8") if msg.key() else None
    value = json.loads(msg.value().decode("utf-8"))
    headers = dict(msg.headers() or [])

    gcs_path = build_raw_path(
        bucket="streamlake-bucket",
        dataset=dataset,
        partition=msg.partition(),
        offset=msg.offset()
    )

    record = {
        "key": key,
        "payload": value,
        "headers": headers,
        "kafka": {
            "topic": msg.topic(),
            "partition": msg.partition(),
            "offset": msg.offset(),
            "timestamp": msg.timestamp()[1],
        }
    }

    
    write_raw_record(gcs_path, record)
