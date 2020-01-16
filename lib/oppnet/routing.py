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

    def __init__(self, algorithm, scan_radius, manet_role=None, manet_group=0):
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
        rp1, rp2 = particle1.routing_parameters, particle2.routing_parameters
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
        routing_params = particle.routing_parameters
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

    routing_params = sender.routing_parameters
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
    routing_params = particle.routing_parameters
    nearby = particle.scan_for_particles_within(hop=routing_params.scan_radius)
    if nearby is None:
        return

    if routing_params.manet_role == MANeTRole.Node:
        nearby = [neighbour for neighbour in nearby if RoutingParameters.same_manet_group(particle, neighbour)]
        __next_step_epidemic__(particle, nearby)

    elif routing_params.manet_role == MANeTRole.Router:
        __next_step_epidemic__(particle)


class RoutingContact:
    def __init__(self, contact_particle, target_particle, hops):
        self.__contact_particle__ = contact_particle
        self.__target_particle__ = target_particle
        self.__hops__ = hops

    def get_contact_particle(self):
        return self.__contact_particle__

    def get_target_particle(self):
        return self.__target_particle__

    def get_hops(self):
        return self.__hops__


class RoutingMap(dict):

    def __init__(self):
        super(RoutingMap, self).__init__()
        self.__max_hops_contact__ = None
        self.__max_hops__ = -1

    def add_contact(self, contact_particle, target_particle, hops, contact=None):
        if not contact:
            contact = RoutingContact(contact_particle, target_particle, hops)

        if target_particle not in self:
            contacts = dict({contact_particle: contact})
            self[target_particle] = contacts
        else:
            self[target_particle][contact_particle] = contact

        if contact.get_hops() > self.__max_hops__ or self.__max_hops_contact__ is None:
            self.__max_hops__ = contact.get_hops()
            self.__max_hops_contact__ = contact

    def get_contact(self, target_particle, contact_id):
        return self[target_particle][contact_id]

    def get_max_hops_(self):
        return self.__max_hops__

    def get_max_hops_contact(self):
        return self.__max_hops_contact__

    def update_contact(self, contact_particle, target_particle, hops):
        self.add_contact(contact_particle, target_particle, hops)

    def remove_contact(self, contact: RoutingContact):
        target_entry = self[contact.get_target_particle()]
        del target_entry[contact]

    def get_all_contact_particles(self):
        all_contacts = []
        for _, contacts in self.items():
            all_contacts.extend(contacts.keys())
        return all_contacts
