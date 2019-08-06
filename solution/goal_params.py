from solution.utils import GoalStateSaver
import random
# Could theoretically fit in the solution file itself, but order-wise it makes sense to put this here!


def check_all_goal_params(sim):
    distance = 12
    if not GoalStateSaver.first_particle_passed:
        GoalStateSaver.first_particle_passed = goal_first_particle_passed(sim.particles, distance)
        if GoalStateSaver.first_particle_passed:
            sim.csv_round_writer.update_goals(0, sim.get_actual_round())
            print("FIRST PASSED at ", sim.get_actual_round())

    if not GoalStateSaver.half_particles_passed:
        GoalStateSaver.half_particles_passed = goal_half_particles_passed(sim.particles, distance)
        if GoalStateSaver.half_particles_passed:
            sim.csv_round_writer.update_goals(1, sim.get_actual_round())
            print("HALF PASSED at ", sim.get_actual_round())

    if goal_all_particles_passed(sim.particles, distance):
        GoalStateSaver.all_particles_passed = True
        sim.csv_round_writer.update_goals(2, sim.get_actual_round())
        print("ALL PASSED at ", sim.get_actual_round())
        avg_coords = [0.0, 0.0]
        for particle in sim.particles:
            avg_coords[0] = avg_coords[0] + particle.coords[0]
            avg_coords[1] = avg_coords[1] + particle.coords[1]
        avg_coords[0] = avg_coords[0] / len(sim.particles)
        avg_coords[1] = avg_coords[1] / len(sim.particles)
        print("SWARM CENTER at: " + str(avg_coords[0]) + " " + str(avg_coords[1]) +
              " for |" + str(random.seed) + "_" + str(sim.param_lambda) + "_" + str(sim.param_delta))
        sim.success_termination()


def goal_first_particle_passed(particles_list, distance):
    for particle in particles_list:
        if particle.coords[0] >= distance:
            return True
    return False


def goal_all_particles_passed(particles_list, distance):
    for particle in particles_list:
        if particle.coords[0] < distance:
            return False
    return True


def goal_half_particles_passed(particles_list, distance):
    # When the particle number is uneven, the half will be rounded up
    half = int(round(len(particles_list) / 2))
    particles_passed = 0
    for particle in particles_list:
        if particle.coords[0] >= distance:
            particles_passed = particles_passed + 1
    if particles_passed >= half:
        return True
    return False

