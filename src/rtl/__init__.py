
from typing import List, Any, Dict
from enum import Enum

from rtl.value import *
from rtl.registers import ArchitectureRegisters as AR


func_name = None
CALLER_SAVE_REGISTERS = set(
    CallerSaveRegister(Type.SI, number, None)
    for number in AR.CALLER_SAVE_REGISTERS_NUM
)
CALLEE_SAVE_REGISTERS = set(
    RealRegister(Type.SI, number, None)
    for number in AR.CALLEE_SAVE_REGISTERS_NUM
)
REAL_REGISTERS = CALLER_SAVE_REGISTERS.union(
    CALLEE_SAVE_REGISTERS
)


class RTL:
    
    def __init__(self, this_insn: int, basic_block: int):
        self.this_insn = this_insn
        self.basic_block = basic_block

        self.defs = None
        self.uses = None

    def set_defs(self):
        self.defs = set()

    def set_uses(self):
        self.uses = set()

    @staticmethod
    def get_(regs, register_mapping):
        ret = regs

        if register_mapping is not None:
            ret = set()
            for reg in regs:
                ret.add(register_mapping[reg])

        return ret

    def set_defs_reg(self, register_mapping=None):
        self.defs = RTL.get_(self.defs, register_mapping)

    def set_uses_reg(self, register_mapping=None):
        self.uses = RTL.get_(self.uses, register_mapping)

    def get_defs(self):
        return self.defs

    def get_uses(self):
        return self.uses

    def asm(self, register_mapping, spilled):
        return []

    def update_virt_reg(self, reg: Value, prime: int):
        pass
        
    @staticmethod
    def factory(rtl_sexp: List[Any]):
        rtl_repr = []

        try:
            insn_type, this_insn, _, _, basic_block, *rest = rtl_sexp
            insn_type = insn_type.lower()
            insn_classes = dict(
                insn=Insn,
                jump_insn=Jump,
                call_insn=Call,
                code_label=Label
            )

            try:
                rtl_repr.append(insn_classes[insn_type].factory(this_insn, basic_block, rest))
            except KeyError:
                pass
        except ValueError:
            pass

        return rtl_repr


class Insn(RTL):
        
    def __init__(self, this_insn: int, basic_block: int, use_value: Value):
        super(Insn, self).__init__(this_insn, basic_block)
        self.use_value = use_value

    def set_uses(self):
        self.uses = self.use_value.get_uses()

    def update_virt_reg(self, reg: Value, prime: int):
        self.use_value.update_virt_reg(reg, prime)

    @staticmethod
    def factory(this_insn: int, basic_block: int, rest: List[Any]):
        insn = None
        instruction = rest[0]
        use_sexp = None
        def_sexp = None

        try: # Set instruction
            _, def_sexp, use_sexp = instruction
            insn = SetInsn(
                this_insn,
                basic_block,
                Value.factory(def_sexp),
                Value.factory(use_sexp)
            )
        except ValueError: # Use instruction
            _, use_sexp = instruction
            insn = Insn(
                this_insn,
                basic_block,
                Value.factory(use_sexp)
            )

        return insn


class SetInsn(Insn):
    
    def __init__(self, this_insn: int, basic_block: int, def_value: Value, use_value: Value):
        super(SetInsn, self).__init__(this_insn, basic_block, use_value)
        self.def_value = def_value

    def set_defs(self):
        self.defs = self.def_value.get_defs()

    def set_uses(self):
        super(SetInsn, self).set_uses()

        if isinstance(self.def_value, Memory):
            self.uses.update(self.def_value.get_uses())

    def update_virt_reg(self, reg: Value, prime: int):
        super(SetInsn, self).update_virt_reg(reg, prime)
        self.def_value.update_virt_reg(reg, prime)

    def asm(self, register_mapping, spilled):
        insns = []

        if isinstance(self.def_value, Register):
            if isinstance(self.use_value, (Register, Const)):
                def_asm = self.def_value.asm(register_mapping)
                use_asm = self.use_value.asm(register_mapping)
                if def_asm != use_asm:
                    insns.append(
                        "mov {}, {}".format(
                            def_asm,
                            use_asm
                        )
                    )
            elif isinstance(self.use_value, BinaryValue):
                if isinstance(self.use_value, Compare):
                    insns.append(
                        self.use_value.asm(register_mapping)
                    )
                elif isinstance(self.use_value, Arithmetic):
                    insns.append(
                        self.use_value.asm(register_mapping).format(
                            self.def_value.asm(register_mapping)
                        )
                    )
                else:
                    raise NotImplementedError
            elif isinstance(self.use_value, Memory):
                insns.append(
                    "ldr {}, {}".format(
                        self.def_value.asm(register_mapping),
                        self.use_value.asm(register_mapping, True)
                    )
                )
            else:
                raise NotImplementedError
        elif isinstance(self.def_value, Memory):
            insns.append(
                "str {}, {}".format(
                    self.use_value.asm(register_mapping),
                    self.def_value.asm(register_mapping, True)
                )
            )
        else:
            raise NotImplementedError

        return insns


class Jump(RTL):
    
    def __init__(self, this_insn: int, basic_block: int, jump_loc: int):
        super(Jump, self).__init__(this_insn, basic_block)
        self.jump_loc = jump_loc

    def asm(self, register_mapping, spilled):
        return [
            "b {}".format(
                Label.make_label(self.jump_loc)
            )
        ]
        
    @staticmethod
    def factory(this_insn: int, basic_block: int, rest: List[Any]):
        jump = None
        jump_loc = None
        _, _, locs = rest[0]

        try: # Conditional jump
            _, comp_sexp, jump_taken, _ = locs
            _, jump_loc = jump_taken
            jump = ConditionalJump(this_insn, basic_block, jump_loc, comp_sexp[0])
        except ValueError: # Unconditional jump
            _, jump_loc = locs
            jump = Jump(this_insn, basic_block, jump_loc)
            
        return jump


