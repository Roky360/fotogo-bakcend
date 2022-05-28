from ..endpoints import app
from ..request import Request
from ..request_type import RequestType
from ..response import Response
from ..status_code import StatusCode


@app.endpoint(endpoint_id=RequestType.GenerateStatistics)
def generate_statistics(request: Request) -> Response:
    """
    Generates statistics for an admin user.

    :param request: Request object.
    :return: Response
    """
    try:
        res = app.db.generate_statistics(request.user_id)
        return Response(StatusCode.OK_200,
                        dict(usr_count=res.users_count, albm_count=res.albums_count, img_count=res.images_count))
    except:
        return Response(StatusCode.InternalServerError_500)


@app.endpoint(endpoint_id=RequestType.GetUsers)
def get_users(request: Request) -> Response:
    """
    Get information about all the users in the system.

    :param request: Request object.
    :return: Response
    """
    try:
        res = app.db.get_users_data(request.user_id)
        return Response(StatusCode.OK_200,
                        [dict(name=i.display_name, email=i.email, photo_url=i.photo_url) for i in res])
    except:
        return Response(StatusCode.InternalServerError_500)
