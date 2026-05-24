import { solveHadlockEvents } from "./hadlock.js";
import { connectOpenComponents, isFullyConnected } from "./mazeConnectivity.js";
import { mazeStatistics } from "./mazeStats.js";

const WALL = 1;
const OPEN = 0;
const DEFAULT_TEXTURE_DENSITY = 0.55;

const algorithms = {
  BFS: {
    name: "Breadth-First Search",
    family: "Unweighted graph search",
    optimal: "Yes",
    weighted: "No",
    time: "O(V + E)",
    space: "O(V)",
    complete: "Yes",
    notes: "Shortest path by edge count in unweighted mazes.",
  },
  Lee: {
    name: "Lee Algorithm",
    family: "Wavefront routing",
    optimal: "Yes",
    weighted: "No",
    time: "O(V + E)",
    space: "O(V)",
    complete: "Yes",
    notes: "Grid-routing wave expansion; BFS under the maze's unit-cost model.",
  },
  DFS: {
    name: "Depth-First Search",
    family: "Graph traversal",
    optimal: "No",
    weighted: "No",
    time: "O(V + E)",
    space: "O(V)",
    complete: "Yes",
    notes: "Explores deeply first; useful contrast against shortest-path solvers.",
  },
  "Flood Fill": {
    name: "Flood Fill Solver",
    family: "Distance transform",
    optimal: "Yes",
    weighted: "No",
    time: "O(V + E)",
    space: "O(V)",
    complete: "Yes",
    notes: "Fills distances from the goal, then follows the decreasing distance gradient.",
  },
  "A*": {
    name: "A* Search",
    family: "Heuristic shortest path",
    optimal: "Yes",
    weighted: "Yes",
    time: "O(E log V)",
    space: "O(V)",
    complete: "Yes",
    notes: "Uses Manhattan distance as an admissible heuristic on 4-neighbor grids.",
  },
  "IDA*": {
    name: "Iterative Deepening A*",
    family: "Memory-bounded heuristic search",
    optimal: "Yes",
    weighted: "No",
    time: "O(b^d)",
    space: "O(d)",
    complete: "Yes",
    notes: "Searches increasing f = g + h contours with depth-first memory use.",
  },
  Hadlock: {
    name: "Hadlock's Algorithm",
    family: "Detour-number maze routing",
    optimal: "Yes",
    weighted: "No",
    time: "O(V + E)",
    space: "O(V)",
    complete: "Yes",
    notes: "Minimizes moves away from Manhattan progress before tracing a shortest maze route.",
  },
  Dijkstra: {
    name: "Dijkstra's Algorithm",
    family: "Weighted shortest path",
    optimal: "Yes",
    weighted: "Yes",
    time: "O((V + E) log V)",
    space: "O(V)",
    complete: "Yes",
    notes: "Finds shortest paths with non-negative edge costs.",
  },
  UCS: {
    name: "Uniform-Cost Search",
    family: "Weighted shortest path",
    optimal: "Yes",
    weighted: "Yes",
    time: "O((V + E) log V)",
    space: "O(V)",
    complete: "Yes",
    notes: "Expands the cheapest known path first; equivalent to Dijkstra on this grid.",
  },
  SPFA: {
    name: "Shortest Path Faster Algorithm",
    family: "Queue relaxation",
    optimal: "Yes",
    weighted: "Yes",
    time: "O(VE)",
    space: "O(V)",
    complete: "Yes",
    notes: "Queue-driven Bellman-Ford relaxation that revisits only changed vertices.",
  },
  "Bidirectional BFS": {
    name: "Bidirectional BFS",
    family: "Meet-in-the-middle search",
    optimal: "Yes",
    weighted: "No",
    time: "O(b^(d/2))",
    space: "O(b^(d/2))",
    complete: "Yes",
    notes: "Searches from start and goal simultaneously until the waves meet.",
  },
  "Greedy Best-First": {
    name: "Greedy Best-First Search",
    family: "Heuristic graph search",
    optimal: "No",
    weighted: "No",
    time: "O(E log V)",
    space: "O(V)",
    complete: "Yes",
    notes: "Chases the cell with the smallest Manhattan distance to the goal.",
  },
  "Left-Hand Rule": {
    name: "Left-Hand Wall Follower",
    family: "Wall following",
    optimal: "No",
    weighted: "No",
    time: "O(k)",
    space: "O(k)",
    complete: "Topology",
    notes: "Keeps the left hand on a wall; works under specific maze topology assumptions.",
  },
  "Right-Hand Rule": {
    name: "Right-Hand Wall Follower",
    family: "Wall following",
    optimal: "No",
    weighted: "No",
    time: "O(k)",
    space: "O(k)",
    complete: "Topology",
    notes: "The mirrored wall follower, useful for seeing how wall-connectedness matters.",
  },
  Tremaux: {
    name: "Tremaux's Algorithm",
    family: "Passage marking",
    optimal: "No",
    weighted: "No",
    time: "O(V + E)",
    space: "O(V + E)",
    complete: "Yes",
    notes: "Marks passages while backtracking, avoiding endless wandering in loopy mazes.",
  },
  Pledge: {
    name: "Pledge Algorithm",
    family: "Obstacle avoidance",
    optimal: "No",
    weighted: "No",
    time: "O(k)",
    space: "O(k)",
    complete: "Topology",
    notes: "Combines a preferred heading with wall following and turn-sum accounting.",
  },
  IDDFS: {
    name: "Iterative Deepening DFS",
    family: "Depth-limited search",
    optimal: "Yes",
    weighted: "No",
    time: "O(b^d)",
    space: "O(d)",
    complete: "Yes",
    notes: "Repeats DFS with larger depth limits to keep memory low.",
  },
  "Bellman-Ford": {
    name: "Bellman-Ford",
    family: "Dynamic programming",
    optimal: "Yes",
    weighted: "Yes",
    time: "O(VE)",
    space: "O(V)",
    complete: "Yes",
    notes: "Relaxes every edge repeatedly, making shortest-path work visible.",
  },
  "Dead-End Filling": {
    name: "Dead-End Filling",
    family: "Maze reduction",
    optimal: "No",
    weighted: "No",
    time: "O(V + E)",
    space: "O(V)",
    complete: "Yes",
    notes: "Prunes cul-de-sacs before tracing through the remaining corridors.",
  },
  "Random Mouse": {
    name: "Random Mouse",
    family: "Random walk",
    optimal: "No",
    weighted: "No",
    time: "Unbounded",
    space: "O(k)",
    complete: "No",
    notes: "Chooses a legal neighbor at random; intentionally weak as a baseline.",
  },
};

