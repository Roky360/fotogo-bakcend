import threading
import ssl

from fotogo_networking.logger import Fore
from fotogo_networking.data_transportation import *


class SocketServer:
    def __init__(self, framework):
        self._address = ('0.0.0.0', 20200)
        self._socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket: SSLSocket = ssl.wrap_socket(self._socket,
                                                  certfile=r'C:\Certbot\live\vm128.hisham.ru\fullchain.pem',
                                                  keyfile=r'C:\Certbot\live\vm128.hisham.ru\privkey.pem',
                                                  server_side=True)
        self._client_accepting_thread = threading.Thread(target=self.client_acceptor)
        self._active = False
        self._framework = framework

    def start(self, backlog: int = 1):
        self._active = True
        self._socket.bind(self._address)
        self._socket.listen(backlog)
        self._client_accepting_thread.start()
        self._framework.logger.info(f"Server is online. Listening on port {self._address[1]}", Fore.CYAN)

    def client_acceptor(self):
        while self._active:
            client, address = self._socket.accept()
            self._framework.logger.info("Client accepted")
            threading.Thread(target=self.connection_handler, args=[client]).start()

    def connection_handler(self, client: SSLSocket):
        id_token, request = receive_request(client)
        if not id_token:
            send_response(request, client)
            return
        res: Response = self._framework.execute(id_token, request)

        send_response(res, client)
        self._framework.logger.info(res)

        client.shutdown(socket.SHUT_WR)

    def stop(self):
        self._active = False
        self._client_accepting_thread.join()
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('127.0.0.1', self._address[1]))
        self._socket.shutdown(socket.SHUT_WR)
        self._framework.logger.info("Server has been shut down", Fore.CYAN)

    def active(self) -> bool:
        return self._active
