import math
from enum import Enum

from lib.oppnet.communication import store_message
from lib.oppnet.meta import process_event, EventType
from lib.oppnet.point import Point


class MemoryMode(Enum):
    Schedule = 0
    Delta = 1
    Broadcast = 2


class Memory:
    def __init__(self, mode):
        self.memory = {}
        self.mode = mode

    def add_scheduled_message_on(self, target_id, round_number, msg):
        if self.mode == MemoryMode.Schedule:
            if round_number in self.memory.keys():
                self.memory[round_number] = self.memory.get(target_id).append((target_id, msg))
            else:
                self.memory[round_number] = [(target_id, msg)]
        else:
            raise NotImplementedError

    def try_deliver_scheduled_messages(self, world):
        if world.get_actual_round() in self.memory.keys():
            m_particles = world.get_particle_map_id()
            tuples_particles = self.memory.pop(world.get_actual_round())
            for e in tuples_particles:
                p_id = e[0]
                p_msg = e[1]
                if p_id in m_particles.keys():
                    p = m_particles.get(p_id)
                    p.write_memory(p_msg)

    def add_delta_message_on(self, target_id, msg, position, start_round, signal_velocity, expiry_rate):
        if self.mode == MemoryMode.Delta:
            process_event(EventType.MessageSent, msg)  # TODO rethink section
            if target_id in self.memory.keys():
                self.memory.get(target_id).append((msg, position, start_round, signal_velocity, expiry_rate))
            else:
                self.memory[target_id] = [(msg, position, start_round, signal_velocity, expiry_rate)]

        else:
            raise NotImplementedError

    def try_deliver_delta_messages(self, world):
        actual_round = world.get_actual_round()
        new_memory = {}
        for target in self.memory.keys():
            new_msgs = []
            for m in self.memory[target]:
                msg = m[0]
                expiry_rate = m[4]
                distance, distance_start_target = self.__calculate_distances__(actual_round, m, target, world)
                if distance < expiry_rate:
                    if distance >= distance_start_target:
                        store_message(msg, msg.get_sender(), msg.get_receiver())
                    else:
                        new_msgs.append(m)
            if len(new_msgs) > 0:
                new_memory[target] = new_msgs
        self.memory = new_memory

    def add_broadcast_message(self, msg, position, start_round, signal_velocity, expiry_rate):
        if self.mode == MemoryMode.Broadcast:
            process_event(EventType.MessageSent, msg)
            sender_id = msg.get_sender().get_id()
            if msg.get_sender() in self.memory.keys():
                self.memory[sender_id] = []
            self.memory[sender_id].append((msg, position, start_round, signal_velocity, expiry_rate))
        else:
            raise NotImplementedError

    def try_deliver_broadcasts(self, world):
        for sender_id, entries in list(self.memory.items()):
            for entry in entries:
                receivers = self.__get_broadcast_receivers__(entry, world)
                self.__deliver__message(entry[0], receivers)

    @staticmethod
    def __deliver__message(message, receivers):
        for receiver in receivers:
            store_message(message, message.get_sender(), receiver)

    def __get_broadcast_receivers__(self, entry, world):
        msg, position, start_round, signal_velocity, expiry_rate = entry
        traveled_distance = signal_velocity * (world.get_actual_round() - start_round)
        locations = self.__get_location_coordinates__(position, traveled_distance)
        receivers = []
        for particle_coordinates, particle in world.get_particle_map_coordinates().items():
            if particle_coordinates in locations:
                receivers.append(particle)
        return receivers

    @staticmethod
    def __get_location_coordinates__(centre, r_max):
        locations = {centre}
        displacement = - r_max + 0.5
        iteration = 0
        for i in range(1, r_max + 1):
            locations.add((i, centre[1]))
            locations.add((-i, centre[1]))
        for i in range(1, r_max + 1):
            for j in range(0, (2 * r_max) - iteration):
                locations.add((displacement + j + centre[0], i + centre[1]))
                locations.add((displacement + j + centre[0], -i + centre[1]))
            iteration = iteration + 1
            displacement = displacement + 0.5
        return locations
    
    def __calculate_distances__(self, actual_round, m, target, world):
        position = m[1]
        start_round = m[2]
        signal_velocity = m[3]
        past_rounds = actual_round - start_round
        distance = signal_velocity * past_rounds
        if target in world.get_particle_map_id():
            vector = world.get_particle_map_id()[target].coordinates
            particle_point = self.get_point_from_vector(vector)
            distance_start_target = self.get_distance(position, particle_point)
        else:
            distance_start_target = math.inf
        return distance, distance_start_target

    @staticmethod
    def get_point_from_vector(vector):
        return Point(vector[0], vector[1])

    @staticmethod
    def get_distance(position1, position2):
        x1, y1 = position1.getx(), position1.gety()
        x2, y2 = position2.getx(), position2.gety()
        x_diff = abs(x2 - x1)
        y_diff = abs(y2 - y1)

        if y1 == y2 and x1 != x2:
            return x_diff
        elif (x_diff - y_diff * 0.5) > 0:
            return y_diff + (x_diff - y_diff * 0.5)
        else:
            return y_diff

    def try_deliver_messages(self, world):
        self.option[self.mode](self, world)

    option = {MemoryMode.Schedule: try_deliver_scheduled_messages,
              MemoryMode.Delta: try_deliver_delta_messages}
