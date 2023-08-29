import math
from fastnash import *
import treelib as tl

# nodeData holds the player, day, and states and efrs vector for decision nodes
# modifies underlying treelib class
class nodeData(tl.Node):
    def __init__(self, states, efrs, day, p):
        self.states = states 
        self.efrs = efrs
        self.day = day
        self.p = p
        self.solved = False

def solveNE(tree, root):
    children = tree.children(root.identifier)
    for child in children:
        if child.data.solved == False:
            solveNE(tree, child)
    player = root.data.p
    if children[0].data.efrs[player] > children[1].data.efrs[player]:
        efrs = children[0].data.efrs
        states = children[0].data.states
    else:
        efrs = children[1].data.efrs
        states = children[1].data.states
    root.data.efrs = efrs
    root.data.states = states
    return (states, efrs)

def get_leaf_info(tree):
    leaves = []
    for node in tree.nodes:
        if tree.children(node) == []:
            leaves.append(node)
    leafData = [(0, 0)] * len(leaves)
    for i, leaf in enumerate(leaves):
        leafData[i] = (tree[leaf].data.states, tree[leaf].data.efrs)
    return leafData


def calc_nodisperse_payoff(d, day):
    return (((d["Tmax"] - day) / d["Tmax"]) * (d["f"]) + (
            d["N"] - 1) * (d["f"]))
def calc_a(d, departure_vector):
    a = [0] * (d['Tmax'])
    for player in departure_vector:
        if player == 'n':
            player = len(a)
        for day in range(player):
            a[day] += 1
    return a

def get_Rmax_index(d, resource):
    for i, j in enumerate(resource):
        if j >= d["Rmax"]:
            return i
    return len(resource)

def calc_resource_vector(d, a_vector):
    time = d["Tmax"]
    resource = [0 for _ in range(time)]
    for i in range(1, time):
        if a_vector[i - 1] != 0:
            resource[i] += (resource[i - 1] + d["r"] / a_vector[i - 1])
    for i in range(time):
        resource[i] += d["Rmin"]
    return resource
def calc_q(d, r):
    return math.ceil(max(0, (d["Rmax"] - r) / d["c"]))

def calc_survival(d, r):
    return math.pow((r / (r + d["k"])), calc_q(d, r))

def calc_payoff(d, day, resources):
    return calc_survival(d, resources) * \
        (((d["Tmax"] - day - calc_q(d, resources)) / d["Tmax"]) * (d["f"] + d["b"]) + (
                d["N"] - 1) * (d["f"] + d["b"]))

def get_payoffs(d, departure_vector, a_vector):
    resource = calc_resource_vector(d, a_vector)
    payoff = [0] * d["n"]
    for player, time in enumerate(departure_vector):
        if time != "n":
            payoff[player] = calc_payoff(d, time, resource[time])
        else:
            r = get_Rmax_index(d, resource)
            payoff[player] = calc_nodisperse_payoff(d, r)
    return payoff

# def compute_nondisperser_efrs(states, d):
#     resources = d['Rmin']
#     nestPopByDay = [0] * (d['Tmax'] + 1)  #vector listing how many offspring were in the nest on each day
#     for player in states:
#         if player != 'n':
#             for j in range(player):  # for dispersed offspring, add 1 to nestPopByDay for each day before dispersal
#                 nestPopByDay[j] += 1
#                 j += 1
#         else:
#             for day in range(d['Tmax']+1):  # for natal offspring, add 1 to nest pop for every day
#                 nestPopByDay[day] += 1
#
#     t = d['Tmax']
#     for day, dayPop in enumerate(nestPopByDay):
#         if dayPop != 0:
#             resources = resources +d['r']/dayPop
#         if resources >= d['Rmax']:
#             t = day  # set t to the day that a non-disperser reaches Rmax
#             break
#     efrs = (d['f']*(d['Tmax'] - t)/d['Tmax']) + d['f'] * (d['N']-1)  # calculate efrs
#     return efrs

# def compute_disperser_efrs(states, dispDay, d):
#     resources = d['Rmin']
#     nestPopByDay = [0] * (d['Tmax'] + 1) #vector listing how many offspring were in the nest on each day
#
#     for player, state in enumerate(states):
#         if state != 'n' and state < dispDay:
#             for day in range(state):  # for dispersed offspring, add 1 to nestPopByDay for each day before dispersal
#                 nestPopByDay[day] += 1
#         else:
#             for day in range(dispDay):  # for natal offspring, add 1 to nest pop for every day
#                 nestPopByDay[day] += 1
#     t = d['Tmax']
#     for day in range(dispDay):
#         if nestPopByDay[day] != 0:
#             resources = resources +d['r']/nestPopByDay[day]
#
#     if resources <= d['Rmax']:
#         q = (d['Rmax'] - resources) / d['c']  # compute q if Rmax has not yet been reached
#         q = math.ceil(q)
#     else:
#         q = 0  # assume q = 0 (no dispersal cost) if R(d) >= Rmax at time of dispersal
#     p = (resources / (resources + d['k']))**q  # compute survival probability
#     rep1 = ((d['Tmax'] - (dispDay+1))/d['Tmax']) * (d['f'] + d['b'])
#     repn = (d['f'] + d['b'])
#
#     efrs = p * (rep1 + repn * (d['N'] - 1))
#     return efrs

