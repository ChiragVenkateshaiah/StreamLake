## Check if Kafka container is actually running
From VM:
```bash
docker ps
```

You must see:
```bash
streamlake-kafka
streamlake-zookeeper
```

If NOT see them:

Start them:
```bash
docker compose up -d
```
Wait for 10 seconds

## Verify Kafka is listening on port 9092
Run on the VM:
```bash
ss -lntp | grep 9092
```

Listening:
```bash
LISTEN 0 4096 0.0.0.0:9092
```