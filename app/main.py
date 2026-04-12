import asyncio
import socket  # noqa: F401


async def main(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment the code below to pass the first stage
    #
    while True:
        msg = await reader.read(1024)
        print(msg)
        if msg and msg != b"\n":
            writer.write(b"+PONG\r\n")
            await writer.drain()
        else:
            break


async def run_server():
    server = await asyncio.start_server(main, "localhost", 6379)
    await server.serve_forever()


if __name__ == "__main__":
    main_loop = asyncio.new_event_loop()
    main_loop.run_until_complete(run_server())
