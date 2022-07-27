from datetime import datetime, timedelta

from firebase_admin import storage


class StorageService:
    """A service that manages Firebase Storage."""

    def __init__(self, app):
        """
        Initializes the StorageService with a storage bucket.

        :param app: A Firebase application.
        """
        self._bucket = storage.bucket(app=app)

    def upload_file(self, blob_path: str, file_path: str, content_type='image/jpg') -> None:
        """
        Upload a file to the storage.

        :param blob_path: The path in the storage in which to store the file.
        :param file_path: Path to the file to upload.
        :param content_type: The type of the file. Default to "image/jpg" - JPG image format.
        """
        self._bucket.blob(blob_path).upload_from_file(file_path, content_type=content_type)

    def get_file_url(self, blob_path: str) -> str:
        """
        Generates a signed URL to a blob.

        :param blob_path: Path to the blob.
        :return: URL: str
        """
        return self._bucket.blob(blob_path).generate_signed_url(
            datetime.now() + timedelta(hours=1))  # one HOUR expiration time (in Israel time zone UTC+3)

    def download_file(self, blob_path: str, file_name: str):
        """
        Download the contents of this blob into a named file.

        :param blob_path: Path of the blob to download
        :param file_name: The file to download to.
        :return: File I/O reference.
        """
        return self._bucket.blob(blob_path).download_to_filename(file_name)

    def get_file_bytes(self, blob_path: str) -> bytes:
        """
        Get the contents of a blob, in bytes.

        :param blob_path: Path of the blob to get.
        :return: File contents as bytes.
        """
        return self._bucket.blob(blob_path).download_as_bytes()

    def delete_file(self, blob_path: str) -> None:
        """
        Deletes a blob from the storage.

        :param blob_path: Path to the blob to delete.
        """
        if self._bucket.blob(blob_path).exists():
            self._bucket.blob(blob_path).delete()

    def delete_directory(self, directory_path: str) -> None:
        """
        Deletes a directory in the bucket by looping over all the files in the directory and deleting each one of them.
        When the folder will be emptied, it will automatically delete itself.

        :param directory_path: The path to the directory.
        :return: None
        """
        for blob in self._bucket.list_blobs(prefix=directory_path):
            blob.delete()
