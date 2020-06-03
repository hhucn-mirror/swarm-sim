"""The world module provides the interface of the simulation world. In the simulation world
all the data of the particles, tiles, and locations are stored.
It also have the the coordination system and stated the maximum of the x and y coordinate.

 .. todo:: What happens if the maximum y or x axis is passed? Either the start from the other side or turns back.
"""
import collections
import importlib
import itertools
import logging
import numpy as np
import os
import random
import threading
import time

from lib import vis3d
from lib.location import Location
from lib.oppnet.memory import Memory
from lib.oppnet.predator import Predator
from lib.particle import Particle
from lib.swarm_sim_header import eprint, get_coordinates_in_direction, scan_within
from lib.tile import Tile


class Flock:
    instance_id = itertools.count()

    def __init__(self, particles):
        self._particles = set(particles)
        self.id = next(Flock.instance_id)
        self._max_coordinates = None
        self._min_coordinates = None

    def add_particle(self, particle: Particle):
        """
        Adds :param particle to its set of particles.
        :param particle: the particle to add
        :type particle: Particle
        """
        self._particles.add(particle)

    def remove_particle(self, particle: Particle):
        """
        Removes :param particle from its set of particles.
        :param particle: the particle to remove
        :type particle: Particle
        """
        self._particles.remove(particle)

    def extend_particles(self, particles):
        """
        Updates the set of particles with :param particles
        :param particles: iterable of Particles to update with
        :type particles: Iterable
        """
        self._particles.update(particles)

    def get_estimated_center(self):
        """
        Gets the estimated center of the flock by interpreting minimum and maximum coordinates as the corners
        of a square.
        :return: the estimated flock center as x,y tuple
        :rtype: tuple
        """
        self._set_min_max_coordinates()
        estimated_x = (self._max_coordinates[0] + self._min_coordinates[0]) / 2
        estimated_y = (self._max_coordinates[1] + self._min_coordinates[1]) / 2
        return estimated_x, estimated_y

    def _set_min_max_coordinates(self):
        """
        Finds the the maximum and minimum coordinates in the particle set.
        """
        coordinates = [particle.coordinates for particle in self._particles]
        self._max_coordinates = np.amax(coordinates, axis=0)
        self._min_coordinates = np.amin(coordinates, axis=0)


