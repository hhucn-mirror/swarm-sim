import numpy as np
import pandas
import shutil
import os
import sys
from glob import glob

MAX_ROUNDS = 3000
TARGET_FOLDER = "/Users/Gorden/Desktop/BA/Tests/robustness"
SCENARIOS = ["single_tile_few_particles", "concave_shape", "simple_shape", "tube_island", "small_cave", "strange_cave",
             "giant_cave", "bottle", "small_bottle"]
# ["single_tile_few_particles", "concave_shape", "simple_shape", "tube_island", "small_cave", "strange_cave", "giant_cave", "bottle", "small_bottle", "two_tiles"]
SOLUTIONS = ["p_max_lifetime.main"]
# ["base.main", "basebetter.main", "p_max_lifetime.main", "send_free_location_info.main", "only_move_if_best_match.main", "p_max_with_id.main", # "prevent_circle_walking.main"]


def eval_test(solution_scenario, target_folder="./outputs"):
    solution = solution_scenario[0]
    scenario = solution_scenario[1]
    files = glob(target_folder + "/mulitple/*[0-9]_" + scenario + "_" +
                 solution.split(".")[0] + "/*/aggregate_rounds.csv")
    data_by_particle_count = {}
    for file in files:
        data = pandas.read_csv(file)
        particle_count = data["Particle Counter"].values[0] + data["Particles Deleted Sum"].values[0]
        if data_by_particle_count.get(particle_count) is None:
            data_by_particle_count[particle_count] = []
        data_by_particle_count[particle_count].append(data)
    output_map = {}  # particle_count -> output data
    for particle_count, data_list in data_by_particle_count.items():
        rounds_taken = np.array([data["Rounds Total"].values[0] for data in data_list])
        rounds_taken_successful = rounds_taken[np.where(rounds_taken != MAX_ROUNDS)]
        seeds = np.array([data["Seed"].values[0] for data in data_list])
        particle_steps = np.array([data["Partilcle Steps Total"].values[0] for data in data_list])
        particle_steps_successful = particle_steps[np.where(rounds_taken != MAX_ROUNDS)]
        successful_seeds = seeds[np.where(rounds_taken != MAX_ROUNDS)]
        failed_seeds = seeds[np.where(rounds_taken == MAX_ROUNDS)]
        min = MAX_ROUNDS
        max = MAX_ROUNDS
        avg = MAX_ROUNDS
        standard_deviation = 0
        particle_steps_avg = np.average(particle_steps)
        failures = np.count_nonzero(rounds_taken == MAX_ROUNDS)
        if (len(data_list) - failures) > 0:
            avg = np.average(rounds_taken_successful)
            particle_steps_avg = np.average(particle_steps_successful)
            min = np.min(rounds_taken_successful)
            max = np.max(rounds_taken_successful)
            standard_deviation = np.std(rounds_taken_successful)
        output_map[particle_count] = {"avg": avg, "fails": failures, "failed_seeds": failed_seeds,
                                      "successful_seeds": successful_seeds, "min": min, "max": max,
                                      "moves": particle_steps_avg, "std_dev":standard_deviation}
    print("Solution", solution, "in Scenario", scenario, "done.")
    return {"solution": solution, "scenario": scenario,
            "output_data": output_map}


def output_sorter(test):
    return SOLUTIONS.index(test["solution"]) + SCENARIOS.index(test["scenario"]) * len(SOLUTIONS)


if __name__ == "__main__":
    solutions_scenarios = ((solution, scenario) for scenario in SCENARIOS for solution in SOLUTIONS)
    output = list(map(lambda x: eval_test(x, target_folder=TARGET_FOLDER), solutions_scenarios))
    output.sort(key=output_sorter)
    outfile = open(TARGET_FOLDER + "/output.txt", "w+")
    for test in output:
        outfile.write("Solution: " + str(test["solution"]) + "\n")
        outfile.write("scenario: " + str(test["scenario"]) + "\n")
        sorted_output = sorted(list(test["output_data"].items()), key=lambda x: x[0])
        for particle_count, test_data in sorted_output:
            outfile.write(" Particle count: " + str(particle_count) + "\n")
            outfile.write("     avg rounds taken: " + str(test_data["avg"]) + "\n")
            outfile.write("     min rounds taken: " + str(test_data["min"]) + "\n")
            outfile.write("     max rounds taken: " + str(test_data["max"]) + "\n")
            outfile.write("     standard deviation of rounds taken: " + str(test_data["std_dev"]) + "\n")
            outfile.write("     avg movements actions: " + str(test_data["moves"]) + "\n")
            outfile.write("     failures: " + str(test_data["fails"]) + "\n")