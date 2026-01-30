from kafka.consumer.consumer import StreamLakeConsumer

consumer = StreamLakeConsumer(
    topic = "streamlake.orders.raw",
    dataset="orders"
)

consumer.start()