import random
import uuid
from deprecated import deprecated
from enum import Enum

from lib.meta import EventType, NetworkEvent


class BufferStrategy(Enum):
    fifo = 0
    lifo = 1
    lru = 2
    mru = 3
    random = 4


class Message:

    seq_number = 0

    def __init__(self, sender, receiver, start_round: int, ttl: int, content=None):
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

        if content is None:
            self.__generate_random()
        else:
            self.content = content

        try:
            sender.send_store.append(self)
        except OverflowError:
            event = NetworkEvent(EventType.ReceiverOutOfMem, sender, receiver, self)
            sender.sim.event_queue.put(event)

    def __create_msg_key(self):
        return id(self)

    def __generate_random(self):
        self.content = uuid.uuid5(self.original_sender.get_id(), 'random_msg')


@deprecated
class MessageStore(dict):
    """
        This class will be removed when the newer MessageStore class in messagestore.py
        is fully evaluated.
    """
    def __init__(self, max_size=1000, buffer_strategy=BufferStrategy.lru, *maps):
        self.max_size = max_size
        self.buffer_strategy = buffer_strategy
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
            if len(self) < self.max_size:
                self[message.key] = message
            else:
                raise OverflowError

    def del_message(self, message: Message):
        del self[message.key]
        # check if this was the only message for the receiver of message
        if len(self[message.receiver.get_id()] < 2):
            del self[message.receiver.get_id()]

    def handle_overflow(self):
        if self.buffer_strategy == BufferStrategy.fifo:
            self.__handle_fifo__()
        elif self.buffer_strategy == BufferStrategy.lifo:
            self.__handle_lifo__()
        elif self.buffer_strategy == BufferStrategy.lru:
            self.__handle_lru__()
        elif self.buffer_strategy == BufferStrategy.mru:
            self.__handle_mru__()

    def __handle_fifo__(self):
        pass

    def __handle_lifo__(self):
        pass

    def __handle_lru__(self):
        pass

    def __handle_mru__(self):
        pass


def send_message(msg_store, sender, receiver, message: Message):
    if message.hop_count == message.ttl:
        try:
            msg_store.remove(message)
        except KeyError:
            pass
        finally:
            event = NetworkEvent(EventType.MessageTTLExpired, sender, receiver, message)
            sender.sim.event_queue.put(event)

    if receiver.get_id() == message.receiver.get_id():
        store = receiver.rcv_store
    else:
        store = receiver.fwd_store
    try:
        store.append(message)
    except OverflowError:
        event = NetworkEvent(EventType.ReceiverOutOfMem, sender, receiver, message)
        sender.sim.event_queue.put(event)
    finally:
        if receiver.get_id() == message.receiver.get_id():
            try:
                msg_store.remove(message)
            except KeyError:
                pass
            finally:
                if sender.get_id() == message.original_sender.get_id():
                    event = NetworkEvent(EventType.MessageDeliveredDirect, sender, receiver, message)
                    sender.sim.event_queue.put(event)
                else:
                    event = NetworkEvent(EventType.MessageDelivered, sender, receiver, message)
                    sender.sim.event_queue.put(event)
        else:
            event = NetworkEvent(EventType.MessageForwarded, sender, receiver, message)
            sender.sim.event_queue.put(event)


def generate_random_messages(particle_list, amount, sim, ttl_range=None):
    if ttl_range is not tuple:
        ttl_range = (1, round(sim.get_max_round()/10))
    for _ in range(amount):
        sender = random.choice(particle_list)
        receiver = random.choice([particle for particle in particle_list if particle != sender])
        Message(sender, receiver, start_round=sim.get_actual_round(), ttl=random.randint(ttl_range[0], ttl_range[1]))
