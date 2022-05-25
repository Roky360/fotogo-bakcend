from datetime import datetime
import time

import firebase_admin
import google.cloud.firestore_v1.client
from firebase_admin import firestore, auth
from firebase_admin.auth import UserRecord

from db_services.data_structures import AlbumDetails, Image, DateTimeRange
from fotogo_networking.admin_data_structures import DBStatistics, UserData
from fotogo_networking.exceptions import *

TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


class DBService:
    _USERS_COLLECTION = 'users'
    _ALBUMS_COLLECTION = 'albums'
    _IMAGES_COLLECTION = 'images'

    def __init__(self, app):
        self._db: google.cloud.firestore_v1.client.Client = firestore.client(app)
        self._client = auth.Client(app)

    @staticmethod
    def delete_documents(coll_ref, batch_size=10):
        docs = coll_ref.limit(batch_size).stream()
        deleted = 0

        for doc in docs:
            doc.reference.delete()
            deleted = deleted + 1

        if deleted >= batch_size:
            return DBService.delete_documents(coll_ref, batch_size)

    def get_user_record(self, uid: str) -> UserRecord:
        return self._client.get_user(uid)

    """ USERS """

    def authenticate_user(self, id_token) -> str:
        """
        Authenticate user by its id token.
        This is a must security step before executing the client's request, to verify the client's identity.
        If the token is not valid, expired or has invalid signature, a 401 response is returned.
        :param id_token: The token to verify.
        :return: User id.
        """
        try:
            res = self._client.verify_id_token(id_token)
            return res['uid']
        except firebase_admin.auth.TokenSignError:
            raise UserNotAuthenticatedException("Invalid token signature.")
        except firebase_admin.auth.RevokedIdTokenError:
            raise UserNotAuthenticatedException("The provided ID token has been revoked.")
        except firebase_admin.auth.ExpiredIdTokenError:
            raise UserNotAuthenticatedException("Token expired")
        except firebase_admin.auth.InvalidIdTokenError:
            raise UserNotAuthenticatedException("The provided ID token is not a valid Firebase ID token.")

    def get_privilege_level(self, uid: str) -> int:
        """
        Checks for user's privilege level in the system.\n
        Privilege levels are:

        * 0: Admin. Has the highest privilege to view statistics, access sensitive data and perform dangerous actions like delete accounts.
        * 1: User. The end-user which can do "regular" operations and manage their account only.

        :param uid: user id.
        :return: int - privilege level.
        """
        return self._db.collection(DBService._USERS_COLLECTION).document(uid).get().to_dict()['privilege_level']

    def add_user(self, uid: str) -> None:
        """
        Used to create new user in the database.
        Called when creating new account.

        :param uid: user id
        :return: None
        """
        user = self.get_user_record(uid)
        self._db.collection(DBService._USERS_COLLECTION).document(uid).set(
            dict(email=user.email, name=user.display_name, priv_level=1))

    def user_exists(self, uid) -> bool:
        return self._db.collection(DBService._USERS_COLLECTION).document(uid).get().exists

    def delete_user_data(self, uid):
        # delete images' documents
        DBService.delete_documents(self._db.collection(DBService._IMAGES_COLLECTION).where('owner_id', '==', uid))

        # delete albums' documents
        DBService.delete_documents(self._db.collection(DBService._ALBUMS_COLLECTION).where('owner_id', '==', uid))

        # delete user document
        self._db.collection(DBService._USERS_COLLECTION).document(uid).delete()

    """ ALBUMS """

    def create_album(self, album: AlbumDetails):
        if not self.user_exists(album.owner_id):
            raise UserNotExistsException

        album_id = str(time.time())
        self._db.collection(DBService._ALBUMS_COLLECTION).add({
            'owner_id': album.owner_id,
            'name': album.name,
            'date_range': {
                'from_date': album.date_range.start,
                'to_date': album.date_range.end
            },
            'is_built': album.is_built,
            'tags': album.tags,
            'permitted_users': album.permitted_users,
            'last_modified': datetime.now()
        }, album_id)
        return album_id

    def get_album_details(self, uid, requested_albums: dict = None):
        """
        Fetches all album data and the first image of it as a cover image.

        :param uid: user id.
        :param requested_albums: ID of a specific album to fetch. If None, ALL the albums of the given user id are
        returned.
        :return:
        """
        # if requested_albums is not None and not self.album_exists(requested_albums):
        #     raise AlbumNotExistsException

        # get specific albums by the given IDs
        if requested_albums is None:
            requested_albums = {}
        album_details = []

        # get all albums owned by the given user ID
        docs = self._db.collection(DBService._ALBUMS_COLLECTION).where('owner_id', '==', uid).get()

        # look for deleted albums
        db_album_ids = [k.id for k in docs]
        for i in requested_albums.keys():
            if i not in db_album_ids:
                # AlbumDetails object with mock values. The only values that matters are album_id - to identify the
                # album to delete, and owner_id which will be checked in frontend and if it's an empty string, it will
                # be deleted from cache.
                album_details.append(AlbumDetails(
                    album_id=i,
                    owner_id='',
                    name='',
                    date_range=DateTimeRange(start=datetime.now(), end=datetime.now()),
                    last_modified=datetime.now()
                ))

        # look for outdated albums
        for doc in docs:
            # if exists in frontend and up-to-date, skip
            db_timestamp = doc.get('last_modified').replace(tzinfo=None)
            client_timestamp = requested_albums.get(doc.id)
            if doc.id in requested_albums.keys() and db_timestamp <= datetime.strptime(
                    client_timestamp[:len(client_timestamp) - 1], TIME_FORMAT):
                continue

            # else, append to returned album_details list
            album_details.append(AlbumDetails(
                owner_id=doc.get('owner_id'),
                album_id=doc.id,
                name=doc.get('name'),
                date_range=DateTimeRange(start=doc.get('date_range')['from_date'],
                                         end=doc.get('date_range')['to_date']),
                last_modified=doc.get('last_modified'),
                is_built=doc.get('is_built'),
                tags=doc.get('tags'),
                permitted_users=doc.get('permitted_users'),
                cover_image=
                list(self._db.collection(DBService._IMAGES_COLLECTION).where('containing_albums', 'array_contains',
                                                                             doc.id).get())[0].id
                # id of first image in album
            ))

        return album_details

    def get_album_contents(self, album_id):
        if not self.album_exists(album_id):
            raise AlbumNotExistsException

        images = []
        docs = self._db.collection(DBService._IMAGES_COLLECTION).where('containing_albums', 'array_contains',
                                                                       album_id).get()
        for doc in docs:
            images.append(Image(
                owner_id=doc.get('owner_id'),
                file_name=doc.get('file_name'),
                image_url=doc.get('url'),
                timestamp=doc.get('timestamp'),
                location=doc.get('location'),
                tag=doc.get('tag'),
                containing_albums=doc.get('containing_albums')
            ))

        return images

    def update_album(self, album_id: str, album: AlbumDetails):
        if not self.user_exists(album.owner_id):
            return False
            # raise Exception('Trying to update album to a user that does not exists!')

        self._db.collection(DBService._ALBUMS_COLLECTION).document(album_id).update(dict(
            name=album.name,
            date_range=album.date_range,
            last_modified=album.last_modified
        ))

    # TODO: necessary?
    def add_images_to_album(self, album_id: str, images_to_add: list[Image]):
        pass

    # TODO: necessary?
    def remove_images_from_album(self):
        pass

    def album_exists(self, album_id):
        return self._db.collection(DBService._ALBUMS_COLLECTION).document(album_id).get().exists

    def delete_album(self, uid, album_id) -> list[str]:
        """
        Deletes an album.\n
        Performs a check that the album exists and that the request comes from the owner of that album.
        Raises AlbumNotExistsException or PermissionDeniedException.\n
        Deletes the album's document, unlinks the album from all its images and return the ones that remain with no
        containing albums.

        :param uid: User id
        :param album_id: The id of the album to delete.
        :return: List of the IDs of the images that have no containing albums alter the deletion.
        """
        if not self.album_exists(album_id):
            raise AlbumNotExistsException
        album = list(self._db.collection(DBService._ALBUMS_COLLECTION).where('owner_id', '==', uid).get())
        if len(album) == 0:
            raise PermissionDeniedException

        # get album images
        album_images = self._db.collection(DBService._IMAGES_COLLECTION).where('containing_albums', 'array_contains',
                                                                               album_id).get()

        # unlink images from album and create a list of images that needs to be deleted
        img_ids_for_deletion = [i.id for i in album_images if self.unlink_image_from_album(uid, i.id, album_id)]

        # Remove the album document
        self._db.collection(DBService._ALBUMS_COLLECTION).document(album_id).delete()

        return img_ids_for_deletion

    """ IMAGES """

    def add_image(self, image: Image):
        if not self.user_exists(image.owner_id):
            raise UserNotExistsException

        self._db.collection(DBService._IMAGES_COLLECTION).document(image.file_name).set({
            'owner_id': image.owner_id,
            'file_name': image.file_name,
            'url': image.url,  # ^^ get after uploading image
            'timestamp': image.timestamp,
            'location': image.location,
            'tag': image.tag,
            'containing_albums': image.containing_albums
        })

    def link_image_to_album(self, uid, image_id, album_id):
        if not self.user_exists(uid):
            return UserNotExistsException
        if not self.album_exists(album_id):
            return AlbumNotExistsException
        if not self.image_exists(image_id):
            return ImageNotExistsException
        image = self._db.collection(DBService._IMAGES_COLLECTION).document(image_id)
        # if uid != image.get().to_dict().get('owner_id'):
        #     raise PermissionDeniedException('User does not have permission to this image: ' + image_id)

        containing_albums: list = image.get().to_dict()['containing_albums']
        containing_albums.append(album_id)
        image.update(dict(containing_albums=containing_albums))

    def unlink_image_from_album(self, uid, image_id, album_id, delete_if_unlinked: bool = True) -> bool:
        """
        Removes an album_id from the containing_albums array of an image.\n
        If delete_if_unlinked is true and containing_albums is empty after the removal, the image's document is deleted,
        and True is returned; else returns False.

        :param uid: User id.
        :param image_id: The image's id to delete.
        :param album_id: The album to unlink from.
        :param delete_if_unlinked: Whether to delete the image's document if containing_albums is empty after the
        removal.
        :return: Whether the image has been deleted or not.
        """
        if not self.user_exists(uid):
            raise UserNotExistsException
        if not self.album_exists(album_id):
            raise AlbumNotExistsException
        if not self.image_exists(image_id):
            raise ImageNotExistsException
        image = self._db.collection(DBService._IMAGES_COLLECTION).document(image_id)
        if uid != image.get().to_dict().get('owner_id'):
            raise PermissionDeniedException('User does not have permission to this image: ' + image_id)

        containing_albums: list = image.get().to_dict()['containing_albums']
        containing_albums.remove(album_id)
        image.update(dict(containing_albums=containing_albums))
        image.update({'containing_albums': containing_albums})
        if delete_if_unlinked and len(containing_albums) == 0:
            self.delete_image(uid, image_id)
            return True
        return False

    def update_image_tag(self, uid, image_id, tag: int):
        """
        Updates the "tag" field of an image.\n
        Checks if the user and the image exists, and if the user has permission to that iamge.

        :param uid:
        :param image_id:
        :param tag:
        :return:
        """
        if not self.user_exists(uid):
            raise Exception('User does not exists!')
        if not self.image_exists(image_id):
            raise Exception('Image does not exists!')

        self._db.collection(DBService._IMAGES_COLLECTION).document(image_id).update(dict(tag=tag))

    def image_exists(self, image_id) -> bool:
        """
        Checks if a document with the given id is exists in the "images" collection.

        :param image_id: The id of the image document.
        :return: If the document exists.
        """
        return self._db.collection(DBService._IMAGES_COLLECTION).document(image_id).get().exists

    def delete_image(self, uid: str, image_id: str):
        """
        Deletes a document represents an image from the database.
        Checks if the user has permission to edit the image (by checking if the user has acc)

        :param uid: User id which requests to delete the image.
        :param image_id: The desired image id to delete
        :return:
        """
        # TODO: check if the image is in an album which the user has access to (make a function to check for that permission)
        if not self.user_exists(uid):
            raise Exception('Trying to delete image to a user that does not exists!')
        if not self.image_exists(image_id):
            return
            raise Exception('Image does not exists!')

        self._db.collection(DBService._IMAGES_COLLECTION).document(image_id).delete()

    """ ADMIN """

    def generate_statistics(self, uid: str) -> DBStatistics:
        if self.get_privilege_level(uid) != 0:
            raise PermissionDeniedException("User does not have admin permission.")

        users_count = len(self._db.collection(DBService._USERS_COLLECTION).get())
        albums_count = len(self._db.collection(DBService._ALBUMS_COLLECTION).get())
        images_count = len(self._db.collection(DBService._IMAGES_COLLECTION).get())

        return DBStatistics(users_count, albums_count, images_count)

    def get_users_data(self, uid: str) -> list[UserData]:
        if self.get_privilege_level(uid) != 0:
            raise PermissionDeniedException("User does not have admin permission.")

        users_docs = self._db.collection(DBService._USERS_COLLECTION).get()
        user_records = [
            self.get_user_record(user.id)
            for user in users_docs]

        return [
            UserData(display_name=user.display_name, email=user.email, photo_url=user.photo_url)
            for user in user_records]
