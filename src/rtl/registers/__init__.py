class ArchitectureRegisters:

    CALLER_SAVE_REGISTERS_NUM = set((0, 1, 2, 3))
    CALLEE_SAVE_REGISTERS_NUM = set((4, 5, 6, 7, 8, 9, 10))
    REAL_REGISTERS_NUM = CALLER_SAVE_REGISTERS_NUM.union(
        CALLEE_SAVE_REGISTERS_NUM
    )

    LR = "lr"
    PC = "pc"
    FP = "fp"
    SP = "sp"
    ARG_POINTER = 104
    CONDITION_CODES = 100
    INT_SIZE = 4
