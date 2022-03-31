import threading

from fotogo_networking.log_messages import *
from fotogo_networking.data_transportation import *
# from fotogo_networking.framework import Framework


class Server:
    def __init__(self, framework):
        self._address = ('localhost', 20200)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client_accepting_thread = threading.Thread(target=self.client_acceptor)
        self._active = False
        self._framework = framework

    @prompt_log(Caller.Server, "Server is online")
    def start(self, backlog: int = 1):
        self._active = True
        self._socket.bind(self._address)
        self._socket.listen(backlog)
        self._client_accepting_thread.start()

    def client_acceptor(self):
        while self._active:
            client, address = self._socket.accept()
            print('client accepted')
            threading.Thread(target=self.connection_handler, args=[client]).start()

    def connection_handler(self, client: socket.socket):
        id_token, request = receive_request(client)
        res = self._framework.execute(id_token, request)
        print(res)
        send_response(res, client)

        client.shutdown(socket.SHUT_WR)
        exit()

    @prompt_log(Caller.Server, "Shutting down...")
    def stop(self):
        self._active = False
        self._client_accepting_thread.join()
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('127.0.0.1', 80))
        self._socket.shutdown(socket.SHUT_WR)

    def active(self) -> bool:
        return self._active
