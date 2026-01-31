from datetime import datetime, timezone


def build_raw_path(
        bucket: str,
        dataset: str,
        partition: int,
        offset: int,
) -> str:
    ingestion_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return(
        f"gs://{bucket}/raw/"
        f"dataset={dataset}/"
        f"ingestion_date={ingestion_date}"
        f"part-{partition}-{offset}.json"
    )
