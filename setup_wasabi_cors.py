import os
import sys

# Configure Django to load settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pro_newmedia.settings")
import django
try:
    django.setup()
except Exception as e:
    print("Failed to setup django:", e)
    sys.exit(1)

from django.conf import settings
import boto3
from botocore.exceptions import ClientError

def configure_cors():
    access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
    secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
    bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
    endpoint = getattr(settings, 'AWS_S3_ENDPOINT_URL', None)
    region = getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')

    if not all([access_key, secret_key, bucket_name, endpoint]):
        print("Missing required AWS/Wasabi settings in .env")
        return

    print(f"Configuring CORS for bucket: {bucket_name}")
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=endpoint,
        region_name=region
    )

    cors_configuration = {
        'CORSRules': [{
            'AllowedHeaders': ['*'],
            'AllowedMethods': ['GET', 'HEAD'],
            'AllowedOrigins': ['*'],
            'ExposeHeaders': ['ETag', 'Content-Type', 'Accept-Ranges', 'Content-Length']
        }]
    }

    try:
        s3_client.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration=cors_configuration
        )
        print("CORS configuration applied successfully to Wasabi!")
    except ClientError as e:
        print(f"Error applying CORS: {e}")

if __name__ == "__main__":
    configure_cors()
