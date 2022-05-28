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
    """
    Manages all the different parts of the server.

    Containing the SocketServer and the DB services, as well as a Logger.
    """

    def __init__(self, app):
        self.server = SocketServer(self)
        self.db = DBService(app)
        self.storage = StorageService(app)
        self.endpoint_map: dict[RequestType, Callable] = {}
        self.logger = Logger("fotogo")

    def start(self):
        """
        Starts the application and the server.
        """
        self.logger.info("Starting application", Fore.CYAN)
        self.server.start(backlog=2)

    def stop(self):
        """
        Stops the application.
        """
        self.logger.info("Closing application", Fore.CYAN)
        self.server.stop()

    def endpoint(self, endpoint_id: RequestType):
        """
        Decorates all the endpoints of the server.

        Adds an endpoint function to self.endpoint_map

        :param endpoint_id: RequestType indicates the endpoint ID.
        """

        def decorator(f):
            self.endpoint_map[endpoint_id] = f
            return f

        return decorator

    def execute(self, id_token: str, request: Request) -> Response:
        """
        Executes an endpoint request.

        First authenticates the client. Returns 404 Unauthorized of authentication failed. Then calls the endpoint
        that handles the request and returns its response.

        :param id_token: User's id token.
        :param request: Request object.
        :return: Response
        """
        request_validated = self.endpoint_map[RequestType.UserAuth](id_token, request)
        if type(request_validated) is Response:  # if token invalid
            return request_validated

        res = self.endpoint_map[request.type](request_validated)
        return res
