
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

    def init(
        self
    ) -> None:
        self.live_out.clear()
        self.live_in.clear()

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
        BASIC_BLOCK: int = 1
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
            next_vertex = insn_reference[vertex.rtl.jump_loc]
            Edge.link(vertex, next_vertex, Edge.EdgeType.JUMP)

            if isinstance(vertex.rtl, ConditionalJump):
                next_vertex = vertices[idx + 1]
                Edge.link(vertex, next_vertex, Edge.EdgeType.SEQUENTIAL)

        else:
            next_vertex = vertices[idx + 1]
            Edge.link(vertex, next_vertex, Edge.EdgeType.BASIC_BLOCK)

    return vertices


# TODO: replace with dominator post-dom
def identify_loops(
    vertices: List[Vertex]
) -> None:
    queue: Queue[Vertex] = Queue()

    for vertex in vertices:
        vertex.loop = 0
        vertex.visited = False

    queue.put(vertices[0])
    while not queue.empty():
        curr = queue.get()
        curr.visited = True

        for out_edge in curr.out_edges:
            next_vertex = out_edge.end
            if next_vertex.visited:
                for i in range(vertices.index(next_vertex), vertices.index(curr) + 1):
                    vertices[i].loop += 1
            else:
                queue.put(next_vertex)
