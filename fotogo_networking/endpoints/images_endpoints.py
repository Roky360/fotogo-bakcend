import base64
import os

from db_services.data_structures import Image
from ..endpoints import app
from ..request import Request


def upload_images(request: Request, album_id) -> None:
    """
    Uploads images to the database.

    Both creates a document in the Images collection and uploads the actual file to the storage, for each image.

    :param request: Request object.
    :param album_id: Album's id to link the images to.
    """
    for img in request.payload:
        curr_image_id = img['file_name']

        if app.db.image_exists(curr_image_id):
            app.db.link_image_to_album(request.user_id, curr_image_id, album_id)
            continue

        # create image document
        app.db.add_image(Image(
            owner_id=request.user_id,
            file_name=curr_image_id,
            timestamp=img['timestamp'],
            location=img['location'] if 'location' in img else None,
            tag=img['tag'] if 'tag' in img else None,
            containing_albums=[album_id],
        ))
        # upload files to storage
        path = f"temp/{img['file_name']}"
        with open(path, 'w+b') as f:
            decoded_bytes = base64.b64decode(img['data'])
            f.write(decoded_bytes)
            f.seek(0)
            app.storage.upload_file(f"{request.user_id}/{img['file_name']}", f)
        os.remove(path)


def delete_images(uid: str, image_ids: list) -> None:
    """
    Deletes images from the database.

    Both deletes the document in the Images collection and the actual file to the storage, for each image.

    :param uid: User id.
    :param image_ids: list of image IDs to delete.
    :return: None
    """
    for img in image_ids:
        app.db.delete_image(uid, img)
        app.storage.delete_file(f"{uid}/{img}")


