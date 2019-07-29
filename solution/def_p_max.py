
def def_p_max (particle):
    if debug:
        print("\n After P", particle.number, "own distance", particle.own_dist)
        print("Direction | Distance")
        for dir in direction:
            print(dir_to_str(dir), "|", particle.nh_dist_list[dir])
        print("Before P MAX:")
        print("id | dist | dir")
        print(particle.p_max)
    find_p_max(particle.p_max, nh_list, particle.rcv_buf)
    upd_dat = check_for_update(particle.p_max, particle.rcv_buf, particle.own_dist, particle.number)
    if upd_dat:
        particle.p_max_table.update(upd_dat)

    if debug:
        print ("P MAX:")
        print("id | dist | dir")
        print(particle.p_max)

    if debug:
        print("P_Max Table \n ID | Distance")
        print ( particle.p_max_table)


def find_p_max(p_max, nh_list, rcv_buf):
    local_p_max(nh_list, p_max)
    global_p_max(p_max, rcv_buf)
    find_identical(p_max, rcv_buf)


def global_p_max(p_max, rcv_buf):
    for rcv_dir in rcv_buf:
        if isinstance(rcv_buf[rcv_dir], DistInfo):
            if rcv_buf[rcv_dir].p_max_dist > p_max.dist:
                p_max.id = rcv_buf[rcv_dir].p_max_id
                p_max.dist = rcv_buf[rcv_dir].p_max_dist
                p_max.dir = rcv_dir
                p_max.black_list.clear()
                p_max.black_list.append(rcv_dir)
                return True
    return False


def local_p_max(nh_list, p_max):
    for dir in direction:
        if nh_list[dir].type == "p" and nh_list[dir].dist > p_max.dist:
            p_max.id = None
            p_max.black_list.clear()
            p_max.black_list.append(dir)
            p_max.dist = nh_list[dir].dist
            p_max.dir = dir
            return True
    return False


def find_identical(p_max, rcv_buf):
    for rcv_dir in rcv_buf:
        if isinstance(rcv_buf[rcv_dir], DistInfo) and rcv_buf[rcv_dir].p_max_dist == p_max.dist:
            if p_max.id != rcv_buf[rcv_dir].p_max_id:
                p_max.black_list.append(rcv_dir)
        if (isinstance(rcv_buf[rcv_dir], DistInfo) or \
                isinstance(rcv_buf[rcv_dir], OwnInfo)) and \
                p_max.id is None and rcv_buf[rcv_dir].own_dist == p_max.dist:
            p_max.id = rcv_buf[rcv_dir].own_id
            p_max.dir = rcv_dir


def check_for_update(p_max, rcv_buf, own_dist, own_id):
    update_dict = {}
    for rcv_dir in rcv_buf:
        if isinstance(rcv_buf[rcv_dir], DistInfo) and rcv_buf[rcv_dir].p_max_dist < p_max.dist \
                and rcv_buf[rcv_dir].p_max_id == p_max.id:
            p_max.id = rcv_buf[rcv_dir].p_max_id
            p_max.dist = rcv_buf[rcv_dir].p_max_dist
            p_max.dir = rcv_dir
            p_max.black_list.clear()
            p_max.black_list.append(rcv_dir)
        elif isinstance(rcv_buf[rcv_dir], OwnInfo) and rcv_buf[rcv_dir].own_dist < p_max.dist \
                and rcv_buf[rcv_dir].own_id == p_max.id:
            p_max.id = rcv_buf[rcv_dir].own_id
            p_max.dist = rcv_buf[rcv_dir].own_dist
            p_max.dir = rcv_dir
            p_max.black_list.clear()
            p_max.black_list.append(rcv_dir)
        elif own_id == p_max.id and own_dist < p_max.dist:
            p_max.id = own_id
            p_max.dist = own_dist
            p_max.dir = None
            p_max.black_list.clear()
            p_max.black_list.append(rcv_dir)
        update_dict.update({p_max.id: p_max.dist})
    return update_dict


def update_table(rcv_buf, table, own_dist):
    table_a = table
    for rcv_dir in rcv_buf:
        if isinstance(rcv_buf[rcv_dir], DistInfo):
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

