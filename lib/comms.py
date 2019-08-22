import copy
import random

from lib.meta import EventType, NetworkEvent


class Message:

    seq_number = 0

    def __init__(self, sender, receiver, start_round: int, ttl: int, content=None):
        """
        Initializes a Message instance and puts it in the sender's MessageStore.
        :param sender: The particle sending the message.
        :type sender: :class:`~particle.Particle`
        :param receiver: The intended receiving particle of the message.
        :type receiver: :class:`~particle.Particle`
        :param start_round: The round when the message was created.
        :type start_round: int
        :param ttl: Time-to-live value of the message.
        :type ttl: int
        :param content: The content of the message.
        :type content: any
        """
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
        self.content = content

        Message.seq_number += 1

        try:
            sender.send_store.append(self)
        except OverflowError:
            event = NetworkEvent(EventType.ReceiverOutOfMem, sender, receiver, start_round, self)
            sender.sim.event_queue.append(event)
        sender.sim.event_queue.append(NetworkEvent(EventType.MessageSent, sender, receiver, start_round, self))

    def __copy__(self):
        new = type(self)(self.sender, self.receiver, self.start_round, self.ttl, self.content)
        new.key = self.key
        new.seq_number = self.seq_number
        new.hop_count = self.hop_count
        Message.seq_number -= 1
        return new

    def __create_msg_key(self):
        """
        :return: the builtin identity of message.
        """
        return id(self)

    def inc_hop_count(self):
        """
        Increments message hop count
        """
        self.hop_count += 1

    def set_sender(self, sender):
        """
        Updates the sender.
        :param sender: The new sender
        :type sender: :class:`~particle.Particle`
        """
        self.sender = sender

    def update_delivery(self, delivery_round):
        if self.delivery_round == 0:
            self.delivery_round = delivery_round
        self.delivered += 1


def send_message(msg_store, sender, receiver, message: Message):
    """
    Puts the :param message: object in the receiver's corresponding MessageStore. Depending on if the message is
    delivered to the sender or forwarded.
    :param msg_store: The MessageStore of the sender the message originates from.
    :type msg_store: :class:`~messagestore.MessageStore`
    :param sender: The particle sending the Message.
    :type sender: :class:`~particle.Particle`
    :param receiver: The intended receiver of the message.
    :type receiver: :class:`~particle.Particle`
    :param message: The message to send.
    :type message: :class:`~comms.Message`
    """

    current_round = sender.sim.get_actual_round()

    original = message
    message = copy.copy(message)

    # remove from original store if ttl expired after this send
    if message.hop_count+1 == message.ttl:
        ttl_expired(original, msg_store, sender, receiver, current_round)

    net_event = None
    if receiver.get_id() == message.receiver.get_id():
        net_event = __deliver_message(message, sender, receiver, current_round)
        # remove original upon delivery
        msg_store.remove(original)
    else:
        # only forward if the receiver does not yet have the message
        store = receiver.fwd_store
        if not store.contains_key(message.key):
            ___store_message__(store, message, sender, receiver, current_round)
            net_event = NetworkEvent(EventType.MessageForwarded, sender, receiver, current_round, message)

    # put the corresponding event into the simulator event queue
    if net_event:
        sender.sim.event_queue.append(net_event)


def ttl_expired(message, store, sender, receiver, current_round):
    """
    Handle expiry of TTL. Delete the message from :param store: and append a corresponding NetworkEvent in the
    simulator EventQueue.
    :param message: The message that expired.
    :type message: :class:`~comms.Message`
    :param store: The MessageStore containing the :param message:.
    :type store: :class:`~messagestore.MessageStore`
    :param sender: The sender of the message.
    :type sender: :class:`~particle.Particle`
    :param receiver: The intended receiver of the message.
    :type receiver: :class:`~particle.Particle`
    :param current_round: The current simulator round
    :type current_round: int
    """
    try:
        store.remove(message)
    except ValueError:
        pass
    finally:
        event = NetworkEvent(EventType.MessageTTLExpired, sender, receiver, current_round, message)
        sender.sim.event_queue.append(event)


def has_message(store, message: Message):
    """
    Checks if message in store.
    :param store: The store to be checked.
    :type store: :class:`~messagestore.MessageStore`
    :param message: The message to be checked.
    :type message: :class:`~comms.Message`
    :return: ? message in store
    :rtype: bool
    """
    return message in store


def __deliver_message(message, sender, receiver, current_round):
    """
    Delivers :param message: from :param sender: to :param receiver:.
    Also creates corresponding NetworkEvent in simulator EventQueue.
    :param message: The message to send.
    :type message: :class:`~comms.Message`
    :param sender: The sender of :param message:.
    :type sender: :class:`~particle.Particle`
    :param receiver: The receiving particle of :param message:.
    :type receiver: :class:`~particle.Particle`
    :param current_round: The current simulator round.
    :type current_round: int
    :return: The corresponding NetworkEvent depending on whether the message was delivered directly
             and/or for the first time.
    :rtype: :class:`~meta.NetworkEvent`
    """
    store = receiver.rcv_store

    message.update_delivery(current_round)

    if sender.get_id() == message.original_sender.get_id():
        if not store.contains_key(message.key):
            net_event = NetworkEvent(EventType.MessageDeliveredDirectUnique, sender, receiver, current_round, message)
        else:
            net_event = NetworkEvent(EventType.MessageDeliveredDirect, sender, receiver, current_round, message)
    else:
        if not store.contains_key(message.key):
            net_event = NetworkEvent(EventType.MessageDeliveredUnique, sender, receiver, current_round, message)
        else:
            net_event = NetworkEvent(EventType.MessageDelivered, sender, receiver, current_round, message)
    ___store_message__(store, message, sender, receiver, current_round)
    return net_event


def ___store_message__(store, message, sender, receiver, current_round):
    """
    Puts the :param message: in the :param receiver:'s :param store: and handles OverflowError by creating
    a ReceiverOutOfMem NetworkEvent. The actual overflow is handled internally in the :param store:
    :param store: The store :param message: is to be put in.
    :type store: :class:`~messagestore.MessageStore`
    :param message: The message to store.
    :type message: :class:`~comms.Message`
    :param sender: The sender of the message.
    :type sender: :class:`~particle.Particle`
    :param receiver: The receiver of the message.
    :type receiver: :class:`~particle.Particle`
    :param current_round: The current simulator round.
    :type current_round: int
    """
    message.inc_hop_count()
    try:
        store.append(message)
    except OverflowError:
        event = NetworkEvent(EventType.ReceiverOutOfMem, sender, receiver, current_round, message)
        sender.sim.event_queue.append(event)


def generate_random_messages(particle_list, amount, sim, ttl_range=None):
    """
    Creates :param amount: many messages for each particle in :param particle_list: with a TTL randomly picked from
    :param ttl_range.

    :param particle_list: The list of particles messages should be generated for.
    :type particle_list: list
    :param amount: The amount of messages to be created for each particle.
    :type amount: number
    :param sim: The simulator instance.
    :type sim: :class:`~sim.Sim`
    :param ttl_range: Min and max value for the TTL value to be randomly drawn from for each message.
    :type ttl_range: tuple
    """
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
