import socket
import threading
import ssl

from fotogo_networking.logger import Fore
from fotogo_networking.data_transportation import *


class SocketServer:
    """A secure, multi-threaded socket server."""

    def __init__(self, framework):
        self._address = ('0.0.0.0', 80)
        self._socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self._socket: SSLSocket = ssl.wrap_socket(self._socket,
        #                                           certfile=r'fullchain.pem',
        #                                           keyfile=r'privkey.pem',
        #                                           # certfile=r'C:\Certbot\live\vm128.hisham.ru\fullchain.pem',
        #                                           # keyfile=r'C:\Certbot\live\vm128.hisham.ru\privkey.pem',
        #                                           server_side=True)
        self._client_accepting_thread = threading.Thread(target=self.__client_acceptor)
        self._active = False
        self._framework = framework

    @property
    def active(self) -> bool:
        return self._active

    def start(self, backlog: int = 1):
        """
        Starts the server.

        Starting the client_accepting_thread that accepting clients while the server is active.

        :param backlog: How many backlogged clients are allowed (how many clients can wait in queue until they are
        accepted). Default to 1.
        """
        self._socket.bind(self._address)
        self._socket.listen(backlog)
        self._active = True
        self._client_accepting_thread.start()
        self._framework.logger.info(f"Server is online. Listening on port {self._address[1]}", Fore.CYAN)

    def __client_acceptor(self):
        """Accepting clients and passing them to connection_handler, while active."""
        while self._active:
            try:
                client, address = self._socket.accept()
                self._framework.logger.info("Client accepted")
                threading.Thread(target=self.__connection_handler, args=[client]).start()
            except ssl.SSLEOFError as e:
                self._framework.logger.error(str(e))
                continue
            except ssl.SSLError as e:
                self._framework.logger.error(str(e))
                continue
            except ConnectionError as e:
                self._framework.logger.error(str(e))
                continue
            except Exception as e:
                self._framework.logger.error(str(e))
                continue

    def __connection_handler(self, client: SSLSocket):
        """
        Handles a client that connected to the server.

        Passes the client's request to Framework, getting back the response and sends it back to the client.

        :param client: Client's socket.
        """
        try:
            id_token, request = receive_request(client)
            if not id_token:
                send_response(request, client)
                self._framework.logger.info(request)
                client.shutdown(socket.SHUT_WR)
                return
            res: Response = self._framework.execute(id_token, request)

            if not send_response(res, client):
                self._framework.logger.error(
                    f"Connection closed unexpectedly with client: {client.getsockname()}")
            else:
                self._framework.logger.info(res)

            client.shutdown(socket.SHUT_WR)
        except Exception as e:
            self._framework.logger.error(str(e))
            client.shutdown(socket.SHUT_WR)
            return

    def stop(self):
        """
        Stops the server.

        Sets active to False, closes the client_accepting_thread and shuts down the server's socket.
        """
        self._active = False
        self._client_accepting_thread.join()
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('127.0.0.1', self._address[1]))
        self._socket.shutdown(socket.SHUT_WR)
        self._framework.logger.info("Server has been shut down", Fore.CYAN)
