from kafka.producer.producer import StreamLakeProducer

producer = StreamLakeProducer(topic="streamlake.orders.raw")

producer.produce(
    key="ORD-100",
    payload={
        "order_id": "ORD-100",
        "amount": 250.50
    },
    dataset="orders"
)