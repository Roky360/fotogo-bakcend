import firebase_admin
from firebase_admin import storage, credentials


class StorageService:
    def __init__(self, app):
        self._bucket = storage.bucket(app=app)

    def upload_file(self, path_in_db: str, file_obj: str, content_type='image/jpg') -> None:
        self._bucket.blob(path_in_db).upload_from_file(file_obj, content_type=content_type)

    def download_file(self, path_in_db: str, file_name: str):
        return self._bucket.blob(path_in_db).download_to_filename(file_name)

    def get_file_bytes(self, path_in_db: str) -> bytes:
        return self._bucket.blob(path_in_db).download_as_bytes()

    def delete_file(self, path_in_db: str):
        self._bucket.blob(path_in_db).delete()


# cred = credentials.Certificate("../serviceAccountKey.json")
# ap: firebase_admin.App = firebase_admin.initialize_app(cred, {
#     'storageBucket': 'fotogo-5e99f.appspot.com'
# })
#
# s = StorageService(ap)
#
# with open('img.png', 'rb') as f:
#     b = f.read()
#
# with open('t.png', 'w+b') as f:
#     f.write(b)
#     f.seek(0)
#     s.bucket.blob('test img').upload_from_file(f, content_type='image/png')
# # s.upload_file('user-id/test.txt', 'a.txt')
# # print(s.get_file_bytes('image'))
# # print(s.download_file('image', 'img.png'))
# # s.delete_file('test')
