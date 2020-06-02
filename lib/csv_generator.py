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
import numpy as np

class CsvParticleFile:
    def __init__(self, directory ):
        self.file_name = directory + '/particle.csv'
        file_exists = os.path.isfile(self.file_name)
        if not file_exists:
            self.csv_file = open(self.file_name, 'w', newline='')
            self.writer = csv.writer(self.csv_file)
            self.writer.writerow(['Particle ID', 'Particle Number',
                                  'Memory Read', 'Memory Write',
                                  'Particle Read', 'Particle Steps',
                                  'Particle Write', 'Tile Read',
                                  'Tile Write',
                                  'Steps NE (0)',
                                  'Steps E  (1)',
                                  'Steps SE (2)',
                                  'Steps SW (3)',
                                  'Steps W  (4)',
                                  'Steps NW (5)',
                                  'Success'
                                  ])

    def write_particle(self, particle):
        csv_iterator = [particle.csv_particle_writer.id, particle.csv_particle_writer.number,
                        particle.csv_particle_writer.memory_read, particle.csv_particle_writer.memory_write,
                        particle.csv_particle_writer.particle_read,
                        particle.csv_particle_writer.steps,
                        particle.csv_particle_writer.particle_write,
                        particle.csv_particle_writer.tile_read,
                        particle.csv_particle_writer.tile_write,
                        particle.csv_particle_writer.directional_steps[0],
                        particle.csv_particle_writer.directional_steps[1],
                        particle.csv_particle_writer.directional_steps[2],
                        particle.csv_particle_writer.directional_steps[3],
                        particle.csv_particle_writer.directional_steps[4],
                        particle.csv_particle_writer.directional_steps[5],
                        particle.csv_particle_writer.success]
        self.writer.writerow(csv_iterator)


class CsvParticleData:
    def __init__(self,  particle_id, particle_number):
        self.id = particle_id
        self.number=particle_number
        self.steps = 0
        self.particle_created=0
        self.particle_deleted=0
        self.particles_dropped = 0
        self.particle_read = 0
        self.particles_taken = 0
        self.particle_write = 0
        self.tile_created = 0
        self.tile_deleted = 0
        self.tile_read = 0
        self.tile_write = 0
        self.location_read = 0
        self.location_write = 0
        self.location_created = 0
        self.location_deleted = 0
        self.memory_read = 0
        self.memory_write = 0
        self.tiles_taken = 0
        self.tiles_dropped = 0
        self.success=0
        self.directional_steps = [0, 0, 0, 0, 0, 0]


    def write_particle(self, steps= 0, particle_read=0, particle_created=0, particle_deleted=0, particles_dropped=0,
                       particles_taken=0,
                       particle_write=0, tile_created=0, tile_deleted=0, tile_read=0, tile_write=0, location_read=0,
                       location_write=0, location_created=0, location_deleted=0, memory_read=0, memory_write=0,
                        tiles_taken = 0, tiles_dropped = 0, success=0):
        self.steps = self.steps + steps
        self.particle_created=self.particle_created+particle_created
        self.particle_deleted=self.particle_deleted+particle_deleted
        self.particles_dropped = self.particles_dropped + particles_dropped
        self.particles_taken = self.particles_taken + particles_taken
        self.particle_read=self.particle_read+particle_read
        self.particle_write=self.particle_write+particle_write
        self.tile_created=self.tile_created+tile_created
        self.tile_deleted=self.tile_deleted+tile_deleted
        self.tile_read=self.tile_read+tile_read
        self.tile_write=self.tile_write+tile_write
        self.location_read=self.location_read+location_read
        self.location_write=self.location_write+location_write
        self.location_created=self.location_created+location_created
        self.location_deleted=self.location_deleted+location_deleted
        self.memory_read=self.memory_read+memory_read
        self.memory_write=self.memory_write+memory_write
        self.tiles_taken = self.tiles_taken + tiles_taken
        self.tiles_dropped = self.tiles_dropped + tiles_dropped
        self.success = self.success+success


    def write_directional_metrics(self, dir=0):
        if 0 <= dir < 6:
            self.directional_steps[dir] = self.directional_steps[dir] + 1


