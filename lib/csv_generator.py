"""

TODO:
1- Order the names based on particles, locations, and tiles and alphabetic
2- A new column called round_success
3- On demand extenstion of the metrics.


"""


import csv
import pandas as pd
import logging
import os


class CsvParticleFile:
    def __init__(self, directory):
        self.file_name = directory + '/particle.csv'
        file_exists = os.path.isfile(self.file_name)
        if not file_exists:
            self.csv_file = open(self.file_name, 'w', newline='')
            self.writer = csv.writer(self.csv_file)
            self.writer.writerow(['Particle ID', 'Particle Number', 'Search Algorithm',
                                  'Location Created', 'Location Deleted',
                                  'Particle Read', 'Particle Write', 'Particle Steps', 'Task Success Round'])

    def write_particle(self, particle):
        csv_iterator = [particle.csv_particle_writer.id, particle.csv_particle_writer.number,
                        particle.csv_particle_writer.search_algorithm,
                        particle.csv_particle_writer.location_created, particle.csv_particle_writer.location_deleted,
                        particle.csv_particle_writer.particle_read,
                        particle.csv_particle_writer.particle_write,
                        particle.csv_particle_writer.steps,
                        particle.csv_particle_writer.success_round]
        self.writer.writerow(csv_iterator)


class CsvParticleData:
    def __init__(self,  particle_id, particle_number):
        self.id = particle_id
        self.number=particle_number
        self.steps = 0
        self.particle_read = 0
        self.particle_write = 0
        self.location_created = 0
        self.location_deleted = 0
        self.success=0
        self.success_round = None
        self.search_algorithm = None

    def write_particle(self, steps= 0, particle_read=0,
                       particle_write=0, location_created=0, location_deleted=0, memory_read=0, memory_write=0,
                       success=0):

        self.steps = self.steps + steps
        self.particle_read=self.particle_read+particle_read
        self.particle_write=self.particle_write+particle_write
        self.location_created=self.location_created+location_created
        self.location_deleted=self.location_deleted+location_deleted
        self.success = self.success+success

    def task_success(self):
        self.success=self.success+1

    def set_task_success_round(self, success_round):
        self.success_round = success_round

    def set_search_algorithm(self, search_algorithm):
        if search_algorithm == -1:
            self.search_algorithm = 'DFS'
        elif search_algorithm == 0:
            self.search_algorithm = 'BFS'


