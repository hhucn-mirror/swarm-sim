import pandas
import shutil
import os
import sys
import time
from glob import glob
import random
import importlib
from multiprocessing import Pool, Queue, Process, Manager
from queue import Empty

NUMBER_OF_SEEDS = 50
MIN_PARTICLE_COUNT = 100
MAX_PARTICLE_COUNT = 100
STEPSIZE_PARTICLE_COUNT = 50
USE_PARTICLE_COUNT = True
MAX_ROUNDS = 10000
SCENARIOS = ["single_tile_few_particles", "concave_shape", "simple_shape", "tube_island", "small_cave", "strange_cave",
             "giant_cave", "bottle", "small_bottle"]
            #["single_tile_few_particles", "concave_shape", "simple_shape", "tube_island", "small_cave", "strange_cave", "giant_cave", "bottle", "small_bottle"]
SOLUTIONS = ["base.main"]#, "base.main", "p_max_lifetime.main", "send_free_location_info.main", "only_move_if_best_match.main", "p_max_with_id.main",
             #"prevent_circle_walking.main"]


def progress_counter_func(taskqueue, test_count):
    tests_done = 0
    while tests_done < test_count:
        try:
            taskqueue.get(False)
            tests_done += 1
            print(str(tests_done / test_count * 100) + "%", "done.")
        except Empty:
            pass
        time.sleep(5)


def run_test(args):
    simulator = importlib.import_module("swarm-sim")
    solution = args[0]
    scenario = args[1]
    seed = args[2]
    particle_count = args[3]
    taskqueue = args[4]
    simulator.swarm_sim(["-r", str(seed), "-w", scenario, "-s", solution, "-v", "0",
                         "-n", str(MAX_ROUNDS), "-d", "1337-01-11_13-37-42", "-m", "1", "-p", particle_count])
    taskqueue.put(seed)


def eval_test(solution_scenario):
    solution = solution_scenario[0]
    scenario = solution_scenario[1]
    files = glob("./outputs/mulitple/1337-01-11_13-37-42_" + scenario + "_" +
                 solution.split(".")[0] + "/*/aggregate_rounds.csv")
    data_by_particle_count = {}
    for file in files:
        data = pandas.read_csv(file)
        particle_count = data["Particle Counter"].values[0]
        if data_by_particle_count.get(particle_count) is None:
            data_by_particle_count[particle_count] = []
        data_by_particle_count[particle_count].append(data)
    output_map = {} # particle_count -> output data
    for particle_count, data_list in data_by_particle_count.items():
        sum = 0
        failures = 0
        failed_seeds = []
        successful_seeds = []
        for data in data_list:
            rounds_taken = data["Rounds Total"].values[0]
            if rounds_taken < MAX_ROUNDS:
                sum += rounds_taken
                successful_seeds.append(data["Seed"].values[0])
            else:
                failures += 1
                failed_seeds.append(data["Seed"].values[0])
        avg = MAX_ROUNDS
        if (len(data_list) - failures) > 0:
            avg = sum / (len(data_list) - failures)
        output_map[particle_count] = {"avg": avg, "fails": failures, "failed_seeds": failed_seeds,
                                      "successful_seeds": successful_seeds}
    print("Solution", solution, "in Scenario", scenario, "done.")
    return {"solution": solution, "scenario": scenario,
            "output_data": output_map}


def output_sorter(test):
    return SOLUTIONS.index(test["solution"]) + SCENARIOS.index(test["scenario"]) * len(SOLUTIONS)


if __name__ == "__main__":
    pandas.set_option("display.max_columns", 100)
    if os.path.isdir("./outputs"):
        shutil.rmtree("./outputs")
    taskmanager = Manager()
    taskqueue = taskmanager.Queue()
    solutions_scenarios = ((solution, scenario) for scenario in SCENARIOS for solution in SOLUTIONS)
    if USE_PARTICLE_COUNT:
        args = ((solution, scenario, random.randint(0, sys.maxsize), particle_count, taskqueue)
                for scenario in SCENARIOS
                for solution in SOLUTIONS
                for _ in range(NUMBER_OF_SEEDS)
                for particle_count in range(MIN_PARTICLE_COUNT, MAX_PARTICLE_COUNT + 1, STEPSIZE_PARTICLE_COUNT))
    else:
        args = ((solution, scenario, random.randint(0, sys.maxsize), -1, taskqueue)
                for scenario in SCENARIOS
                for solution in SOLUTIONS
                for _ in range(NUMBER_OF_SEEDS))
    args = list(args)
    test_count = len(args)
    print("number of tests:", test_count)
    progress_process = Process(target=progress_counter_func, args=(taskqueue, test_count))
    progress_process.daemon = True
    progress_process.start()
    with Pool(processes=3) as pool:
        print("starting")
        list(pool.map(run_test, args))
        print("tests done, starting evaluation")
        output = list(pool.map(eval_test, solutions_scenarios))
        output.sort(key=output_sorter)
    progress_process.join()
    outfile = open("./outputs/output.txt", "w+")
    for test in output:
        outfile.write("Solution: " + str(test["solution"]) + "\n")
        outfile.write("scenario: " + str(test["scenario"]) + "\n")
        sorted_output = sorted(list(test["output_data"].items()), key=lambda x: x[0])
        for particle_count, test_data in sorted_output:
            outfile.write(" Particle count: " + str(particle_count) + "\n")
            outfile.write("     avg rounds taken: " + str(test_data["avg"]) + "\n")
            if test_data["avg"] < MAX_ROUNDS:
                outfile.write("     successful seeds: " + str(test_data["successful_seeds"]) + "\n")
            outfile.write("     failed simulations: " + str(test_data["fails"]) + "\n")
            if test_data["fails"] > 0:
                outfile.write("     failed seeds: " + str(test_data["failed_seeds"]) + "\n")
