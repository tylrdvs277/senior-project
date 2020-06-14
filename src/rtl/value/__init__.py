
from typing import List, Any, Set, Optional, Dict, cast, NewType
from enum import Enum
from copy import deepcopy

from rtl.registers import ArchitectureRegisters as AR


RegMap = NewType('RegMap', Dict['Register','RealRegister'])


class Type(Enum):
    SI = 1
    CC = 2

    @staticmethod
    def translate(
        type: str
    ) -> 'Type':
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
    def factory(
        value_sexp: List[Any]
    ) -> 'Value':
        value_repr: Value
        value_type: str = str(value_sexp[0].lower())

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

    def get_defs(
        self
    ) -> Set['Register']:
        return set()

    def get_uses(
        self
    ) -> Set['Register']:
        return set()

    def asm(
        self, 
        register_mapping: RegMap, 
        mem: bool=False
    ) -> str:
        pass

    def update_virt_reg(
        self, 
        reg: 'Value', 
        prime: int
    ) -> None:
        pass


class Register(Value):

    def __init__(
        self, 
        reg_type: Type, 
        number: int
    ) -> None:
        self.reg_type: Type = reg_type
        self.number: int = number

    def asm(
        self, 
        register_mapping: RegMap, 
        mem: bool=False
    ) -> str:
        assert(self in register_mapping)

        return register_mapping[self].asm(register_mapping)

    def __repr__(
        self
    ) -> str:
        return "{}({})".format(self.__class__.__name__, str(self.number))

    @staticmethod
    def factory(
        reg_sexp: List[Any]
    ) -> Value:
        reg: Value
        reg_label, number_str, *rest = reg_sexp
        number: int = int(number_str)
        reg_type = Type.translate(str(reg_label))
        repr: Optional[List[Any]] = None if len(rest) == 0 else rest[0]

        if number == AR.CONDITION_CODES:
            reg = ConditionCodes(reg_type, number)
        elif (
            number in AR.REAL_REGISTERS_NUM
            or number == AR.ARG_POINTER
        ):
            reg = RealRegister.factory(reg_sexp)
        elif repr is None or isinstance(repr, List):
            reg = VirtualRegister(reg_type, number)
        else:
            raise NotImplementedError

        return reg

    def __hash__(
        self
    ) -> int:
        return hash(self.number)

    def __eq__(
        self, 
        other: object
    ) -> bool:
        return (
            self.__class__ == other.__class__
            and self.number == cast(Register,other).number
        )


class RealRegister(Register):

    def __init__(
        self, 
        reg_type: Type, 
        number: int, 
        repr: Optional[str]
    ) -> None:
        assert(number in AR.REAL_REGISTERS_NUM or number == AR.ARG_POINTER)
        super(RealRegister, self).__init__(reg_type, number)
        self.repr: Optional[str] = repr

    def asm(
        self, 
        register_mapping: RegMap, 
        mem: bool=False
    ) -> str:
        repr: str

        if self.number == AR.ARG_POINTER:
            repr = AR.FP
        else:
            repr = "r{}".format(self.number)

        return repr

    def __lt__(
        self, 
        other: 'RealRegister'
    ) -> bool:
        return self.number < other.number

    @staticmethod
    def factory(
        reg_sexp: List[Any]
    ) -> Value:
        reg: Value
        reg_label, number_str, *rest = reg_sexp
        number: int = int(number_str)
        reg_type: Type = Type.translate(str(reg_label))
        repr: Optional[str] = None if len(rest) == 0 else str(rest[0])

        if number in AR.CALLER_SAVE_REGISTERS_NUM:
            reg = CallerSaveRegister(reg_type, number, repr)
        else:
            reg = RealRegister(reg_type, number, repr)

        return reg


class CallerSaveRegister(RealRegister):

    def __init__(
        self, 
        reg_type: Type, 
        number: int, 
        repr: Optional[str]
    ) -> None:
        assert(number in AR.CALLER_SAVE_REGISTERS_NUM)
        super(CallerSaveRegister, self).__init__(reg_type, number, repr)

    def create_set(
        self
    ) -> Set[Register]:
        return {deepcopy(self)}

    def get_defs(
        self
    ) -> Set[Register]:
        return self.create_set()

    def get_uses(
        self
    ) -> Set[Register]:
        return self.create_set()


class ConditionCodes(Register):

    def __init__(
        self, 
        reg_type: Type, 
        number: int
    ) -> None:
        super(ConditionCodes, self).__init__(reg_type, number)

    @staticmethod
    def get_cc(
    ) -> 'ConditionCodes':
        return ConditionCodes(Type.CC, AR.CONDITION_CODES)
        

