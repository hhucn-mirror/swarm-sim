import logging
import random
from enum import Enum

from lib.oppnet.mobility_model import MobilityModel, MobilityModelMode
from lib.particle import Particle
from lib.swarm_sim_header import scan_within_per_hop, get_coordinates_in_direction


class ChaseMode(Enum):
    FocusFlock = 1
    FocusParticle = 2


class Predator(Particle):
    def __init__(self, world, coordinates, color, particle_counter=0, csv_generator=None, mm_mode=None):
        super().__init__(world=world, coordinates=coordinates, color=color, particle_counter=particle_counter,
                         csv_generator=csv_generator)
        self.scan_radius = self.world.config_data.predator_scan_radius
        self.chase_mode = self.world.config_data.predator_chase_mode
        if not mm_mode:
            mm_mode = MobilityModelMode.POI
        self.mobility_model = MobilityModel(self.coordinates, mm_mode)

    def move_to(self, direction):
        """
        Moves the predator to the given direction

        :param direction: The direction is defined by loaded grid class
        :return: True: Success Moving;  False: Non moving
        """
        direction_coord = get_coordinates_in_direction(self.coordinates, direction)
        direction, direction_coord = self.check_within_border(direction, direction_coord)
        if self.world.grid.are_valid_coordinates(direction_coord) \
                and direction_coord not in self.world.particle_map_coordinates:
            if self.coordinates in self.world.particle_map_coordinates:
                del self.world.particle_map_coordinates[self.coordinates]
            self.coordinates = direction_coord
            self.world.particle_map_coordinates[self.coordinates] = self
            if self.world.vis:
                self.world.vis.predator_changed(self)
            logging.info("particle %s successfully moved to %s", str(self.get_id()), direction)
            return True

        return False

    def chase(self):
        if self.chase_mode == ChaseMode.FocusParticle:
            next_direction = self.chase_nearest_particle()
        else:
            next_direction = self.chase_nearby_flock()
        if next_direction:
            return self.move_to(next_direction)
        else:
            return False

    def chase_nearest_particle(self):
        """
        Returns the nearest particle within the predator's scan_radius or None if no particle is close enough.
        :return: nearest particle or None
        :rtype: Particle
        """
        nearest_particles = scan_within_per_hop(self.world.particle_map_coordinates, self.coordinates,
                                                self.scan_radius, self.world.grid)
        if nearest_particles:
            if len(nearest_particles[0]) > 0:
                self.mobility_model.poi = random.choice(nearest_particles[0])
            else:
                self.mobility_model.poi = nearest_particles[0][0]
            return self.mobility_model.next_direction(self.coordinates)
        else:
            return None

    def chase_nearby_flock(self):
        try:
            self.mobility_model.poi = self.world.get_nearby_flock_center_by_coordinates(self.coordinates, self.scan_radius)
            return self.mobility_model.next_direction(self.coordinates)
        except IndexError:
            return None
