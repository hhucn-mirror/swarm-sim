from lib.swarm_sim_header import *
from solution import solution_header


def find_p_max(particle):
    """
    calculates the p_max for a particle based on all information this particle has
    :param particle: the particle for which the p_max should be calculated
    :return: none
    """
    if debug and debug_p_max_calculation:
        print("\n After P", particle.number, "own distance", particle.own_dist)
        print("Direction | Distance")
        for direction in direction_list:
            print(direction_number_to_string(direction), "|", particle.nh_list[direction])
        print("Before P MAX:")
        print("id | dist | direction")
        print(particle.p_max)

    own_p_max(particle.own_dist, particle.p_max, particle.number, particle.nh_list, particle.prev_direction,
              particle.p_max_table)
    global_p_max(particle)
    #find_identical(particle.p_max, particle.rcv_buf)
    upd_dat = check_for_update(particle.p_max, particle.rcv_buf, particle.own_dist, particle.number, particle.p_max_table)

    #if upd_dat:
        #particle.p_max_table.update(upd_dat)
    # if len(particle.p_max_table) > 0:
    #     particle.p_max.id = max(particle.p_max_table, key=particle.p_max_table.get)
    #     particle.p_max.dist = particle.p_max_table[particle.p_max.id]
    if debug and debug_p_max_calculation:
        print("P MAX:")
        print("id | dist | direction")
        print(particle.p_max)

    if debug and debug_p_max_calculation:
        print("P_Max Table \n ID | Distance")
        print(particle.p_max_table)


def own_p_max(own_distance, p_max, particle_number, nh_list, prev_direction, p_max_table):
    """
    Checks if this particle has maximum distance
    :param own_distance: the distance of this particle
    :param p_max: the current p_max of this particle
    :param particle_number: the particles id
    :param nh_list: the particles neighborhood
    :param prev_direction: the direction the particle came fro mwith it's last movement
    :param p_max_table: unused
    :return: True if this particle is at maximum distance, False otherwise
    """
    nearest_free_location = solution_header.Neighbor("fl", math.inf)
    for direction in direction_list:
        if direction != prev_direction:
            neighbor = nh_list[direction]
            if neighbor.type == "fl" and neighbor.dist < nearest_free_location.dist:
                nearest_free_location.dist = neighbor.dist
            elif neighbor.type == "p" and own_distance < neighbor.dist:
                return False
    if nearest_free_location.dist >= own_distance and p_max.dist < own_distance < math.inf and \
            particle_number not in p_max_table.keys():
        p_max.ids = {particle_number}
        p_max.black_list.clear()
        p_max.dist = own_distance
        p_max.directions = []
        return True
    return False


def global_p_max(particle):
    """
    Finds the greatest p_max in all messages received
    :param particle: the particle for which the p_max should be calculated
    :return: False
    """
    for rcv_direction in particle.rcv_buf:
        if isinstance(particle.rcv_buf[rcv_direction], solution_header.PMax):
            if particle.rcv_buf[rcv_direction].p_max_dist > particle.p_max.dist:
                particle.p_max.ids = particle.rcv_buf[rcv_direction].p_max_ids
                particle.p_max.dist = particle.rcv_buf[rcv_direction].p_max_dist
                if particle.nh_list[rcv_direction].dist == particle.own_dist:
                    particle.p_max.directions.append(rcv_direction)
                else:
                    particle.p_max.directions = []
                particle.p_max.black_list.clear()
                particle.p_max.black_list.append(rcv_direction)
            elif particle.rcv_buf[rcv_direction].p_max_dist == particle.p_max.dist:
                if any(id in particle.rcv_buf[rcv_direction].p_max_ids for id in particle.p_max.ids):
                    particle.broadcast_pmax = True
                else:
                    particle.p_max.ids |= particle.rcv_buf[rcv_direction].p_max_ids
                if particle.nh_list[rcv_direction].dist == particle.own_dist:
                    particle.p_max.directions.append(rcv_direction)
    return False


def find_identical(p_max, rcv_buf):
    """
    unused
    :param p_max:
    :param rcv_buf:
    :return:
    """
    for rcv_direction in rcv_buf:
        if isinstance(rcv_buf[rcv_direction], solution_header.PMax) and rcv_buf[rcv_direction].p_max_dist == p_max.dist:
            if any(id in rcv_buf[rcv_direction].p_max_ids for id in p_max.ids):
                p_max.black_list.append(rcv_direction)


