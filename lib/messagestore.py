from collections import deque

from lib.comms import BufferStrategy


class MessageStore(deque):

    def __init__(self, init=None, maxlen=None, strategy=BufferStrategy.fifo):
        self.strategy = strategy
        if not init:
            super().__init__(maxlen=maxlen)
        else:
            super().__init__(init, maxlen=maxlen)

    def append(self, x):
        if self.strategy == BufferStrategy.lifo:
            if self.maxlen == len(self):
                super().pop(len(x))
            super().append(x)
        else:
            super().append(x)
        #if self.maxlen == len(self):
        #    raise OverflowError

    def __getitem__(self, index):
        if self.strategy == BufferStrategy.mru:
            x = super().pop(index)
            super().appendleft(x)
        elif self.strategy == BufferStrategy.lru:
            x = super().pop(index)
            super().append(x)
        super().__getitem__(index)
