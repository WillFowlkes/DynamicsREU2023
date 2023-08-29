# Ithaca College Dynamical Systems REU 2023
## Game tree analysis for an evolutionary dynamics of dispersal model

This code was written to help analyze game trees in a model developed to study timing of dispersal in birds. The code builds a game tree base on a dictionary of input parameters and has functions to solve the tree for a Nash equilibrium using backwards induction and to find the strategy vector that maximizes total payoff of all players. 

This code uses the treelib library for python to create the game trees. It also uses some functions from our fast NE solver and adapts them to compute payoff vectors in a tree.

### Generating a game tree

The function recursive_build_tree takes three input parameters - tree, root, and d. Tree is a tree object from the treelib library, and root is the root node object of the tree. These both must be created before building the rest of the tree recursively. d is a dictionary containing all the parameter values for an instances of the game. These parameters are described in detail in our paper, "Evolutionarily Stable Dispersal Timing: Effects of Dispersal Costs and Kin Competition". 

The treelib library uses a tree class to store trees, which are made up of nodes from a node class. Our creates the class nodeData to modify treelib's node class and allow us to store data on each node. Each node contains the following data attributes: states, efrs, day, p, and solved. States and efrs are vectors of length n, where each entry represents a player. Indexing players from 0, players k is in the state states[k] (which is either "n" if the player is in the natal area or a number of the dispersal day if the player has dispersed). Player k has an efrs of efrs[k], which is non-zero only for leaf nodes. p and day give the number of the player whos turn it is, and what day of the game it currently is at a given node. The solved attribue is initially set to false for all nodes except the leaf nodes. This is not used in building the tree, but is used later to find Nash equilibria using backwards induction.

To build a tree, a treelib tree object must be created, and a root node must be initialized with states vector of length n with all entries "n", an efrs vector of length n with all entries 0, day and p both set to 0, solved set to false. Then recursive_build_tree can be called on the root node.

The function recursive_build_tree creates 2 children of the input node - one representing when the deciding player stays, and one representing when the deciding player disperses. If all players have dispersed, or if time Tmax, representing the maximum game length, has been reached, then the function returns null and breaks out of the call. Otherwise, recursive_build_tree is called on the two child nodes.

This process generates a full game tree, and runs in O(Tmax ^ n). In tests run on an M1 Macbook with 8GB RAM, running this algorithm became impractical for cases larger than n = 6, Tmax = 7.

### Computing EFRS and use of code from fast algorithm

We also use an optimized algorithm to find Nash equilibria by utilizing symmetries of the model, running in O(Tmax * n). Some of that code is repeated in this file, with slight adjustments. The functions get_payoffs receives a dictionary d of parameters, the states vector for a node, and an "a" vector for the node. The "a" vector can be computed using the calc_a function, which takes a parameter dictionary and a states vector (see paper and other readme for information on "a" vectors). From these arguments, the get_payoffs function returns a vector of length n of the EFRS of each player.

To solve a tree, the get_payoffs function must be called on every leaf in a tree, and the efrs of each leaf must be set to the resulting payoff vector. The function solve(d) takes a dictionary d as input, and returns a tree with the correct efrs for the leaf nodes.

### Solving a game tree

The function solveNE take a treelib tree object and the tree's root node as inputs, and return a tuple containing the states and efrs vectors for a Nash equilibrium of the tree. 

SolveNE, when called on a parent node, compares the efrs for each of the 2 child node and "chooses" whichever node has a higher efrs for the player whos turn it is in the parent node. The parent's solved attribute is then marked to true, and it's efrs and states vectors are set to the erfrs and states of the child node that was chosen. A parent can only choose between 2 child nodes if both child nodes are solved. If a child is not solved, then solveNE is called recursively on the child. Initially, solved is set to false for all nodes except the leaf nodes, so when solveNE is called on the root of a tree, it continues calling itself until it reaches a parent of two leaf nodes. Then, it can start working back up the tree. When all nodes are solved, the initial function call completes and returns efrs and states vectors for a Nash equilibrium.

It must be noted that the solveNE function does not necessarily return a strict Nash equilibrium. If, for a deciding player, both child nodes return the same efrs, then the node corresponding to the strategy of staying in the natal area is chosen. However, we found that Nash equilbria tended to be strict in our model, with the exception of edge cases that were contrived to have multiple Nash equilibria. More details can be found in the "uniqueness of Nash equilibria" section of our paper.

### Finding strategies that maximize sum of efrs across all players

The function find_max_sum can be used to find the strategy that maximizes the total fitness of the gene rather than the fitness of individuals. The function only takes one arguement, a game tree object. The game tree must have efrs vectors computed for all leaf nodes. The max_sum function simply loops through all leaves and returns the node object of the leaf with the highest sum of efrs's.

### Accessing leaf data

The treelib library's build in functionality is wanting, so we implemented some functionality to get info on a tree. The function get_leaf_info takes in a tree object with efrs's calculated for all leaf nodes and return the vector leafData. leafData contains an entry for every leaf node in the input tree, and each entry is a tuple of length two where the first entry is the leaf's states vector and the second entry is the leaf's efrs vector. This is useful for getting an overview of individual game trees.









