
from sys import argv, exit
from typing import List

import sexp as s
import rtl as r
import graph as g
import liveness as l


def parse_args(args: List[str]):

    try:
        _, in_file, out_file = args
    except ValueError:
        print("Usage: {} in_file out_file".format(args[0]))
        exit(1)

    return in_file, out_file


def main():
    rtls = []
    spilled = []
    in_file, out_file = parse_args(argv)

    r.func_name, rtl_sexps = s.read_sexp(in_file)
    for rtl_sexp in rtl_sexps:
        rtls += r.RTL.factory(rtl_sexp)

    vertices = g.generate_cfg(rtls)
    g.identify_loops(vertices)

    colorable = False
    while not colorable:

        l.compute_liveness(vertices)
        matrix = l.interference_matrix(vertices)
        colors = l.color_graph(matrix)
        
        if colors is not None:
            colorable = True
        else:
            spill_reg = l.spill_candidate(vertices)
            spilled.append(spill_reg)
            l.spill_register(vertices, spill_reg)

    register_allocation = l.color_to_register(colors)
    rtls = [vertex.rtl for vertex in vertices]

    
    asm = r.generate_assembly(rtls, register_allocation, spilled)

    with open(out_file, "w") as f:
        f.write(asm)


if __name__ == "__main__":
    main()