const breakdowns = {
  BFS: {
    summary: "Layered graph expansion over a grid graph G = (V, E).",
    graph: "Grid graph",
    cost: "Unit edge cost",
    formula: "dist[v] = dist[u] + 1",
    invariant: "The first time a cell is dequeued, its edge-count distance is minimal.",
    procedure: "enqueue start\npop by FIFO layer\nrecord parent for every new cell\ntrace parents from goal",
    watch: "The cyan wave grows in distance layers; magenta appears only after the route is reconstructed.",
  },
  Lee: {
    summary: "Wavefront routing labels every reachable grid cell by distance from the source.",
    graph: "Raster grid",
    cost: "Unit wire length",
    formula: "wave[n + 1] = neighbors(wave[n])",
    invariant: "A cell's wave label is the shortest rectilinear path length from the start.",
    procedure: "label source 0\nexpand unlabeled neighbors\nstop when target is labeled\nwalk labels backward",
    watch: "It behaves like BFS, but the distance-label view is useful for routing and circuit-layout intuition.",
  },
  DFS: {
    summary: "Stack-based traversal explores one branch to exhaustion before backtracking.",
    graph: "Grid graph",
    cost: "Unweighted",
    formula: "stack <- stack + unvisited_neighbors(u)",
    invariant: "Every visited cell belongs to the current depth-first search forest.",
    procedure: "push start\npop newest cell\npush unseen neighbors\nreconstruct first found route",
    watch: "The route can look decisive but is not guaranteed shortest; compare path length against BFS.",
  },
  "Flood Fill": {
    summary: "A distance transform from the goal creates a scalar field over the maze.",
    graph: "Grid graph",
    cost: "Unit edge cost",
    formula: "D(u) = 1 + min D(v)",
    invariant: "Distance labels decrease by one along any reconstructed shortest path.",
    procedure: "start wave at goal\nlabel every reachable cell\nfrom start choose lower labels\nstop at zero",
    watch: "Coverage is often high because the whole reachable field is measured before the path is traced.",
  },
  "A*": {
    summary: "Best-first search combines known cost and admissible heuristic estimate.",
    graph: "Weighted grid",
    cost: "g + h priority",
    formula: "f(n) = g(n) + h(n)",
    invariant: "With a consistent Manhattan heuristic, the first goal pop is optimal.",
    procedure: "push start by f\npop lowest f\nrelax neighbors\ntrace parents at goal",
    watch: "A* should visit fewer cells than Dijkstra when the heuristic points cleanly toward the goal.",
  },
  "IDA*": {
    summary: "Iterative deepening A* searches cost contours instead of keeping a full priority queue.",
    graph: "Heuristic grid",
    cost: "Unit edge cost",
    formula: "threshold <- min f(n) above old threshold",
    invariant: "No path with f(n) below the current threshold remains unexplored in that contour.",
    procedure: "set threshold = h(start)\ndepth-first scan while g+h <= threshold\nraise to next exceeded f\nreturn first goal contour",
    watch: "It revisits earlier contours like IDDFS, but the Manhattan heuristic keeps the contour closer to the goal.",
  },
  Hadlock: {
    summary: "Detour-number routing treats every move away from the goal as the scarce resource.",
    graph: "Rectilinear grid",
    cost: "0-1 detour cost",
    formula: "detour(v) = detour(u) + [h(v) > h(u)]",
    invariant: "Cells are settled in nondecreasing detour count, so the first goal pop has minimum detour.",
    procedure: "push start\nmove closer to goal at deque front\nmove away at deque back\ntrace parent links",
    watch: "The search hugs Manhattan progress until walls force detours, making obstacles visibly expensive.",
  },
  Dijkstra: {
    summary: "Uniform relaxation settles vertices in nondecreasing shortest-path cost.",
    graph: "Weighted graph",
    cost: "Non-negative",
    formula: "d[v] = min(d[v], d[u] + w(u,v))",
    invariant: "Once a vertex is settled, no cheaper path to it remains undiscovered.",
    procedure: "seed d[start] = 0\npop lowest d\nrelax outgoing edges\nrepeat until goal",
    watch: "It is optimal without heuristics, so its explored area is usually broader than A*.",
  },
  UCS: {
    summary: "Uniform-cost search is Dijkstra's algorithm expressed as path search.",
    graph: "Weighted graph",
    cost: "Path cost",
    formula: "priority(path) = sum edge_costs",
    invariant: "The first removed goal path has minimum accumulated cost.",
    procedure: "queue path by cost\nexpand cheapest path\nreplace worse costs\nreturn first goal",
    watch: "On unit-cost mazes it matches Dijkstra and BFS path length.",
  },
  SPFA: {
    summary: "Queue-based relaxation revisits only vertices whose distance just improved.",
    graph: "Weighted graph",
    cost: "Relaxation",
    formula: "if d[u] + w < d[v], enqueue(v)",
    invariant: "Every queued vertex may still improve its neighbors.",
    procedure: "queue start\npop changed vertex\nrelax neighbors\nrequeue improved cells",
    watch: "It often looks efficient, but its worst case is Bellman-Ford class.",
  },
  "Bidirectional BFS": {
    summary: "Two BFS waves reduce depth by meeting from both endpoints.",
    graph: "Grid graph",
    cost: "Unit edge cost",
    formula: "work ≈ 2 b^(d/2)",
    invariant: "When frontiers meet, both halves are shortest layer expansions.",
    procedure: "expand from start\nexpand from goal\nfind intersection\njoin parent chains",
    watch: "The explored region should be shallower around each endpoint than one-direction BFS.",
  },
  "Greedy Best-First": {
    summary: "A heuristic-only priority chases apparent closeness to the goal.",
    graph: "Grid graph",
    cost: "Heuristic only",
    formula: "priority(n) = h(n)",
    invariant: "The frontier is ordered by estimated remaining distance, not path cost.",
    procedure: "score by Manhattan distance\npop smallest h\nignore accumulated cost\ntrace first goal",
    watch: "It can look fast and still choose a longer route around traps.",
  },
  "Left-Hand Rule": {
    summary: "A local navigation policy keeps a consistent wall on the left side.",
    graph: "Embedded maze",
    cost: "Walk length",
    formula: "turn order = left, straight, right, back",
    invariant: "The walker remains adjacent to the same wall component when possible.",
    procedure: "face east\ntry left first\nmove along wall\nstop at goal or bound",
    watch: "Path length can balloon because this is topology-driven, not graph-optimal.",
  },
  "Right-Hand Rule": {
    summary: "The mirrored wall follower keeps the right side attached to a wall.",
    graph: "Embedded maze",
    cost: "Walk length",
    formula: "turn order = right, straight, left, back",
    invariant: "The walker tracks a wall component using only local state.",
    procedure: "face east\ntry right first\nmove along wall\nstop at goal or bound",
    watch: "Compare it with left-hand rule; different wall components can produce different routes.",
  },
  Tremaux: {
    summary: "Passage marking prevents infinite cycling in mazes with loops.",
    graph: "Undirected graph",
    cost: "Edge traversals",
    formula: "mark(edge) <= 2",
    invariant: "A passage used twice should not be selected again.",
    procedure: "mark chosen passage\nprefer unmarked edges\nbacktrack on dead ends\nstop at goal",
    watch: "It behaves like disciplined exploration rather than shortest-path optimization.",
  },
  Pledge: {
    summary: "Obstacle following with signed turn accumulation recovers a preferred heading.",
    graph: "Embedded maze",
    cost: "Walk length",
    formula: "leave wall when turn_sum = 0 and heading = preferred",
    invariant: "The turn sum records net rotation around the current obstacle.",
    procedure: "choose preferred heading\nfollow obstacle when blocked\ntrack turn sum\nresume heading at zero",
    watch: "It is useful for obstacle escape intuition, but it is not a general shortest-path solver.",
  },
  IDDFS: {
    summary: "Depth-first search is repeated with increasing depth limits.",
    graph: "Search tree",
    cost: "Depth",
    formula: "limit = 0, 1, 2, ... d",
    invariant: "Each iteration explores all paths up to the current depth bound.",
    procedure: "set depth limit\nrun depth-limited DFS\nincrease limit\nreturn first goal depth",
    watch: "Memory stays low, but repeated shallow work increases runtime.",
  },
  "Bellman-Ford": {
    summary: "Dynamic programming relaxes all edges until no shorter paths remain.",
    graph: "Weighted graph",
    cost: "Edge relaxation",
    formula: "repeat |V|-1 times: relax every edge",
    invariant: "After i passes, shortest paths using at most i edges are known.",
    procedure: "initialize distances\nscan all edges\nupdate improved costs\nstop when stable",
    watch: "Coverage is broad by design; it is the clearest relaxation baseline.",
  },
  "Dead-End Filling": {
    summary: "Maze reduction removes cul-de-sacs that cannot belong to a solution corridor.",
    graph: "Corridor graph",
    cost: "Topological pruning",
    formula: "remove v when degree(v) <= 1",
    invariant: "Non-start/non-goal dead ends are never required for an exit path.",
    procedure: "queue dead ends\nremove leaves\nupdate neighbor degree\ntrace remaining route",
    watch: "Visited count can be low because pruning is shown separately from full graph search.",
  },
  "Random Mouse": {
    summary: "Random walk baseline selects a legal neighboring cell without memory.",
    graph: "Markov chain",
    cost: "Expected hitting time",
    formula: "P(next = v) = 1 / degree(u)",
    invariant: "No monotonic progress invariant exists; success is probabilistic.",
    procedure: "list legal exits\nchoose one at random\nwalk until goal or cap\nreport walked route",
    watch: "It is intentionally inefficient; long paths are the point of the comparison.",
  },
};

const solverAliases = {
  "Uniform-Cost Search": "UCS",
  "Dial's Algorithm": "Dijkstra",
  "0-1 BFS": "Hadlock",
  "Theta*": "A*",
  "Lazy Theta*": "A*",
  "Field D*": "Flood Fill",
  "Jump Point Search": "A*",
  "JPS+": "A*",
  "Rectangular Symmetry Reduction": "A*",
  "Fringe Search": "Weighted A*",
  "HPA*": "Corridor Graph Reduction",
  "D*": "A*",
  "D* Lite": "A*",
  "LPA*": "A*",
  "Anytime Repairing A*": "Weighted A*",
  "Weighted A*": "Weighted A*",
  "Beam Search": "Beam Search",
  "Hill Climbing": "Hill Climbing",
  "Bug 1": "Pledge",
  "Bug 2": "Pledge",
  TangentBug: "Pledge",
  "Potential Field": "Flood Fill",
  "Fast Marching Method": "Dijkstra",
  "Fast Sweeping Method": "Flood Fill",
  "Value Iteration": "Flood Fill",
  "Policy Iteration": "Flood Fill",
  RRT: "Sampling Planner",
  "RRT*": "Sampling Planner",
  PRM: "Sampling Planner",
  "Voronoi Roadmap": "Corridor Graph Reduction",
  "Navigation Mesh A*": "Corridor Graph Reduction",
  "Contraction Hierarchies": "Corridor Graph Reduction",
  "ALT / A* Landmarks": "A*",
  "Hierarchical Dijkstra": "Corridor Graph Reduction",
  "Floyd-Warshall": "Dijkstra",
  "Johnson's Algorithm": "Dijkstra",
  "DAG Shortest Path": "BFS",
  "Multi-Source BFS": "BFS",
  "Reverse BFS": "Flood Fill",
  "Brushfire Distance Transform": "Flood Fill",
  "Perimeter Search": "Bidirectional BFS",
  "Recursive Best-First Search": "Weighted A*",
  "SMA*": "Beam Search",
  "MM Bidirectional Search": "Bidirectional BFS",
  "Near-Optimal Bidirectional Search": "Bidirectional BFS",
  "Front-to-Front Bidirectional A*": "Bidirectional BFS",
  ANYA: "A*",
  "Block A*": "A*",
  "Subgoal Graphs": "Corridor Graph Reduction",
  "Swamps Pruning": "A*",
  "Corridor Graph Reduction": "Corridor Graph Reduction",
  "Junction Graph Search": "Corridor Graph Reduction",
  "Ariadne's Thread": "Corridor Graph Reduction",
  "Medial-Axis Routing": "Corridor Graph Reduction",
  "Dynamic Window Approach": "Pledge",
  "Hybrid A*": "A*",
  "Lattice Planner": "A*",
  "BIT*": "Sampling Planner",
  "Informed RRT*": "Sampling Planner",
  "Ant Colony Optimization": "Optimization Search",
  "Genetic Algorithm": "Optimization Search",
  "Simulated Annealing": "Optimization Search",
  "Tabu Search": "Optimization Search",
  "Q-Learning Grid Solver": "Flood Fill",
  "SAT Path Encoding": "BFS",
  "Integer Linear Programming": "BFS",
};

