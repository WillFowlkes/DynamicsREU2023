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

def calc_survival_vector(d, dep, resource):
    survival_rates = []
    for date in dep:
        if date == d["Tmax"]:
            survival_rates.append(1)
        else:
            survival_rates.append(calc_survival(d, resource[date]))
    return survival_rates


def sensitivity_analysis(d, var, low, high, outfile, increment=1):
    with open(outfile, 'w') as file:
        file = csv.writer(file)
        file.writerow([var,"departure dates", "mean departure",
                       "standard deviation departure", "payoffs",
                       "mean payoff", "standard deviation payoff",
                       "survival rates", "mean survival rate"])
        for i in numpy.arange(low, high, increment):
            d[var] = i
            a = a_finder(d)
            dep = get_departure_vector(d, a)
            p = get_payoffs(d, dep, a)
            resource = calc_resource_vector(d, a)
            survival_rates = calc_survival_vector(d, dep, resource)
            file.writerow([str(i),dep, get_mean(dep), get_stddev(dep), get_payoffs(
                d, dep, a), get_mean(p),
                            get_stddev(p), survival_rates, get_mean(survival_rates)])

def individual_sensitivity_analysis(d, n, var, low, high, outfile, increment =1):

    with open(outfile, 'w') as file:
        file = csv.writer(file)
        row = [["player "+str(n),var,"departure time","payoff","survival rate"] for n in range(1,
                                                                                             n+1)]
        newrow = []
        for l in row:
            for m in range(0, n):
                newrow.append(l[m])
        file.writerow(newrow)
        for i in numpy.arange(low, high, increment):
            d[var] = i
            a = a_finder(d)
            dep = get_departure_vector(d, a)
            p = get_payoffs(d, dep, a)
            resource = calc_resource_vector(d, a)
            survival_rates = calc_survival_vector(d, dep, resource)
            row = [[j+1, i, dep[j], p[j], survival_rates[j]] for j in range(0, n)]
            newrow = []
            for l in row:
                for m in range(0, n):
                    newrow.append(l[m])
            file.writerow(newrow)
            
                
            



def main():
    # parameters = parameter.Parameter()
    # parameters.setAll()
    # parameters.set("b")
    # print(parameters.get("b"))
    #
    # print("printing results...")


    #test_cases()
    bird = {"N": 1,
             "n": 4,
             "r": 12/5,
             "c": 2,
             "Rmin": 40,
             "Rmax": 136,
             "Tmax": 120,
             "b": 4,
             "k": 0.5,
             "f": 20}
    # ex = a_finder(bird)
    # dep = get_departure_vector(bird, ex)
    # payoffs = get_payoffs(bird, dep, ex)

    sensitivity_analysis(bird, "N", 1, 11, 'bigN.csv')
    bird["N"] = 1

    sensitivity_analysis(bird, "n", 1, 10, 'n.csv')
    bird["n"] = 4

    sensitivity_analysis(bird, "c", 1, 11, 'c.csv', 0.1)
    bird["c"] = 2

    sensitivity_analysis(bird, "r", 1, 6, 'r.csv', 0.1)
    bird["r"] = 12/5

    sensitivity_analysis(bird, "Rmin", 1, 81, 'Rmin.csv', 0.1)
    bird["Rmin"] = 40

    sensitivity_analysis(bird, "b", -20, 21, 'b.csv', 0.1)
    bird["b"] = 4

    sensitivity_analysis(bird, "k", 0, 2, 'k.csv', 0.1)
    bird["k"] = 0.5

    sensitivity_analysis(bird, "Tmax", 90, 241, 'Tmax.csv')
    bird["k"] = 120
    bird["n"] = 4

    individual_sensitivity_analysis(bird,bird["n"], "c", 1, 11, 'c2.csv', 0.1)
    bird["c"] = 2

    individual_sensitivity_analysis(bird,bird["n"], "r", 1, 6, 'r2.csv', 0.1)
    bird["r"] = 12 / 5

    individual_sensitivity_analysis(bird,bird["n"], "Rmin", 1, 81, 'Rmin2.csv', 0.1)
    bird["Rmin"] = 40

    individual_sensitivity_analysis(bird,bird["n"], "b", -20, 21, 'b2.csv', 0.1)
    bird["b"] = 4

    individual_sensitivity_analysis(bird,bird["n"], "k", 0, 2, 'k2.csv', 0.1)
    bird["k"] = 0.5

    individual_sensitivity_analysis(bird,bird["n"], "Tmax", 90, 241, 'Tmax.csv')
    bird["k"] = 120



if __name__ == '__main__':
    main()