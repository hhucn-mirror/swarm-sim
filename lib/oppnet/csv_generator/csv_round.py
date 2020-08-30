import csv

import pandas as pd

from lib.oppnet.csv_generator import CsvMessageData


class CsvRoundData:
    """
    Collects information about the simulation on a round by round basis.
    """

    def __init__(self, sim, solution=0, seed=20,
                 steps=0, tiles_num=0, particle_num=0, predator_num=0, directory='outputs/'):
        """
        Constructor. Initializes round data by creating csv in :param directory.
        :param sim: simulator object
        :param solution: solution name
        :param seed: random seed
        :param steps: steps by all particles
        :param tiles_num: number of tiles
        :param particle_num: number of particles
        :param predator_num: number of predators
        :param directory: directory string for the csv file
        """
        self.sim = sim
        self.tiles_num = tiles_num

        self.csv_msg_writer = CsvMessageData(directory)
        self.solution = solution
        self.actual_round = sim.get_actual_round()
        self.seed = seed
        self.steps = steps
        self.steps_sum = steps
        self.particle_num = particle_num
        self.predator_num = predator_num
        self.success_counter = 0

        self.memory_write = 0
        self.memory_read = 0
        self.particle_write = 0
        self.particle_read = 0
        self.messages_created = 0
        self.messages_replicated = 0
        self.messages_sent = 0
        self.messages_forwarded = 0
        self.messages_delivered = 0
        self.messages_delivered_directly = 0
        self.messages_received = 0
        self.message_ttl_expired = 0
        self.messages_delivered_unique = 0
        self.messages_delivered_directly_unique = 0
        self.receiver_out_of_mem = 0

        self.broadcasts_sent = 0
        self.broadcasts_delivered = 0

        self.particles_caught = 0

        self.directory = directory
        self.file_name = '%s%s' % (self.directory, '/rounds.csv')
        self.csv_file = open(self.file_name, 'w', newline='')
        self.writer_round = csv.writer(self.csv_file)
        self.writer_round.writerow([
            'Round Number', 'Seed', 'solution', 'Particle Counter',
            'Particle Steps', 'Particle Steps Sum',
            'Messages Created', 'Message Replication Counter', 'Messages Sent',
            'Messages Forwarded', 'Messages Delivered Total', 'Messages Delivered Directly',
            'Messages Received', 'Messages TTL Expired',
            'Messages Delivered Unique', 'Messages Delivered Directly Unique',
            'Broadcasts Sent', 'Broadcast Messages Delivered',
            'Receiver Out Of Mem', 'Predator Counter', 'Particles Caught', 'Solution Success'
        ])

    def success(self):
        """
        Increments success variable.
        :return: None
        """
        self.success_counter = self.success_counter + 1

    def get_messages_sent(self):
        """
        Gets the number of messages sent.
        :return: int
        """
        return self.messages_sent

    def get_messages_forwarded(self):
        """
        Gets the number of messages forwarded.
        :return: int
        """
        return self.messages_forwarded

    def get_messages_delivered(self):
        """
        Gets the number of messages delivered.
        :return: int
        """
        return self.messages_delivered

    def get_messages_delivered_directly(self):
        """
        Gets the number of messages delivered directly.
        :return: int
        """
        return self.messages_delivered_directly

    def get_messages_received(self):
        """
        Gets the number of messages received.
        :return: int
        """
        return self.messages_received

    def update_tiles_num(self, tiles_num):
        """
        Sets the number of tiles to :param tiles_num.
        :param tiles_num: number of tiles
        """
        self.tiles_num = tiles_num

    def update_particle_num(self, particle_num):
        """
        Sets the number of particles to :param particle_num.
        :param particle_num: number of particles
        """
        self.particle_num = particle_num

    def update_predator_num(self, predator_num):
        """
        Sets the number of predators to :param predator_num.
        :param predator_num: number of predators
        """
        self.predator_num = predator_num

    @NotImplemented
    def update_locations_num(self, locations_num):
        return

    def update_metrics(self, steps=0, memory_write=0, memory_read=0, particle_write=0, particle_read=0,
                       messages_created=0, messages_replicated=0, messages_sent=0, messages_forwarded=0,
                       messages_delivered=0, messages_delivered_directly=0, messages_received=0,
                       messages_delivered_unique=0, messages_delivered_directly_unique=0,
                       message_ttl_expired=0, broadcasts_sent=0, broadcasts_delivered=0, receiver_out_of_mem=0,
                       particles_caught=0):
        """
        Updates the round metrics.
        :param steps: int
        :param memory_write: int
        :param memory_read: int
        :param particle_write: int
        :param particle_read: int
        :param messages_created: int
        :param messages_replicated: int
        :param messages_sent: int
        :param messages_forwarded: int
        :param messages_delivered: int
        :param messages_delivered_directly:
        :param messages_received: int
        :param messages_delivered_unique: int
        :param messages_delivered_directly_unique: int
        :param message_ttl_expired: int
        :param broadcasts_sent: int
        :param broadcasts_delivered: int
        :param receiver_out_of_mem: int
        :param particles_caught: int
        :return: None
        """
        self.steps_sum += steps

        if self.actual_round == self.sim.get_actual_round():
            self.steps += steps
            self.memory_write += memory_write
            self.memory_read += memory_read
            self.particle_write += particle_write
            self.messages_created += messages_created
            self.messages_replicated += messages_replicated
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
            self.broadcasts_sent += broadcasts_sent
            self.broadcasts_delivered += broadcasts_delivered

        elif self.actual_round != self.sim.get_actual_round():
            self.actual_round = self.sim.get_actual_round()
            self.steps = steps
            self.memory_write = memory_write
            self.memory_read = memory_read
            self.particle_write = particle_write
            self.particle_read = particle_read
            self.messages_sent = messages_created
            self.messages_replicated = messages_replicated
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
            self.broadcasts_sent = broadcasts_sent
            self.broadcasts_delivered = broadcasts_delivered

    def next_line(self, simulator_round):
        """
        Writes the next round in the csv file.
        :param simulator_round: round to write.
        :return: None
        """
        csv_iterator = [simulator_round, self.seed, self.solution, self.particle_num,
                        self.steps, self.steps_sum,
                        self.messages_created, self.messages_replicated, self.messages_sent, self.messages_forwarded,
                        self.messages_delivered, self.messages_delivered_directly, self.messages_received,
                        self.message_ttl_expired, self.messages_delivered_unique,
                        self.messages_delivered_directly_unique,
                        self.broadcasts_sent, self.broadcasts_delivered, self.receiver_out_of_mem,
                        self.predator_num, self.particles_caught, self.success_counter]
        self.writer_round.writerow(csv_iterator)
        self.actual_round = simulator_round
        self.steps = 0
        self.messages_created = 0
        self.messages_replicated = 0
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
        self.broadcasts_sent = 0
        self.broadcasts_delivered = 0

    def aggregate_metrics(self):
        """
        Creates a new csv file aggregating the round data. Mostly by creating sums but also more advanced
        metrics such as OppNet metrics overhead, delivery success rate and delivery efficiency for message passing.
        :return: None
        """
        self.csv_file.close()
        data = pd.read_csv(self.file_name)
        file_name = self.directory + "/aggregate_rounds.csv"
        csv_file = open(file_name, 'w', newline='')
        writer_round = csv.writer(csv_file)
        """Average Min Max for all other metrics"""
        writer_round.writerow(['Seed', 'Rounds Total',
                               'Solution',
                               'Messages Created Sum', 'Message Replication Sum',
                               'Messages Sent Sum', 'Messages Forwarded Sum',
                               'Messages Delivered Total Sum', 'Messages Delivered Directly Sum',
                               'Messages Received Sum', 'Messages TTL Expired',
                               'Messages Delivered Unique Sum', 'Messages Delivered Directly Unique Sum',
                               'Broadcasts Sent Sum', 'Broadcast Messages Delivered Sum',
                               'Message Delivery Success ζ', 'Message Delivery Efficiency η', 'Message Overhead σ',
                               'Receiver Out Of Mem Sum', 'Particles Caught Sum'
                               ])
        sent_sum = data['Messages Sent'].sum()
        created_sum = data['Messages Created'].sum()
        replicated_sum = data['Message Replication Counter'].sum()
        delivered_sum = data['Messages Delivered Total'].sum()
        delivered_unique_sum = data['Messages Delivered Unique'].sum()
        delivered_directly_unique_sum = data['Messages Delivered Directly Unique'].sum()
        delivered_unique_total = delivered_unique_sum + delivered_directly_unique_sum
        broadcasts_sent = data['Broadcasts Sent'].sum()

        csv_iterator = [self.seed, data['Round Number'].count(),
                        self.solution,
                        created_sum, replicated_sum,
                        sent_sum, data['Messages Forwarded'].sum(),
                        delivered_sum, data['Messages Delivered Directly'].sum(),
                        data['Messages Received'].sum(), data['Messages TTL Expired'].sum(),
                        delivered_unique_sum, delivered_directly_unique_sum,
                        broadcasts_sent, data['Broadcast Messages Delivered'].sum(),
                        delivered_sum / sent_sum, delivered_unique_total / delivered_sum,
                        replicated_sum / created_sum,
                        data['Receiver Out Of Mem'].sum(), data['Particles Caught'].sum()
                        ]
        writer_round.writerow(csv_iterator)
        csv_file.close()
