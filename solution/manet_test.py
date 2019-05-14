import random
import math

from lib.comms import CommEvent, Message, send_message

sub_nets = ["top-left", "bottom-left", "top-right", "bottom-right"]
E = 0
SE = 1
SW = 2
W = 3
NW = 4
NE = 5
S = 6 # S for stop and not south
direction = [E, SE, SW, W, NW, NE]

# battery constants
initial_charge = 1000
step_cost = 1
scan_cost_alpha = 2
send_cost_alpha = scan_cost_alpha
scan_radius = 2
scan_cost = pow(scan_radius, scan_cost_alpha)
send_cost = scan_cost
success = {}
# message ttl
global_ttl = 10

particle_colors = {"forward": [0.0, 0.0, 0.8], "empty": [0.8, 0.0, 0.0], "received": [0.0, 0.8, 0.0]}


def solution(sim):
    global particles
    # initialisation period
    if sim.get_actual_round() == 1:
        particles = sim.get_particle_list()
        particles_per = len(particles)/len(sub_nets)
        # set the sub_net attribute for all particles
        # this assumes the particles are added in the order of the sub_nets list
        for particle in particles:
            setattr(particle, "sub_net", sub_nets[math.ceil(particle.number/particles_per) % len(sub_nets)])
            # select particle for intra-sub-net comm
            setattr(particle, "intra", particle.number % len(sub_nets) == 0)
            # set initial battery charge
            setattr(particle, "battery", initial_charge)
        # send 100 random messages
        [send_random_message(sim) for i in range(0, 100)]
        for suc in CommEvent:
            success[suc] = 0
    elif sim.get_actual_round() < sim.get_max_round():
        for particle in particles:
            next_action(sim, particle, sim.get_actual_round())
    else:
        for suc in CommEvent:
            print("%s: %d " % (suc, success[suc]))


def next_action(sim, particle, iround):
    if hasattr(particle, "skip_round"):
        if getattr(particle, "skip_round"):
            setattr(particle, "skip_round", False)
            return
    else:
        setattr(particle, "skip_round", True)

    bat = getattr(particle, "battery")
    cost = 0
    if not getattr(particle, "intra"):
        return
    if bat >= step_cost:
        particle.move_to(random.choice(direction))
        cost = step_cost
    else:
        print("Particle %d has not enough battery to move." % particle.number)
        particle.color = particle_colors.get("empty")

    if bat >= scan_cost:
        cost += scan_cost
        nearby = particle.scan_for_particle_within(hop=scan_radius)
        if nearby is not None:
            setattr(particle, "skip_round", True)
            for neighbour in nearby:
                # first check if we've got a message for this exact neighbour
                if neighbour.get_id() in particle.send_store:
                    for message_key in particle.send_store[neighbour.get_id()]:
                        if (bat - (cost + send_cost)) > 0:
                            print("Message %s successfully delivered in round %d." % (message_key, iround))
                            success[CommEvent.MessageDelivered] += 1
                            cost += send_cost
                            neighbour.color = particle_colors.get("received")
                        else:
                            print("Particle %d has not enough battery to send." % particle.number)
                            return
                    # intra network particles forward all outbound messages
                    if getattr(neighbour, "intra"):
                        for receiver in sim.get_particle_list():
                            if receiver.get_id() in particle.send_store:
                                for message_key in particle.send_store[receiver.get_id()]:
                                    if (bat - (cost + send_cost)) > 0:
                                        print("Message %s successfully forwarded in round %d." % (message_key, iround))
                                        success[CommEvent.MessageForwarded] += 1
                                        cost += send_cost
                                        particle.color = particle_colors.get("forward")
                                    else:
                                        print("Particle %d has not enough battery tor send." % particle.number)
                                        return
    else:
        print("Particle %d has not enough battery to scan." % particle.number)
        return
    setattr(particle, "battery", bat-cost)


def send_random_message(sim):
    sender_ind = random.randint(0, len(sim.particles) - 1)
    receiver_ind = random.randint(0, len(sim.particles) - 1)
    while receiver_ind == sender_ind:
        receiver_ind = random.randint(0, len(sim.particles) - 1)
    m = Message(sender=sim.particles[sender_ind], receiver=sim.particles[receiver_ind],
                start_round=sim.get_actual_round(), ttl=global_ttl)
    sim.particles[sender_ind].send_store.add_message(m)
    setattr(m.original_sender, "battery", getattr(m.original_sender, "battery") - send_cost)
