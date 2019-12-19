from lib.oppnet.messagestore import MessageStore
from lib.particle import Particle


class Particle(Particle):
    def __init__(self, world, coordinates, color, ms_size=None, ms_strategy=None):
        super().__init__(world=world, coordinates=coordinates, color=color)
        if not ms_size:
            ms_size = world.particle_ms_size
        if not ms_strategy:
            ms_strategy = world.particle_ms_strategy
        self.send_store = MessageStore(maxlen=ms_size, strategy=ms_strategy)
        self.rcv_store = MessageStore(maxlen=ms_size, strategy=ms_strategy)
        self.signal_velocity = 1