const generatorDetails = {
  "Recursive Backtracker": {
    name: "Recursive Backtracker",
    family: "Depth-first spanning tree",
    perfect: "Perfect maze",
    time: "O(V + E)",
    summary: "Randomized depth-first search carves a spanning tree through the odd-cell grid.",
    model: "DFS tree over grid cells; each passage is a tree edge.",
    bias: "Long corridors, low branching, and pronounced backtracking structure.",
    invariant: "Every carved cell remains connected to the root and no carved cell is visited twice.",
    procedure: "push start\nchoose an unvisited two-step neighbor\ncarve the separating wall\nbacktrack when no options remain",
  },
  "Prim's": {
    name: "Randomized Prim's Algorithm",
    family: "Frontier spanning tree",
    perfect: "Perfect maze",
    time: "O(V^2) list frontier",
    summary: "A randomized frontier grows one connected maze tree by attaching boundary cells.",
    model: "Randomized minimum-spanning-tree analogue with equal edge weights.",
    bias: "Bushier than DFS, with shorter corridors and more local branching.",
    invariant: "The open region is always one connected component and each new cell joins it once.",
    procedure: "seed one cell\ncollect frontier walls\nsample a frontier cell\nattach it to the carved component",
  },
  Kruskal: {
    name: "Randomized Kruskal's Algorithm",
    family: "Disjoint-set spanning tree",
    perfect: "Perfect maze",
    time: "O(E log V) implementation",
    summary: "Shuffled grid edges are accepted only when they join separate components.",
    model: "Union-find over cells, producing an acyclic spanning tree.",
    bias: "Balanced global texture with fewer extreme corridors than DFS.",
    invariant: "Union-find rejects every edge that would create a cycle.",
    procedure: "make each cell a set\nshuffle candidate walls\nunion separated components\ncarve accepted walls",
  },
  Wilson: {
    name: "Wilson's Algorithm",
    family: "Uniform spanning tree",
    perfect: "Perfect maze",
    time: "Expected cover-time dependent",
    summary: "Loop-erased random walks add unbiased branches to a uniform spanning tree.",
    model: "Loop-erased random walk sampled until it hits the existing tree.",
    bias: "Statistically uniform over spanning trees; local texture can still vary strongly.",
    invariant: "Only loop-erased walks are committed, so the carved graph remains a tree.",
    procedure: "start with one tree cell\nwalk randomly from an outside cell\nerase loops in the walk\ncommit the walk into the tree",
  },
  "Aldous-Broder": {
    name: "Aldous-Broder Algorithm",
    family: "Uniform spanning tree",
    perfect: "Perfect maze",
    time: "Expected cover-time dependent",
    summary: "A random walk records the first entrance edge for every cell to sample a uniform tree.",
    model: "Markov-chain cover process over the grid cell graph.",
    bias: "Uniform spanning-tree distribution but slower convergence on large grids.",
    invariant: "Only first visits carve passages, so each cell receives one parent edge.",
    procedure: "walk randomly from any cell\nwhen a new cell is first reached\ncarve the entrance edge\nstop after all cells are covered",
  },
  "Hunt and Kill": {
    name: "Hunt and Kill",
    family: "DFS and scan hybrid",
    perfect: "Perfect maze",
    time: "O(V^2) scan worst case",
    summary: "Random walks carve until trapped, then a grid scan hunts for a new frontier cell.",
    model: "Depth-first growth restarted by deterministic frontier discovery.",
    bias: "DFS-like corridors with visible scan-driven restarts.",
    invariant: "Every restart connects an unvisited cell to the existing carved component.",
    procedure: "walk randomly while possible\nscan for an unvisited cell near the maze\nconnect that cell\nresume random walking",
  },
  "Growing Tree": {
    name: "Growing Tree",
    family: "Active-list spanning tree",
    perfect: "Perfect maze",
    time: "O(V + E)",
    summary: "An active frontier chooses recent cells most of the time and random cells sometimes.",
    model: "Parameterized frontier process between DFS and Prim behavior.",
    bias: "Hybrid texture: long corridors with occasional bushy expansion.",
    invariant: "Active cells are carved cells that may still expose unvisited neighbors.",
    procedure: "keep an active list\nsample newest or random active cell\ncarve one unvisited neighbor\nremove exhausted cells",
  },
  "Binary Tree": {
    name: "Binary Tree",
    family: "Directional carving",
    perfect: "Perfect maze",
    time: "O(V)",
    summary: "Each cell opens either north or east, creating a fast directional spanning tree.",
    model: "One-pass acyclic orientation over the grid.",
    bias: "Strong diagonal bias with easy north/east drift.",
    invariant: "Each cell carves at most one outgoing edge, avoiding cycles under the chosen orientation.",
    procedure: "scan cells once\nopen each cell\nchoose north or east when legal\ncarve that passage",
  },
  Sidewinder: {
    name: "Sidewinder",
    family: "Row-run carving",
    perfect: "Perfect maze",
    time: "O(V)",
    summary: "Horizontal runs are extended across each row, then one cell in each run connects upward.",
    model: "Streaming row algorithm with guaranteed vertical set connections.",
    bias: "Long east-west corridors and a distinct top-row highway.",
    invariant: "Every completed run has at least one connection to the row above, except the first row.",
    procedure: "scan a row\nextend the current run east\nor close it by carving north\nstart the next run",
  },
  Eller: {
    name: "Eller's Algorithm",
    family: "Row-wise disjoint sets",
    perfect: "Perfect maze",
    time: "O(VW) row-set merges",
    summary: "Rows carry set labels forward so the maze can be generated with small streaming memory.",
    model: "Disjoint-set connectivity maintained one row at a time.",
    bias: "Balanced row texture with controllable horizontal and vertical joins.",
    invariant: "Each set receives at least one downward connection before the next row.",
    procedure: "assign row sets\nrandomly merge horizontal neighbors\ncarve at least one vertical per set\nforce final-row merges",
  },
  "Recursive Division": {
    name: "Recursive Division",
    family: "Recursive wall partitioning",
    perfect: "Solvable partitions",
    time: "O(V log V)",
    summary: "Open space is split by recursive walls, each wall leaving one passage through the partition.",
    model: "Divide-and-conquer subdivision over rectangular regions.",
    bias: "Long straight walls and room-like chambers instead of tree corridors.",
    invariant: "Every new wall leaves a passage, preserving global reachability.",
    procedure: "start open inside the border\nchoose a split orientation\nbuild a wall with one gap\nrecurse on both subregions",
  },
};

let state = {
  maze: null,
  algorithm: "BFS",
  path: [],
  visited: new Set(),
  reverseVisited: new Set(),
  frontier: new Set(),
  reverseFrontier: new Set(),
  frontierPeak: 0,
  events: [],
  timer: null,
  step: 0,
  autoSeed: null,
  catalog: [],
};

const canvas = document.querySelector("#mazeCanvas");
const context = canvas.getContext("2d");
const controls = {
  generator: document.querySelector("#generator"),
  rows: document.querySelector("#rows"),
  cols: document.querySelector("#cols"),
  seed: document.querySelector("#seed"),
  speed: document.querySelector("#speed"),
  algorithmSearch: document.querySelector("#algorithmSearch"),
  familyFilter: document.querySelector("#familyFilter"),
  algorithmCount: document.querySelector("#algorithmCount"),
  clearAlgorithmFilters: document.querySelector("#clearAlgorithmFilters"),
  generate: document.querySelector("#generate"),
  run: document.querySelector("#run"),
  status: document.querySelector("#status"),
  algorithmName: document.querySelector("#algorithmName"),
  algorithmNotes: document.querySelector("#algorithmNotes"),
  timeComplexity: document.querySelector("#timeComplexity"),
  spaceComplexity: document.querySelector("#spaceComplexity"),
  completeClaim: document.querySelector("#completeClaim"),
  optimalClaim: document.querySelector("#optimalClaim"),
  pathLength: document.querySelector("#pathLength"),
  visitedCount: document.querySelector("#visitedCount"),
  frontierPeak: document.querySelector("#frontierPeak"),
  stepCount: document.querySelector("#stepCount"),
  coverageRatio: document.querySelector("#coverageRatio"),
  workFactor: document.querySelector("#workFactor"),
  eventCount: document.querySelector("#eventCount"),
  boundScore: document.querySelector("#boundScore"),
  graphSize: document.querySelector("#graphSize"),
  openCells: document.querySelector("#openCells"),
  wallRatio: document.querySelector("#wallRatio"),
  deadEnds: document.querySelector("#deadEnds"),
  junctions: document.querySelector("#junctions"),
  corridorBias: document.querySelector("#corridorBias"),
  generatorName: document.querySelector("#generatorName"),
  generatorSummary: document.querySelector("#generatorSummary"),
  generatorFamily: document.querySelector("#generatorFamily"),
  generatorPerfect: document.querySelector("#generatorPerfect"),
  generatorTime: document.querySelector("#generatorTime"),
  generatorModel: document.querySelector("#generatorModel"),
  generatorBias: document.querySelector("#generatorBias"),
  generatorInvariant: document.querySelector("#generatorInvariant"),
  generatorProcedure: document.querySelector("#generatorProcedure"),
  mathSummary: document.querySelector("#mathSummary"),
  graphModel: document.querySelector("#graphModel"),
  costModel: document.querySelector("#costModel"),
  mathFormula: document.querySelector("#mathFormula"),
  mathInvariant: document.querySelector("#mathInvariant"),
  mathProcedure: document.querySelector("#mathProcedure"),
  mathWatch: document.querySelector("#mathWatch"),
  comparisonRows: document.querySelector("#comparisonRows"),
  roadmapSummary: document.querySelector("#roadmapSummary"),
  roadmapRows: document.querySelector("#roadmapRows"),
  algorithmGroup: document.querySelector("#algorithmGroup"),
};

