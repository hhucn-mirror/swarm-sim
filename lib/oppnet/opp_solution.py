from collections import deque
from threading import Thread

from lib.oppnet.meta import NetworkEvent, EventType
from ..std_lib import green, yellow, red, orange, blue

event_queue = deque()


def process_event_queue(sim):
    """
    Processes the EventQueue of the simulator and updates corresponding csv metrics. Called every round.
    :return: Nothing
    """
    t = Thread(target=__process_event_queue__(sim))
    t.start()


def __process_event_queue__(sim):
    while not len(event_queue) == 0:
        net_event: NetworkEvent = event_queue.pop()
        event_type: EventType = net_event.event_type

        if event_type == EventType.MessageSent:
            net_event.sender.csv_particle_writer.write_particle(messages_sent=1)
            # add to message data
            sim.csv_round_writer.csv_msg_writer.update_metrics(net_event.message, sent=1)
        elif event_type == EventType.MessageDeliveredFirst:
            # update round metrics
            sim.csv_round_writer.update_metrics(messages_sent=1, messages_delivered_unique=1, messages_received=1)
            # update particle metrics for both sender and receiver
            net_event.sender.csv_particle_writer.write_particle(messages_sent=1, messages_delivered=1)
            net_event.receiver.csv_particle_writer.write_particle(messages_received=1)
            # update message data
            sim.csv_round_writer.csv_msg_writer.update_metrics(net_event.message, delivered=1,
                                                               delivery_round=sim.get_actual_round())
            # color receiver
            net_event.receiver.set_color(green)
            net_event.sender.set_color(blue)
        elif event_type == EventType.MessageDeliveredFirstDirect:
            # update round metrics
            sim.csv_round_writer.update_metrics(messages_sent=1, messages_delivered_directly_unique=1,
                                                messages_received=1)
            # update particle metrics for both sender and receiver
            net_event.sender.csv_particle_writer.write_particle(messages_sent=1, messages_delivered=1)
            net_event.receiver.csv_particle_writer.write_particle(messages_received=1)
            # update message data
            sim.csv_round_writer.csv_msg_writer.update_metrics(net_event.message, delivered_direct=1, delivered=1,
                                                               delivery_round=sim.get_actual_round())
            # color receiver
            net_event.receiver.set_color(green)
            net_event.sender.set_color(blue)
        elif event_type == EventType.MessageDeliveredDirect:
            # update round metrics
            sim.csv_round_writer.update_metrics(messages_sent=1, messages_delivered_directly=1,
                                                messages_received=1)
            # update particle metrics for both sender and receiver
            net_event.sender.csv_particle_writer.write_particle(messages_sent=1, messages_delivered_directly=1)
            net_event.receiver.csv_particle_writer.write_particle(messages_received=1)
            # update message data
            sim.csv_round_writer.csv_msg_writer.update_metrics(net_event.message, delivered_direct=1,
                                                               delivery_round=sim.get_actual_round())
            # color receiver
            net_event.receiver.set_color(green)
            net_event.sender.set_color(blue)
        elif event_type == EventType.MessageDelivered:
            # update round metrics
            sim.csv_round_writer.update_metrics(messages_sent=1, messages_delivered=1, messages_received=1)
            # update particle metrics for both sender and receiver
            net_event.sender.csv_particle_writer.write_particle(messages_sent=1, messages_delivered=1)
            net_event.receiver.csv_particle_writer.write_particle(messages_received=1)
            # update message data
            sim.csv_round_writer.csv_msg_writer.update_metrics(net_event.message, delivered=1,
                                                               delivery_round=sim.get_actual_round())
            # color receiver
            net_event.receiver.set_color(green)
            net_event.sender.set_color(blue)
        elif event_type == EventType.MessageForwarded:
            # update round metrics
            sim.csv_round_writer.update_metrics(messages_sent=1, messages_forwarded=1)
            # update particle metrics for both sender and receiver
            net_event.sender.csv_particle_writer.write_particle(messages_sent=1, messages_forwarded=1)
            # update message data
            sim.csv_round_writer.csv_msg_writer.update_metrics(net_event.message, forwarded=1)
            # color receiver
            net_event.receiver.set_color(yellow)
        elif event_type == EventType.MessageTTLExpired:
            # update round metrics
            sim.csv_round_writer.update_metrics(message_ttl_expired=1)
            # update particle metrics for the sender
            net_event.sender.csv_particle_writer.write_particle(messages_ttl_expired=1)
            # color receiver
            net_event.sender.set_color(orange)
        elif event_type == EventType.ReceiverOutOfMem:
            # update round metrics
            sim.csv_round_writer.update_metrics(receiver_out_of_mem=1)
            # update particle metrics for the receiver
            net_event.receiver.csv_particle_writer.write_particle(out_of_mem=1)
            # color receiver
            net_event.receiver.set_color(red)
