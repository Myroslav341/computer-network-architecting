import os
import socket
from os import listdir

from lib import Response, Command
from threads.send_thread import SendFileThread


def process_command(command: Command) -> Response:
    global CURRENT_DIR

    if command.name == "GET_DIR":
        return Response(code=200, payload={"dirs": listdir(f'{CURRENT_DIR}')})

    if command.name == "CHANGE_DIR":
        new_folder = command.options[0]

        if new_folder == "..":
            if "/" not in CURRENT_DIR:
                return Response(code=450, payload={"message": "given path is not a folder or doesn't exist."})
            new_path = "".join(CURRENT_DIR.split("/")[:-1])
        else:
            new_path = f"{CURRENT_DIR}/{new_folder}"

        if not os.path.isdir(new_path):
            return Response(code=450, payload={"message": "given path is not a folder or doesn't exist."})

        CURRENT_DIR = new_path

        return Response(code=200, payload={"dirs": listdir(f'{CURRENT_DIR}')})

    if command.name == "DOWNLOAD" or command.name == "DOWNLOAD_PARTIAL":
        file_name, target_port, last_loaded_part = command.options[0], command.options[1], command.options[2]

        file_path = f"{CURRENT_DIR}/{file_name}"

        if not os.path.isfile(file_path):
            return Response(code=450, payload={"message": "given path is not a file."})

        SendFileThread(
            target_port=target_port,
            file_path=file_path,
            partial=command.name == "DOWNLOAD_PARTIAL",
            last_loaded_part=last_loaded_part,
        ).start()

        return Response(code=200, payload={"status": "started"})

    return Response(code=400, payload={"message": "no such a command."})


CURRENT_DIR = "test_dir"
SERVER_ADDRESS = ('localhost', 8686)
connection = None


def run():
    global connection
    # Настраиваем сокет
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(SERVER_ADDRESS)
    server_socket.listen(1)
    print('server is running, please, press ctrl+c to stop')

    connection, address = server_socket.accept()
    print(f"new connection from {address}")

    # Слушаем запросы
    while True:
        command_raw = connection.recv(1024)
        command_raw = command_raw.decode("utf-8")

        command_object = Command.from_json_str(command_raw)

        print(f"new {command_object.name} command")

        if command_object.name == "exit":
            connection.send(bytes('closing connection!', encoding='UTF-8'))
            connection.close()
            break

        response = process_command(command_object)
        connection.send(bytes(response.to_json_str(), encoding='UTF-8'))


if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        if connection:
            connection.close()
