from lib.swarm_sim_header import *
import solution.message as message


def def_p_max (particle):
    if debug and debug_p_max_calculation:
        print("\n After P", particle.number, "own distance", particle.own_dist)
        print("Direction | Distance")
        for dir in direction_list:
            print(direction_number_to_string(dir), "|", particle.nh_dist_list[dir])
        print("Before P MAX:")
        print("id | dist | dir")
        print(particle.p_max)
    find_p_max(particle)
    upd_dat = check_for_update(particle.p_max, particle.rcv_buf, particle.own_dist, particle.number, particle.p_max_table)
    if upd_dat:
        particle.p_max_table.update(upd_dat)
    # if len(particle.p_max_table) > 0:
    #     particle.p_max.id = max(particle.p_max_table, key=particle.p_max_table.get)
    #     particle.p_max.dist = particle.p_max_table[particle.p_max.id]
    if debug and debug_p_max_calculation:
        print("P MAX:")
        print("id | dist | dir")
        print(particle.p_max)

    if debug and debug_p_max_calculation:
        print("P_Max Table \n ID | Distance")
        print(particle.p_max_table)


def find_p_max(particle):
    local_p_max(particle.own_dist, particle.p_max, particle.number, particle.nh_dist_list, particle.prev_dir, particle.p_max_table)
    global_p_max(particle.p_max, particle.rcv_buf, particle.nh_dist_list, particle.own_dist)
    find_identical(particle.p_max, particle.rcv_buf)
    # if particle.p_max.dist > particle.own_dist + 2:
    #     particle.p_max.dist = -math.inf


def global_p_max(p_max, rcv_buf, nh_list, own_dist):
    for rcv_dir in rcv_buf:
        if isinstance(rcv_buf[rcv_dir], message.PMax):
            if rcv_buf[rcv_dir].p_max_dist > p_max.dist:
                p_max.id = rcv_buf[rcv_dir].p_max_id
                p_max.dist = rcv_buf[rcv_dir].p_max_dist
                if nh_list[rcv_dir].dist == own_dist:
                    p_max.dir.append(rcv_dir)
                else:
                    p_max.dir = []
                p_max.black_list.clear()
                p_max.black_list.append(rcv_dir)
            elif rcv_buf[rcv_dir].p_max_dist == p_max.dist and nh_list[rcv_dir].dist == own_dist:
                p_max.dir.append(rcv_dir)
    return False


def local_p_max__(nh_list, p_max):
    for dir in direction_list:
        if nh_list[dir].type == "p" and p_max.dist < nh_list[dir].dist < math.inf:
            p_max.id = None
            p_max.black_list.clear()
            p_max.black_list.append(dir)
            p_max.dist = nh_list[dir].dist
            p_max.dir = dir
            return True
    return False


def local_p_max(own_distance, p_max, particle_number, nh_list, prev_dir, p_max_table):
    nearest_free_location = Neighbor("fl", math.inf)
    for dir in direction_list:
        if dir != prev_dir:
            neighbor = nh_list[dir]
            if neighbor.type == "fl" and neighbor.dist < nearest_free_location.dist:
                nearest_free_location.dist = neighbor.dist
            elif neighbor.type == "p" and own_distance < neighbor.dist:
                return False
    if nearest_free_location.dist >= own_distance and p_max.dist < own_distance < math.inf and \
            particle_number not in p_max_table.keys():
        p_max.id = particle_number
        p_max.black_list.clear()
        p_max.dist = own_distance
        p_max.dir = []
        return True
    return False


def find_identical(p_max, rcv_buf):
    for rcv_dir in rcv_buf:
        if isinstance(rcv_buf[rcv_dir], message.PMax) and rcv_buf[rcv_dir].p_max_dist == p_max.dist:
            if p_max.id != rcv_buf[rcv_dir].p_max_id:
                p_max.black_list.append(rcv_dir)


def check_for_update(p_max, rcv_buf, own_dist, own_id, p_max_table):
    update_dict = {}
    for rcv_dir in rcv_buf:
        if isinstance(rcv_buf[rcv_dir], message.PMax) and rcv_buf[rcv_dir].p_max_dist < p_max.dist \
                and rcv_buf[rcv_dir].p_max_id == p_max.id:
            p_max.id = rcv_buf[rcv_dir].p_max_id
            p_max.dist = rcv_buf[rcv_dir].p_max_dist
            p_max.dir.append(rcv_dir)
            p_max.black_list.clear()
            p_max.black_list.append(rcv_dir)
        elif isinstance(rcv_buf[rcv_dir], message.OwnDist) and rcv_buf[rcv_dir].own_dist < p_max.dist \
                and rcv_buf[rcv_dir].own_id == p_max.id:
            p_max.id = rcv_buf[rcv_dir].own_id
            p_max.dist = rcv_buf[rcv_dir].own_dist
            p_max.dir.append(rcv_dir)
            p_max.black_list.clear()
            p_max.black_list.append(rcv_dir)
        elif own_id == p_max.id and own_dist < p_max.dist:
            p_max.id = own_id
            p_max.dist = own_dist
            p_max.dir = []
            p_max.black_list.clear()
            p_max.black_list.append(rcv_dir)
        # if isinstance(rcv_buf[rcv_dir], message.PMax):
        #     foreign_p_max_table = rcv_buf[rcv_dir].p_max_table
        #     for particle_id in foreign_p_max_table.keys():
        #         if particle_id in p_max_table.keys():
        #             if foreign_p_max_table[particle_id] < p_max_table[particle_id]:
        #                 update_dict.update({particle_id: foreign_p_max_table[particle_id]})
        #         else:
        #             update_dict.update({particle_id: foreign_p_max_table[particle_id]})
        if p_max.id is not None:
            update_dict.update({p_max.id: p_max.dist})
    return update_dict


def update_table(rcv_buf, table, own_dist):
    table_a = table
    for rcv_dir in rcv_buf:
        if isinstance(rcv_buf[rcv_dir], message.PMax):
            if rcv_buf[rcv_dir].own_id in table_a and \
                    rcv_buf[rcv_dir].own_dist < table_a[rcv_buf[rcv_dir].own_id]:
                table_a[rcv_buf[rcv_dir].p_max_id] = rcv_buf[rcv_dir].own_dist
            if rcv_buf[rcv_dir].p_max_id in table_a and \
                rcv_buf[rcv_dir].p_max_dist < table_a[rcv_buf[rcv_dir].p_max_id]:
                table_a[rcv_buf[rcv_dir].p_max_id] = rcv_buf[rcv_dir].p_max_dist
            if rcv_buf[rcv_dir].p_max_id in table_a and \
                table_a[rcv_buf[rcv_dir].p_max_id] <= own_dist:
                del table_a[rcv_buf[rcv_dir].p_max_id]
    return table_a

