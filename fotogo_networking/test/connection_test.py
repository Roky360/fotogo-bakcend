import socket
from fotogo_networking.data_transportation import send_response, receive_request
from fotogo_networking.request import Request
from fotogo_networking.request_type import RequestType


def main():
    # soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('connecting')
    # soc.connect(("157.90.143.126", 53214))
    s = socket.create_connection(("192.168.1.162", 20200))

    req = Request(0, 'usr-id-das9y32h', {
        'album_id': '92149h231rj'
    }, ['img1'])

    s.close()


if __name__ == '__main__':
    main()
