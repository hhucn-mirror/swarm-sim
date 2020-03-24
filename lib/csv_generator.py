"""

TODO:
1- Order the names based on particles, locations, and tiles and transparencybetic
2- A new column called round_success
3- On demand extenstion of the metrics.


"""

import csv
import logging
import os

import pandas as pd
import numpy as np

class CsvParticleFile:
    def __init__(self, directory):
        self.file_name = directory + '/particle.csv'
        file_exists = os.path.isfile(self.file_name)
        if not file_exists:
            self.csv_file = open(self.file_name, 'w', newline='')
            self.writer = csv.writer(self.csv_file)
            self.writer.writerow(['Particle ID', 'Particle Number',
                                  'Particle Steps',
                                  'Particles Taken', 'Particles Dropped',
                                 'Success'
                                  ])

    def write_particle(self, particle):
        csv_iterator = [particle.csv_particle_writer.id, particle.csv_particle_writer.number,
                        particle.csv_particle_writer.steps, particle.csv_particle_writer.particles_taken,
                        particle.csv_particle_writer.particles_dropped,
                        particle.csv_particle_writer.particle_write, particle.csv_particle_writer.success]
        self.writer.writerow(csv_iterator)


class CsvParticleData:
    def __init__(self, particle_id, particle_number):
        self.id = particle_id
        self.number = particle_number
        self.steps = 0
        self.particle_created = 0
        self.particle_deleted = 0
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
        self.success = 0

    def write_particle(self, steps=0, particle_read=0, particle_created=0, particle_deleted=0, particles_dropped=0,
                       particles_taken=0,
                       particle_write=0, tile_created=0, tile_deleted=0, tile_read=0, tile_write=0, location_read=0,
                       location_write=0, location_created=0, location_deleted=0, memory_read=0, memory_write=0,
                       tiles_taken=0, tiles_dropped=0, success=0):
        self.steps = self.steps + steps
        self.particle_created = self.particle_created + particle_created
        self.particle_deleted = self.particle_deleted + particle_deleted
        self.particles_dropped = self.particles_dropped + particles_dropped
        self.particles_taken = self.particles_taken + particles_taken
        self.particle_read = self.particle_read + particle_read
        self.particle_write = self.particle_write + particle_write
        self.tile_created = self.tile_created + tile_created
        self.tile_deleted = self.tile_deleted + tile_deleted
        self.tile_read = self.tile_read + tile_read
        self.tile_write = self.tile_write + tile_write
        self.location_read = self.location_read + location_read
        self.location_write = self.location_write + location_write
        self.location_created = self.location_created + location_created
        self.location_deleted = self.location_deleted + location_deleted
        self.memory_read = self.memory_read + memory_read
        self.memory_write = self.memory_write + memory_write
        self.tiles_taken = self.tiles_taken + tiles_taken
        self.tiles_dropped = self.tiles_dropped + tiles_dropped
        self.success = self.success + success


