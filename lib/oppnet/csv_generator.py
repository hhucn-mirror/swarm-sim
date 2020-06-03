"""

TODO:
1- Order the names based on particles, locations, and tiles and alphabetic
2- A new column called round_success
3- On demand extenstion of the metrics.


"""

import csv
import os

import pandas as pd

from lib.oppnet.communication import Message


class CsvParticleFile:
    def __init__(self, directory):
        self.file_name = directory + '/particle.csv'
        file_exists = os.path.isfile(self.file_name)
        if not file_exists:
            self.csv_file = open(self.file_name, 'w', newline='')
            self.writer = csv.writer(self.csv_file)
            self.writer.writerow(['Particle ID', 'Particle Number', 'Particle Steps',
                                  'Messages Sent', 'Messages Forwarded', 'Messages Delivered',
                                  'Messages Delivered Directly', 'Messages Received',
                                  'Messages TTL Expired', 'Out of Memory'
                                  ])

    def write_particle(self, particle):
        csv_iterator = [particle.csv_particle_writer.id, particle.csv_particle_writer.number,
                        particle.csv_particle_writer.steps,
                        particle.csv_particle_writer.messages_sent, particle.csv_particle_writer.messages_forwarded,
                        particle.csv_particle_writer.messages_delivered,
                        particle.csv_particle_writer.messages_delivered_directly,
                        particle.csv_particle_writer.messages_received,
                        particle.csv_particle_writer.messages_ttl_expired,
                        particle.csv_particle_writer.out_of_mem,
                        ]
        self.writer.writerow(csv_iterator)


class CsvParticleData:
    def __init__(self, particle_id, particle_number):
        self.id = particle_id
        self.number = particle_number
        self.steps = 0
        self.particle_write = 0
        self.messages_sent = 0
        self.messages_forwarded = 0
        self.messages_delivered = 0
        self.messages_delivered_directly = 0
        self.messages_received = 0
        self.messages_ttl_expired = 0
        self.out_of_mem = 0

    def write_particle(self, steps=0, particle_write=0, messages_sent=0, messages_forwarded=0,
                       messages_delivered=0, messages_delivered_directly=0, messages_received=0,
                       messages_ttl_expired=0, out_of_mem=0):
        self.steps += steps
        self.particle_write += particle_write
        self.messages_sent += messages_sent
        self.messages_forwarded += messages_forwarded
        self.messages_delivered += messages_delivered
        self.messages_delivered_directly += messages_delivered_directly
        self.messages_received += messages_received
        self.messages_ttl_expired += messages_ttl_expired
        self.out_of_mem += out_of_mem


class CsvPredatorFile:
    def __init__(self, directory):
        self.file_name = directory + '/predator.csv'
        file_exists = os.path.isfile(self.file_name)
        if not file_exists:
            self.csv_file = open(self.file_name, 'w', newline='')
            self.writer = csv.writer(self.csv_file)
            self.writer.writerow(['Predator ID', 'Predator Number', 'Predator Steps', 'Particles Caught'])

    def write_particle(self, predator):
        csv_iterator = [predator.csv_predator_writer.id, predator.csv_predator_writer.number,
                        predator.csv_predator_writer.steps, predator.csv_predator_writer.particles_caught,
                        ]
        self.writer.writerow(csv_iterator)


class CsvPredatorData:
    def __init__(self, predator_id, predator_number):
        self.id = predator_id
        self.number = predator_number
        self.steps = 0
        self.particles_caught = 0

    def write_particle(self, steps=0, particles_caught=0):
        self.steps += steps
        self.particles_caught += particles_caught


