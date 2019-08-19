import random
import uuid

from lib.meta import EventType, NetworkEvent


class Message:

    seq_number = 0

    def __init__(self, sender, receiver, start_round: int, ttl: int, content=None):
        self.original_sender = sender
        self.sender = sender
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
            event = NetworkEvent(EventType.ReceiverOutOfMem, sender, receiver, start_round, self)
            sender.sim.event_queue.append(event)
        sender.sim.event_queue.append(NetworkEvent(EventType.MessageSent, sender, receiver, start_round, self))

    def __create_msg_key(self):
        return id(self)

    def __generate_random(self):
        self.content = uuid.uuid5(self.original_sender.get_id(), 'random_msg')

    def inc_hop_count(self):
        self.hop_count += 1

    def set_sender(self, sender):
        self.sender = sender


def send_message(msg_store, sender, receiver, message: Message):

    current_round = sender.sim.get_actual_round()

    # remove from original store if ttl expired after this send
    if message.hop_count+1 == message.ttl:
        ttl_expired(message, msg_store, sender, receiver, current_round)
        return

    net_event = None
    if receiver.get_id() == message.receiver.get_id():
        net_event = __deliver_message(msg_store, message, sender, receiver, current_round)
    else:
        # only forward if the receiver does not yet have the message
        store = receiver.fwd_store
        if not has_message(store, message):
            ___store_message__(store, message, sender, receiver, current_round)
            net_event = NetworkEvent(EventType.MessageForwarded, sender, receiver, current_round, message)

    # put the corresponding event into the simulator event queue
    if net_event:
        sender.sim.event_queue.append(net_event)


def ttl_expired(message, store, sender, receiver, current_round):
    try:
        store.remove(message)
    except ValueError:
        pass
    finally:
        event = NetworkEvent(EventType.MessageTTLExpired, sender, receiver, current_round, message)
        sender.sim.event_queue.append(event)


def has_message(store, message: Message):
    return message in store


def __deliver_message(original_store, message, sender, receiver, current_round):
    store = receiver.rcv_store

    if sender.get_id() == message.original_sender.get_id():
        if not has_message(store, message):
            net_event = NetworkEvent(EventType.MessageDeliveredDirectUnique, sender, receiver, current_round, message)
        else:
            net_event = NetworkEvent(EventType.MessageDeliveredDirect, sender, receiver, current_round, message)
    else:
        if not has_message(store, message):
            net_event = NetworkEvent(EventType.MessageDeliveredUnique, sender, receiver, current_round, message)
        else:
            net_event = NetworkEvent(EventType.MessageDelivered, sender, receiver, current_round, message)
    ___store_message__(store, message, sender, receiver, current_round)
    # delete delivered message
    try:
        original_store.remove(message)
    except ValueError:
        pass
    return net_event


def ___store_message__(store, message, sender, receiver, current_round):
    message.inc_hop_count()
    try:
        store.append(message)
    except OverflowError:
        event = NetworkEvent(EventType.ReceiverOutOfMem, sender, receiver, current_round, message)
        sender.sim.event_queue.append(event)


def generate_random_messages(particle_list, amount, sim, ttl_range=None):
    if ttl_range is not None:
        if ttl_range is not tuple:
            ttl_range = (1, round(sim.get_max_round()/10))
    else:
        ttl_range = (sim.message_ttl, sim.message_ttl)
    for sender in particle_list:
        for _ in range(0, amount):
            receiver = random.choice([particle for particle in particle_list if particle != sender])
            Message(sender, receiver, start_round=sim.get_actual_round(),
                    ttl=random.randint(ttl_range[0], ttl_range[1]))
