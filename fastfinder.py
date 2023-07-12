import math
import csv
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
    for i in range(1, time):
        if a_vector[i-1] != 0:
            resource[i] += (resource[i - 1] + d["r"] / a_vector[i-1])
    for i in range( time):
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
    return len(resource)

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
            # if departure_vector[i] == d["Tmax"]:
            #     departure_vector[i] = "n"
    return departure_vector

def get_payoffs(d, departure_vector, a_vector):
    resource = calc_resource_vector(d, a_vector)
    payoff = [0]*d["n"]
    for player, time in enumerate(departure_vector):
        if time != d["Tmax"]:
            payoff[player] = calc_payoff(d, time, resource[time])
        else:
            r = get_Rmax_index(d, resource)
            payoff[player] = calc_nodisperse_payoff(d,r)
    return payoff

def calc_nodisperse_payoff(d, day):
    return (((d["Tmax"] - day ) / d["Tmax"]) * (d["f"]) + (
                                                        d["N"] - 1) * (d["f"]))
def get_mean(data):
    return sum(data)/len(data)

def get_stddev(data):
    return numpy.std(data)

def test_cases():
    print("Test case 1")
    case1 = {"N": 2,
         "n": 3,
         "r": 9,
         "c": 6,
         "Rmin": 6,
         "Rmax": 12,
         "Tmax": 2,
         "b": 1,
         "k": 1,
         "f": 10}
    a1 = a_finder(case1)
    dept1 = get_departure_vector(case1, a1)
    if dept1 == [1, 0, 0]:
        print("PASS: Departure date")
    else:
        print("FAIL: Departure date: expected [1,0,0], got " + str(dept1))
    payoffs1 = get_payoffs(case1, dept1, a1)
    if payoffs1 == [33/2, 99/7, 99/7]:
        print("PASS: Payoffs")
    else:
        print("FAIL: Payoffs: expected ["+str(33/2)+", " +str(99/7)+", "+ str(99/7)+"], got "+str(
            payoffs1))

    print("Test case 2")
    case2 = {"N": 10,
             "n": 2,
             "r": 4,
             "c": 3,
             "Rmin": 4,
             "Rmax": 10,
             "Tmax": 3,
             "b": 1,
             "k": 2,
             "f": 5}
    a2 = a_finder(case2)
    dept2 = get_departure_vector(case2, a2)
    if dept2 == [3, 3]:
        print("PASS: Departure date")
    else:
        print("FAIL: Departure date: expected [3, 3], got " + str(dept2))
    payoffs2 = get_payoffs(case2, dept2, a2)
    if payoffs2 == [45, 45]:
        print("PASS: Payoffs")
    else:
        print("FAIL: Payoffs: expected [45, 45], got " + str(payoffs2))

    print("Test case 3")
    case3 = {"N": 1,
             "n": 4,
             "r": 20,
             "c": 10,
             "Rmin": 20,
             "Rmax": 30,
             "Tmax": 2,
             "b": 2,
             "k": 10,
             "f": 10}
    a3 = a_finder(case3)
    dept3 = get_departure_vector(case3, a3)
    if dept3 == [1, 1, 0, 0]:
        print("PASS: Departure date")
    else:
        print("FAIL: Departure date: expected [1,1,0,0], got " + str(dept3))
    payoffs3 = get_payoffs(case3, dept3, a3)
    if payoffs3 == [6,6,4,4]:
        print("PASS: Payoffs")
    else:
        print("FAIL: Payoffs: expected [6,6,4,4], got " + str(payoffs3))

    print("Test case 4")
    case4 = {"N": 2,
             "n": 2,
             "r": 6,
             "c": 3,
             "Rmin": 12,
             "Rmax": 24,
             "Tmax": 4,
             "b": 2,
             "k": 6,
             "f": 6}
    a4 = a_finder(case4)
    dept4 = get_departure_vector(case4, a4)
    if dept4 == [3, 3]:
        print("PASS: Departure date")
    else:
        print("FAIL: Departure date: expected [3, 3], got " + str(dept4))
    payoffs4 = get_payoffs(case4, dept4, a4)
    if payoffs4 == [56/9, 56/9]:
        print("PASS: Payoffs")
    else:
        print("FAIL: Payoffs: expected [56/9, 56/9], got " + str(payoffs4))

def sensitivity_analysis(d, var, low, high, outfile):
    with open(outfile, 'w') as file:
        file = csv.writer(file)
        file.writerow([var,"departure dates", "mean departure",
                       "standard deviation departure", "payoffs",
                       "mean payoff", "death rate",
                       "standard deviation payoff"])
        for i in range(low, high):
            d[var] = i
            a = a_finder(d)
            dep = get_departure_vector(d, a)
            print(dep)
            p = get_payoffs(d, dep, a)
            print(p)
            file.writerow([str(i),get_mean(dep),  get_mean(p), get_stddev(dep), get_stddev(p)])





def main():
    # parameters = parameter.Parameter()
    # parameters.setAll()
    # parameters.set("b")
    # print(parameters.get("b"))
    #
    # print("printing results...")


    #test_cases()
    AmericanRobin = {"N": 1,
             "n": 4,
             "r": 12/5,
             "c": 2,
             "Rmin": 40,
             "Rmax": 136,
             "Tmax": 120,
             "b": 4,
             "k": 0.5,
             "f": 20}
    # ex = a_finder(example)
    # dep = get_departure_vector(example, ex)
    # payoffs = get_payoffs(example, dep, ex)
    var = "N"
    low = 1
    high = 11
    sensitivity_analysis(AmericanRobin, var, low, high, 'bigN.csv')
    var = "n"
    low = 1
    high = 10
    sensitivity_analysis(AmericanRobin, var, low, high, 'n.csv')
    var = "c"
    low = 1
    high = 11
    sensitivity_analysis(AmericanRobin, var, low, high, 'c.csv')
    var = "r"
    low = 1
    high = 6
    sensitivity_analysis(AmericanRobin, var, low, high, 'r.csv')
    var = "Rmin"
    low = 1
    high = 81
    sensitivity_analysis(AmericanRobin, var, low, high, 'Rmin.csv')
    var = "b"
    low = 1
    high = 21
    sensitivity_analysis(AmericanRobin, var, low, high, 'b.csv')
    var = "k"
    low = 0
    high = 10
    sensitivity_analysis(AmericanRobin, var, low, high, 'k.csv')
    var = "Tmax"
    low = 90
    high = 241
    sensitivity_analysis(AmericanRobin, var, low, high, 'Tmax.csv')



if __name__ == '__main__':
    main()