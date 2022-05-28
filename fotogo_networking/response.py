from fotogo_networking.status_code import StatusCode


class Response:
    """Represents a response from the server to the client."""

    def __init__(self, status_code: StatusCode, payload=''):
        """
        Creates a Response() object.

        :param status_code: Response StatusCode
        :param payload: Response payload (optional)
        """
        self._status_code = status_code
        self._payload = payload

    @property
    def status_code(self) -> StatusCode:
        """
        The status code of the response.

        :return: StatusCode enum
        """
        return self._status_code

    @property
    def payload(self):
        """
        The payload of the response.

        :return: string
        """
        return self._payload

    def __repr__(self):
        return f"Response(status_code: {self._status_code}, " \
               f"payload: {(str(len(self._payload)) + ' images') if type(self._payload) is list else self._payload})"
