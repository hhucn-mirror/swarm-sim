from enum import Enum

from lib.oppnet.communication import send_message


class Algorithm(Enum):
    """
    Used to distinguish routing algorithms.
    """
    Epidemic = 0
    Epidemic_MANeT = 1


class MANeTRole(Enum):
    """
    Used to distinguish roles of particles in a MANeT.
    """
    Router = 0
    Node = 1


class RoutingParameters:

    def __init__(self, algorithm, scan_radius, manet_role=None, manet_group=0, delivery_delay=2):
        """
        Constructor
        :param algorithm: The routing algorithm to be used.
        :type algorithm: :class:`~routing.Algorithm`
        :param scan_radius: Scan radius for particle scanning.
        :type scan_radius: int
        :param manet_role: Role of the particle in an MANeT island.
        :type manet_role: :class:`~routing.MANeTRole`
        :param manet_group: Group the particle belongs to.
        :type manet_group: int
        :param delivery_delay: The number of rounds to wait until the message is delivered.
        :type delivery_delay: int
        """
        if type(algorithm) == str:
            self.algorithm = Algorithm[algorithm]
        else:
            self.algorithm = algorithm
        self.manet_role = manet_role
        self.manet_group = manet_group
        if manet_role is None:
            self.manet_role = MANeTRole.Node
        self.scan_radius = scan_radius
        self.delivery_delay = delivery_delay

    def set(self, particle):
        """
        Sets attribute routing_params of :param particle:.
        :param particle: the particle whose attribute is set
        """
        setattr(particle, "routing_params", self)

    @staticmethod
    def get(particle):
        """
        Gets the routing_params attribute of :param particle:.
        :param particle: The particle to get the attribute from.
        :type particle: :class:`~particle.Particle`
        :return: MobilityModel of :param particle:.
        :rtype: :class:`~mobility_model.MobilityModel`
        """
        return getattr(particle, "routing_params")

    @staticmethod
    def same_manet_group(particle1, particle2):
        """
        Compares the MANeT groups of two particles :param particle1: and :param particle2:.
        :param particle1: First particle
        :type particle1: :class:`~particle.Particle`
        :param particle2: Second particle
        :type particle2: :class:`~particle.Particle`
        :return: If :param particle1: and :param particle2: are in the same MANeT group.
        :rtype: bool
        """
        rp1, rp2 = RoutingParameters.get(particle1), RoutingParameters.get(particle2)
        return rp1.manet_group == rp2.manet_group


def next_step(particles, scan_radius=None):
    """
    Executes the next routing steps for each particle in order.
    :param particles: List of particles
    :type particles: list
    :param scan_radius: Particle scan radius.
    :type scan_radius: int
    """
    # execute the SendEvents for each particle
    for particle in particles:
        routing_params = RoutingParameters.get(particle)
        if scan_radius is not None:
            routing_params.scan_radius = scan_radius

        if routing_params.algorithm == Algorithm.Epidemic_MANeT:
            __next_step_manet_epidemic__(particle)
        elif routing_params.algorithm == Algorithm.Epidemic:
            __next_step_epidemic__(particle)


def __next_step_epidemic__(sender, nearby=None):
    """
    Executes the next epidemic routing steps for a :param particle:.
    :param sender: The particle which creates .
    :type sender: :class:`~particle.Particle`
    :param nearby: Nearby particles to interact with.
    :type nearby: list
    """

    routing_params = RoutingParameters.get(sender)
    if nearby is None:
        nearby = sender.scan_for_particles_within(hop=routing_params.scan_radius)
        if nearby is None:
            return

    for msg in list(sender.send_store):
        for neighbour in nearby:
            send_message(sender, neighbour, msg)


def __next_step_manet_epidemic__(particle):
    """
    Executes the next manet epidemic for a :param particle: depending on MANeT role.
    :param particle: The particle which routing model should be executed.
    :type particle: :class:`~particle.Particle`
    """
    routing_params = RoutingParameters.get(particle)
    nearby = particle.scan_for_particles_within(hop=routing_params.scan_radius)
    if nearby is None:
        return

    if routing_params.manet_role == MANeTRole.Node:
        nearby = [neighbour for neighbour in nearby if RoutingParameters.same_manet_group(particle, neighbour)]
        __next_step_epidemic__(particle, nearby)

    elif routing_params.manet_role == MANeTRole.Router:
        __next_step_epidemic__(particle)
