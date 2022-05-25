from fotogo_networking.status_code import StatusCode


class Response:
    def __init__(self, status_code: StatusCode, payload=''):
        self._status_code = status_code
        self._payload = payload

    @property
    def status_code(self):
        return self._status_code

    @property
    def payload(self):
        return self._payload

    def __repr__(self):
        return f"Response(status_code: {self._status_code}, " \
               f"payload: {(str(len(self._payload)) + ' images') if type(self._payload) is list else self._payload})"
