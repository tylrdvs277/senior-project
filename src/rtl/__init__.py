
from typing import List, Any, Dict, Optional, cast
from enum import Enum

from rtl.value import *
from rtl.registers import ArchitectureRegisters as AR


func_name: str
CALLER_SAVE_REGISTERS: Set[CallerSaveRegister] = set(
    CallerSaveRegister(Type.SI, number, None)
    for number in AR.CALLER_SAVE_REGISTERS_NUM
)
CALLEE_SAVE_REGISTERS: Set[RealRegister] = set(
    RealRegister(Type.SI, number, None)
    for number in AR.CALLEE_SAVE_REGISTERS_NUM
)
REAL_REGISTERS: Set[RealRegister] = CALLEE_SAVE_REGISTERS.union(
    CALLER_SAVE_REGISTERS
)


class RTL:
    
    def __init__(
        self, 
        this_insn: int, 
        basic_block: int
    ) -> None:
        self.this_insn: int = this_insn
        self.basic_block: int = basic_block

        self.defs: Set[Register]
        self.uses: Set[Register]

    def set_defs(
        self
    ) -> None:
        self.defs = set()

    def set_uses(
        self
    ) -> None:
        self.uses = set()

    @staticmethod
    def get_(
        regs: Set[Register], 
        register_mapping: Optional[RegMap]
    ) -> Set[Register]:
        ret: Set[Register] = regs

        if register_mapping is not None:
            register_mapping_unpack: RegMap = cast('RegMap', register_mapping) 
            ret = set()
            for reg in regs:
                ret.add(register_mapping_unpack[reg])

        return ret

    def set_defs_reg(
        self, 
        register_mapping: Optional[RegMap]=None
    ) -> None:
        self.defs = RTL.get_(self.defs, register_mapping)

    def set_uses_reg(
        self, 
        register_mapping: Optional[RegMap]=None
    ) -> None:
        self.uses = RTL.get_(self.uses, register_mapping)

    def get_defs(
        self
    ) -> Set[Register]:
        return self.defs

    def get_uses(
        self
    ) -> Set[Register]:
        return self.uses

    def asm(
        self, 
        register_mapping: RegMap, 
        spilled: List[Register]
    ) -> List[str]:
        return []

    def update_virt_reg(
        self, 
        reg: Value, 
        prime: int
    ) -> None:
        pass
        
    @staticmethod
    def factory(
        rtl_sexp: List[Any]
    ) -> List['RTL']:
        rtl_repr: List['RTL'] = []

        try:
            insn_type, this_insn, _, _, basic_block, *rest = rtl_sexp
            insn_type: str = str(insn_type).lower()
            insn_classes: Dict[str,'RTL'] = dict(
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
        
    def __init__(
        self, 
        this_insn: int, 
        basic_block: int, 
        use_value: Value
    ) -> None:
        super(Insn, self).__init__(this_insn, basic_block)
        self.use_value: Value = use_value

    def set_uses(
        self
    ) -> None:
        self.uses = self.use_value.get_uses()

    def update_virt_reg(
        self, 
        reg: Value, 
        prime: int
    ) -> None:
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
    
    def __init__(
        self, 
        this_insn: int, 
        basic_block: int, 
        def_value: Value, 
        use_value: Value
    ) -> None:
        super(SetInsn, self).__init__(this_insn, basic_block, use_value)
        self.def_value: Value = def_value

    def set_defs(
        self
    ) -> None:
        self.defs = self.def_value.get_defs()

    def set_uses(
        self
    ) -> None:
        super(SetInsn, self).set_uses()

        if isinstance(self.def_value, Memory):
            self.uses.update(self.def_value.get_uses())

    def update_virt_reg(
        self, 
        reg: Value, 
        prime: int
    ) -> None:
        super(SetInsn, self).update_virt_reg(reg, prime)
        self.def_value.update_virt_reg(reg, prime)

    def asm(
        self, 
        register_mapping: Dict[Register,RealRegister], 
        spilled
    ) -> List[str]:
        insns: List[str] = []

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
    
    def __init__(
        self, 
        this_insn: int, 
        basic_block: int, 
        jump_loc: int
    ) -> None:
        super(Jump, self).__init__(this_insn, basic_block)
        self.jump_loc: int = jump_loc

    def asm(
        self, 
        register_mapping: Dict[Register,RealRegister], 
        spilled
    ) -> List[str]:
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

    def __init__(
        self, 
        this_insn: int, 
        basic_block: int, 
        jump_loc: int, 
        comp: str
    ) -> None:
        super(ConditionalJump, self).__init__(this_insn, basic_block, jump_loc)
        self.comp: str = comp.lower()

    def asm(
        self, 
        register_mapping: Dict[Register,RealRegister], 
        spilled
    ) -> List[str]:
        return [
            "b{} {}".format(
                self.comp,
                Label.make_label(self.jump_loc)
            )
        ]


class Call(RTL):

    EXIT_FUNCS: Set[str] = {"exit", "abort"}

    def __init__(
        self, 
        this_insn: int, 
        basic_block: int, 
        func_name: str
    ) -> None:
        super(Call, self).__init__(this_insn, basic_block)
        self.func_name: str = func_name


    def asm(
        self, 
        register_mapping: Dict[Register,RealRegister], 
        spilled
    ) -> List[str]:
        return [
            "bl {}".format(
                self.func_name
            )
        ]
    
    def is_exit_func(
        self
    ) -> bool:
        return self.func_name in Call.EXIT_FUNCS

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
    def flatten_list(
        deep_list: List[Any]
    ) -> List[Any]:
        flattened: List[Any] = []

        for element in deep_list:
            if isinstance(element, (list, tuple)):
                flattened += Call.flatten_list(element)
            else:
                flattened.append(element)
        
        return flattened


class Label(RTL):

    def __init__(
        self, 
        this_insn: int, 
        basic_block: int
    ) -> None:
        super(Label, self).__init__(this_insn, basic_block)

    def asm(
        self, 
        register_mapping: Dict[Register,RealRegister], 
        spilled
    ) -> List[str]:
        return [
            "{}:".format(
                Label.make_label(self.this_insn)
            )
        ]

    @staticmethod
    def make_label(
        insn_number: int
    ) -> str:
        assert(func_name is not None)

        return "L{}_{}".format(insn_number, func_name)

    @staticmethod
    def factory(this_insn: int, basic_block: int, rest: List[Any]):
        return Label(this_insn, basic_block)


class Stack(RTL):

    def __init__(
        self, 
        this_insn: int, 
        basic_block: int, 
        value: Value
    ) -> None:
        super(Stack, self).__init__(this_insn, basic_block)
        assert(isinstance(value, VirtualRegister))
        self.value: Value = value
   
    def asm(
        self, 
        register_mapping: Dict[Register,RealRegister], 
        spilled
    ) -> List[str]:
        return [
            "{} {}, [{},#{}]".format(
                "{}",
                self.value.asm(register_mapping),
                AR.SP,
                self.stack_pos(spilled) * AR.INT_SIZE
            )
        ]

    def stack_pos(
        self, 
        spilled
    ) -> int:
        for (idx, reg) in enumerate(spilled):
            if self.value.fuzzy_eq(reg):
                return idx

        raise AssertionError


class Load(Stack):

    def __init__(
        self, 
        this_insn: int, 
        basic_block: int, 
        value: Value
    ) -> None:
        super(Load, self).__init__(this_insn, basic_block, value)

    def set_defs(
        self
    ) -> None:
        self.defs = self.value.get_defs()

    def asm(
        self, 
        register_mapping: Dict[Register,RealRegister], 
        spilled
    ) -> List[str]:
        return [
            super(Load, self).asm(register_mapping, spilled)[0].format(
                "ldr"
            )
        ]


class Store(Stack):
    
    def __init__(
        self, 
        this_insn: int, 
        basic_block: int, 
        value: Value
    ) -> None:
        super(Store, self).__init__(this_insn, basic_block, value)

    def set_uses(
        self
    ) -> None:
        self.uses = self.value.get_uses()

    def asm(
        self, 
        register_mapping: Dict[Register,RealRegister], 
        spilled
    ) -> List[str]:
        return [
            super(Store, self).asm(register_mapping, spilled)[0].format(
                "str"
            )
        ]


class LoopPreheader(RTL):

    def __init__(
        self,
        this_insn: int, 
        basic_block: int
    ) -> None:
        super(LoopPreheader, self).__init__(this_insn, basic_block)


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
