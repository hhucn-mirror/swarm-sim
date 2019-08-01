import configparser


class ConfigData:

    def __init__(self, config):

        self.seedvalue = config.getint("Simulator", "seedvalue")
        self.max_round = config.getint("Simulator", "max_round")
        self.random_order = config.getboolean("Simulator", "random_order")
        self.visualization = config.getint("Simulator", "visualization")

        try:
            self.scenario = config.get("File", "scenario")
        except configparser.NoOptionError as noe:
            self.scenario = "init_scenario.py"

        try:
            self.solution = config.get("File", "solution")
        except configparser.NoOptionError as noe:
            self.solution = "solution.py"

        self.size_x = config.getint("Simulator", "size_x")
        self.size_y = config.getint("Simulator", "size_y")
        self.window_size_x = config.getint("Simulator", "window_size_x")
        self.window_size_y = config.getint("Simulator", "window_size_y")
        self.border = config.getint("Simulator", "border")
        self.max_particles = config.getint("Simulator", "max_particles")
        self.mm_limitation = config.getboolean("Matter", "mm_limitation")
        self.particle_mm_size = config.getint("Matter", "particle_mm_size")
        self.tile_mm_size = config.getint("Matter", "tile_mm_size")
        self.location_mm_size = config.getint("Matter", "location_mm_size")
        self.dir_name = None

        # Marking Variables
        self.start_communication_round = config.getint("Marking", "start_communication_round")
        self.communication_frequency = config.getint("Marking", "communication_frequency")
        self.communication_range = config.getint("Marking", "communication_range")
        self.search_algorithm = config.getint("Marking", "search_algorithm")
        self.start_position = config_section_map(config, "Marking")['start_position']
        self.particles_num = config.getint("Marking", "particles_num")

        self.sq_size = config.getint("Marking", "sq_size")

def config_section_map(config, section):
    """
    This is a helper method which reads strings as there is no config.getstring() method
    see  line 40 for usage example
    """
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
        except:
            dict1[option] = None
    return dict1
