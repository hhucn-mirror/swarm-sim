from .utils import Utils


class ParticleGraph:
    list_particles = []

    def create_neighbor_graph(self, sim, particle, neighbors, loc_coords=None, empty=False):
        utils = Utils()
        particle_node = ParticleNode()
        particle_node.particle = particle
        particle_node.avoid = True
        neighbors_list = [None, None, None, None, None, None]
        for dir in range(0, 6):
            coords = []
            if empty:
                coords = loc_coords
            else:
                coords = utils.determine_coords_from_direction(particle.coords, dir)
            for nb in neighbors:
                if utils.compare_coords(coords, nb.coords):
                    nb_node = ParticleNode()
                    nb_node.particle = nb
                    nb_node.make_connection(utils.inv_dir(dir), particle_node)

                    particle_node.make_connection(dir, nb_node)
                    neighbors_list[dir] = nb_node
                    self.list_particles.append(nb_node)

        for i in range(0, 6):
            particle_node = neighbors_list[i]
            nb_left = neighbors_list[(i-1) % 6]
            nb_right = neighbors_list[(i+1) % 6]
            if particle_node is not None:
                if nb_left is not None:
                    particle_node.make_connection(-1, nb_left)
                    nb_left.make_connection(-1, particle_node)
                if nb_right is not None:
                    particle_node.make_connection(-1, nb_right)
                    nb_right.make_connection(-1, particle_node)

    def merge_graphs_at(self, graph2):
        temp_list = []
        for node in self.list_particles:
            temp_list.append(node)
        for node in temp_list:
            for node2 in graph2.list_particles:
                if node.particle == node2.particle:
                    node.make_connection(-1, node2)
                    node2.make_connection(-1, node)
                # else:
                    # self.list_particles.append(node2)

    def run_search_from(self, particle_node, visit=0, mark=0):
        if not particle_node.avoid and not particle_node.visited:
            if visit + mark > 0:
                if visit == 1:
                    particle_node.visited = True
                if mark == 1:
                    particle_node.marked = True
            for conn in particle_node.list_connections:
                self.run_search_from(conn.particle_node, visit, mark)

    def check_visited(self):
        for node in self.list_particles:
            if not node.visited:
                return False
        return True

    def check_marked(self):
        for node in self.list_particles:
            if not node.marked:
                return False
        return True

    def clear_search(self):
        for particle in self.list_particles:
            particle.visited = False
            particle.marked = False


class ParticleNode:
    particle = None
    list_connections = []
    visited = False
    marked = False
    avoid = False

    def make_connection(self, dir, node):
        conn = Connection()
        conn.dir = dir
        conn.particle_node = node
        self.list_connections.append(conn)


class Connection:
    dir = -1
    particle_node = None