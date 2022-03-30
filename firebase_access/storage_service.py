import firebase_admin
from firebase_admin import storage, credentials


class StorageService:
    def __init__(self, app):
        self.bucket = storage.bucket(app=app)

    def upload_file(self, path_in_db: str, file_path: str) -> None:
        self.bucket.blob(path_in_db).upload_from_filename(file_path)

    def download_file(self, path_in_db: str, file_name: str):
        return self.bucket.blob(path_in_db).download_to_filename(file_name)

    def get_file_bytes(self, path_in_db: str) -> bytes:
        return self.bucket.blob(path_in_db).download_as_bytes()

    def delete_file(self, path_in_db: str):
        self.bucket.blob(path_in_db).delete()


# cred = credentials.Certificate("../serviceAccountKey.json")
# ap: firebase_admin.App = firebase_admin.initialize_app(cred, {
#     'storageBucket': 'fotogo-5e99f.appspot.com'
# })
#
# s = StorageService(ap)
#
# # s.upload_file('test', '../a.txt')
# # print(s.get_file_bytes('image'))
# # print(s.download_file('image', 'img.png'))
# s.delete_file('test')
