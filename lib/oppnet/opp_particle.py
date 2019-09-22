from lib.oppnet.messagestore import MessageStore, BufferStrategy
from lib.particle import Particle
from lib.std_lib import black


class Particle(Particle):
    def __init__(self, sim, x, y, color=black, alpha=1, mm_size=0, ms_size=100,
                 ms_strategy=BufferStrategy.fifo):
        super().__init__(sim, x, y, color, alpha, mm_size=mm_size)
        self.send_store = MessageStore(maxlen=ms_size, strategy=ms_strategy)
        self.fwd_store = MessageStore(maxlen=ms_size, strategy=ms_strategy)
        self.rcv_store = MessageStore(maxlen=ms_size, strategy=ms_strategy)