class CsvRoundData:
    def __init__(self, sim, task=0, solution=0, seed=20,
                 steps=0, tiles_num=0, particle_num=0, predator_num=0, directory='outputs/'):
        self.sim = sim
        self.tiles_num = tiles_num

        self.csv_msg_writer = CsvMessageData(directory)
        self.task = task
        self.solution = solution
        self.actual_round = sim.get_actual_round()
        self.seed = seed
        self.steps = steps
        self.steps_sum = steps
        self.particle_num = particle_num
        self.tile_num = tiles_num
        self.predator_num = predator_num
        self.success_counter = 0

        self.memory_write = 0
        self.memory_read = 0
        self.particle_write = 0
        self.particle_read = 0
        self.messages_sent = 0
        self.messages_forwarded = 0
        self.messages_delivered = 0
        self.messages_delivered_directly = 0
        self.messages_received = 0
        self.message_ttl_expired = 0
        self.messages_delivered_unique = 0
        self.messages_delivered_directly_unique = 0
        self.receiver_out_of_mem = 0

        self.particles_caught = 0

        self.directory = directory
        self.file_name = '%s%s' % (self.directory, '/rounds.csv')
        self.csv_file = open(self.file_name, 'w', newline='')
        self.writer_round = csv.writer(self.csv_file)
        self.writer_round.writerow(['',
                                    'Round Number', 'Seed', 'solution', 'Particle Counter',
                                    'Particle Steps', 'Particle Steps Sum',
                                    'Messages Sent', 'Messages Forwarded',
                                    'Messages Delivered', 'Messages Delivered Directly',
                                    'Messages Received', 'Messages TTL Expired',
                                    'Messages Delivered Unique', 'Messages Delivered Directly Unique',
                                    'Receiver Out Of Mem', 'Predator Counter', 'Particles Caught', 'Solution Success'
                                    ])

    def success(self):
        self.success_counter = self.success_counter + 1

    def get_messages_sent(self):
        return self.messages_sent

    def get_messages_forwarded(self):
        return self.messages_forwarded

    def get_messages_delivered(self):
        return self.messages_delivered

    def get_messages_delivered_directly(self):
        return self.messages_delivered_directly

    def get_messages_received(self):
        return self.messages_received

    def update_tiles_num(self, tiles_num):
        self.tiles_num = tiles_num

    def update_particle_num(self, particle_num):
        self.particle_num = particle_num

    def update_predator_num(self, predator_num):
        self.predator_num = predator_num

    def update_metrics(self, steps=0, memory_write=0, memory_read=0, particle_write=0, particle_read=0,
                       messages_sent=0, messages_forwarded=0,
                       messages_delivered=0, messages_delivered_directly=0, messages_received=0,
                       messages_delivered_unique=0, messages_delivered_directly_unique=0,
                       message_ttl_expired=0, receiver_out_of_mem=0, particles_caught=0):

        self.steps_sum += steps

        if self.actual_round == self.sim.get_actual_round():
            self.steps += steps
            self.memory_write += memory_write
            self.memory_read += memory_read
            self.particle_write += particle_write
            self.messages_sent += messages_sent
            self.messages_forwarded += messages_forwarded
            self.messages_delivered += messages_delivered
            self.messages_delivered_directly += messages_delivered_directly
            self.messages_received += messages_received
            self.message_ttl_expired += message_ttl_expired
            self.messages_delivered_unique += messages_delivered_unique
            self.messages_delivered_directly_unique += messages_delivered_directly_unique
            self.receiver_out_of_mem += receiver_out_of_mem
            self.particles_caught += particles_caught

        elif self.actual_round != self.sim.get_actual_round():
            self.actual_round = self.sim.get_actual_round()
            self.steps = steps
            self.memory_write = memory_write
            self.memory_read = memory_read
            self.particle_write = particle_write
            self.particle_read = particle_read
            self.messages_sent = messages_sent
            self.messages_forwarded = messages_forwarded
            self.messages_delivered = messages_delivered
            self.messages_delivered_directly = messages_delivered_directly
            self.messages_received = messages_received
            self.message_ttl_expired = message_ttl_expired
            self.messages_delivered_unique = messages_delivered_unique
            self.messages_delivered_directly_unique = messages_delivered_directly_unique
            self.receiver_out_of_mem = receiver_out_of_mem
            self.particles_caught = particles_caught

    def next_line(self, simulator_round):
        csv_iterator = ['', simulator_round, self.seed, self.solution, self.particle_num,
                        self.steps, self.steps_sum,
                        self.messages_sent, self.messages_forwarded, self.messages_delivered,
                        self.messages_delivered_directly, self.messages_received,
                        self.message_ttl_expired, self.messages_delivered_unique,
                        self.messages_delivered_directly_unique, self.receiver_out_of_mem,
                        self.predator_num, self.particles_caught, self.success_counter]
        self.writer_round.writerow(csv_iterator)
        self.actual_round = simulator_round
        self.steps = 0
        self.messages_sent = 0
        self.messages_forwarded = 0
        self.messages_delivered = 0
        self.messages_delivered_directly = 0
        self.messages_received = 0
        self.message_ttl_expired = 0
        self.messages_delivered_unique = 0
        self.messages_delivered_directly_unique = 0
        self.receiver_out_of_mem = 0
        self.particles_caught = 0
        self.success_counter = 0

    def aggregate_metrics(self):
        self.csv_file.close()
        data = pd.read_csv(self.file_name)
        file_name = self.directory + "/aggregate_rounds.csv"
        csv_file = open(file_name, 'w', newline='')
        writer_round = csv.writer(csv_file)
        """Average Min Max for all other metrics"""
        writer_round.writerow(['Seed', 'Rounds Total',
                               'Solution',
                               'Messages Sent Sum', 'Messages Forwarded Sum',
                               'Messages Delivered Sum', 'Messages Delivered Directly Sum',
                               'Messages Received Sum', 'Messages TTL Expired',
                               'Messages Delivered Unique Sum', 'Messages Delivered Directly Unique Sum',
                               'Receiver Out Of Mem Sum', 'Particles Caught Sum'
                               ])

        csv_iterator = [self.seed, data['Round Number'].count(),
                        self.solution,
                        data['Messages Sent'].sum(), data['Messages Forwarded'].sum(),
                        data['Messages Delivered'].sum(), data['Messages Delivered Directly'].sum(),
                        data['Messages Received'].sum(), data['Messages TTL Expired'].sum(),
                        data['Messages Delivered Unique'].sum(), data['Messages Delivered Directly Unique'].sum(),
                        data['Receiver Out Of Mem'].sum(), data['Particles Caught'].sum()
                        ]
        writer_round.writerow(csv_iterator)
        csv_file.close()


class CsvMessageData:
    """
    Collects sending, forwarding and delivery information for a dictionary of message objects in a csv.
    Contains :class:`~csv_generatore.MessageData` objects.
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
