import asyncio
import socket  # noqa: F401


class RESP_Parser:
    def __init__(self, reader: asyncio.StreamReader):
        self.reader = reader

    async def parse(self):
        try:
            # Read until the standard RESP delimiter \r\n is found
            line = await self.reader.readuntil(b"\r\n")
        except asyncio.IncompleteReadError:
            return None

        if not line:
            return None

        prefix = chr(line[0])
        # Remove the single character prefix and the trailing \r\n, then decode
        msg_body = line[1:-2].decode("utf-8")

        if prefix == "*":
            return await self.parse_array(msg_body)
        if prefix == "+":
            return await self.parse_simple_string(msg_body)
        if prefix == "$":
            return await self.parse_bulk_string(msg_body)

    async def parse_simple_string(self, msg_body: str):
        # The line is already read until \r\n, so msg_body is the string.
        return msg_body

    async def parse_bulk_string(self, msg_body: str):
        length = int(msg_body)
        if length == -1:
            return None

        # Read the exact length + 2 bytes for the trailing \r\n
        data = await self.reader.readexactly(length + 2)
        # Strip the trailing \r\n and decode
        return data[:-2].decode("utf-8")

    async def parse_array(self, msg_body: str):
        num_elements = int(msg_body)
        if num_elements == -1:
            return None

        elements = []
        for _ in range(num_elements):
            elements.append(await self.parse())

        return elements


# *2\r\n$4\r\nECHO\r\n$3\r\nhey\r\n
# *3\r\n$4\r\nECHO\r\n$3\r\nhey\r\n$5\r\nWorld\r\n
# async def parse_RESP_Array(msg: bytes):
#     print(msg.decode("utf-8"))


async def main(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    parser = RESP_Parser(reader)
    while True:
        parsed_data = await parser.parse()
        if not parsed_data:
            break

        print("Parsed:", parsed_data)

        # A basic setup to respond to commands! Feel free to modify this as needed.
        if isinstance(parsed_data, list) and len(parsed_data) > 0:
            command = parsed_data[0].upper()
            if command == "PING":
                writer.write(b"+PONG\r\n")
                await writer.drain()
            elif command == "ECHO" and len(parsed_data) > 1:
                echo_text = parsed_data[1]
                writer.write(f"${len(echo_text)}\r\n{echo_text}\r\n".encode())
                await writer.drain()
            else:
                writer.write(b"+OK\r\n")
                await writer.drain()
        else:
            writer.write(parsed_data)


async def run_server():
    server = await asyncio.start_server(main, "localhost", 6378)
    await server.serve_forever()


if __name__ == "__main__":
    main_loop = asyncio.new_event_loop()
    main_loop.run_until_complete(run_server())
