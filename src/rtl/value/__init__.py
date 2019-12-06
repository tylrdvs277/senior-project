
from typing import List, Any, Set
from enum import Enum
from copy import deepcopy

from rtl.registers import ArchitectureRegisters as AR


class Type(Enum):
    SI = 1
    CC = 2

    @staticmethod
    def translate(type: str):
        ret = None
        type = type.lower()

        if "si" in type:
            ret = Type.SI
        elif "cc" in type:
            ret = Type.CC
        else:
            raise NotImplementedError

        return ret


class Value:

    @staticmethod
    def factory(value_sexp: List[Any]):
        value_repr = None
        value_type = value_sexp[0].lower()

        if "const" in value_type:
            value_repr = Const.factory(value_sexp)
        elif "reg" in value_type:
            value_repr = Register.factory(value_sexp)
        elif "mem" in value_type:
            value_repr = Memory.factory(value_sexp)
        elif "compare" in value_type:
            value_repr = Compare.factory(value_sexp)
        elif ("plus" in value_type
                or "ashift" in value_type
                or "mult" in value_type
                or "minus" in value_type):
            value_repr = Arithmetic.factory(value_sexp)
        else:
            raise NotImplementedError

        return value_repr

    def get_defs(self):
        return set()

    def get_uses(self):
        return set()

    def update_virt_reg(self, reg, prime):
        pass


class Register(Value):

    def __init__(self, reg_type: Type, number: int):
        self.reg_type = reg_type
        self.number = number

    def asm(self, register_mapping, mem=False):
        assert(self in register_mapping)

        return register_mapping[self].asm(register_mapping)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, str(self.number))

    @staticmethod
    def factory(reg_sexp: List[Any]):
        reg = None
        reg_label, number, *rest = reg_sexp
        reg_type = Type.translate(reg_label)
        repr = None if len(rest) == 0 else rest[0]

        if number == AR.CONDITION_CODES:
            reg = ConditionCodes(reg_type, number)
        elif (number in AR.REAL_REGISTERS_NUM
                or number == AR.ARG_POINTER):
            reg = RealRegister.factory(reg_type, number, repr)
        elif repr is None or isinstance(repr, List):
            reg = VirtualRegister(reg_type, number)
        else:
            raise NotImplementedError

        return reg

    def __hash__(self):
        return hash(self.number)

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__
            and self.number == other.number
        )


class RealRegister(Register):

    def __init__(self, reg_type: Type, number: int, repr: str):
        assert(number in AR.REAL_REGISTERS_NUM or number == AR.ARG_POINTER)
        super(RealRegister, self).__init__(reg_type, number)
        self.repr = repr

    def asm(self, register_mapping, mem=False):
        repr = None

        if self.number == AR.ARG_POINTER:
            repr = AR.FP
        else:
            repr = "r{}".format(self.number)

        return repr

    def __lt__(self, other):
        return self.number < other.number

    @staticmethod
    def factory(reg_type: Type, number: int, repr: str):
        reg = None

        if number in AR.CALLER_SAVE_REGISTERS_NUM:
            reg = CallerSaveRegister(reg_type, number, repr)
        else:
            reg = RealRegister(reg_type, number, repr)

        return reg


class CallerSaveRegister(RealRegister):

    def __init__(self, reg_type: Type, number: int, repr: str):
        assert(number in AR.CALLER_SAVE_REGISTERS_NUM)
        super(CallerSaveRegister, self).__init__(reg_type, number, repr)

    def create_set(self):
        return {deepcopy(self)}

    def get_defs(self):
        return self.create_set()

    def get_uses(self):
        return self.create_set()


class ConditionCodes(Register):

    def __init__(self, reg_type: Type, number: int):
        super(ConditionCodes, self).__init__(reg_type, number)


class VirtualRegister(Register):

    def __init__(self, reg_type: Type, number: int, prime: int = 0):
        super(VirtualRegister, self).__init__(reg_type, number)

        self.prime = prime

    def create_set(self):
        return {deepcopy(self)}

    def get_defs(self):
        return self.create_set()

    def get_uses(self):
        return self.create_set()

    def update_virt_reg(self, reg: Value, prime: int):
        if self == reg:
            self.prime = prime

    def __repr__(self):
        return "{}({},{})".format(
            self.__class__.__name__,
            self.number,
            self.prime
        )

    def __hash__(self):
        return super(VirtualRegister, self).__hash__() ^ hash(self.prime)

    def __eq__(self, other):
        return (
            super(VirtualRegister, self).__eq__(other)
            and self.prime == other.prime
        )

    def fuzzy_eq(self, other):
        return super(VirtualRegister, self).__eq__(other)


