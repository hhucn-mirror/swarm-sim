from collections import deque
from enum import Enum


class BufferStrategy(Enum):
    fifo = 0
    lifo = 1


class MessageStore(deque):

    def __init__(self, init=None, maxlen=None, strategy=BufferStrategy.fifo):
        if type(strategy) == str:
            self.strategy = BufferStrategy[strategy]
        else:
            self.strategy = strategy
        if not init:
            super().__init__(maxlen=maxlen)
        else:
            super().__init__(init, maxlen=maxlen)

    def append(self, x):
        # pop the right element if max len reached
        if self.maxlen == len(self) and self.strategy == BufferStrategy.lifo:
            super().pop()

        super().append(x)
        if self.maxlen == len(self):
            # manually raise an OverFlowError for protocol purposes
            raise OverflowError
