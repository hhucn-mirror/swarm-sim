import copy
import random

from lib.oppnet.meta import EventType, process_event
from lib.oppnet.point import Point


class Message:
    seq_number = 0

    def __init__(self, sender, receiver, start_round=None, ttl=None, content=None, is_copy=False, actual_receiver=None):
        """
        Initializes a Message instance and puts it in the sender's MessageStore.
        :param sender: The particle sending the message.
        :type sender: :class:`~opp_particle.Particle`
        :param receiver: The intended receiving particle of the message.
        :type receiver: :class:`~opp_particle.Particle`
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
        self.key = self.__create_msg_key__()
        self.delivered = 0
        if not start_round:
            start_round = sender.world.get_actual_round()
        self.start_round = start_round
        self.delivery_round = 0
        self.forwarder = None
        if not ttl:
            ttl = sender.world.message_ttl
        self.ttl = ttl
        self.hops = 0
        self.content = content

        if is_copy:
            self.actual_receiver = actual_receiver
        else:
            self.actual_receiver = receiver
            try:
                self.sender.send_store.append(self)
            except OverflowError:
                process_event(EventType.ReceiverOutOfMem, self)

        Message.seq_number += 1

    def __eq__(self, other):
        """
        Checks if :param other: is equal to :param self: by comparing their keys.
        :param other: Other message object.
        :return: if self equals other as boolean
        """
        return self.key == other.key

    def get_receiver(self):
        """
        Returns the current receiver.
        :return: receiving :class:`~opp_particle.Particle`
        """
        return self.receiver

    def set_receiver(self, receiver):
        """
        Updates the current receiver to :param receiver:.
        :param receiver: the receiver to update to
        """
        self.receiver = receiver

    def get_actual_receiver(self):
        """
        Returns the actual receiver.
        :return: actual receiving :class:`~opp_particle.Particle`
        """
        return self.actual_receiver

    def set_actual_receiver(self, receiver):
        """
        Updates the actual receiver to :param receiver:.
        :param receiver: the new actual receiver
        """
        self.actual_receiver = receiver

    def get_sender(self):
        """
        Returns the current sender.
        :return: the current sender
        """
        return self.sender

    def get_content(self):
        """
        Returns the message content.
        :return: the message content
        :rtype: any
        """
        return self.content

    def get_hops(self):
        """
        Returns the number of hops the message has travelled.
        :return: hops
        :rtype: int
        """
        return self.hops

    def __copy__(self):
        """
        Creates a copy of the message object by reusing the same key and sequence number.
        :return: the message copy
        """
        new = type(self)(self.sender, self.receiver, self.start_round, self.ttl, self.content, is_copy=True,
                         actual_receiver=self.get_actual_receiver())
        new.key = self.key
        new.seq_number = self.seq_number
        new.hops = self.hops + 1
        Message.seq_number -= 1
        return new

    def __create_msg_key__(self):
        """
        Returns the key for a message object
        :return: the builtin identity of message.
        """
        return id(self)

    def inc_hops(self):
        """
        Increments message hop count
        """
        self.hops += 1

    def set_sender(self, sender):
        """
        Updates the sender.
        :param sender: The new sender
        :type sender: :class:`~opp_particle.Particle`
        """
        self.sender = sender

    def update_delivery(self):
        delivery_round = self.sender.world.get_actual_round()
        if self.delivery_round == 0:
            self.delivery_round = delivery_round
        self.delivered += 1


def send_message(sender, receiver, message: Message):
    """
    Sends :param message: from :param sender: to :param receiver: by giving it to the memory module.
    Checks beforehand if ttl has expired and in such case does not send it.
    :param sender: The particle sending the Message.
    :type sender: :class:`~opp_particle.Particle`
    :param receiver: The intended receiver of the message.
    :type receiver: :class:`~opp_particle.Particle`
    :param message: The message to send.
    :type message: :class:`~communication.Message`
    """

    current_round = sender.world.get_actual_round()
    msg_store = sender.send_store

    # check if the message ttl has expired after this
    if message.hops == message.ttl:
        ttl_expired(message, msg_store)
        return

    original = message
    message = copy.copy(original)
    message.set_sender(sender)
    message.set_receiver(receiver)

    memory = sender.world.memory
    memory.add_delta_message_on(receiver.get_id(), message, Point(sender.coordinates[0], sender.coordinates[1]),
                                current_round, sender.signal_velocity, 5)  # TODO: add attributes to particles


def broadcast_message(sender, receivers, message_content):
    """
    Sends :param message_content: from :param sender: to all :param receivers: by giving it to the memory module.
    Checks beforehand if ttl has expired and in such case does not send it.
    :param sender: The particle sending the Message.
    :type sender: :class:`~opp_particle.Particle`
    :param receivers: The intended receivers of the message.
    :type receivers: :class:`~opp_particle.Particle`
    :param message_content: The content of the message to be send.
    :type message_content: any`
    """

    for receiver in receivers:
        message = Message(sender, receiver, content=message_content)
        send_message(sender, receiver, message)


def ttl_expired(message, store):
    """
    Handle expiry of TTL. Delete the message from :param store: and calls the process_event function
    for an expired ttl.
    :param message: The message that expired.
    :type message: :class:`~communication.Message`
    :param store: The MessageStore containing the :param message:.
    :type store: :class:`~messagestore.MessageStore`
    """
    try:
        store.remove(message)
    except ValueError:
        pass
    finally:
        process_event(EventType.MessageTTLExpired, message)


def store_message(message, sender, receiver):
    """
    Puts the :param message: in the :param receiver:'s :param store: and handles OverflowError by creating
    a ReceiverOutOfMem NetworkEvent. The actual overflow is handled internally in the :param store:
    :param message: The message to store.
    :type message: :class:`~communication.Message`
    :param sender: The sender of the message.
    :type sender: :class:`~opp_particle.Particle`
    :param receiver: The receiver of the message.
    :type receiver: :class:`~opp_particle.Particle`
    """

    if message.get_actual_receiver().number == message.get_receiver().number:
        message.update_delivery()
        sender.send_store.remove(message)  # remove message in sender on delivery
        store = receiver.rcv_store  # chose receive-store
        process_event(EventType.MessageDelivered, message)  # process csv event
        if message.original_sender == message.sender:
            process_event(EventType.MessageDeliveredDirect, message)
    else:
        store = receiver.send_store
        if not (store.contains_key(message.key)):
            process_event(EventType.MessageForwarded, message)  # TODO: remove receiver sender
    try:
        store.append(message)
    except OverflowError:
        process_event(EventType.ReceiverOutOfMem, message)


def generate_random_messages(particle_list, amount, world, ttl_range=None):
    """
    Creates :param amount: many messages for each particle in :param particle_list: with a TTL randomly picked from
    :param ttl_range.

    :param particle_list: The list of particles messages should be generated for.
    :type particle_list: list
    :param amount: The amount of messages to be created for each particle.
    :type amount: number
    :param world: The simulator instance.
    :type world: :class:`~world.World`
    :param ttl_range: Min and max value for the TTL value to be randomly drawn from for each message.
    :type ttl_range: tuple
    :return: list of generated messages
    """
    messages = []
    if ttl_range is not None:
        if ttl_range is not tuple:
            ttl_range = (1, round(world.get_max_round() / 10))
    else:
        ttl_range = (world.message_ttl, world.message_ttl)
    for sender in particle_list:
        for _ in range(0, amount):
            receiver = random.choice([particle for particle in particle_list if particle != sender])
            messages.append(Message(sender, receiver, start_round=world.get_actual_round(),
                                    ttl=random.randint(ttl_range[0], ttl_range[1])))
    return messages
