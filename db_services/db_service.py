import random
from datetime import datetime
import time
from typing import Type

import firebase_admin
import google.cloud.firestore_v1.client
from firebase_admin import firestore, auth
from firebase_admin.auth import UserRecord

from db_services.data_structures import AlbumDetails, Image, DateTimeRange
from fotogo_networking.admin_data_structures import DBStatistics, UserData
from fotogo_networking.exceptions import *
from fotogo_networking.exceptions import UserNotExistsException, AlbumNotExistsException, ImageNotExistsException

TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


class DBService:
    """A service that manages operations with Firebase Cloud Firestore database."""
    _USERS_COLLECTION = 'users'
    _ALBUMS_COLLECTION = 'albums'
    _IMAGES_COLLECTION = 'images'

    def __init__(self, app):
        """
        Initializes DBService with a Firebase app.

        :param app: Firebase app.
        """
        self._db: google.cloud.firestore_v1.client.Client = firestore.client(app)
        self._client = auth.Client(app)

    @staticmethod
    def delete_documents(coll_ref, batch_size=10):
        """
        Deletes all the documents in coll_ref.

        Used to delete mass documents (like collections with hundreds of documents) in a memory-effective way.
        Deletes batch_size documents each iteration recursively, in order to not fill-up the memory.

        :param coll_ref: Reference to the collection to delete.
        :param batch_size: How many documents to delete in each iteration. Default to 10.
        :return:
        """
        docs = coll_ref.limit(batch_size).stream()
        deleted = 0

        for doc in docs:
            doc.reference.delete()
            deleted = deleted + 1

        if deleted >= batch_size:
            return DBService.delete_documents(coll_ref, batch_size)

    def get_user_record(self, uid: str) -> UserRecord:
        """
        Returns a UserRecord from user id.

        :param uid: User id.
        :return: UserRecord
        """
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
            dict(email=user.email, name=user.display_name, privilege_level=1))

    def user_exists(self, uid) -> bool:
        """
        Returns if aa uid (user id) exists in the Users collection.

        :param uid: User id
        :return: bool
        """
        return self._db.collection(DBService._USERS_COLLECTION).document(uid).get().exists

    def delete_user_data(self, uid) -> None:
        """
        Deletes all the data related to a user in the database.

        Deletes all images and albums owned by the user, as well as its document in the users collection.

        :param uid: User id to delete.
        """
        # delete images' documents
        DBService.delete_documents(self._db.collection(DBService._IMAGES_COLLECTION).where('owner_id', '==', uid))

        # delete albums' documents
        DBService.delete_documents(self._db.collection(DBService._ALBUMS_COLLECTION).where('owner_id', '==', uid))

        # delete user document
        self._db.collection(DBService._USERS_COLLECTION).document(uid).delete()

    """ ALBUMS """

    def update_last_modified(self, last_modified: datetime, album_id: str):
        self._db.collection(DBService._ALBUMS_COLLECTION).document(album_id).update(dict(last_modified=last_modified))

    def create_album(self, album: AlbumDetails) -> str:
        """
        Creates a new album in the database.

        The owner_id must exist in the Users collection.

        :param album: AlbumDetails object.
        :return: The album's id, as stored in the database.
        """
        if not self.user_exists(album.owner_id):
            raise UserNotExistsException

        album_id = str(time.time())
        while self.album_exists(album_id):
            album_id += str(random.randint(0, 10))
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

    def sync_album_details(self, uid, requested_albums: dict = None) -> list[AlbumDetails]:
        """
        Syncs client's albums with the albums stored in DB, for one user.

        For each outdated album, fetches all album data and the first image of it as a cover image. For deleted albums,
        returns AlbumDetails object with empty owner_id, as a sign that the album needs to be deleted in client side.

        :param uid: user id.
        :param requested_albums: A dictionary containing all the albums' IDs as keys and their last-modified field as
        value.
        :return:
        """
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
            album_images = list(
                self._db.collection(DBService._IMAGES_COLLECTION).where('containing_albums', 'array_contains',
                                                                        doc.id).get())
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
                cover_image=album_images[0].id if len(album_images) > 0 else None
                # id of first image in album
            ))

        return album_details

    def get_album_contents(self, album_id) -> list[Image]:
        """
        Returns a list of all the images on an album.

        :param album_id: Album id.
        :return: List of Image object, representing all the images on the album.
        """
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

    def update_album(self, album: AlbumDetails):
        """
        Updates album details, like its title.

        :param album: AlbumDetails object with updated data.
        :return: False if the user does not exist, else None.
        """
        if not self.user_exists(album.owner_id):
            return False
            # raise Exception('Trying to update album to a user that does not exists!')

        self._db.collection(DBService._ALBUMS_COLLECTION).document(album.id).update(dict(
            name=album.name,
            date_range=dict(from_date=album.date_range.start, to_date=album.date_range.end),
            last_modified=album.last_modified
        ))

        return True

    def album_exists(self, album_id):
        """
        Returns if an album_id exists in the Albums collection.

        :param album_id: Album id
        :return: bool
        """
        return self._db.collection(DBService._ALBUMS_COLLECTION).document(album_id).get().exists

    def delete_album(self, uid, album_id) -> list[str]:
        """
        Deletes an album.

        Performs a check that the album exists and that the request comes from the owner of that album.
        Raises AlbumNotExistsException or PermissionDeniedException.

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

    def add_image(self, image: Image) -> None:
        """
        Adds an image to the database.

        Creates a document in the Images collection.

        :param image: Image object to add
        """
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

    def link_image_to_album(self, uid, image_id, album_id) -> Type[UserNotExistsException | AlbumNotExistsException |
                                                                   ImageNotExistsException]:
        """
        Links an image to an album.

        Adds the album's id to the containing_albums field of the image.

        The user, album and the image must exist in the database.

        :param uid: The id of the user making the request.
        :param image_id:
        :param album_id:
        :return: UserNotExistsException if the user does not exist, AlbumNotExistsException if the album does not exist,
        ImageNotExistsException if the image does not exist. If everything is OK, returns None.
        """
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

        :param uid: The id of the user making the request.
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

    def update_image_tag(self, uid, image_id, tag: int) -> None:
        """
        Updates the "tag" field of an image.\n
        Checks if the user and the image exists, and if the user has permission to that image.

        :param uid: The id of the user making the request.
        :param image_id: The id of the image.
        :param tag: New tag id.
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

    def delete_image(self, uid: str, image_id: str) -> None:
        """
        Deletes a document represents an image from the database.
        Checks if the user has permission to edit the image (by checking if the user has acc)

        :param uid: User id which requests to delete the image.
        :param image_id: The desired image id to delete
        :return:
        """
        # TODO: check if the image is in an album which the user has access to (make a function to check for that
        #  permission)
        if not self.user_exists(uid):
            raise Exception('Trying to delete image to a user that does not exists!')
        if not self.image_exists(image_id):
            return

        self._db.collection(DBService._IMAGES_COLLECTION).document(image_id).delete()

    """ ADMIN """

    def generate_statistics(self, uid: str) -> DBStatistics:
        """
        Generates statistics of the system, and packs them in DBStatistics object.

        The uid must be at admin privilege level.

        :param uid: The id of the user making the request.
        :return: DBStatistics object.
        """
        if self.get_privilege_level(uid) != 0:
            raise PermissionDeniedException("User does not have admin permission.")

        users_count = len(self._db.collection(DBService._USERS_COLLECTION).get())
        # count the non-admin users
        # users_count = 0
        # for user in self._db.collection(DBService._USERS_COLLECTION).get():
        #     if user.get('privilege_level') != 0:
        #         users_count += 1
        albums_count = len(self._db.collection(DBService._ALBUMS_COLLECTION).get())
        images_count = len(self._db.collection(DBService._IMAGES_COLLECTION).get())

        return DBStatistics(users_count, albums_count, images_count)

    def get_users_data(self, uid: str) -> list[UserData]:
        """
        Returns the user data of all the non-admin users registered.

        :raises PermissionDeniedException: If uid does not have admin permission.

        :param uid: User id.
        :return: list of UserData objects
        """
        if self.get_privilege_level(uid) != 0:
            raise PermissionDeniedException("User does not have admin permission.")

        users_docs = self._db.collection(DBService._USERS_COLLECTION).get()
        user_records = [
            self.get_user_record(user.id)
            for user in users_docs]

        return [
            UserData(uid=user.uid, display_name=user.display_name, email=user.email, photo_url=user.photo_url,
                     privilege_level=self._db.collection(DBService._USERS_COLLECTION).document(user.uid).get().get(
                         'privilege_level'))
            for user in user_records
        ]
