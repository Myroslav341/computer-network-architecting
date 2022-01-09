import socket
import threading
from typing import Tuple, List, Dict

from lib import FileResponse
from threads.base_thread import BaseThread


_partial_downloads: Dict[str, Tuple[str, int]] = {}
_partial_downloads_lock = threading.Lock()


class ReceiveFileThread(BaseThread):
    def __init__(self, address_to_download: Tuple[str, int], target_path: str, partial: bool):
        super(ReceiveFileThread, self).__init__()
        self.address_to_download = address_to_download
        self.target_path = target_path
        self.received_bytes = ""
        self.is_partial = partial

        if target_path in _partial_downloads:
            self.received_bytes = _partial_downloads[target_path][0]

    def get_state(self) -> int:
        if self.target_path in _partial_downloads:
            return _partial_downloads[self.target_path][1]

        return -1

    def handler(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(self.address_to_download)
        server_socket.listen(1)

        connection, address = server_socket.accept()

        while True:
            file_response_raw = connection.recv(1024)
            file_response_raw = file_response_raw.decode("utf-8")

            response = FileResponse.from_json_str(file_response_raw)

            self.received_bytes += response.content

            if self.is_partial and response.part_index > response.total_parts // 2:
                break

            if not response.is_last_part:
                continue

            if self.target_path in _partial_downloads:
                _partial_downloads_lock.acquire()
                _partial_downloads.pop(self.target_path)
                _partial_downloads_lock.release()

            with open(self.target_path, "w") as f:
                f.write(self.received_bytes)

            break

        if not response.is_last_part:
            _partial_downloads_lock.acquire()
            _partial_downloads[self.target_path] = (self.received_bytes, response.part_index)
            _partial_downloads_lock.release()

        connection.close()
