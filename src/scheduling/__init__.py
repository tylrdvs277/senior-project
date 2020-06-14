from typing import Any, List, Set, cast, Tuple
from queue import PriorityQueue

from graph import *
from rtl import *
from rtl.value import Memory

MEM_LATENCY = 4
DEF_USE_LATENCY = 1
ANTI_LATENCY = 0

# The class irepresents a dependency DAG
class Graph:

    class Heuristic:

        def __init__(
            self, 
            order: int
        ) -> None:
            self.d: int = 0
            self.s: int = 0
            self.order: int = order

        def __repr__(
            self
        ) -> str:
            return "({},{},{})".format(self.d, self.s, self.order)

        def __lt__(
            self, 
            value: 'Graph.Heuristic'
        ) -> bool:
            lt: bool = False

            if self.d > value.d:
                lt = True
            elif self.d == value.d:
                if self.s > value.s:
                    lt = True
                elif self.s == value.s:
                    lt = self.order < value.order

            return lt

    def __init__(
        self, 
        directed: bool = False
    ) -> None:
        self.__matrix: List[List[Optional[int]]] = []
        self.__transpose: List[List[Optional[int]]] = []
        self.__dim: int = 0
        self.__node_to_row: Dict[int,int] = dict()
        self.__row_to_node: Dict[int,int] = dict()
        self.__directed: bool = directed
        self.__node_heuristics: Dict[int,Graph.Heuristic] = dict()

    def add_node(
        self, 
        node: int
    ) -> None:
        if node in self:
            return

        self.__dim += 1

        for idx in range(len(self.__matrix)):
            self.__matrix[idx].append(None)
            self.__transpose[idx].append(None)

        self.__matrix.append([None for _ in range(self.__dim)])
        self.__transpose.append([None for _ in range(self.__dim)])

        self.__node_to_row[node] = self.__dim - 1
        self.__row_to_node[self.__dim - 1] = node
        self.__node_heuristics[node] = Graph.Heuristic(node)

    def add_edge(
        self, 
        node1: int,
        node2: int, 
        weight: int
    ) -> None:
        row1: int
        row2: int

        for node in [node1, node2]:
            self.add_node(node)

        row1 = self.__node_to_row[node1]
        row2 = self.__node_to_row[node2]

        self.__node_heuristics[node1].s += 1 if self.__matrix[row1][row2] is None else 0
        self.__matrix[row1][row2] = weight
        self.__transpose[row2][row1] = weight
        if not self.__directed:
            self.__matrix[row2][row1] = weight
            self.__transpose[row1][row2] = weight
            self.__node_heuristics[node2].s += 1 if self.__matrix[row1][row2] is None else 0

    def remove_node(
        self, 
        node: int
    ) -> None:
        assert(node in self)

        row_num: int = self.__node_to_row[node]

        self.__matrix[row_num] = [None for _ in range(self.__dim)]
        self.__transpose[row_num] = [None for _ in range(self.__dim)]

        for idx in range(len(self.__matrix)):
            self.__matrix[idx][row_num] = None
            self.__transpose[idx][row_num] = None

        del self.__row_to_node[row_num]
        del self.__node_to_row[node]
        del self.__node_heuristics[node]
    
    def is_edge(
        self, 
        node1: int, 
        node2: int
    ) -> bool:
        assert(node1 in self and node2 in self)

        row1 = self.__node_to_row[node1]
        row2 = self.__node_to_row[node2]

        return self.__matrix[row1][row2] is not None

    def dfs(
        self, 
        start_node: int, 
        visited: Set[int]
    ) -> List[int]:
        topo_sort: List[int] = [start_node]
        row: int = self.__node_to_row[start_node]

        visited.update({start_node})

        for idx in range(len(self.__matrix)):
            if self.__matrix[idx][row] is not None and self.__row_to_node[idx] not in visited:
                topo_sort += self.dfs(self.__row_to_node[idx], visited)

        return topo_sort

    # Calculate the "d" value for each node
    def heuristics(
        self
    ) -> None:
        visited: Set[int] = set()
        topo_sort: List[int] = []

        for idx in range(len(self.__matrix)):
            if self.__row_to_node[idx] not in visited:
                topo_sort = self.dfs(
                    self.__row_to_node[idx], visited) + topo_sort

        row: int
        for node in topo_sort:
            row = self.__node_to_row[node]
            for idx in range(len(self.__matrix)):
                if self.__matrix[idx][row] is not None:
                    self.__node_heuristics[self.__row_to_node[idx]].d = (
                        max(
                            self.__node_heuristics[self.__row_to_node[idx]].d,
                            self.__node_heuristics[node].d +
                            cast('int',self.__matrix[idx][row])
                        )
                    )

    # Build the schedule list using a READY list
    def schedule(
        self
    ) -> List[int]:
        ready: PriorityQueue[Graph.Heuristic] = PriorityQueue()
        seen: Set[int] = set()
        schedule: List[int] = []
        curr: Graph.Heuristic

        while True:
            for idx in range(len(self.__transpose)):
                if (idx in self.__row_to_node
                        and self.__row_to_node[idx] not in seen
                        and self.__transpose[idx].count(None) == self.__dim):
                    seen.add(self.__row_to_node[idx])
                    ready.put(self.__node_heuristics[self.__row_to_node[idx]])

            if ready.empty():
                break

            curr = ready.get()
            schedule.append(curr.order)
            self.remove_node(curr.order)

        return schedule

    def __contains__(
        self, 
        node: int
    ) -> bool:
        return node in self.__node_to_row


