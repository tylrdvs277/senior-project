from os import getenv
from sys import argv
from typing import List, Tuple, Any, Optional, Dict

import sexp as s
import rtl as r
import graph as g
import liveness as l
import scheduling as i
import rtl.value as v

class IllegalArgumentError(Exception):
    pass

def parse_args(
    args: List[str]
) -> Tuple[str,str]:
    try:
        _, in_file, out_file = args
    except ValueError:
        raise IllegalArgumentError("Usage: {} in_file out_file".format(args[0]))

    return in_file, out_file


def main(
) -> None:
    rtls: List[r.RTL] = []
    spilled: List[r.Register] = []

    in_file: str
    out_file: str
    in_file, out_file = parse_args(argv)

    rtl_sexps: List[List[Any]]
    r.func_name, rtl_sexps = s.read_sexp(in_file)
    for rtl_sexp in rtl_sexps:
        rtls += r.RTL.factory(rtl_sexp)

    vertices: List[g.Vertex] = g.generate_cfg(rtls)
    g.dominance(vertices)
    g.identify_backedge(vertices)
    return

    if not getenv("NO_SCHEDULE"):
        i.bb_instruction_schedule(vertices, None)

    colorable: bool = False
    colors: Dict[r.Register,int]
    matrix: l.Matrix[r.Register]
    while not colorable:

        l.compute_liveness(vertices)
        matrix = l.interference_matrix(vertices)
        
        colorable = True
        try:
            colors = l.color_graph(matrix)
        except l.UncolorableError:
            colorable = False
        
        if not colorable:
            spill_reg: r.VirtualRegister = l.spill_candidate(vertices)
            spilled.append(spill_reg)
            l.spill_register(vertices, spill_reg)

    register_allocation: v.RegMap = l.color_to_register(colors)
    if not getenv("NO_SCHEDULE"):
        i.bb_instruction_schedule(vertices, register_allocation)

    rtls = [vertex.rtl for vertex in vertices]
    asm: str = r.generate_assembly(rtls, register_allocation, spilled)

    with open(out_file, "w") as f:
        f.write(asm)


if __name__ == "__main__":
    main()
