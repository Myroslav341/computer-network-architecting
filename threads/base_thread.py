from threading import Thread


class BaseThread(Thread):
    def run(self):
        self.handler()

    def handler(self, *args, **kwargs):
        raise NotImplementedError()