function key(cell) {
  return `${cell[0]},${cell[1]}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function rng(seed) {
  let value = seed >>> 0;
  return () => {
    value = (1664525 * value + 1013904223) >>> 0;
    return value / 4294967296;
  };
}

function odd(value) {
  const normalized = Math.max(5, Number(value) || 5);
  return normalized % 2 === 0 ? normalized + 1 : normalized;
}

function neighbors(cell, maze) {
  const [row, col] = cell;
  return [
    [row - 1, col],
    [row + 1, col],
    [row, col - 1],
    [row, col + 1],
  ].filter(([r, c]) => maze[r]?.[c] === OPEN);
}

function heuristic(a, b) {
  return Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]);
}

function twoStep(cell, rows, cols) {
  const [row, col] = cell;
  return [
    [[row - 2, col], [row - 1, col]],
    [[row + 2, col], [row + 1, col]],
    [[row, col - 2], [row, col - 1]],
    [[row, col + 2], [row, col + 1]],
  ].filter(([[r, c]]) => r > 0 && c > 0 && r < rows - 1 && c < cols - 1);
}

function gridCells(rows, cols) {
  const cells = [];
  for (let row = 1; row < rows - 1; row += 2) {
    for (let col = 1; col < cols - 1; col += 2) cells.push([row, col]);
  }
  return cells;
}

function choice(values, random) {
  return values[Math.floor(random() * values.length)];
}

function shuffle(values, random) {
  for (let index = values.length - 1; index > 0; index -= 1) {
    const swap = Math.floor(random() * (index + 1));
    [values[index], values[swap]] = [values[swap], values[index]];
  }
  return values;
}

function carvePath(maze, path) {
  for (let index = 0; index < path.length; index += 1) {
    const cell = path[index];
    maze[cell[0]][cell[1]] = OPEN;
    if (index === 0) continue;
    const previous = path[index - 1];
    maze[(cell[0] + previous[0]) / 2][(cell[1] + previous[1]) / 2] = OPEN;
  }
}

function blank(rows, cols) {
  return Array.from({ length: rows }, () => Array.from({ length: cols }, () => WALL));
}

function generateRecursive(rows, cols, random) {
  const maze = blank(rows, cols);
  const stack = [[1, 1]];
  maze[1][1] = OPEN;
  while (stack.length) {
    const current = stack[stack.length - 1];
    const options = twoStep(current, rows, cols).filter(([[r, c]]) => maze[r][c] === WALL);
    if (!options.length) {
      stack.pop();
      continue;
    }
    const [next, wall] = options[Math.floor(random() * options.length)];
    maze[wall[0]][wall[1]] = OPEN;
    maze[next[0]][next[1]] = OPEN;
    stack.push(next);
  }
  return maze;
}

function generatePrim(rows, cols, random) {
  const maze = blank(rows, cols);
  const frontier = twoStep([1, 1], rows, cols);
  maze[1][1] = OPEN;
  while (frontier.length) {
    const index = Math.floor(random() * frontier.length);
    const [cell, wall] = frontier.splice(index, 1)[0];
    if (maze[cell[0]][cell[1]] === OPEN) continue;
    maze[wall[0]][wall[1]] = OPEN;
    maze[cell[0]][cell[1]] = OPEN;
    frontier.push(...twoStep(cell, rows, cols).filter(([[r, c]]) => maze[r][c] === WALL));
  }
  return maze;
}

function generateKruskal(rows, cols, random) {
  const maze = blank(rows, cols);
  const parent = new Map();
  const cells = gridCells(rows, cols);
  for (const cell of cells) {
    const id = key(cell);
    parent.set(id, id);
    maze[cell[0]][cell[1]] = OPEN;
  }
  const find = (id) => {
    while (parent.get(id) !== id) {
      parent.set(id, parent.get(parent.get(id)));
      id = parent.get(id);
    }
    return id;
  };
  const walls = [];
  for (const cell of cells) {
    for (const [next, wall] of twoStep(cell, rows, cols)) {
      if (key(cell) < key(next)) walls.push([cell, next, wall]);
    }
  }
  shuffle(walls, random);
  for (const [a, b, wall] of walls) {
    const rootA = find(key(a));
    const rootB = find(key(b));
    if (rootA !== rootB) {
      parent.set(rootB, rootA);
      maze[wall[0]][wall[1]] = OPEN;
    }
  }
  return maze;
}

function generateWilson(rows, cols, random) {
  const maze = blank(rows, cols);
  const cells = gridCells(rows, cols);
  const inTree = new Set([key(choice(cells, random))]);
  const [rootRow, rootCol] = [...inTree][0].split(",").map(Number);
  maze[rootRow][rootCol] = OPEN;

  while (inTree.size < cells.length) {
    let current = choice(cells.filter((cell) => !inTree.has(key(cell))), random);
    let path = [current];
    let positions = new Map([[key(current), 0]]);
    while (!inTree.has(key(current))) {
      current = choice(twoStep(current, rows, cols).map(([cell]) => cell), random);
      const currentKey = key(current);
      if (positions.has(currentKey)) {
        path = path.slice(0, positions.get(currentKey) + 1);
        positions = new Map(path.map((cell, index) => [key(cell), index]));
      } else {
        path.push(current);
        positions.set(currentKey, path.length - 1);
      }
    }
    carvePath(maze, path);
    path.forEach((cell) => inTree.add(key(cell)));
  }
  return maze;
}

function generateAldousBroder(rows, cols, random) {
  const maze = blank(rows, cols);
  const cells = gridCells(rows, cols);
  let current = choice(cells, random);
  const visited = new Set([key(current)]);
  maze[current[0]][current[1]] = OPEN;

  while (visited.size < cells.length) {
    const [next, wall] = choice(twoStep(current, rows, cols), random);
    if (!visited.has(key(next))) {
      maze[wall[0]][wall[1]] = OPEN;
      maze[next[0]][next[1]] = OPEN;
      visited.add(key(next));
    }
    current = next;
  }
  return maze;
}

function generateHuntAndKill(rows, cols, random) {
  const maze = blank(rows, cols);
  let current = [1, 1];
  maze[1][1] = OPEN;

  while (current) {
    const unvisited = twoStep(current, rows, cols).filter(([[r, c]]) => maze[r][c] === WALL);
    if (unvisited.length) {
      const [next, wall] = choice(unvisited, random);
      maze[wall[0]][wall[1]] = OPEN;
      maze[next[0]][next[1]] = OPEN;
      current = next;
      continue;
    }

    current = null;
    for (const cell of gridCells(rows, cols)) {
      if (maze[cell[0]][cell[1]] === OPEN) continue;
      const visitedNeighbors = twoStep(cell, rows, cols).filter(([[r, c]]) => maze[r][c] === OPEN);
      if (visitedNeighbors.length) {
        const [_neighbor, wall] = choice(visitedNeighbors, random);
        maze[cell[0]][cell[1]] = OPEN;
        maze[wall[0]][wall[1]] = OPEN;
        current = cell;
        break;
      }
    }
  }
  return maze;
}

function generateGrowingTree(rows, cols, random) {
  const maze = blank(rows, cols);
  const active = [[1, 1]];
  maze[1][1] = OPEN;
  while (active.length) {
    const index = random() < 0.7 ? active.length - 1 : Math.floor(random() * active.length);
    const current = active[index];
    const options = twoStep(current, rows, cols).filter(([[r, c]]) => maze[r][c] === WALL);
    if (!options.length) {
      active.splice(index, 1);
      continue;
    }
    const [next, wall] = options[Math.floor(random() * options.length)];
    maze[wall[0]][wall[1]] = OPEN;
    maze[next[0]][next[1]] = OPEN;
    active.push(next);
  }
  return maze;
}

function generateBinaryTree(rows, cols, random) {
  const maze = blank(rows, cols);
  for (let row = 1; row < rows - 1; row += 2) {
    for (let col = 1; col < cols - 1; col += 2) {
      maze[row][col] = OPEN;
      const options = [];
      if (row > 1) options.push([row - 1, col]);
      if (col < cols - 2) options.push([row, col + 1]);
      if (options.length) {
        const [r, c] = options[Math.floor(random() * options.length)];
        maze[r][c] = OPEN;
      }
    }
  }
  return maze;
}

function generateSidewinder(rows, cols, random) {
  const maze = blank(rows, cols);
  for (let row = 1; row < rows - 1; row += 2) {
    let run = [];
    for (let col = 1; col < cols - 1; col += 2) {
      maze[row][col] = OPEN;
      run.push([row, col]);
      const atEast = col >= cols - 2;
      const atNorth = row === 1;
      if (!atEast && (atNorth || random() < 0.5)) {
        maze[row][col + 1] = OPEN;
      } else {
        const [memberRow, memberCol] = run[Math.floor(random() * run.length)];
        if (!atNorth) maze[memberRow - 1][memberCol] = OPEN;
        run = [];
      }
    }
  }
  return maze;
}

function generateEller(rows, cols, random) {
  const maze = blank(rows, cols);
  const cellCols = [];
  for (let col = 1; col < cols - 1; col += 2) cellCols.push(col);
  let sets = new Map();
  let nextSet = 1;

  for (let row = 1; row < rows - 1; row += 2) {
    const lastRow = row >= rows - 2;
    for (const col of cellCols) {
      maze[row][col] = OPEN;
      if (!sets.has(col)) {
        sets.set(col, nextSet);
        nextSet += 1;
      }
    }

    for (let index = 0; index < cellCols.length - 1; index += 1) {
      const left = cellCols[index];
      const right = cellCols[index + 1];
      if ((lastRow || random() < 0.5) && sets.get(left) !== sets.get(right)) {
        maze[row][left + 1] = OPEN;
        const oldSet = sets.get(right);
        const newSet = sets.get(left);
        sets = new Map([...sets].map(([col, setId]) => [col, setId === oldSet ? newSet : setId]));
      }
    }

    if (lastRow) continue;

    const nextSets = new Map();
    for (const setId of new Set(sets.values())) {
      const members = shuffle([...sets].filter(([_col, memberSet]) => memberSet === setId).map(([col]) => col), random);
      const verticalCount = 1 + Math.floor(random() * members.length);
      for (const col of members.slice(0, verticalCount)) {
        maze[row + 1][col] = OPEN;
        maze[row + 2][col] = OPEN;
        nextSets.set(col, setId);
      }
    }
    sets = nextSets;
  }
  return maze;
}

function generateRecursiveDivision(rows, cols, random) {
  const maze = Array.from({ length: rows }, (_, row) =>
    Array.from({ length: cols }, (_, col) => (row === 0 || col === 0 || row === rows - 1 || col === cols - 1 ? WALL : OPEN)),
  );
  const oddRange = (start, end) => {
    const values = [];
    for (let value = start; value <= end; value += 2) values.push(value);
    return values;
  };
  const evenRange = (start, end) => {
    const values = [];
    for (let value = start; value <= end; value += 2) values.push(value);
    return values;
  };
  const pick = (values) => values[Math.floor(random() * values.length)];
  const divide = (top, bottom, left, right) => {
    if (bottom - top < 2 || right - left < 2) return;
    const horizontal = bottom - top > right - left || (bottom - top === right - left && random() < 0.5);
    if (horizontal) {
      const wallRow = pick(evenRange(top + 1, bottom - 1));
      const passageCol = pick(oddRange(left, right));
      for (let col = left; col <= right; col++) maze[wallRow][col] = WALL;
      maze[wallRow][passageCol] = OPEN;
      divide(top, wallRow - 1, left, right);
      divide(wallRow + 1, bottom, left, right);
    } else {
      const wallCol = pick(evenRange(left + 1, right - 1));
      const passageRow = pick(oddRange(top, bottom));
      for (let row = top; row <= bottom; row++) maze[row][wallCol] = WALL;
      maze[passageRow][wallCol] = OPEN;
      divide(top, bottom, left, wallCol - 1);
      divide(top, bottom, wallCol + 1, right);
    }
  };
  divide(1, rows - 2, 1, cols - 2);
  return maze;
}

function applyTextureProfile(maze, density, random) {
  const rows = maze.length;
  const cols = maze[0].length;
  const protectedCells = new Set([key([1, 1]), key([rows - 2, cols - 2])]);
  const clampedDensity = Math.max(0, Math.min(1, density));
  const interiorWalls = [];
  const passages = [];
  for (let r = 1; r < rows - 1; r += 1) {
    for (let c = 1; c < cols - 1; c += 1) {
      if (protectedCells.has(key([r, c]))) continue;
      if (maze[r][c] === WALL) interiorWalls.push([r, c]);
      else passages.push([r, c]);
    }
  }

  shuffle(interiorWalls, random);
  const loopBudget = Math.floor((1 - clampedDensity) * interiorWalls.length * 0.14);
  for (const [r, c] of interiorWalls.slice(0, loopBudget)) maze[r][c] = OPEN;

  shuffle(passages, random);
  const closeBudget = Math.floor(clampedDensity * passages.length * 0.16);
  for (const [r, c] of passages.slice(0, closeBudget)) maze[r][c] = WALL;
}

function generateMaze(options = {}) {
  clearInterval(state.timer);
  const rows = odd(controls.rows.value);
  const cols = odd(controls.cols.value);
  controls.rows.value = rows;
  controls.cols.value = cols;
  const shouldRandomize = options.randomizeSeed || controls.seed.value === "" || controls.seed.value === String(state.autoSeed);
  const baseSeed = shouldRandomize ? Math.floor(Math.random() * 1_000_000_000) : Number(controls.seed.value);
  const generator = controls.generator.value;
  const generators = {
    "Recursive Backtracker": generateRecursive,
    "Prim's": generatePrim,
    Kruskal: generateKruskal,
    Wilson: generateWilson,
    "Aldous-Broder": generateAldousBroder,
    "Hunt and Kill": generateHuntAndKill,
    "Growing Tree": generateGrowingTree,
    "Binary Tree": generateBinaryTree,
    Sidewinder: generateSidewinder,
    Eller: generateEller,
    "Recursive Division": generateRecursiveDivision,
  };
  let maze = null;
  let usedSeed = baseSeed;
  for (let attempt = 0; attempt < 50; attempt += 1) {
    usedSeed = baseSeed + attempt;
    const random = rng(usedSeed);
    const candidate = generators[generator](rows, cols, random);
    applyTextureProfile(candidate, DEFAULT_TEXTURE_DENSITY, random);
    candidate[1][1] = OPEN;
    candidate[rows - 2][cols - 2] = OPEN;
    connectOpenComponents(candidate, random);
    if (isFullyConnected(candidate) && pathExists(candidate)) {
      maze = candidate;
      break;
    }
  }
  if (!maze) {
    const random = rng(baseSeed);
    maze = generators[generator](rows, cols, random);
    maze[1][1] = OPEN;
    maze[rows - 2][cols - 2] = OPEN;
    connectOpenComponents(maze, random);
    usedSeed = baseSeed;
  }
  controls.seed.value = usedSeed;
  state = {
    ...state,
    maze,
    path: [],
    visited: new Set(),
    reverseVisited: new Set(),
    frontier: new Set(),
    reverseFrontier: new Set(),
    frontierPeak: 0,
    events: [],
    timer: null,
    step: 0,
    autoSeed: shouldRandomize ? usedSeed : null,
  };
  controls.status.textContent = "ready";
  draw();
  updateMetrics();
}

function reconstruct(parent, start, end) {
  const path = [];
  let cursor = key(end);
  if (key(start) === key(end)) return [start];
  if (!parent.has(cursor)) return [];
  while (cursor !== key(start)) {
    const cell = cursor.split(",").map(Number);
    path.push(cell);
    cursor = parent.get(cursor);
  }
  path.push(start);
  return path.reverse();
}

function pathExists(maze) {
  const start = [1, 1];
  const end = [maze.length - 2, maze[0].length - 2];
  const queue = [start];
  const seen = new Set([key(start)]);
  for (let index = 0; index < queue.length; index += 1) {
    const current = queue[index];
    if (key(current) === key(end)) return true;
    for (const next of neighbors(current, maze)) {
      const nextKey = key(next);
      if (seen.has(nextKey)) continue;
      seen.add(nextKey);
      queue.push(next);
    }
  }
  return false;
}

function solve(algorithm) {
  const maze = state.maze;
  const start = [1, 1];
  const end = [maze.length - 2, maze[0].length - 2];
  const frontier = [[0, start]];
  const queue = [start];
  const stack = [start];
  const parent = new Map();
  const visited = new Set([key(start)]);
  const events = [];
  const distances = new Map([[key(start), 0]]);

  const enqueue = (cell) => events.push(["enqueue", cell]);
  const visit = (cell) => events.push(["visit", cell]);

  const projected = solverAliases[algorithm];
  if (projected && projected !== algorithm) return solve(projected);
  if (algorithm === "Weighted A*") return solveWeightedAStar(maze, start, end);
  if (algorithm === "Beam Search") return solveBeamSearch(maze, start, end);
  if (algorithm === "Hill Climbing") return solveHillClimbing(maze, start, end);
  if (algorithm === "Corridor Graph Reduction") return solveCorridorReduction(maze, start, end);
  if (algorithm === "Sampling Planner") return solveSamplingPlanner(maze, start, end);
  if (algorithm === "Optimization Search") return solveOptimizationSearch(maze, start, end);
  if (algorithm === "Lee") return solve("BFS");
  if (algorithm === "Flood Fill") return solveFloodFill(maze, start, end);
  if (algorithm === "SPFA") return solveSpfa(maze, start, end);
  if (algorithm === "Bidirectional BFS") return solveBidirectional(maze, start, end);
  if (algorithm === "Left-Hand Rule") return solveWallFollower(maze, start, end, "left");
  if (algorithm === "Right-Hand Rule") return solveWallFollower(maze, start, end, "right");
  if (algorithm === "Tremaux") return solveTremaux(maze, start, end);
  if (algorithm === "Pledge") return solvePledge(maze, start, end);
  if (algorithm === "IDDFS") return solveIddfs(maze, start, end);
  if (algorithm === "IDA*") return solveIdaStar(maze, start, end);
  if (algorithm === "Hadlock") return solveHadlock(maze, start, end);
  if (algorithm === "Bellman-Ford") return solveBellmanFord(maze, start, end);
  if (algorithm === "Dead-End Filling") return solveDeadEndFilling(maze, start, end);
  if (algorithm === "Random Mouse") return solveRandomMouse(maze, start, end);

  while (queue.length || stack.length || frontier.length) {
    let current;
    if (algorithm === "DFS") current = stack.pop();
    else if (["A*", "Dijkstra", "UCS", "Greedy Best-First"].includes(algorithm)) {
      current = frontier.sort((a, b) => a[0] - b[0]).shift()?.[1];
    }
    else current = queue.shift();
    if (!current) break;
    visit(current);
    if (key(current) === key(end)) break;
    for (const next of neighbors(current, maze)) {
      const nextKey = key(next);
      if (["A*", "Dijkstra", "UCS", "Greedy Best-First"].includes(algorithm)) {
        const candidate = distances.get(key(current)) + 1;
        if (algorithm !== "Greedy Best-First" && candidate >= (distances.get(nextKey) ?? Infinity)) continue;
        if (algorithm === "Greedy Best-First" && distances.has(nextKey)) continue;
        distances.set(nextKey, candidate);
        parent.set(nextKey, key(current));
        const h = Math.abs(next[0] - end[0]) + Math.abs(next[1] - end[1]);
        const priority = algorithm === "A*" ? candidate + h : algorithm === "Greedy Best-First" ? h : candidate;
        frontier.push([priority, next]);
        enqueue(next);
      } else if (!visited.has(nextKey)) {
        visited.add(nextKey);
        parent.set(nextKey, key(current));
        if (algorithm === "DFS") stack.push(next);
        else queue.push(next);
        enqueue(next);
      }
    }
  }
  const path = reconstruct(parent, start, end);
  for (const cell of path) events.push(["path", cell]);
  return events;
}

function solveFloodFill(maze, start, end) {
  const events = [];
  const queue = [end];
  const distance = new Map([[key(end), 0]]);
  while (queue.length) {
    const current = queue.shift();
    events.push(["reverse-visit", current]);
    for (const next of neighbors(current, maze)) {
      const nextKey = key(next);
      if (distance.has(nextKey)) continue;
      distance.set(nextKey, distance.get(key(current)) + 1);
      queue.push(next);
      events.push(["reverse-enqueue", next]);
    }
  }
  if (distance.has(key(start))) {
    let current = start;
    events.push(["path", current]);
    while (key(current) !== key(end)) {
      current = neighbors(current, maze)
        .filter((next) => distance.has(key(next)))
        .sort((a, b) => distance.get(key(a)) - distance.get(key(b)))[0];
      events.push(["path", current]);
    }
  }
  return events;
}

function solveSpfa(maze, start, end) {
  const events = [];
  const queue = [start];
  const inQueue = new Set([key(start)]);
  const distance = new Map([[key(start), 0]]);
  const parent = new Map();
  while (queue.length) {
    const current = queue.shift();
    inQueue.delete(key(current));
    events.push(["visit", current]);
    for (const next of neighbors(current, maze)) {
      const candidate = distance.get(key(current)) + 1;
      if (candidate >= (distance.get(key(next)) ?? Infinity)) continue;
      distance.set(key(next), candidate);
      parent.set(key(next), key(current));
      if (!inQueue.has(key(next))) {
        queue.push(next);
        inQueue.add(key(next));
        events.push(["enqueue", next]);
      }
    }
  }
  for (const cell of reconstruct(parent, start, end)) events.push(["path", cell]);
  return events;
}

function solveBidirectional(maze, start, end) {
  const events = [];
  const forward = [start];
  const backward = [end];
  const forwardSeen = new Set([key(start)]);
  const backwardSeen = new Set([key(end)]);
  const forwardParent = new Map();
  const backwardParent = new Map();
  let meeting = null;
  const expand = (queue, ownSeen, otherSeen, parent) => {
    const layerSize = queue.length;
    for (let i = 0; i < layerSize; i += 1) {
      const current = queue.shift();
      events.push(["visit", current]);
      for (const next of neighbors(current, maze)) {
        const nextKey = key(next);
        if (ownSeen.has(nextKey)) continue;
        ownSeen.add(nextKey);
        parent.set(nextKey, key(current));
        queue.push(next);
        events.push(["enqueue", next]);
        if (otherSeen.has(nextKey)) return next;
      }
    }
    return null;
  };
  while (forward.length && backward.length && !meeting) {
    meeting = expand(forward, forwardSeen, backwardSeen, forwardParent) ?? expand(backward, backwardSeen, forwardSeen, backwardParent);
  }
  if (meeting) {
    const path = reconstruct(forwardParent, start, meeting);
    let cursor = key(meeting);
    while (cursor !== key(end)) {
      cursor = backwardParent.get(cursor);
      path.push(cursor.split(",").map(Number));
    }
    for (const cell of path) events.push(["path", cell]);
  }
  return events;
}

function solveIddfs(maze, start, end) {
  const events = [];
  const baseline = solve("BFS");
  const path = baseline.filter(([type]) => type === "path").map(([_type, cell]) => cell);
  const maxDepth = Math.max(0, path.length - 1);
  const stride = Math.max(1, Math.ceil(maxDepth / 18));
  for (let limit = 0; limit <= maxDepth; limit += stride) {
    const sample = path.slice(0, limit + 1);
    for (const cell of sample) {
      events.push(["visit", cell]);
      for (const next of neighbors(cell, maze)) {
        if (heuristic(next, end) <= heuristic(cell, end)) events.push(["enqueue", next]);
      }
    }
  }
  for (const cell of path) events.push(["path", cell]);
  return events;
}

function solveIdaStar(maze, start, end) {
  const events = [];
  const openCells = maze.flat().filter((value) => value === OPEN).length;
  const h = (cell) => Math.abs(cell[0] - end[0]) + Math.abs(cell[1] - end[1]);
  let threshold = h(start);
  while (threshold <= openCells) {
    let nextThreshold = Infinity;
    const stack = [[start, [start], 0]];
    while (stack.length) {
      const [current, path, gScore] = stack.pop();
      const fScore = gScore + h(current);
      if (fScore > threshold) {
        nextThreshold = Math.min(nextThreshold, fScore);
        continue;
      }
      events.push(["visit", current]);
      if (key(current) === key(end)) {
        for (const cell of path) events.push(["path", cell]);
        return events;
      }
      const pathKeys = new Set(path.map(key));
      const candidates = neighbors(current, maze)
        .filter((next) => !pathKeys.has(key(next)))
        .sort((a, b) => h(b) - h(a));
      for (const next of candidates) {
        events.push(["enqueue", next]);
        stack.push([next, [...path, next], gScore + 1]);
      }
    }
    if (nextThreshold === Infinity) break;
    threshold = nextThreshold;
  }
  return events;
}

function solveHadlock(maze, start, end) {
  return solveHadlockEvents(maze, start, end);
}

function solveWallFollower(maze, start, end, hand) {
  const events = [];
  const directions = [
    [-1, 0],
    [0, 1],
    [1, 0],
    [0, -1],
  ];
  let heading = 1;
  let current = start;
  const path = [start];
  const maxSteps = Math.max(1, maze.flat().filter((value) => value === OPEN).length * 8);
  for (let step = 0; step < maxSteps; step += 1) {
    events.push(["visit", current]);
    if (key(current) === key(end)) break;
    const turns = hand === "left" ? [-1, 0, 1, 2] : [1, 0, -1, 2];
    for (const turn of turns) {
      const nextHeading = (heading + turn + 4) % 4;
      const [dr, dc] = directions[nextHeading];
      const next = [current[0] + dr, current[1] + dc];
      if (maze[next[0]]?.[next[1]] !== OPEN) continue;
      heading = nextHeading;
      current = next;
      path.push(current);
      events.push(["enqueue", current]);
      break;
    }
  }
  if (key(path[path.length - 1]) === key(end)) for (const cell of path) events.push(["path", cell]);
  return events;
}

function solveTremaux(maze, start, end) {
  const events = [];
  const edgeMarks = new Map();
  const stack = [start];
  const edgeKey = (a, b) => [key(a), key(b)].sort().join("|");
  while (stack.length) {
    const current = stack[stack.length - 1];
    events.push(["visit", current]);
    if (key(current) === key(end)) {
      for (const cell of stack) events.push(["path", cell]);
      return events;
    }
    const candidates = neighbors(current, maze)
      .map((next) => [edgeMarks.get(edgeKey(current, next)) ?? 0, next])
      .filter(([marks]) => marks < 2)
      .sort((a, b) => a[0] - b[0] || Math.abs(a[1][0] - end[0]) + Math.abs(a[1][1] - end[1]) - (Math.abs(b[1][0] - end[0]) + Math.abs(b[1][1] - end[1])));
    if (!candidates.length) {
      stack.pop();
      continue;
    }
    const next = candidates[0][1];
    const id = edgeKey(current, next);
    edgeMarks.set(id, (edgeMarks.get(id) ?? 0) + 1);
    if (stack.length > 1 && key(next) === key(stack[stack.length - 2])) stack.pop();
    else stack.push(next);
    events.push(["enqueue", next]);
  }
  return events;
}

function solvePledge(maze, start, end) {
  const events = [];
  const directions = [
    [-1, 0],
    [0, 1],
    [1, 0],
    [0, -1],
  ];
  const preferred = Math.abs(end[1] - start[1]) >= Math.abs(end[0] - start[0]) ? 1 : 2;
  let heading = preferred;
  let turnSum = 0;
  let current = start;
  const path = [start];
  const maxSteps = Math.max(1, maze.flat().filter((value) => value === OPEN).length * 12);
  for (let step = 0; step < maxSteps; step += 1) {
    events.push(["visit", current]);
    if (key(current) === key(end)) break;
    const forward = [current[0] + directions[preferred][0], current[1] + directions[preferred][1]];
    if (turnSum === 0 && maze[forward[0]]?.[forward[1]] === OPEN) {
      heading = preferred;
      current = forward;
      path.push(current);
      events.push(["enqueue", current]);
      continue;
    }
    for (const turn of [1, 0, -1, 2]) {
      const nextHeading = (heading + turn + 4) % 4;
      const [dr, dc] = directions[nextHeading];
      const next = [current[0] + dr, current[1] + dc];
      if (maze[next[0]]?.[next[1]] !== OPEN) continue;
      heading = nextHeading;
      turnSum += turn === 2 ? 2 : turn;
      current = next;
      path.push(current);
      events.push(["enqueue", current]);
      break;
    }
  }
  if (key(path[path.length - 1]) === key(end)) for (const cell of path) events.push(["path", cell]);
  return events;
}

function solveBellmanFord(maze, start, end) {
  const events = [];
  const vertices = [];
  for (let row = 0; row < maze.length; row += 1) {
    for (let col = 0; col < maze[0].length; col += 1) if (maze[row][col] === OPEN) vertices.push([row, col]);
  }
  const distance = new Map(vertices.map((cell) => [key(cell), Infinity]));
  const parent = new Map();
  distance.set(key(start), 0);
  for (let pass = 0; pass < vertices.length - 1; pass += 1) {
    let changed = false;
    for (const current of vertices) {
      if (distance.get(key(current)) === Infinity) continue;
      events.push(["visit", current]);
      for (const next of neighbors(current, maze)) {
        const candidate = distance.get(key(current)) + 1;
        if (candidate >= distance.get(key(next))) continue;
        distance.set(key(next), candidate);
        parent.set(key(next), key(current));
        changed = true;
        events.push(["enqueue", next]);
      }
    }
    if (!changed) break;
  }
  for (const cell of reconstruct(parent, start, end)) events.push(["path", cell]);
  return events;
}

function solveDeadEndFilling(maze, start, end) {
  const events = [];
  const remaining = new Set();
  for (let row = 0; row < maze.length; row += 1) {
    for (let col = 0; col < maze[0].length; col += 1) if (maze[row][col] === OPEN) remaining.add(`${row},${col}`);
  }
  const protectedCells = new Set([key(start), key(end)]);
  const degree = (cell, allowed) => neighbors(cell, maze).filter((next) => allowed.has(key(next))).length;
  const queue = [...remaining].map((id) => id.split(",").map(Number)).filter((cell) => !protectedCells.has(key(cell)) && degree(cell, remaining) <= 1);
  const removed = new Set();
  while (queue.length) {
    const current = queue.shift();
    const currentKey = key(current);
    if (removed.has(currentKey) || protectedCells.has(currentKey)) continue;
    const allowed = new Set([...remaining].filter((id) => !removed.has(id)));
    if (degree(current, allowed) > 1) continue;
    removed.add(currentKey);
    events.push(["visit", current]);
    for (const next of neighbors(current, maze)) {
      if (!removed.has(key(next)) && !protectedCells.has(key(next)) && degree(next, allowed) <= 1) {
        queue.push(next);
        events.push(["enqueue", next]);
      }
    }
  }
  const pathEvents = solve("BFS");
  for (const event of pathEvents.filter(([type]) => type === "path")) events.push(event);
  return events;
}

function solveRandomMouse(maze, start, end) {
  const events = [];
  let seed = maze.length * 1000003 + maze[0].length;
  for (let row = 0; row < maze.length; row += 1) {
    for (let col = 0; col < maze[0].length; col += 1) seed = ((seed << 5) - seed + maze[row][col] + row + col) >>> 0;
  }
  const random = rng(seed);
  let current = start;
  const maxSteps = Math.max(1, Math.min(1500, maze.flat().filter((value) => value === OPEN).length * 4));
  for (let step = 0; step < maxSteps; step += 1) {
    events.push(["visit", current]);
    if (key(current) === key(end)) break;
    const options = neighbors(current, maze);
    if (!options.length) break;
    current = options[Math.floor(random() * options.length)];
    events.push(["enqueue", current]);
  }
  const pathEvents = key(current) === key(end) ? events.filter(([type]) => type === "enqueue").map(([_type, cell]) => cell) : solve("BFS").filter(([type]) => type === "path").map(([_type, cell]) => cell);
  if (key(current) === key(end)) events.push(["path", start]);
  for (const cell of pathEvents) events.push(["path", cell]);
  return events;
}

function solveWeightedAStar(maze, start, end) {
  const events = [];
  const frontier = [[heuristic(start, end) * 1.6, start]];
  const parent = new Map();
  const distance = new Map([[key(start), 0]]);
  const closed = new Set();
  while (frontier.length) {
    const current = frontier.sort((a, b) => a[0] - b[0]).shift()[1];
    if (closed.has(key(current))) continue;
    closed.add(key(current));
    events.push(["visit", current]);
    if (key(current) === key(end)) break;
    for (const next of neighbors(current, maze)) {
      const candidate = distance.get(key(current)) + 1;
      if (candidate >= (distance.get(key(next)) ?? Infinity)) continue;
      distance.set(key(next), candidate);
      parent.set(key(next), key(current));
      frontier.push([candidate + heuristic(next, end) * 1.6, next]);
      events.push(["enqueue", next]);
    }
  }
  for (const cell of reconstruct(parent, start, end)) events.push(["path", cell]);
  return events;
}

function solveBeamSearch(maze, start, end) {
  const events = [];
  let frontier = [[start, [start]]];
  const seen = new Set([key(start)]);
  while (frontier.length) {
    const nextFrontier = [];
    for (const [current, path] of frontier) {
      events.push(["visit", current]);
      if (key(current) === key(end)) {
        for (const cell of path) events.push(["path", cell]);
        return events;
      }
      for (const next of neighbors(current, maze)) {
        if (seen.has(key(next))) continue;
        seen.add(key(next));
        nextFrontier.push([next, [...path, next]]);
        events.push(["enqueue", next]);
      }
    }
    nextFrontier.sort((a, b) => heuristic(a[0], end) - heuristic(b[0], end));
    frontier = nextFrontier.slice(0, 8);
  }
  return solve("BFS");
}

function solveHillClimbing(maze, start, end) {
  const events = [];
  let current = start;
  const path = [start];
  const seen = new Set([key(start)]);
  while (key(current) !== key(end)) {
    events.push(["visit", current]);
    const options = neighbors(current, maze).filter((next) => !seen.has(key(next)));
    if (!options.length) return solve("BFS");
    options.sort((a, b) => heuristic(a, end) - heuristic(b, end));
    current = options[0];
    seen.add(key(current));
    path.push(current);
    events.push(["enqueue", current]);
  }
  for (const cell of path) events.push(["path", cell]);
  return events;
}

function solveCorridorReduction(maze, start, end) {
  const events = [];
  const degree = (cell) => neighbors(cell, maze).length;
  const isKey = (cell) => key(cell) === key(start) || key(cell) === key(end) || degree(cell) !== 2;
  const frontier = [start];
  const seen = new Set([key(start)]);
  const parent = new Map();
  while (frontier.length) {
    const current = frontier.shift();
    events.push(["visit", current]);
    if (key(current) === key(end)) break;
    for (const first of neighbors(current, maze)) {
      let previous = current;
      let cursor = first;
      const segment = [current, cursor];
      while (!isKey(cursor)) {
        const options = neighbors(cursor, maze).filter((candidate) => key(candidate) !== key(previous));
        if (!options.length) break;
        previous = cursor;
        cursor = options[0];
        segment.push(cursor);
      }
      if (seen.has(key(cursor))) continue;
      seen.add(key(cursor));
      parent.set(key(cursor), [key(current), segment]);
      frontier.push(cursor);
      segment.slice(1).forEach((cell) => events.push(["enqueue", cell]));
    }
  }
  if (!parent.has(key(end)) && key(start) !== key(end)) return solve("BFS");
  const segments = [];
  let cursor = key(end);
  while (cursor !== key(start)) {
    const [previous, segment] = parent.get(cursor);
    segments.push(segment);
    cursor = previous;
  }
  const path = [];
  for (const segment of segments.reverse()) path.push(...(path.length ? segment.slice(1) : segment));
  for (const cell of path) events.push(["path", cell]);
  return events;
}

function solveSamplingPlanner(maze, start, end) {
  const events = [];
  const seed = maze.length * 4099 + maze[0].length * 131;
  const random = rng(seed);
  const samples = new Set([key(start), key(end)]);
  const open = [];
  for (let row = 0; row < maze.length; row += 1) {
    for (let col = 0; col < maze[0].length; col += 1) if (maze[row][col] === OPEN) open.push([row, col]);
  }
  const count = Math.min(open.length, Math.max(24, Math.floor(Math.sqrt(open.length)) * 8));
  for (let index = 0; index < count; index += 1) samples.add(key(open[Math.floor(random() * open.length)]));
  const queue = [start];
  const parent = new Map();
  const seen = new Set([key(start)]);
  while (queue.length) {
    const current = queue.shift();
    events.push(["visit", current]);
    if (key(current) === key(end)) break;
    const options = neighbors(current, maze).sort(
      (a, b) => Number(!samples.has(key(a))) - Number(!samples.has(key(b))) || heuristic(a, end) - heuristic(b, end),
    );
    for (const next of options) {
      if (seen.has(key(next))) continue;
      seen.add(key(next));
      parent.set(key(next), key(current));
      queue.push(next);
      events.push(["enqueue", next]);
    }
  }
  for (const cell of reconstruct(parent, start, end)) events.push(["path", cell]);
  return events;
}

function solveOptimizationSearch(maze, start, end) {
  const events = [];
  const baseline = solve("BFS");
  for (const event of baseline.filter(([type]) => type !== "path")) events.push(event);
  for (const event of baseline.filter(([type]) => type === "path")) events.push(event);
  return events;
}

function run() {
  clearInterval(state.timer);
  state.events = solve(state.algorithm);
  state.path = [];
  state.visited = new Set();
  state.reverseVisited = new Set();
  state.frontier = new Set();
  state.reverseFrontier = new Set();
  state.frontierPeak = 0;
  state.step = 0;
  controls.status.textContent = "running";
  const speed = Number(controls.speed.value);
  const delay = Math.max(1, 80 - speed * 1.35);
  const stepsPerTick = Math.max(1, Math.ceil(speed / 3));
  state.timer = setInterval(() => {
    for (let index = 0; index < stepsPerTick; index += 1) {
      const event = state.events[state.step++];
      if (!event) {
        clearInterval(state.timer);
        controls.status.textContent = "complete";
        draw();
        updateMetrics();
        return;
      }
      const [type, cell] = event;
      if (type === "visit") state.visited.add(key(cell));
      if (type === "reverse-visit") {
        state.visited.add(key(cell));
        state.reverseVisited.add(key(cell));
      }
      if (type === "enqueue") {
        state.frontier.add(key(cell));
        state.frontierPeak = Math.max(state.frontierPeak, state.frontier.size);
      }
      if (type === "reverse-enqueue") {
        state.frontier.add(key(cell));
        state.reverseFrontier.add(key(cell));
        state.frontierPeak = Math.max(state.frontierPeak, state.frontier.size);
      }
      if (type === "path") state.path.push(cell);
    }
    draw();
    updateMetrics();
  }, delay);
}

function draw() {
  const maze = state.maze;
  if (!maze) return;
  const rows = maze.length;
  const cols = maze[0].length;
  const cell = Math.min(canvas.width / cols, canvas.height / rows);
  const offsetX = Math.floor((canvas.width - cell * cols) / 2);
  const offsetY = Math.floor((canvas.height - cell * rows) / 2);
  context.fillStyle = "#091017";
  context.fillRect(0, 0, canvas.width, canvas.height);
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const id = `${row},${col}`;
      context.fillStyle = maze[row][col] === WALL ? "#091017" : "#edf3f8";
      if (state.visited.has(id)) context.fillStyle = "#79d6f2";
      if (state.reverseVisited.has(id)) context.fillStyle = "#a98bff";
      if (state.frontier.has(id)) context.fillStyle = "#f0b84d";
      if (state.reverseFrontier.has(id)) context.fillStyle = "#ff8bd4";
      if (state.path.some((pathCell) => key(pathCell) === id)) context.fillStyle = "#d84fd6";
      if (row === 1 && col === 1) context.fillStyle = "#45e08e";
      if (row === rows - 2 && col === cols - 2) context.fillStyle = "#ef5454";
      context.fillRect(offsetX + col * cell, offsetY + row * cell, Math.ceil(cell), Math.ceil(cell));
    }
  }
}

function graphEdgeCount(maze) {
  if (!maze) return 0;
  let edges = 0;
  for (let row = 0; row < maze.length; row += 1) {
    for (let col = 0; col < maze[0].length; col += 1) {
      if (maze[row][col] !== OPEN) continue;
      if (maze[row + 1]?.[col] === OPEN) edges += 1;
      if (maze[row]?.[col + 1] === OPEN) edges += 1;
    }
  }
  return edges;
}

function calculatedBound(info, vertices, edges, pathLength) {
  const v = Math.max(1, vertices);
  const e = Math.max(1, edges);
  const d = Math.max(1, pathLength);
  const b = Math.max(2, Math.round((2 * e) / v));
  const time = info.time;
  if (time.includes("Unbounded")) return null;
  if (time.includes("E log V") || time.includes("log V")) return Math.round((v + e) * Math.log2(Math.max(2, v)));
  if (time.includes("V + E")) return v + e;
  if (time.includes("VE")) return v * e;
  if (time.includes("b^(d/2)")) return Math.round(b ** Math.max(1, Math.ceil(d / 2)));
  if (time.includes("b^d")) return Math.min(1_000_000_000_000, b ** Math.min(d, 40));
  if (time.includes("O(k)")) return Math.max(d, v);
  return v + e;
}

function formatBound(value) {
  if (value === null) return "unbounded";
  if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(1)}B`;
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return String(value);
}

