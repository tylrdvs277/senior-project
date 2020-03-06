from copy import deepcopy
from typing import Set, List, Dict, TypeVar, Generic, Optional

from graph import *
from rtl import *
from rtl.value import *
from rtl.registers import ArchitectureRegisters as AR

NUM_COLORS: int = len(AR.REAL_REGISTERS_NUM)
COLORS: Set[int] = set(i for i in range(NUM_COLORS))

T = TypeVar("T")

class Matrix(Generic[T]):

    def __init__(
        self
    ) -> None:
        self.matrix: List[List[int]] = []
        self.dim: int = 0
        self.node_to_row: Dict[T,int] = dict()
        self.row_to_node: Dict[int,T] = dict()

        self.is_deleted: bool = False 
        self.delete_matrix: List[List[int]]
        self.deleted: Set[int]
        self.num_colors: int
        self.delete_dim: int

    def add_node(
        self, 
        node: T
    ) -> None:
        assert(not self.is_deleted)

        if node in self:
            return

        self.dim += 1

        for row in self.matrix:
            row.append(0)

        new_row: List[int] = [0 for _ in range(self.dim)]
        self.matrix.append(new_row)

        self.node_to_row[node] = self.dim - 1
        self.row_to_node[self.dim - 1] = node

    def remove_node(
        self
    ) -> T:
        assert(self.is_deleted)

        found: bool = False
        found_row_num: int
        row_num: int = 0
        max_degree: int = -1
        while not found and row_num < len(self.delete_matrix):
            if row_num in self.deleted:
                row_num += 1
                continue

            degree: int = sum(self.delete_matrix[row_num])
            if degree < self.num_colors:
                found = True
                found_row_num = row_num
            elif degree > max_degree:
                max_degree = degree
                found_row_num = row_num

            row_num += 1

        self.delete_dim -= 1
        self.deleted.add(found_row_num)
        for i in range(self.dim):
            self.delete_matrix[found_row_num][i] = 0
            self.delete_matrix[i][found_row_num] = 0

        return self.row_to_node[found_row_num]

    def init_coloring(
        self, 
        num_colors: int
    ) -> None:
        self.is_deleted = True
        self.delete_matrix = deepcopy(self.matrix)
        self.deleted = set()
        self.num_colors = num_colors
        self.delete_dim = self.dim

    def add_edge(
        self, 
        node1: T, 
        node2: T
    ):
        assert(not self.is_deleted)

        for node in [node1, node2]:
            self.add_node(node)

        row1: int = self.node_to_row[node1]
        row2: int = self.node_to_row[node2]

        self.matrix[row1][row2] = 1
        self.matrix[row2][row1] = 1

    def interferes_with(
        self, 
        node: T
    ) -> Set[T]:
        assert(node in self)

        interfere = set()

        row_num = self.node_to_row[node]
        for i in range(len(self.matrix[row_num])):
            if self.matrix[row_num][i] == 1:
                interfere.add(self.row_to_node[i])

        return interfere

    def __contains__(
        self, 
        node: T
    ):
        return node in self.node_to_row


# Compute live in and live out until it converges
def compute_liveness(
    vertices: List[Vertex]
):
    iterate: bool = True

    for vertex in vertices:
        vertex.rtl.set_defs()
        vertex.rtl.set_uses()
        vertex.init_liveness()

    while iterate:
        iterate = False

        for vertex in reversed(vertices):
            vertex.compute_live_out()
            if vertex.compute_live_in():
                iterate = True


# Builds the interference matrix using liveness
def interference_matrix(
    vertices: List[Vertex]
) -> Matrix[Register]:
    matrix: Matrix[Register] = Matrix()

    real_regs: List[RealRegister] = list(REAL_REGISTERS)
    for i in range(len(real_regs)):
        for j in range(i + 1, len(real_regs)):
            matrix.add_edge(
                real_regs[i],
                real_regs[j]
            )

    for vertex in vertices:
        live_in_list: List[Register] = list(vertex.live_in)
        if isinstance(vertex.rtl, Call):
            live_in_list.extend(list(CALLER_SAVE_REGISTERS))

        for i in range(len(live_in_list)):
            if live_in_list[i] not in matrix:
                matrix.add_node(live_in_list[i])
            for j in range(i + 1, len(live_in_list)):
                matrix.add_edge(
                    live_in_list[i],
                    live_in_list[j]
                )

    return matrix

