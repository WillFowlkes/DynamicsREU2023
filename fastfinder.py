import math
import pandas
import numpy
import matplotlib
# import parameter


# START OF WILL CODE
def a_finder(d):
    a_vector = [d["n"] for _ in range(d["Tmax"])]
    cols = d["n"]
    timing_matrix = initialize(d)
    for i in range(cols):
        resource = calc_resource_vector(d, a_vector)
        date = find_dispersal_date(d, resource)
        timing_matrix, a_vector = update_matrix(date, i, timing_matrix, a_vector)
    return a_vector


def calc_q(d, r):
    return math.ceil(max(0, (d["Rmax"] - r) / d["c"]))


def calc_survival(d, r):
    return math.pow((r / (r + d["k"])), calc_q(d, r))


def initialize(d):
    return [[0 for _ in range(d["n"])] for __ in range(d["Tmax"])]


def calc_resource_vector(d, a_vector):
    time = d["Tmax"]
    resource = [0 for _ in range(time)]
    resource[0] = d["r"] / a_vector[0]
    for i in range(1, time):
        if a_vector[i] != 0:
            resource[i] += resource[i - 1] + d["r"] / a_vector[i]
    for i in range(time):
        resource[i] += d["Rmin"]
    return resource


def find_dispersal_date(d, resource):
    time = d["Tmax"]
    payoffs = [0 for _ in range(time)]

    ## calculate dispersal payoff
    for i, r in enumerate(resource):
        payoffs[i] = calc_payoff(d, i, r)
    j = get_Rmax_index(d, resource)
    payoffs.append(((d["Tmax"] - j) / d["Tmax"]) * (d["f"]) + (d["f"]) * (d["N"] - 1))
    return payoffs.index(max(payoffs))

def calc_payoff(d, day, resources):
    return calc_survival(d, resources) * \
        (((d["Tmax"] - day - calc_q(d, resources)) / d["Tmax"]) * (d["f"]+ d["b"]) + (
                                                        d["N"] - 1) * (d["f"] + d["b"]))


def get_Rmax_index(d, resource):
    for i, j in enumerate(resource):
        if j >= d["Rmax"]:
            return i


def update_matrix(date, i, timing_matrix, a_vector):
    for j, __ in enumerate(a_vector):
        if date <= j:
            a_vector[j] -= 1
    for k, _ in enumerate(a_vector):
        if date <= k:
            timing_matrix[k][i] += 1
    return timing_matrix, a_vector


def get_departure_vector(d, a_vector):
    departure_vector = [0] * d["n"]
    for val in a_vector:
        for i, _ in enumerate(departure_vector):
            if val > i:
                departure_vector[i] += 1
    return departure_vector

def get_payoffs(d, departure_vector, a_vector):
    resource = calc_resource_vector(d, a_vector)
    payoff = [0]*d["n"]
    for player, time in enumerate(departure_vector):
        payoff[player] = calc_payoff(d, time, resource[time])
    return payoff

def main():
    # parameters = parameter.Parameter()
    # parameters.setAll()
    # parameters.set("b")
    # print(parameters.get("b"))
    #
    # print("printing results...")

    d = {"N": 2,
         "n": 3,
         "r": 9,
         "c": 6,
         "Rmin": 6,
         "Rmax": 12,
         "Tmax": 2,
         "b": 1,
         "k": 1,
         "f": 10}
    # set conditions for root node
    rootInfo = {
        'states': ['n'] * d['n'],
        'efrs': [0] * d['n'],
        'day': 0,
        'p': 0,
        'resources': [d['Rmin']] * d['n']
    }
    

    a_vector = a_finder(d)
    departure_vector = get_departure_vector(d, a_vector)
    print(get_payoffs(d, departure_vector, a_vector))
    print(departure_vector)


if __name__ == '__main__':
    main()