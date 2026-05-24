# Algorithm Catalog

Maze Solver models a maze as a rectangular grid graph. Open cells are vertices, passable north/south/east/west moves are edges, and the default edge cost is one. That keeps the visualizer approachable while still exposing standard graph-search and maze-generation ideas.

## Solvers

| Algorithm | Family | Complete | Optimal | Weighted | Time | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Breadth-First Search | Unweighted graph search | Yes | Yes | No | `O(V + E)` | Expands by distance layers and finds the shortest path by edge count. |
| Depth-First Search | Graph traversal | Yes | No | No | `O(V + E)` | Dives down corridors first and is useful for contrast against shortest-path methods. |
| A* Search | Heuristic shortest path | Yes | Yes | Yes | `O(E log V)` with a heap | Uses `f(n) = g(n) + h(n)` and Manhattan distance, which is admissible on this 4-neighbor grid. |
| Dijkstra's Algorithm | Weighted shortest path | Yes | Yes | Yes | `O((V + E) log V)` | Expands the cheapest settled frontier and supports non-negative edge weights. |
| Uniform-Cost Search | Weighted shortest path | Yes | Yes | Yes | `O((V + E) log V)` | The search-problem framing of Dijkstra's algorithm. |
| Bidirectional BFS | Meet-in-the-middle search | Yes | Yes | No | `O(b^(d/2))` idealized | Runs breadth-first waves from both endpoints until the waves meet. |
| Greedy Best-First Search | Heuristic graph search | Yes | No | No | `O(E log V)` | Uses only the heuristic priority, so it is fast-looking but not shortest-path guaranteed. |
| Iterative Deepening DFS | Depth-limited search | Yes | Yes | No | `O(b^d)` | Repeats DFS with increasing depth limits for low memory use. |
| Bellman-Ford | Dynamic programming shortest path | Yes | Yes | Yes | `O(VE)` | Repeated edge relaxation makes the cost propagation model visible. |
| Dead-End Filling | Maze reduction | Yes | No | No | `O(V + E)` | Removes cul-de-sacs and then traces through the reduced corridor graph. |

## Generators

| Algorithm | Family | Perfect Maze | Texture |
| --- | --- | --- | --- |
| Recursive Backtracker | Depth-first spanning tree | Yes | Long corridors and dramatic backtracking. |
| Randomized Prim | Frontier spanning tree | Yes | Dense, bushy branch structure. |
| Randomized Kruskal | Disjoint-set spanning tree | Yes | Evenly shuffled carved walls. |
| Wilson's Algorithm | Uniform spanning tree | Yes | Mathematically uniform spanning-tree sampling through loop-erased walks. |
| Aldous-Broder | Uniform spanning tree | Yes | Uniform sampling through a simple random walk. |
| Hunt and Kill | Depth-first scan hybrid | Yes | Walks until stuck, then hunts for a fresh frontier. |
| Binary Tree | Directional biased generation | Yes | Fast diagonal bias, useful as a baseline. |
| Sidewinder | Row-run generation | Yes | Row-wise runs with northern connections. |
| Growing Tree | Configurable frontier growth | Yes | A tunable blend of newest-cell and random frontier behavior. |
| Eller's Algorithm | Row-wise set merging | Yes | Builds one row at a time while preserving set connectivity. |
| Recursive Division | Wall subdivision | No | Starts open and recursively adds walls with single passages. |

## References

- E. W. Dijkstra, "A note on two problems in connexion with graphs", Numerische Mathematik, 1959.
- P. E. Hart, N. J. Nilsson, and B. Raphael, "A Formal Basis for the Heuristic Determination of Minimum Cost Paths", IEEE Transactions on Systems Science and Cybernetics, 1968.
- R. E. Bellman, "On a routing problem", Quarterly of Applied Mathematics, 1958.
- R. E. Korf, "Depth-first iterative-deepening: An optimal admissible tree search", Artificial Intelligence, 1985.
- D. B. Wilson, "Generating random spanning trees more quickly than the cover time", STOC, 1996.
- D. Aldous and A. Broder, random-walk uniform spanning tree algorithms.
