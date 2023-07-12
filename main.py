import math
import pandas
import numpy
import matplotlib
# import parameter
import treelib as tl


# nodeData holds the player, day, and states and efrs vector for decision nodes
class nodeData(tl.Node):
    def __init__(self, states, efrs, day, p):
        self.states = states
        self.efrs = efrs
        self.day = day
        self.p = p
        self.solved = False


def compute_nondisperser_efrs(states, d):
    resources = 0
    nestPopByDay = [0] * d['n']  # vector listing how many offspring were in the nest on each day
    for player in range(len(states)):
        if states[player] != 'n':
            j = 0
            while j < states[
                player]:  # for dispersed offspring, add 1 to nestPopByDay for each day before dispersal
                nestPopByDay[j] += 1
                j += 1
        else:
            for day in range(d['Tmax']):  # for natal offspring, add 1 to nest pop for every day
                nestPopByDay[day] += 1
    t = d['Tmax']
    for dayPop in nestPopByDay:
        if dayPop != 0:
            resources = resources + d['r'] / dayPop
        if resources >= d['Rmax']:
            t = dayPop  # set t to the day that a non-disperser reaches Rmax
            break
    efrs = (d['f'] * (d['Tmax'] - t) / d['Tmax']) + d['f'] * d['N']  # calculate efrs
    return efrs


def compute_disperser_efrs(states, dispDay, d):
    resources = 0
    nestPopByDay = [0] * d['n']  # vector listing how many offspring were in the nest on each day

    for player in range(len(states)):
        if states[player] != 'n' and states[player] < dispDay:
            j = 0
            while j < dispDay:  # for dispersed offspring, add 1 to nestPopByDay for each day before dispersal
                nestPopByDay[j] += 1
                j += 1
        else:
            for day in range(dispDay):  # for natal offspring, add 1 to nest pop for every day
                nestPopByDay[day] += 1

    t = d['Tmax']
    for dayPop in nestPopByDay:
        if dayPop != 0:
            resources = resources + d['r'] / dayPop

    if resources <= d['Rmax']:
        q = d['Rmax'] - resources / d['c']  # compute q if Rmax has not yet been reached
        q = math.ceil(q)
    else:
        q = 0  # assume q = 0 (no dispersal cost) if R(d) >= Rmax at time of dispersal
    p = (resources / (resources + d['k'])) ** q  # compute survival probability
    rep1 = ((d['Tmax'] - dispDay) / d['Tmax']) * (d['f'] + d['b'])
    repn = (d['f'] + d['b'])

    efrs = p * (rep1 + repn * (d['N'] - 1))
    return efrs


# recursive_build_tree - call on the root node to generate entire tree
def recursive_build_tree(tree, root, d):
    # copy data from parent node
    p = root.data.p
    day = root.data.day
    states = root.data.states
    efrs = root.data.efrs

    # If all players have dispersed, return.
    for i, player in enumerate(states):
        if player == 'n':
            break
        else:
            if i == len(states):
                root.data.solved = True
                return

    # update p to next non-dispersed player
    while True:
        p = p + 1
        p = p % d['n']
        if root.data.states[p] == 'n':  # set p if next non-dispersed player is found
            break
    # update day if necessary
    if p <= root.data.p:
        day += 1
    # update p to next non-dispersed player
    while True:
        p = p + 1
        p = p % d['n']
        if root.data.states[p] == 'n':  # set p if next non-dispersed player is found
            break
    # update day if necessary
    if p <= root.data.p:
        day += 1
    # if Tmax was reached at the parent node, update non-disperser efrs and break.
    if root.data.day == d['Tmax']:
        root.data.solved = True
        efrs = compute_nondisperser_efrs(root.data.states, d)
        root.data.efrs[:] = [x if x != 0 else efrs for x in root.data.efrs]
        return
    # create 2 child nodes: one for if player stays, one for if player disperses
    # note: for uniqueness and interpretability, nodes are named according to convention: d{day}p{player}{states vector}
    # non-disperse node:
    child1 = "d" + str(day) + "p" + str(p) + str(states)
    print()
    print(child1)
    tree.create_node(tag=child1, identifier=child1,
                     parent=root.identifier,
                     data=nodeData(states, efrs, day, p))
    # disperse node:
    states[(p - 1) % d['n']] = day
    disperserEFRS = compute_disperser_efrs(states, day, d)
    efrs[(p - 1) % d['n']] = disperserEFRS
    child2 = "d" + str(day) + "p" + str(p) + str(states)
    print(child2)
    print()
    tree.create_node(tag=child2, identifier=child2,
                     parent=root.identifier,
                     data=nodeData(states, efrs, day, p))
    recursive_build_tree(tree, tree[child1], d)
    recursive_build_tree(tree, tree[child2], d)
    return


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
    #
    # tree = tl.Tree()  # initialize tree
    # # create root node:
    # nodeName = "d" + str(rootInfo['day']) + "p" + str(rootInfo['p']) + str(rootInfo['states'])
    # tree.create_node(tag=nodeName,
    #                  identifier='root',
    #                  data=nodeData(rootInfo['states'], rootInfo['efrs'], rootInfo['day'],
    #                                rootInfo['p'])
    #                  )
    #
    # recursive_build_tree(tree, tree['root'], d)
    # print(tree)


if __name__ == '__main__':
    main()