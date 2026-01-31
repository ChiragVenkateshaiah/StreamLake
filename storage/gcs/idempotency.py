from google.cloud import storage


def object_exists(gcs_path: str) -> bool:
    client = storage.Client()
    bucket_name, blob_path = gcs_path.replace("gs://", "").split("/", 1)

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)


    return blob.exists()