class World:
    matter_classes = [Particle, Tile, Location, Predator]

    def __init__(self, config_data):
        """
        Initializing the world constructor
        :param config_data: configuration data from config.ini file
        """
        self.__round_counter = 1
        self.__end = False

        self.particle_id_counter = 0
        self.particles = []
        self.particle_map_coordinates = {}
        self.particle_map_id = {}
        self.particles_created = []
        self.particles_rm = []
        self.__particle_deleted = False
        self.particle_color_map = {}

        self.tiles = []
        self.tile_map_coordinates = {}
        self.tile_map_id = {}
        self.tiles_created = []
        self.tiles_rm = []

        self.__tile_deleted = False
        self.new_tile = None
        self.__tile_deleted = False

        self.locations = []
        self.location_map_coordinates = {}
        self.location_map_id = {}
        self.locations_created = []
        self.locations_rm = []
        self.__location_deleted = False
        self.new_location = None

        self.predators = []
        self.predator_map_coordinates = {}
        self.predator_map_id = {}
        self.predators_created = []
        self.predators_rm = []
        self.__predator_deleted = False

        self.config_data = config_data
        self.grid = config_data.grid

        self.particle_mod = importlib.import_module(config_data.particle)

        self.csv_generator = importlib.import_module(config_data.csv_generator)
        self.csv_round = self.csv_generator.CsvRoundData(sim=self,
                                                         solution=config_data.solution,
                                                         seed=config_data.seed_value,
                                                         directory=config_data.direction_name)

        self._particle_flocks_ids = {}
        self._flocks = []

        if config_data.visualization:
            self.vis = vis3d.Visualization(self)
        else:
            self.vis = None

        mod = importlib.import_module('scenario.' + self.config_data.scenario)

        if config_data.visualization:
            import threading
            x = threading.Thread(target=mod.scenario, args=(self,))
            self.vis.wait_for_thread(x, "loading scenario... please wait.", "Loading Scenario")
        else:
            mod.scenario(self)

        if self.config_data.particle_random_order:
            random.shuffle(self.particles)

        self.memory = Memory()

    def reset(self):
        """
        resets everything (particles, tiles, locations) except for the logging in system.log and in the csv file...
        reloads the scenario.
        :return:
        """
        self.__round_counter = 1
        self.__end = False

        self.particle_id_counter = 0
        self.particles = []
        self.particles_created = []
        self.particles_rm = []
        self.particle_map_coordinates = {}
        self.particle_map_id = {}
        self.__particle_deleted = False
        self.particle_color_map = {}

        self.tiles = []
        self.tiles_created = []
        self.tiles_rm = []
        self.tile_map_coordinates = {}
        self.tile_map_id = {}
        self.__tile_deleted = False

        self.locations = []
        self.locations_created = []
        self.location_map_coordinates = {}
        self.location_map_id = {}
        self.locations_rm = []
        self.__location_deleted = False

        self.predators = []
        self.predator_map_coordinates = {}
        self.predator_map_id = {}
        self.predators_created = []
        self.predators_rm = []
        self.__predator_deleted = False

        self._particle_flocks_ids = {}
        self._flocks = []

        if self.config_data.visualization:
            self.vis.reset()

        mod = importlib.import_module('scenario.' + self.config_data.scenario)

        if self.config_data.visualization:
            # if visualization is on, run the scenario in a separate thread and show that the program runs..
            x = threading.Thread(target=mod.scenario, args=(self,))
            self.vis.wait_for_thread(x, "loading scenario... please wait.", "Loading Scenario")
            self.vis.update_visualization_data()

        else:
            # if no vis, just run the scenario on the main thread
            mod.scenario(self)

        if self.config_data.particle_random_order:
            random.shuffle(self.particles)

    def save_scenario(self):

        if os.path.exists("scenario") and os.path.isdir("scenario"):
            try:
                f = open("scenario/scenario_%s.py" % str(time.perf_counter_ns()), "w+")
                f.write("def solution(world):\n")
                for p in self.particle_map_coordinates.values():
                    f.write("\tworld.add_particle(%s, color=%s)\n" % (str(p.coordinates), str(p.get_color())))
                for t in self.tile_map_coordinates.values():
                    f.write("\tworld.add_tile(%s, color=%s)\n" % (str(t.coordinates), str(t.get_color())))
                for l in self.location_map_coordinates.values():
                    f.write("\tworld.add_location(%s, color=%s)\n" % (str(l.coordinates), str(l.get_color())))
                f.flush()
                f.close()
            except IOError as e:
                eprint(e)
        else:
            eprint("\"scenario\" folder doesn't exist. "
                   "Please create it in the running directory before saving scenarios.")

    def csv_aggregator(self):
        self.csv_round.aggregate_metrics()
        particle_csv = self.csv_generator.CsvParticleFile(self.config_data.direction_name)
        for p in self.particles:
            particle_csv.write_particle(p)
        particle_csv.csv_file.close()

    def set_successful_end(self):
        self.csv_round.success()
        self.__end = True
        
    def get_max_round(self):
        """
        The max round number
    
        :return: maximum round number
        """
        return self.config_data.max_round

    def get_actual_round(self):
        """
        The actual round number

        :return: actual round number
        """
        return self.__round_counter

    def set_unsuccessful_end(self):
        """
        Allows to terminate before the max round is reached
        """
        self.__end = True

    def get_end(self):
        """
            Returns the end parameter values either True or False
        """
        return self.__end

    def inc_round_counter_by(self, number=1):
        """
        Increases the the round counter by

        :return:
        """
        self.__round_counter += number

    def get_solution(self):
        """
        actual solution name

        :return: actual solution name
        """
        return self.config_data.solution

    def get_amount_of_particles(self):
        """
        Returns the actual number of particles in the world

        :return: The actual number of Particles
        """
        return len(self.particles)

    def get_particle_list(self):
        """
        Returns the actual number of particles in the world

        :return: The actual number of Particles
        """
        return self.particles

    def get_particle_map_coordinates(self):
        """
        Get a dictionary with all particles mapped with their actual coordinates

        :return: a dictionary with particles and their coordinates
        """
        return self.particle_map_coordinates

    def get_particle_map_id(self):
        """
        Get a dictionary with all particles mapped with their own ids

        :return: a dictionary with particles and their own ids
        """
        return self.particle_map_id

    def get_amount_of_tiles(self):
        """
        Returns the actual number of particles in the world

        :return: The actual number of Particles
        """
        return len(self.tiles)

    def get_tiles_list(self):
        """
        Returns the actual number of tiles in the world

        :return: a list of all the tiles in the world
        """
        return self.tiles

    def get_tile_map_coordinates(self):
        """
        Get a dictionary with all tiles mapped with their actual coordinates

        :return: a dictionary with particles and their coordinates
        """
        return self.tile_map_coordinates

    def get_tile_map_id(self):
        """
        Get a dictionary with all particles mapped with their own ids

        :return: a dictionary with particles and their own ids
        """
        return self.tile_map_id

    def get_predators_list(self):
        """
        Returns the actual number of tiles in the world

        :return: a list of all the tiles in the world
        """
        return self.predators

    def get_predator_map_coordinates(self):
        """
        Get a dictionary with all tiles mapped with their actual coordinates

        :return: a dictionary with particles and their coordinates
        """
        return self.predator_map_coordinates

    def get_predator_map_id(self):
        """
        Get a dictionary with all particles mapped with their own ids

        :return: a dictionary with particles and their own ids
        """
        return self.predator_map_id

    def get_amount_of_locations(self):
        """
        Returns the actual number of locations in the world

        :return: The actual number of locations
        """
        return len(self.locations)

    def get_location_list(self):
        """
        Returns the actual number of locations in the world

        :return: The actual number of locations
        """
        return self.locations

    def get_location_map_coordinates(self):
        """
        Get a dictionary with all locations mapped with their actual coordinates

        :return: a dictionary with locations and their coordinates
        """
        return self.location_map_coordinates

    def get_location_map_id(self):
        """
        Get a dictionary with all locations mapped with their own ids

        :return: a dictionary with locations and their own ids
        """
        return self.location_map_id

    def get_world_x_size(self):
        """

        :return: Returns the maximal x size of the world
        """
        return self.config_data.size_x

    def get_world_y_size(self):
        """
        :return: Returns the maximal y size of the world
        """
        return self.config_data.size_y

    def get_world_size(self):
        """
        :return: Returns the maximal (x,y) size of the world as a tupel
        """
        return self.config_data.size_x, self.config_data.size_y

    def get_tile_deleted(self):
        return self.__tile_deleted

    def get_particle_deleted(self):
        return self.__particle_deleted

    def get_location_deleted(self):
        return self.__location_deleted

    def get_message_ttl(self):
        return self.config_data.message_ttl

    def set_tile_deleted(self):
        self.__tile_deleted = False

    def set_particle_deleted(self):
        self.__particle_deleted = False

    def set_location_deleted(self):
        self.__location_deleted = False

    def add_particle(self, coordinates, color=None):
        """
        Add a particle to the world database

        :param coordinates: The x coordinate of the particle
        :param color: The color of the particle
        :return: Added Matter; False: Unsuccessful
        """

        if len(coordinates) == 2:
            coordinates = (coordinates[0], coordinates[1], 0.0)

        if len(self.particles) < self.config_data.max_particles:
            if color is None:
                color = self.config_data.particle_color
            particle = self.particle_mod.Particle(self, coordinates=coordinates, color=color,
                                                  particle_counter=self.particle_id_counter,
                                                  csv_generator=self.csv_generator)
            return_value = self.add_matter(particle, coordinates)
            if return_value:
                self.particles_created.append(particle)
                self.particle_color_map[particle] = color
                self.particle_id_counter += 1
            return return_value
        else:
            logging.info("Max of particles reached and no more particles can be created")
            return False

    def remove_particle(self, particle_id):
        """ Removes a particle with a given particle id from the world database


        :param particle_id: particle id
        :return: True: Successful removed; False: Unsuccessful
        """
        self.remove_matter(particle_id, Particle)

    def remove_particle_on(self, coordinates):
        """
        Removes a particle on a give coordinate from to the world database

        :param coordinates: A tuple that includes the x and y coordinates
        :return: True: Successful removed; False: Unsuccessful
        """
        return self.remove_matter_on(coordinates, Particle)

    def add_tile(self, coordinates, color=None):
        """
        Adds a tile to the world database
        :param color: color of the tile (None for config default)
        :param coordinates: the coordinates on which the tile should be added
        :return: Successful added matter; False: Unsuccessful
        """
        if color is None:
            color = self.config_data.tile_color
        return self.add_matter(Tile(self, coordinates, color), coordinates)

    def remove_tile(self, tile_id):
        """
        Removes a tile with a given tile_id from to the world database

        :param tile_id: The tiles id that should be removed
        :return:  True: Successful removed; False: Unsuccessful
        """
        return self.remove_matter(tile_id, Tile)

    def remove_tile_on(self, coordinates):
        """
        Removes a tile on a give coordinates from to the world database

        :param coordinates: A tuple that includes the x and y coordinates
        :return: True: Successful removed; False: Unsuccessful
        """
        self.remove_matter_on(coordinates, Tile)

    def add_location(self, coordinates, color=None):
        """
        Add a tile to the world database

        :param color:
        :param coordinates: the coordinates on which the tile should be added
        :return: True: Successful added; False: Unsuccessful
        """
        if color is None:
            color = self.config_data.location_color
        return self.add_matter(Location(self, coordinates, color), coordinates)

    def remove_location(self, location_id):
        """
        Removes a tile with a given tile_id from to the world database

        :param location_id: The locations id that should be removed
        :return:  True: Successful removed; False: Unsuccessful
        """
        return self.remove_matter(location_id, Location)

    def remove_location_on(self, coordinates):
        """
        Removes a location on a give coordinates from to the world database

        :param coordinates: A tuple that includes the x and y coordinates
        :return: True: Successful removed; False: Unsuccessful
        """
        return self.remove_matter_on(coordinates, Location)

    def add_predator(self, coordinates, color=None):
        if color is None:
            color = self.config_data.predator_color
        return self.add_matter(Predator(self, coordinates, color, csv_generator=self.csv_generator), coordinates)

    def add_matter(self, matter, coordinates):
        """
        Add a tile to the world database

        :param matter: Matter
        :param coordinates: the coordinates on which the tile should be added
        :return: True: Successful added; False: Unsuccessful
        """
        matter_type = type(matter)
        bases = matter_type.__bases__
        if matter_type not in self.matter_classes and bases[0] not in self.matter_classes:
            eprint('world.py -> add_matter() class {} with bases {} of matter param not supported'.format(
                matter_type, bases[0]))
            return

        if len(coordinates) == 2:
            coordinates = (coordinates[0], coordinates[1], 0.0)

        map_coordinates = self._get_map_coordinates_for_matter(matter)
        matters_list = self._get_matter_list(matter)

        if self.grid.are_valid_coordinates(coordinates):
            if coordinates not in map_coordinates:
                matters_list.append(matter)
                if self.vis is not None:
                    self._get_matter_changed_function(matter)(matter)
                map_coordinates[matter.coordinates] = matter
                self._get_map_id_for_matter(matter)[matter.get_id()] = matter
                self._get_csv_update_num_function_for_matter(matter)(len(matters_list))
                logging.info("Created {} with id {} on coordinates {}".format(
                    type(matter), matter.get_id(), matter.coordinates))
                matter.created = True
                return matter
            else:
                logging.info("there is already a location on {}".format(matter.coordinates))
                return False
        else:
            logging.info("{} is not a valid location!".format(matter.coordinates))
            return False

    def remove_matter(self, matter_id, matter_class):
        """
        Removes a matter with a given tile_id from to the world database

        :param matter_id: The matter id that should be removed
        :param matter_class: The matter subclass
        :return:  True: Successful removed; False: Unsuccessful
        """
        map_id = self._get_map_id_for_matter(matter_class)
        map_coordinates = self._get_map_coordinates_for_matter(matter_class)
        matter_list = self._get_matter_list(matter_class)
        if matter_id in map_id:
            removed_matter = map_id[matter_id]
            if removed_matter in matter_list:
                matter_list.remove(removed_matter)
            if self.vis is not None:
                self.vis.remove_location(removed_matter)
            self._get_matter_list_rm(matter_class).append(removed_matter)
            logging.info("Deleted matter with id {} on {}".format(matter_id, removed_matter.coordinates))
            try:
                del map_coordinates[removed_matter.coordinates]
            except KeyError:
                pass
            try:
                del map_id[matter_id]
            except KeyError:
                pass
            self._get_csv_update_num_function_for_matter(matter_class)(len(matter_list))
            self._update_deleted_metrics_(matter_class)
            return True
        else:
            return False

    def _update_deleted_metrics_(self, matter):
        if isinstance(matter, Particle) or matter == Particle:
            self.csv_round.update_metrics(particles_deleted=1)
        elif isinstance(matter, Location) or matter == Location:
            self.csv_round.update_metrics(location_deleted=1)
        elif isinstance(matter, Tile) or matter == Tile:
            self.csv_round.update_metrics(tile_deleted=1)
        else:
            return None

    def remove_matter_on(self, coordinates, matter_class):
        """
        Removes a matter on a give coordinates from to the world database

        :param coordinates: A tuple that includes the x and y coordinates
        :param matter_class: The matter subclass
        :return: True: Successful removed; False: Unsuccessful
        """
        map_coordinates = self._get_map_coordinates_for_matter(matter_class)
        if coordinates in map_coordinates:
            return self.remove_matter(map_coordinates[coordinates].get_id(), matter_class)
        else:
            return False

    def move_particles(self, particle_directions: dict):
        """
        Moves all particles inside the :param particle_directions: keys
        direction of the corresponding dictionary value. Moves them one
        after another to avoid crowding locations.
        :param particle_directions: particle -> direction dictionary
        :type particle_directions: dict
        """
        particle_set = set(particle_directions.keys())
        ordered_particles = collections.OrderedDict()
        particle_map_coordinates = self.particle_map_coordinates
        i = 0
        while i < len(particle_directions) ** 2 and len(particle_set) > 0:
            i += 1
            for particle in list(particle_set):
                direction = particle_directions[particle]
                direction_coord = get_coordinates_in_direction(particle.coordinates, direction)
                direction, direction_coord = particle.check_within_border(direction, direction_coord)
                # remove the particle from the set if the next coordinates are not valid
                if not self.grid.are_valid_coordinates(direction_coord):
                    particle_set.remove(particle)
                    del particle_map_coordinates[particle.coordinates]
                # add it to the ordered dictionary
                elif direction_coord not in particle_map_coordinates \
                        and particle not in ordered_particles:
                    particle_set.remove(particle)
                    ordered_particles[particle] = direction
                    if particle.coordinates in particle_map_coordinates:
                        del particle_map_coordinates[particle.coordinates]

        for particle, direction in ordered_particles.items():
            particle.move_to(direction)

    def move_particles_collision_free(self, particles: [Particle], direction):
        """
        Moves a list of :param particles: in a :param direction: while avoiding
        collisions, i.e. particles are moved in the order of their 'closeness'
        to :param direction:. E.g. two particles a, b with coordinates a_c = (0.5, 1, 0)
        and b_c = (1, 0, 0) moving northeast -> (0.5, 1, 0). Particle b would move
        after a, since a is equivalent to the northeast vector.
        :param particles: list of particles to move
        :type particles: list of Particle objects
        :param direction: the direction for particles to move to
        :type direction: a direction vector
        :return: sorted list of particle coordinates
        :rtype: list of coordinates
        """
        coordinates_list = [particle.coordinates for particle in particles]
        # northeast
        if direction == (0.5, 1, 0):
            coordinates_list.sort(key=self.__get_x_y__)
        # east
        elif direction == (1, 0, 0):
            coordinates_list.sort(key=self.__get_x__)
        # southeast
        elif direction == (0.5, -1, 0):
            coordinates_list.sort(key=self.__get_y__, reverse=True)
            coordinates_list.sort(key=self.__get_x__)
        # southwest
        elif direction == (-0.5, -1, 0):
            coordinates_list.sort(key=self.__get_x_y__, reverse=True)
        # west
        elif direction == (-1, 0, 0):
            coordinates_list.sort(key=self.__get_x__, reverse=True)
        # northwest
        else:
            coordinates_list.sort(key=self.__get_y__)
            coordinates_list.sort(key=self.__get_x__, reverse=True)

        for coordinates in coordinates_list:
            particle = self.particle_map_coordinates[coordinates]
            particle.move_to(direction)

        return coordinates_list

    def reset_particle_colors(self):
        """
        Resets the color parameter of every particle in the world to its original value.
        :return: Nothing
        """
        for particle, color in self.particle_color_map.items():
            particle.set_color(color)

    def _get_matter_list(self, matter):
        """
            Returns the corresponding list of matter for the class of :param matter.
            :param matter: Matter object or Matter subclass
            :return: function
            """
        if isinstance(matter, Predator) or matter == Predator:
            return self.predators
        elif isinstance(matter, Particle) or matter == Particle:
            return self.particles
        elif isinstance(matter, Location) or matter == Location:
            return self.locations
        elif isinstance(matter, Tile) or matter == Tile:
            return self.tiles
        else:
            return None

    def _get_matter_list_rm(self, matter):
        """
            Returns the corresponding list of removed matter for the class of :param matter.
            :param matter: Matter object or Matter subclass
            :return: function
            """
        if isinstance(matter, Predator) or matter == Predator:
            return self.predators_rm
        elif isinstance(matter, Particle) or matter == Particle:
            return self.particles_rm
        elif isinstance(matter, Location) or matter == Location:
            return self.locations_rm
        elif isinstance(matter, Tile) or matter == Tile:
            return self.tiles_rm
        else:
            return None

    def _get_matter_changed_function(self, matter):
        """
            Returns the corresponding matter changed function in vis for the class of :param matter.
            :param matter: Matter object or Matter subclass
            :return: function
            """
        if isinstance(matter, Predator) or matter == Predator:
            return self.vis.predator_changed
        elif isinstance(matter, Particle) or matter == Particle:
            return self.vis.particle_changed
        elif isinstance(matter, Location) or matter == Location:
            return self.vis.location_changed
        elif isinstance(matter, Tile) or matter == Tile:
            return self.vis.tile_changed
        else:
            return None

    def _get_matter_removed_function(self, matter):
        """
            Returns the corresponding matter changed function in vis for the class of :param matter.
            :param matter: Matter object or Matter subclass
            :return: function
            """
        if isinstance(matter, Predator) or matter == Predator:
            return self.vis.predator_changed
        elif isinstance(matter, Particle) or matter == Particle:
            return self.vis.particle_changed
        elif isinstance(matter, Location) or matter == Location:
            return self.vis.location_changed
        elif isinstance(matter, Tile) or matter == Tile:
            return self.vis.tile_changed
        else:
            return None

    def _get_map_coordinates_for_matter(self, matter):
        """
        Returns the corresponding map_coordinates dictionary for the class of :param matter.
        :param matter: Matter object or Matter subclass
        :return: dict
        """
        if isinstance(matter, Predator) or matter == Predator:
            return self.predator_map_coordinates
        elif isinstance(matter, Particle) or matter == Particle:
            return self.particle_map_coordinates
        elif isinstance(matter, Location) or matter == Location:
            return self.location_map_coordinates
        elif isinstance(matter, Tile) or matter == Tile:
            return self.tile_map_coordinates
        else:
            return None

    def _get_map_id_for_matter(self, matter):
        """
        Returns the corresponding map_id dictionary for the class of :param matter.
        :param matter: Matter object or Matter subclass
        :return: dict
        """
        if isinstance(matter, Predator) or matter == Predator:
            return self.predator_map_id
        elif isinstance(matter, Particle) or matter == Particle:
            return self.particle_map_id
        elif isinstance(matter, Location) or matter == Location:
            return self.location_map_id
        elif isinstance(matter, Tile) or matter == Tile:
            return self.tile_map_id
        else:
            return None

    def _get_csv_update_num_function_for_matter(self, matter):
        """
            Returns the corresponding matter updated number function in csv_generator for the class of :param matter.
            :param matter: Matter object
            :return: function
            """
        if isinstance(matter, Predator) or matter == Predator:
            return self.csv_round.update_predator_num
        elif isinstance(matter, Particle) or matter == Particle:
            return self.csv_round.update_particle_num
        elif isinstance(matter, Location) or matter == Location:
            return self.csv_round.update_locations_num
        elif isinstance(matter, Tile) or matter == Tile:
            return self.csv_round.update_tiles_num
        else:
            return None

    def get_nearby_flock_center_by_coordinates(self, coordinates, max_hops):
        particles = scan_within(self.particle_map_coordinates, coordinates, max_hops, self.grid)
        flock_ids = self.get_particles_flock_ids(particles)
        estimated_flock_center = self._flocks[random.choice(flock_ids)].get_estimated_center()
        return self.grid.get_nearest_valid_coordinates(estimated_flock_center)

    def update_flock_id_for_particles(self, particles: [Particle], new_flock_id=None):
        """
        Sets the value of all items in :param particles in the particle_flock_ids dictionary to :param new_flock_id,
        if it is set. Else it's set to the most common value for particles existing as keys in the particle_flock_ids
        dictionary. If no entries exist, entries with the increment of the flock_id_counter will be created for all
        items in :param particles.
        :param particles: particles to update
        :type particles: list
        :param new_flock_id: the new flock id
        :type new_flock_id: int
        :return: the new flock_id
        :rtype: int
        """
        if not new_flock_id:
            flock_ids = self.get_particles_flock_ids(particles)
            if flock_ids:
                new_flock_id = self.get_most_common(flock_ids)
            else:
                return self._add_new_flock_(particles)
        self.move_particles_to_flock(new_flock_id, particles)
        return new_flock_id

    def _add_new_flock_(self, particles):
        new_flock = Flock(particles)
        self._flocks.append(new_flock)
        for particle in particles:
            self._particle_flocks_ids[particle] = new_flock.id
        return new_flock.id

    def move_particles_to_flock(self, new_flock_id, particles):
        """
        Moves :param particles to flock with :param new_flock_id.
        :param new_flock_id: new flock id
        :type new_flock_id: int
        :param particles: particles to move
        :type particles: list
        """
        for particle in particles:
            try:
                self._flocks[self._particle_flocks_ids[particle]].remove_particle(particle)
            except KeyError:
                pass
            finally:
                self._particle_flocks_ids[particle] = new_flock_id
        self._flocks[new_flock_id].extend_particles(particles)

    def get_particles_flock_ids(self, particles: [Particle]):
        """
        Returns a list of ids for each particle in :param particles.
        :param particles: list of particles
        :type particles: list
        :return: list of ids
        :rtype: list
        """
        return [self._particle_flocks_ids[particle] for particle in particles if particle in self._particle_flocks_ids]

    @staticmethod
    def get_most_common(items):
        [(most_common, _)] = collections.Counter(items).most_common(1)
        return most_common

    @staticmethod
    def __get_x__(coordinates):
        return coordinates[0]

    @staticmethod
    def __get_y__(coordinates):
        return coordinates[1]

    @staticmethod
    def __get_x_y__(coordinates):
        return coordinates[0] + coordinates[1]

    @staticmethod
    def __get_z__(coordinates):
        return coordinates[2]