class CsvRoundData:
    def __init__(self, world, task=0, scenario=0, solution=0, seed=20, directory="outputs/"):
        self.world = world
        self.task = task
        self.scenario = scenario
        self.solution = solution
        self.actual_round = 1
        self.seed = seed
        self.steps = 0
        self.steps_sum = 0
        self.particle_created = 0
        self.particle_deleted = 0
        self.particle_num = 0
        self.particle_read = 0
        self.particle_write = 0
        self.tile_created = 0
        self.tile_deleted = 0
        self.tile_num = 0
        self.tile_read = 0
        self.tile_write = 0
        self.locations_num = 0
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
        self.success_round = 0
        self.success_counter = 0
        self.tiles_taken = 0
        self.tiles_dropped = 0
        self.tiles_taken_sum = 0
        self.tiles_dropped_sum = 0
        self.directory = directory
        self.file_name = directory + '/rounds.csv'
        self.csv_file = open(self.file_name, 'w', newline='')
        self.writer_round = csv.writer(self.csv_file)
        self.coating_steps = np.nan
        self.cave_coating_steps = np.nan
        self.scanning_steps = np.nan
        self.taking_steps = np.nan
        self.cave_scanning_steps = np.nan
        self.to_tile_steps = np.nan
        self.leader_coating_steps = np.nan
        self.out_of_cave_steps = np.nan
        self.cave_pathing = np.nan
        self.finished = np.nan
        self.layer = np.nan
        self.valid = np.nan

        self.writer_round.writerow(['',
                                    'scenario', 'solution', 'Seed', 'Round Number',
                                    'Success Counter', 'Success Round',
                                    'Particle Counter',
                                    'Particles Dropped', 'Particles Dropped Sum',
                                    'Particle Steps', 'Particle Steps Sum',
                                    'Particles Taken', 'Particles Taken Sum',
                                    'Tile Counter', 'Coating', 'Cave Coating','Scanning',
                                    'Cave Scanning', 'Taking', 'To Tile', 'Leader Coating', 'Out of Cave',
                                    'Cave Pathing', 'Finished',  'Layer', 'Valid'
                                    ])

    def update_particle_num(self, particle):
        self.particle_num = particle

    def update_tiles_num(self, tile):
        self.tile_num = tile

    def update_locations_num(self, act_locations_num):
        self.locations_num = act_locations_num

    def success(self):
        self.success_round = 1
        self.success_counter = self.success_counter + self.success_round

    def update_coating(self):
        self.coating_steps =  1

    def update_cave_coating(self):
        self.cave_coating_steps =  1

    def update_scanning(self):
        self.scanning_steps =  1

    def update_cave_scanning(self):
        self.cave_scanning_steps =  1

    def update_taking(self):
        self.taking_steps =  1

    def update_to_tile(self):
        self.to_tile_steps =  1

    def update_out_of_cave(self):
        self.out_of_cave_steps =  1

    def update_leader_coating(self):
        self.leader_coating_steps =  1

    def update_cave_discovery(self):
        self.cave_pathing = 1

    def update_finished(self):
        self.finished = 1

    def update_layer(self):
        self.layer = 1

    def update_valid(self, value):
        self.valid = value


    def update_metrics(self, steps=0,
                       particle_read=0, tile_read=0, location_read=0, memory_read=0,
                       particle_write=0, tile_write=0, location_write=0, memory_write=0,
                       particle_created=0, tile_created=0, location_created=0,
                       particle_deleted=0, tile_deleted=0, location_deleted=0, tiles_taken=0, tiles_dropped=0,
                       particles_taken=0, particles_dropped=0):
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
        self.particles_taken = self.particles_taken + particles_taken
        self.particles_dropped = self.particles_dropped + particles_dropped
        logging.debug("CSV: Ending writing_rounds")

    def next_line(self, sim_round):
        csv_iterator = ['', self.scenario, self.solution, self.seed, sim_round,
                        self.success_counter, self.success_round,
                        self.particle_num,
                        self.particles_dropped, self.particles_dropped_sum,
                        self.steps, self.steps_sum,
                        self.particles_taken, self.particles_taken_sum,
                        self.tile_num, self.coating_steps,  self.cave_coating_steps, self.scanning_steps, self.cave_scanning_steps,
                        self.taking_steps, self.to_tile_steps, self.leader_coating_steps, self.out_of_cave_steps, self.cave_pathing,
                        self.finished, self.layer, self.valid]
        self.writer_round.writerow(csv_iterator)
        self.actual_round = sim_round
        self.steps = 0
        self.particle_read = 0
        self.tile_read = 0
        self.location_read = 0
        self.memory_read = 0
        self.particle_write = 0
        self.tile_write = 0
        self.location_write = 0
        self.memory_write = 0
        self.particle_created = 0
        self.tile_created = 0
        self.location_created = 0
        self.particle_deleted = 0
        self.tile_deleted = 0
        self.location_deleted = 0
        self.tiles_dropped = 0
        self.tiles_taken = 0
        self.success_round = 0
        self.success_counter = 0
        self.particles_taken = 0
        self.particles_dropped = 0

        self.coating_steps = np.nan
        self.scanning_steps = np.nan
        self.taking_steps = np.nan
        self.cave_scanning_steps = np.nan
        self.to_tile_steps = np.nan
        self.leader_coating_steps = np.nan
        self.out_of_cave_steps = np.nan
        self.cave_coating_steps = np.nan
        self.cave_pathing = np.nan
        self.finished = np.nan
        self.layer = np.nan
        self.valid = np.nan

    # def aggregate_metrics(self):
    #     self.csv_file.close()
    #     data = pd.read_csv(self.file_name)
    #     file_name = self.directory + "/aggregate_rounds.csv"
    #     csv_file = open(file_name, 'w', newline='')
    #     writer_round = csv.writer(csv_file)
    #     """Average Min Max for all other metrics"""
    #     writer_round.writerow(['Scenario', 'Solution', 'Seed', 'Particle Counter', 'Rounds Total',
    #                            'Success Counter',
    #                            'Particles Dropped Sum', 'Particles Dropped Avg',
    #                            'Particles Dropped Min', 'Particles Dropped Max',
    #                            'Partilcle Steps Total', 'Particle Steps Avg',
    #                            'Particle Steps Min', 'Particle Steps Max',
    #                            'Particles Taken Sum', 'Particles Taken Avg',
    #                            'Particles Taken Min', 'Particles Taken Max',
    #                            'Tile Counter',
    #                            'Total Outside Coating Steps', 'Total Cave Coating Steps', 'Total Leader Coating Steps',
    #                            'Total Coating Steps',
    #                            'Total Taking Steps',
    #                            'Total Cave Scanning', 'Total Outside Scanning', 'Total Scanning',
    #                            'Total To Tile', 'Out of Cave', "Total Steps", "Total Cave Pathing", "Total Finished",
    #                            "Total Stages", "Total Layer", "Valid State", 'AVG Rounds per Particle',
    #                            'AVG Steps per Particle'])
    #
    #     csv_interator = [self.scenario, self.solution, self.seed, len(self.world.particles), data['Round Number'].count(),
    #                      data['Success Counter'].max(),
    #
    #                      data['Particles Dropped'].sum(), round(data['Particles Dropped'].mean(), 2),
    #                      data['Particles Dropped'].min(), data['Particles Dropped'].max(),
    #
    #                      data['Particle Steps'].sum(), round(data['Particle Steps'].mean(), 2),
    #                      data['Particle Steps'].min(), data['Particle Steps'].max(),
    #
    #                      data['Particles Taken'].sum(), round(data['Particles Taken'].mean(), 2),
    #                      data['Particles Taken'].min(),
    #                      data['Particles Taken'].max(),
    #                      self.tile_num,
    #                      data['Coating'].count(), data['Cave Coating'].count(), data['Leader Coating'].count(),
    #                      data['Coating'].count() + data['Cave Coating'].count() + data['Leader Coating'].count(),
    #                      data['Taking'].count(), data['Cave Scanning'].count(), data['Scanning'].count(),
    #                      data['Cave Scanning'].count() + data['Scanning'].count()+ data['Cave Pathing'].count(), data['To Tile'].count(),
    #                      data['Out of Cave'].count(),
    #                      data['Coating'].count() + data['Cave Coating'].count() + data['Leader Coating'].count() +
    #                      data['Taking'].count() +
    #                      data['Cave Scanning'].count() + data['Scanning'].count() + data['To Tile'].count() +
    #                      data['Out of Cave'].count(), data['Cave Pathing'].count(), data['Finished'].count(),
    #
    #                      data['Coating'].count() + data['Cave Coating'].count() + data['Leader Coating'].count() +
    #                      data['Taking'].count() +
    #                      data['Cave Scanning'].count() + data['Scanning'].count() + data['To Tile'].count() +
    #                      data['Out of Cave'].count() + data['Cave Pathing'].count() + data['Finished'].count() + data[
    #                          'Particles Dropped'].sum()
    #                      + data['Particles Taken'].sum() + 1, data['Layer'].count(), data['Valid'].sum(),
    #
    #                      round(data['Round Number'].count() / len(self.world.particles),2),
    #                      round(data['Particle Steps'].sum() / len(self.world.particles), 2)]
    #
    #     writer_round.writerow(csv_interator)
    #     csv_file.close()
    #
    def aggregate_metrics(self):
        self.csv_file.close()
        data = pd.read_csv(self.file_name)
        file_name = self.directory + "/aggregate_rounds.csv"
        csv_file = open(file_name, 'w', newline='')
        writer_round = csv.writer(csv_file)
        """Average Min Max for all other metrics"""
        writer_round.writerow(['Scenario','Particles', 'Tiles', 'Rounds','Steps',
                                "Valid State", 'AVG Rounds per Particle', 'AVG Steps per Particle',
                                'AVG Rounds per Tile', 'AVG Steps per Tile'])

        csv_interator = [self.scenario, len(self.world.particles), self.tile_num, data['Round Number'].count(),  data['Particle Steps'].sum(),
                         data['Valid'].sum(),
                         round(data['Round Number'].count() / len(self.world.particles), 2),
                         round( data['Particle Steps'].sum() /len(self.world.particles), 2),
                          round(data['Round Number'].count() / self.tile_num, 2),
                          round(data['Particle Steps'].sum() / self.tile_num, 2)
                          ]

        writer_round.writerow(csv_interator)
        csv_file.close()

    # def aggregate_metrics(self):
    #     self.csv_file.close()
    #     data = pd.read_csv(self.file_name)
    #     file_name = self.directory + "/aggregate_rounds.csv"
    #     csv_file = open(file_name, 'w', newline='')
    #     writer_round = csv.writer(csv_file)
    #     """Average Min Max for all other metrics"""
    #     writer_round.writerow([ 'Scenario','Particles', 'Rounds'])
    #
    #     csv_interator = [self.scenario, len(self.world.particles), data['Round Number'].count()]
    #
    #     writer_round.writerow(csv_interator)
    #     csv_file.close()
