import json
from google.cloud import storage
from storage.gcs.idempotency import object_exists



def write_raw_record(
        gcs_path: str,
        record: dict,
):
    if object_exists(gcs_path):
        print(f"[IDEMPOTENT-SKIP] {gcs_path}")
        return
    
    client = storage.Client()
    bucket_name, blob_path = gcs_path.replace("gs://", "").split("/", 1)

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)


    blob.upload_from_string(
        data=json.dumps(record),
        content_type="application/json"
    )

    print(f"[GCS-WRITE] {gcs_path}")