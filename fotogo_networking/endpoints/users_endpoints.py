from ..endpoints import app
from ..exceptions import *
from ..request import Request
from ..request_type import RequestType
from ..response import Response
from ..status_code import StatusCode


@app.endpoint(endpoint_id=RequestType.UserAuth)
def user_auth(id_token: str, request: Request) -> Request | Response:
    """
    Authenticates a user by validating its id_token.

    :param id_token: Id token to validate.
    :param request: Request object.
    :return: Response, if the auth failed; Request object if succeeded.
    """
    try:
        request.user_id = app.db.authenticate_user(id_token)
        return request
    except UserNotAuthenticatedException as e:
        return Response(StatusCode.Unauthorized_401, str(e))


@app.endpoint(endpoint_id=RequestType.CheckUserExists)
def check_user_exists(request: Request) -> Response:
    """
    Checks if a user exists in the database. Returns -1 if not.
    If exists, checks for their privilege level and returns it.

    * -1: Unregistered account
    * 0: Admin
    * 1: User

    :param request: Request object.
    :return: Privilege level of the user, if it exists; else -1.
    """
    try:
        if app.db.user_exists(request.user_id):
            return Response(StatusCode.OK_200, app.db.get_privilege_level(request.user_id))
        return Response(StatusCode.OK_200, -1)
    except:
        return Response(StatusCode.InternalServerError_500)


@app.endpoint(endpoint_id=RequestType.CreateAccount)
def create_account(request: Request) -> Response:
    """
    Handles CreateAccount request.

    :param request: Request object.
    :return: Response
    """
    try:
        app.db.add_user(request.user_id)
    except:
        return Response(StatusCode.InternalServerError_500)

    return Response(StatusCode.OK_200)


@app.endpoint(endpoint_id=RequestType.DeleteAccount)
def delete_account(request: Request) -> Response:
    """
    Handles DeleteAccount request.

    :param request: Request object.
    :return: Response
    """
    try:
        app.db.delete_user_data(request.user_id)
        app.storage.delete_directory(request.user_id)

        return Response(StatusCode.OK_200)
    except:
        return Response(StatusCode.InternalServerError_500)
