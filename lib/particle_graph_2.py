from .utils import Utils


class ParticleGraph:
    list_particle_nodes = []

    def check_connectivity_after_move(self, coords, neighbors, dir):
        self.list_particle_nodes = []
        neighbors_nodes = []
        for nb in neighbors:
            new_node = ParticleNode()
            # new_node.list_connections = []
            new_node.particle = nb
            neighbors_nodes.append(new_node)
            self.list_particle_nodes.append(new_node)
        utils = Utils()
        for node in neighbors_nodes:
            particle = node.particle
            for nb_dir in range(0, 6):
                coords_a = utils.determine_coords_from_direction(particle.coords, nb_dir)
                for node2 in neighbors_nodes:
                    particle2 = node2.particle
                    coords_b = particle2.coords
                    if utils.compare_coords(coords_a, coords_b):
                        node.make_connection(nb_dir, node2)
        coords_empty_space = utils.determine_coords_from_direction(coords, dir)
        dummy_node = ParticleNode()
        dummy_node.list_connections = []
        self.list_particle_nodes.append(dummy_node)
        for dirval in range(0, 6):
            coords_nb = utils.determine_coords_from_direction(coords_empty_space, dirval)
            for dummy_nb in neighbors_nodes:
                if utils.compare_coords(coords_nb, dummy_nb.particle.coords):
                    dummy_node.make_connection(-1, dummy_nb)
                    dummy_nb.make_connection(-1, dummy_node)
        self.clear_search()
        self.run_search_from(dummy_node)
        checked = self.check_visited()
        return [checked, len(dummy_node.list_connections)]

    def run_search_from(self, particle_node):
        if not particle_node.visited:
            particle_node.visited = True
            for conn in particle_node.list_connections:
                self.run_search_from(conn.particle_node)

    def check_visited(self):
        for node in self.list_particle_nodes:
            if not node.visited:
                return False
        return True

    def check_marked(self):
        for node in self.list_particle_nodes:
            if not node.marked:
                return False
        return True

    def clear_search(self):
        for particle in self.list_particle_nodes:
            particle.visited = False
            particle.marked = False


class ParticleNode:
    particle = None
    list_connections = []
    visited = False
    marked = False
    avoid = False

    def __init__(self):
        self.particle = None
        self.list_connections = []
        self.visited = False
        self.marked = False
        self.avoid = False

    def make_connection(self, dir, node):
        conn = Connection()
        conn.dir = dir
        conn.particle_node = node
        self.list_connections.append(conn)


class Connection:
    dir = -1
    particle_node = None