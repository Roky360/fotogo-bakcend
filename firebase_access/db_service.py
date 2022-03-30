import firebase_admin
import google.cloud.firestore_v1.client
from firebase_admin import firestore, auth

from firebase_access.data_structures import Album, Image
from fotogo_networking.exceptions import *


class DBService:
    def __init__(self, app):
        self._db: google.cloud.firestore_v1.client.Client = firestore.client(app)
        self._client = auth.Client(app)

    """ USERS """

    def authenticate_user(self, id_token):
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

    def add_user(self, uid: str):
        """
        Used to create new user in the database.
        Called when creating new account.
        :param uid: user id
        :return:
        """
        user = auth.get_user(uid)
        self._db.collection('users').document(uid).set({
            'email': user.email,
            'name': user.display_name,
            # TODO: add session-id
        })

    def user_exists(self, uid):
        return self._db.collection('users').document(uid).get().exists

    def delete_user_data(self, uid):
        pass

    """ ALBUMS """

    def create_album(self, album: Album):
        if not self.user_exists(album.owner_id):
            raise UserNotExistsException
        self._db.collection('albums').add({
            'owner_id': album.owner_id,
            'name': album.name,
            'date_range': {
                'from_date': album.date_range.start,
                'to_date': album.date_range.end
            },
            'is_built': False,
            'tags': album.tags,
            'location': album.location,
            'permitted_users': album.permitted_users,
        })

    def get_album_details(self, uid, album_id=None):
        """
        Fetches all album data and the first image of it as a cover image.

        :param uid: user id.
        :param album_id: ID of a specific album to fetch. If None, ALL the albums of the given user id are returned.
        :return:
        """
        if album_id is not None and not self.album_exists(album_id):
            raise AlbumNotExistsException

        # get specific album by the given ID
        if album_id is not None:
            doc = self._db.collection('albums').document(album_id).get()
            return [Album(
                owner_id=doc.get('owner_id'),
                name=doc.get('name'),
                date_range=doc.get('date_range'),
                is_built=doc.get('is_built'),
                tags=doc.get('tags'),
                location=doc.get('location'),
                permitted_users=doc.get('permitted_users')
            )]

        # get all albums owned by the given user ID
        docs = self._db.collection('albums').where('owner_id', '==', uid).get()
        print(docs)
        return [Album(
            owner_id=doc.get('owner_id'),
            name=doc.get('name'),
            date_range=doc.get('date_range'),
            is_built=doc.get('is_built'),
            tags=doc.get('tags'),
            location=doc.get('location'),
            permitted_users=doc.get('permitted_users')
        ) for doc in docs]

    def get_album_contents(self, album_id):
        if not self.album_exists(album_id):
            raise AlbumNotExistsException

        images = []
        docs = self._db.collection('images').where('containing_albums', 'array_contains', album_id).get()
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

    def update_album(self, album_id: str, album: Album):
        if not self.user_exists(album.owner_id):
            return False
            # raise Exception('Trying to update album to a user that does not exists!')

        self._db.collection('albums').document(album_id).update(dict(
            name=album.name,
            date_range=album.date_range,
            location=album.location
        ))

    # necessary?
    def add_images_to_album(self):
        pass

    def remove_images_from_album(self):
        pass

    def album_exists(self, album_id):
        return self._db.collection('albums').document(album_id).get().exists

    def delete_album(self):
        pass

    """ IMAGES """

    def upload_image(self, image: Image):
        if not self.user_exists(image.owner_id):
            raise UserNotExistsException

        # TODO: upload the actual file
        self._db.collection('images').document(image.file_name).set({
            'owner_id': image.owner_id,
            'file_name': image.file_name,
            'url': image.url,  # ^^ get after uploading image
            'timestamp': image.timestamp,
            'location': image.location,
            'tag': image.tag,
            'containing_albums': image.containing_albums
        })

    def link_image_to_album(self, uid, image_id, album_id, link=True):
        if not self.user_exists(uid):
            return UserNotExistsException
        if not self.album_exists(album_id):
            return AlbumNotExistsException
        if not self.image_exists(image_id):
            return ImageNotExistsException
        image = self._db.collection('images').document(image_id)
        if uid != image.get('owner_id'):
            raise PermissionDeniedException('User does not have permission to this image: ' + image_id)

        containing_albums = image.get().to_dict()['containing_albums']
        if link:
            containing_albums.append(album_id)
        else:
            containing_albums.remove(album_id)
        image.update({'containing_album': containing_albums})

    def unlink_image_to_album(self, uid, image_id, album_id):
        self.link_image_to_album(uid, image_id, album_id, link=False)

    def update_image_tag(self, uid, image_id, tag: int):
        if not self.user_exists(uid):
            raise Exception('User does not exists!')
        if not self.image_exists(image_id):
            raise Exception('Image does not exists!')

        self._db.collection('images').document(image_id).update(dict(tag=tag))

    def image_exists(self, image_id):
        return self._db.collection('images').document(image_id).get().exists

    def delete_image(self, uid: str, image_id: str):
        if not self.user_exists(uid):
            raise Exception('Trying to delete image to a user that does not exists!')
        if not self.image_exists(image_id):
            raise Exception('Image does not exists!')

        # TODO: upload the actual file
        self._db.collection('images').document(image_id).delete()