class CsvRoundData:
    def __init__(self, sim, task=0, scenario=0, solution=0, seed=20, tiles_num=0,  particle_num=0, locations_num=0,
                 steps=0,  directory="outputs/"):
        self.sim = sim
        self.task = task
        self.scenario = scenario
        self.solution = solution
        self.actual_round=sim.get_actual_round()
        self.seed = seed
        self.steps = steps
        self.steps_sum = steps
        self.particle_num = particle_num
        self.particle_read = 0
        self.particle_write = 0
        self.locations_num = locations_num
        self.location_created = 0
        self.location_deleted = 0
        self.particle_read_sum = 0
        self.particle_write_sum = 0
        self.location_created_sum = 0
        self.location_deleted_sum = 0
        self.success_round = 0
        self.all_marked_round = None
        self.search_algorithm = None
        self.start_communication_round = 0
        self.communication_frequency = 0
        self.communication_range = 0
        self.success_counter = 0
        self.directory = directory
        self.file_name = directory + '/rounds.csv'
        self.csv_file = open(self.file_name, 'w', newline='')
        self.writer_round = csv.writer(self.csv_file)
        self.writer_round.writerow([
                                    'scenario', 'solution', 'Seed', 'Round Number',
                                    'Successful Termination', 'Successful Marking',
                                    'Particle Counter',
                                    'Particle Steps', 'Particle Steps Sum',
                                    'Particle Read', 'Particle Read Sum',
                                    'Particle Write', 'Particle Write Sum',
                                    'Location Created', 'Location Created Sum',
                                    'Location Deleted', 'Location Deleted Sum',
                                    ])

    def update_particle_num (self, particle):
        self.particle_num = particle

    def update_locations_num(self, act_locations_num):
        self.locations_num = act_locations_num

    def success(self):
        self.success_counter = 1

    def marking_success(self):
        self.success_round = 1

    def set_marking_success_round(self, actual_round):
        self.all_marked_round = actual_round

    def set_start_communication_round(self, start_communication_round):
        self.start_communication_round = start_communication_round

    def set_communication_frequency(self, communication_frequency):
        self.communication_frequency = communication_frequency

    def set_communication_range(self, communication_range):
        self.communication_range = communication_range

    def set_search_algorithm(self, search_algorithm):
        if search_algorithm == 0:
            self.search_algorithm = 'BFS'
        elif search_algorithm == 1:
            self.search_algorithm = 'DFS'
        elif search_algorithm == 2:
            self.search_algorithm = 'MIXED'

    def update_metrics(self, steps=0, particle_read=0, memory_read=0, particle_write=0, memory_write=0,
                       location_created=0, location_deleted=0):
        logging.debug("CSV: Starting writing_rounds")
        self.location_created_sum = self.location_created_sum + location_created
        self.location_deleted_sum = self.location_deleted_sum + location_deleted
        self.steps_sum = self.steps_sum + steps
        self.particle_read_sum = self.particle_read_sum + particle_read
        self.particle_write_sum = self.particle_write_sum + particle_write

        if self.actual_round == self.sim.get_actual_round():
            self.steps = self.steps + steps
            self.particle_read = self.particle_read + particle_read
            self.particle_write = self.particle_write + particle_write
            self.location_created = self.location_created + location_created
            self.location_deleted = self.location_deleted + location_deleted

        elif self.actual_round != self.sim.get_actual_round():
            self.actual_round = self.sim.get_actual_round()
            self.steps = steps
            self.particle_read = particle_read
            self.particle_write = particle_write
            self.location_created = location_created
            self.location_deleted = location_deleted

        logging.debug("CSV: Ending writing_rounds")

    def next_line(self, round):
        csv_iterator = [self.scenario, self.solution, self.seed, round,
                        self.success_counter, self.success_round,
                        self.particle_num,
                        self.steps, self.steps_sum,
                        self.particle_read, self.particle_read_sum,
                        self.particle_write, self.particle_write_sum,
                        self.location_created, self.location_created_sum,
                        self.location_deleted, self.location_deleted_sum]

        self.writer_round.writerow(csv_iterator)
        self.actual_round = round
        self.steps = 0
        self.particle_read = 0
        self.particle_write = 0
        self.location_created = 0
        self.location_deleted = 0
        self.success_round = 0
        self.success_counter = 0

    def aggregate_metrics(self):
        self.csv_file.close()
        data = pd.read_csv(self.file_name)
        file_name = self.directory+"/aggregate_rounds.csv"
        csv_file = open(file_name, 'w', newline='')
        writer_round = csv.writer(csv_file)
        """Average Min Max for all other metrics"""
        writer_round.writerow(['Scenario', 'Solution', 'Seed', 'Search Algorithm', 'Successful Termination Round',
                                'Successful Marking Round',
                                'Start Communication round', 'Communication Frequency', 'Communication Range',
                                'Particle Counter',
                                'Particle Steps Total', 'Particle Steps Avg',
                                'Particle Steps Min', 'Particle Steps Max',
                                'Particle Read Sum', 'Particle Read Avg', 'Particle Read Min', 'Particle Read Max',
                                'Particle Write Sum', 'Particle Write Avg', 'Particle Write Min', 'Particle Write Max',
                                'Location Created Sum', 'Location Created Avg',
                                'Location Created Min', 'Location Created Max',
                                'Location Deleted Sum', 'Location Deleted Avg',
                                'Location Deleted Min', 'Location Deleted Max',
                                ])

        csv_iterator = [self.scenario, self.solution, self.seed, self.search_algorithm, data['Round Number'].count(),
                        self.all_marked_round,

                        self.start_communication_round, self.communication_frequency, self.communication_range,

                        self.particle_num,

                        data['Particle Steps'].sum(), data['Particle Steps'].mean(),
                        data['Particle Steps'].min(), data['Particle Steps'].max(),

                        data['Particle Read'].sum(), data['Particle Read'].mean(), data['Particle Read'].min(),
                        data['Particle Read'].max(),

                        data['Particle Write'].sum(), data['Particle Write'].mean(), data['Particle Write'].min(),
                        data['Particle Write'].max(),

                        data['Location Created'].sum(), data['Location Created'].mean(),
                        data['Location Created'].min(), data['Location Created'].max(),

                        data['Location Deleted'].sum(), data['Location Deleted'].mean(),
                        data['Location Deleted'].min(), data['Location Deleted'].max()]

        writer_round.writerow(csv_iterator)
        csv_file.close()

    def all_aggregate_metrics(self):
        self.csv_file.close()
        data = pd.read_csv(self.file_name)
        file_name = self.directory+"/aggregate_rounds.csv"
        csv_file = open(file_name, 'w', newline='')
        writer_round = csv.writer(csv_file)
        """Average Min Max for all other metrics"""
        writer_round.writerow(['Scenario', 'Solution', 'Seed', 'Rounds Total',
                                'Particle Counter',
                                'Success Rate Sum', 'Success Ratio',
                                'Success Rate Avg', 'Success Rate Min', 'Success Rate Max',
                                'Success Round Min', 'Success Round Max',
                                'Particle Counter',
                                'Particle Steps Total', 'Particle Steps Avg',
                                'Particle Steps Min', 'Particle Steps Max',
                                'Particle Read Sum', 'Particle Read Avg', 'Particle Read Min', 'Particle Read Max',
                                'Particle Write Sum', 'Particle Write Avg', 'Particle Write Min', 'Particle Write Max',
                                'Location Created Sum', 'Location Created Avg',
                                'Location Created Min', 'Location Created Max',
                                'Location Deleted Sum', 'Location Deleted Avg',
                                'Location Deleted Min', 'Location Deleted Max'])

        csv_iterator = [self.scenario, self.solution, self.seed, data['Round Number'].count(),
                        self.particle_num,
                        data['Success Counter'].sum(),
                        data['Success Counter'].sum() / data['Round Number'].sum(),

                        data['Success Counter'].mean(), data['Success Counter'].min(),
                        data['Success Counter'].max(),

                        data['Success Round'].min(),
                        data['Success Round'].max(),

                        self.particle_num,

                        data['Particle Steps'].sum(), data['Particle Steps'].mean(),
                        data['Particle Steps'].min(), data['Particle Steps'].max(),

                        data['Particle Read'].sum(), data['Particle Read'].mean(), data['Particle Read'].min(),
                        data['Particle Read'].max(),

                        data['Particle Write'].sum(), data['Particle Write'].mean(), data['Particle Write'].min(),
                        data['Particle Write'].max(),

                        data['Location Created'].sum(), data['Location Created'].mean(),
                        data['Location Created'].min(), data['Location Created'].max(),

                        data['Location Deleted'].sum(), data['Location Deleted'].mean(),
                        data['Location Deleted'].min(), data['Location Deleted'].max()]

        writer_round.writerow(csv_iterator)
        csv_file.close()


class CsvParticleMovement:
    def __init__(self, sim, directory="outputs/", particle_num=0):
        self.sim = sim
        self.directory = directory
        self.file_name = directory + '/movement.csv'
        self.csv_file = open(self.file_name, 'w', newline='')
        self.writer_round = csv.writer(self.csv_file)
        self.row = ['Round Number']
        self.particle_num = particle_num
        for particle in range(1, particle_num + 1):
            self.row.append("Particle:" + str(particle) + " x")
            self.row.append("Particle:" + str(particle) + " y")
        self.writer_round.writerow(self.row)

    def update_all_particles(self, particle_list, round):
        csv_iterator = [round]
        particle_list.sort(key=lambda part: part.number)
        for particle in particle_list:
            csv_iterator.append(particle.coords[0])
            csv_iterator.append(particle.coords[1])
        self.writer_round.writerow(csv_iterator)



