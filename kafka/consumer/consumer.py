import time
from confluent_kafka import Consumer, KafkaException
from kafka.consumer.config import get_kafka_consumer_config
from kafka.consumer.handler import handle_record
from kafka.consumer.commit_manager import commit_offset
from kafka.consumer.dlq_handler import send_to_dlq



class StreamLakeConsumer:
    """
    Long-running Kafka consumer for StreamLake.
    """

    KAFKA_READY_RETRIES = 10
    KAFKA_READY_DELAY_SEC = 3

    def __init__(self, topic: str, dataset: str):
        self.topic = topic
        self.dataset = dataset
        self.group_id = f"streamlake-consumer-{dataset}"

        self.consumer = Consumer(
            get_kafka_consumer_config(self.group_id)
        )

        self.consumer.subscribe([self.topic])

    def _wait_for_kafka(self):
        """
        Block until Kafka is reachable before subscribing.
        Prevents immediate 'Connection refused' crashes on cold starts.
        """
        for attempt in range(1, self.KAFKA_READY_RETRIES + 1):
            try:
                # list_topics() does an actual TCP handshake + metadata fetch
                self.consumer.list_topics(timeout=2)
                print(f"[✔] Kafka is ready (attempt {attempt})")
                return
            
            except KafkaException:
                remaining = self.KAFKA_READY_RETRIES - attempt
                if remaining == 0:
                    raise ConnectionError(
                        f"Kafka did not become available after {self.KAFKA_READY_RETRIES} attempts."
                        f"Check that the broker is running and KAFKA_BOOTSTRAP_SERVERS is correct"
                    )
                print(f"[...] Kafka not ready, retrying in {self.KAFKA_READY_DELAY_SEC}s... (attempt {attempt}/{self.KAFKA_READY_RETRIES})")
                time.sleep(self.KAFKA_READY_DELAY_SEC)

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
                    print(f"[ERROR] Exception in handle_record: {exc}")
                    import traceback
                    traceback.print_exc()
                    send_to_dlq(msg, exc)
                    commit_offset(self.consumer, msg)

        except KeyboardInterrupt:
            print("Shutting down consumer...")

        finally:
            self.consumer.close()