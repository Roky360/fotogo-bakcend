from datetime import datetime

from firebase_admin import storage


class StorageService:
    def __init__(self, app):
        self._bucket = storage.bucket(app=app)

    def upload_file(self, blob_path: str, file_path: str, content_type='image/jpg') -> None:
        self._bucket.blob(blob_path).upload_from_file(file_path, content_type=content_type)

    def get_file_url(self, blob_path: str):
        return self._bucket.blob(blob_path).generate_signed_url(
            datetime.now().replace(minute=datetime.now().minute + 0,  # TODO: fails if current minute is 59
                                   hour=datetime.now().hour - 2))  # one HOUR expiration time (in Israel time zone UTC+3)

    def download_file(self, blob_path: str, file_name: str):
        return self._bucket.blob(blob_path).download_to_filename(file_name)

    def get_file_bytes(self, blob_path: str) -> bytes:
        return self._bucket.blob(blob_path).download_as_bytes()

    def delete_file(self, blob_path: str):
        if self._bucket.blob(blob_path).exists():
            self._bucket.blob(blob_path).delete()

    def delete_directory(self, directory_path: str):
        """
        Deletes a directory in the bucket by looping over all the files in the directory and deleting each one of them.
        When the folder will be emptied, it will automatically delete itself.
        :param directory_path: The path to the directory.
        :return: None
        """
        for blob in self._bucket.list_blobs(prefix=directory_path):
            blob.delete()
