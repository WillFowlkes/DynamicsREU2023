"""
This Python File was written by Will Fowlkes (Vanderbilt University, class of 2025) as part of
the 2023 IC Dynamics REU.  The purpose of fastfinder.py is to find the Nash Equilibrium of a finite
sequential game faster than by using backwards induction. For a game of x players making y
choices, the complexity is O(y^x).  The algorithm implemented here, nicknamed Fast Nash, takes this
game to O(x*y), allowing for much greater analysis.

Contact Information: whitman.w.fowlkes@vanderbilt.edu
"""


import math
import csv
import numpy


"""
a_finder(d):

:parameter d: the dictionary of parameters used in the game.

The main loop of the algorithm.  This loops through the players in the game, and calculates the 
optimal dispersal date for each player.  Due to a proof provided in the paper, this can be done 
independently of other players as long as it is done in reverse player order.

:returns a_vector:  This is a vector of length "Tmax" which gives the remaining number of 
philopatric individuals at any given data.  This is used to calculate the resources of a 
dispersing player.
"""
def a_finder(d):
    #initialize data structures
    a_vector = [d["n"] for _ in range(d["Tmax"])]
    cols = d["n"]

    # timing matrix gives a 2D visualization of when each individual is expected to disperse.
    timing_matrix = initialize(d)

    #loop through players
    for i in range(cols):
        resource = calc_resource_vector(d, a_vector)
        date = find_dispersal_date(d, resource)
        timing_matrix, a_vector = update_matrix(date, i, timing_matrix, a_vector)
    return a_vector


"""
calc_q(d, r)

:parameter d: the dictionary of parameters used in the game.
           r: the accumulated resources of an individual

This function calculates q, the time spent in dispersal.

:return q: the time spent in the dispersal process.
"""
def calc_q(d, r):
    return math.ceil(max(0, (d["Rmax"] - r) / d["c"]))


"""
calc_survival(d, r)

:parameter d: the dictionary of parameters used in the game.
           r: the accumulated resources of an individual

This function calculates p_s, the probability that an individual survival dispersal, given an 
accumulated resources r.

:return p_s: the chance that an individual survives dispersal.
"""
def calc_survival(d, r):
    return math.pow((r / (r + d["k"])), calc_q(d, r))


"""
initialize(d)

:parameter d: the dictionary of parameters used in the game.

This function initialized the 2D timing matrix to all 0's.

:return timing_matrix: the 2D representation of departure times.
"""
def initialize(d):
    return [[0 for _ in range(d["n"])] for __ in range(d["Tmax"])]


"""
calc_resource_vector(d, a_vector)

:parameter d: the dictionary of parameters used in the game.
           a_vector: the vector giving the number of remaining philopatric individuals at any time

This function calculates the number of resources that an individual would have accumulated 
at any given date of departure.

:return resource: the accumulated resources of an individual at any point in time
"""
def calc_resource_vector(d, a_vector):
    time = d["Tmax"]
    resource = [0 for _ in range(time)]

    # resources are split by the number of remaining philopatric individuals
    for i in range(1, time):
        if a_vector[i-1] != 0:
            resource[i] += (resource[i - 1] + d["r"] / a_vector[i-1])

    # after adding in resource gain, we then increment all terms by "Rmin"
    for i in range( time):
        resource[i] += d["Rmin"]
    return resource

"""
find_dispersal_date(d, resource)

:parameter d: the dictionary of parameters used in the game.
           resource: the accumulated resources of an individual at any point in time

This function calculates the payoff an individual would obtain at any point in time, and then 
takes whichever date give the maximal payoff.  An error is thrown in there is more than one max 
(see uniqueness_check())

:return departure date: the date an individual begins dispersal.
"""
def find_dispersal_date(d, resource):
    time = d["Tmax"]
    payoffs = [0 for _ in range(time)]

    ## calculate dispersal payoff
    for i, r in enumerate(resource):
        payoffs[i] = calc_payoff(d, i, r)

    # add in the payoff one obtains by not dispersing
    j = get_Rmax_index(d, resource)
    payoffs.append(((d["Tmax"] - j) / d["Tmax"]) * (d["f"]) + (d["f"]) * (d["N"] - 1))


    uniqueness_check(d, payoffs, max(payoffs))
    return payoffs.index(max(payoffs))


"""
uniqueness_check(d, p, max)

:parameter d: the dictionary of parameters used in the game.
           p: the list of all payoffs to an individual
           max: the maximal payoff; what we want to check for duplicates of
           

This function checks whether the maximal payoff is unique, which is a condition for having a 
mixed Nash Equilibrium.
"""
def uniqueness_check(d, p, max):
    maxima =0
    for i in p:
        if i == max:
            maxima+=1
    if maxima > 1:
        print("BAD NEWS")
        print(d)
        print("BAD NEWS")


"""
calc_payoff(d, day, resources)

:parameter d: the dictionary of parameters used in the game.
           day: the day dispersal occurs on
           resources: the accumulated resources on the dispersal date

This function calculates the payoff obtained when dispersing on day "day" with "resources" 
accumulated resources.

returns payoff: the payoff obtained
"""
def calc_payoff(d, day, resources):
    return calc_survival(d, resources) * \
        (((d["Tmax"] - day - calc_q(d, resources)) / d["Tmax"]) * (d["f"]+ d["b"]) + (
                                                        d["N"] - 1) * (d["f"] + d["b"]))

"""
get_Rmax_index(d, resource)

:parameter d: the dictionary of parameters used in the game.
           resource: the accumulated resources on any given departure date.

This function calculates the time at which a non-dispersing individual reaches Rmax.  This 
corresponds the the z in the payoff formula provided in the paper.

returns payoff: the day at which Rmax is reached
"""
def get_Rmax_index(d, resource):
    for i, j in enumerate(resource):
        if j >= d["Rmax"]:
            return i

    # Rmax is always reached.  If we get to here, it must be on the last day.
    return len(resource)


