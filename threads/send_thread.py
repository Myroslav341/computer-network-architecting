import socket
from time import sleep

from lib import FileResponse
from threads.base_thread import BaseThread


class SendFileThread(BaseThread):
    def __init__(self, target_port: int, file_path: str, partial: bool, last_loaded_part: int):
        super(SendFileThread, self).__init__()
        self.target_port = target_port
        self.file_path = file_path
        self.is_partial = partial
        self.last_loaded_part = last_loaded_part

    def handler(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', self.target_port))

        with open(self.file_path, "r") as f:
            content = f.read()

        # content = content.decode("utf-8")
        content_length = len(content)
        batch_size = 600

        if content_length < batch_size:
            batches_count = 2

            batches = content[:content_length // 2], content[content_length // 2:]
        else:
            batches_count = content_length // batch_size
            batches = []
            for batch_id in range(batches_count):
                batches.append(content[batch_id * batch_size:(batch_id + 1) * batch_size:])

        for i, batch in list(enumerate(batches))[self.last_loaded_part + 1:]:
            client.send(
                bytes(
                    FileResponse(
                        content=batch,
                        part_index=i,
                        total_parts=batches_count
                    ).to_json_str(),
                    encoding='UTF-8'
                )
            )
            sleep(0.001)

            if self.is_partial and i > batches_count // 2:
                break
