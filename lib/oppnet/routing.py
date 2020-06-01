from enum import Enum

from lib.oppnet.communication import send_message

PROB_KEY = 'PROB_KEY'


class Algorithm(Enum):
    """
    Used to distinguish routing algorithms.
    """
    Epidemic = 0
    Epidemic_MANeT = 1
    Prophet = 2


class MANeTRole(Enum):
    """
    Used to distinguish roles of particles in a MANeT.
    """
    Router = 0
    Node = 1


class RoutingParameters:

    def __init__(self, algorithm, scan_radius, manet_role=None, manet_group=0, delivery_delay=2,
                 l_encounter=.75, gamma=.99, beta=.25, p_init=.75):
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
        :param l_encounter: the encounter impact for any particle in PRoPHET
        :type l_encounter: float
        :param gamma: age scaling for PRoPHET
        :type gamma: float
        :param beta: the encounter impact for the receiving particle in PRoPHET
        :type beta: float
        :param p_init: initial estimated delivery probability in PRoPHET
        :type p_init: float
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
        self.l_encounter = l_encounter
        self.gamma = gamma
        self.beta = beta
        self.p_init = p_init

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
        elif routing_params.algorithm == Algorithm.Prophet:
            __next_step_prophet__(particle)


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
        nearby = sender.scan_for_particle_within(hop=routing_params.scan_radius)
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
    nearby = particle.scan_for_particle_within(hop=routing_params.scan_radius)
    if nearby is None:
        return

    if routing_params.manet_role == MANeTRole.Node:
        nearby = [neighbour for neighbour in nearby if RoutingParameters.same_manet_group(particle, neighbour)]
        __next_step_epidemic__(particle, nearby)

    elif routing_params.manet_role == MANeTRole.Router:
        __next_step_epidemic__(particle)


def __next_step_prophet__(particle):
    """
    Executes the next PRoPHET routing step for :param particle.
    :param particle: The particle which routing model should be executed.
    :type particle: :class:`~particle.Particle`
    """
    routing_params = RoutingParameters.get(particle)
    nearby = particle.scan_for_particle_within(hop=routing_params.scan_radius)
    probabilities = __age_delivery_probability__(particle, routing_params)
    if nearby:
        for encounter in nearby:
            (current_probability, last_encounter_round) = probabilities[encounter.get_id()]
            current_probability = __update_estimated_probability__(current_probability, routing_params)
            probabilities = __try_and_transfer_messages__(particle, probabilities, current_probability,
                                                          routing_params, encounter)

    particle.write_to_with(matter=particle, key=PROB_KEY, data=probabilities)


def __age_delivery_probability__(particle, routing_params):
    """
    Ages the estimated delivery probability for each entry in the probability dictionary of :param particle.
    :param particle: the particle of which probabilities to update
    :type particle: :class:`~particle.Particle`
    :param routing_params: the routing parameters of the :param particle
    :type routing_params: :class:`~routing.RoutingParameters`
    :return: the particles updated delivery probabilities
    :rtype:  dict
    """
    probabilities = particle.read_from_with(matter=particle, key=PROB_KEY)
    current_round = particle.sim.get_actual_round()
    for receiver_id, (probability, last_encounter_round) in probabilities.items():
        probability = probability * pow(routing_params.gamma, (current_round - last_encounter_round))
        probabilities[receiver_id] = (probability, last_encounter_round)
    return probabilities


def __update_estimated_probability__(current_probability, routing_params):
    """
    Updates the estimated delivery probability for an encountered particle.
    :param current_probability: the current estimated delivery probability
    :type current_probability: float
    :param routing_params: the routing parameters of the :param particle
    :type routing_params: :class:`~routing.RoutingParameters`
    :return: the updated estimated delivery probability
    :rtype: float
    """
    return current_probability + (1 - current_probability) * routing_params.l_encounter


def __try_and_transfer_messages__(particle, probabilities, particle_probability_for_encounter,
                                  routing_params, encounter):
    """
    Transfers messages from :param particle to :param encounter if the latter has at least an equally high
    estimated probability to deliver them.
    :param particle: the particle to transfer the messages from
    :type particle: :class:`~particle.Particle`
    :param probabilities: the estimated delivery probabilities dictionary from :param particle
    :type probabilities: dict
    :param particle_probability_for_encounter: the estimated delivery probability from :param particle
    to :param encounter
    :type particle_probability_for_encounter: float
    :param routing_params: the routing parameters of the :param particle
    :type routing_params: :class:`~routing.RoutingParameters`
    :param encounter: the particle encountered by :param particle
    :type encounter: :class:`~particle.Particle`
    :return: the updated estimated delivery probabilities of :param particle
    :rtype: dict
    """
    probabilities_encounter = particle.read_from_with(matter=encounter, key=PROB_KEY)
    for message in list(particle.send_store):
        receiver_id = message.get_actual_receiver().get_id()
        # get both estimated delivery probabilities for the particle and its encounter
        (particle_probability_for_receiver, last_encounter_receiver) = probabilities.get(receiver_id)
        (encounter_probability_for_receiver, _) = probabilities_encounter.get(receiver_id)
        # if the encounter is at least as likely to deliver the message, then transfer it
        if encounter_probability_for_receiver >= particle_probability_for_receiver:
            send_message(particle, encounter, message)
        # regardless update probability for particle with receiver_id
        particle_probability_for_receiver += (1 - particle_probability_for_receiver) * \
            particle_probability_for_encounter * encounter_probability_for_receiver * routing_params.beta
        probabilities[receiver_id] = (particle_probability_for_receiver, last_encounter_receiver)
    return probabilities
