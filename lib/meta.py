from enum import Enum

from lib.colors import Colors


class CommEvent(Enum):
    MessageSent = 0
    MessageDelivered = 1
    MessageDeliveredDirect = 2
    MessageForwarded = 3
    MessagesDeliveredUnique = 4
    MessageTTLExpired = 5
    #
    ReceiverOutOfMem = 10


def success_event(sender, receiver, message, event):

    if event == CommEvent.MessageDeliveredDirect:
        # update particle metrics for both sender and receiver
        sender.csv_particle_writer.write_particle(messages_sent=1, messages_delivered_directly=1)
        receiver.csv_particle_writer.write_particle(messages_received=1)
        # update round metrics
        sender.sim.csv_round_writer.update_metrics(messages_sent=1, messages_delivered_directly=1, messages_received=1)
        receiver.set_color(Colors.cyan.value)
    elif event == CommEvent.MessageDelivered:
        # update particle metrics for both sender and receiver
        sender.csv_particle_writer.write_particle(messages_sent=1, messages_delivered=1)
        receiver.csv_particle_writer.write_particle(messages_received=1)
        # update round metrics
        sender.sim.csv_round_writer.update_metrics(messages_sent=1, messages_delivered=1, messages_received=1)
        receiver.set_color(Colors.green.value)
    elif event == CommEvent.MessageForwarded:
        # update particle metrics for both sender and receiver
        sender.csv_particle_writer.write_particle(messages_sent=1, messages_forwarded=1)
        receiver.csv_particle_writer.write_particle(messages_received=1)
        # update round metrics
        sender.sim.csv_round_writer.update_metrics(messages_sent=1, messages_forwarded=1, messages_received=1)
        sender.set_color(Colors.violet.value)
    elif event == CommEvent.MessageTTLExpired:
        # update round metrics
        sender.sim.csv_round_writer.update_metrics(message_ttl_expired=1)
        message.original_sender.set_color(Colors.red.value)
    elif event == CommEvent.ReceiverOutOfMem:
        # update round metrics
        sender.sim.csv_round_writer.update_metrics(receiver_out_of_mem=1)
        sender.set_color(Colors.red.value)

    print("CommEvent: " + str(event.name))