"""
update_matrix(date, i, timing_matrix, a_vector)

:parameter date: The departure date of player i
           i: The player in questions; this corresponds to a column in timing_matrix
           timing_matrix: the 2D representation of departure times.
           a_vector: the vector giving the number of remaining philopatric individuals at any time

This function updates the timing_matrix with player i's departure date. knowing player i's 
behavior, the a_vector is updated.

:returns timing_matrix: updated with player i's behavior
         a_vector: updated with player i's behavior
"""
def update_matrix(date, i, timing_matrix, a_vector):
    for j, __ in enumerate(a_vector):
        if date <= j:
            a_vector[j] -= 1
    for k, _ in enumerate(a_vector):
        if date <= k:
            timing_matrix[k][i] += 1
    return timing_matrix, a_vector


"""
get_departure_vector(d, a_vector)

:parameter d: the dictionary of parameters used in the game.
           a_vector: the remaining number of philopatric individuals at any given time, 
           now updated for each player.

Since a_vector is now fully formed and provides a complete picture of behavior in the game, 
we use it to get a depature vector, a vector of length n which gives the departure date of each 
player.  A depature date of "Tmax" means that an individual does not disperse.

:returns departure_vector: a vector of each player's departure date.
"""
def get_departure_vector(d, a_vector):
    departure_vector = [0] * d["n"]
    for val in a_vector:
        for i, _ in enumerate(departure_vector):
            if val > i:
                departure_vector[i] += 1
            # optional if you would rather have no dispersal represented as "n" instead of
            # the value of Tmax
            # if departure_vector[i] == d["Tmax"]:
            #     departure_vector[i] = "n"
    return departure_vector


"""
get_departure_vector(d, departure_vector, a_vector)

:parameter d: the dictionary of parameters used in the game.
           departure_vector: a vector of each player's departure date.
           a_vector: the fully updated remaining number of philopatric individuals at any date
           
We use departure_vector and a_vector to calculate a payoff vector, which gives each player's best 
payoff and thus gives the Nash Equilibrium payoffs for the whole game.

:returns payoff: a vector of each player's payoff
"""
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
    return (((d["Tmax"] - day ) / d["Tmax"]) * (d["f"]) + (d["N"] - 1) * (d["f"]))


## THE FOLLOWING FUNCTIONS ARE USED IN THE STATISTICAL ANALYSIS OR IN TESTING
"""
get_mean(data)

returns the mean of a list of numerical data.
"""
def get_mean(data):
    return sum(data)/len(data)

"""
get_stddev(data)

returns the standard deviation of a list of numerical data.
"""
def get_stddev(data):
    return numpy.std(data)

"""
test_cases()

Checks if the program passes the test cases. This is used to check for correctness
"""
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

"""
calc_survival_vector(d, dep, resource)

:parameter d: the dictionary of parameters used in the game.
           departure_vector: a vector of each player's departure date.
           a_vector: the fully updated remaining number of philopatric individuals at any date 

Calculates the survival rate of each individual.  Though survival is calculated when computing 
payoffs, we provide a separate function for just survival for its own analysis.

:return survival_rates: a vector of each players chance of survival.
"""
def calc_survival_vector(d, departure_vector, resource):
    survival_rates = []
    for date in departure_vector:
        if date == d["Tmax"]:
            survival_rates.append(1)
        else:
            survival_rates.append(calc_survival(d, resource[date]))
    return survival_rates

"""
sensitivity_analysis(d, var, low, high, outfile, increment=1)

:parameter d: the dictionary of parameters used in the game.
           var: the parameter we want to analyze.
           low: the minimum value of var
           high: the maximum value of var
           outfile: the csv file we want data to be written to
           increment: the amount we increase var by in analysis, defaulted to 1
           
Completes sensitivity analysis over a single variable.
"""
def sensitivity_analysis(d, var, low, high, outfile, increment=1):
    with open(outfile, 'w') as file:
        file = csv.writer(file)

        #write the header row
        file.writerow([var,"departure dates", "mean departure",
                       "standard deviation departure", "payoffs",
                       "mean payoff", "standard deviation payoff",
                       "survival rates", "mean survival rate"])

        for i in numpy.arange(low, high, increment):
            # set the parameter value then calculate the data
            d[var] = i
            a = a_finder(d)
            dep = get_departure_vector(d, a)
            p = get_payoffs(d, dep, a)
            resource = calc_resource_vector(d, a)
            survival_rates = calc_survival_vector(d, dep, resource)

            # write the data to the outfile
            file.writerow([str(i),dep, get_mean(dep), get_stddev(dep), get_payoffs(
                d, dep, a), get_mean(p),
                            get_stddev(p), survival_rates, get_mean(survival_rates)])


"""
individual_sensitivity_analysis(d, n, var, low, high, outfile, increment =1)

:parameter d: the dictionary of parameters used in the game.
           n: the number of players.
           var: the parameter we want to analyze.
           low: the minimum value of var
           high: the maximum value of var
           outfile: the csv file we want data to be written to
           increment: the amount we increase var by in analysis, defaulted to 1

Completes sensitivity analysis over a single variable for each player.  This does essentially 
the same thing as sensitivity_analysis, but formats it by player first then variable value second.
"""
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
    """
    declare dictionary here:
     example = {"N": 1,
             "n": 4,
             "r": 12/5,
             "c": 2,
             "Rmin": 40,
             "Rmax": 136,
             "Tmax": 120,
             "b": 0.8,
             "k": 0.5,
             "f": 4}
     call functions here:
     var = a_finder(example)
    """

if __name__ == '__main__':
    main()