# Divides code into basic blocks
def bb_instruction_schedule(
    vertices: List[Vertex], 
    register_mapping: Optional[RegMap]=None
) -> None:
    init_length: int = len(vertices)

    idx: int = 0
    basic_block: int = -1
    first_bb: int = -1

    for vertex in vertices:
        vertex.rtl.set_defs()
        vertex.rtl.set_uses()
        vertex.rtl.set_defs_reg(register_mapping)
        vertex.rtl.set_uses_reg(register_mapping)

    while idx < len(vertices):
        if basic_block == -1:
            basic_block = vertices[idx].rtl.basic_block
            first_bb = idx
            idx += 1
        elif basic_block != vertices[idx].rtl.basic_block:
            local_instruction_schedule(vertices, first_bb, idx - 1)
            assert(init_length == len(vertices))
            basic_block = -1
        else:
            idx += 1


# Builds the DAG for a basic block and reschedules the instructions
def local_instruction_schedule(
    vertices: List[Vertex], 
    start: int, 
    end: int
) -> None:

    if isinstance(vertices[start].rtl, Label):
        start += 1
    if isinstance(vertices[end].rtl, Jump):
        end -= 1

    curr_defs: Set[Register]
    next_defs: Set[Register]
    next_uses: Set[Register]
    mem: bool = False
    matrix: Graph = Graph(directed=True)
    idx2: int
    idx1: int

    for idx1 in range(start, end + 1):
        matrix.add_node(idx1)

    for idx1 in range(start, end + 1):

        mem = ((isinstance(vertices[idx1].rtl, SetInsn)
                and isinstance(cast(SetInsn, vertices[idx1].rtl).use_value, Memory))
               or isinstance(vertices[idx1].rtl, Load))

        curr_defs = vertices[idx1].rtl.defs
        if isinstance(vertices[idx1].rtl, Call):
            curr_defs = curr_defs.union(CALLER_SAVE_REGISTERS)

        idx2 = idx1 - 1
        while idx2 >= start and len(curr_defs) > 0:
            next_defs = vertices[idx2].rtl.defs
            next_uses = vertices[idx2].rtl.uses
            if isinstance(vertices[idx2].rtl, Call):
                next_defs = next_defs.union(CALLER_SAVE_REGISTERS)
                next_uses = next_uses.union(CALLER_SAVE_REGISTERS)

            if len(curr_defs.intersection(next_uses)) != 0:
                matrix.add_edge(idx2, idx1, ANTI_LATENCY)
            curr_defs = curr_defs.difference(next_defs)
            idx2 -= 1

        curr_defs = vertices[idx1].rtl.defs
        if isinstance(vertices[idx1].rtl, Call):
            curr_defs = curr_defs.union(CALLER_SAVE_REGISTERS)

        idx2 = idx1 + 1
        while idx2 <= end and len(curr_defs) > 0:
            next_defs = vertices[idx2].rtl.defs
            next_uses = vertices[idx2].rtl.uses
            if isinstance(vertices[idx2].rtl, Call):
                next_defs = next_defs.union(CALLER_SAVE_REGISTERS)
                next_uses = next_uses.union(CALLER_SAVE_REGISTERS)

            if len(curr_defs.intersection(next_uses)) != 0:
                matrix.add_edge(
                    idx1, idx2, 
                    MEM_LATENCY if mem else DEF_USE_LATENCY
                )
            curr_defs = curr_defs.difference(next_defs)
            idx2 += 1

    matrix.heuristics()
    vertices[start : end + 1] = [vertices[idx] for idx in matrix.schedule()]


