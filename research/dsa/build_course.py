"""Reproducible original exercises and schedules; never rewrites the original research."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-10-31"


def write(name, **collections):
    data = {"$schema": "DSA_PACKAGE_SCHEMA.json", "dataset_type": "dsa",
            "research_version": "1.0.0", "research_date": DATE, **collections}
    (ROOT / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


MODULES = [
    ("foundations", "Algorithmic foundations",
     "Big O, Big Theta, Big Omega, best/average/worst case, amortized analysis, recursion, iteration, divide and conquer",
     "Count work before timing it. An asymptotic upper bound is not an exact runtime; identify the input variable and case. Geometric capacity growth makes append amortized constant despite occasional linear copies. A recursive implementation also consumes stack space.",
     "For each loop, state the number of iterations as a function of input size; separate allocated storage from returned output.",
     "Compare direct counting with algebraic summation; derive the recurrence rather than guessing from syntax."),
    ("arrays", "Arrays and strings",
     "arrays, strings, hash maps, hash sets, frequency counting, prefix sums, difference arrays, subarrays, matrix traversal",
     "Hashing replaces repeated searches with expected constant-time lookup, at a memory cost. Prefix sums turn a range sum into a difference of cumulative sums. Difference arrays batch range updates before one reconstruction pass. JavaScript strings require an explicit Unicode policy.",
     "At position i, the map or prefix table describes exactly the processed prefix.",
     "Compare scanning each query with preprocessing; distinguish expected hash behavior from worst-case guarantees."),
    ("patterns", "Problem-solving patterns",
     "two pointers, sliding window, fast/slow pointers, prefix/suffix, hashing, binary search on answers, in-place manipulation, sorting",
     "A sliding window is justified by an invariant that can be repaired while its left edge moves monotonically. Negative numbers invalidate many sum-threshold window arguments. Binary search on answers requires a monotone feasibility predicate, not merely sorted-looking data.",
     "Each item enters and leaves the maintained state at most once; explain why moving a pointer cannot discard a valid better answer.",
     "Use brute force as an oracle on small cases, then prove the optimized window or search predicate."),
    ("linked", "Linked lists and caches",
     "singly/doubly linked lists, reversal, cycle detection, merging, fast/slow pointers, LRU cache",
     "Pointer changes must preserve access to the unprocessed suffix. Floyd's two speeds detect a cycle without storing every node. A hash map plus doubly linked list supports lookup and recency changes without scanning; distinguish node identity from equal values.",
     "The processed prefix is valid and the unprocessed suffix remains reachable.",
     "Compare auxiliary arrays with pointer rewiring; a bounded cache must state eviction and recency semantics."),
    ("stacks", "Stacks, queues and monotonic structures",
     "stacks, queues, deques, monotonic stacks/queues, expression evaluation, parentheses, parsing",
     "Stacks model unfinished nested work; queues model arrival order. A monotonic stack discards candidates dominated by a later item. Its nested loop is amortized linear because every index is pushed and popped at most once. Avoid Array.shift in a hot queue.",
     "Stack entries are unresolved candidates in a stated monotone order.",
     "Compare scanning forward from each item with retaining only candidates that can still affect the answer."),
    ("sorting", "Searching and sorting",
     "linear/binary search, lower/upper bounds, merge/quick/heap/counting sort, stability, sorting trade-offs",
     "Binary search is a boundary search over a half-open interval. Merge sort gives predictable comparison complexity and uses extra storage; quicksort needs pivot and worst-case analysis; counting sort depends on key range, not just item count. JavaScript numeric sort needs a comparator.",
     "All positions before low are known false and all positions at or after high are known true for the boundary predicate.",
     "Compare linear search with sorted search including preprocessing; explain stable ordering and worst-case behavior."),
    ("trees", "Trees and ordered indexes",
     "binary trees, BSTs, preorder/inorder/postorder/level order, DFS/BFS, height/depth, LCA, balanced trees, serialization",
     "A tree traversal combines results from children according to a contract. BST validity is a global bound, not just a parent-child comparison. DFS storage depends on height, BFS on maximum width. Balancing preserves logarithmic height; serialization must preserve null children.",
     "Each recursive call receives valid bounds or returns a well-defined subtree summary.",
     "Compare recursive DFS, an explicit stack and level-order traversal; include a skewed-tree test."),
    ("heaps", "Heaps and priority queues",
     "min/max heaps, heapify, priority queues, Top K, K-way merge, streaming",
     "A heap exposes an extreme item without fully sorting all items. A size-k min-heap keeps the k largest seen values. Bottom-up heap construction is linear, not n log n. A k-way merge keeps one frontier item per sorted source.",
     "The retained heap represents the best k items of the processed prefix, or one frontier from each source.",
     "Compare full sorting with a bounded heap; account for output sorting separately."),
    ("intervals", "Intervals and sweep lines",
     "merging, overlap, meeting rooms, scheduling, sweep line, event sorting",
     "State whether intervals are closed or half-open before coding. Sorting by start allows one active merged interval; resource counts use arrival/departure events. At equal timestamps, a departure precedes an arrival for half-open intervals.",
     "Completed merged intervals cannot overlap the active interval; active event count equals simultaneous demand.",
     "Compare pairwise overlap tests with sorting and a sweep; test touching boundaries explicitly."),
    ("graphs", "Graphs and connectivity",
     "adjacency lists/matrices, DFS/BFS, cycles, components, topological sort, Dijkstra, Bellman-Ford, MST, union-find, shortest paths",
     "BFS finds shortest paths only with equal edge costs. Dijkstra relies on nonnegative weights; Bellman-Ford detects reachable negative cycles. Topological ordering exists only for a DAG. Union-find tracks undirected connectivity, not directed reachability.",
     "A BFS vertex is enqueued once; a topological frontier contains only vertices with zero remaining indegree.",
     "Compare adjacency list and matrix costs; choose shortest-path algorithms from edge constraints, not habit."),
    ("backtracking", "Backtracking and constraint search",
     "recursion trees, subsets, permutations, combinations, constraint satisfaction, pruning, N-Queens",
     "Backtracking makes a choice, explores the remaining choices and restores state. A start index prevents duplicate combinations; permutations require a different used-item contract. Pruning is safe only when a branch cannot contain a valid answer.",
     "The current path is valid, and undo restores exactly the state before the choice.",
     "Compare exhaustive enumeration with constraint-driven pruning; output size can dominate algorithm runtime."),
    ("dp", "Dynamic programming",
     "memoization, tabulation, states, recurrences, 1D/2D DP, knapsack, grids, LCS, LIS, tree DP",
     "Define what each state means before selecting a recurrence. Memoization shares repeated subproblems; tabulation follows dependency order. Loop direction distinguishes reusable coins from 0/1 choices. For LCS and grid DP, specify both dimensions and boundary states.",
     "Every computed state depends only on already valid states and represents a complete optimum for its stated subproblem.",
     "Write an exponential oracle on tiny inputs, derive the recurrence, then optimize storage only after correctness."),
    ("greedy", "Greedy algorithms and proofs",
     "greedy choice, interval/activity selection, priority optimization, correctness proofs, greedy versus DP",
     "A locally attractive choice needs an exchange or dominance proof. Earliest finishing activities leave maximum remaining room; highest weight is not a valid replacement for weighted interval scheduling, which requires a different formulation.",
     "A chosen prefix can be extended to an optimal solution without reducing the remaining feasible choices.",
     "Construct a counterexample to tempting heuristics before relying on one; compare with a DP oracle."),
    ("advanced", "Advanced data structures and algorithms",
     "tries, bits, bitmasks, DSU, advanced graphs, combinatorics, segment trees, Fenwick trees",
     "A trie shares prefixes while a Fenwick tree stores partial sums over bit-defined ranges. Bitwise JavaScript operators use signed 32-bit integers; arbitrary precision needs BigInt. Segment trees support more general aggregates at increased implementation complexity.",
     "Each indexed aggregate covers a precisely defined range; trie counts represent inserted words, not traversals.",
     "Choose advanced structures only when query/update constraints justify them; derive low-bit transitions."),
    ("senior", "Senior engineering coding interviews",
     "OO design, interfaces, patterns, concurrency, thread safety, races, practical coding, refactoring, testing, debugging, APIs, data modeling",
     "Practical assessments evaluate evolving contracts, tests and maintainability, not just optimal puzzle complexity. State idempotency, error and ownership boundaries. JavaScript async I/O is not CPU parallelism; limit active work explicitly and discuss shared-state races.",
     "Every output obeys the contract even on duplicates, malformed input or partial failure; bounded workers preserve input order.",
     "Compare a minimal pure function with an extensible design. Refactor only after observable behavior is protected by tests."),
]

# Statements, implementations and fixtures below are original Academy exercises.
# They are not copied platform problems or alleged company questions.
EXERCISES = [
    ("foundations", "Count triangular work", "easy",
     "Given an integer n, return the number of visits performed by loops i=0..n-1 and j=0..i. Do not execute the loops in your final implementation.",
     "0 <= n <= 1000000; return an exact Number integer.",
     "function solve(n) { return n * (n + 1) / 2; }",
     [(0, 0), (4, 10), (10, 55)], "O(1)", "O(1)", "Summation", "Sum row lengths 1 through n.",
     "Loop counting is O(n^2); algebraic summation is constant-time under this bounded-number model."),
    ("foundations", "Growth-copy accounting", "medium",
     "A dynamic buffer starts at capacity 1 with length 0. Before each append to a full buffer, double capacity and copy its current contents. Given n appends, return total copied items, excluding the new appends.",
     "0 <= n <= 1000000; growth happens only when an append would exceed capacity.",
     "function solve(n) { let capacity = 1, copied = 0; while (capacity < n) { copied += capacity; capacity *= 2; } return copied; }",
     [(0, 0), (1, 0), (5, 7), (8, 7)], "O(log n)", "O(1)", "Amortized analysis", "Account for a geometric series of capacity copies.",
     "Simulating all appends is O(n); summing growth events is O(log n). Total copying is less than 2n."),
    ("arrays", "Telemetry frequency table", "easy",
     "Given an array of lowercase event names, return [name,count] pairs sorted lexicographically by name. Treat repeated names as the same event type.",
     "0 <= events.length <= 100000; names contain only lowercase ASCII letters.",
     "function solve(events) { const counts = new Map(); for (const name of events) counts.set(name, (counts.get(name) || 0) + 1); return [...counts].sort((a,b) => a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0); }",
     [([], []), (["login", "reset", "login"], [["login", 2], ["reset", 1]]), (["b", "a"], [["a", 1], ["b", 1]])],
     "O(n + u log u)", "O(u)", "Frequency counting", "Count with a map and sort only distinct names.",
     "Repeated full-array scans are quadratic; hashing is expected linear before sorting u unique keys."),
    ("arrays", "Batched range totals", "medium",
     "Input is {values,queries}. Each query [left,right] uses inclusive zero-based bounds. Return each range sum in query order.",
     "0 <= values.length <= 100000; queries are valid nonempty ranges; integer sums remain safe integers.",
     "function solve({values,queries}) { const prefix=[0]; for (const value of values) prefix.push(prefix[prefix.length-1]+value); return queries.map(([l,r]) => prefix[r+1]-prefix[l]); }",
     [({"values": [], "queries": []}, []), ({"values": [2,-1,4], "queries": [[0,2],[1,1]]}, [5,-1])],
     "O(n + q)", "O(n)", "Prefix sums", "Store a leading-zero prefix and subtract at the two boundaries.",
     "Scanning each range costs O(nq); preprocessing makes each valid query constant-time."),
    ("patterns", "Unique-event window", "medium",
     "Given an array of event names, return the length of the longest contiguous block containing no repeated name.",
     "0 <= events.length <= 100000; event identity is exact string equality.",
     "function solve(events) { const seen=new Map(); let left=0,best=0; for(let right=0;right<events.length;right++){ if(seen.has(events[right])) left=Math.max(left,seen.get(events[right])+1); seen.set(events[right],right); best=Math.max(best,right-left+1); } return best; }",
     [([], 0), (["a","b","a","c"], 3), (["a","a"], 1)], "O(n) expected", "O(u)",
     "Sliding window", "Advance the left boundary past the last occurrence, never backwards.",
     "Enumerating and checking every interval is superlinear; each boundary advances monotonically."),
    ("patterns", "Signed target windows", "hard",
     "Input is {values,target}. Return the number of nonempty contiguous subarrays whose sum equals target; values may be negative.",
     "0 <= values.length <= 100000; values and counts remain safe integers.",
     "function solve({values,target}) { const counts=new Map([[0,1]]); let prefix=0,result=0; for(const value of values){ prefix+=value; result+=counts.get(prefix-target)||0; counts.set(prefix,(counts.get(prefix)||0)+1); } return result; }",
     [({"values": [], "target": 0}, 0), ({"values": [1,-1,1], "target": 1}, 3), ({"values": [0,0], "target": 0}, 3)],
     "O(n) expected", "O(n)", "Prefix hashing", "Count earlier prefixes equal to current prefix minus target.",
     "A threshold sliding window is invalid with negative values; use prefix counts rather than enumerating all O(n^2) windows."),
    ("linked", "Reverse a node chain", "easy",
     "Input is the head of an acyclic singly linked list represented by nested {value,next} objects, or null. Return its reversed head by changing next links.",
     "At most 10000 nodes; final next is null; values may repeat.",
     "function solve(head) { let previous=null,current=head; while(current!==null){ const next=current.next; current.next=previous; previous=current; current=next; } return previous; }",
     [(None, None), ({"value":1,"next":{"value":2,"next":None}}, {"value":2,"next":{"value":1,"next":None}})],
     "O(n)", "O(1) auxiliary", "Pointer reversal", "Save the next pointer before rewiring.",
     "An array copy uses O(n) auxiliary space; iterative pointer reversal uses a constant number of references."),
    ("linked", "Bounded recency cache", "hard",
     "Input is {capacity,operations}, where operations are ['put',key,value] or ['get',key]. Return an array containing each get result or null for a miss. A get or overwrite makes the key most recent; evict least recent on overflow.",
     "1 <= capacity <= 1000; keys are strings; up to 10000 operations; stored values are integers.",
     "function solve({capacity,operations}) { const cache=new Map(),out=[]; for(const [action,key,value] of operations){ if(action==='get'){ if(!cache.has(key)){out.push(null);continue;} const saved=cache.get(key); cache.delete(key);cache.set(key,saved);out.push(saved); } else {cache.delete(key);cache.set(key,value); if(cache.size>capacity) cache.delete(cache.keys().next().value);} } return out; }",
     [({"capacity":1,"operations":[["put","a",2],["get","a"],["put","b",3],["get","a"]]}, [2,None]),
      ({"capacity":2,"operations":[["get","x"],["put","x",1],["put","x",4],["get","x"]]}, [None,4])],
     "O(m) expected with insertion-ordered Map", "O(c) auxiliary",
     "LRU cache", "Refresh insertion order on both get and overwrite; then remove the first key on overflow.",
     "The JavaScript reference uses Map order. Implement a hash map plus doubly linked nodes as the independent language-neutral variation; never claim Map provides a portable linked-list API."),
    ("stacks", "Validate nested brackets", "easy",
     "Given a string consisting only of ()[]{}, return whether all brackets are correctly nested and matched.",
     "Length <= 100000; the empty string is valid.",
     "function solve(value) { const stack=[],pairs={')':'(',']':'[','}':'{'}; for(const char of value){ if('([{'.includes(char)) stack.push(char); else if(stack.pop()!==pairs[char]) return false; } return stack.length===0; }",
     [("", True), ("([]{})", True), ("([)]", False)], "O(n)", "O(n)", "Nested stack",
     "Keep the opening brackets that have not yet been closed.",
     "Counting characters alone cannot validate nesting; the stack models unresolved structure."),
    ("stacks", "Next higher measurement", "medium",
     "Given integer measurements, return for each position the distance to the next strictly greater measurement, or 0 if none exists.",
     "Length <= 100000; equal values are not greater.",
     "function solve(values) { const out=Array(values.length).fill(0),stack=[]; for(let i=0;i<values.length;i++){ while(stack.length && values[i]>values[stack[stack.length-1]]){const old=stack.pop();out[old]=i-old;} stack.push(i); } return out; }",
     [([], []), ([4,4,6,3], [2,1,0,0]), ([3,2,1], [0,0,0])],
     "O(n) amortized", "O(n)", "Monotonic stack", "Retain unresolved indices in nonincreasing value order.",
     "Searching forward from every index is quadratic; each index is pushed and popped at most once."),
    ("sorting", "Find the first permitted position", "easy",
     "Input is {values,target} with ascending integers. Return the first index whose value is at least target, or values.length if no such index exists.",
     "Length <= 100000; duplicates are allowed.",
     "function solve({values,target}) { let low=0,high=values.length; while(low<high){const mid=low+Math.floor((high-low)/2);if(values[mid]<target) low=mid+1;else high=mid;} return low; }",
     [({"values":[],"target":1},0), ({"values":[1,2,2,5],"target":2},1), ({"values":[1,2],"target":8},2)],
     "O(log n)", "O(1)", "Lower bound", "Maintain a half-open search interval and never discard a possible earlier boundary.",
     "Linear scanning is O(n); the sorted predicate permits binary boundary search."),
    ("sorting", "Stable merge ordering", "medium",
     "Given records {key,id}, return them sorted by ascending numeric key while preserving input order among equal keys. Implement merge sort rather than calling built-in sort.",
     "At most 10000 records; ids are distinct strings.",
     "function solve(items) { if(items.length<2)return items.slice(); const mid=Math.floor(items.length/2),a=solve(items.slice(0,mid)),b=solve(items.slice(mid)),out=[];let i=0,j=0;while(i<a.length&&j<b.length)out.push(a[i].key<=b[j].key?a[i++]:b[j++]);return out.concat(a.slice(i),b.slice(j)); }",
     [([],[]), ([{"key":2,"id":"a"},{"key":1,"id":"b"},{"key":2,"id":"c"}],[{"key":1,"id":"b"},{"key":2,"id":"a"},{"key":2,"id":"c"}])],
     "O(n log n)", "O(n) peak auxiliary plus O(log n) stack", "Divide and conquer",
     "When keys tie, take from the left half first.",
     "Insertion sorting can be quadratic; balanced merge recursion gives predictable comparison growth."),
    ("trees", "Depth of a diagnostics tree", "easy",
     "Input is a binary tree {value,left,right} with null missing children. Return the maximum number of nodes on a root-to-leaf path; an empty tree has depth 0.",
     "At most 1000 nodes; height at most 500 in this browser exercise.",
     "function solve(node) { return node===null?0:1+Math.max(solve(node.left),solve(node.right)); }",
     [(None,0), ({"value":1,"left":{"value":2,"left":None,"right":None},"right":None},2)],
     "O(n)", "O(h)", "Tree DFS", "Compute child depths before combining their maximum.",
     "Repeated subtree traversals waste work; one postorder traversal returns the needed summary."),
    ("trees", "Validate global search bounds", "medium",
     "Given a binary tree {value,left,right}, return whether it is a strict binary search tree. All left descendants must be smaller and all right descendants greater; duplicates are invalid.",
     "At most 1000 nodes; finite safe integers.",
     "function solve(root) { function valid(node,low,high){return node===null || (node.value>low && node.value<high && valid(node.left,low,node.value)&&valid(node.right,node.value,high));}return valid(root,-Infinity,Infinity); }",
     [(None,True), ({"value":5,"left":{"value":3,"left":None,"right":None},"right":None},True),
      ({"value":5,"left":None,"right":{"value":7,"left":{"value":4,"left":None,"right":None},"right":None}},False)],
     "O(n)", "O(h)", "Propagated bounds", "Pass ancestor constraints, not merely the immediate parent.",
     "Checking only parent-child pairs misses violations several levels deep."),
    ("heaps", "Retain the largest k readings", "medium",
     "Input is {values,k}. Return the k largest values including duplicates, in ascending order. Use a bounded min-heap rather than sorting every reading.",
     "0 <= k <= values.length <= 100000.",
     "function solve({values,k}) { if(k===0)return [];const heap=[];function push(v){heap.push(v);let i=heap.length-1;while(i>0){let p=Math.floor((i-1)/2);if(heap[p]<=heap[i])break;[heap[p],heap[i]]=[heap[i],heap[p]];i=p;}}function down(){let i=0;while(2*i+1<heap.length){let j=2*i+1;if(j+1<heap.length&&heap[j+1]<heap[j])j++;if(heap[i]<=heap[j])break;[heap[i],heap[j]]=[heap[j],heap[i]];i=j;}}for(const v of values){if(heap.length<k)push(v);else if(v>heap[0]){heap[0]=v;down();}}return heap.sort((a,b)=>a-b); }",
     [({"values":[],"k":0},[]), ({"values":[3,1,5,5,2],"k":3},[3,5,5])],
     "O(n log(k+1) + k log k)", "O(k)", "Bounded heap",
     "The smallest retained value is the replacement boundary.",
     "Sorting every input costs O(n log n); a bounded heap helps when k is much smaller than n."),
    ("heaps", "Merge sorted event streams", "hard",
     "Given an array of ascending numeric arrays, return one ascending array containing every value. Preserve duplicates. Use one frontier item per nonempty source in a min-heap.",
     "At most 100 streams and 100000 total values.",
     "function solve(streams) { const heap=[],out=[];function push(x){heap.push(x);let i=heap.length-1;while(i>0){const p=(i-1)>>1;if(heap[p][0]<=heap[i][0])break;[heap[p],heap[i]]=[heap[i],heap[p]];i=p;}}function pop(){const first=heap[0],last=heap.pop();if(heap.length){heap[0]=last;let i=0;while(2*i+1<heap.length){let j=2*i+1;if(j+1<heap.length&&heap[j+1][0]<heap[j][0])j++;if(heap[i][0]<=heap[j][0])break;[heap[i],heap[j]]=[heap[j],heap[i]];i=j;}}return first;}streams.forEach((s,i)=>{if(s.length)push([s[0],i,0]);});while(heap.length){const [v,s,p]=pop();out.push(v);if(p+1<streams[s].length)push([streams[s][p+1],s,p+1]);}return out; }",
     [([],[]), ([[1,4],[],[1,3]],[1,1,3,4])],
     "O(N log(k+1))", "O(k) auxiliary excluding output", "K-way merge",
     "After removing one frontier item, advance only its source.",
     "Flatten-and-sort ignores that each source is already ordered."),
    ("intervals", "Merge occupied spans", "medium",
     "Given closed intervals [start,end], return their union as sorted disjoint intervals. Touching endpoints merge.",
     "At most 10000 intervals; start <= end; integer endpoints.",
     "function solve(intervals) { const sorted=intervals.map(x=>x.slice()).sort((a,b)=>a[0]-b[0]),out=[];for(const [a,b] of sorted){const last=out[out.length-1];if(last && a<=last[1])last[1]=Math.max(last[1],b);else out.push([a,b]);}return out; }",
     [([],[]), ([[3,5],[1,3],[9,10]],[[1,5],[9,10]])],
     "O(n log n)", "O(n)", "Sorted sweep", "Compare the next start with the active interval's maximum end.",
     "Repeated pairwise merging can be quadratic and order-sensitive."),
    ("intervals", "Provision meeting capacity", "medium",
     "Given half-open meetings [start,end), return the minimum number of rooms. A meeting ending at t releases its room before another starting at t.",
     "At most 10000 intervals; start < end.",
     "function solve(meetings) { const events=[];for(const [a,b] of meetings)events.push([a,1],[b,-1]);events.sort((a,b)=>a[0]-b[0]||a[1]-b[1]);let active=0,best=0;for(const [,delta]of events){active+=delta;best=Math.max(best,active);}return best; }",
     [([],0), ([[0,2],[2,3]],1), ([[0,5],[1,4],[2,3]],3)],
     "O(n log n)", "O(n)", "Event sweep", "Sort departures before arrivals at an equal timestamp.",
     "Pairwise overlap counts do not directly yield maximum simultaneous demand."),
    ("graphs", "Unweighted service hops", "medium",
     "Input is {adjacency,start}, with adjacency an array of outgoing neighbor arrays. Return each vertex's shortest hop count from start, or -1 if unreachable.",
     "1 <= vertices <= 10000; start and all neighbors are valid indices; edges may be directed.",
     "function solve({adjacency,start}) { const distances=Array(adjacency.length).fill(-1),queue=[start];distances[start]=0;for(let head=0;head<queue.length;head++){const node=queue[head];for(const next of adjacency[node])if(distances[next]===-1){distances[next]=distances[node]+1;queue.push(next);}}return distances; }",
     [({"adjacency":[[]],"start":0},[0]), ({"adjacency":[[1],[2],[],[]],"start":0},[0,1,2,-1])],
     "O(V + E)", "O(V)", "BFS", "Assign distance when enqueuing, not after removing.",
     "DFS discovery order is not a shortest-path guarantee; weighted edges require another algorithm."),
    ("graphs", "Dependency release ordering", "hard",
     "Input is an adjacency list of directed dependencies: an edge u->v means u must finish before v. Return the deterministic FIFO Kahn order, initially enqueueing zero-indegree vertices in ascending index order; return null if cyclic.",
     "At most 10000 vertices; no duplicate edges; neighbors preserve input order.",
     "function solve(adjacency) { const degree=Array(adjacency.length).fill(0),queue=[];for(const nexts of adjacency)for(const next of nexts)degree[next]++;degree.forEach((d,i)=>{if(!d)queue.push(i);});for(let head=0;head<queue.length;head++)for(const next of adjacency[queue[head]])if(--degree[next]===0)queue.push(next);return queue.length===adjacency.length?queue:null; }",
     [([],[]), ([[1],[2],[]],[0,1,2]), ([[1],[0]],None)],
     "O(V + E)", "O(V)", "Topological sorting", "Remove remaining indegrees as completed vertices release successors.",
     "Sorting by numeric ID alone does not satisfy dependency edges; leftover vertices prove a cycle exists."),
    ("backtracking", "Enumerate feature subsets", "medium",
     "Given distinct feature names, return every subset. Use include/exclude recursion, explore exclusion first, and preserve original order within a subset.",
     "At most 12 names; return subsets in the specified recursion order.",
     "function solve(names) { const out=[],path=[];function visit(i){if(i===names.length){out.push(path.slice());return;}visit(i+1);path.push(names[i]);visit(i+1);path.pop();}visit(0);return out; }",
     [([], [[]]), (["a","b"],[[],["b"],["a"],["a","b"]])],
     "O(n 2^n) including output copies", "O(n) auxiliary excluding output",
     "Include/exclude", "Restore the path after exploring the included branch.",
     "There are exponentially many requested outputs; no linear-time complete enumeration exists."),
    ("backtracking", "Reusable allocation combinations", "hard",
     "Input is {sizes,target}, where sizes are distinct positive integers. Return nondecreasing combinations summing to target, lexicographically by sorted choice exploration. A size may be reused. The target-zero result is [[]].",
     "At most 8 sizes; 0 <= target <= 30; positive sizes prevent nonterminating recursion.",
     "function solve({sizes,target}) { const values=sizes.slice().sort((a,b)=>a-b),out=[],path=[];function visit(start,left){if(left===0){out.push(path.slice());return;}for(let i=start;i<values.length&&values[i]<=left;i++){path.push(values[i]);visit(i,left-values[i]);path.pop();}}visit(0,target);return out; }",
     [({"sizes":[2,3],"target":7},[[2,2,3]]), ({"sizes":[2],"target":1},[]), ({"sizes":[2],"target":0},[[]])],
     "Output-sensitive exponential search; depth <= target/min(sizes)", "O(target/min(sizes)) auxiliary",
     "Constraint backtracking", "A start index prevents permutation duplicates; keep it unchanged to reuse a chosen size.",
     "Generating arbitrary permutations wastes work; sorting permits safe remaining-target pruning."),
    ("dp", "Minimum provisioning bundles", "medium",
     "Input is {sizes,target}. Return the minimum count of reusable positive bundle sizes that sums exactly to target, or -1 if impossible.",
     "1 <= sizes.length <= 20; 0 <= target <= 10000; sizes are positive integers.",
     "function solve({sizes,target}) { const dp=Array(target+1).fill(Infinity);dp[0]=0;for(let amount=1;amount<=target;amount++)for(const size of sizes)if(size<=amount)dp[amount]=Math.min(dp[amount],dp[amount-size]+1);return Number.isFinite(dp[target])?dp[target]:-1; }",
     [({"sizes":[2,5],"target":7},2), ({"sizes":[2],"target":3},-1), ({"sizes":[3],"target":0},0)],
     "O(target * sizes.length)", "O(target)", "1D dynamic programming",
     "Define dp[a] as the minimum bundles for exact amount a; impossible states stay infinite.",
     "Largest-first greedy fails for some denomination sets; the recurrence examines every final bundle choice."),
    ("dp", "Increasing release sequence", "hard",
     "Given integer release scores, return the length of the longest strictly increasing subsequence, not necessarily contiguous. Equal scores do not extend it.",
     "Length <= 100000; finite safe integers.",
     "function solve(values) { const tails=[];for(const value of values){let low=0,high=tails.length;while(low<high){const mid=(low+high)>>1;if(tails[mid]<value)low=mid+1;else high=mid;}tails[low]=value;}return tails.length; }",
     [([],0), ([4,2,3,1,5],3), ([2,2,2],1)],
     "O(n log n)", "O(n)", "DP frontier with lower bound",
     "tails[i] is the smallest possible final value of an increasing subsequence of length i+1.",
     "A quadratic predecessor DP is a useful oracle; a minimal-tail frontier supports binary search but does not itself reconstruct a valid subsequence."),
    ("greedy", "Maximum compatible activities", "medium",
     "Given half-open activities [start,end), return the maximum number one worker can perform without overlap. Every activity has equal value.",
     "At most 10000 activities; start < end.",
     "function solve(activities) { const sorted=activities.slice().sort((a,b)=>a[1]-b[1]||a[0]-b[0]);let end=-Infinity,count=0;for(const [a,b]of sorted)if(a>=end){count++;end=b;}return count; }",
     [([],0), ([[0,5],[1,2],[2,3],[3,4]],3)],
     "O(n log n)", "O(n) for input-preserving copy", "Greedy exchange",
     "Replace an optimal first choice with the earliest-finishing compatible activity without reducing future options.",
     "Earliest start and shortest duration are tempting but incorrect general heuristics; weighted activities need a different DP."),
    ("greedy", "Find a viable circular route", "hard",
     "Input is {supply,cost} of equal nonzero length. Return the candidate start produced by a left-to-right deficit reset that can complete the circle, or -1 if total supply is insufficient.",
     "At most 100000 stops; nonnegative finite integers; when several starts work, use the stated deterministic reset rule.",
     "function solve({supply,cost}) { let total=0,tank=0,start=0;for(let i=0;i<supply.length;i++){const delta=supply[i]-cost[i];total+=delta;tank+=delta;if(tank<0){start=i+1;tank=0;}}return total<0?-1:start%supply.length; }",
     [({"supply":[1],"cost":[2]},-1), ({"supply":[1,2,3],"cost":[2,2,1]},1)],
     "O(n)", "O(1)", "Greedy deficit elimination",
     "A negative accumulated segment eliminates every starting point inside that segment.",
     "Testing each possible start is quadratic; the deficit argument safely skips a whole segment."),
    ("advanced", "Count indexed prefixes", "medium",
     "Input is {words,prefixes}. Return for each prefix the number of inserted words beginning with it, counting duplicate insertions. Empty prefix counts all words. Build a trie.",
     "At most 10000 words; lowercase ASCII; each word/prefix length <= 100.",
     "function solve({words,prefixes}) { const root={count:0,next:new Map()};for(const word of words){let node=root;node.count++;for(const char of word){if(!node.next.has(char))node.next.set(char,{count:0,next:new Map()});node=node.next.get(char);node.count++;}}return prefixes.map(prefix=>{let node=root;for(const char of prefix){node=node.next.get(char);if(!node)return 0;}return node.count;}); }",
     [({"words":[],"prefixes":[""]},[0]), ({"words":["api","app","api"],"prefixes":["a","ap","api","b",""]},[3,3,2,0,3])],
     "O(total word characters + total prefix characters)", "O(total word characters)",
     "Trie", "Increment counts once per inserted word along its path.",
     "Scanning every word for every prefix repeats character work; the trie shares prefix traversal."),
    ("advanced", "Mutable range counter", "hard",
     "Input is {values,operations}. Operations are ['add',index,delta] or ['sum',left,right] with inclusive indices. Return each sum result. Use a Fenwick tree.",
     "1 <= values.length <= 10000; at most 10000 valid operations; sums remain safe integers.",
     "function solve({values,operations}) { const tree=Array(values.length+1).fill(0),out=[];function add(i,d){for(i++;i<tree.length;i+=i&-i)tree[i]+=d;}function prefix(i){let sum=0;for(i++;i>0;i-=i&-i)sum+=tree[i];return sum;}values.forEach((v,i)=>add(i,v));for(const [kind,a,b]of operations){if(kind==='add')add(a,b);else out.push(prefix(b)-prefix(a-1));}return out; }",
     [({"values":[1,2,3],"operations":[["sum",0,2],["add",1,5],["sum",1,2]]},[6,10]),
      ({"values":[0],"operations":[["add",0,-2],["sum",0,0]]},[-2])],
     "O((n + q) log n) with this simple construction", "O(n)", "Fenwick tree",
     "Convert external indices to one-based positions and define each low-bit range.",
     "Plain prefixes make updates linear; Fenwick partial sums balance updates and queries logarithmically."),
    ("senior", "Idempotent batch boundary", "medium",
     "Given events {id,value}, return {accepted,duplicates}. Accept only the first occurrence of each id in input order; duplicates is the number of later occurrences. Do not mutate the input.",
     "At most 10000 events; ids are strings; values are integers; deduplication applies only within this batch.",
     "function solve(events) { const seen=new Set(),accepted=[];let duplicates=0;for(const event of events){if(seen.has(event.id)){duplicates++;continue;}seen.add(event.id);accepted.push({...event});}return {accepted,duplicates}; }",
     [([],{"accepted":[],"duplicates":0}), ([{"id":"a","value":1},{"id":"a","value":2}],{"accepted":[{"id":"a","value":1}],"duplicates":1})],
     "O(n) expected", "O(n)", "Practical API contract",
     "Specify duplicate identity, scope and ordering before choosing the storage structure.",
     "This local function is not durable exactly-once delivery. Extend with transactional idempotency keys, validation and partial-failure tests in a separate API lab."),
    ("senior", "Bounded asynchronous work", "hard",
     "Input is {values,limit}. Simulate asynchronous doubling using a resolved Promise for each item. Return doubled values in original input order, using no more than limit worker loops. Do not launch one Promise per input item up front.",
     "1 <= limit <= 10; at most 1000 values; this exercise models scheduling, not network or CPU parallelism.",
     "async function solve({values,limit}) { let next=0;const out=Array(values.length);async function worker(){while(next<values.length){const index=next++;out[index]=await Promise.resolve(values[index]*2);}}await Promise.all(Array.from({length:Math.min(limit,values.length)},()=>worker()));return out; }",
     [({"values":[],"limit":2},[]), ({"values":[3,1,4],"limit":2},[6,2,8])],
     "O(n) work", "O(limit) worker state excluding output",
     "Bounded async scheduling",
     "Claim an index before awaiting, and write its result back to that original index.",
     "Output fixtures alone cannot prove the concurrency bound. Instrument active work in your own tests and discuss rejection, cancellation and thread-based races."),
]

RESOURCE_SPECS = [
    ("mit-video", "MIT 6.006 Introduction to Algorithms, Spring 2020", "MIT OpenCourseWare",
     "https://www.youtube.com/playlist?list=PLUl4u3cNGP63EdVPNLG3ToM6LaEUuStEY", "youtube_playlist"),
    ("bari-video", "Algorithms", "Abdul Bari",
     "https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O", "youtube_playlist"),
    ("fiset-video", "Data Structures Easy to Advanced Course", "William Fiset / freeCodeCamp",
     "https://www.youtube.com/watch?v=RBSGKlAvoiM", "youtube_video"),
    ("graph-video", "Algorithms Course - Graph Theory Tutorial", "William Fiset / freeCodeCamp",
     "https://www.youtube.com/watch?v=09_LlHjoEiY", "youtube_video"),
    ("dp-video", "Dynamic Programming - Learn to Solve Algorithmic Problems", "Alvin Zablan / freeCodeCamp",
     "https://www.youtube.com/watch?v=oBt53YbR9Kk", "youtube_video"),
    ("neetcode-video", "NeetCode public playlists", "NeetCode",
     "https://www.youtube.com/@NeetCode/playlists", "youtube_channel"),
    ("mit-notes", "MIT 6.006 lecture and recitation notes", "MIT OpenCourseWare",
     "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/pages/lecture-notes/", "official_documentation"),
    ("princeton", "Algorithms, 4th edition companion site", "Princeton / Sedgewick and Wayne",
     "https://algs4.cs.princeton.edu/home/", "official_documentation"),
    ("visualgo", "VisuAlgo algorithm visualizations", "VisuAlgo",
     "https://visualgo.net/en", "interactive_visualization"),
    ("js-docs", "JavaScript reference", "MDN",
     "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference", "official_documentation"),
    ("ts-docs", "TypeScript handbook", "Microsoft",
     "https://www.typescriptlang.org/docs/handbook/intro.html", "official_documentation"),
    ("python-docs", "Python data structures tutorial", "Python Software Foundation",
     "https://docs.python.org/3/tutorial/datastructures.html", "official_documentation"),
    ("neetcode-roadmap", "NeetCode 150 public roadmap", "NeetCode",
     "https://neetcode.io/roadmap", "practice_roadmap"),
]

RESOURCE_SKILLS = {
    "mit-video": ["foundations", "arrays", "sorting", "trees", "heaps", "graphs", "dp", "greedy"],
    "bari-video": ["foundations", "sorting", "graphs", "backtracking", "dp", "greedy"],
    "fiset-video": ["arrays", "linked", "stacks", "trees", "heaps", "advanced"],
    "graph-video": ["graphs", "advanced"],
    "dp-video": ["dp"],
    "neetcode-video": ["arrays", "patterns", "linked", "stacks", "sorting", "trees", "heaps", "intervals", "graphs", "backtracking", "dp", "greedy", "advanced"],
    "mit-notes": ["foundations", "arrays", "sorting", "trees", "heaps", "graphs", "dp", "greedy"],
    "princeton": ["foundations", "arrays", "sorting", "trees", "heaps", "graphs", "advanced"],
    "visualgo": ["foundations", "arrays", "linked", "stacks", "sorting", "trees", "heaps", "graphs", "advanced"],
    "js-docs": ["arrays", "advanced", "senior"],
    "ts-docs": ["senior"],
    "python-docs": ["arrays", "stacks", "sorting"],
    "neetcode-roadmap": ["arrays", "patterns", "linked", "stacks", "sorting", "trees", "heaps", "intervals", "graphs", "backtracking", "dp", "greedy", "advanced"],
}

EXTRA_SOURCES = [
    ("candidate-hackerrank", "https://www.hackerrank.com/interview/preparation-kits", "HackerRank preparation kits; supplementary practice candidate, not selected as a video-first course."),
    ("candidate-leetcode", "https://leetcode.com/explore/", "LeetCode Explore; free portions coexist with premium content. Not used as a source of copied problem statements."),
    ("senior-video", "https://www.youtube.com/watch?v=C842vFY5kRo", "Existing Academy system-design video reused for practical API and engineering trade-offs."),
    ("senior-reading", "https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design", "Existing Academy official API design reading reused for the senior module."),
]

COMPANIES = [
    ("google","Google","big_tech","https://www.google.com/about/careers/applications/"),
    ("microsoft","Microsoft","big_tech","https://careers.microsoft.com/"),
    ("amazon","Amazon","big_tech","https://www.amazon.jobs/"),
    ("meta","Meta","big_tech","https://www.metacareers.com/"),
    ("apple","Apple","big_tech","https://www.apple.com/careers/"),
    ("netflix","Netflix","big_tech","https://jobs.netflix.com/"),
    ("nvidia","NVIDIA","big_tech","https://www.nvidia.com/en-us/about-nvidia/careers/"),
    ("stripe","Stripe","engineering_technology","https://stripe.com/jobs"),
    ("uber","Uber","engineering_technology","https://www.uber.com/us/en/careers/"),
    ("airbnb","Airbnb","engineering_technology","https://careers.airbnb.com/"),
    ("linkedin","LinkedIn","engineering_technology","https://careers.linkedin.com/"),
    ("bloomberg","Bloomberg","engineering_technology","https://www.bloomberg.com/company/careers/"),
    ("datadog","Datadog","engineering_technology","https://careers.datadoghq.com/"),
    ("cloudflare","Cloudflare","engineering_technology","https://www.cloudflare.com/careers/"),
    ("snowflake","Snowflake","engineering_technology","https://careers.snowflake.com/"),
    ("adobe","Adobe","engineering_technology","https://careers.adobe.com/"),
    ("salesforce","Salesforce","engineering_technology","https://careers.salesforce.com/"),
    ("atlassian","Atlassian","engineering_technology","https://www.atlassian.com/company/careers"),
    ("shopify","Shopify","engineering_technology","https://www.shopify.com/careers"),
    ("openai","OpenAI","ai","https://openai.com/careers/"),
    ("anthropic","Anthropic","ai","https://www.anthropic.com/careers"),
    ("cohere","Cohere","ai","https://cohere.com/careers"),
    ("mistral","Mistral AI","ai","https://mistral.ai/careers"),
    ("huggingface","Hugging Face","ai","https://huggingface.co/join-us"),
    ("deepmind","Google DeepMind","ai","https://deepmind.google/careers/"),
    ("safaricom","Safaricom","africa","https://www.safaricom.co.ke/careers"),
    ("mkopa","M-KOPA","africa","https://www.m-kopa.com/careers"),
    ("andela","Andela","africa","https://www.andela.com/careers"),
    ("flutterwave","Flutterwave","africa","https://flutterwave.com/us/careers"),
    ("cellulant","Cellulant","africa","https://www.cellulant.io/careers/"),
    ("pesapal","PesaPal","africa","https://pesapal.careers-page.com/"),
    ("microsoft-africa","Microsoft Africa","africa","https://careers.microsoft.com/"),
    ("worldbank","World Bank","international_development","https://www.worldbank.org/en/about/careers"),
    ("unicef","UNICEF","international_development","https://jobs.unicef.org/"),
    ("undp","UNDP","international_development","https://www.undp.org/careers"),
    ("canonical","Canonical","remote_first","https://canonical.com/careers"),
    ("gitlab","GitLab","remote_first","https://about.gitlab.com/jobs/"),
    ("automattic","Automattic","remote_first","https://automattic.com/work-with-us/"),
]

GUIDES = {
    "google": ("https://www.google.com/about/careers/applications/interview-tips/",
               "Official general interview advice is available. The accessible page does not establish a specific engineering round count, DSA topic frequency or senior design format; use balanced practice pending recruiter guidance.", []),
    "microsoft": ("https://careers.microsoft.com/us/en/technical-interviewing",
                  "Official guidance names data structures and Big O. Practice clean implementation, tests and technical explanation.", ["arrays","patterns","linked","trees","graphs","senior"]),
    "amazon": ("https://www.amazon.jobs/content/en/how-we-hire/interview-prep/software-development-topics",
               "Official guidance includes a coding assessment and software-development topics. Supplement coding with object-oriented/system design and Leadership Principles preparation.", ["arrays","trees","graphs","dp","senior"]),
    "meta": ("https://d3no4ktch0fdq4.cloudfront.net/public/course/files/Meta_SWE_full_loop_guide.pdf",
             "The employer-authored full-loop guide covers coding, design and behavioral interviews. Recruiter materials govern the actual role's format.", ["arrays","patterns","trees","graphs"]),
    "nvidia": ("https://www.nvidia.com/en-us/about-nvidia/careers/how-we-hire/",
               "Official guidance describes team interviews and 30-60-minute conversations. It does not establish a universal DSA topic distribution.", []),
    "openai": ("https://openai.com/interview-guide/",
               "Official guidance says assessments vary by team and may include pair coding, take-home projects or technical tests. Prepare practical implementation; no universal puzzle-only process is claimed.", ["senior"]),
    "atlassian": ("https://www.atlassian.com/company/careers/resources/interviewing/engineering",
                  "Official engineering guidance covers data structures, code design, system design and values discussions.", ["arrays","trees","senior"]),
}
REPORTS = [
    ("stripe", "https://leetcode.com/discuss/post/8372404/", "Candidate report, July 2, 2026: multipart parsing/data processing using sets and maps; not guaranteed policy."),
    ("stripe", "https://leetcode.com/discuss/post/7566910/", "New-graduate candidate report, February 2026: multipart programming and follow-ups. Senior applicability is uncertain."),
    ("anthropic", "https://interviewing.io/anthropic-interview-questions", "Candidate-report synthesis updated October 29, 2026; practical coding and systems reports, not employer policy."),
]


def build():
    from academy.dsa_content import package_schema

    (ROOT / "DSA_PACKAGE_SCHEMA.json").write_text(json.dumps(package_schema(), indent=2) + "\n")
    observations = json.loads((ROOT / "DSA_URL_VERIFICATION.json").read_text()) if (ROOT / "DSA_URL_VERIFICATION.json").exists() else {}
    sources = []

    def source(key, url, label, evidence="official"):
        sid = "source-dsa-" + key
        sources.append({"id": sid, "url": url, "title": label, "source_type": evidence,
                        "accessed_at": DATE, "http_observation": observations.get(url, {"status": None, "scope": "Public web search/page inspection; direct HTTP not yet recorded."})})
        return sid

    skills = [{"id": "skill-dsa-" + key, "name": name, "track_ids": ["track-dsa"],
               "topic_concepts": concepts.split(", "), "sample_required_count": None,
               "sample_preferred_count": None, "sample_mention_count": None, "sample_job_ids": [],
               "learner_leverage": "Programming experience is leverage, not evidence of algorithm fluency.",
               "practice_requirement": invariant}
              for key, name, concepts, explanation, invariant, tradeoff in MODULES]
    modules = [{"id": "knowledge-dsa-" + key, "title": name, "track_ids": ["track-dsa"],
                "skill_ids": ["skill-dsa-" + key], "explanation": explanation, "invariant": invariant,
                "tradeoff": tradeoff, "concepts": concepts.split(", "),
                "advanced_labs": [f"Implement and test {concept.strip()} on tiny synthetic inputs; state an invariant, a counterexample and complexity."
                                  for concept in concepts.split(",")]}
               for key, name, concepts, explanation, invariant, tradeoff in MODULES]
    write("DSA_SKILL_MATRIX.json", tracks=[{
        "id": "track-dsa", "name": "Data Structures and Algorithms - Big Tech Coding Interviews",
        "priority": 6, "target_role_categories": ["senior", "coding_interviews"],
        "baseline_assessment": "Solve one array, tree and graph problem without hints; state complexity and write edge-case tests. Do not assume prior professional experience proves DSA fluency.",
        "skill_ids": [s["id"] for s in skills],
    }], skills=skills, modules=modules)
    resources = []
    for key, title, creator, url, kind in RESOURCE_SPECS:
        sid = source("resource-" + key, url, title)
        video = kind.startswith("youtube")
        metadata = observations.get(url, {}).get("oembed", {})
        resources.append({
            "id": "resource-dsa-" + key, "title": metadata.get("title") or title,
            "selection_label": title, "publisher_author": metadata.get("author_name"),
            "creator": creator, "provider": creator,
            "url": url, "resource_type": kind, "track_ids": ["track-dsa"],
            "skill_ids": ["skill-dsa-"+key for key in RESOURCE_SKILLS[key]], "difficulty": "intermediate_to_advanced",
            "duration_minutes": None, "duration_status": "Exact duration unavailable; watch selected sections within the lesson budget.",
            "published_at": None, "last_verified_at": DATE, "free_status": "fully_free" if video or key in ("visualgo","neetcode-roadmap") else "free_documentation",
            "free_evidence": "Public publisher material or public YouTube listing inspected. Paid add-ons, textbooks, certificates and Pro courses are not required; only the linked public portion is selected.",
            "verification_scope": "Publisher/public listing and available chapter metadata; no exhaustive playback or full correctness audit.",
            "view_count": None, "like_count": None, "comment_count": None, "playlist_size": None,
            "community_feedback_summary": "Comments unavailable; no sentiment or exact engagement counts invented.",
            "overall_score": 76 if video else 78, "technical_quality_score": 20,
            "score_breakdown": {"correctness_spot_check":20,"coverage":16,"demonstration":15 if video else 12,
                                "interview_relevance":15,"publisher_provenance":10 if video else 15,"community":None},
            "score_rationale": "Provisional editorial selection score, not measured learner outcomes; missing community data scores no points. Correctness 25, coverage 20, demonstration 20, relevance 20, provenance 15; maximum 100.",
            "confidence":"medium", "verification_sources":[sid],
            "limitations":["Most videos are foundational refreshers; the original independent labs and proofs raise senior-level depth.",
                           "Exact publication/duration and comments remain unknown; older stable algorithms are not made current by changing a date."],
            "selection_reason": "Original educator/publisher, visual or documented explanation, free selected content, and explicit limits.",
        })
    write("DSA_RESOURCE_CATALOG.json", resources=resources)
    for key, url, title in EXTRA_SOURCES:
        source(key, url, title)
    questions = []
    for index, (key,title,difficulty,statement,constraints,code,cases,time,space,pattern,hint,explanation) in enumerate(EXERCISES):
        qid = f"question-dsa-{index+1:02}"
        questions.append({
            "id":qid,"track_id":"track-dsa","title":title,"question":statement,
            "skill_ids":["skill-dsa-"+key],"pattern":pattern,"difficulty":difficulty,"category":"coding",
            "constraints":[constraints],"input_output":"Call solve(input) with the JSON input shape in each fixture; return a JSON-compatible result.",
            "test_cases":[{"input":a,"output":b} for a,b in cases], "hints":[hint],
            "expected_algorithm":pattern,"complexity":{"time":time,"space":space},
            "solution_code":code,"detailed_explanation":explanation+" "+hint,
            "expected_answer_elements":[hint,"State the invariant.",f"Time: {time}; auxiliary space: {space}.","Cover empty, boundary and adversarial inputs."],
            "evaluation_rubric":[{"criterion":dimension,"max_points":5,"full_credit":description}
                                for dimension,description in [
                                    ("understanding","Clarifies input, output and constraints."),
                                    ("pattern","Explains why the pattern applies rather than naming it."),
                                    ("algorithm","Derives and compares a valid approach."),
                                    ("correctness","Justifies invariant and checks against a tiny oracle."),
                                    ("quality","Uses readable contracts and minimal mutable state."),
                                    ("time_complexity","Derives input-dependent runtime including sorting/output."),
                                    ("space_complexity","Separates auxiliary space, stack and output."),
                                    ("edge_cases","Handles all stated boundary and malformed-input policies."),
                                    ("testing","Runs representative and counterexample tests."),
                                    ("communication","Explains decisions, uncertainty and trade-offs.")]],
            "follow_up_questions":[f"Prove this claim: {hint}", "Build a brute-force oracle for small inputs and compare randomized valid cases.",
                                   "Which changed constraint would invalidate this algorithm? Implement and analyze that harder variation."],
            "common_mistakes":["Ignoring the precise input contract.","Treating sample tests as a full correctness proof.",
                               "Forgetting output size or recursive stack in complexity.","Claiming a company asks this original problem."],
            "related_question_ids":[f"question-dsa-{(index ^ 1)+1:02}"],
            "recommended_minutes":20 if difficulty=="easy" else 30 if difficulty=="medium" else 45,
            "source_ids":["source-dsa-resource-mit-notes"], "source_url":None,
            "company_relevance":"General practice mapped to researched preparation topics, not evidence this exercise was asked.",
            "interview_stage":"coding_or_practical_screen",
            "authorship":"Original Academy exercise and reference implementation. Difficulty is editorial, not employer- or platform-calibrated.",
        })
    write("DSA_QUESTION_BANK.json", questions=questions, mock_interviews=[
        {"id":"mock-dsa-"+key,"track_id":"track-dsa","title":name+" coding conversation",
         "question_ids":[q["id"] for q in questions if q["skill_ids"]==["skill-dsa-"+key]],
         "duration_minutes":60,"scenario":"Clarify, derive, implement, test, analyze complexity and discuss a changed constraint."}
        for key,name,*_ in MODULES])
    existing = json.loads((ROOT.parent / "EMPLOYER_RESEARCH.json").read_text())["employers"]
    employer_ids = {e["id"] for e in existing}
    employers, profiles = [], []
    for key,name,category,url in COMPANIES:
        eid = "employer-" + ("microsoft" if key=="microsoft-africa" else key)
        sid = source("company-"+key,url,name+" careers")
        tier = 1 if key in ("google","microsoft","amazon","meta","safaricom","mkopa","andela","microsoft-africa") else 3 if category in ("ai","international_development") else 2
        focus, process, classification, profile_sources = [], "No role-specific interview process verified. Use balanced generic practice and ask the recruiter for the actual assessment.", "unknown", [sid]
        if key in GUIDES:
            guide, process, focus = GUIDES[key]
            profile_sources.append(source("guide-"+key,guide,name+" official preparation guide"))
            classification = "officially_documented"
        if key == "microsoft-africa":
            process = GUIDES["microsoft"][1] + " Regional vacancies and country eligibility require separate confirmation."
            focus = GUIDES["microsoft"][2]
            profile_sources.append("source-dsa-guide-microsoft")
            classification = "officially_documented"
        if key in ("stripe","anthropic"):
            relevant = [r for r in REPORTS if r[0]==key]
            profile_sources.extend(source("report-"+key+"-"+str(i), report_url, summary, "candidate_report")
                                   for i,(_,report_url,summary) in enumerate(relevant))
            classification = "limited_anecdotal_evidence"
            process = "Candidate reports suggest practical multipart implementation; not a guaranteed format or question-frequency estimate."
            focus = ["arrays","senior"] if key=="stripe" else ["senior"]
        limitations = ["No suitable live vacancy or Kenyan remote-employment eligibility is asserted.",
                       "Seniority, visa/payroll eligibility, location, format and tool policy must be confirmed for the specific role.",
                       "Unknown fields are not negative evidence; preparation tiers are editable editorial priorities."]
        profiles.append({
            "id":"profile-dsa-"+key,"name":name,"employer_id":eid,"category":category,
            "career_url":url,"relevant_job_titles":["Software Engineer","Senior Software Engineer","Platform Engineer"],
            "job_title_status":"Watchlist search terms, not verified current openings.",
            "location_eligibility":"Unknown for this learner; inspect each posting and ask about Kenya payroll, work authorization and relocation.",
            "remote_from_kenya":"unknown","seniority":"Role-specific; no uniform cross-company level mapping.",
            "preparation_tier":tier,"interview_evidence":classification,"coding_assessment_format":process,
            "dsa_intensity":"Coding preparation is documented; intensity is not measured." if classification=="officially_documented" and focus else "unknown",
            "main_dsa_topics":focus,"pattern_skill_ids":["skill-dsa-"+item for item in focus],
            "system_design_expectations":"Documented design component; confirm seniority and exact scope." if key in ("microsoft","microsoft-africa","amazon","meta","atlassian") else "Unknown from the selected sources; prepare the existing software track without claiming it is required.",
            "practical_coding_expectations":process,
            "behavioral_requirements":"Prepare evidence of ownership, collaboration and decisions; this is general preparation, not an employer-specific rubric.",
            "role_specific_requirements":"Extract from the exact job description in Career Intelligence.",
            "candidate_report_scope":"Individual/aggregated public reports, not official policy; new-graduate evidence is not automatically transferable to senior hiring." if key in ("stripe","anthropic") else "No candidate report retained.",
            "source_ids":profile_sources,"source_urls":[url]+([GUIDES[key][0]] if key in GUIDES else []),
            "research_date":DATE,"confidence":"medium" if classification=="officially_documented" else "low",
            "limitations":limitations,
        })
        if eid not in employer_ids:
            employers.append({"id":eid,"name":name,"career_url":url,
                              "watch_keywords":["Software Engineer","Senior Software Engineer"],
                              "limitations":"Research watchlist only. Interview process and Kenya eligibility may be unknown.",
                              "enabled":True,"preparation_tier":tier})
            employer_ids.add(eid)
        if key=="amazon":
            profiles[-1]["behavioral_requirements"]="Official preparation material includes Leadership Principles and behavioral examples. Prepare specific ownership, decision and collaboration stories using STAR."
    source_urls = {entry["id"]: entry["url"] for entry in sources}
    for profile in profiles:
        profile["source_urls"] = [source_urls[sid] for sid in profile["source_ids"]]
    write("DSA_COMPANY_RESEARCH.json", profiles=profiles, employers=employers)
    write("DSA_SOURCE_REGISTER.json", sources=sources)
    write("DSA_LEARNING_DEPENDENCIES.json", edges=[
        {"from":"skill-dsa-"+MODULES[i-1][0],"to":"skill-dsa-"+MODULES[i][0],
         "reason":"Recommended course sequence; repair an undemonstrated prerequisite within the current budget."}
        for i in range(1,len(MODULES))])
    for days in (14,30,60):
        lessons=[]
        phases = ["concept_and_slice","independent_implementation","failure_and_tradeoffs","mock_and_revision"]
        for day in range(1,days+1):
            module_index = day if days==14 else (day-1)//(days//15)
            phase_index = 0 if days==14 else (day-1)%(days//15)
            key,name,concepts,explanation,invariant,tradeoff = MODULES[module_index]
            chosen = [q for q in questions if q["skill_ids"]==["skill-dsa-"+key]]
            if days==14 and day==1:
                chosen = questions[:4]
                name = "Algorithmic foundations, arrays and strings"
                explanation = MODULES[0][3] + " " + explanation
            lesson_id=f"lesson-dsa-{days}-{day:02}"
            video="dp-video" if key=="dp" else "graph-video" if key=="graphs" else "bari-video" if key in ("foundations","greedy","backtracking") else "fiset-video" if key in ("linked","stacks","heaps","advanced") else "mit-video"
            if key=="patterns": video="neetcode-video"
            video_id = "resource-system-design" if key=="senior" else "resource-dsa-"+video
            reading_ids = ["resource-api-design","resource-dsa-js-docs","resource-dsa-ts-docs"] if key=="senior" else ["resource-dsa-mit-notes","resource-dsa-js-docs"]
            tasks = [
                "Guided implementation: derive a brute-force oracle, then implement the first exercise and prove its invariant.",
                "Independent implementation: close all hints, solve the second exercise, test boundary cases and record complexity.",
                f"Advanced extension: implement and test two of {concepts}. Inject one incorrect state update and verify an adversarial test catches it; compare approaches.",
                "Mock and revision: run a 60-minute two-question conversation without hints, review recorded weaknesses and reimplement a failed earlier question.",
            ]
            lessons.append({
                "id":lesson_id,"day":day,"track_id":"track-dsa","topic":name+" - "+phases[phase_index].replace("_"," "),
                "knowledge_unit_id":"knowledge-dsa-"+key,"skill_ids":list(dict.fromkeys(sid for q in chosen for sid in q["skill_ids"])),
                "learning_objectives":[explanation,invariant,tradeoff],
                "why_it_matters":"Derive the approach, implement independently, test and communicate complexity rather than memorizing a platform answer.",
                "prerequisites":{"lesson_ids":[lessons[-1]["id"]] if lessons else [],
                                 "skill_ids":[],"baseline_knowledge":["Working programming, functions, basic tests and Git"],
                                 "gap_policy":"Repair prerequisites inside the budget; extend the calendar rather than adding hidden hours."},
                "recommended_youtube_resource_id":video_id,
                "supplementary_reading_resource_ids":reading_ids,
                "video_duration_minutes":None,"planned_video_minutes":35,
                "video_selection":{"focus":concepts,"selection_method":"Select a relevant publisher-labeled chapter and watch at most 35 minutes.",
                                   "verified_timestamp_seconds":None,"coverage_limit":"No claim that the linked video fully covers every named advanced topic."},
                "reading_focus":f"Read the sections on {concepts}; verify language-specific semantics against the reference.",
                "concept_explanation":explanation,"example_implementation":chosen[0]["solution_code"],
                "complexity_analysis":chosen[0]["complexity"],
                "coding_exercises":[q["id"] for q in chosen],"interview_question_ids":[q["id"] for q in chosen],
                "practical_implementation_exercise":tasks[phase_index] + " Guided contract: "+chosen[0]["question"]+" Independent contract: "+chosen[-1]["question"],
                "revision_exercise":"Reimplement a previously failed question without hints. Explain why its invariant holds and which input broke your earlier approach.",
                "study_guide":{
                    "before_video":[explanation,"Recognize: "+invariant,"Predict a brute-force approach and its input-dependent cost."],
                    "during_video":["Observe the state changes and the proof behind them.", "Record the invariant, not just the final code.", "For later phases choose a new variation or prerequisite repair rather than repeating a watched chapter. Stop within the video budget."],
                    "after_video":{"comprehension_questions":[tradeoff,"Which counterexample defeats the tempting shortcut?"],
                                   "practice":tasks[phase_index],
                                   "validate_understanding":[invariant,"Run all fixtures and a tiny randomized oracle.",
                                                            "State time, auxiliary space, stack and output complexity."]}},
                "time_budget_minutes":{"preparation":10,"video":35,"reading":25,"implementation":100,"interview":20,"revision":20},
                "estimated_total_study_minutes":210,"expected_outcome":"Original tested implementation, independent attempt, explicit complexity analysis and a spoken trade-off explanation.",
                "completion_criteria":["Record passing fixtures and at least one adversarial test.","Submit an independent implementation or honestly record assistance.",
                                       "Record time/space analysis and explain the invariant.","Answer the interview questions; opening a solution does not complete the lesson."],
                "phase":phases[phase_index],"assessment_status":"authored_plan_not_learner_executed",
            })
        write(f"DSA_CURRICULUM_{days}_DAYS.json",curricula=[{
            "id":f"curriculum-dsa-{days}","track_id":"track-dsa","duration_days":days,
            "daily_minutes":210,"total_hours":days*3.5,
            "scope":"Intensive refresh with combined foundation/array day; not mastery." if days==14 else "Progressive guided and independent practice with advanced extension labs; mastery is evidence-based, not guaranteed by elapsed days.",
            "capstone_completion_level":"tested_algorithm_portfolio",
            "adjustment_policy":{"daily_budget":"180-240 minutes configurable; 30/45-minute companion practice is reserved from another track, never added on top.",
                                 "unfinished_work":"Carry or extend unfinished work; do not mark viewed solutions mastered."},
            "lessons":lessons,
        }])


if __name__ == "__main__":
    build()
