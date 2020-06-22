from lib.oppnet.communication import Message, send_message
from lib.oppnet.message_types import DirectionMessageContent, RelativeLocationMessageContent, CardinalDirection
from lib.oppnet.particles import FlockMode


class Mixin:
    def send_direction_message(self):
        """
        Sends a DirectionMessageContent with the current_dir of the particle's mobility_model and its current neighbours
        :return: nothing
        """
        self.reset_neighborhood_direction_counter()
        self.__neighborhood_direction_counter__[self.mobility_model.current_dir] += 1
        content = DirectionMessageContent(self.mobility_model.current_dir, list(self.__current_neighborhood__.keys()))
        for neighbour in self.__current_neighborhood__.keys():
            message = Message(self, neighbour, self.world.get_actual_round(), content=content)
            send_message(self, neighbour, message)

    def send_all_to_forward(self):
        """
        Tries to forward each message in the send_store.
        :return: nothing
        """
        while len(self.send_store) > 0:
            self.forward_via_contact(self.send_store.pop())

    def query_relative_location(self):
        """
        Sends a message with RelativeLocationMessageContent to each surrounding particle, querying the amount of hops
        in each cardinal direction for a message to reach the outer ring of a flock.
        :return: nothing
        """
        self.set_flock_mode(FlockMode.QueryingLocation)
        self.reset_max_cardinal_direction_hops()
        cardinal_directions = CardinalDirection.get_cardinal_directions_list()
        queried_directions_per_particle = {}
        for cardinal_direction in cardinal_directions:
            one_hop_particles = self.get_particles_in_cardinal_direction_hop(cardinal_direction, 1)
            if len(one_hop_particles) > 0:
                queried_directions_per_particle = self.__add_queried_direction__(cardinal_direction, one_hop_particles,
                                                                                 queried_directions_per_particle)
            # scan with maximum scan radius to detect whether the particle is actually at the edge of the flock
            elif len(self.get_particles_in_cardinal_direction_hop(cardinal_direction,
                                                                  self.routing_parameters.scan_radius)) == 0:
                self.__max_cardinal_direction_hops__[cardinal_direction] = 0
        self.__send_relative_location_queries__(queried_directions_per_particle)

    @staticmethod
    def __add_queried_direction__(cardinal_direction, particles, queried_directions_per_particle):
        """
        Adds :param particles to :param queried_directions_per_particle by appending :param cardinal_direction
        to its values.

        :param cardinal_direction: value to append
        :type cardinal_direction: CardinalDirection
        :param particles: list of particles
        :type particles: [Particle]
        :param queried_directions_per_particle: dictionary of particle, [CardinalDirection] pairs
        :type queried_directions_per_particle: dict
        :return: dictionary of particle, [CardinalDirection] pairs
        :rtype: dict
        """
        for particle in particles:
            if particle not in queried_directions_per_particle:
                queried_directions_per_particle[particle] = [cardinal_direction]
            else:
                queried_directions_per_particle[particle].append(cardinal_direction)
        return queried_directions_per_particle

    def __send_relative_location_queries__(self, queried_directions_per_particle: dict):
        """
        Sends RelativeMessageContent to each particle in the keys of :param queried_directions_per_particle.
        Expects queried_directions parameter of RelativeMessageContent as value of
        :param queried_directions_per_particle.

        :param queried_directions_per_particle: dict of particles to send a RelativeMessageContent message to
        :type queried_directions_per_particle: dict
        :return: nothing
        """
        for particle, queried_locations in queried_directions_per_particle.items():
            content = RelativeLocationMessageContent(queried_locations, False, self.__hops_per_direction_for_neighbor())
            send_message(self, particle, Message(self, particle, content=content))

    def __send_relative_location_response__(self):
        """
        Sends a RelativeLocationMessageContent response. This will set the hops inside
        the content to the maximum it knows itself + 1.
        :return: nothing
        """
        for receiver, queried_directions in list(self.__received_queried_directions__.items()):
            hops_per_direction = self.__hops_per_direction_for_neighbor(queried_directions)
            if hops_per_direction:
                content = RelativeLocationMessageContent([], True, hops_per_direction)
                send_message(self, receiver, Message(self, receiver, content=content))
                # remove the directions that are included in the response
                for queried_direction in content.hops_per_direction.keys():
                    self.__received_queried_directions__[receiver].remove(queried_direction)
                    if len(self.__received_queried_directions__[receiver]) == 0:
                        del self.__received_queried_directions__[receiver]
