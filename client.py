import socket

from lib import Response, Command, FileResponse
from threads.receive_thread import ReceiveFileThread


def response_processor(command: Command, response: Response):
    if response.code != 200:
        print(f"error code {response.code}, reason: {response.payload.get('message')}")

    if command.name == "GET_DIR":
        print("dirs list: ")
        for d in response.payload.get("dirs", []):
            print(f"- {d}")

    if command.name == "CHANGE_DIR":
        print("dirs list: ")
        for d in response.payload.get("dirs", []):
            print(f"- {d}")

    if command.name == "DOWNLOAD":
        print(f"status: {response.payload.get('status')}")

    if command.name == "DOWNLOAD_PARTIAL":
        print(f"partial download: {response.payload.get('status')}")


address_to_server = ('localhost', 8686)
address_to_download = ['localhost', 8687]
TARGET_DIR = "target_dir"
RECEIVED_BYTES = ""

if __name__ == '__main__':
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect(address_to_server)

    while (command_raw := input("-> ")) != "exit":
        command_raw = command_raw.strip()
        command_name = command_raw.split(" ")[0]
        options = command_raw.split(" ")[1:] if len(command_raw.split(" ")) > 1 else []

        command_object = Command(name=command_name, options=options)

        if command_object.name == "DOWNLOAD" or command_object.name == "DOWNLOAD_PARTIAL":
            thread = ReceiveFileThread(
                address_to_download=(address_to_download[0], address_to_download[1]),
                target_path=f"{TARGET_DIR}/{command_object.options[0]}",
                partial=command_object.name == "DOWNLOAD_PARTIAL"
            )
            loaded_parts = thread.get_state()
            thread.start()
            command_object.options.append(address_to_download[1])
            command_object.options.append(loaded_parts)
            address_to_download[1] += 1

        client.send(bytes(command_object.to_json_str(), encoding='UTF-8'))

        server_response = client.recv(1024)
        server_response = server_response.decode("utf-8")

        response_processor(command_object, Response.from_json_str(server_response))

    client.send(bytes(Command(name="exit").to_json_str(), encoding='UTF-8'))

    server_response = client.recv(1024)
    server_response = server_response.decode("utf-8")

    print(server_response)
