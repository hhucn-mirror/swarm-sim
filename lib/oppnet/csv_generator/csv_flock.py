import csv
import logging

from lib.oppnet.util import get_max_flock_radius, optimal_flock_distance, all_pairs_flock_distance, flock_spread, \
    flock_uniformity


class CsvFlockRoundData:
    """
    Collects metrics about a flock for each round.
    Contains :class:`~csv_generator.FlockData` objects.
    """

    def __init__(self, grid, directory="outputs/", solution=""):
        """
        :param grid: the simulation grid object
        :param solution: The simulator solution used
        :type: solution: str
        :param directory: The directory for the csv to be put in.
        :type directory: str
        """
        self.solution = solution
        self.flock_data = []
        self.directory = directory
        self.grid = grid

    def add_flock(self, flock):
        self.flock_data.append(FlockRoundData(flock))

    def __del__(self):
        """
        Destructor that writes the csv rows.
        """
        self.write_rows()

    def write_rows(self):
        """
        Writes rows for all flocks.
        """
        for flock_number, flock_round_data in enumerate(self.flock_data):
            file_name = self.directory + '/flock_{}.csv'.format(flock_number)
            data_rows = self.get_data_rows(flock_round_data)
            self.write_csv_file(file_name, data_rows)

    def write_csv_file(self, file_name, data_rows):
        with open(file_name, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(self.get_header_row())
            csv_writer.writerows(data_rows)

    def get_data_rows(self, flock_round_data):
        data_rows = []
        for sim_round in range(0, flock_round_data.get_recorded_rounds()):
            data_rows.append(self.get_data_row(sim_round, flock_round_data.get_round_directions(sim_round),
                                               flock_round_data.get_round_coordinates(sim_round)))
        return data_rows

    def get_data_row(self, sim_round, particle_directions, particle_coordinates):
        particles_count = len(particle_directions)
        flock_radius = get_max_flock_radius(particles_count)

        optimal_all_pairs_distance = optimal_flock_distance(flock_radius)
        all_pairs_distance = all_pairs_flock_distance(particle_coordinates)
        all_pairs_optimality = optimal_all_pairs_distance / all_pairs_distance
        if all_pairs_distance < optimal_all_pairs_distance:
            logging.debug("WARNING: csv_generator -> get_data_row(): all_pairs_distance < optimal_all_pairs_distance")

        spread_euclidean, spread_hops, center_coordinates = flock_spread(particle_coordinates, self.grid)

        return [sim_round, particles_count, flock_radius, optimal_all_pairs_distance,
                all_pairs_distance, all_pairs_optimality, flock_uniformity(particle_directions),
                spread_euclidean, spread_hops, center_coordinates]

    def update_metrics(self):
        for flock_round_data in self.flock_data:
            flock_round_data.update()

    @staticmethod
    def get_header_row():
        return ['Round', 'Flock Size', 'Flock Radius', 'Optimal All-Pairs Distance', 'Actual All-Pairs Distance',
                'All-Pairs Distance Optimality', 'Uniformity', 'Euclidean Spread', 'Hop Spread', 'Flock Center']


class FlockRoundData:
    def __init__(self, particles):
        self._particles = particles
        self.particles_round_coordinates = [[particle.coordinates for particle in particles]]
        self.particles_directions = [[particle.mobility_model.current_dir for particle in particles]]

    def update(self):
        self.particles_round_coordinates.append([particle.coordinates for particle in self._particles])
        self.particles_directions.append([particle.mobility_model.current_dir for particle in self._particles])

    def get_round_coordinates(self, sim_round):
        return self.particles_round_coordinates[sim_round]

    def get_round_directions(self, sim_round):
        return self.particles_directions[sim_round]

    def get_recorded_rounds(self):
        return len(self.particles_directions)