class ConditionalJump(Jump):

    def __init__(self, this_insn: int, basic_block: int, jump_loc: int, comp: str):
        super(ConditionalJump, self).__init__(this_insn, basic_block, jump_loc)
        self.comp = comp.lower()

    def asm(self, register_mapping, spilled):
        return [
            "b{} {}".format(
                self.comp,
                Label.make_label(self.jump_loc)
            )
        ]


class Call(RTL):

    def __init__(self, this_insn: int, basic_block: int, func_name: str):
        super(Call, self).__init__(this_insn, basic_block)
        self.func_name = func_name

    def asm(self, register_mapping, spilled):
        return [
            "bl {}".format(
                self.func_name
            )
        ]

    @staticmethod
    def factory(this_insn: int, basic_block: int, rest: List[Any]):
        func_name = None
        flattened = Call.flatten_list(rest)
        idx = 0

        while func_name is None and idx < len(flattened) - 1:
            if (isinstance(flattened[idx], str) and 
                    "symbol_ref" in flattened[idx].lower()):
                func_name = flattened[idx + 1]

            idx += 1

        assert(func_name is not None)
        return Call(this_insn, basic_block, func_name)

    @staticmethod
    def flatten_list(deep_list: List[Any]):
        flattened = []

        for element in deep_list:
            if isinstance(element, (list, tuple)):
                flattened += Call.flatten_list(element)
            else:
                flattened.append(element)
        
        return flattened


class Label(RTL):

    def __init__(self, this_insn: int, basic_block: int):
        super(Label, self).__init__(this_insn, basic_block)

    def asm(self, register_mapping, spilled):
        return [
            "{}:".format(
                Label.make_label(self.this_insn)
            )
        ]

    @staticmethod
    def make_label(insn_number: int):
        assert(func_name is not None)

        return "L{}_{}".format(insn_number, func_name)

    @staticmethod
    def factory(this_insn: int, basic_block: int, rest: List[Any]):
        return Label(this_insn, basic_block)


class Stack(RTL):

    def __init__(self, this_insn: int, basic_block: int, value: Value):
        super(Stack, self).__init__(this_insn, basic_block)
        assert(isinstance(value, VirtualRegister))
        self.value = value
   
    def asm(self, register_mapping, spilled):
        return [
            "{} {}, [{},#{}]".format(
                "{}",
                self.value.asm(register_mapping),
                AR.SP,
                self.stack_pos(spilled) * AR.INT_SIZE
            )
        ]

    def stack_pos(self, spilled):
        for (idx, reg) in enumerate(spilled):
            if self.value.fuzzy_eq(reg):
                return idx

        raise AssertionError


class Load(Stack):

    def __init__(self, this_insn: int, basic_block: int, value: Value):
        super(Load, self).__init__(this_insn, basic_block, value)

    def set_defs(self):
        self.defs = self.value.get_defs()

    def asm(self, register_mapping, spilled):
        return [
            super(Load, self).asm(register_mapping, spilled)[0].format(
                "ldr"
            )
        ]


class Store(Stack):
    
    def __init__(self, this_insn: int, basic_block: int, value: Value):
        super(Store, self).__init__(this_insn, basic_block, value)

    def set_uses(self):
        self.uses = self.value.get_uses()

    def asm(self, register_mapping, spilled):
        return [
            super(Store, self).asm(register_mapping, spilled)[0].format(
                "str"
            )
        ]


# Generates the assembly language as a string
def generate_assembly(
    rtls: List[RTL], 
    register_mapping: Dict[Register,RealRegister], 
    spilled: List[Register]
) -> str:
    asm = [
        ".arch armv7a",
        ".global {}".format(func_name),
        "{}:".format(func_name),
        "\tmov {}, {}".format(
            AR.FP,
            AR.SP
        )
    ]

    callee_save_regs = set()
    for (sym_reg, real_reg) in register_mapping.items():
        if (
            sym_reg not in REAL_REGISTERS
            and real_reg in CALLEE_SAVE_REGISTERS
        ):
            callee_save_regs.add(real_reg)

    callee_save_regs = list(callee_save_regs)
    callee_save_regs.sort()
    callee_save_regs = [reg.asm(register_mapping) for reg in callee_save_regs]

    asm.append(
        "\tpush {" + ", ".join(callee_save_regs) + ", " + AR.LR + "}"
    )

    if len(spilled) > 0:
        asm.append(
            "\tsub {0}, {0}, #{1}".format(
                AR.SP,
                len(spilled) * AR.INT_SIZE
            )
        )

    for rtl in rtls:
        asm_insns = rtl.asm(register_mapping, spilled)
        if len(asm_insns) > 0:
            asm_insns = [""] + asm_insns + [""]

        if isinstance(rtl, Label):
            asm += asm_insns
        else:
            for asm_insn in asm_insns:
                asm.append("\t" + asm_insn)

    if len(spilled) > 0:
        asm.append(
            "\tadd {0}, {0}, #{1}".format(
                AR.SP,
                len(spilled) * AR.INT_SIZE
            )
        )

    asm.append(
        "\tpop {" + ", ".join(callee_save_regs) + ", " + AR.PC + "}"
    )

    return "\n".join(asm) + "\n"
