"""Object storage abstraction with MinIO (S3-compatible) and local fallback."""

from pathlib import Path
from typing import Optional
from uuid import uuid4

from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class StorageService:
    def __init__(self) -> None:
        self._client = None
        self._use_local = True
        self.bucket = getattr(settings, "minio_bucket", "healthcare")
        self.local_root = Path(settings.upload_dir)
        self.local_root.mkdir(parents=True, exist_ok=True)
        self._connect()

    def _connect(self) -> None:
        endpoint = getattr(settings, "minio_endpoint", "")
        access = getattr(settings, "minio_access_key", "")
        secret = getattr(settings, "minio_secret_key", "")
        if not endpoint or not access:
            logger.info("storage_using_local_fs", path=str(self.local_root))
            return
        try:
            from minio import Minio

            secure = getattr(settings, "minio_secure", False)
            self._client = Minio(endpoint, access_key=access, secret_key=secret, secure=secure)
            if not self._client.bucket_exists(self.bucket):
                self._client.make_bucket(self.bucket)
            self._use_local = False
            logger.info("minio_connected", endpoint=endpoint, bucket=self.bucket)
        except Exception as exc:  # noqa: BLE001
            logger.warning("minio_fallback_local", error=str(exc))
            self._use_local = True
            self._client = None

    def save_bytes(self, data: bytes, filename: str, content_type: str = "application/octet-stream") -> str:
        object_name = f"{uuid4().hex}_{Path(filename).name}"
        if self._use_local or self._client is None:
            path = self.local_root / object_name
            path.write_bytes(data)
            return str(path)

        from io import BytesIO

        self._client.put_object(
            self.bucket,
            object_name,
            BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
        return f"minio://{self.bucket}/{object_name}"

    def health(self) -> str:
        return "local" if self._use_local else "minio"


_storage: Optional[StorageService] = None


def get_storage() -> StorageService:
    global _storage
    if _storage is None:
        _storage = StorageService()
    return _storage