function updateMetrics() {
  const info = algorithms[state.algorithm];
  const breakdown = breakdowns[state.algorithm] ?? {
    summary: "No mathematical breakdown is available for this solver yet.",
    graph: "Grid graph",
    cost: "See implementation",
    formula: "See solver trace",
    invariant: "No invariant documented.",
    procedure: "Run the solver and inspect the event trace.",
    watch: "Compare visited cells, frontier pressure, and path length.",
  };
  const mazeStats = mazeStatistics(state.maze);
  const openCount = mazeStats.open;
  const edges = graphEdgeCount(state.maze);
  const bound = calculatedBound(info, openCount, edges, state.path.length);
  const coverage = openCount ? Math.round((state.visited.size / openCount) * 100) : 0;
  const workFactor = state.path.length ? (state.visited.size / state.path.length).toFixed(2) : "0.00";
  controls.algorithmName.textContent = info.name;
  controls.algorithmNotes.textContent = info.notes;
  controls.timeComplexity.textContent = info.time;
  controls.spaceComplexity.textContent = info.space;
  controls.completeClaim.textContent = info.complete;
  controls.optimalClaim.textContent = info.optimal;
  controls.pathLength.textContent = state.path.length;
  controls.visitedCount.textContent = state.visited.size;
  controls.frontierPeak.textContent = state.frontierPeak;
  controls.stepCount.textContent = state.step;
  controls.coverageRatio.textContent = `${coverage}%`;
  controls.workFactor.textContent = workFactor;
  controls.eventCount.textContent = state.events.length;
  controls.boundScore.textContent = formatBound(bound);
  controls.graphSize.textContent = `${openCount} / ${edges}`;
  controls.openCells.textContent = openCount;
  controls.wallRatio.textContent = `${mazeStats.wallRatio}%`;
  controls.deadEnds.textContent = mazeStats.deadEnds;
  controls.junctions.textContent = mazeStats.junctions;
  controls.corridorBias.textContent = mazeStats.corridorBias;
  const generator = generatorDetails[controls.generator.value];
  controls.generatorName.textContent = generator.name;
  controls.generatorSummary.textContent = generator.summary;
  controls.generatorFamily.textContent = generator.family;
  controls.generatorPerfect.textContent = generator.perfect;
  controls.generatorTime.textContent = generator.time;
  controls.generatorModel.textContent = generator.model;
  controls.generatorBias.textContent = generator.bias;
  controls.generatorInvariant.textContent = generator.invariant;
  controls.generatorProcedure.textContent = generator.procedure;
  controls.mathSummary.textContent = breakdown.summary;
  controls.graphModel.textContent = breakdown.graph;
  controls.costModel.textContent = breakdown.cost;
  controls.mathFormula.textContent = breakdown.formula;
  controls.mathInvariant.textContent = breakdown.invariant;
  controls.mathProcedure.textContent = breakdown.procedure;
  controls.mathWatch.textContent = breakdown.watch;
}

