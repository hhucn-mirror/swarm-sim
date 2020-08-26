import csv
import os


class CsvParticleFile:
    """
    Collects information about particles.
    """

    def __init__(self, directory):
        """
        Constructor. Initializes csv file in :param directory.
        :param directory:
        """
        self.file_name = directory + '/particle.csv'
        file_exists = os.path.isfile(self.file_name)
        if not file_exists:
            self.csv_file = open(self.file_name, 'w', newline='')
            self.writer = csv.writer(self.csv_file)
            self.writer.writerow(['Particle ID', 'Particle Number', 'Particle Steps',
                                  'Messages Sent', 'Messages Forwarded', 'Messages Delivered',
                                  'Messages Delivered Directly', 'Messages Received',
                                  'Broadcasts Sent', 'Broadcasts Delivered',
                                  'Messages TTL Expired', 'Out of Memory'
                                  ])

    def write_particle(self, particle):
        """
        Writes the particle
        :param particle:
        :return: None
        """
        csv_iterator = [particle.csv_particle_writer.id, particle.csv_particle_writer.number,
                        particle.csv_particle_writer.steps,
                        particle.csv_particle_writer.messages_sent, particle.csv_particle_writer.messages_forwarded,
                        particle.csv_particle_writer.messages_delivered,
                        particle.csv_particle_writer.messages_delivered_directly,
                        particle.csv_particle_writer.messages_received,
                        particle.csv_particle_writer.broadcasts_sent,
                        particle.csv_particle_writer.broadcasts_delivered,
                        particle.csv_particle_writer.messages_ttl_expired,
                        particle.csv_particle_writer.out_of_mem,
                        ]
        self.writer.writerow(csv_iterator)


class CsvParticleData:
    """
    Collects information about a specific particle.
    """

    def __init__(self, particle_id, particle_number):
        """
        Constructor. Initializes identification using particle id and particle number.
        :param particle_id: particle id number
        :param particle_number: particle number
        """
        self.id = particle_id
        self.number = particle_number
        self.steps = 0
        self.particle_write = 0
        self.messages_sent = 0
        self.messages_forwarded = 0
        self.messages_delivered = 0
        self.messages_delivered_directly = 0
        self.messages_received = 0
        self.broadcasts_sent = 0
        self.broadcasts_delivered = 0
        self.messages_ttl_expired = 0
        self.out_of_mem = 0

    def write_particle(self, steps=0, particle_write=0, messages_sent=0, messages_forwarded=0,
                       messages_delivered=0, messages_delivered_directly=0, messages_received=0,
                       broadcasts_sent=0, broadcasts_delivered=0,
                       messages_ttl_expired=0, out_of_mem=0):
        """
        Updates particle metrics.
        :param steps: int
        :param particle_write: int
        :param messages_sent: int
        :param messages_forwarded: int
        :param messages_delivered: int
        :param messages_delivered_directly:
        :param messages_received: int
        :param broadcasts_sent: int
        :param broadcasts_delivered: int
        :param messages_ttl_expired: int
        :param out_of_mem: int
        :return: None
        """
        self.steps += steps
        self.particle_write += particle_write
        self.messages_sent += messages_sent
        self.messages_forwarded += messages_forwarded
        self.messages_delivered += messages_delivered
        self.messages_delivered_directly += messages_delivered_directly
        self.messages_received += messages_received
        self.broadcasts_sent += broadcasts_sent
        self.broadcasts_delivered += broadcasts_delivered
        self.messages_ttl_expired += messages_ttl_expired
        self.out_of_mem += out_of_mem
