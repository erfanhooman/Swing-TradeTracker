import os
from typing import Optional

import botocore.exceptions
from aiobotocore.session import AioSession
from dotenv import load_dotenv

load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")


class MinioClient:
    """Handles interactions with MinIO to check, upload, and retrieve icons."""

    def __init__(self):
        self.session = AioSession()

    def _get_client(self):
        # Create a client context manager without awaiting

        return self.session.create_client(
            "s3",
            endpoint_url=MINIO_ENDPOINT,
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY,
            region_name="us-east-1"
        )

    async def icon_exists(self, coin: str) -> Optional[str]:
        """Check if icon already exists in MinIO, return its URL if found."""
        async with self._get_client() as client:
            try:
                await client.head_object(Bucket=MINIO_BUCKET, Key=f"{coin}.png")
                return f"/{MINIO_BUCKET}/{coin}.png"
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    return None
                raise

    async def upload_icon(self, coin: str, image_data: bytes) -> str:
        """Upload icon to MinIO and return its public URL."""
        async with self._get_client() as client:
            await client.put_object(Bucket=MINIO_BUCKET, Key=f"{coin}.png", Body=image_data, ContentType="image/png")
        return f"/{MINIO_BUCKET}/{coin}.png"