class Const(Value):

    def __init__(self, value: int):
        self.value = value

    def asm(self, register_mapping, mem=False):
        repr = None

        if mem:
            assert(self.value > 0)

            value = self.value
            num_bits = 0
            num_one = 0
            while value > 1:
                if value & 1 == 1:
                    num_one += 1
                value >>= 1
                num_bits += 1

            assert(num_one == 0)

            repr = "#{}".format(
                num_bits
            )
        else:
            repr = "#{}".format(
                self.value
            )

        return repr

    @staticmethod
    def factory(const_sexp: List[Any]):
        _, value, *_ = const_sexp

        return Const(value)


class Memory(Value):

    def __init__(self, mem_type: Type, addr: Value):
        self.mem_type = mem_type
        self.addr = addr

    def get_uses(self):
        return self.addr.get_uses()

    def update_virt_reg(self, reg: Value, prime: int):
        self.addr.update_virt_reg(reg, prime)

    def asm(self, register_mapping, mem=True):
        return "[{}]".format(
            self.addr.asm(register_mapping, True)
        )

    @staticmethod
    def factory(mem_sexp: List[Any]):
        mem_str, mem_addr_sexp, *_ = mem_sexp

        type = Type.translate(mem_str)
        addr = Value.factory(mem_addr_sexp)

        return Memory(type, addr)


class BinaryValue(Value):

    def __init__(self, result_type: Type, value1: Value, value2: Value):
        self.result_type = result_type
        self.value1 = value1
        self.value2 = value2

    def get_uses(self):
        return self.value1.get_uses().union(self.value2.get_uses())

    def update_virt_reg(self, reg: Value, prime: int):
        self.value1.update_virt_reg(reg, prime)
        self.value2.update_virt_reg(reg, prime)


class Compare(BinaryValue):

    def __init__(self, compare_type: Type, value1: Value, value2: Value):
        super(Compare, self).__init__(compare_type, value1, value2)

    @staticmethod
    def factory(compare_sexp: List[Any]):
        op_str, value1_sexp, value2_sexp = compare_sexp

        type = Type.translate(op_str)
        value1 = Value.factory(value1_sexp)
        value2 = Value.factory(value2_sexp)

        return Compare(type, value1, value2)

    def asm(self, register_mapping, mem=False):
        return "cmp {}, {}".format(
            self.value1.asm(register_mapping),
            self.value2.asm(register_mapping)
        )


class Arithmetic(BinaryValue):

    class ArithmeticOp(Enum):
        PLUS = "add"
        ASHIFT = "lsl"
        MULT = "mult"
        MINUS = "sub"

        @staticmethod
        def translate(op_str: str):
            ret = None

            if "plus" in op_str:
                ret = Arithmetic.ArithmeticOp.PLUS
            elif "ashift" in op_str and "ashiftrt" not in op_str:
                ret = Arithmetic.ArithmeticOp.ASHIFT
            elif "mult" in op_str:
                ret = Arithmetic.ArithmeticOp.MULT
            elif "minus" in op_str:
                ret = Arithmetic.ArithmeticOp.MINUS
            else:
                raise NotImplementedError

            return ret

    def __init__(self, arith_type: Type, value1: Value, value2: Value, arith_op: ArithmeticOp):
        super(Arithmetic, self).__init__(arith_type, value1, value2)
        self.arith_op = arith_op

    def asm(self, register_mapping, mem=False):
        repr = None

        if mem:
            if self.arith_op == Arithmetic.ArithmeticOp.PLUS:
                if isinstance(self.value1, Register):
                    repr = "{},{}".format(
                        self.value1.asm(register_mapping),
                        self.value2.asm(register_mapping, isinstance(
                            self.value1, Arithmetic))
                    )
                else:
                    repr = "{},{}".format(
                        self.value2.asm(register_mapping),
                        self.value1.asm(register_mapping, isinstance(
                            self.value1, Arithmetic))
                    )
            elif self.arith_op == Arithmetic.ArithmeticOp.MULT:
                assert(
                    isinstance(self.value1, Register)
                    and isinstance(self.value2, Const)
                )

                repr = "{},{}{}".format(
                    self.value1.asm(register_mapping, True),
                    Arithmetic.ArithmeticOp.ASHIFT.value,
                    self.value2.asm(register_mapping, True)
                )
            else:
                raise NotImplementedError
        else:
            repr = "{} {}, {}, {}".format(
                self.arith_op.value,
                "{}",
                self.value1.asm(register_mapping),
                self.value2.asm(register_mapping)
            )

        return repr

    @staticmethod
    def factory(arith_sexp: List[Any]):
        op_str, value1_sexp, value2_sexp = arith_sexp
        arith_op = Arithmetic.ArithmeticOp.translate(op_str)
        arith_type = Type.translate(op_str)
        value1 = Value.factory(value1_sexp)
        value2 = Value.factory(value2_sexp)

        return Arithmetic(arith_type, value1, value2, arith_op)
