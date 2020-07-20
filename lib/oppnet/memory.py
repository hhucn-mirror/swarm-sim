import math

from lib.oppnet.communication import store_message
from lib.oppnet.meta import process_event, EventType
from lib.oppnet.point import Point
from lib.oppnet.util import get_distance_from_points
from lib.swarm_sim_header import get_hexagon_ring


class Memory:
    def __init__(self):
        self.schedule_memory = {}
        self.delta_memory = {}
        self.broadcast_memory = {}

    def add_scheduled_message_on(self, target_id, round_number, message):
        if round_number in self.schedule_memory.keys():
            self.schedule_memory[round_number] = self.schedule_memory.get(target_id).append((target_id, message))
        else:
            self.schedule_memory[round_number] = [(target_id, message)]

    def __try_deliver_scheduled_messages__(self, current_round, particle_map_id):
        if current_round in self.schedule_memory.keys():
            m_particles = particle_map_id
            tuples_particles = self.schedule_memory.pop(current_round)
            for e in tuples_particles:
                p_id = e[0]
                p_message = e[1]
                if p_id in m_particles.keys():
                    p = m_particles.get(p_id)
                    p.write_memory(p_message)

    def add_delta_message_on(self, target_id, message, position, start_round, signal_velocity, signal_range):
        process_event(EventType.MessageSent, message)
        if target_id in self.delta_memory.keys():
            self.delta_memory.get(target_id).append((message, position, start_round, signal_velocity, signal_range))
        else:
            self.delta_memory[target_id] = [(message, position, start_round, signal_velocity, signal_range)]

    def __try_deliver_delta_messages__(self, current_round, particle_map_id):
        new_memory = {}
        for target in list(self.delta_memory.keys()):
            new_messages = []
            for memory_entry in list(self.delta_memory[target]):
                message = memory_entry[0]
                signal_range = memory_entry[4]
                distance, distance_start_target = self.__calculate_distances__(current_round, memory_entry, target,
                                                                               particle_map_id)
                if distance < signal_range:
                    if distance >= distance_start_target:
                        store_message(message, message.get_sender(), message.get_receiver())
                    else:
                        new_messages.append(memory_entry)
                else:
                    self.delta_memory[target].remove(memory_entry)
            if len(new_messages) > 0:
                new_memory[target] = new_messages
        self.delta_memory = new_memory

    def add_broadcast_message(self, message, position, start_round, signal_velocity, signal_range):
        sender = message.get_sender()
        process_event(EventType.BroadcastSent, message)
        if sender not in self.broadcast_memory.keys():
            self.broadcast_memory[sender] = []
        self.broadcast_memory[sender].append((message, position, start_round, signal_velocity, signal_range))

    def __try_deliver_broadcasts__(self, current_round, particle_map_coordinates):
        locations = []
        for sender, entries in list(self.broadcast_memory.items()):
            for entry in entries:
                message, _, start_round, signal_velocity, signal_range = entry
                traveled_distance = signal_velocity * (current_round - start_round)
                if traveled_distance < signal_range:
                    receivers, coordinates = self.__get_broadcast_receivers__(entry, traveled_distance,
                                                                              particle_map_coordinates)
                    locations.extend(coordinates)
                    self.__deliver_broadcast(message, receivers)
                else:
                    self.broadcast_memory[sender].remove(entry)
                    if len(self.broadcast_memory[sender]) == 0:
                        del self.broadcast_memory[sender]
        return locations

    def __calculate_distances__(self, actual_round, memory_entry, target, particle_map_id):
        position = memory_entry[1]
        start_round = memory_entry[2]
        signal_velocity = memory_entry[3]
        past_rounds = actual_round - start_round
        distance = signal_velocity * past_rounds
        if target in particle_map_id:
            vector = particle_map_id[target].coordinates
            particle_point = Point.get_point_from_vector(vector)
            distance_start_target = get_distance_from_points(position, particle_point)
        else:
            distance_start_target = math.inf
        return distance, distance_start_target

    def try_deliver_messages(self, world):
        current_round = world.get_actual_round()
        particle_map_id = world.get_particle_map_id()
        self.__try_deliver_scheduled_messages__(current_round, particle_map_id)
        self.__try_deliver_delta_messages__(current_round, particle_map_id)
        locations = self.__try_deliver_broadcasts__(current_round, world.get_particle_map_coordinates())
        world.draw_broadcast_ring(locations)

    @staticmethod
    def __deliver_broadcast(message, receivers):
        for receiver in receivers:
            message.set_receiver(receiver)
            message.set_actual_receiver(receiver)
            message.is_broadcast = True
            receiver.rcv_store.append(message)
            process_event(EventType.BroadcastDelivered, message)

    @staticmethod
    def __get_broadcast_receivers__(memory_entry, traveled_distance, particle_map_coordinates):
        message, position, start_round, signal_velocity, signal_range = memory_entry
        new_locations = []
        for distance in range(traveled_distance - signal_velocity + 1, traveled_distance + 1):
            new_locations.extend(get_hexagon_ring((position.getx(), position.gety(), 0), distance))
        particle_locations = particle_map_coordinates.keys()
        receiving_particles = set(
            [particle_map_coordinates.get(key) for key in new_locations if key in particle_locations])

        return receiving_particles, new_locations
