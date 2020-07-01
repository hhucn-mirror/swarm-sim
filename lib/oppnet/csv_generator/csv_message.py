import csv

from lib.oppnet.communication import Message


class CsvMessageData:
    """
    Collects sending, forwarding and delivery information for a dictionary of message objects in a csv.
    Contains :class:`~csv_generator.MessageData` objects.
    """

    def __init__(self, directory="outputs/", solution=""):
        """
        :param solution: The simulator solution used
        :type: solution: str
        :param directory: The directory for the csv to be put in.
        :type directory: str
        """
        self.solution = solution
        self.messages = {}
        self.directory = directory
        self.file_name = directory + '/messages.csv'
        self.csv_file = open(self.file_name, 'w', newline='')
        self.writer = csv.writer(self.csv_file)

        self.writer.writerow(['Key', 'Number',
                              'Original Sender Number', 'Receiver Number',
                              'Sent Count',
                              'Forwarding Count', 'Delivery Count',
                              'Direct Delivery Count',
                              'Initial Sent Round', 'First Delivery Round',
                              'First Delivery Hops', 'Minimum Hops'
                              ])

    def __del__(self):
        """
        Destructor that writes the csv rows.
        """
        # write message data rows
        self.write_rows()

    def write_rows(self):
        """
        Writes rows for all messages.
        """
        for key, m_data in self.messages.items():
            self.writer.writerow([key, m_data.seq_number,
                                  m_data.sender, m_data.receiver,
                                  m_data.sent, m_data.forwarded,
                                  m_data.delivered, m_data.delivered_direct,
                                  m_data.sent_round, m_data.delivery_round,
                                  m_data.first_hops, m_data.min_hops
                                  ])
        self.csv_file.close()

    def add_messages(self, messages):
        """
        Adds messages to the messages dictionary.
        :param messages: iterable type of messages
        :type messages: Iterable
        """
        if hasattr(messages, '__iter__'):
            for m in messages:
                self.add_message(m)

    def add_message(self, message: Message):
        """
        Adds a new message to track.
        :param message: The message to track.
        :type message: :class:`~communication.Message`
        """
        if message.key not in self.messages.keys():
            self.messages[message.key] = MessageData(message)

    def update_metrics(self, message: Message, sent=0, forwarded=0,
                       delivered=0, delivered_direct=0, delivery_round=None,
                       ):
        """
        Updates the corresponding parameter values for a :param message: in the messages dictionary.
        :param message: The tracked message which statistics are updated.
        :type message: :class:`~message.Message`
        :param sent: The amount it was sent.
        :type sent: int
        :param forwarded: The amount it was forwarded.
        :type forwarded: int
        :param delivered: The amount it was delivered.
        :type delivered: int
        :param delivered_direct: The amount it was delivered directly from sender to receiver.
        :type delivered_direct: int
        :param delivery_round: The round the message was delivered in.
        :type delivery_round: int
        """
        self.add_message(message)
        m_data = self.messages[message.key]
        if not delivery_round:
            hops = None
        else:
            hops = message.hops
        m_data.update_metric(sent, forwarded, delivered, delivered_direct, delivery_round, hops)
        self.messages[message.key] = m_data


class MessageData:
    """
    The tracking data for a message.
    """

    def __init__(self, message: Message):
        """
        :param message:
        :type message: :class:`~communication.Message`
        """
        self.key = message.key
        self.seq_number = message.seq_number
        self.sender = message.original_sender.number
        if message.actual_receiver is None:
            self.receiver = 'broadcast'
        else:
            self.receiver = message.actual_receiver.number
        self.sent = 0
        self.sent_round = message.start_round
        self.forwarded = 0
        self.delivered = 0
        self.delivered_direct = 0
        self.delivery_round = None
        self.first_hops = None
        self.min_hops = None

    def update_metric(self, sent=0, forwarded=0, delivered=0, delivered_direct=0, delivery_round=None, hops=None):
        """
        Updates the statistics.
        :param sent: The amount it was sent.
        :type sent: int
        :param forwarded: The amount it was forwarded.
        :type forwarded: int
        :param delivered: The amount it was delivered.
        :type delivered: int
        :param delivered_direct: The amount it was delivered directly from sender to receiver.
        :type delivered_direct: int
        :param delivery_round: The round the message was delivered in.
        :type delivery_round: int
        :param hops: The hops of the message object.
        :type hops: int
        """
        self.sent += sent
        self.forwarded += forwarded
        self.delivered += delivered
        self.delivered_direct += delivered_direct
        if delivery_round and not self.delivery_round:
            self.delivery_round = delivery_round
        if hops:
            if not self.first_hops:
                self.first_hops = hops
                self.min_hops = hops
            elif hops < self.min_hops:
                self.min_hops = hops

    def get_sent_count(self):
        """
        Returns the sent count.
        :return: sent count
        """
        return self.sent

    def get_forwarding_count(self):
        """
        Returns the forwarding count.
        :return: forwarding count
        """
        return self.forwarded

    def get_delivery_count(self):
        """
        Returns the delivery count.
        :return: delivery count
        """
        return self.delivered

    def get_delivery_round(self):
        """
        Returns the delivery round. Might be None.
        :return: delivery round
        """
        return self.delivery_round

    def get_first_delivery_hops(self):
        """
        Returns the hops of the first delivery. Might be None.
        :return: hops of the first delivery
        """
        return self.first_hops
