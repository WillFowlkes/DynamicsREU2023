import pandas
import numpy
import matplotlib
import parameter
import treelib as tl

# nodeData holds the attributes
class nodeData(tl.Node):
    def __init__(self, states, efrs, day, p):
        self.states = states
        self.efrs = efrs
        self.day = day
        self.p = p
        self.solved = False


def compute_nondisperser_efrs(states):
    resources = 0
    nestPopByDay = [0] * d['n'] #vector listing how many offspring were in the nest on each day
    for player in states:
        if states[player] != 'n':
            j = 0
            while j < states[player]:
                nestPopByDay[j] += 1
                j += 1
    t = d['Tmax']
    for day in nestPopByDay:
        resources = resources +d['r']/nestPopByDay[day]
        if resources >= d['Rmax']:
            t = day  # set t to the day that a non-disperser reaches Rmax
            break
    efrs = (d['f']*(d['Tmax'] - t)/d['Tmax']) + d['f'] * d['N']  # calculate efrs
    return efrs

def compute_disperser_efrs(states, p, day):
    # TO-DO
    return


# recursive_build_tree - call on the root node to generate entire tree
def recursive_build_tree(tree, root, d):
    if root.data.day == d['Tmax']:  # if Tmax was reached at the parent node, update non-disperser efrs and break.
        root.data.solved = True
        efrs = compute_nondisperser_efrs(root.data.states)
        root.data.efrs[:] = [x if x != 0 else efrs for x in root.data.efrs]
        return
    # copy data from parent node
    p = root.data.p
    day = root.data.day
    states = root.data.states
    efrs = root.data.efrs


    # update p to next non-dispersed player
    p = p + 1
    while True:
        if p % d['n'] == root.data.p:  # break out of recursive call if all players are dispersed
            root.data.solved = True
            return
        if root.data.states[p%d['n']] == 'n':
            break
        else:
            p += 1
    # update day if necessary
    if p <= root.data.p:
        day += 1
    # create 2 child nodes: one for if player stays, one for if player disperses
    # note: for uniqueness and interpretability, nodes are named according to convention: d{day}p{player}{states vector}
    # non-disperse node:
    child1 = "d" + str(day) + "p" + str(p) + str(states)
    tree.create_node(tag = child1, identifier = child1,
                     parent = root.identifier,
                     data = nodeData(states, efrs, day, p))
    # disperse node:
    states[p] = day
    disperserEFRS = compute_disperser_efrs(states, p, day)
    efrs[p] = disperserEFRS
    child2 = "d" + str(day) + "p" + str(p) + str(states)
    tree.create_node(tag = child2, identifier = child2,
                     parent = root.identifier,
                     data = nodeData(states, efrs, day, p))
    recursive_build_tree(tree, child1, d)
    recursive_build_tree(tree, child2, d)
    return


def main():

    # parameters = parameter.Parameter()
    # parameters.setAll()
    # parameters.set("b")
    # print(parameters.get("b"))
    #
    # print("printing results...")

    d = {"N": 1,
                  "n": 3,
                  "r": 1,
                  "c": 1,
                  "Rmin": 1,
                  "Rmax": 1,
                  "Tmax": 1,
                  "b": 1,
                  "k": 1,
                  "f": 1}
    # set conditions for root node
    rootInfo = {
        'states' : ['n'] * d['n'],
        'efrs' : [0] * d['n'],
        'day' : 0,
        'p' : 1,
        'resources' : [d['Rmin']] * d['n']
        }
    
    tree = tl.Tree() #initialize tree   
    #create root:
    nodeName = "d" + str(rootInfo['day']) + "p" +str(rootInfo['p']) + str(rootInfo['states'])
    tree.create_node(tag = nodeName,
                     identifier = 'root',
                     data = nodeData(rootInfo['states'], rootInfo['efrs'], rootInfo['day'], rootInfo['p'])
                     )
    print(tree['root'].data.efrs)
    


if __name__ == '__main__':
    main()
