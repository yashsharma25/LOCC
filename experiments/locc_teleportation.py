from qiskit.circuit.gate import Gate
from locc import locc_controller, locc_operation

def teleportation():
    locc_teleporation_obj = locc_controller()

    locc_op1 = locc_operation()
    locc_op1.party_index = 0
    locc_op1.qudit_index = 0
    locc_op1.operation_type = "default"
    locc_op1.operator = Gate.H

    locc_op2 = locc_operation()
    locc_op2.party_index = 0
    locc_op2.qudit_index = 0
    locc_op2.operation_type = "measure"

    locc_op3 = locc_operation()
    locc_op3.party_index = 0
    locc_op3.qudit_index = 1
    locc_op3.operation_type = "measure"


    locc_op4 = locc_operation()
    locc_op4.party_index = 1
    locc_op4.qudit_index = 0
    locc_op4.operation_type = "conditional_operation"
    locc_op4.condition = (0, 0, 1)
    locc_op4.operator = Gate.X


    locc_op5 = locc_operation()
    locc_op5.party_index = 1
    locc_op5.qudit_index = 0
    locc_op5.operation_type = "conditional_operation"
    locc_op5.condition = (0, 0, 1)
    locc_op5.operator = Gate.Z

    locc_teleporation_obj.protocol = [locc_op1, locc_op2, locc_op3, locc_op4, locc_op5]

    return locc_teleporation_obj