class CsvRoundData:
    def __init__(self, sim, task=0, scenario=0, solution=0, seed=20,  particle_num=0, tiles_num=0, locations_num=0,
                 steps=0,  directory="outputs/"):
        self.sim = sim

        self.task = task
        self.scenario = scenario
        self.solution = solution
        self.actual_round=sim.get_actual_round()
        self.seed = seed
        self.steps  = steps
        self.steps_sum = steps
        self.particle_created=0
        self.particle_deleted=0
        self.particle_num = particle_num
        self.particle_read = 0
        self.particle_write = 0
        self.tile_created = 0
        self.tile_deleted = 0
        self.tile_num = tiles_num
        self.tile_read = 0
        self.tile_write = 0
        self.locations_num = locations_num
        self.location_read = 0
        self.location_write = 0
        self.location_created = 0
        self.location_deleted = 0
        self.memory_read = 0
        self.memory_write = 0
        self.particle_created_sum = 0
        self.particle_deleted_sum = 0
        self.particle_read_sum = 0
        self.particle_write_sum = 0
        self.particles_taken = 0
        self.particles_dropped = 0
        self.particles_taken_sum = 0
        self.particles_dropped_sum = 0
        self.tile_created_sum = 0
        self.tile_deleted_sum = 0
        self.tile_read_sum = 0
        self.tile_write_sum = 0
        self.location_read_sum = 0
        self.location_write_sum = 0
        self.location_created_sum = 0
        self.location_deleted_sum = 0
        self.memory_read_sum = 0
        self.memory_write_sum = 0
        self.success_round = None
        self.success_counter = 0
        self.tiles_taken = 0
        self.tiles_dropped = 0
        self.tiles_taken_sum = 0
        self.tiles_dropped_sum = 0
        self.directional_metrics_sum = [0, 0, 0, 0, 0, 0]
        self.directional_metrics = [0, 0, 0, 0, 0, 0]
        self.goal_first_tile = -1
        self.goal_half_of_tiles = -1
        self.goal_all_tiles = -1
        self.directory = directory
        self.file_name = directory + '/rounds.csv'
        self.csv_file = open(self.file_name, 'w', newline='')
        self.writer_round = csv.writer(self.csv_file)
        self.writer_round.writerow(['',
                                     'scenario', 'solution', 'Seed', 'Round Number',
                                    'Success Counter', 'Success Round',
                                    'Particle Counter',
                                    'Particles Created', 'Particles Created Sum',
                                    'Particles Deleted', 'Particles Deleted Sum',
                                    'Particles Dropped', 'Particles Dropped Sum',
                                    'Particle Read', 'Particle Read Sum',
                                    'Particle Steps', 'Particle Steps Sum',
                                    'Particles Taken', 'Particles Taken Sum',
                                    'Particle Write', 'Particle Write Sum',
                                    'Memory Read', 'Memory Read Sum',
                                    'Memory Write', 'Memory Write Sum',
                                    'Location Counter',
                                    'Location Created', 'Location Created Sum',
                                    'Location Deleted', 'Location Deleted Sum',
                                    'Location Read', 'Location Read Sum',
                                    'Location Write', 'Location Write Sum',
                                    'Tile Counter',
                                    'Tiles Created', 'Tiles Created Sum',
                                    'Tiles Deleted', 'Tiles Deleted Sum',
                                    'Tiles Dropped', 'Tiles Dropped Sum',
                                    'Tile Read', 'Tile Read Sum',
                                    'Tiles Taken', 'Tiles Taken Sum',
                                    'Tile Write', 'Tile Write Sum',
                                    'Steps NE (0)', 'Steps NE Sum (0)',
                                    'Steps E  (1)', 'Steps E  Sum (1)',
                                    'Steps SE (2)', 'Steps SE Sum (2)',
                                    'Steps SW (3)', 'Steps WS Sum (3)',
                                    'Steps W  (4)', 'Steps W  Sum (4)',
                                    'Steps NW (5)', 'Steps NW Sum (5)'
                                    ])

    def update_particle_num (self, particle):
        self.particle_num = particle

    def update_tiles_num (self, tile):
        self.tile_num = tile

    def update_locations_num(self, act_locations_num):
        self.locations_num = act_locations_num

    def success(self):
        self.success_counter=self.success_counter+1

    def update_metrics(self, steps = 0,
                        particle_read = 0, tile_read = 0, location_read = 0, memory_read = 0,
                        particle_write = 0, tile_write = 0, location_write = 0, memory_write = 0,
                        particle_created=0, tile_created=0, location_created=0,
                        particle_deleted=0, tile_deleted=0, location_deleted=0, tiles_taken=0, tiles_dropped=0,
                        particles_taken=0, particles_dropped=0, directional_metrics=[]):
        logging.debug("CSV: Starting writing_rounds")
        self.location_created_sum = self.location_created_sum + location_created
        self.location_deleted_sum = self.location_deleted_sum + location_deleted
        self.location_read_sum = self.location_read_sum + location_read
        self.location_write_sum = self.location_write_sum + location_write
        self.particle_created_sum = self.particle_created_sum + particle_created
        self.particle_deleted_sum = self.particle_deleted_sum + particle_deleted
        self.particle_read_sum = self.particle_read_sum + particle_read
        self.steps_sum = self.steps_sum + steps
        self.particle_write_sum = self.particle_write_sum + particle_write
        self.memory_write_sum = self.memory_write_sum + memory_write
        self.memory_read_sum = self.memory_read_sum + memory_read
        self.tile_created_sum = self.tile_created_sum + tile_created
        self.tile_deleted_sum = self.tile_deleted_sum + tile_deleted
        self.tiles_dropped_sum = self.tiles_dropped_sum + tiles_dropped
        self.tile_read_sum = self.tile_read_sum + tile_read
        self.tiles_taken_sum = self.tiles_taken_sum + tiles_taken
        self.tile_write_sum = self.tile_write_sum + tile_write
        self.particles_taken_sum = self.particles_taken_sum + particles_taken
        self.particles_dropped_sum = self.particles_dropped_sum + particles_dropped
        if len(directional_metrics) == 6:
            self.directional_metrics_sum[0] = self.directional_metrics_sum[0] + directional_metrics[0]
            self.directional_metrics_sum[1] = self.directional_metrics_sum[1] + directional_metrics[1]
            self.directional_metrics_sum[2] = self.directional_metrics_sum[2] + directional_metrics[2]
            self.directional_metrics_sum[3] = self.directional_metrics_sum[3] + directional_metrics[3]
            self.directional_metrics_sum[4] = self.directional_metrics_sum[4] + directional_metrics[4]
            self.directional_metrics_sum[5] = self.directional_metrics_sum[5] + directional_metrics[5]

        if self.actual_round == self.sim.get_actual_round():
            self.steps = self.steps + steps
            self.particle_read = self.particle_read + particle_read
            self.tile_read = self.tile_read + tile_read
            self.location_read = self.location_read + location_read
            self.memory_read = self.memory_read + memory_read
            self.particle_write = self.particle_write + particle_write
            self.tile_write = self.tile_write + tile_write
            self.location_write = self.location_write + location_write
            self.memory_write = self.memory_write + memory_write
            self.particle_created = self.particle_created + particle_created
            self.tile_created = self.tile_created + tile_created
            self.location_created = self.location_created + location_created
            self.particle_deleted = self.particle_deleted + particle_deleted
            self.tile_deleted = self.tile_deleted + tile_deleted
            self.location_deleted = self.location_deleted + location_deleted
            self.tiles_dropped = self.tiles_dropped + tiles_dropped
            self.tiles_taken = self.tiles_taken + tiles_taken
            self.particles_taken= self.particles_taken + particles_taken
            self.particles_dropped = self.particles_dropped + particles_dropped
            if len(directional_metrics) == 6:
                self.directional_metrics[0] = self.directional_metrics[0] + directional_metrics[0]
                self.directional_metrics[1] = self.directional_metrics[1] + directional_metrics[1]
                self.directional_metrics[2] = self.directional_metrics[2] + directional_metrics[2]
                self.directional_metrics[3] = self.directional_metrics[3] + directional_metrics[3]
                self.directional_metrics[4] = self.directional_metrics[4] + directional_metrics[4]
                self.directional_metrics[5] = self.directional_metrics[5] + directional_metrics[5]
        elif self.actual_round !=self.sim.get_actual_round():
            self.actual_round = self.sim.get_actual_round()
            self.steps = steps
            self.particle_read = particle_read
            self.tile_read = tile_read
            self.location_read = location_read
            self.memory_read = memory_read
            self.particle_write = particle_write
            self.tile_write = tile_write
            self.location_write = location_write
            self.memory_write = memory_write
            self.particle_created = particle_created
            self.tile_created = tile_created
            self.location_created = location_created
            self.particle_deleted = particle_deleted
            self.tile_deleted = tile_deleted
            self.location_deleted = location_deleted
            self.tiles_dropped = tiles_dropped
            self.tiles_taken = tiles_taken
            self.particles_taken = particles_taken
            self.particles_dropped = particles_dropped
            if len(directional_metrics) == 6:
                self.directional_metrics = directional_metrics
        logging.debug("CSV: Ending writing_rounds")

    def update_goals(self, goalnum, value):
        if goalnum == 0:
            self.goal_first_tile = value
        elif goalnum == 1:
            self.goal_half_of_tiles = value
        elif goalnum == 2:
            self.goal_all_tiles = value

    def next_line(self, round):
        csv_iterator = ['', self.scenario, self.solution, self.seed, round,
                        self.success_counter, self.success_round,
                        self.particle_num, self.particle_created, self.particle_created_sum,
                        self.particle_deleted, self.particle_deleted_sum,
                        self.particles_dropped, self.particles_dropped_sum,
                        self.particle_read, self.particle_read_sum,
                        self.steps, self.steps_sum,
                        self.particles_taken, self.particles_taken_sum,
                        self.particle_write, self.particle_write_sum,
                        self.memory_read, self.memory_read_sum, self.memory_write, self.memory_write_sum,
                        self.locations_num, self.location_created, self.location_created_sum,
                        self.location_deleted, self.location_deleted_sum,
                        self.location_read, self.location_read_sum,
                        self.location_write, self.location_write_sum,
                        self.tile_num, self.tile_created, self.tile_created_sum,
                        self.tile_deleted, self.tile_deleted_sum, self.tiles_dropped, self.tiles_dropped_sum,
                        self.tile_read, self.tile_read_sum, self.tiles_taken, self.tiles_taken_sum,
                        self.tile_write, self.tile_write_sum,
                        self.directional_metrics[0], self.directional_metrics_sum[0],
                        self.directional_metrics[1], self.directional_metrics_sum[1],
                        self.directional_metrics[2], self.directional_metrics_sum[2],
                        self.directional_metrics[3], self.directional_metrics_sum[3],
                        self.directional_metrics[4], self.directional_metrics_sum[4],
                        self.directional_metrics[5], self.directional_metrics_sum[5]
                        ]
        self.writer_round.writerow(csv_iterator)
        self.actual_round = round
        self.steps=0
        self.particle_read=0
        self.tile_read=0
        self.location_read=0
        self.memory_read=0
        self.particle_write=0
        self.tile_write=0
        self.location_write=0
        self.memory_write=0
        self.particle_created = 0
        self.tile_created = 0
        self.location_created = 0
        self.particle_deleted = 0
        self.tile_deleted = 0
        self.location_deleted = 0
        self.tiles_dropped = 0
        self.tiles_taken = 0
        self.success_round = None
        self.success_counter = 0
        self.particles_taken = 0
        self.particles_dropped = 0
        self.directional_metrics = [0, 0, 0, 0, 0, 0]

    def aggregate_metrics(self):
        self.csv_file.close()
        data = pd.read_csv(self.file_name)
        file_name = self.directory+"/aggregate_rounds.csv"
        csv_file = open(file_name, 'w', newline='')
        writer_round = csv.writer(csv_file)
        """Average Min Max for all other metrics"""
        writer_round.writerow([ 'Seed', 'Rounds Total',
                                'Success',
                                'Particle Counter',

                                'Particle Steps Total',  'Particle Steps Avg',
                                'Particle Steps Min', 'Particle Steps Max',
                                'Steps NE (0)', 'Steps E  (1)', 'Steps SE (2)',
                                'Steps SW (3)', 'Steps W  (4)', 'Steps NW (5)',
                                'FirstHit', 'HalfLine', 'FullLine'
                               ])

        csv_interator = [ self.seed, data['Round Number'].count(),

                         data['Success Counter'].sum(),
                         self.particle_num,
                           data['Particle Steps'].sum(), data['Particle Steps'].mean(),
                         data['Particle Steps'].min(), data['Particle Steps'].max(),


                         data['Steps NE (0)'].sum(), data['Steps E  (1)'].sum(), data['Steps SE (2)'].sum(),
                         data['Steps SW (3)'].sum(), data['Steps W  (4)'].sum(), data['Steps NW (5)'].sum(),
                         self.goal_first_tile, self.goal_half_of_tiles, self.goal_all_tiles
                         ]

        writer_round.writerow(csv_interator)
        csv_file.close()