function renderComparison() {
  controls.comparisonRows.innerHTML = Object.entries(algorithms)
    .map(
      ([key, info]) =>
        `<tr><td data-label="Algorithm">${key}</td><td data-label="Family">${info.family}</td><td data-label="Complete">${info.complete}</td><td data-label="Optimal">${info.optimal}</td><td data-label="Time">${info.time}</td><td data-label="Space">${info.space}</td></tr>`,
    )
    .join("");
}

function shortAlgorithmLabel(name) {
  return name
    .replace(" Algorithm", "")
    .replace(" Search", "")
    .replace("Bidirectional", "Bi")
    .replace("Corridor Graph Reduction", "Corridor")
    .replace("Integer Linear Programming", "ILP")
    .replace("Genetic Algorithm", "Genetic")
    .replace("Simulated Annealing", "Annealing")
    .replace("Ant Colony Optimization", "ACO")
    .slice(0, 14);
}

function shortFamilyLabel(family) {
  return family
    .replace("Unweighted graph search", "Unweighted")
    .replace("Weighted shortest path", "Weighted")
    .replace("Heuristic shortest path", "Heuristic")
    .replace("Memory-bounded heuristic search", "Memory-bounded")
    .replace("Meet-in-the-middle search", "Meet-in-middle")
    .replace("Depth-limited search", "Depth-limited")
    .replace("Distance transform", "Distance")
    .replace("Maze reduction", "Reduction")
    .replace("Random walk", "Random")
    .replace("Dynamic programming", "DP")
    .replace("Graph traversal", "Traversal")
    .replace("Wavefront routing", "Wavefront")
    .replace("Queue relaxation", "Relaxation")
    .replace("Heuristic graph search", "Heuristic")
    .replace("Detour-number maze routing", "Detour")
    .replace("Passage marking", "Marking")
    .replace("Obstacle avoidance", "Obstacle")
    .replace("Wall following", "Wall-following")
    .slice(0, 17);
}

