import socket

MAX_PACKET_LENGTH = 16384


def receive_message(sender: socket.socket):
    # get length
    payload_length_bytes = sender.recv(4)
    payload_length = int.from_bytes(payload_length_bytes[0:4], "big")
    print(payload_length)

    # get payload
    bytes_left = payload_length
    payload = b''
    while bytes_left > 0:
        print(bytes_left, 'bytes left')
        if bytes_left < MAX_PACKET_LENGTH:
            decrease_amount = bytes_left
        else:
            decrease_amount = MAX_PACKET_LENGTH

        payload += sender.recv(decrease_amount)
        bytes_left -= decrease_amount

    return payload


def test(sock: socket.socket):
    print('xxx')
    client, address = sock.accept()
    print('accepted')
    data = client.recv(1024)
    print(data)

    exit()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5938))
    # server.bind(('0.0.0.0', 0))
    print(server.getsockname())
    server.listen(1)
    print("server is online!")

    # test(server)

    i = 0
    while True:
        print('waiting for clients')
        client, address = server.accept()
        print("accepted client")
        data = receive_message(client)
        print(len(data))

        if len(data) > 100:
            with open(f"{i}.png", 'wb') as f:
                f.write(data)
                i += 1
            print('saved image:', f"{i}.png")

    client.send(b'ok!')
    print("data sent to client")

    print("closing connection...")
    server.close()


if __name__ == '__main__':
    main()
