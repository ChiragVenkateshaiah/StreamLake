from confluent_kafka import Consumer
from kafka.consumer.config import get_kafka_consumer_config
from kafka.consumer.handler import handle_record
from kafka.consumer.commit_manager import commit_offset
from kafka.consumer.dlq_handler import send_to_dlq



class StreamLakeConsumer:
    """
    Long-running Kafka consumer for StreamLake.
    """


    def __init__(self, topic: str, dataset: str):
        self.topic = topic
        self.dataset = dataset
        self.group_id = f"streamlake-consumer-{dataset}"

        self.consumer = Consumer(
            get_kafka_consumer_config(self.group_id)
        )

        self.consumer.subscribe([self.topic])

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
                    send_to_dlq(msg, exc)
                    commit_offset(self.consumer, msg)

        except KeyboardInterrupt:
            print("Shutting down consumer...")

        finally:
            self.consumer.close()