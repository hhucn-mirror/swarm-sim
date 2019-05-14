import uuid
from enum import Enum


class CommEvent(Enum):
    MessageSent = 0
    MessageDelivered = 1
    MessageDeliveredDirect = 2
    MessageForwarded = 3
    MessagesDeliveredUnique = 4
    MessageTTLExpired = 5
    #
    ReceiverOutOfMem = 10


class Message:

    seq_number = 0

    def __init__(self, sender, receiver, start_round: int, ttl: int, content=''):
        self.original_sender = sender
        self.receiver = receiver
        self.seq_number = Message.seq_number
        self.key = self.__create_msg_key()
        self.delivered = 0
        self.start_round = start_round
        self.delivery_round = 0
        self.forwarder = None
        self.ttl = ttl
        self.hop_count = 0
        Message.seq_number += 1

        if content == '' or content is None:
            self.__generate_random()
        else:
            self.content = content

    def __create_msg_key(self):
        return uuid.uuid5(self.receiver.get_id(), str('msg_%d' % self.seq_number))

    def __generate_random(self):
        self.content = uuid.uuid5(self.original_sender.get_id(), 'random_msg')


class MessageStore(dict):

    def __init__(self, max_size=10, *maps):
        self.max_size = max_size
        self.size = 0
        super().__init__(*maps)

    def add_message(self, message: Message):
        # check if the message is already present
        if message.key in self.keys():
            message = self.get(message.key)
            assert isinstance(Message, message)
            message.delivered += 1
            self.update(map(message.key, message))
        # add the message to the list of message keys intended for receiver
        else:
            if not message.receiver.get_id() in self:
                self[message.receiver.get_id()] = []
            self[message.receiver.get_id()].append(message.key)
            # add the actual message, if enough space
            if self.size < self.max_size:
                self[message.key] = message
                self.size += 1
            else:
                raise OverflowError

    def del_message(self, message: Message):
        del self[message.key]
        self.size -= 1


def send_message(sender, message: Message, receiver):
        try:
            receiver.rcv_store.add_message(message)
        except OverflowError:
            return CommEvent.ReceiverOutOfMem
        finally:
            if sender.get_id() == message.original_sender.get_id():
                try:
                    sender.send_store.del_message(message)
                except KeyError:
                    pass
            else:
                try:
                    sender.fwd_store.del_message(message)
                except KeyError:
                    pass
        if receiver == message.receiver:
            if sender == message.original_sender:
                return CommEvent.MessageDeliveredDirect
            else:
                return CommEvent.MessageDelivered
        else:
            return CommEvent.MessageForwarded

