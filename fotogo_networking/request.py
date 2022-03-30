from fotogo_networking.request_type import RequestType


class Request:
    def __init__(self, request_type: RequestType, args: dict, payload: list, user_id: str = ''):
        self._type = RequestType._value2member_map_[request_type]
        self._uid = user_id
        self._args = args
        self._payload = payload

    @property
    def type(self):
        """
        Get the type of the Request object.

        :return: RequestType
        """
        return self._type

    @property
    def user_id(self):
        return self._uid

    @user_id.setter
    def user_id(self, value):
        self._uid = value

    @property
    def args(self):
        return self._args

    @property
    def payload(self):
        return self._payload

    def __repr__(self):
        return f"Request(type: {self._type}, user_id: {self._uid}, args: {self._args}, payload: {self._payload})"
