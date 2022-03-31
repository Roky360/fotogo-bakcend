from ..endpoints import app
from ..exceptions import *
from ..request import Request
from ..request_type import RequestType
from ..response import Response
from ..status_code import StatusCode


@app.endpoint(endpoint_id=RequestType.UserAuth)
def user_auth(id_token: str, request: Request) -> Request | Response:
    try:
        request.user_id = app.db.authenticate_user(id_token)
        return request
    except UserNotAuthenticatedException as e:
        return Response(StatusCode.Unauthorized_401, str(e))


@app.endpoint(endpoint_id=RequestType.CheckUserExists)
def check_user_exists(request: Request) -> Response:
    if app.db.user_exists(request.user_id):
        return Response(StatusCode.OK_200, True)
    else:
        return Response(StatusCode.NotFound_404, False)


@app.endpoint(endpoint_id=RequestType.CreateAccount)
def create_account(request: Request) -> Response:
    try:
        app.db.add_user(request.user_id)
    except:
        return Response(StatusCode.InternalServerError_500)

    return Response(StatusCode.OK_200)


@app.endpoint(endpoint_id=RequestType.DeleteAccount)
def delete_account(request: Request) -> Response:
    try:
        app.db.delete_user_data(request.user_id)
    except:
        return Response(StatusCode.InternalServerError_500)

    return Response(StatusCode.OK_200)
