import json
import socket
import time

from fotogo_networking.request import Request
from fotogo_networking.response import Response
from fotogo_networking.request_type import RequestType

"""
request structure:
{msg_len: 4 bytes}{method: byte}{payload}
000001230hello
metadata\ndata
"""

MAX_PAYLOAD_LENGTH = int.from_bytes(b'\xff\xff\xff\xff', "big")  # 4294967295 | 4,294,967,295
MAX_PACKET_READ_LENGTH = 16384


def send_response(response: Response, sender: socket.socket):
    """
    Accepts Response() object, parses it into bytes and sends it over the sender socket.
    :param response:
    :param sender:
    :return:
    """
    response_dict = dict(
        status_code=response.status_code,
        payload=response.payload
    )
    jsoned_response = json.dumps(response_dict)
    response_length = len(jsoned_response)
    if response_length > MAX_PAYLOAD_LENGTH:
        raise OverflowError("Response length too big!")

    # response_length_bytes = response_length.to_bytes(4, byteorder='big')
    # print(response_length)

    # data = response_length_bytes + jsoned_response.encode()
    data = jsoned_response.encode()

    sender.send(data)  # WITHOUT LENGTH BEFORE JSON


def receive_request(sender: socket.socket) -> (str, Request):
    """
    Receives bytes from the sender socket, parses it into Request() object and returns it.

    :param sender: The socket that sent the data.
    :return: Request()
    """
    # get request length
    payload_length_bytes = sender.recv(4)
    data_length = int.from_bytes(payload_length_bytes[0:4], "big")

    # get request json object
    bytes_left = data_length
    data = b''
    while bytes_left > 0:
        # print(f"{bytes_left} left")
        read_amount = max(0, min(bytes_left, MAX_PACKET_READ_LENGTH))  # clamp bytes_left between 0 and MAX_READ
        # print(f"read amount: {read_amount}")
        read_data = sender.recv(read_amount)
        data += read_data
        bytes_left -= len(read_data)

    data_json: dict = json.loads(data)

    return data_json['id_token'], Request(data_json['request_id'], data_json['args'],
                                          data_json['payload'])
