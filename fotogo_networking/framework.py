from collections.abc import Callable

from firebase_access.db_service import DBService
from firebase_access.storage_service import StorageService
from fotogo_networking.response import Response
from fotogo_networking.server import Server
from fotogo_networking.request_type import RequestType
from fotogo_networking.request import Request


class Framework:
    def __init__(self, app):
        self.server = Server(self)
        self.db = DBService(app)
        self.storage = StorageService(app)
        self.endpoint_map: dict[RequestType, Callable] = {}

    def start(self):
        self.server.start()

    def endpoint(self, endpoint_id: RequestType):
        def decorator(f):
            self.endpoint_map[endpoint_id] = f
            return f

        return decorator

    def execute(self, id_token: str, request: Request):
        request_validated = self.endpoint_map[RequestType.UserAuth](id_token, request)
        if type(request_validated) is Response:  # if token invalid
            return request_validated

        res = self.endpoint_map[request.type](request_validated)
        return res
