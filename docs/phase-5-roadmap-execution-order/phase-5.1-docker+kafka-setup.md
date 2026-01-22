# StreamLake - Docker + Kafka Setup (Phase-5.1)

## Goal of this step
By the end of this step: **"Apache Kafka will be running using Compose on a GCP VM, and I can create topics, produce messages, and consume them"**

If this is true, everything else becomes easy.


## Prerequisites on the VM
Make sure these are installed on GCP VM:
```bash
docker --version
docker compose version
```
if Docker is not installed, install if first from official repo (Ubuntu):
```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
```

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

```bash
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu noble stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

```bash
sudo apt update
```

### Install Docker + Compose:

```bash
sudo apt install -y docker-ce docker-ce-cli containerd.io 
sudo apt install -y docker-ce
docker-buildx-plugin docker-compose-plugin
```

Now add user to Docker group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Restart the VM and VS code reload and then verify:

```bash
docker --version
docker compose version
```


## Folder Location
```bash
~/projects/StreamLake
```
Placed Docker infra at the project root, exactly as designed


## Create `docker-compose.yml`
```yaml
version: "3.8"

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    container_name: streamlake-zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: streamlake-kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181

      # Kafka listeners
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092

      # Single-node safe defaults
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1

      # Disable auto topic creation (GOOD PRACTICE)
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "false"
```

### Why this setup is correct
- Single broker -> perfect for learning
- Explicit topic creation -> production discipline
- No hidden magic
- Easy to reason about offsets, partitions, replay

## Start Kafka
From the StreamLake root directory:
```bash
docker compose up -d
```
Verify containers:
```bash
docker ps
```
Result:
```bash
streamlake-zookeeper
streamlake-kafka
```

## 5. Verify Kafka is Reachable
Enter the Kafka container:
```bash
docker exec -it streamlake-kafka bash
```

List topics
```bash
kafka-topics --bootstrap-server localhost:9092 --list
```
If this works -> Kafka is healthy ✅


## 6. Create StreamLake Topics (Phase-1 Applied)
Create RAW topic:
```bash
kafka-topics \
    --bootstrap-server localhost:9092 \
    --create \
    --topic streamlake.orders.raw \
    --partitions 3 \
    --replication-factor 1
```
Create DLQ topic:
```bash
kafka-topics \
    --bootstrap-server localhost:9092 \
    --create \
    --topic streamlake.orders.dlq \
    --partitions 1 \
    --replication-factor 1
```
Verify:
```bash
kafka-topics --bootstrap-server localhost:9092 --describe
```
This confirms Phase-1 design is now REAL

## 7. Smoke Test
### Produce a test message
```bash
kafka-console-producer \
    --bootstrap-server localhost:9092 \
    --topic streamlake.orders.raw \
    --property "parse.key=true" \
    --propery "key.separator=:"
```

Message:
```bash
ORD-1:{"order_id": "ORD-1", "amount":100}
```

### Consume it
```bash
kafka-console-consumer \
    --bootstrap-server localhost:9092 \
    --topic streamlake.orders.raw \
    --from-beginning
```

## Confirmation:
- Kafka set up
- Used Docker Compose (industry standard)
- Created deterministic topics
- Controlled partitions
- Proven end-to-end Kafka flow
