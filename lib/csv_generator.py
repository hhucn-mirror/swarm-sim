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
    def __init__(self, directory ):
        self.file_name = directory + '/particle.csv'
        file_exists = os.path.isfile(self.file_name)
        if not file_exists:
            self.csv_file = open(self.file_name, 'w', newline='')
            self.writer = csv.writer(self.csv_file)
            self.writer.writerow(['Particle ID', 'Particle Number',
                                  'Memory Read', 'Memory Write',
                                  'Particle Read',
                                   'Particle Write',
                                    'Success'
                                  ])
    def write_particle(self, particle):
        csv_iterator = [particle.csv_particle_writer.id,
                        particle.csv_particle_writer.number,
                        particle.csv_particle_writer.memory_read,
                        particle.csv_particle_writer.memory_write,
                        particle.csv_particle_writer.particle_write,]
        self.writer.writerow(csv_iterator)


class CsvParticleData:
    def __init__(self,  particle_id, particle_number):
        self.id = particle_id
        self.number=particle_number
        self.particle_read = 0
        self.particle_write = 0
        self.memory_read = 0
        self.memory_write = 0


    def write_particle(self,  particle_read=0,
                       particle_write=0,
                       memory_read=0, memory_write=0):
        self.particle_read=self.particle_read+particle_read
        self.particle_write=self.particle_write+particle_write
        self.memory_read=self.memory_read+memory_read
        self.memory_write=self.memory_write+memory_write






