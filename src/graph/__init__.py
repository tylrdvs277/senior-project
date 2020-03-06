
from typing import List
from enum import Enum
from queue import Queue

from rtl import *

# Control flow structures
class Vertex:

    def __init__(
        self, 
        rtl: RTL
    ) -> None:
        self.in_edges: List[Edge] = []
        self.out_edges: List[Edge] = []

        self.rtl: RTL = rtl

        self.visited: bool = False
        self.loop: int = 0

        self.live_in: Set[Register] = set()
        self.live_out: Set[Register] = set()

        self.dom: Set['Vertex'] = set()

    def init_liveness(
        self
    ) -> None:
        self.live_out.clear()
        self.live_in.clear()

    def add_dom(
        self,
        vertex: 'Vertex'
    ) -> None:
        self.dom.add(vertex)

    def update_dom(
        self
    ) -> bool:
        tmp: Set['Vertex'] = set()
        edge: Edge
        change: bool

        tmp = tmp.union(self.in_edges[0].start.dom)
        for edge in self.in_edges[1 : ]:
            tmp.intersection_update(edge.start.dom)
        tmp.add(self)

        change = False
        if len(tmp) != len(self.dom):
            change = True
            self.dom = tmp

        return change

    def compute_live_out(
        self
    ) -> None:
        self.live_out = set()

        for edge in self.out_edges:
            self.live_out = self.live_out.union(edge.end.live_in)

    def compute_live_in(
        self
    ) -> bool:
        temp = self.rtl.uses.union(self.live_out.difference(self.rtl.defs))
        changed: bool = False

        if temp != self.live_in:
            self.live_in = temp
            changed = True

        return changed


class Edge:

    class EdgeType(Enum):
        SEQUENTIAL: int = 2
        JUMP: int = 3

    def __init__(
        self, 
        start: Vertex, 
        end: Vertex, 
        edge_type: EdgeType, 
        src_bb: int, 
        dest_bb: int
    ) -> None:
        self.start: Vertex = start
        self.end: Vertex = end

        self.edge_type: Edge.EdgeType = edge_type

        self.src_bb: int = src_bb
        self.dest_bb: int = dest_bb
        
        self.visited: bool = False

    @staticmethod
    def link(
        start: Vertex, 
        end: Vertex, 
        edge_type: EdgeType
    ):
        edge = Edge(
            start,
            end,
            edge_type,
            start.rtl.basic_block,
            end.rtl.basic_block
        )
        start.out_edges.append(edge)
        end.in_edges.append(edge)


# Generates an instruction local CFG
def generate_cfg(
    rtls: List[RTL]
) -> List[Vertex]:
    vertex: Vertex
    next_vertex: Vertex
    vertices: List[Vertex] = [Vertex(rtl) for rtl in rtls]
    insn_reference: Dict[int,Vertex] = {vertex.rtl.this_insn: vertex for vertex in vertices}

    for idx in range(len(vertices) - 1):
        vertex = vertices[idx]

        if isinstance(vertex.rtl, Jump):
            jump_rtl: Jump = cast(Jump, vertex.rtl)
            next_vertex = insn_reference[jump_rtl.jump_loc]
            Edge.link(vertex, next_vertex, Edge.EdgeType.JUMP)

            if isinstance(vertex.rtl, ConditionalJump):
                next_vertex = vertices[idx + 1]
                Edge.link(vertex, next_vertex, Edge.EdgeType.SEQUENTIAL)

        elif isinstance(vertex.rtl, Call) and cast(Call, vertex.rtl).is_exit_func():
            pass

        else:
            next_vertex = vertices[idx + 1]
            Edge.link(vertex, next_vertex, Edge.EdgeType.SEQUENTIAL)

    return vertices


def dominance(
    vertices: List[Vertex]
) -> None:
    vertex: Vertex

    vertices[0].add_dom(vertices[0])
    for vertex in vertices[1 : ]:
        for dom_vertex in vertices:
            vertex.add_dom(dom_vertex)

    change: bool = True
    while change:
        change = False

        for vertex in vertices[1 : ]:
            if vertex.update_dom():
                change = True


# Backedge m to n
def identify_loop(
    vertices: List[Vertex],
    m: Vertex,
    n: Vertex
) -> Set[Vertex]:
    loop: Set[Vertex] = {m, n}
    stack: List[Vertex] = []
    p: Vertex
    q: Vertex

    if m is not n:
        stack.append(m)

    while len(stack) > 0:
        p = stack.pop()
        edge: Edge

        for edge in p.in_edges:
            q = edge.start
            if q not in loop:
                loop.add(q)
                stack.append(q)
    
    return loop


# TODO: replace with dominator post-dom
def identify_backedge(
    vertices: List[Vertex]
) -> None:
    vertex: Vertex
    loop: Set[Vertex]
    headers: Dict[Vertex,Set[Vertex]] = dict()
    edge: Edge
    loop_header: Vertex
    loop_headers: Set[Vertex] = set()
    idx: int
    max_bb: int
    new_vertex: Vertex

    for vertex in vertices:
        for edge in vertex.out_edges:
            if edge.end in vertex.dom:
                loop_header = edge.end
                loop = identify_loop(vertices, vertex, loop_header)
                loop_headers.add(loop_header)

                for v in loop:
                    v.loop += 1

    max_bb = max(map(lambda vertex: vertex.rtl.basic_block, vertices))
    for loop_header in loop_headers:
        max_bb += 1
        new_vertex = Vertex(LoopPreheader(-1, max_bb))

        preheader_in_edges: List[Edge] = []
        loop_header_in_edges: List[Edge] = []
        for edge in loop_header.in_edges:
            if edge.edge_type == Edge.EdgeType.SEQUENTIAL:
                edge.end = new_vertex
                preheader_in_edges.append(edge)
            elif edge.edge_type == Edge.EdgeType.JUMP:
                loop_header_in_edges.append(edge)
            else:
                raise NotImplementedError
        new_vertex.in_edges = preheader_in_edges
        loop_header.in_edges = loop_header_in_edges
        Edge.link(new_vertex, loop_header, Edge.EdgeType.SEQUENTIAL)

        new_vertex.loop = loop_header.loop - 1

        idx = vertices.index(loop_header)
        vertices.insert(idx, new_vertex)
