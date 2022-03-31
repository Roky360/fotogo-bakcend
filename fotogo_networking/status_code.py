from enum import IntEnum


class StatusCode(IntEnum):
    OK_200 = 200
    Created_201 = 201

    BadRequest_400 = 400
    Unauthorized_401 = 401
    Forbidden_403 = 403
    NotFound_404 = 404

    InternalServerError_500 = 500

    # TODO: support more status codes
