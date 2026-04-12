import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment the code below to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    simple_socket = server_socket.accept()  # wait for client
    simple_socket[0].send(b"+PONG\r\n")


if __name__ == "__main__":
    main()
