from firebase_access.data_structures import Album
from ..endpoints import app
from ..exceptions import *
from ..request import Request
from ..request_type import RequestType
from ..response import Response
from ..status_code import StatusCode


@app.endpoint(endpoint_id=RequestType.CreateAlbum)
def create_album(request: Request) -> Response:
    try:
        app.db.create_album(Album(
            owner_id=request.user_id,
            name=request.args['album_data']['name'],
            date_range=request.args['album_data']['date_range']
        ))
    except UserNotExistsException:
        return Response(StatusCode.NotFound_404)
    except:
        return Response(StatusCode.InternalServerError_500, '')

    return Response(StatusCode.OK_200, '')


@app.endpoint(endpoint_id=RequestType.GetAlbumDetails)
def get_album_details(request: Request) -> Response:
    try:
        res = app.db.get_album_details(
            request.user_id,
            request.args['album_id'] if 'album_id' in request.args else None
        )
        album_list = [
            dict(
                owner_id=i.owner_id,
                name=i.name,
                date_range=i.date_range.__str__(),
                is_built=i.is_built,
                tags=i.tags,
                location=i.location,
                permitted_users=i.permitted_users
            ) for i in res
        ]
    except AlbumNotExistsException:
        return Response(StatusCode.NotFound_404)
    except:
        return Response(StatusCode.InternalServerError_500)

    return Response(StatusCode.OK_200, album_list)


@app.endpoint(endpoint_id=RequestType.GetAlbumContents)
def get_album_contents(request: Request) -> Response:
    try:
        res = app.db.get_album_contents(request.args['album_id'])
    except AlbumNotExistsException:
        return Response(StatusCode.NotFound_404)
    except:
        return Response(StatusCode.InternalServerError_500)

    return Response(StatusCode.OK_200, res)


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
    pass


@app.endpoint(endpoint_id=RequestType.RemoveFromAlbum)
def remove_from_album(request: Request) -> Response:
    pass


@app.endpoint(endpoint_id=RequestType.BuildAlbum)
def build_album(request: Request) -> Response:
    pass


@app.endpoint(endpoint_id=RequestType.DeleteAlbum)
def delete_album(request: Request) -> Response:
    pass