class UncolorableError(ValueError):
    pass

# Attempts to color the graph
def color_graph(
    matrix: Matrix
) -> Dict[Register,int]:
    matrix.init_coloring(NUM_COLORS)
    colorable: bool = True
    node_to_color: Dict[Register,int] = dict()

    node: Register
    node_stack: List[Register] = [matrix.remove_node() for _ in range(matrix.dim)]
    while len(node_stack) > 0 and colorable:
        node = node_stack.pop()
        interferes = matrix.interferes_with(node)
        interferes_colors: Set[int] = set(
            node_to_color[node] for node in interferes if node in node_to_color
        )
        color_candidates: Set[int] = COLORS.difference(interferes_colors)

        if len(color_candidates) == 0:
            colorable = False
        else:
            node_to_color[node] = color_candidates.pop()

    if not colorable:
        raise UncolorableError

    return node_to_color


# ID a spill candidate
def spill_candidate(
    vertices: List[Vertex]
) -> VirtualRegister:
    reg_spill_factor: Dict[VirtualRegister,int] = dict()

    for vertex in vertices:
        for reg in vertex.rtl.defs.union(vertex.rtl.uses):
            if (
                not isinstance(reg, VirtualRegister)
                or reg.prime != 0
            ):
                continue
            if reg not in reg_spill_factor:
                reg_spill_factor[reg] = 0
            reg_spill_factor[reg] += 1 * (2 ** vertex.loop)

    min_reg: VirtualRegister
    min_spill_factor: int = -1
    for (reg, spill_factor) in reg_spill_factor.items():
        if spill_factor < min_spill_factor or min_spill_factor == -1:
            min_spill_factor = spill_factor
            min_reg = reg
    min_reg_copy: VirtualRegister = deepcopy(min_reg)

    return min_reg_copy


# Spill the spill candidate
def spill_register(
    vertices: List[Vertex], 
    reg: VirtualRegister
) -> None:
    idx: int = 0
    new_reg: VirtualRegister
    rtl: RTL
    new_vertex: Vertex
    prime: int
    while idx < len(vertices):
        prime = vertices[idx].rtl.this_insn

        if reg in vertices[idx].rtl.uses:
            new_reg = VirtualRegister(reg.reg_type, reg.number, prime)
            vertices[idx].rtl.update_virt_reg(reg, prime)
            rtl = Load(-1, vertices[idx].rtl.basic_block, new_reg)
            new_vertex = Vertex(rtl)
            new_vertex.loop = vertices[idx].loop

            for edge in vertices[idx].in_edges:
                edge.end = new_vertex
                new_vertex.in_edges.append(edge)

            vertices[idx].in_edges = []
            Edge.link(new_vertex, vertices[idx], Edge.EdgeType.SEQUENTIAL)

            vertices.insert(idx, new_vertex)
            idx += 1

        if reg in vertices[idx].rtl.defs:
            new_reg = VirtualRegister(reg.reg_type, reg.number, prime)
            vertices[idx].rtl.update_virt_reg(reg, prime)
            rtl = Store(-1, vertices[idx].rtl.basic_block, new_reg)
            new_vertex = Vertex(rtl)
            new_vertex.loop = vertices[idx].loop

            for edge in vertices[idx].out_edges:
                edge.start = new_vertex
                new_vertex.out_edges.append(edge)

            vertices[idx].out_edges = []
            Edge.link(vertices[idx], new_vertex, Edge.EdgeType.SEQUENTIAL)

            vertices.insert(idx + 1, new_vertex)
            idx += 2
        else:
            idx += 1


# Maps a color to architecture register
def color_to_register(
    color_mapping: Dict[Register, int]
) -> RegMap:
    color_register_mapping: Dict[int,RealRegister] = dict()
    register_mapping: RegMap = RegMap(dict())

    for real_reg in REAL_REGISTERS:
        color_register_mapping[color_mapping[real_reg]] = real_reg

    for (reg, color) in color_mapping.items():
        register_mapping[reg] = color_register_mapping[color]

    return register_mapping