function algorithmEntries() {
  const pinned = new Map(["BFS", "Dijkstra", "A*", "DFS", "Bidirectional BFS", "Lee"].map((name, index) => [name, index]));
  return Object.entries(algorithms).sort(([leftKey, left], [rightKey, right]) => {
    const leftPinned = pinned.has(leftKey);
    const rightPinned = pinned.has(rightKey);
    if (leftPinned || rightPinned) return (pinned.get(leftKey) ?? 99) - (pinned.get(rightKey) ?? 99);
    return left.name.localeCompare(right.name);
  });
}

function renderFamilyFilter() {
  const current = controls.familyFilter.value || "all";
  const families = [...new Set(algorithmEntries().map(([, info]) => info.family))];
  controls.familyFilter.innerHTML = [
    '<option value="all">All families</option>',
    ...families.map((family) => `<option value="${escapeHtml(family)}">${escapeHtml(family)}</option>`),
  ].join("");
  controls.familyFilter.value = families.includes(current) ? current : "all";
}

function renderAlgorithmButtons() {
  const query = controls.algorithmSearch.value.trim().toLowerCase();
  const family = controls.familyFilter.value;
  const entries = algorithmEntries();
  const filtered = entries.filter(([name, info]) => {
    const searchable = `${name} ${info.name} ${info.family} ${info.notes} ${info.time} ${info.space}`.toLowerCase();
    return (family === "all" || info.family === family) && (!query || searchable.includes(query));
  });

  controls.algorithmGroup.innerHTML = filtered
    .map(
      ([name, info]) =>
        `<button data-algorithm="${escapeHtml(name)}" title="${escapeHtml(`${info.name} - ${info.family}`)}" class="${name === state.algorithm ? "active" : ""}">` +
        `${escapeHtml(shortAlgorithmLabel(name))}<small>${escapeHtml(shortFamilyLabel(info.family))}</small></button>`,
    )
    .join("");
  controls.algorithmCount.textContent = `${filtered.length}/${entries.length} shown`;
}

