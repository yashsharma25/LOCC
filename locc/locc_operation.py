class locc_operation:
    '''
    @party_index is the index of the party on which this operation is to be applied

    @qudit_index is the index of the qudit on which the operation is to be applied

    @operation_type
    Possible values are "measurement", "conditional_operation", "default"

    @condition is a tuple of (party_index, qudit_index, measurement_result})

    @operator is the unitary operation to be applied
    '''
    def __init__(self, party_index, qudit_index, operation_type, condition, operator):
        self.party_index = party_index
        self.qudit_index = qudit_index
        self.operation_type = operation_type
        self.condition = condition
        self.operator = operator