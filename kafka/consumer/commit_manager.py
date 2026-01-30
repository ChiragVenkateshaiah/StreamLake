from confluent_kafka import TopicPartition

def commit_offset(consumer, msg):
    """
    Commit offset for a successfully handled message.
    """

    tp = TopicPartition(
        msg.topic(),
        msg.partition(),
        msg.offset() + 1
    )

    consumer.commit(
        offsets=[tp],
        asynchronous=False,
    )


    print(
        f"[COMMIT] topic={msg.topic()}"
        f"partition={msg.partition()}"
        f"offset={msg.offset()}"
    )