def check_for_update(p_max, rcv_buf, particle_distance, particle_id, p_max_table):
    """
    Checks if multiple message send either the same p_max distance or have the same p_max id
    :param p_max: the particles current p_max
    :param rcv_buf: all messages in this particles memory
    :param particle_distance: the particles current distance
    :param particle_id: the particles id
    :param p_max_table: unused
    :return: True
    """
    update_dict = {}
    for rcv_direction in rcv_buf:
        # checks if the current p_max is outdated and should be reduced
        check_p_max_messages(p_max, rcv_buf, rcv_direction)
        check_sender_particle_is_p_max(p_max, rcv_buf, rcv_direction)
        check_if_self_is_p_max(p_max, particle_distance, particle_id, rcv_direction)

        # if isinstance(rcv_buf[rcv_direction], solution_header.PMax):
        #     foreign_p_max_table = rcv_buf[rcv_direction].p_max_table
        #     for particle_id in foreign_p_max_table.keys():
        #         if particle_id in p_max_table.keys():
        #             if foreign_p_max_table[particle_id] < p_max_table[particle_id]:
        #                 update_dict.update({particle_id: foreign_p_max_table[particle_id]})
        #         else:
        #             update_dict.update({particle_id: foreign_p_max_table[particle_id]})
        # if len(p_max.ids) > 0:
            # update_dict.update({p_max.ids: p_max.dist})
    return True


def check_p_max_messages(p_max, rcv_buf, rcv_direction):
    if isinstance(rcv_buf[rcv_direction], solution_header.PMax) and rcv_buf[rcv_direction].p_max_dist < p_max.dist \
            and any(id in rcv_buf[rcv_direction].p_max_ids for id in p_max.ids):
        p_max.ids = rcv_buf[rcv_direction].p_max_ids
        p_max.dist = rcv_buf[rcv_direction].p_max_dist
        p_max.directions.append(rcv_direction)
        p_max.black_list.clear()
        p_max.black_list.append(rcv_direction)


def check_sender_particle_is_p_max(p_max, rcv_buf, rcv_direction):
    if isinstance(rcv_buf[rcv_direction], solution_header.OwnDistance) and rcv_buf[
        rcv_direction].particle_distance < p_max.dist \
            and rcv_buf[rcv_direction].particle_id in p_max.ids:
        p_max.ids = {rcv_buf[rcv_direction].particle_id}
        p_max.dist = rcv_buf[rcv_direction].particle_distance
        p_max.directions.append(rcv_direction)
        p_max.black_list.clear()
        p_max.black_list.append(rcv_direction)


def check_if_self_is_p_max(p_max, particle_distance, particle_id, rcv_direction):
    if particle_id in p_max.ids and particle_distance < p_max.dist:
        p_max.ids = {particle_id}
        p_max.dist = particle_distance
        p_max.directions = []
        p_max.black_list.clear()
        p_max.black_list.append(rcv_direction)


def update_table(rcv_buf, table, own_dist):
    """
    unused
    :param rcv_buf:
    :param table:
    :param own_dist:
    :return:
    """
    table_a = table
    for rcv_direction in rcv_buf:
        if isinstance(rcv_buf[rcv_direction], solution_header.PMax):
            if rcv_buf[rcv_direction].particle_id in table_a and \
                    rcv_buf[rcv_direction].particle_distance < table_a[rcv_buf[rcv_direction].particle_id]:
                table_a[rcv_buf[rcv_direction].p_max_id] = rcv_buf[rcv_direction].particle_distance
            if rcv_buf[rcv_direction].p_max_id in table_a and \
                rcv_buf[rcv_direction].p_max_dist < table_a[rcv_buf[rcv_direction].p_max_id]:
                table_a[rcv_buf[rcv_direction].p_max_id] = rcv_buf[rcv_direction].p_max_dist
            if rcv_buf[rcv_direction].p_max_id in table_a and \
                table_a[rcv_buf[rcv_direction].p_max_id] <= own_dist:
                del table_a[rcv_buf[rcv_direction].p_max_id]
    return table_a

