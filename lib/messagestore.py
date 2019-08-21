from collections import deque
from enum import Enum


class BufferStrategy(Enum):
    fifo = 0
    lifo = 1


class MessageStore(deque):
    """
    A simple expansion of collections.deque that implements fifo and lifo strategies.
    """

    def __init__(self, init=None, maxlen=None, strategy=BufferStrategy.fifo):
        """
        :param init: Initial deque.
        :type init: Iterable
        :param maxlen: Maximum length of the deque.
        :type maxlen: int
        :param strategy: Buffering strategy of the deque.
        :type strategy: :class:`~messagestore.BufferStrategy` or string
        """
        if type(strategy) == str:
            try:
                self.strategy = BufferStrategy[strategy]
            except ValueError:
                self.strategy = BufferStrategy.fifo
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
