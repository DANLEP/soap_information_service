from google.cloud import storage

credentials_file = "credentials.json"
bucket_name = "soap_istt"
google_url = "https://storage.googleapis.com/"


async def upload_to_gcs(file):
    destination_blob_name = f"photo/{file.filename}"
    # Initialize the Google Cloud Storage client with the credentials
    storage_client = storage.Client.from_service_account_json(credentials_file)

    # Get the target bucket
    bucket = storage_client.bucket(bucket_name)

    # Upload the file to the bucket
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(file.file.read(), content_type=file.content_type)

    return file.filename


async def delete_blob(file_name: str):
    """Deletes a blob from the bucket."""
    destination_blob_name = f"photo/{file_name}"

    storage_client = storage.Client.from_service_account_json(credentials_file)

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    generation_match_precondition = None

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to delete is aborted if the object's
    # generation number does not match your precondition.
    blob.reload()  # Fetch blob metadata to use in generation_match_precondition.
    generation_match_precondition = blob.generation

    blob.delete(if_generation_match=generation_match_precondition)