
# elects leader with the highest id
def elect(particle_list):
    for particle in particle_list:
        send_max_id_to_all_nbs(particle)
    for particle in particle_list:
        if particle.number == particle.read_memory_with("MaxID"):
            particle.write_memory_with("Leader", 1)
            particle.set_color(4)

# sends max id to all nbs and recursivley the nbs send it to their nbs
def send_max_id_to_all_nbs(particle):
    nbs = particle.scan_for_particle_within(hop=1)
    for nb in nbs:
        if nb.read_memory_with("MaxID") < particle.read_memory_with("MaxID"):
            particle.write_to_with(nb, "MaxID", particle.read_memory_with("MaxID"))
            send_max_id_to_all_nbs(nb)

def get_random_particle(particle_list):
    return particle_list[0]
