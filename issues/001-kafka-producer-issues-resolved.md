# Real-World Issues Encountered & Debugging

During implementation, multiple Kafka connectivity issues were encountered and resolved. These issues demonstrate practical Kafka debugging and problem-solving skills.

## Issue-1: Duplicate Port in Bootstrap Server
### Error Observed
```vbnet
localhost:127.0.0.1:9092:9092/bootstrap
Failed to resolve 'localhost:127.0.0.1:9092:9092'
```

### Root Cause
The bootstrap server configuration accidentally contained the port twice

### Resolution
Corrected the configuration by removing the duplicated port segment.

This issue was identified by carefully reading the error message and tracing the malformed address.


## Issue-2: Invalid Port After Partial Fix
### Error Observed
```bash
Connect to ipv4#127.0.0.1:127 failed: Connection refused
```

### Root Cause
An incorrect bootstrap value caused Kafka to interpret `127` as the port number

### Resolution
Updated the configuration to use the correct and explicit address:
```text
127.0.0.1:9092
```

## Issue-3: Docker Kafka Advertised Listener Mismatch
### Symptom
- Kafka CLI worked inside the container
- Producer failed from the host

### Root Cause
Misconfigured `KAFKA_ADVERTISED_LISTENERS` in Docker caused clients to receive unreachable broker addresses.

### Resolution
Aligned:
- `KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://127.0.0.1:9092`
- Producer `bootstrap.servers=127.0.0.1:9092`

## Final Confirmation

After fixes:

```text
[SUCCESS] Topic=streamlake.orders.raw Partition=1 Offset=0
```

Consumer verification:

```json
{"order_id": "ORD-100", "amount": 250.5}
```

This confirmed end-to-end producer connectivity and correctness.
