import random
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

        sender.send_store.add_message(self, False)

    def __create_msg_key(self):
        return uuid.uuid5(self.receiver.get_id(), str('msg_%d' % self.seq_number))

    def __generate_random(self):
        self.content = uuid.uuid5(self.original_sender.get_id(), 'random_msg')


class MessageStore(dict):

    def __init__(self, max_size=1000, *maps):
        self.max_size = max_size
        self.size = 0
        super().__init__(*maps)

    def add_message(self, message: Message, inc_hop_cnt=True):
        # check if the message is already present
        if message.key in self.keys():
            message = self.get(message.key)
            assert isinstance(Message, message)
            message.delivered += 1
            self.update(map(message.key, message))
        # add the message to the list of message keys intended for receiver
        else:
            # increment hop_count
            if inc_hop_cnt:
                message.hop_count += 1
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
        # check if this was the only message for the receiver of message
        if len(self[message.receiver.get_id()] < 2):
            del self[message.receiver.get_id()]
        self.size -= 1


def send_message(msg_store, sender, receiver, message: Message):
    if message.hop_count == message.ttl:
        try:
            msg_store.del_message(message)
        except KeyError:
            pass
        finally:
            return CommEvent.MessageTTLExpired

    if receiver.get_id() == message.receiver.get_id():
        store = receiver.rcv_store
    else:
        store = receiver.fwd_store

    try:
        store.add_message(message)
    except OverflowError:
        return CommEvent.ReceiverOutOfMem
    finally:
        if receiver.get_id() == message.receiver.get_id():
            try:
                msg_store.del_message(message)
            except KeyError:
                pass
            finally:
                if sender.get_id() == message.original_sender.get_id():
                    return CommEvent.MessageDeliveredDirect
                else:
                    return CommEvent.MessageDelivered
        else:
            return CommEvent.MessageForwarded


def generate_random_messages(particle_list, amount, ttl_range=None):
    sim = particle_list[0].sim
    if ttl_range is not tuple:
        ttl_range = (1, round(sim.get_max_round()/10))
    for i in range(amount):
        sender = random.choice(particle_list)
        receiver = random.choice([particle for particle in particle_list if particle != sender])
        Message(sender, receiver, start_round=sim.get_actual_round(), ttl=random.randint(ttl_range[0], ttl_range[1]))
