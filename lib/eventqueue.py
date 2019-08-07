from queue import Queue


class EventQueue(Queue):

    def __init__(self, maxsize=0):
        super().__init__(maxsize)
