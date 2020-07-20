from enum import Enum

from lib.swarm_sim_header import green, blue, orange, yellow, red, cyan


class EventType(Enum):
    """
    Made to easily distinguish to events in the network.
    """
    MessageSent = 0
    MessageDelivered = 1
    MessageDeliveredDirect = 2
    MessageForwarded = 3
    MessageDeliveredFirst = 4
    MessageDeliveredFirstDirect = 5
    MessageTTLExpired = 6
    MessageCreated = 7
    MessageReplicated = 8
    BroadcastSent = 9
    BroadcastDelivered = 10
    #
    ReceiverOutOfMem = 11


def process_event(event_type, message):
    """
    Updates the values in csv_generator corresponding to each event and message.
    :param event_type: The type of event
    :type event_type: :class:`~meta.EventType`
    :param message: The message to send.
    :type message: :class:`~communication.Message`
    """
    sender = message.sender
    receiver = message.receiver
    if sender not in sender.world.particles:
        return
    if event_type == EventType.MessageCreated:
        sender.world.csv_round.update_metrics(messages_created=1)
    elif event_type == EventType.MessageReplicated:
        sender.world.csv_round.update_metrics(messages_replicated=1)
    elif event_type == EventType.MessageSent:
        sender.csv_particle_writer.write_particle(messages_sent=1)
        sender.world.csv_round.update_metrics(messages_sent=1)
        # add to message data
        sender.world.csv_round.csv_msg_writer.update_metrics(message, sent=1)
    elif event_type == EventType.MessageDeliveredFirst:
        # update round metrics
        sender.world.csv_round.update_metrics(messages_delivered_unique=1)
        # update message data
        sender.world.csv_round.csv_msg_writer.update_metrics(message, delivered=1,
                                                             delivery_round=sender.world.get_actual_round())
        # color receiver
        receiver.set_color(green)
        sender.set_color(blue)
    elif event_type == EventType.MessageDeliveredFirstDirect:
        # update round metrics
        sender.world.csv_round.update_metrics(messages_delivered_directly_unique=1)
        # update particle metrics for both sender and receiver
        sender.csv_particle_writer.write_particle(messages_delivered_directly=1)
        # update message data
        sender.world.csv_round.csv_msg_writer.update_metrics(message, delivered_direct=1,
                                                             delivery_round=sender.world.get_actual_round())
        # color receiver
        receiver.set_color(green)
        sender.set_color(blue)
    elif event_type == EventType.MessageDeliveredDirect:
        # update round metrics
        sender.world.csv_round.update_metrics(messages_delivered_directly=1)
        # update particle metrics for both sender and receiver
        sender.csv_particle_writer.write_particle(messages_delivered_directly=1)
        # update message data
        sender.world.csv_round.csv_msg_writer.update_metrics(message, delivered_direct=1,
                                                             delivery_round=sender.world.get_actual_round())
        # color receiver
        receiver.set_color(green)
        sender.set_color(blue)
    elif event_type == EventType.MessageDelivered:
        # update round metrics
        sender.world.csv_round.update_metrics(messages_delivered=1, messages_received=1)
        # update particle metrics for both sender and receiver
        sender.csv_particle_writer.write_particle(messages_delivered=1)
        receiver.csv_particle_writer.write_particle(messages_received=1)
        # update message data
        sender.world.csv_round.csv_msg_writer.update_metrics(message, delivered=1,
                                                             delivery_round=sender.world.get_actual_round())
        # color receiver
        receiver.set_color(green)
        sender.set_color(blue)
    elif event_type == EventType.MessageForwarded:
        # update round metrics
        sender.world.csv_round.update_metrics(messages_forwarded=1, messages_received=1)
        # update particle metrics for both sender and receiver
        sender.csv_particle_writer.write_particle(messages_forwarded=1)
        receiver.csv_particle_writer.write_particle(messages_received=1)
        # update message data
        sender.world.csv_round.csv_msg_writer.update_metrics(message, forwarded=1)
        # color receiver
        receiver.set_color(yellow)
    elif event_type == EventType.MessageTTLExpired:
        # update round metrics
        sender.world.csv_round.update_metrics(message_ttl_expired=1)
        # update particle metrics for the sender
        sender.csv_particle_writer.write_particle(messages_ttl_expired=1)
        # color receiver
        sender.set_color(orange)
    elif event_type == EventType.ReceiverOutOfMem:
        # update round metrics
        sender.world.csv_round.update_metrics(receiver_out_of_mem=1)
        # update particle metrics for the receiver
        receiver.csv_particle_writer.write_particle(out_of_mem=1)
        # color receiver
        receiver.set_color(red)
    elif event_type == EventType.BroadcastSent:
        # update round metrics
        sender.world.csv_round.update_metrics(broadcasts_sent=1)
        # update particle metrics for the sender
        sender.csv_particle_writer.write_particle(broadcasts_sent=1)
    elif event_type == EventType.BroadcastDelivered:
        # update round metrics
        sender.world.csv_round.update_metrics(broadcasts_delivered=1)
        # update particle metrics for the sender
        sender.csv_particle_writer.write_particle(broadcasts_delivered=1)
        # color receiver
        receiver.set_color(cyan)
