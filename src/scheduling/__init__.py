from typing import Any, List, Set
from queue import PriorityQueue

from graph import *
from rtl import *
from rtl.value import Memory

MEM_LATENCY = 4
DEF_USE_LATENCY = 1
ANTI_LATENCY = 0


class Graph:

    class Heuristic:

        def __init__(self, order: Any):
            self.d = 0
            self.s = 0
            self.order = order

        def __repr__(self):
            return "({},{},{})".format(self.d, self.s, self.order)

        def __lt__(self, value):
            assert(self.__class__ == value.__class__)

            if self.d > value.d:
                return True
            elif self.d == value.d:
                if self.s > value.s:
                    return True
                elif self.s == value.s:
                    return self.order < value.order
                else:
                    return False
            else:
                return False

    def __init__(self, directed: bool = False):
        self.__matrix = []
        self.__dim = 0
        self.__node_to_row = dict()
        self.__row_to_node = dict()
        self.__directed = directed
        self.__node_heuristics = dict()

    def add_node(self, node: Any):
        if node in self:
            return

        self.__dim += 1

        for row in self.__matrix:
            row.append(None)

        self.__matrix.append([None for _ in range(self.__dim)])

        self.__node_to_row[node] = self.__dim - 1
        self.__row_to_node[self.__dim - 1] = node
        self.__node_heuristics[node] = Graph.Heuristic(node)

    def add_edge(self, node1: Any, node2: Any, weight: int):
        row1 = -1
        row2 = -1

        for node in [node1, node2]:
            self.add_node(node)

        row1 = self.__node_to_row[node1]
        row2 = self.__node_to_row[node2]

        self.__node_heuristics[node1].s += 1 if self.__matrix[row1][row2] is None else 0
        self.__matrix[row1][row2] = weight
        if not self.__directed:
            self.__matrix[row2][row1] = weight
            self.__node_heuristics[node2].s += 1 if self.__matrix[row1][row2] is None else 0

    def remove_node(self, node: Any):
        assert(node in self)

        row_num = self.__node_to_row[node]

        del self.__matrix[row_num]

        for row in self.__matrix:
            del row[row_num]

        del self.__row_to_node[row_num]
        del self.__node_to_row[node]

        self.__dim -= 1

    def is_edge(self, node1: Any, node2: Any):
        assert(node1 in self and node2 in self)

        row1 = self.__node_to_row[node1]
        row2 = self.__node_to_row[node2]

        return self.__matrix[row1][row2] is not None

    def dfs(self, start_node: Any, visited: Set):
        topo_sort = [start_node]
        row = self.__node_to_row[start_node]

        visited.update({start_node})

        for idx in range(len(self.__matrix)):
            if self.__matrix[idx][row] is not None and self.__row_to_node[idx] not in visited:
                topo_sort += self.dfs(self.__row_to_node[idx], visited)

        return topo_sort

    def heuristics(self):
        visited = set()
        topo_sort = []

        for idx in range(len(self.__matrix)):
            if self.__row_to_node[idx] not in visited:
                topo_sort = self.dfs(
                    self.__row_to_node[idx], visited) + topo_sort

        row = -1
        for node in topo_sort:
            row = self.__node_to_row[node]
            for idx in range(len(self.__matrix)):
                if self.__matrix[idx][row] is not None:
                    self.__node_heuristics[self.__row_to_node[idx]].d = (
                        max(
                            self.__node_heuristics[self.__row_to_node[idx]].d,
                            self.__node_heuristics[node].d +
                            self.__matrix[idx][row]
                        )
                    )

    def __contains__(self, node):
        return node in self.__node_to_row


def bb_instruction_schedule(vertices: List[Vertex], register_mapping=None):
    init_length = len(vertices)

    idx = 0
    basic_block = -1
    first_bb = -1

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


def local_instruction_schedule(vertices: List[Vertex], start, end):

    if isinstance(vertices[start].rtl, Label):
        start += 1
    if isinstance(vertices[end].rtl, Jump):
        end -= 1

    curr_defs = None
    next_defs = None
    next_uses = None
    mem = False
    matrix = Graph(directed=True)
    idx2 = -1

    for idx1 in range(start, end + 1):
        matrix.add_node(idx1)

    for idx1 in range(start, end + 1):

        mem = ((isinstance(vertices[idx1].rtl, SetInsn)
                and isinstance(vertices[idx1].rtl.use_value, Memory))
               or isinstance(vertices[idx1].rtl, Load))

        curr_defs = vertices[idx1].rtl.defs
        if isinstance(vertices[idx1].rtl, Call):
            curr_defs = curr_defs.union(CALLER_SAVE_REGISTERS)

        idx2 = idx1 - 1
        while idx2 >= start and len(curr_defs) > 0:
            next_defs = vertices[idx2].rtl.defs
            next_uses = vertices[idx2].rtl.uses
            if isinstance(vertices[idx1].rtl, Call):
                next_defs = next_defs.union(CALLER_SAVE_REGISTERS)
                next_uses = next_uses.union(CALLER_SAVE_REGISTERS)

            curr_defs = curr_defs.difference(next_defs)
            if len(curr_defs.intersection(next_uses)) != 0:
                matrix.add_edge(idx2, idx1, ANTI_LATENCY)
            idx2 -= 1

        curr_defs = vertices[idx1].rtl.get_defs()
        if isinstance(vertices[idx1].rtl, Call):
            curr_defs.update(CALLER_SAVE_REGISTERS)

        idx2 = idx1 + 1
        while idx2 <= end and len(curr_defs) > 0:
            next_defs = vertices[idx2].rtl.defs
            next_uses = vertices[idx2].rtl.uses
            if isinstance(vertices[idx1].rtl, Call):
                next_defs = next_defs.union(CALLER_SAVE_REGISTERS)
                next_uses = next_uses.union(CALLER_SAVE_REGISTERS)

            if len(curr_defs.intersection(next_uses)) != 0:
                matrix.add_edge(
                    idx1, idx2, MEM_LATENCY if mem else DEF_USE_LATENCY)
            curr_defs = curr_defs.difference(next_defs)
            idx2 += 1

    matrix.heuristics()
    
