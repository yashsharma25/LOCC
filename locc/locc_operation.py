class locc_operation:

    '''
    Args:

    party_index: index of the party on which this operation is to be applied

    qudit_index: index of the qudit on which the operation is to be applied

    operation_type: Possible values are "measurement", "conditional_operation", "default"

    condition: A tuple of (party_index, qudit_index, measurement_result})

    operator: Qiskit gate or any unitary operation to be applied

    Example:
    locc_op4.party_index = 1
    locc_op4.qudit_index = 0
    locc_op4.operation_type = "conditional_operation"
    locc_op4.condition = (0, 0, 1)
    locc_op4.operator = Gate.X

    The above example means that if the 0th qudit of the 0th party measures 1, then apply X gate to the 0th qudit of the first party

    '''

    def __init__(self, party_index, qudit_index, operation_type, operator = None, condition = None):
        self.party_index = party_index
        self.qudit_index = qudit_index
        self.operation_type = operation_type
        self.operator = operator
        self.condition = condition
