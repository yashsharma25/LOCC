from locc_controller import locc_controller

class locc_discriminate:
    def __init__(self):
        return
    
    #this function check if the given protocol can discriminate between two states
    def discriminate(self, state1, state2, protocol):
        l1 = locc_controller(protocol, state1)
        l2 = locc_controller(protocol, state2)

        l1.execute_protocol()
        l2.execute_protocol()

        #specify which measurements to make. That is done in the protocol
        #now the next step is to compare the measurement results to check which state is given to us
        
        s1_measurements = state1.measure_all_possibilities()
        s2_measurements = state2.measure_all_possibilities()

        for (p1,q1), (p2, q2) in zip(l1.k_party_obj.measurement_result.items(), l2.k_party_obj.measurement_result.items()):
            if (p1, q1) in s1_measurements and (p2, q2) not in s2_measurements:
                print("This is state 1")
                return 
            
            elif (p1, q1) not in s1_measurements and (p2, q2) in s2_measurements:
                print("This is state 2")
                return