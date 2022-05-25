from collections.abc import Callable

from colorama import Fore

from db_services.db_service import DBService
from db_services.storage_service import StorageService
from fotogo_networking.logger import Logger
from fotogo_networking.response import Response
from fotogo_networking.socket_server import SocketServer
from fotogo_networking.request_type import RequestType
from fotogo_networking.request import Request


class Framework:
    def __init__(self, app):
        self.server = SocketServer(self)
        self.db = DBService(app)
        self.storage = StorageService(app)
        self.endpoint_map: dict[RequestType, Callable] = {}
        self.logger = Logger("fotogo")

    def start(self):
        self.logger.info("Starting application", Fore.CYAN)
        self.server.start()

    def stop(self):
        self.logger.info("Closing application", Fore.CYAN)
        self.server.stop()

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
