# 5. Technology Stack

StreamLake uses open-source and free-tier compatible technologies.


## Core Technologies

- Apache Kafka for streaming ingestion
- FastAPI for ingestion API
- Pydantic for schema validation
- Google Cloud Storage for lakehouse raw zone
- Apache Airflow for orchestration
- Docker and Docker Compose for runtime
- Python as the primary language


## Design Rationale

Kafka is chosen for its strong ordering, replay, and durability guarantees.

Airflow is used only for orchestration, not streaming.

GCS provides cheap and durable object storage.

All components can be run at zero cost using open-source software and GCP free tier.

