import time
from confluent_kafka.admin import AdminClient, NewTopic, KafkaException


BOOTSTRAP_SERVERS = "127.0.0.1:9092"
KAFKA_READY_RETRIES = 10
KAFKA_READY_DELAY_SEC = 3


def wait_for_kafka():
    """
    Docstring for wait_for_kafka

    Block until Kafka is reachable before attempting topic creation.
    """

    admin = AdminClient({"bootstrap.servers": BOOTSTRAP_SERVERS})

    for attempt in range(1, KAFKA_READY_RETRIES + 1):
        try:
            # list_topics() does an actual metadata fetch
            admin.list_topics(timeout=2)
            print(f"[✔] Kafka is ready (attempt {attempt})")
            return admin
        
        except KafkaException:
            remaining = KAFKA_READY_RETRIES - attempt
            if remaining == 0:
                raise ConnectionError(
                    f"Kafka did not become available after {KAFKA_READY_RETRIES} attempts. "
                    f"Check that the broker is running at {BOOTSTRAP_SERVERS}"
                )
            print(f"[...] Kafka not ready, retrying in {KAFKA_READY_DELAY_SEC}s... (attempt {attempt}/{KAFKA_READY_RETRIES})")
            time.sleep(KAFKA_READY_DELAY_SEC)



def create_topics():
    """
    Docstring for create_topics
    Create all required topics for StreamLake.
    Idempotent - won't fail if topics already exist.
    """
    admin = wait_for_kafka()

    topics = [
        NewTopic(
            topic="streamlake.orders.raw",
            num_partitions=3,
            replication_factor=1,
            config={
                "retention.ms": "604800000", # 7 days
                "compression.type": "snappy",
            }
        ),
        # Add more topics here as StreamLake grows:
        # NewTopic(
        #   topic="streamlake.users.raw",
        #   num_partitions=3,
        #   replication_factor=1
        # ),
    ]

    # Create topics
    fs = admin.create_topics(topics, validate_only=False)

    # Wait for results
    for topic, future in fs.items():
        try:
            future.result() # Block until topic creation completes
            print(f"[✔] Topic '{topic}' created successfully")
        except Exception as e:
            error_msg = str(e).lower()
            if "already exists" in error_msg or "topic_already_exists" in error_msg:
                print(f"[➡] Topic '{topic}' already exists (skipping)")
            else:
                print(f"[x] Failed to create topic '{topic}': {e}")
                raise



if __name__ == "__main__":
    print("=== StreamLake Topic Steup ===\n")
    create_topics()
    print("\n[✔] All topics ready")