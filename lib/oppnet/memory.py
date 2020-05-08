import math
from enum import Enum

from lib.oppnet.communication import store_message
from lib.oppnet.meta import process_event, EventType
from lib.oppnet.point import Point
from lib.oppnet.util import get_distance
from lib.swarm_sim_header import get_hexagon_coordinates


class MemoryMode(Enum):
    Schedule = 0
    Delta = 1
    Broadcast = 2


class Memory:
    def __init__(self):
        self.schedule_memory = {}
        self.delta_memory = {}
        self.broadcast_memory = {}

    def add_scheduled_message_on(self, target_id, round_number, msg):
        if round_number in self.schedule_memory.keys():
            self.schedule_memory[round_number] = self.schedule_memory.get(target_id).append((target_id, msg))
        else:
            self.schedule_memory[round_number] = [(target_id, msg)]

    def __try_deliver_scheduled_messages__(self, current_round, particle_map_id):
        if current_round in self.schedule_memory.keys():
            m_particles = particle_map_id
            tuples_particles = self.schedule_memory.pop(current_round)
            for e in tuples_particles:
                p_id = e[0]
                p_msg = e[1]
                if p_id in m_particles.keys():
                    p = m_particles.get(p_id)
                    p.write_memory(p_msg)

    def add_delta_message_on(self, target_id, msg, position, start_round, signal_velocity, expiry_rate):
        process_event(EventType.MessageSent, msg)
        if target_id in self.delta_memory.keys():
            self.delta_memory.get(target_id).append((msg, position, start_round, signal_velocity, expiry_rate))
        else:
            self.delta_memory[target_id] = [(msg, position, start_round, signal_velocity, expiry_rate)]

    def __try_deliver_delta_messages__(self, current_round, particle_map_id):
        new_memory = {}
        for target in self.delta_memory.keys():
            new_msgs = []
            for m in self.delta_memory[target]:
                msg = m[0]
                expiry_rate = m[4]
                distance, distance_start_target = self.__calculate_distances__(current_round, m, target,
                                                                               particle_map_id)
                if distance < expiry_rate:
                    if distance >= distance_start_target:
                        store_message(msg, msg.get_sender(), msg.get_receiver())
                    else:
                        new_msgs.append(m)
            if len(new_msgs) > 0:
                new_memory[target] = new_msgs
        self.delta_memory = new_memory

    def add_broadcast_message(self, msg, position, start_round, signal_velocity, expiry_rate):
        process_event(EventType.MessageSent, msg)
        sender = msg.get_sender()
        if sender not in self.broadcast_memory.keys():
            self.broadcast_memory[sender] = []
        self.broadcast_memory[sender].append((msg, position, start_round, signal_velocity, expiry_rate))

    def __try_deliver_broadcasts__(self, current_round, particle_map_coordinates):
        for sender, entries in list(self.broadcast_memory.items()):
            for entry in entries:
                receivers = self.__get_broadcast_receivers__(entry, current_round, particle_map_coordinates)
                self.__deliver__message(entry[0], receivers)

    def __calculate_distances__(self, actual_round, m, target, particle_map_id):
        position = m[1]
        start_round = m[2]
        signal_velocity = m[3]
        past_rounds = actual_round - start_round
        distance = signal_velocity * past_rounds
        if target in particle_map_id:
            vector = particle_map_id[target].coordinates
            particle_point = self.get_point_from_vector(vector)
            distance_start_target = get_distance(position, particle_point)
        else:
            distance_start_target = math.inf
        return distance, distance_start_target

    def try_deliver_messages(self, world):
        current_round = world.get_actual_round()
        particle_map_id = world.get_particle_map_id()
        self.__try_deliver_scheduled_messages__(current_round, particle_map_id)
        self.__try_deliver_delta_messages__(current_round, particle_map_id)
        self.__try_deliver_broadcasts__(current_round, world.get_particle_map_coordinates())

    @staticmethod
    def __deliver__message(message, receivers):
        for receiver in receivers:
            message.set_receiver(receiver)
            message.set_actual_receiver(receiver)
            store_message(message, message.get_sender(), receiver)

    @staticmethod
    def __get_broadcast_receivers__(entry, current_round, particle_map_coordinates):
        msg, position, start_round, signal_velocity, expiry_rate = entry
        traveled_distance = signal_velocity * (current_round - start_round)
        locations = get_hexagon_coordinates((position.getx(), position.gety()), traveled_distance, True)
        particle_locations = particle_map_coordinates.keys()
        receiving_particles = [particle_map_coordinates.get(key) for key in locations if key in particle_locations]
        return receiving_particles

    @staticmethod
    def get_point_from_vector(vector):
        return Point(vector[0], vector[1])
