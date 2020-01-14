import pandas
import shutil
import os
import sys
from glob import glob
import random
import importlib
from multiprocessing import Pool

NUMBER_OF_SEEDS = 20
MAX_ROUNDS = 10000
SCENARIOS = ["giant_cave"]#["single_tile_particle_line", "single_tile_few_particles", "single_tile_many_particles",
            # "concave_shape", "simple_shape", "tube_island", "small_cave", "strange_cave"]
SOLUTIONS = ["p_max_lifetime.main"]#, "base.main", "send_free_location_info.main", "only_move_if_best_match.main", "p_max_with_id.main",
             #"prevent_circle_walking.main"]


def run_test(solution_scenario):
    simulator = importlib.import_module("swarm-sim")
    solution = solution_scenario[0]
    scenario = solution_scenario[1]
    for i in range(NUMBER_OF_SEEDS):
        simulator.swarm_sim(["-r", str(random.randint(0, sys.maxsize)), "-w", scenario, "-s", solution, "-v", "0",
                             "-n", str(MAX_ROUNDS), "-d", "1337-01-11_13-37-42", "-m", "1"])
    files = glob("./outputs/mulitple/1337-01-11_13-37-42_" + scenario + "_" +
                 solution.split(".")[0] + "/*/rounds.csv")
    sum = 0
    failures = 0
    failed_seeds = []
    for file in files:
        data = pandas.read_csv(file)
        line = data.tail(1)["Round Number"].values
        if len(line > 0):
            if line[0] < MAX_ROUNDS:
                sum += line[0]
            else:
                failures += 1
                failed_seeds.append(file.split("\\")[-2])
    avg = MAX_ROUNDS
    if (len(files) - failures) > 0:
        avg = sum / (len(files) - failures)
    print("Solution", solution, "in Scenario", scenario, "done.")
    return {"solution": solution, "scenario": scenario,
            "avg": avg, "fails": failures, "failed_seeds": failed_seeds}


def output_sorter(test):
    return SOLUTIONS.index(test["solution"]) + SCENARIOS.index(test["scenario"]) * len(SOLUTIONS)


if __name__ == "__main__":
    pandas.set_option("display.max_columns", 100)
    if os.path.isdir("/Users/Gorden/Python/swarm-sim/outputs"):
        shutil.rmtree("/Users/Gorden/Python/swarm-sim/outputs")
    solutions_scenarios = ((solution, scenario) for scenario in SCENARIOS for solution in SOLUTIONS)
    with Pool(processes=4) as pool:
        print("starting")
        output = list(pool.map(run_test, solutions_scenarios))
        output.sort(key=output_sorter)
    outfile = open("./outputs/output.txt", "w+")
    for test in output:
        outfile.write("Solution: " + str(test["solution"]) + "\n")
        outfile.write("scenario: " + str(test["scenario"]) + "\n")
        outfile.write("avg rounds taken: " + str(test["avg"]) + "\n")
        outfile.write("failed simulations: " + str(test["fails"]) + "\n")
        if test["fails"] > 0:
            outfile.write("failed seeds: " + str(test["failed_seeds"]) + "\n")
