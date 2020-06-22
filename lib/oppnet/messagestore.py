from collections import deque
from enum import Enum

from lib.oppnet.communication import Message


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
        self.keys = {}
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

    def __len__(self):
        """
        Returns the length of the deque.
        :return: length of deque
        """
        return super().__len__()

    def pop(self, **kwargs):
        """
        Pops right element of the queue
        :param kwargs: Unused Pyobject of collections.deque
        :type kwargs: Pyobject
        :return: right element of the deque
        """
        message = super().pop(**kwargs)
        try:
            self.keys.pop(message.key)
        except KeyError:
            pass
        return message

    def popleft(self, **kwargs):
        """
        Pops left element of the queue
        :param kwargs: Unused Pyobject of collections.deque
        :type kwargs: Pyobject
        :return: left element of the deque
        """
        message = super().popleft()
        try:
            self.keys.pop(message.key)
        except KeyError:
            pass
        return message

    def append(self, m: Message):
        """
        Appends :param m: to deque and adds its key. Handles a full deque by popping messages at the ends of the deque.
        :param m: the message to add
        """
        # pop the right element if max len reached
        if self.contains_key(m.key):
            return
        if self.maxlen == len(self):
            if self.strategy == BufferStrategy.fifo:
                self.popleft()
            else:
                self.pop()

        super().append(m)
        self.__append_key__(m.key, m)

        if self.maxlen == len(self):
            # manually raise an OverFlowError for protocol purposes
            raise OverflowError

    def appends(self, messages: [Message]):
        """
        Appends all messsages in list :param messages: to deque and adds its key. Handles a full deque by popping
        messages at the ends of the deque.
        :param messages: the messages to add
        """
        for message in messages:
            self.append(message)

    def remove(self, message):
        """
        Removes a :param message: if it exists in the deque.
        :param message: the message to remove
        """
        try:
            super().remove(message)
            self.keys.pop(message.key)
        except ValueError:
            pass
        except KeyError:
            pass

    def contains_key(self, key):
        """
        Check if a message key exists in the deque
        :param key: key of a message to be checked
        :return: if a key exists in the deque
        """
        return key in self.keys

    def get_by_key(self, key):
        """
        Returns a message by it's key.
        :param key: The key of the message to be retrieved
        :return: the message correspoding to key
        """
        return self.keys[key]

    def __append_key__(self, key, m_index):
        """
        Adds :param key:, :param m_index: pair as key, value pair to keys.
        :param key: the key to use
        :param m_index: the object to use as value
        """
        if key not in self.keys:
            self.keys[key] = m_index