def changing(directory,  particle_num):

    data = pd.read_csv( directory+"/aggregate_rounds.csv")
    file_name = directory+"/changed.csv"
    data= data.replace(5000, np.NaN)
    # data.to_csv(directory+'/test.csv')
    # for val in range(len(data)):
    #     if data['Rounds Total'].values[val] ==  5000:
    #         print ("Found ", data['Rounds Total'].values[val])
    #         data['Rounds Total'].values[val]=1
    # # csv_file = open(file_name, 'w', newline='')
    # writer_round = csv.writer(csv_file)
    """Average Min Max for all other metrics"""
    #writer_round.writerow(
    data.to_csv(directory + '/test.csv')
def all_aggregate_metrics(directory,  particle_num):

    data = pd.read_csv( directory+"/aggregate_rounds.csv")
    file_name = directory+"/all_aggregate_rounds.csv"
    csv_file = open(file_name, 'w', newline='')
    writer_round = csv.writer(csv_file)
    """Average Min Max for all other metrics"""
    writer_round.writerow([
                             'Particle Counter',
                           'Rounds Avg',
                           'Rounds Std','Rounds Sem','Rounds Mad', "AVG per Particle", "SD per Particle","Sem per Particle","Mad per Particle",

                            'Rounds Max',
                            'Rounds Min',
                            'Particle Steps Total',  'Particle Steps Avg', 'Particle Steps Std',
                            'Particle Steps Min', 'Particle Steps Max',

                           'Success Rate Sum', 'Success Avg',
                           'Success Rate Std', 'Success Rate Min', 'Success Rate Max'

    ])


    csv_interator = [particle_num,
                     data['Rounds Total'].mean(),
                     data['Rounds Total'].std(),
                     data['Rounds Total'].sem(),
                     data['Rounds Total'].mad(),
                     data['Rounds Total'].mean()/particle_num,
                     data['Rounds Total'].std() / particle_num,
                     data['Rounds Total'].sem()/particle_num,
                     data['Rounds Total'].mad() / particle_num,
                     data['Rounds Total'].min(),
                     data['Rounds Total'].max(),

                     data['Particle Steps Total'].sum(), data['Particle Steps Total'].mean(),
                     data['Particle Steps Total'].std(),
                     data['Particle Steps Total'].min(), data['Particle Steps Total'].max(),



                     data['Success'].sum(),
                     data['Success'].mean(),

                     data['Success'].std(), data['Success'].min(),
                     data['Success'].max(),
                     ]




    writer_round.writerow(csv_interator)
    csv_file.close()


def get_change(current, previous):
    if current == previous:
        return 100.0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return 0

def da():
    df = pd.read_csv("./outputs/multiple/charged/all_aggregates.csv")


    bla = { "Particle Numbers": df['Particle Counter'].values, "PCAR": abs(df['Rounds Avg'].pct_change())*100,
            "PCEAR":abs(df['Rounds Std'].pct_change()) *100, "PCARPA": abs(df['AVG per Particle'].pct_change())*100,
            "PCAERPA": abs(df['SD per Particle'].pct_change())*100, }

    d= pd.DataFrame(bla)
    d.to_csv("./outputs/multiple/charged/new.csv")
    #csv_file.close()