def trace_schedule(
    vertices: List[Vertex]
) -> List[RTL]:

    for vertex in vertices:
        vertex.visited = False

    trace: List[Vertex] = get_trace(vertices)
    joins: Dict[Vertex, Set[Register]] = dict()
    splits: Dict[Vertex, Set[Register]] = dict()
    for vertex in trace:
        if len(vertex.in_edges) > 1:
            live_out: Set[Register] = set()
            for edge in vertex.in_edges:
                if edge.start not in trace:
                    live_out = live_out.union(edge.start.live_out)
            joins[vertex] = live_out
        if len(vertex.out_edges) > 1:
            live_in: Set[Register] = set()
            for edge in vertex.out_edges:
                if edge.end not in trace:
                    live_in = live_in.union(edge.end.live_in)
            splits[vertex] = live_in
    before: List[Vertex] = vertices[ : vertices.index(trace[0])]
    after: List[Vertex] = vertices[vertices.index(trace[-1]) : ]
    gaps: Dict[Tuple[Vertex, Vertex], List[Vertex]] = dict()
    for idx1 in range(len(trace) - 1):
        idx2: int = idx1 + 1
        v_idx1: int = vertices.index(trace[idx1])
        v_idx2: int = vertices.index(trace[idx2])
        if v_idx1 + 1 != v_idx2:
            gaps[(trace[idx1], trace[idx2])] = vertices[v_idx1 + 1 : v_idx2]
    
    schedule: List[Vertex] = trace_schedule_(trace, joins, splits)

    new_vertices: List[Vertex] = before
    for idx1 in range(len(schedule) - 1):
        idx2: int = idx1 + 1
        new_vertices.append(schedule[idx1])
        if (schedule[idx1], schedule[idx2]) in gaps:
            new_vertices += gaps[(schedule[idx1], schedule[idx2])]
    new_vertices += after

    return [vertex.rtl for vertex in new_vertices]


def get_trace(
    vertices: List[Vertex]
) -> List[Vertex]:
    trace: List[Vertex] = list()

    max_vertex: Vertex = vertices[0]
    max_expect: float = vertices[0].expect
    for vertex in vertices[1 : ]:
        if vertex.expect > max_expect:
            max_expect = vertex.expect
            max_vertex = vertex

    start: Vertex = max_vertex

    current: Vertex = start

    # Go forward
    while True:
        for edge in current.out_edges:
            if any(
                [isinstance(next_edge.start.rtl, LoopPreheader) for next_edge in edge.end.in_edges]
            ):
                break
        else:
            best_next: Optional[Vertex] = None
            best_expect: float = -1.0
            for edge in current.out_edges:
                if edge.end.expect > best_expect:
                    best_expect = edge.end.expect
                    best_next = edge.end
            if best_next is not None:
                best_next_v: Vertex = cast(Vertex, best_next)
                if best_next_v.expects[current] >= max(best_next_v.expects.values()):
                    current = best_next_v
                    trace.append(current)
                    continue
                else:
                    break
            else:
                break
        break

    current = start
    while True:
        for edge in current.in_edges:
            if edge.start.loop > current.loop:
                break
        else:
            trace.append(current)
            best_prev: Optional[Vertex] = None
            best_expect: float = -1.0
            for edge in current.in_edges:
                if edge.start.expect > best_expect:
                    best_expect = edge.start.expect
                    best_next = edge.start
            if best_prev is not None:
                best_prev_v: Vertex = cast(Vertex, best_prev)
                if current.expects[best_prev_v] >= max(current.expects.values()):
                    current = best_prev_v
                    continue
                else:
                    break
            else:
                break
        break

    return sorted(trace, key=lambda v: vertices.index(v))