class CsvRoundData:
    def __init__(self, sim, task=0, solution=0, seed=20,  particle_num=0,
                   directory="outputs/"):
        self.sim = sim
        self.task = task
        self.solution = solution
        self.actual_round=sim.get_actual_round()
        self.seed = seed
        self.particle_num = particle_num
        self.particle_read = 0
        self.particle_write = 0
        self.memory_read = 0
        self.memory_write = 0
        self.particle_read_sum = 0
        self.particle_write_sum = 0
        self.memory_read_sum = 0
        self.memory_write_sum = 0
        self.directory = directory
        self.file_name = directory + '/rounds.csv'
        self.csv_file = open(self.file_name, 'w', newline='')
        self.writer_round = csv.writer(self.csv_file)
        self.writer_round.writerow(['',
                                    'Round Number', 'Seed','solution',
                                    'Memory Read', 'Memory Read Sum',
                                    'Memory Write', 'Memory Write Sum',
                                    'Particle Counter',
                                    'Particle Read', 'Particle Read Sum',
                                    'Particle Write', 'Particle Write Sum',
                                    'Density','Density Radius',
                                    'Calculated directions','Calculated distances','memreads',
                                    'safe','critical','uncomfortable'
                                    ])

    def update_particle_num (self, particle):
        self.particle_num = particle




    def update_metrics(self,
                        particle_read = 0,  memory_read = 0,
                        particle_write = 0, memory_write = 0,
                        ):
        logging.debug("CSV: Starting writing_rounds")
        self.particle_read_sum = self.particle_read_sum + particle_read
        self.particle_write_sum = self.particle_write_sum + particle_write
        self.memory_write_sum = self.memory_write_sum + memory_write
        self.memory_read_sum = self.memory_read_sum + memory_read

        if self.actual_round == self.sim.get_actual_round():
            self.particle_read = self.particle_read + particle_read
            self.memory_read = self.memory_read + memory_read
            self.particle_write = self.particle_write + particle_write
            self.memory_write = self.memory_write + memory_write
            self.density=self.sim.get_density()
            self.densityRadius=self.sim.get__densityRadius()
            self.calculated_dir=self.sim.get_calculated_dir()
            self.calculated_dis=self.sim.get_calculated_dis()
            self.memory_reads=self.sim.get_mems()
            self.safe=self.sim.get_safe()
            self.critical = self.sim.get_critical()
            self.uncomfortable = self.sim.get_uncomfortable()
        elif self.actual_round !=self.sim.get_actual_round():
            self.actual_round = self.sim.get_actual_round()
            self.particle_read = particle_read
            self.memory_read = memory_read
            self.particle_write = particle_write
            self.memory_write = memory_write
            self.density = self.sim.get_density()
            self.densityRadius=self.sim.get__densityRadius()
            self.calculated_dir=self.sim.get_calculated_dir()
            self.calculated_dis=self.sim.get_calculated_dis()
            self.memory_reads = self.sim.get_mems()
            self.safe = self.sim.get_safe()
            self.critical = self.sim.get_critical()
            self.uncomfortable = self.sim.get_uncomfortable()
        logging.debug("CSV: Ending writing_rounds")

    def next_line(self, round):
        csv_iterator = ['',round, self.seed, self.solution,
                        self.memory_read, self.memory_read_sum, self.memory_write, self.memory_write_sum,
                        self.particle_num,
                        self.particle_read, self.particle_read_sum,
                        self.particle_write, self.particle_write_sum,
                        self.density,
                        self.densityRadius,
                        self.calculated_dir,
                        self.calculated_dis,
                        self.memory_reads,
                        self.safe,
                        self.critical,
                        self.uncomfortable]
        self.writer_round.writerow(csv_iterator)
        self.actual_round = round
        self.particle_read=0
        self.memory_read=0
        self.particle_write=0
        self.memory_write=0

    def aggregate_metrics(self):
        self.csv_file.close()
        data = pd.read_csv(self.file_name)
        file_name = self.directory+"/aggregate_rounds.csv"
        csv_file = open(file_name, 'w', newline='')
        writer_round = csv.writer(csv_file)
        """Average Min Max for all other metrics"""
        writer_round.writerow(['Seed', 'Rounds Total',
                                'Solution', 'Particle Counter',
                                'Success Rate',
                                'Particle Read Sum', 'Particle Read Avg', 'Particle Read Min', 'Particle Read Max',
                                'Particle Write Sum', 'Particle Write Avg', 'Particle Write Min', 'Particle Write Max',
                                'Memory Read Sum', 'Memory Read Avg', 'Memory Read Min', 'Memory Read Max',
                                'Memory Write Sum', 'Memory Write Avg', 'Memory Write Min', 'Memory Write Max',
                                'Density Avg', 'Density Min','Density Max','Max-Min Density', 'Density Radius',
                               'calculated dir sum','calculated dir avg','calculated dir min','calculated dir max',
                               'calculated distance sum', 'calculated distance avg', 'calculated distance min', 'calculated distance max',
                               'memory reads sum', 'memory reads average',
                               'safe sum', 'safe average',
                               'critical sum', 'critical average',
                               'uncomp sum', 'uncomp average'])

        csv_interator = [self.seed, data['Round Number'].count(),

                         self.solution, self.particle_num,
                         data['Round Number'].count()*100/self.sim.get_max_round(),


                         data['Particle Read'].sum(), data['Particle Read'].mean(),data['Particle Read'].min(),
                         data['Particle Read'].max(),


                         data['Particle Write'].sum(), data['Particle Write'].mean(), data['Particle Write'].min(),
                         data['Particle Write'].max(),

                         data['Memory Read'].sum(), data['Memory Read'].mean(), data['Memory Read'].min(),
                         data['Memory Read'].max(),

                         data['Memory Write'].sum(), data['Memory Write'].mean(), data['Memory Write'].min(),
                         data['Memory Write'].max(),

                         data['Density'].mean(),data['Density'].min(),data['Density'].max(),
                         data['Density'].max()-data['Density'].min(),
                         data['Density Radius'].mean(),

                         data['Calculated directions'].sum(),data['Calculated directions'].mean(),
                         data['Calculated directions'].min(),data['Calculated directions'].max(),

                         data['Calculated distances'].sum(), data['Calculated distances'].mean(),
                         data['Calculated distances'].min(), data['Calculated distances'].max(),

                         data['memreads'].sum() ,data['memreads'].mean(),

                         data['safe'].sum(), data['safe'].mean(),
                         data['critical'].sum(),data['critical'].mean(),
                         data['uncomfortable'].sum(),data['uncomfortable'].mean()
                         ]



        writer_round.writerow(csv_interator)
        csv_file.close()


