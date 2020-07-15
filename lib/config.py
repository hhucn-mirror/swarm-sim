import configparser
import importlib
import json
from ast import literal_eval as make_tuple
from datetime import datetime

from lib.oppnet.memory import MemoryMode
from lib.oppnet.messagestore import BufferStrategy
from lib.oppnet.mobility_model import MobilityModelMode
from lib.oppnet.predator import PursuitMode
from lib.oppnet.routing import Algorithm, RoutingParameters


class ConfigData:

    def __init__(self):
        config = configparser.ConfigParser(allow_no_value=True)
        config.read("config.ini")
        self.seed_value = config.getint("Simulator", "seedvalue")
        self.max_round = config.getint("Simulator", "max_round")
        self.particle_random_order = config.getboolean("Simulator", "particle_random_order")
        self.particle_random_order_always = config.getboolean("Simulator", "particle_random_order_always")
        self.window_size_x = config.getint("Simulator", "window_size_x")
        self.window_size_y = config.getint("Simulator", "window_size_y")

        self.visualization = config.getint("Visualization", "visualization")
        try:
            self.gui = config.get("Visualization", "gui")
        except configparser.NoOptionError as noe:
            print("no gui option given. setting to default \"gui.py\"")
            self.gui = "gui.py"

        try:
            self.grid_class = config.get("Visualization", "grid_class")
        except configparser.NoOptionError as noe:
            raise RuntimeError("Fatal Error: no grid class defined in config.ini!")

        try:
            self.grid_size = config.getint("Visualization", "grid_size")
        except configparser.NoOptionError as noe:
            raise RuntimeError("Fatal Error: no grid size defined in config.ini!")

        test = getattr(importlib.import_module("grids.%s" % self.grid_class), self.grid_class)
        self.grid = test(self.grid_size)

        self.particle_model_file = config.get("Visualization", "particle_model_file")
        self.tile_model_file = config.get("Visualization", "tile_model_file")
        self.location_model_file = config.get("Visualization", "location_model_file")
        self.predator_model_file = config.get("Visualization", "predator_model_file")

        self.particle_color = make_tuple(config.get("Visualization", "particle_color"))
        self.tile_color = make_tuple(config.get("Visualization", "tile_color"))
        self.location_color = make_tuple(config.get("Visualization", "location_color"))
        self.predator_color = make_tuple((config.get("Visualization", "predator_color")))
        self.particle_scaling = make_tuple(config.get("Visualization", "particle_scaling"))
        self.tile_scaling = make_tuple(config.get("Visualization", "tile_scaling"))
        self.location_scaling = make_tuple(config.get("Visualization", "location_scaling"))
        self.predator_scaling = make_tuple(config.get("Visualization", "predator_scaling"))
        self.grid_color = make_tuple(config.get("Visualization", "grid_color"))
        self.cursor_color = make_tuple(config.get("Visualization", "cursor_color"))
        self.background_color = make_tuple(config.get("Visualization", "background_color"))
        self.center_color = make_tuple(config.get("Visualization", "center_color"))
        self.line_color = make_tuple(config.get("Visualization", "line_color"))
        self.line_scaling = make_tuple(config.get("Visualization", "line_scaling"))
        self.show_lines = config.getboolean("Visualization", "show_lines")
        self.coordinates_color = make_tuple(config.get("Visualization", "coordinates_color"))
        self.coordinates_scaling = make_tuple(config.get("Visualization", "coordinates_scaling"))
        self.show_coordinates = config.getboolean("Visualization", "show_coordinates")
        self.show_center = config.getboolean("Visualization", "show_center")
        self.focus_color = make_tuple(config.get("Visualization", "focus_color"))
        self.show_focus = config.getboolean("Visualization", "show_focus")

        self.look_at = make_tuple(config.get("Visualization", "look_at"))
        self.phi = config.getint("Visualization", "phi")
        self.theta = config.getint("Visualization", "theta")
        self.radius = config.getint("Visualization", "radius")
        self.fov = config.getint("Visualization", "fov")
        self.cursor_offset = config.getint("Visualization", "cursor_offset")
        self.render_distance = config.getint("Visualization", "render_distance")

        self.size_x = config.getfloat("World", "size_x")
        self.size_y = config.getfloat("World", "size_y")
        self.border = config.getboolean("World", "border")
        self.max_particles = config.getint("World", "max_particles")

        self.memory_limitation = config.getboolean("Matter", "memory_limitation")
        self.particle_mm_size = config.getint("Matter", "particle_mm_size")
        self.tile_mm_size = config.getint("Matter", "tile_mm_size")
        self.location_mm_size = config.getint("Matter", "location_mm_size")

        self.message_store_size = config.getint("Routing", "ms_size")
        self.message_store_strategy = BufferStrategy(config.getint("Routing", "ms_strategy"))
        routing_algorithm = Algorithm(config.getint("Routing", "algorithm"))
        interaction_radius = config.getint("Routing", "interaction_radius")
        l_encounter = config.getfloat("Routing", "l_encounter")
        gamma = config.getfloat("Routing", "gamma")
        beta = config.getfloat("Routing", "beta")
        p_init = config.getfloat("Routing", "p_init")
        self.routing_parameters = RoutingParameters(routing_algorithm, interaction_radius, l_encounter=l_encounter,
                                                    gamma=gamma, beta=beta, p_init=p_init)

        self.message_ttl = config.getint("Routing", "message_ttl")

        self.signal_velocity = config.getint("Communication", "signal_velocity")
        self.signal_range = config.getint("Communication", "signal_range")

        self.mobility_model_mode = MobilityModelMode(config.getint("MobilityModel", "mm_mode"))
        self.mobility_model_length = json.loads(config.get("MobilityModel", "mm_length"))
        self.mobility_model_zone = json.loads(config.get("MobilityModel", "mm_zone"))
        if config.has_option("MobilityModel", "mm_starting_dir"):
            self.mobility_model_starting_dir = json.loads(config.get("MobilityModel", "mm_starting_dir"))
            if type(self.mobility_model_starting_dir) is list:
                self.mobility_model_starting_dir = tuple(self.mobility_model_starting_dir)
            elif type(self.mobility_model_starting_dir) == str and self.mobility_model_starting_dir == 'random':
                self.mobility_model_starting_dir = 'random'
        else:
            self.mobility_model_starting_dir = None

        self.memory_mode = MemoryMode(config.getint("Memory", "memory_mode"))

        self.flock_radius = config.getint("Flocking", "flock_radius")
        self.leader_count = config.getint("Flocking", "leader_count")
        self.commit_quorum = config.getfloat("Flocking", "commit_quorum")
        self.propagate_predator_signal = config.getboolean("Flocking", "propagate_predator_signal")
        # predator config
        self.predator_interaction_radius = config.getint("Flocking", "predator_interaction_radius")
        self.predator_pursuit_mode = PursuitMode(config.getint("Flocking", "predator_pursuit_mode"))
        self.predator_pursuit_rounds = config.getint("Flocking", "predator_pursuit_rounds")
        self.predator_initial_amount = config.getint("Flocking", "predator_initial_amount")
        try:
            self.scenario = config.get("File", "scenario")
        except configparser.NoOptionError as noe:
            self.scenario = "init_scenario.py"

        try:
            self.solution = config.get("File", "solution")
        except configparser.NoOptionError as noe:
            self.solution = "solution.py"

        try:
            self.csv_generator = config.get("File", "csv_generator")
        except configparser.NoOptionError as noe:
            self.csv_generator = "lib.csv_generator.py"

        try:
            self.particle = config.get("File", "particle")
        except configparser.NoOptionError as noe:
            self.particle = "lib.particle.py"

        self.local_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')[:-1]
        self.multiple_sim = 0
