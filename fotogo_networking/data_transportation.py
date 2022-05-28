import json
from ssl import SSLSocket

from fotogo_networking.request import Request
from fotogo_networking.response import Response
from fotogo_networking.status_code import StatusCode

MAX_PAYLOAD_LENGTH = int.from_bytes(b'\xff\xff\xff\xff', "big")  # 4294967295 | 4,294,967,295 bytes
MAX_PACKET_READ_LENGTH = 16384


def send_response(response: Response, sender: SSLSocket) -> None:
    """
    Accepts Response() object, parses it into bytes and sends it over the sender socket.

    :param response: Response object to send back to the client.
    :param sender: Sender socket (client socket).
    :return: None
    """
    response_dict = dict(
        status_code=response.status_code,
        payload=response.payload
    )
    jsoned_response = json.dumps(response_dict)

    sender.send(jsoned_response.encode())


def receive_request(sender: SSLSocket) -> tuple[str, Request] | tuple[bool, Response]:
    """
    Receives bytes from the sender socket, parses it into Request() object and returns it.

    :param sender: The socket that sent the data.
    :return: id_token, Request() (False, Response() in case of an error)
    """
    try:
        # read request length
        payload_length_bytes = sender.recv(4)
        data_length = int.from_bytes(payload_length_bytes[0:4], "big")

        # read request json object
        bytes_left = data_length
        data = b''
        while bytes_left > 0:
            read_amount = max(0, min(bytes_left, MAX_PACKET_READ_LENGTH))  # clamp bytes_left between 0 and MAX_READ
            read_data = sender.recv(read_amount)
            data += read_data
            bytes_left -= len(read_data)

        data_json: dict = json.loads(data)

        return data_json['id_token'], Request(data_json['request_id'], data_json['args'], data_json['payload'])
    except:
        return False, Response(StatusCode.BadRequest_400)