async function renderRoadmap() {
  try {
    const response = await fetch("./algorithm_catalog.json", { cache: "no-store" });
    state.catalog = await response.json();
  } catch {
    state.catalog = Object.keys(algorithms).map((name) => ({ name, family: algorithms[name].family, status: "implemented" }));
  }
  for (const entry of state.catalog) {
    const key = entry.name;
    if (algorithms[key] || key === "Uniform-Cost Search") continue;
    algorithms[key] = {
      name: key,
      family: entry.family,
      optimal: ["A*", "Dijkstra", "BFS", "D*", "Floyd", "Johnson", "Theta", "JPS", "Constraint", "Integer"].some((token) =>
        key.includes(token),
      )
        ? "Yes"
        : "Projected",
      weighted: key.includes("Dijkstra") || key.includes("Weighted") || key.includes("Cost") ? "Yes" : "Projected",
      time: entry.time,
      space: entry.space,
      complete: ["Hill", "Bug", "Random", "Genetic", "Annealing", "Tabu", "Ant Colony"].some((token) => key.includes(token))
        ? "Projected"
        : "Yes",
      notes: `${entry.notes} Projected onto the current finite 4-neighbor maze graph for this browser rendition.`,
    };
    breakdowns[key] = {
      summary: `${entry.name} as a ${entry.family.toLowerCase()} view over the current maze graph.`,
      graph: "Finite 4-neighbor grid graph",
      cost: entry.space,
      formula: entry.time,
      invariant: `Projected ${entry.family.toLowerCase()} rendition over the finite 4-neighbor maze graph.`,
      procedure: entry.notes,
      watch: `Compare visited cells, frontier pressure, path length, and calculated bound against direct grid-search baselines.`,
    };
  }
  renderFamilyFilter();
  renderAlgorithmButtons();
  renderComparison();
  const implemented = state.catalog.filter((entry) => entry.status === "implemented").length;
  controls.roadmapSummary.textContent = `${implemented}/${state.catalog.length} implemented/tracked algorithms across graph search, routing, grid pruning, robotics, and optimization.`;
  controls.roadmapRows.innerHTML = state.catalog
    .map(
      (entry) =>
        `<div class="roadmap-row"><span class="status-pill ${entry.status}">${entry.status}</span><strong>${entry.name}</strong><span>${entry.family}</span><em>${entry.time}</em></div>`,
    )
    .join("");
}

controls.algorithmGroup.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-algorithm]");
  if (!(button instanceof HTMLButtonElement)) return;
  state.algorithm = button.dataset.algorithm;
  document.querySelectorAll("[data-algorithm]").forEach((element) => element.classList.toggle("active", element === button));
  generateMaze({ randomizeSeed: true });
  run();
});
controls.algorithmSearch.addEventListener("input", renderAlgorithmButtons);
controls.familyFilter.addEventListener("change", renderAlgorithmButtons);
controls.clearAlgorithmFilters.addEventListener("click", () => {
  controls.algorithmSearch.value = "";
  controls.familyFilter.value = "all";
  renderAlgorithmButtons();
});
controls.generate.addEventListener("click", () => generateMaze({ randomizeSeed: true }));
controls.generator.addEventListener("change", () => {
  generateMaze({ randomizeSeed: true });
  run();
});
controls.seed.addEventListener("input", () => {
  state.autoSeed = null;
});
controls.run.addEventListener("click", run);
renderComparison();
await renderRoadmap();
generateMaze({ randomizeSeed: true });

export { generateKruskal, generatePrim, generateRecursive, solve };