# recursive_build_tree - call on the root node to generate entire tree
def recursive_build_tree(tree, root, d):
    # copy data from parent node
    p = root.data.p
    day = root.data.day
    states = root.data.states.copy()
    efrs = root.data.efrs.copy()
    solved = root.data.solved

    # If all players have dispersed, return.
    for i, player in enumerate(states):
        if player == 'n':
            break
        else:
            if i == len(states)-1:
                root.data.solved = True
                return

    # update p to next non-dispersed player
    while True:
        p = p + 1
        p = p%d['n']
        if root.data.states[p] == 'n':  # set p if next non-dispersed player is found
            break
    # update day if necessary
    if p <= root.data.p:
        day += 1

    # create 2 child nodes: one for if player stays, one for if player disperses
    # note: for uniqueness and interpretability, nodes are named according to convention: d{day}p{player}{states vector}
    # non-disperse node:
    child1 = "d" + str(day) + "p" + str(p) + str(states)
    tree.create_node(tag = child1, identifier = child1,
                     parent = root.identifier,
                     data = nodeData(states.copy(), efrs.copy(), day, p))
    # disperse node:
    states[root.data.p] = root.data.day
    # disperserEFRS = compute_disperser_efrs(states, root.data.day, d)
    # efrs[root.data.p] = disperserEFRS
    child2 = "d" + str(day) + "p" + str(p) + str(states)
    tree.create_node(tag = child2, identifier = child2,
                     parent = root.identifier,
                     data = nodeData(states.copy(), efrs.copy(), day, p))

    # if Tmax was reached at the parent node, and all players have gone, update non-disperser efrs and break.
    if root.data.day >= d['Tmax'] and root.data.p >= p:
        tree[child1].data.solved = True
        tree[child2].data.solved = True
        # nonDispEfrs = compute_nondisperser_efrs(tree[child1].data.states, d)
        # tree[child1].data.efrs[:] = [x if x != 0 else nonDispEfrs for x in root.data.efrs]
        # dispEfrs = compute_disperser_efrs(tree[child2].data.states, root.data.day, d)
        # nonDispEfrs = compute_nondisperser_efrs(tree[child1].data.states, d)
        # tree[child2].data.efrs[:] = [x if x != 0 else nonDispEfrs for x in root.data.efrs]
        # tree[child2].data.efrs[root.data.p] = dispEfrs
        return

    recursive_build_tree(tree, tree[child1], d)
    recursive_build_tree(tree, tree[child2], d)

    return

def find_max_sum(tree):
    max = ([], [0])
    for leaf in get_leaf_info(tree):
        #print(leaf, max)
        if sum(leaf[1]) > sum(max[1]):
            # print(leaf[1], max[1])
            max = leaf
    return max

# Solve function takes input of a dictionary of parameters and returns a tuple containing the timing and payoff vectors
def solve(d):

    # compute Rmax and update
    d['Rmax'] = d['Rmin'] + (d['Tmax'] + 1)*d['r']/d['n']
    # print('Set Rmax to', d['Rmax'])

    # set conditions for root node

    rootInfo = {
        'states' : ['n'] * d['n'],
        'efrs' : [0] * d['n'],
        'day' : 0,
        'p' : 0,
        'resources' : [d['Rmin']] * d['n']
        }

    tree = tl.Tree()  #initialize tree
    # create root node:
    nodeName = "d" + str(rootInfo['day']) + "p" +str(rootInfo['p']) + str(rootInfo['states'])
    tree.create_node(tag = nodeName,
                     identifier = 'root',
                     data = nodeData(rootInfo['states'], rootInfo['efrs'], rootInfo['day'], rootInfo['p'])
                     )

    recursive_build_tree(tree, tree['root'], d)

    d['Tmax'] += 1

    for leaf in tree.leaves():
        leaf.data.efrs = get_payoffs(d, leaf.data.states, calc_a(d, leaf.data.states))

    d['Tmax'] -= 1
    return tree

baseD = {"N": 2,
         "n": 3,
         "r": 12 / 5,
         "c": 2,
         "Rmin": 40,
         "Rmax": 40 + 136,
         "Tmax": 1, 
         "b": 4,
         "k": .8,
         "f": 3}
