import math
import pandas
import numpy
import matplotlib
#import parameter
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
    nestPopByDay = [0] * d['n'] #vector listing how many offspring were in the nest on each day
    for player in range(len(states)):
        if states[player] != 'n':
            j = 0
            while j < states[player]:  # for dispersed offspring, add 1 to nestPopByDay for each day before dispersal
                nestPopByDay[j] += 1
                j += 1
        else:
            for day in range(d['Tmax']):  # for natal offspring, add 1 to nest pop for every day
                nestPopByDay[day] += 1
    t = d['Tmax']
    for dayPop in nestPopByDay:
        if dayPop != 0:
            resources = resources +d['r']/dayPop
        if resources >= d['Rmax']:
            t = dayPop  # set t to the day that a non-disperser reaches Rmax
            break
    efrs = (d['f']*(d['Tmax'] - t)/d['Tmax']) + d['f'] * d['N']  # calculate efrs
    return efrs

def compute_disperser_efrs(states, dispDay, d):

    resources = 0
    nestPopByDay = [0] * d['n'] #vector listing how many offspring were in the nest on each day

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
            resources = resources +d['r']/dayPop

    if resources <= d['Rmax']:
        q = d['Rmax'] - resources / d['c']  # compute q if Rmax has not yet been reached
        q = math.ceil(q)
    else:
        q = 0  # assume q = 0 (no dispersal cost) if R(d) >= Rmax at time of dispersal
    p = (resources / (resources + d['k']))**q  # compute survival probability
    rep1 = ((d['Tmax'] - dispDay)/d['Tmax']) * (d['f'] + d['b'])
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
        p = p%d['n']
        if root.data.states[p] == 'n':  # set p if next non-dispersed player is found
            break
    # update day if necessary
    if p <= root.data.p:
        day += 1
    # update p to next non-dispersed player
    while True:
        p = p + 1
        p = p%d['n']
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
    tree.create_node(tag = child1, identifier = child1,
                     parent = root.identifier,
                     data = nodeData(states, efrs, day, p))
    # disperse node:
    states[(p-1)%d['n']] = day
    disperserEFRS = compute_disperser_efrs(states, day, d)
    efrs[(p-1)%d['n']] = disperserEFRS
    child2 = "d" + str(day) + "p" + str(p) + str(states)
    print(child2)
    print()
    tree.create_node(tag = child2, identifier = child2,
                     parent = root.identifier,
                     data = nodeData(states, efrs, day, p))
    recursive_build_tree(tree, tree[child1], d)
    recursive_build_tree(tree, tree[child2], d)
    return


def main():

    # parameters = parameter.Parameter()
    # parameters.setAll()
    # parameters.set("b")
    # print(parameters.get("b"))
    #
    # print("printing results...")

    d = {"N": 3,
         "n": 2,
         "r": 1,
         "c": .8,
         "Rmin": 1,
         "Rmax": 2,
         "Tmax": 1,
         "b": .2,
         "k": .3,
         "f": 1}
    # set conditions for root node
    rootInfo = {
        'states' : ['n'] * d['n'],
        'efrs' : [0] * d['n'],
        'day' : 0,
        'p' : 0,
        'resources' : [d['Rmin']] * d['n']
        }
    
    tree = tl.Tree() #initialize tree   
    #create root node:
    nodeName = "d" + str(rootInfo['day']) + "p" +str(rootInfo['p']) + str(rootInfo['states'])
    tree.create_node(tag = nodeName,
                     identifier = 'root',
                     data = nodeData(rootInfo['states'], rootInfo['efrs'], rootInfo['day'], rootInfo['p'])
                     )

    
    recursive_build_tree(tree, tree['root'], d)
    print(tree)

if __name__ == '__main__':
    main()
