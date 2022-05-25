import base64
from datetime import datetime

from db_services.data_structures import AlbumDetails, DateTimeRange
from ..endpoints import app
from .images_endpoints import upload_images, delete_images
from ..exceptions import *
from ..request import Request
from ..request_type import RequestType
from ..response import Response
from ..status_code import StatusCode


@app.endpoint(endpoint_id=RequestType.CreateAlbum)
def create_album(request: Request) -> Response:
    try:
        album_data = request.args['album_data']
        # create album
        album_id = app.db.create_album(AlbumDetails(
            album_id='',
            owner_id=request.user_id,
            name=album_data['name'],
            date_range=DateTimeRange(start=datetime.strptime(album_data['date_range'][0], '%Y-%m-%d'),
                                     end=datetime.strptime(album_data['date_range'][1], '%Y-%m-%d')),
            last_modified=album_data['last_modified'],
            is_built=True,
            permitted_users=album_data['permitted_users']
        ))

        upload_images(request, album_id)

        return Response(StatusCode.Created_201, str(album_id))
    except UserNotExistsException:
        return Response(StatusCode.NotFound_404)
    except Exception as e:
        raise e
        return Response(StatusCode.InternalServerError_500)


@app.endpoint(endpoint_id=RequestType.SyncAlbumDetails)
def get_album_details(request: Request) -> Response:
    try:
        res = app.db.get_album_details(
            request.user_id,
            request.args['requested_albums'] if 'requested_albums' in request.args else None
        )
        album_list = [
            dict(
                owner_id=i.owner_id,
                album_id=i.id,
                name=i.name,
                date_range=i.date_range.format(),
                last_modified=str(i.last_modified),
                is_built=i.is_built,
                tags=i.tags,
                permitted_users=i.permitted_users,
                cover_image=base64.b64encode(app.storage.get_file_bytes(f"{i.owner_id}/{i.cover_image}")).decode(
                    'ascii') if i.owner_id != '' else ''
            ) for i in res
        ]
        return Response(StatusCode.OK_200, album_list)
    except Exception as e:
        raise e
        return Response(StatusCode.InternalServerError_500)


@app.endpoint(endpoint_id=RequestType.GetAlbumContents)
def get_album_contents(request: Request) -> Response:
    try:
        res = app.db.get_album_contents(request.args['album_id'])
        images = [
            dict(
                file_name=i.file_name,
                timestamp=str(i.timestamp).split(' ')[0],
                location=(i.location.longitude, i.location.latitude) if i.location is not None else None,
                tag=i.tag,
                containing_albums=i.containing_albums,
                data=base64.b64encode(app.storage.get_file_bytes(f"{i.owner_id}/{i.file_name}")).decode('ascii')
            ) for i in res
        ]
        return Response(StatusCode.OK_200, images)
    except AlbumNotExistsException:
        return Response(StatusCode.NotFound_404)
    except:
        return Response(StatusCode.InternalServerError_500)


@app.endpoint(endpoint_id=RequestType.UpdateAlbum)
def update_album(request: Request) -> Response:
    try:
        res = app.db.update_album(request.args['album_id'], request.args['album_data'])
    except:
        return Response(StatusCode.InternalServerError_500)

    if not res:
        return Response(StatusCode.NotFound_404)

    return Response(StatusCode.OK_200)


@app.endpoint(endpoint_id=RequestType.AddToAlbum)
def add_to_album(request: Request) -> Response:
    try:
        upload_images(request, request.args['album_data']['album_id'])
        return Response(StatusCode.OK_200)
    except:
        return Response(StatusCode.InternalServerError_500)


@app.endpoint(endpoint_id=RequestType.RemoveFromAlbum)
def remove_from_album(request: Request) -> Response:
    try:
        images_to_delete = []

        for img in request.payload:
            deleted = app.db.unlink_image_from_album(request.user_id, img, request.args['album_id'])
            if deleted:
                images_to_delete.append(img)

        delete_images(request.user_id, images_to_delete)

        return Response(StatusCode.OK_200)
    except:
        return Response(StatusCode.InternalServerError_500)


@app.endpoint(endpoint_id=RequestType.DeleteAlbum)
def delete_album(request: Request) -> Response:
    try:
        img_ids_to_unlink = app.db.delete_album(request.user_id, request.args['album_id'])
        delete_images(request.user_id, img_ids_to_unlink)

        return Response(StatusCode.OK_200)
    except AlbumNotExistsException as e:
        return Response(StatusCode.NotFound_404)
    except PermissionDeniedException as e:
        return Response(StatusCode.Forbidden_403)
    except Exception as e:
        raise e
        return Response(StatusCode.InternalServerError_500)