def trace_schedule_(
    trace: List[Vertex],
    joins: Dict[Vertex, Set[Register]],
    splits: Dict[Vertex, Set[Register]]
) -> List[Vertex]:
    matrix: Graph = Graph(directed=True)

    for vertex in trace:
        vertex.rtl.set_defs()
        vertex.rtl.set_uses()

    for idx in range(len(trace)):
        matrix.add_node(idx)

    for idx, vertex in enumerate(trace):
        
        mem: bool = (
            (isinstance(vertex.rtl, SetInsn)
            and isinstance(cast(SetInsn, vertex.rtl).use_value, Memory))
            or isinstance(vertex.rtl, Load)
        )
        is_join: bool = vertex in joins
        is_split: bool = vertex in splits
        b_branch: bool = (
            isinstance(vertex.rtl, Jump) and 
            not isinstance(vertex.rtl, ConditionalJump)
        )

        curr_defs: Set[Register] = vertex.rtl.defs
        if isinstance(vertex.rtl, Call):
            curr_defs = curr_defs.union(CALLER_SAVE_REGISTERS)
        elif isinstance(vertex.rtl, Compare):
            curr_defs = curr_defs.union({ConditionCodes.get_cc()})

        idx_prime: int = idx - 1
        while idx_prime >= 0:
            next_defs = trace[idx_prime].rtl.defs
            next_uses = trace[idx_prime].rtl.uses
            if isinstance(trace[idx_prime].rtl, Call):
                next_defs = next_defs.union(CALLER_SAVE_REGISTERS)
                next_uses = next_uses.union(CALLER_SAVE_REGISTERS)
            elif isinstance(trace[idx_prime].rtl, Compare):
                next_defs = next_defs.union({ConditionCodes.get_cc()})
            elif isinstance(trace[idx_prime].rtl, ConditionalJump):
                next_uses = next_uses.union({ConditionCodes.get_cc()})

            if (
                len(curr_defs.intersection(next_uses)) != 0 or is_split or 
                (is_join and len(next_defs.intersection(joins[vertex])) > 0) or 
                b_branch
            ):
                matrix.add_edge(idx_prime, idx, ANTI_LATENCY)
            curr_defs = curr_defs.difference(next_defs)
            idx_prime -= 1

        curr_defs = vertex.rtl.defs
        if isinstance(vertex.rtl, Call):
            curr_defs = curr_defs.union(CALLER_SAVE_REGISTERS)
        elif isinstance(vertex.rtl, Compare):
            curr_defs = curr_defs.union({ConditionCodes.get_cc()})

        for idx_prime, vertex_prime in enumerate(trace[idx + 1: ], idx + 1):
            next_defs = vertex_prime.rtl.defs
            next_uses = vertex_prime.rtl.uses
            is_store: bool = (
                (isinstance(vertex_prime.rtl, SetInsn)
                and isinstance(cast(SetInsn, vertex_prime.rtl).def_value, Memory))
                or isinstance(vertex_prime.rtl, Store)
            )
            if isinstance(vertex_prime.rtl, Call):
                next_defs = next_defs.union(CALLER_SAVE_REGISTERS)
                next_uses = next_uses.union(CALLER_SAVE_REGISTERS)
            elif isinstance(vertex_prime.rtl, Compare):
                next_defs = next_defs.union({ConditionCodes.get_cc()})
            elif isinstance(vertex_prime.rtl, ConditionalJump):
                next_uses = next_uses.union({ConditionCodes.get_cc()})

            if len(curr_defs.intersection(next_uses)) != 0:
                matrix.add_edge(
                    idx, idx_prime, 
                    MEM_LATENCY if mem else DEF_USE_LATENCY
                )
            elif (
                is_join or (is_split and is_store) or 
                (is_split and len(curr_defs.intersection(splits[vertex])) > 0) or
                b_branch
            ):
                matrix.add_edge(idx, idx_prime, ANTI_LATENCY)
            curr_defs = curr_defs.difference(next_defs)

    matrix.heuristics()
    trace = [trace[idx] for idx in matrix.schedule()]

    return trace
