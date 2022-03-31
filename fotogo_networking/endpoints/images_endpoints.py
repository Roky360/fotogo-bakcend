from firebase_access.data_structures import Image
from ..endpoints import app
from ..request import Request
from ..request_type import RequestType
from ..response import Response
from ..status_code import StatusCode
from fotogo_networking.exceptions import *


@app.endpoint(endpoint_id=RequestType.UploadImage)
def upload_images(request: Request, album_id) -> Response:
    try:
        # create images documents
        for img in request.payload:
            app.db.upload_images(Image(
                owner_id=request.user_id,
                file_name=img['file_name'],
                timestamp=img['timestamp'],
                location=img['location'] if 'location' in img else None,
                tag=img['tag'] if 'tag' in img else None,
                containing_albums=[album_id],
            ))
        # upload files to storage
        for img in request.payload:
            with open(f"temp/{img['data']}.jpg", 'w+b') as f:
                f.write(img['data'])
                f.seek(0)
                app.storage.upload_file(f"{request.user_id}/{img['file_name']}", f)
    except UserNotExistsException:
        return Response(StatusCode.BadRequest_400)
    except:
        return Response(StatusCode.InternalServerError_500)

    return Response(StatusCode.OK_200)


@app.endpoint(endpoint_id=RequestType.DeleteImage)
def delete_image(request: Request) -> Response:
    # try:
    #     for img in request.args['images_id']:
    #         app.db.delete_image(request.user_id, img)
    # except (UserNotExistsException, AlbumNotExistsException, ImageNotExistsException):
    #     return Response(StatusCode.NotFound_404)
    # except:
    #     return Response(StatusCode.InternalServerError_500)

    return Response(StatusCode.OK_200)