class VirtualRegister(Register):

    def __init__(
        self, 
        reg_type: Type, 
        number: int, 
        prime: int = 0
    ) -> None:
        super(VirtualRegister, self).__init__(reg_type, number)

        self.prime: int = prime

    def create_set(
        self
    ) -> Set[Register]:
        return {deepcopy(self)}

    def get_defs(
        self
    ) -> Set[Register]:
        return self.create_set()

    def get_uses(
        self
    ) -> Set[Register]:
        return self.create_set()

    def update_virt_reg(
        self, 
        reg: Value, 
        prime: int
    ) -> None:
        if self == reg:
            self.prime = prime

    def __repr__(
        self
    ) -> str:
        return "{}({},{})".format(
            self.__class__.__name__,
            self.number,
            self.prime
        )

    def __hash__(
        self
    ) -> int:
        return super(VirtualRegister, self).__hash__() ^ hash(self.prime)

    def __eq__(
        self, 
        other: object
    ) -> bool:
        return (
            super(VirtualRegister, self).__eq__(other)
            and self.prime == cast(VirtualRegister,other).prime
        )

    def fuzzy_eq(
        self, 
        other: object
    ) -> bool:
        return super(VirtualRegister, self).__eq__(other)


class Const(Value):

    def __init__(
        self, 
        value: int
    ) -> None:
        self.value: int = value

    def asm(
        self, 
        register_mapping: RegMap, 
        mem: bool=False
    ) -> str:
        repr: str

        if mem:
            assert(self.value > 0)

            value: int = self.value
            num_bits: int = 0
            num_one: int = 0
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
    def factory(
        const_sexp: List[Any]
    ) -> Value:
        _, value, *_ = const_sexp

        return Const(value)


class Memory(Value):

    def __init__(
        self, 
        mem_type: Type, 
        addr: Value
    ) -> None:
        self.mem_type: Type = mem_type
        self.addr: Value = addr

    def get_uses(
        self
    ) -> Set[Register]:
        return self.addr.get_uses()

    def update_virt_reg(
        self, 
        reg: Value, 
        prime: int
    ) -> None:
        self.addr.update_virt_reg(reg, prime)

    def asm(
        self, 
        register_mapping: RegMap, 
        mem: bool=False
    ) -> str:
        return "[{}]".format(
            self.addr.asm(register_mapping, True)
        )

    @staticmethod
    def factory(
        mem_sexp: List[Any]
    ) -> Value:
        mem_str, mem_addr_sexp, *_ = mem_sexp

        type: Type = Type.translate(str(mem_str))
        addr: Value = Value.factory(mem_addr_sexp)

        return Memory(type, addr)


class BinaryValue(Value):

    def __init__(
        self, 
        result_type: Type, 
        value1: Value, 
        value2: Value
    ) -> None:
        self.result_type: Type = result_type
        self.value1: Value = value1
        self.value2: Value = value2

    def get_uses(
        self
    ) -> Set[Register]:
        return self.value1.get_uses().union(self.value2.get_uses())

    def update_virt_reg(
        self, 
        reg: Value, 
        prime: int
    ) -> None:
        self.value1.update_virt_reg(reg, prime)
        self.value2.update_virt_reg(reg, prime)


class Compare(BinaryValue):

    def __init__(
        self, 
        compare_type: Type, 
        value1: Value, 
        value2: Value
    ) -> None:
        super(Compare, self).__init__(compare_type, value1, value2)

    @staticmethod
    def factory(
        compare_sexp: List[Any]
    ) -> Value:
        op_str, value1_sexp, value2_sexp = compare_sexp

        type: Type = Type.translate(str(op_str))
        value1: Value = Value.factory(value1_sexp)
        value2: Value = Value.factory(value2_sexp)

        return Compare(type, value1, value2)

    def asm(
        self, 
        register_mapping: RegMap, 
        mem: bool=False
    ) -> str:
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
        def translate(
            op_str: str
        ) -> 'Arithmetic.ArithmeticOp':
            ret: Arithmetic.ArithmeticOp

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

    def __init__(
        self, 
        arith_type: Type, 
        value1: Value, 
        value2: Value, 
        arith_op: ArithmeticOp
    ) -> None:
        super(Arithmetic, self).__init__(arith_type, value1, value2)
        self.arith_op: Arithmetic.ArithmeticOp = arith_op

    def asm(
        self, 
        register_mapping: RegMap, 
        mem: bool=False
    ) -> str:
        repr: str

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
    def factory(
        arith_sexp: List[Any]
    ) -> Value:
        op_str, value1_sexp, value2_sexp = arith_sexp
        arith_op: Arithmetic.ArithmeticOp = Arithmetic.ArithmeticOp.translate(op_str)
        arith_type: Type = Type.translate(str(op_str))
        value1: Value = Value.factory(value1_sexp)
        value2: Value = Value.factory(value2_sexp)

        return Arithmetic(arith_type, value1, value2, arith_op)
